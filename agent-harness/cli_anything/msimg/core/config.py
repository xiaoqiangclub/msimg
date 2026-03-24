"""
MSIMG CLI 核心模块 - 配置管理
"""

import json
from typing import Any, Dict, Optional
from pathlib import Path


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置管理器

        Args:
            config_file: 配置文件路径，默认为 ~/.msimg/config.json
        """
        if config_file:
            self.config_file = Path(config_file)
        else:
            home_dir = Path.home()
            self.config_file = home_dir / ".msimg" / "config.json"

        # 确保配置目录存在
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # 初始化默认配置
        self.default_config = {
            "api_key": "",
            "default_model": "qwen",
            "default_size": "16:9",
            "save_directory": "./generated_images",
            "enable_failover": True,
            "max_retries": 3,
            "verbose": True,
            "submit_timeout": 30,
            "poll_timeout": 300,
            "download_timeout": 60,
            "poll_interval": 5,
            "retry_delay": 2.0,
            "retry_on_network_error": True,
            "upload_on_success": False,
            "notification_mode": "NONE",
            "image_upload": {
                "default_uploader": "smms",
                "smms_token": "",
                "imgurl_token": "",
                "imgurl_uid": "",
                "luoguo_enabled": True,
                "qiniu_access_key": "",
                "qiniu_secret_key": "",
                "qiniu_bucket": "",
                "qiniu_domain": "",
                "aliyun_access_key_id": "",
                "aliyun_access_key_secret": "",
                "aliyun_endpoint": "",
                "aliyun_bucket_name": "",
                "upyun_bucket": "",
                "upyun_username": "",
                "upyun_password": "",
                "upyun_domain": "",
                "github_token": "",
                "github_repo": "",
                "github_branch": "main",
                "github_use_jsdelivr": True,
                "local_storage_dir": "./uploads",
                "local_base_url": "http://localhost/uploads"
            },
            "proxy": {
                "http": "",
                "https": ""
            }
        }

    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 合并默认配置，确保所有键都存在
                    config = self.default_config.copy()
                    config.update(user_config)
                    return config
            else:
                return self.default_config.copy()
        except Exception as e:
            print(f"⚠️  无法加载配置文件，使用默认配置: {str(e)}")
            return self.default_config.copy()

    def save_config(self, config: Dict[str, Any]) -> bool:
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ 保存配置失败: {str(e)}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            key: 配置键，支持嵌套键如 'image_upload.smms_token'
            default: 默认值

        Returns:
            配置值
        """
        config = self.load_config()

        # 支持嵌套键访问
        keys = key.split('.')
        value = config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> bool:
        """
        设置配置值

        Args:
            key: 配置键，支持嵌套键如 'image_upload.smms_token'
            value: 配置值

        Returns:
            是否设置成功
        """
        config = self.load_config()

        # 支持嵌套键设置
        keys = key.split('.')
        target = config
        for k in keys[:-1]:
            if k not in target or not isinstance(target, dict):
                target[k] = {}
            target = target[k]

        target[keys[-1]] = value

        return self.save_config(config)

    def reset(self) -> bool:
        """重置为默认配置"""
        return self.save_config(self.default_config)

    def get_api_key(self) -> str:
        """获取API密钥"""
        return self.get("api_key", "")

    def set_api_key(self, api_key: str) -> bool:
        """设置API密钥"""
        return self.set("api_key", api_key)

    def get_submit_timeout(self) -> int:
        """获取提交超时时间"""
        return self.get("submit_timeout", 30)

    def set_submit_timeout(self, timeout: int) -> bool:
        """设置提交超时时间"""
        return self.set("submit_timeout", timeout)

    def get_poll_timeout(self) -> int:
        """获取轮询超时时间"""
        return self.get("poll_timeout", 300)

    def set_poll_timeout(self, timeout: int) -> bool:
        """设置轮询超时时间"""
        return self.set("poll_timeout", timeout)

    def get_download_timeout(self) -> int:
        """获取下载超时时间"""
        return self.get("download_timeout", 60)

    def set_download_timeout(self, timeout: int) -> bool:
        """设置下载超时时间"""
        return self.set("download_timeout", timeout)

    def get_poll_interval(self) -> int:
        """获取轮询间隔时间"""
        return self.get("poll_interval", 5)

    def set_poll_interval(self, interval: int) -> bool:
        """设置轮询间隔时间"""
        return self.set("poll_interval", interval)

    def get_retry_delay(self) -> float:
        """获取重试延迟时间"""
        return self.get("retry_delay", 2.0)

    def set_retry_delay(self, delay: float) -> bool:
        """设置重试延迟时间"""
        return self.set("retry_delay", delay)

    def get_retry_on_network_error(self) -> bool:
        """获取网络错误时是否重试"""
        return self.get("retry_on_network_error", True)

    def set_retry_on_network_error(self, retry: bool) -> bool:
        """设置网络错误时是否重试"""
        return self.set("retry_on_network_error", retry)

    def get_upload_on_success(self) -> bool:
        """获取生成成功后是否自动上传"""
        return self.get("upload_on_success", False)

    def set_upload_on_success(self, upload: bool) -> bool:
        """设置生成成功后是否自动上传"""
        return self.set("upload_on_success", upload)

    def get_notification_mode(self) -> str:
        """获取通知模式"""
        return self.get("notification_mode", "NONE")

    def set_notification_mode(self, mode: str) -> bool:
        """设置通知模式"""
        return self.set("notification_mode", mode)