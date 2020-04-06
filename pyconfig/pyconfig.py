"""Main module."""
import asyncio
import collections
import functools
import json
import logging.config
import os

import yaml
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


def mixin(d, u):
    """
    if  value x in "keyx:valuex" pair is list, it's will be replaced
    :param d:
    :param u:
    :return:
    """
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = mixin(d.get(k, {}), v)
        else:
            d[k] = v
    return d


class DictProxy(object):
    def __init__(self, obj):
        self.obj = obj

    def __getitem__(self, key):
        return wrap(self.obj[key])

    def __getattr__(self, key):
        try:
            return wrap(getattr(self.obj, key))
        except AttributeError:
            try:
                return self.get(key, None)
            except KeyError:
                raise AttributeError(key)


class ListProxy(object):
    def __init__(self, obj):
        self.obj = obj

    def __getitem__(self, key):
        return wrap(self.obj[key])


def wrap(value):
    if isinstance(value, dict):
        return DictProxy(value)
    if isinstance(value, (tuple, list)):
        return ListProxy(value)
    return value


class Config(FileSystemEventHandler):
    def __init__(self):
        self._cfg = {}
        self._observer = None
        self._path = None
        self._change_handlers = set()

    def __str__(self):
        return json.dumps(self._cfg, indent=2)

    def init(self, config_folder: str):
        if os.path.isabs(config_folder):
            self._path = config_folder
        else:
            self._path = os.path.join(os.path.expanduser('~'), config_folder)

        self._load_from_local_file()
        if self._observer:
            self._observer.stop()

        self._observer = Observer()
        self._observer.schedule(self, self._path, recursive=True)
        self._observer.start()

    def add_change_handler(self, handler):
        self._change_handlers.add(handler)

    def _load_from_local_file(self, show_config=False):
        self._cfg = {}
        role = os.getenv('SERVER_ROLE', 'DEV')
        logger.info("server role is %s", role)
        try:
            with open(os.path.join(self._path, "base.yaml"), "r", encoding='utf-8') as base:
                self._cfg = yaml.safe_load(base)

            if role == 'PRODUCTION':
                with open(os.path.join(self._path, "production.yaml"), "r", encoding='utf-8') as prod:
                    _prod = yaml.safe_load(prod)
                    mixin(self._cfg, _prod)

            elif role == 'TEST':
                with open(os.path.join(self._path, "test.yaml"), "r", encoding='utf-8') as test:
                    _test = yaml.safe_load(test)
                    mixin(self._cfg, _test)

            else:
                try:
                    with open(os.path.join(self._path, "dev.yaml"), "r", encoding='utf-8') as dev:
                        _dev = yaml.safe_load(dev)
                        mixin(self._cfg, _dev)
                except FileNotFoundError:
                    pass

            if show_config:
                logger.info("configuration is\n%s", json.dumps(self._cfg, indent=4, ensure_ascii=False))
        except Exception as e:
            logger.exception(e)

    def on_modified(self, event):
        self._load_from_local_file()
        for handler in self._change_handlers:
            handler(self)

    def update(self, d):
        mixin(self._cfg, d)

    def __getattr__(self, key):
        value = self._cfg.get(key, None)
        if isinstance(value, dict):
            return DictProxy(self._cfg[key])
        else:
            return value

    def __getitem__(self, item):
        return self._cfg.get(item, None)



cfg = Config()

__all__ = ['cfg']
