import os
import tempfile
import unittest
from pathlib import Path

import cfg4py


class TestPathExpansion(unittest.TestCase):
    def test_path_expansion_in_config(self):
        # 创建临时目录用于测试
        test_dir = tempfile.mkdtemp()
        config_file = os.path.join(test_dir, "defaults.yaml")

        # 创建带有路径展开宏的测试配置
        config_content = """
test_path: ${path:~/test.log}
        """

        with open(config_file, "w") as f:
            f.write(config_content)

        # 初始化配置
        cfg = cfg4py.init(test_dir, strict=False)

        # 验证路径是否正确展开
        expected_path = os.path.expanduser("~/test.log")
        self.assertEqual(cfg.test_path, expected_path)


if __name__ == "__main__":
    unittest.main()
