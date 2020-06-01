"""Top-level package for Cfg4Py."""
from cfg4py.core import (
    RemoteConfigFetcher, enable_logging, config_remote_fetcher, init,
    update_config, RedisConfigFetcher, config_server, envar, _cfg_obj)

__author__ = """Aaron Yang"""
__email__ = 'code@jieyu.ai'
__version__ = "__version__ = '0.6.0'"


def get_instance():
    return _cfg_obj


__all__ = ['RemoteConfigFetcher', 'enable_logging', 'config_remote_fetcher', 'init', 'update_config',
           'RedisConfigFetcher', 'config_server', 'envar', 'get_instance']
