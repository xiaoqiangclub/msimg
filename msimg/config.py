# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# GitHub：https://github.com/xiaoqiangclub
# 邮箱：xiaoqiangclub@hotmail.com
# 创建时间：2025-01-20 10:00
# 文件描述：配置类定义
# 文件路径：msimg/config.py

from dataclasses import dataclass
from typing import Optional
from .constants import DEFAULT_BASE_URL


@dataclass
class APIConfig:
    """
    API 配置类
    
    属性:
        api_key: API 密钥（必需）
        base_url: API 基础 URL（可选，默认使用魔塔官方地址）
        name: API 名称，用于日志显示（可选）
    """
    api_key: str
    base_url: str = DEFAULT_BASE_URL
    name: Optional[str] = None
    
    def __post_init__(self):
        if self.name is None:
            # 如果未设置名称，使用 base_url 作为标识
            self.name = self.base_url.split("//")[-1].split("/")[0]