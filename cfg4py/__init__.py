"""Top-level package for Cfg4Py."""
from cfg4py.core import (
    RemoteConfigFetcher, enable_logging, config_remote_fetcher, init,
    update_config, RedisConfigFetcher, config_server_role, envar, _cfg_obj,
    get_config_dir)

__author__ = """Aaron Yang"""
__email__ = 'code@jieyu.ai'
__version__ = "__version__ = '0.7.0'"


def get_instance():
    return _cfg_obj


__all__ = ['RemoteConfigFetcher', 'enable_logging', 'config_remote_fetcher', 'init',
           'update_config',
           'RedisConfigFetcher', 'config_server_role', 'envar', 'get_instance',
           'get_config_dir']
