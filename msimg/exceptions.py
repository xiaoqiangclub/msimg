# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# GitHub：https://github.com/xiaoqiangclub
# 邮箱：xiaoqiangclub@hotmail.com
# 创建时间：2025-01-20 10:00:00
# 文件描述：自定义异常类
# 文件路径：msimg/exceptions.py


class MsimgError(Exception):
    """msimg 基础异常类"""
    pass


class APIError(MsimgError):
    """API 调用错误"""
    pass


class NetworkError(MsimgError):
    """网络连接错误"""
    pass


class TimeoutError(MsimgError):
    """超时错误"""
    pass


class ValidationError(MsimgError):
    """参数验证错误"""
    pass