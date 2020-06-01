"""Main module."""
import json
import logging.config
import os
import re
from collections import Mapping

from apscheduler.schedulers.background import BackgroundScheduler
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from watchdog.observers import Observer
from cfg4py.config import Config

logger = logging.getLogger(__name__)

envar = '__cfg4py_server_role__'
_scheduler = BackgroundScheduler()
_remote_fetcher = None
_dump_on_change: bool = False

# handle local configuration file change
_local_observer = None
_cfg_obj = Config()

_cfg_default = {}
_cfg_local = {}
_cfg_remote = {}

_local_config_dir: str = ''


class RemoteConfigFetcher:
    def fetch(self) -> dict:
        raise NotImplementedError("sub class must implement this!") # pragma: no cover


class RedisConfigFetcher(RemoteConfigFetcher):
    def __init__(self, key: str, host: str = 'localhost', port: int = 6379, db: int = 0, **kwargs):
        self.key = key
        # noinspection PyPackageRequirements
        from redis import StrictRedis
        self.client = StrictRedis(host, port=port, db=db, **kwargs)

    def fetch(self) -> dict:
        settings = None
        try:
            logger.info("fetching configuration from redis server")
            settings = self.client.get(self.key)
            return json.loads(settings)
        except json.JSONDecodeError: # pragma: no cover
            logger.warning("failed to decode settings:\n%s", settings)
        except Exception as e: # pragma: no cover
            logger.exception(e)

        return {}


class LocalConfigChangeHandler(FileSystemEventHandler):
    def dispatch(self, event):
        if isinstance(event, FileModifiedEvent):
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

    if log_file is None, then it'll provide console logging, otherwise, the console logging is turned off, all
    events will be logged into the provided file.

    Args:
        level: the log level, one of logging.DEBUG, logging.INFO, logging.WARNING, logging.Error
        log_file: the absolute file path for the log.
        file_size: file size in MB unit
        file_count: how many backup files leaved in disk

    Returns:
        None
    """

    assert file_count > 0
    assert file_size > 0

    from logging import handlers

    formatter = logging.Formatter('%(asctime)s %(levelname)-1.1s %(filename)s:%(lineno)s | %(message)s')

    _logger = logging.getLogger()
    _logger.setLevel(level)

    if log_file is None:
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        _logger.addHandler(console)
    else:
        rotating_file = handlers.RotatingFileHandler(log_file, maxBytes=1024 * 1024 * file_size,
                                                     backupCount=file_count)
        rotating_file.setFormatter(formatter)
        _logger.addHandler(rotating_file)


def config_remote_fetcher(fetcher: RemoteConfigFetcher, interval: int = 300):
    """
    config a remote configuration fetcher, which will pull the settings on every `refresh_interval`
    Args:
        fetcher: sub class of `RemoteConfigFetcher`
        interval: how long should cfg4py to pull the configuration from remote

    Returns:

    """
    global _remote_fetcher
    _remote_fetcher = fetcher

    _scheduler.add_job(_refresh, 'interval', seconds=interval)
    _scheduler.start()


def build(save_to: str):
    global _cfg_obj
    with open(os.path.join(os.path.dirname(__file__), "config.py"), "r") as origin:
        lines = origin.readlines()
        lines.append("\n")

    no_instance = [
        f"{' ' * 4}def __init__(self):\n",
        f"{' ' * 8}raise TypeError('Do NOT instantiate this class')\n",
    ]
    lines.extend(no_instance)
    with open(save_to, encoding='utf-8', mode="w") as f:
        lines = _schema_from_obj_(_cfg_obj, lines)
        f.writelines("".join(lines))


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
                lines.append('\n')
                lines.append(f"{' ' * 4 * depth}class {name}:\n")
                _schema_from_obj_(child, lines, depth)
            else:
                _type = f"{type(child)}"
                _type = re.sub(r".*\'(.*)\'>", r"\1", _type)
                if _type != 'NoneType':
                    lines.append(f"{' ' * 4 * depth}{name}: Optional[{_type}] = None\n")
                else:
                    lines.append(f"{' ' * 4 * depth}{name} = None\n")
    else:
        print(obj)

    return lines


def init(local_cfg_path: str = None, dump_on_change=True):
    """
    create cfg object.
    Args:
        local_cfg_path: the directory name where your configuration files exist
        dump_on_change: if configuration is updated, whether or not to dump them into log file

    Returns:
    """
    global _local_config_dir, _dump_on_change, _remote_fetcher, _local_observer, _cfg_obj, _cfg_local, _cfg_remote

    _dump_on_change = dump_on_change
    if local_cfg_path:
        _local_config_dir = os.path.expanduser(local_cfg_path)

        # handle local configuration file change
        _local_observer = Observer()
        _local_observer.schedule(LocalConfigChangeHandler(), _local_config_dir, recursive=False)
        _local_observer.start()

        _cfg_local = _load_from_local_file()
        update_config(_mixin(_cfg_remote, _cfg_local))

        # todo: will this overwrite existing file occasionally?
        save_to = os.path.join(_local_config_dir, "cfg4py_auto_gen.py")
        build(save_to)
    return _cfg_obj


def update_config(conf: dict):
    global _cfg_obj

    if 'logging' in conf:
        _process_logging_settings(conf["logging"])

        del conf['logging']

    if _dump_on_change:
        logger.info("configuration is\n%s", json.dumps(conf, indent=4, ensure_ascii=False))

    _to_obj(_cfg_obj, conf)
    return _cfg_obj


def _process_logging_settings(conf: dict):
    logging.config.dictConfig(conf)


def _guess_loader():
    files = os.listdir(_local_config_dir)
    counter = {
        ".yml":  0,
        ".yaml": 0,
        ".json": 0
    }

    for f in files:
        _, ext = os.path.splitext(f)
        if ext == '.yml':
            counter[ext] += 1
        elif ext == '.yaml':
            counter[ext] += 1
        elif ext == ".json":
            counter[ext] += 1

    _max = 0
    ext = ''
    for key in counter.keys():
        if counter[key] > _max:
            _max = counter[key]
            ext = key

    if ext in [".yml", ".yaml"]:
        # noinspection PyPackageRequirements
        from ruamel.yaml import YAML
        yaml = YAML(typ='safe')
        return yaml.load, ext
    if ext in [".json"]:
        return json.load, ext

def get_config_dir():
    return _local_config_dir

def _load_from_local_file() -> dict:
    """
    read configuration hierarchically from disk
    Args:

    Returns:

    Todo: add other known file format support with third-party parsers
    """
    conf = {}
    loader, ext = _guess_loader()

    role = os.getenv(envar, '')
    logger.info("server role is %s", role)
    if role == '':
        msg = f"You must config environment variables {envar} as one of 'DEV, TEST, PRODUCTION'"
        raise EnvironmentError(msg)
    try:
        with open(os.path.join(_local_config_dir, f"defaults{ext}"), "r", encoding='utf-8') as base:
            conf = loader(base)

        if role == 'PRODUCTION':
            with open(os.path.join(_local_config_dir, f"production{ext}"), "r", encoding='utf-8') as prod:
                _prod = loader(prod)
                _mixin(conf, _prod)

        elif role == 'TEST':
            with open(os.path.join(_local_config_dir, f"test{ext}"), "r", encoding='utf-8') as test:
                _test = loader(test)
                _mixin(conf, _test)

        else:
            with open(os.path.join(_local_config_dir, f"dev{ext}"), "r", encoding='utf-8') as dev:
                _dev = loader(dev)
                _mixin(conf, _dev)
    except FileNotFoundError as e:
        if e.filename.find('defaults') != -1:
            raise FileNotFoundError("Failed to find default configuration file")
    except Exception as e:
        logger.exception(e)

    return conf


# noinspection PyUnusedLocal
def config_server_role(role: str):
    os.environ[envar] = role
