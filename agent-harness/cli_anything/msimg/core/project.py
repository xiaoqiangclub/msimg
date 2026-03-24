"""
MSIMG CLI 核心模块 - 项目管理
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


class ProjectManager:
    """项目管理器"""

    def __init__(self, project_dir: Optional[str] = None):
        """
        初始化项目管理器

        Args:
            project_dir: 项目目录，默认为当前目录
        """
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.config_file = self.project_dir / ".msimg_config.json"

    def init_project(self) -> bool:
        """初始化项目"""
        try:
            if self.config_file.exists():
                print(f"⚠️  项目已在 {self.project_dir} 初始化过")
                return False

            default_config = {
                "api_key": "",
                "default_model": "qwen",
                "default_size": "16:9",
                "save_directory": "./generated_images",
                "enable_failover": True,
                "max_retries": 3
            }

            self.save_config(default_config)
            print(f"✅ 项目已初始化: {self.project_dir}")
            print(f"📝 配置文件: {self.config_file}")
            return True
        except Exception as e:
            print(f"❌ 初始化项目失败: {str(e)}")
            return False

    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            print(f"❌ 加载配置失败: {str(e)}")
            return {}

    def save_config(self, config: Dict[str, Any]) -> bool:
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ 保存配置失败: {str(e)}")
            return False

    def get_api_key(self) -> str:
        """获取API密钥"""
        config = self.load_config()
        return config.get("api_key", "")

    def set_api_key(self, api_key: str) -> bool:
        """设置API密钥"""
        config = self.load_config()
        config["api_key"] = api_key
        return self.save_config(config)