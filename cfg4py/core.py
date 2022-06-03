"""Main module."""
import logging.config
import os
import re
from collections.abc import Mapping
from io import StringIO

from apscheduler.schedulers.background import BackgroundScheduler
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError
from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from cfg4py.config import Config

logger = logging.getLogger(__name__)

envar = "__cfg4py_server_role__"
_scheduler = BackgroundScheduler()
_remote_fetcher = None
_dump_on_change: bool = False

yaml = YAML(typ="safe")

# handle local configuration file change
_local_observer = None
_cfg_obj = Config()

_cfg_local = {}
_cfg_remote = {}
_strict = True

_local_config_dir: str = ""


class RemoteConfigFetcher:
    def fetch(self) -> str:
        raise NotImplementedError("sub class must implement this!")  # pragma: no cover


class RedisConfigFetcher(RemoteConfigFetcher):
    def __init__(
        self, key: str, host: str = "localhost", port: int = 6379, db: int = 0, **kwargs
    ):
        self.key = key
        from redis import StrictRedis  # type: ignore

        self.client = StrictRedis(
            host, port=port, db=db, decode_responses="utf-8", **kwargs
        )

    def fetch(self) -> dict:
        settings = None
        try:
            logger.info("fetching configuration from redis server")
            settings = self.client.get(self.key)
            return _load_and_replace_envar(settings)
        except Exception as e:  # pragma: no cover
            logger.exception(e)

        return {}


class LocalConfigChangeHandler(FileSystemEventHandler):
    def dispatch(self, event):
        if not isinstance(event, FileModifiedEvent):
            return

        ext = os.path.splitext(event.src_path)
        if ext in [".yml", ".yaml"]:
            _load_from_local_file()


def _mixin(d, u):
    # noinspection SpellCheckingInspection
    """
    if  value x in "keyx:valuex" pair is list, it's will be replaced
    :param d:
    :param u:
    :return:
    """
    u = u or {}
    d = d or {}
    for k, v in u.items():
        if isinstance(v, Mapping):
            d[k] = _mixin(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def _to_obj(obj, conf: dict):
    for key, value in conf.items():
        if type(value) == dict:
            _obj = Config()
            setattr(obj, key, _obj)
            _to_obj(_obj, value)
        else:
            setattr(obj, key, value)


def _refresh():
    global _cfg_local, _cfg_remote
    _cfg_remote = _remote_fetcher.fetch()
    merged = _mixin(_cfg_remote, _cfg_local)
    update_config(merged)


def enable_logging(level=logging.INFO, log_file=None, file_size=10, file_count=7):
    """
    Enable basic log function for the application

    if log_file is None, then it'll provide console logging, otherwise, the console
    logging is turned off, all events will be logged into the provided file.

    Args:
        level: the log level, one of logging.DEBUG, logging.INFO, logging.WARNING,
        logging.Error
        log_file: the absolute file path for the log.
        file_size: file size in MB unit
        file_count: how many backup files leaved in disk

    Returns:
        None
    """

    assert file_count > 0
    assert file_size > 0

    from logging import handlers

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-1.1s %(filename)s:%(lineno)s | %(message)s"
    )

    _logger = logging.getLogger()
    _logger.setLevel(level)

    if log_file is None:
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        _logger.addHandler(console)
    else:
        file_dir = os.path.dirname(log_file)
        os.makedirs(file_dir, exist_ok=True)
        rotating_file = handlers.RotatingFileHandler(
            log_file, maxBytes=1024 * 1024 * file_size, backupCount=file_count
        )
        rotating_file.setFormatter(formatter)
        _logger.addHandler(rotating_file)


def config_remote_fetcher(fetcher: RemoteConfigFetcher, interval: int = 300):
    """
    config a remote configuration fetcher, which will pull the settings on every
     `refresh_interval`
    Args:
        fetcher: sub class of `RemoteConfigFetcher`
        interval: how long should cfg4py to pull the configuration from remote

    Returns:

    """
    global _remote_fetcher
    _remote_fetcher = fetcher

    _scheduler.add_job(_refresh, "interval", seconds=interval)
    _scheduler.start()


def build(save_to: str):
    global _cfg_obj
    with open(os.path.join(os.path.dirname(__file__), "config.py"), "r") as origin:
        lines = origin.readlines()
        lines.append("\n")

    no_instance = [
        f"{' ' * 4}def __init__(self):\n",
        f"{' ' * 8}raise TypeError(\"Do NOT instantiate this class\")\n\n",
    ]
    lines.extend(no_instance)
    with open(save_to, encoding="utf-8", mode="w") as f:
        lines = _schema_from_obj_(_cfg_obj, lines)
        content = re.sub("\n+$", "\n", "".join(lines))

        f.write(content)
        # f.writelines("".join(lines))


def _schema_from_obj_(obj, lines, depth: int = 0):
    """
    build a python file for auto-complete.
    """
    depth += 1
    if isinstance(obj, Config):
        for name in obj.__dict__.copy().keys():
            if name.startswith("__"):
                continue
            child = getattr(obj, name)
            if callable(child):
                continue

            if isinstance(child, Config):
                lines.append(f"{' ' * 4 * depth}class {name}:\n")
                _schema_from_obj_(child, lines, depth)
            else:
                _type = f"{type(child)}"
                _type = re.sub(r".*\'(.*)\'>", r"\1", _type)
                if _type != "NoneType":
                    lines.append(f"{' ' * 4 * depth}{name}: Optional[{_type}] = None\n")
                else:
                    lines.append(f"{' ' * 4 * depth}{name} = None\n")
                lines.append("\n")
    else:
        print(obj)

    return lines


def init(local_cfg_path: str = None, dump_on_change=True, strict=False):
    """
    create cfg object.
    Args:
        local_cfg_path: the directory name where your configuration files exist
        dump_on_change: if configuration is updated, whether or not to dump them into
         log file

    Returns:
    """
    global _local_config_dir, _dump_on_change, _remote_fetcher, _local_observer
    global _cfg_obj, _cfg_local, _cfg_remote
    global _strict

    _strict = strict
    _dump_on_change = dump_on_change
    if local_cfg_path:
        _local_config_dir = os.path.expanduser(local_cfg_path)

        _cfg_local = _load_from_local_file()
        update_config(_mixin(_cfg_remote, _cfg_local))

        try:
            # handle local configuration file change, this may not be available on some platform, like apple m1
            _local_observer = Observer()
            _local_observer.schedule(
                LocalConfigChangeHandler(), _local_config_dir, recursive=False
            )
            _local_observer.start()
        except Exception as e:
            logger.exception(e)
            logger.warning("failed to watch file changes. Hot-reload is not available")

    return _cfg_obj


def yaml_dump(conf, options=None):
    if options is None:
        options = {}
    string_stream = StringIO()
    try:
        yaml.dump(conf, string_stream, **options)
        output_str = string_stream.getvalue()
    finally:
        string_stream.close()
    return output_str


def update_config(conf: dict):
    global _cfg_obj

    if "logging" in conf:
        _process_logging_settings(conf["logging"])
        logconf = conf["logging"].copy()

        # logging settings usually contains python keywork, for example class
        # thus these keys cannot be treated as Config's members
        del conf["logging"]

    if _dump_on_change:
        logger.info("configuration is\n%s", yaml_dump(conf))

    _to_obj(_cfg_obj, conf)
    if "logconf" in locals():
        _cfg_obj.logging = logconf

    return _cfg_obj


def _process_logging_settings(conf: dict):
    logging.config.dictConfig(conf)


def _guess_extension():
    files = os.listdir(_local_config_dir)
    counter = {".yml": 0, ".yaml": 0}

    for f in files:
        _, ext = os.path.splitext(f)
        if ext == ".yml":
            counter[ext] += 1
        elif ext == ".yaml":
            counter[ext] += 1

    _max = 0
    ext = ""
    for key in counter.keys():
        if counter[key] > _max:
            _max = counter[key]
            ext = key

    if ext in [".yml", ".yaml"]:
        # noinspection PyPackageRequirements
        return ext
    else:
        msg = "No config files present, or file format is not yaml."
        raise FileNotFoundError(msg)


def get_config_dir():
    return _local_config_dir


def _load_and_replace_envar(content: str):
    """parse content, replace placeholder with environment variables, and load with yaml

    Args:
        content (str): the content of configurations
    """
    pattern = re.compile(r".*?\${(\w+)}.*?")
    match = pattern.findall(content)
    if match:
        replaced = content
        for g in match:
            replaced = replaced.replace(
                f"${{{g}}}", os.environ.get(g, f"ERROR_ENVAR_NOT_SET[{g}]")
            )
        try:
            return yaml.load(replaced)
        except YAMLError as e:
            logger.error("failed to parse:%s\n", content)
            raise e

    try:
        return yaml.load(content)
    except YAMLError as e:
        logger.error("failed to parse：%s\n", content)
        raise e


def _load_from_local_file() -> dict:
    """
    read configuration hierarchically from disk
    Args:

    Returns:

    """
    global _strict

    conf = {}

    role = os.getenv(envar, "")
    if role == "" and _strict:
        msg = f"You must config environment variables {envar} as one of"
        "'DEV, TEST, PRODUCTION'"
        raise EnvironmentError(msg)
    try:
        ext = _guess_extension()
        with open(
            os.path.join(_local_config_dir, f"defaults{ext}"), "r", encoding="utf-8"
        ) as base:
            conf = _load_and_replace_envar(base.read(-1))

        if role == "PRODUCTION":
            with open(
                os.path.join(_local_config_dir, f"production{ext}"),
                "r",
                encoding="utf-8",
            ) as prod:
                _prod = _load_and_replace_envar(prod.read(-1))
                _mixin(conf, _prod)

        elif role == "TEST":
            with open(
                os.path.join(_local_config_dir, f"test{ext}"), "r", encoding="utf-8"
            ) as test:
                _test = _load_and_replace_envar(test.read(-1))
                _mixin(conf, _test)
        elif role == "DEV":
            with open(
                os.path.join(_local_config_dir, f"dev{ext}"), "r", encoding="utf-8"
            ) as dev:
                _dev = _load_and_replace_envar(dev.read(-1))
                _mixin(conf, _dev)
        else:
            pass
    except FileNotFoundError as e:
        if e.filename.find("defaults") != -1:
            raise FileNotFoundError("Failed to find default configuration file")
    except Exception as e:
        logger.exception(e)

    return conf


# noinspection PyUnusedLocal
def config_server_role(role: str):
    os.environ[envar] = role
