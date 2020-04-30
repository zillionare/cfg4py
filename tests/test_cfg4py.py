#!/usr/bin/env python

"""Tests for `cfg4py` package."""

import unittest
import os

import cfg4py
from cfg4py import core
import logging

from command_line import Command

logger = logging.getLogger(__name__)


class TestCfg4Py(unittest.TestCase):
    """Tests for `cfg4py` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        cfg4py.enable_logging()
        os.environ['__cfg4py_server_role__'] = 'DEV'
        self.resource_path = os.path.join(os.path.dirname(__file__), "../cfg4py/resources/")
        self.resource_path = os.path.normpath(self.resource_path)

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_create_config(self):
        """Test something."""
        logger.info("resource_path is %s", self.resource_path)
        cfg = cfg4py.init(self.resource_path)
        self.assertEqual(cfg.services.redis.host, '127.0.0.1')

    def test_001_update_config(self):
        conf = {
            "aaron": {
                "surname": "yang"
            },
            "services": {
                "redis": {
                    "host": "localhost"
                }
            }
        }

        cfg = cfg4py.update_config(conf)
        self.assertEqual('localhost', cfg.services.redis.host)

    def test_001_build(self):
        conf = {
            "aaron":    {
                "surname": "yang"
            },
            "services": {
                "redis": {
                    "host": "localhost"
                }
            }
        }

        cfg4py.update_config(conf)
        core.build(os.path.join(self.resource_path, "cfg4py_auto_gen.py"))
        try:
            import sys
            sys.path.insert(0, self.resource_path)
            # noinspection PyUnresolvedReferences
            from cfg4py_auto_gen import Config
            # no exception means the file has been generated successfully
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

    def test_002_create_config(self):
        from cfg4py.resources.cfg4py_auto_gen import Config
        os.environ['__cfg4py_server_role__'] = 'DEV'
        cfg: Config = cfg4py.init(self.resource_path)
        print("cfg.services.redis.host is", cfg.services.redis.host)

    def test_003_config_remote_fetcher(self):
        from cfg4py import RedisConfigFetcher
        from redis import StrictRedis
        import json
        r = StrictRedis('localhost',)
        r.set("my_app_config", json.dumps({
            "services": {
                "redis": {
                    "host": "192.168.3.1",
                },
                "redis2": {
                    "host": "192.168.3.2"
                }
            }
        }))

        cfg = cfg4py.init(self.resource_path)
        fetcher = RedisConfigFetcher(key="my_app_config")
        logger.info("configuring a remote fetcher")
        cfg4py.config_remote_fetcher(fetcher, 1)
        import time
        time.sleep(2)
        logger.info("please check log output to see if update_config is called at least 1 once")
        # the one from dev.yaml
        self.assertEqual(cfg.services.redis.host, '127.0.0.1')
        # the one from redis
        self.assertEqual(cfg.services.redis2.host, '192.168.3.2')

    def test_004_command_hint(self):
        cmd = Command()
        logger.info("please check the output")
        cmd.hint('pip')
        cmd.hint('pip', True)
        cmd.hint('postgres/psycopg2')
        cmd.hint('pip/tshinghua')
