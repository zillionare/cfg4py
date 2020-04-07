#!/usr/bin/env python

"""Tests for `pyconfig` package."""

import unittest

from pyconfig import pyconfig
import logging

logger = logging.getLogger(__name__)


class TestPyconfig(unittest.TestCase):
    """Tests for `pyconfig` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        pyconfig.enable_logging()

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_create_config(self):
        """Test something."""
        import os
        os.environ['__pyconfig_server_role__'] = 'DEV'

        path = os.path.join(os.path.dirname(__file__), "../pyconfig/resources/")
        path = os.path.normpath(path)

        logger.info("path is %s", path)
        cfg = pyconfig.create_config(path)
        self.assertEqual(cfg.services.redis.host, '127.0.0.1')

    def test_001_update_config(self):
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

        cfg = pyconfig.update_config(conf)
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

        pyconfig.update_config(conf)
        save_to = "/tmp/"
        pyconfig.build(os.path.join(save_to, "pyconfig_auto_gen.py"))
        try:
            import sys
            sys.path.insert(0, save_to)
            # noinspection PyUnresolvedReferences
            from pyconfig_auto_gen import Config
            # no exception means the file has been generated successfully
            self.assertTrue(True)
        except Exception as e:
            self.assertTrue(False)

    def test_002_create_config(self):
        import os
        # from pyconfig.resources.config import Config
        os.environ['__pyconfig_server_role__'] = 'DEV'
        cfg = pyconfig.create_config('/workspace/pyconfig/pyconfig/resources')
        print("cfg.services.redis.host is", cfg.services.redis.host)

    def test_003_config_remote_fetcher(self):
        from pyconfig import RedisConfigFetcher
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

        cfg = pyconfig.create_config()
        fetcher = RedisConfigFetcher(key="my_app_config")
        logger.info("configuring a remote fetcher")
        pyconfig.config_remote_fetcher(fetcher, 1)
        import time
        time.sleep(2)
        logger.info("please check log output to see if update_config is called at least 1 once")
        self.assertEqual(cfg.services.redis.host, '127.0.0.1')
