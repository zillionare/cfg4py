#!/usr/bin/env python
"""Tests for `cfg4py` package."""
import logging
import os
import shutil
import sys
import tempfile
import time
import unittest
from unittest import mock
from unittest.mock import patch

import cfg4py
from cfg4py import core
from cfg4py.cli import Command

logger = logging.getLogger(__name__)


def early_jump(msg):
    logger.info("Mock exit: %s", msg)
    raise SystemExit


class TestCfg4Py(unittest.TestCase):
    """Tests for `cfg4py` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        cfg4py.enable_logging()
        os.environ["__cfg4py_server_role__"] = "TEST"
        self.resource_path = os.path.join(
            os.path.dirname(__file__), "../cfg4py/resources/"
        )
        self.resource_path = os.path.normpath(self.resource_path)
        self.home = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
        self.output = os.path.join(tempfile.gettempdir(), "cfg4py_test")
        shutil.rmtree(self.output, ignore_errors=True)

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_create_config(self):
        """Test something."""
        logger.info("resource_path is %s", self.resource_path)
        cfg = cfg4py.init(self.resource_path, strict=True)
        self.assertEqual(cfg.services.redis.host, "127.0.0.1")

    def test_001_update_config(self):
        conf = {
            "aaron": {"surname": "yang"},
            "services": {"redis": {"host": "localhost"}},
        }

        cfg = cfg4py.update_config(conf)
        self.assertEqual("localhost", cfg.services.redis.host)

    def test_001_build(self):
        conf = {
            "aaron": {"surname": "yang"},
            "services": {"redis": {"host": "localhost"}},
        }

        cfg4py.update_config(conf)
        core.build(os.path.join(self.resource_path, "schema.py"))
        try:
            sys.path.insert(0, self.resource_path)
            from schema import Config  # noqa

            # no exception means the file has been generated successfully
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

    def test_002_create_config(self):
        from cfg4py.resources.schema import Config

        os.environ["__cfg4py_server_role__"] = "DEV"
        cfg: Config = cfg4py.init(self.resource_path, strict=True)
        print("cfg.services.redis.host is", cfg.services.redis.host)

    def test_003_config_remote_fetcher(self):
        import json

        from redis import StrictRedis  # type: ignore

        from cfg4py import RedisConfigFetcher

        r = StrictRedis("localhost")
        r.set(
            "my_app_config",
            json.dumps(
                {
                    "services": {
                        "redis": {
                            "host": "192.168.3.1",
                        },
                        "redis2": {"host": "192.168.3.2"},
                    }
                }
            ),
        )

        cfg = cfg4py.init(self.resource_path, strict=True)
        fetcher = RedisConfigFetcher(key="my_app_config")
        logger.info("configuring a remote fetcher")
        cfg4py.config_remote_fetcher(fetcher, 0.1)
        time.sleep(0.5)
        logger.info(
            "please check log output to see if update_config is called at least 1 once"
        )
        # the one from dev.yaml
        self.assertEqual(cfg.services.redis.host, "127.0.0.1")
        # the one from redis
        self.assertEqual(cfg.services.redis2.host, "192.168.3.2")

    def test_004_command_hint(self):
        cmd = Command()
        logger.info("please check the output")
        cmd.hint("pip")
        cmd.hint("pip", True)
        cmd.hint("postgres/psycopg2")
        cmd.hint("postgres/psycopg2", True)
        cmd.hint("pip/tshinghua")

    def test_005_sigleton(self):
        cfg1 = cfg4py.get_instance()
        cfg2 = cfg4py.get_instance()

        self.assertEqual(id(cfg1), id(cfg2))

    def test_006_scaffold(self):
        cmd = Command()

        # folder not exists, create
        answers = [self.output, "Y", "11"]
        with unittest.mock.patch("builtins.input", side_effect=answers):
            cmd.scaffold(None)

        self.assertTrue(os.path.exists(os.path.join(self.output, "defaults.yaml")))

        # files exists, ask for dst again, then we give non-exist path and 'Q' to quit
        answers = ["", "Q"]

        with unittest.mock.patch("builtins.input", side_effect=answers):
            try:
                with unittest.mock.patch(
                    "sys.exit", lambda *args: early_jump("user pressed Q")
                ):
                    cmd.scaffold(self.output)
                self.assertTrue(False, "sys exit not triggered")
            except SystemExit:
                self.assertTrue(True)

        # path exists and the folder is empty
        shutil.rmtree(self.output, ignore_errors=True)
        os.makedirs(self.output, exist_ok=True)
        answers = ["31"]
        with unittest.mock.patch("builtins.input", side_effect=answers):
            cmd.scaffold(self.output)

        self.assertTrue(os.path.exists(os.path.join(self.output, "defaults.yaml")))

        # non exist index
        shutil.rmtree(self.output, ignore_errors=True)
        os.makedirs(self.output, exist_ok=True)
        with unittest.mock.patch("builtins.input", side_effect=["99"]):
            cmd.scaffold(self.output)

        # chose logging
        shutil.rmtree(self.output, ignore_errors=True)
        os.makedirs(self.output, exist_ok=True)
        with unittest.mock.patch("builtins.input", side_effect=["0"]):
            cmd.scaffold(self.output)

    def test_007_cmd_build(self):
        cmd = Command()

        os.makedirs(self.output)
        with unittest.mock.patch("builtins.input", side_effect=["31"]):
            cmd.scaffold(self.output)

        # normal run
        cmd.build(self.output)
        cfg = cfg4py.init(self.output, strict=True)
        self.assertEqual(cfg.postgres.dsn, "dbname=test user=postgres password=secret")

        # path not exists run
        shutil.rmtree(self.output)
        try:
            with unittest.mock.patch(
                "sys.exit", lambda *args: early_jump("Path not exists")
            ):
                cmd.build(self.output)
            self.assertTrue(False, "sys.exit not triggered")
        except SystemExit:
            self.assertTrue(True)

        # no files in self.output
        os.makedirs(self.output, exist_ok=True)
        try:
            with unittest.mock.patch(
                "sys.exit", lambda *args: early_jump("no files in folder")
            ):
                cmd.build(self.output)
            self.assertTrue(False, "sys.exit not triggered")
        except SystemExit:
            self.assertTrue(True)

    def test_008_enable_logging(self):
        os.makedirs(self.output, 0o777, exist_ok=True)
        cfg4py.enable_logging(
            log_file=os.path.join(self.output, "cfg4py.log"),
            file_size=1e-6,
            file_count=3,
        )
        logger.info("%s", ["test log"])

    def test_009_set_server_role(self):
        cmd = Command()
        cmd.set_server_role()

    def test_010_read_envar(self):
        tmpdir = tempfile.gettempdir()
        cfg4dir = os.path.join(tmpdir, "cfg4py_test")
        config_file = os.path.join(cfg4dir, "defaults.yaml")
        os.makedirs(cfg4dir, 0o777, exist_ok=True)
        os.environ["account"] = "aaron"
        content = ["account: ${account}", "\n"]

        with open(config_file, "w+") as f:
            f.writelines("\n".join(content))

        cfg = cfg4py.init(cfg4dir, strict=True)
        self.assertEqual(cfg.account, "aaron")

    def test_011_non_strict_mode(self):
        os.environ[cfg4py.envar] = ""
        cfg = cfg4py.init(self.resource_path, strict=False)
        self.assertEqual(cfg.services.redis.host, "localhost")

    def test_012_only_yml_files(self):
        tmpdir = tempfile.gettempdir()
        cfg4dir = os.path.join(tmpdir, "cfg4py_test/")
        os.makedirs(cfg4dir, 0o777, exist_ok=True)

        os.environ["account"] = "aaron"
        content = ["account: ${account}", "\n"]

        config_file = os.path.join(cfg4dir, "defaults.yaml")

        with open(config_file, "w+") as f:
            f.writelines("\n".join(content))

        cfg4py.init(cfg4dir)

        with patch(
            "cfg4py.core._load_from_local_file",
            side_effect=Exception("I should NOT be invoked"),
        ):
            touchme = os.path.join(cfg4dir, "ignore_me.test")

            with open(touchme, "w") as f:
                f.writelines("whenever you see this file, delete it")

    @mock.patch("cfg4py.core.LocalConfigChangeHandler.dispatch")
    def test_013_watch(self, mocked_handler):
        """test watch file change"""
        tmpdir = tempfile.gettempdir()
        cfg4dir = os.path.join(tmpdir, "cfg4py_test/")
        os.makedirs(cfg4dir, 0o777, exist_ok=True)

        os.environ["account"] = "aaron"
        content = ["account: ${account}", "\n"]

        config_file = os.path.join(cfg4dir, "defaults.yaml")

        with open(config_file, "w+") as f:
            f.writelines("\n".join(content))

        cfg4py.init(cfg4dir)

        for i in range(3):
            time.sleep(1)
            with open(config_file, "w+") as f:
                f.writelines(f"\n{i}".join(content))

        # signaled twice (closed, modified) for each write
        self.assertTrue(mocked_handler.call_count > 3)

    def test_014_check_logging(self):
        # according to issue #4, we should return logging settings
        cfg = cfg4py.init(self.resource_path)
        self.assertTrue(getattr(cfg, "logging", None))
        self.assertTrue(cfg.logging.get("handlers"))
