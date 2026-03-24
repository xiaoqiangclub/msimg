import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from cli_anything.msimg.core.project import ProjectManager
from cli_anything.msimg.core.session import SessionManager
from cli_anything.msimg.core.config import ConfigManager
from cli_anything.msimg.core.export import ExportManager


class TestProjectManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_manager = ProjectManager(self.temp_dir)

    def test_init_project(self):
        result = self.project_manager.init_project()
        self.assertTrue(result)

        # 检查配置文件是否存在
        config_file = Path(self.temp_dir) / ".msimg_config.json"
        self.assertTrue(config_file.exists())

    def test_set_and_get_api_key(self):
        test_key = "test_api_key_123"
        result = self.project_manager.set_api_key(test_key)
        self.assertTrue(result)

        retrieved_key = self.project_manager.get_api_key()
        self.assertEqual(retrieved_key, test_key)


class TestSessionManager(unittest.TestCase):
    def setUp(self):
        self.session_manager = SessionManager()

    def test_session_lifecycle(self):
        session_id = self.session_manager.start_session("test")
        self.assertIsNotNone(session_id)
        self.assertTrue(self.session_manager.is_session_active())

        info = self.session_manager.get_session_info()
        self.assertIn("id", info)
        self.assertIn("start_time", info)

        result = self.session_manager.end_session()
        self.assertTrue(result)
        self.assertFalse(self.session_manager.is_session_active())


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.temp_config_file = tempfile.mktemp(suffix=".json")
        self.config_manager = ConfigManager(self.temp_config_file)

    def test_config_operations(self):
        # 测试设置和获取配置
        self.config_manager.set("test_key", "test_value")
        value = self.config_manager.get("test_key")
        self.assertEqual(value, "test_value")

        # 测试嵌套键
        self.config_manager.set("nested.key", "nested_value")
        value = self.config_manager.get("nested.key")
        self.assertEqual(value, "nested_value")

    def test_default_config(self):
        # 测试默认配置值
        api_key = self.config_manager.get("api_key")
        self.assertEqual(api_key, "")

        default_model = self.config_manager.get("default_model")
        self.assertEqual(default_model, "qwen")

    def test_extended_config_options(self):
        # 测试扩展的配置选项
        self.config_manager.set("submit_timeout", 60)
        self.config_manager.set("poll_timeout", 600)
        self.config_manager.set("download_timeout", 120)
        self.config_manager.set("poll_interval", 10)
        self.config_manager.set("retry_delay", 5.0)
        self.config_manager.set("retry_on_network_error", False)
        self.config_manager.set("upload_on_success", True)
        self.config_manager.set("notification_mode", "ALL")

        self.assertEqual(self.config_manager.get("submit_timeout"), 60)
        self.assertEqual(self.config_manager.get("poll_timeout"), 600)
        self.assertEqual(self.config_manager.get("download_timeout"), 120)
        self.assertEqual(self.config_manager.get("poll_interval"), 10)
        self.assertEqual(self.config_manager.get("retry_delay"), 5.0)
        self.assertEqual(self.config_manager.get("retry_on_network_error"), False)
        self.assertEqual(self.config_manager.get("upload_on_success"), True)
        self.assertEqual(self.config_manager.get("notification_mode"), "ALL")

    def test_image_upload_config(self):
        # 测试图床上传配置
        self.config_manager.set("image_upload.qiniu_access_key", "qiniu_test_key")
        self.config_manager.set("image_upload.qiniu_secret_key", "qiniu_test_secret")
        self.config_manager.set("image_upload.qiniu_bucket", "test_bucket")
        self.config_manager.set("image_upload.qiniu_domain", "test.domain.com")

        self.assertEqual(self.config_manager.get("image_upload.qiniu_access_key"), "qiniu_test_key")
        self.assertEqual(self.config_manager.get("image_upload.qiniu_secret_key"), "qiniu_test_secret")
        self.assertEqual(self.config_manager.get("image_upload.qiniu_bucket"), "test_bucket")
        self.assertEqual(self.config_manager.get("image_upload.qiniu_domain"), "test.domain.com")


class TestExportManager(unittest.TestCase):
    def setUp(self):
        self.export_manager = ExportManager()
        self.temp_dir = tempfile.mkdtemp()

    def test_json_export(self):
        test_data = {"key": "value", "number": 123}
        output_path = os.path.join(self.temp_dir, "test.json")

        result = self.export_manager.export_json(test_data, output_path)
        self.assertTrue(result)

        # 验证文件内容
        import json
        with open(output_path, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        self.assertEqual(loaded_data, test_data)

    def test_csv_export(self):
        test_data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25}
        ]
        output_path = os.path.join(self.temp_dir, "test.csv")

        result = self.export_manager.export_csv(test_data, output_path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_path))


if __name__ == '__main__':
    unittest.main()