# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# GitHub：https://github.com/xiaoqiangclub
# 邮箱：xiaoqiangclub@hotmail.com
# 创建时间：2025-01-20 10:00:00
# 文件描述：msimg 模块入口文件，导出核心功能
# 文件路径：msimg/__init__.py

from .version import __version__, __author__, __email__
from .generator import generate_image
from .config import APIConfig
from .strategies import SelectionStrategy, NotificationMode
from .constants import SIZE_PRESETS, MODEL_PRESETS
from .exceptions import (
    MsimgError,
    APIError,
    NetworkError,
    TimeoutError,
    ValidationError,
)

# 图床上传器类
from .image_uploader import (
    # 上传器类
    SMUploader,
    ImgURLUploader,
    LuoGuoUploader,
    QiniuUploader,
    AliyunOSSUploader,
    UpyunUploader,
    GitHubUploader,
    LocalStorageUploader,

    # 便捷创建函数
    create_smms_uploader,
    create_imgurl_uploader,
    create_luoguo_uploader,
    create_qiniu_uploader,
    create_aliyun_uploader,
    create_upyun_uploader,
    create_github_uploader,
    create_local_uploader,
)

__all__ = [
    # 版本信息
    "__version__",
    "__author__",
    "__email__",

    # 核心功能
    "generate_image",

    # 配置类
    "APIConfig",

    # 策略枚举
    "SelectionStrategy",
    "NotificationMode",

    # 预设常量
    "SIZE_PRESETS",
    "MODEL_PRESETS",

    # 异常类
    "MsimgError",
    "APIError",
    "NetworkError",
    "TimeoutError",
    "ValidationError",

    # 图床上传器类
    "SMUploader",
    "ImgURLUploader",
    "LuoGuoUploader",
    "QiniuUploader",
    "AliyunOSSUploader",
    "UpyunUploader",
    "GitHubUploader",
    "LocalStorageUploader",

    # 图床便捷创建函数
    "create_smms_uploader",
    "create_imgurl_uploader",
    "create_luoguo_uploader",
    "create_qiniu_uploader",
    "create_aliyun_uploader",
    "create_upyun_uploader",
    "create_github_uploader",
    "create_local_uploader",
]
