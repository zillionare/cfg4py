#!/usr/bin/env python

"""Tests for `cfg4py` package."""

import unittest

from cfg4py import cfg4py
import logging

logger = logging.getLogger(__name__)


class TestCfg4Py(unittest.TestCase):
    """Tests for `cfg4py` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        cfg4py.enable_logging()

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_create_config(self):
        """Test something."""
        import os
        os.environ['__cfg4py_server_role__'] = 'DEV'

        path = os.path.join(os.path.dirname(__file__), "../cfg4py/resources/")
        path = os.path.normpath(path)

        logger.info("path is %s", path)
        cfg = cfg4py.create_config(path)
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
        import os
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
        save_to = "/tmp/"
        cfg4py.build(os.path.join(save_to, "cfg4py_auto_gen.py"))
        try:
            import sys
            sys.path.insert(0, save_to)
            # noinspection PyUnresolvedReferences
            from cfg4py_auto_gen import Config
            # no exception means the file has been generated successfully
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

    def test_002_create_config(self):
        import os
        # from cfg4py.resources.config import Config
        os.environ['__cfg4py_server_role__'] = 'DEV'
        cfg = cfg4py.create_config('/workspace/cfg4py/cfg4py/resources')
        print("cfg.services.redis.host is", cfg.services.redis.host)

    def test_003_config_remote_fetcher(self):
        from cfg4py import RedisConfigFetcher
        from redis import StrictRedis
        import json
        r = StrictRedis('localhost')
        r.set("my_app_config", json.dumps({
            "services": {
                "redis": {
                    "host": "127.0.0.1"
                }
            }
        }))

        cfg = cfg4py.create_config()
        fetcher = RedisConfigFetcher(key="my_app_config")
        logger.info("configuring a remote fetcher")
        cfg4py.config_remote_fetcher(fetcher, 1)
        import time
        time.sleep(2)
        logger.info("please check log output to see if update_config is called at least 1 once")
        self.assertEqual(cfg.services.redis.host, '127.0.0.1')
