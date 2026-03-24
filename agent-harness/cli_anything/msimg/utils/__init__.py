"""
MSIMG CLI 工具函数
"""

import os
import sys
from pathlib import Path


def get_msimg_root():
    """获取MSIMG项目根目录"""
    # 尝试从当前文件向上查找msimg目录
    current_path = Path(__file__).parent
    for parent in current_path.parents:
        if (parent / "msimg" / "__init__.py").exists():
            return parent
    # 如果没找到，返回当前目录
    return Path.cwd()


def ensure_msimg_available():
    """确保MSIMG模块可用"""
    msimg_root = get_msimg_root()
    if str(msimg_root) not in sys.path:
        sys.path.insert(0, str(msimg_root))


def format_size(size_tuple):
    """格式化尺寸显示"""
    if isinstance(size_tuple, (tuple, list)) and len(size_tuple) == 2:
        return f"{size_tuple[0]}x{size_tuple[1]}"
    return str(size_tuple)


def validate_image_path(path):
    """验证图片路径"""
    if not os.path.exists(path):
        return False, "文件不存在"

    valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
    ext = os.path.splitext(path)[1].lower()
    if ext not in valid_extensions:
        return False, f"不支持的图片格式: {ext}"

    return True, "有效"