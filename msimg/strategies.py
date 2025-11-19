# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# GitHub：https://github.com/xiaoqiangclub
# 邮箱：xiaoqiangclub@hotmail.com
# 创建时间：2025-01-20 10:00:00
# 文件描述：策略枚举定义
# 文件路径：msimg/strategies.py

from enum import Enum


class SelectionStrategy(Enum):
    """选择策略枚举"""
    RANDOM = "random"              # 随机选择
    SEQUENTIAL = "sequential"      # 顺序选择（从第一个开始）
    ROUND_ROBIN = "round_robin"    # 轮询选择（记住上次位置）


class NotificationMode(Enum):
    """通知模式枚举"""
    SUCCESS = "success"            # 仅发送成功消息
    ERROR = "error"                # 仅发送错误消息
    ALL = "all"                    # 发送所有消息（成功和错误）
    NONE = "none"                  # 不发送消息