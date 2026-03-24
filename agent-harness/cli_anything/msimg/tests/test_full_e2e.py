import unittest
import tempfile
import os
import subprocess
import sys
from pathlib import Path
from io import StringIO

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from msimg import generate_image
from cli_anything.msimg.core.msimg_cli import cli
from cli_anything.msimg.core.project import ProjectManager
from cli_anything.msimg.core.session import SessionManager
from cli_anything.msimg.core.config import ConfigManager
from cli_anything.msimg.core.export import ExportManager


class TestCLISubprocess(unittest.TestCase):
    def test_cli_help(self):
        """测试CLI帮助命令"""
        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('MSIMG CLI - 魔塔社区文生图API命令行工具', result.output)

    def test_models_command(self):
        """测试models命令"""
        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(cli, ['models'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('支持的预设模型:', result.output)

    def test_sizes_command(self):
        """测试sizes命令"""
        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(cli, ['sizes'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('支持的预设尺寸:', result.output)

    def test_generate_command_missing_args(self):
        """测试generate命令缺少必要参数"""
        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(cli, ['generate'])
        # 应该返回非零退出码，因为缺少必要参数
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn('Missing option', result.output)


class TestFullWorkflow(unittest.TestCase):
    """完整的端到端工作流测试"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_api_key = "test_key_123"  # 这应该是一个模拟的密钥

    @unittest.skip("跳过需要真实API的服务测试")
    def test_full_generation_workflow(self):
        """测试完整的图片生成工作流（需要真实API）"""
        # 这个测试需要真实的API密钥才能运行
        # 在这里我们只是展示测试结构
        pass


if __name__ == '__main__':
    # 运行所有测试
    unittest.main(verbosity=2)