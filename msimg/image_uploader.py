# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# GitHub：https://github.com/xiaoqiangclub
# 邮箱：xiaoqiangclub@hotmail.com
# 创建时间：2025-01-20 10:00:00
# 文件描述：图床上传工具集合，支持多种常见图床服务和多种图片输入格式
# 文件路径：msimg/image_uploader.py

"""
msimg 图床上传模块

支持的图床：
- SM.MS (免费，5MB限制，国内优化)
- ImgURL (免费，10MB限制)
- 路过图床 (免费，10MB限制)
- 七牛云 (需要账号，有免费额度)
- 阿里云 OSS (需要账号，有免费额度)
- 又拍云 (需要账号，有免费额度)
- GitHub (免费，配合 CDN 使用)
- 本地存储 (用于自建服务)

支持的图片输入格式：
- PIL.Image.Image 对象
- 本地文件路径 (str)
- 网络图片 URL (http/https)
- Base64 编码字符串
- 图片字节流 (bytes)

快速开始：
    >>> from msimg.image_uploader import create_smms_uploader
    >>> 
    >>> # 创建图床上传函数
    >>> uploader = create_smms_uploader(api_token='your-token')
    >>> 
    >>> # 上传本地图片
    >>> url = uploader('/path/to/image.jpg')
    >>> 
    >>> # 上传网络图片
    >>> url = uploader('https://example.com/image.jpg')
    >>> 
    >>> # 上传 PIL.Image 对象
    >>> from PIL import Image
    >>> img = Image.open('test.jpg')
    >>> url = uploader(img)
    >>> 
    >>> # 上传 Base64 图片
    >>> url = uploader('data:image/png;base64,iVBORw0KGgo...')

配合 msimg 使用：
    >>> from msimg import generate_image
    >>> from msimg.image_uploader import create_smms_uploader
    >>> 
    >>> uploader = create_smms_uploader(api_token='your-token')
    >>> 
    >>> result = generate_image(
    ...     prompt="test",
    ...     api_configs="key",
    ...     image_upload_callbacks=[uploader],
    ...     upload_on_success=True
    ... )
"""

import base64
import hashlib
import requests
import re
from pathlib import Path
from typing import Optional, Union
from datetime import datetime
from io import BytesIO

try:
    from PIL import Image
except ImportError:
    raise ImportError("请安装 Pillow: pip install Pillow")


# ============================================================================
# 类型定义
# ============================================================================

ImageInput = Union[str, bytes, Image.Image]
"""
支持的图片输入类型：
- str: 本地路径、网络URL、Base64字符串
- bytes: 图片字节流
- PIL.Image.Image: PIL图片对象
"""


# ============================================================================
# 基础工具函数
# ============================================================================

def _is_base64(s: str) -> bool:
    """
    判断字符串是否为 Base64 编码
    
    :param s: 待判断的字符串
    :return: 是否为 Base64
    """
    # 检查是否为 data URI 格式
    if s.startswith('data:image/'):
        return True

    # 检查是否为纯 Base64 字符串
    # Base64 字符集：A-Z, a-z, 0-9, +, /, =
    if re.match(r'^[A-Za-z0-9+/]*={0,2}$', s) and len(s) % 4 == 0:
        try:
            base64.b64decode(s, validate=True)
            return True
        except Exception:
            return False

    return False


def _decode_base64_image(base64_str: str) -> bytes:
    """
    解码 Base64 图片
    
    :param base64_str: Base64 字符串（支持 data URI 格式）
    :return: 图片字节流
    """
    # 处理 data URI 格式: data:image/png;base64,xxxxx
    if base64_str.startswith('data:image/'):
        # 提取 Base64 部分
        base64_str = base64_str.split(',', 1)[1]

    # 解码
    try:
        image_data = base64.b64decode(base64_str)
        return image_data
    except Exception as e:
        raise ValueError(f"Base64 解码失败: {e}")


def _image_to_bytes(image: ImageInput, format: str = 'PNG') -> tuple:
    """
    将各种格式的图片转换为字节流
    
    支持的输入格式：
    - PIL.Image.Image 对象
    - 本地文件路径 (str)
    - 网络图片 URL (http/https)
    - Base64 编码字符串 (data:image/... 或纯 Base64)
    - 图片字节流 (bytes)
    
    :param image: 图片输入
    :param format: 输出格式（PNG/JPEG/WEBP）
    :return: (字节数据, 文件名)
    
    示例：
        >>> # PIL.Image 对象
        >>> from PIL import Image
        >>> img = Image.open('test.jpg')
        >>> data, filename = _image_to_bytes(img)
        
        >>> # 本地路径
        >>> data, filename = _image_to_bytes('/path/to/image.jpg')
        
        >>> # 网络 URL
        >>> data, filename = _image_to_bytes('https://example.com/image.jpg')
        
        >>> # Base64 (data URI)
        >>> data, filename = _image_to_bytes('data:image/png;base64,iVBORw0KGgo...')
        
        >>> # Base64 (纯字符串)
        >>> data, filename = _image_to_bytes('iVBORw0KGgoAAAANSUhEUgAA...')
        
        >>> # 字节流
        >>> with open('image.jpg', 'rb') as f:
        ...     data, filename = _image_to_bytes(f.read())
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # 处理 PIL.Image 对象
    if isinstance(image, Image.Image):
        buffer = BytesIO()
        image.save(buffer, format=format)
        file_data = buffer.getvalue()
        filename = f"msimg_{timestamp}.{format.lower()}"
        return file_data, filename

    # 处理字节流
    elif isinstance(image, bytes):
        file_data = image
        filename = f"msimg_{timestamp}.{format.lower()}"
        return file_data, filename

    # 处理字符串（路径、URL、Base64）
    elif isinstance(image, str):
        # 1. 检查是否为网络 URL
        if image.startswith(('http://', 'https://')):
            try:
                response = requests.get(image, timeout=10)
                response.raise_for_status()
                file_data = response.content
                # 尝试从 URL 提取文件名
                url_path = image.split('?')[0]  # 去除查询参数
                url_filename = Path(url_path).name
                if url_filename and '.' in url_filename:
                    filename = url_filename
                else:
                    filename = f"remote_{timestamp}.jpg"
                return file_data, filename
            except Exception as e:
                raise ValueError(f"下载网络图片失败: {e}")

        # 2. 检查是否为 Base64
        elif _is_base64(image):
            try:
                file_data = _decode_base64_image(image)
                filename = f"base64_{timestamp}.{format.lower()}"
                return file_data, filename
            except Exception as e:
                raise ValueError(f"Base64 解码失败: {e}")

        # 3. 当作本地文件路径处理
        else:
            try:
                file_path = Path(image)
                if not file_path.exists():
                    raise FileNotFoundError(f"文件不存在: {image}")

                with open(file_path, 'rb') as f:
                    file_data = f.read()
                filename = file_path.name
                return file_data, filename
            except Exception as e:
                raise ValueError(f"读取本地文件失败: {e}")

    else:
        raise TypeError(
            f"不支持的图片类型: {type(image)}。"
            f"支持的类型: PIL.Image.Image, str (路径/URL/Base64), bytes"
        )


# ============================================================================
# 免费图床
# ============================================================================

class SMUploader:
    """
    SM.MS 图床上传器
    
    官网：https://sm.ms/
    国内优化：https://smms.app/
    
    特点：
    - ✅ 免费使用
    - 📦 单个文件最大 5MB
    - 🔑 需要注册获取 API Token（可选，但建议提供）
    - 🚀 国内访问快
    
    获取 Token：
    - 国内：https://smms.app/home/apitoken
    - 国际：https://sm.ms/home/apitoken
    
    支持的输入格式：
    - PIL.Image.Image 对象
    - 本地文件路径
    - 网络图片 URL
    - Base64 编码字符串
    - 图片字节流
    """

    def __init__(self,
                 api_token: Optional[str] = None,
                 api_domain: str = 'https://smms.app') -> None:
        """
        初始化上传器
        
        :param api_token: SM.MS API Token（可选，建议提供以提高配额）
        :param api_domain: API 域名，默认 https://smms.app（国内优化），也可使用 https://sm.ms
        """
        self.api_domain = api_domain.rstrip('/')
        self.api_url = f'{self.api_domain}/api/v2/upload'
        self.api_token = api_token

    def upload(self, image: ImageInput) -> str:
        """
        上传图片到 SM.MS
        
        :param image: 图片输入，支持：
                     - PIL.Image.Image 对象
                     - 本地文件路径 (str)
                     - 网络图片 URL (str, http/https)
                     - Base64 编码 (str, data:image/... 或纯 Base64)
                     - 图片字节流 (bytes)
        :return: 图床URL
        
        示例：
            >>> uploader = SMUploader(api_token='your-token')
            >>> 
            >>> # 上传本地图片
            >>> url = uploader.upload('/path/to/image.jpg')
            >>> 
            >>> # 上传网络图片
            >>> url = uploader.upload('https://example.com/image.jpg')
            >>> 
            >>> # 上传 PIL.Image
            >>> from PIL import Image
            >>> img = Image.open('test.jpg')
            >>> url = uploader.upload(img)
            >>> 
            >>> # 上传 Base64
            >>> url = uploader.upload('data:image/png;base64,iVBORw0KGgo...')
        """
        try:
            # 转换为字节流
            file_data, filename = _image_to_bytes(image, format='PNG')

            # 检查文件大小（SM.MS 限制 5MB）
            file_size_mb = len(file_data) / 1024 / 1024
            if file_size_mb > 5:
                raise ValueError(f"文件大小超过 5MB: {file_size_mb:.2f}MB")

            # 准备上传
            files = {'smfile': (filename, file_data)}
            headers = {}

            if self.api_token:
                headers['Authorization'] = self.api_token

            # 上传
            response = requests.post(
                self.api_url,
                files=files,
                headers=headers,
                timeout=30
            )

            result = response.json()

            # 处理结果
            if result.get('success'):
                url = result['data']['url']
                print(f"  ✅ SM.MS 上传成功: {url}")
                return url
            elif result.get('code') == 'image_repeated':
                # 图片已存在
                url = result['images']
                print(f"  ℹ️ 图片已存在: {url}")
                return url
            else:
                error_msg = result.get('message', '未知错误')
                raise Exception(f"SM.MS 上传失败: {error_msg}")

        except Exception as e:
            print(f"  ❌ SM.MS 上传失败: {e}")
            raise


class ImgURLUploader:
    """
    ImgURL 图床上传器
    
    官网：https://www.imgurl.org/
    
    特点：
    - ✅ 免费使用
    - 📦 单个文件最大 10MB
    - 🔑 需要注册获取 API Token 和 UID
    - 📁 支持相册管理
    
    获取配置：https://www.imgurl.org/vip/manage/api
    """

    def __init__(self, api_token: str, api_uid: str):
        """
        初始化上传器
        
        :param api_token: ImgURL API Token
        :param api_uid: ImgURL 用户 UID
        """
        self.api_url = 'https://www.imgurl.org/api/v2/upload'
        self.api_token = api_token
        self.api_uid = api_uid

    def upload(self, image: ImageInput) -> str:
        """
        上传图片到 ImgURL
        
        :param image: 图片输入（支持多种格式）
        :return: 图床URL
        """
        try:
            # 转换为字节流
            file_data, _ = _image_to_bytes(image, format='PNG')

            # 检查文件大小
            file_size_mb = len(file_data) / 1024 / 1024
            if file_size_mb > 10:
                raise ValueError(f"文件大小超过 10MB: {file_size_mb:.2f}MB")

            # Base64 编码
            image_base64 = base64.b64encode(file_data).decode('utf-8')

            # 上传
            data = {
                'uid': self.api_uid,
                'token': self.api_token,
                'image': image_base64
            }

            response = requests.post(self.api_url, data=data, timeout=30)
            result = response.json()

            if result.get('code') == 200:
                url = result['data']['url']
                print(f"  ✅ ImgURL 上传成功: {url}")
                return url
            else:
                error_msg = result.get('msg', '未知错误')
                raise Exception(f"ImgURL 上传失败: {error_msg}")

        except Exception as e:
            print(f"  ❌ ImgURL 上传失败: {e}")
            raise


class LuoGuoUploader:
    """
    路过图床上传器
    
    官网：https://imgtu.com/
    
    特点：
    - ✅ 免费使用
    - 📦 单个文件最大 10MB
    - 🎯 无需注册即可使用
    - 🚀 国内访问快
    """

    def __init__(self):
        """初始化上传器"""
        self.api_url = 'https://imgtu.com/api/v1/upload'

    def upload(self, image: ImageInput) -> str:
        """
        上传图片到路过图床
        
        :param image: 图片输入（支持多种格式）
        :return: 图床URL
        """
        try:
            # 转换为字节流
            file_data, filename = _image_to_bytes(image, format='PNG')

            # 上传
            files = {'source': (filename, file_data)}

            response = requests.post(
                self.api_url,
                files=files,
                timeout=30
            )

            result = response.json()

            if result.get('status_code') == 200:
                url = result['image']['url']
                print(f"  ✅ 路过图床上传成功: {url}")
                return url
            else:
                error_msg = result.get('error', {}).get('message', '未知错误')
                raise Exception(f"路过图床上传失败: {error_msg}")

        except Exception as e:
            print(f"  ❌ 路过图床上传失败: {e}")
            raise


# ============================================================================
# 云服务商图床
# ============================================================================

class QiniuUploader:
    """
    七牛云上传器
    
    官网：https://www.qiniu.com/
    
    特点：
    - 💎 10GB 免费存储
    - 📊 10GB/月 免费流量
    - 🏢 大厂服务，稳定可靠
    - 🔐 需要实名认证
    
    依赖：pip install qiniu
    """

    def __init__(self, access_key: str, secret_key: str, bucket: str, domain: str):
        """
        初始化上传器
        
        :param access_key: 七牛云 AccessKey
        :param secret_key: 七牛云 SecretKey
        :param bucket: 存储空间名称
        :param domain: CDN 域名（需要自己配置）
        """
        try:
            from qiniu import Auth, put_data
            self.auth = Auth(access_key, secret_key)
            self.bucket = bucket
            self.domain = domain
            self.put_data = put_data
        except ImportError:
            raise ImportError("请先安装七牛云SDK: pip install qiniu")

    def upload(self, image: ImageInput) -> str:
        """
        上传图片到七牛云
        
        :param image: 图片输入（支持多种格式）
        :return: CDN URL
        """
        try:
            # 转换为字节流
            file_data, filename = _image_to_bytes(image, format='PNG')

            # 生成唯一文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_hash = hashlib.md5(file_data).hexdigest()[:8]
            key = f"msimg/{timestamp}_{file_hash}_{filename}"

            # 生成上传凭证
            token = self.auth.upload_token(self.bucket, key)

            # 上传
            ret, info = self.put_data(token, key, file_data)

            if info.status_code == 200:
                url = f"http://{self.domain}/{key}"
                print(f"  ✅ 七牛云上传成功: {url}")
                return url
            else:
                raise Exception(f"七牛云上传失败: {info}")

        except Exception as e:
            print(f"  ❌ 七牛云上传失败: {e}")
            raise


class AliyunOSSUploader:
    """
    阿里云 OSS 上传器
    
    官网：https://www.aliyun.com/product/oss
    
    特点：
    - 💎 40GB 免费存储（6个月）
    - 📊 10GB/月 免费流量
    - 🏢 大厂服务，稳定可靠
    
    依赖：pip install oss2
    """

    def __init__(self, access_key_id: str, access_key_secret: str,
                 endpoint: str, bucket_name: str):
        """
        初始化上传器
        
        :param access_key_id: AccessKey ID
        :param access_key_secret: AccessKey Secret
        :param endpoint: Endpoint（如 oss-cn-hangzhou.aliyuncs.com）
        :param bucket_name: Bucket 名称
        """
        try:
            import oss2
            auth = oss2.Auth(access_key_id, access_key_secret)
            self.bucket = oss2.Bucket(auth, endpoint, bucket_name)
            self.endpoint = endpoint
            self.bucket_name = bucket_name
        except ImportError:
            raise ImportError("请先安装阿里云OSS SDK: pip install oss2")

    def upload(self, image: ImageInput) -> str:
        """
        上传图片到阿里云 OSS
        
        :param image: 图片输入（支持多种格式）
        :return: CDN URL
        """
        try:
            # 转换为字节流
            file_data, filename = _image_to_bytes(image, format='PNG')

            # 生成对象名
            timestamp = datetime.now().strftime('%Y%m%d/%H%M%S')
            file_hash = hashlib.md5(file_data).hexdigest()[:8]
            object_name = f"msimg/{timestamp}_{file_hash}_{filename}"

            # 上传
            result = self.bucket.put_object(object_name, file_data)

            if result.status == 200:
                url = f"https://{self.bucket_name}.{self.endpoint}/{object_name}"
                print(f"  ✅ 阿里云OSS上传成功: {url}")
                return url
            else:
                raise Exception(f"阿里云OSS上传失败: {result}")

        except Exception as e:
            print(f"  ❌ 阿里云OSS上传失败: {e}")
            raise


class UpyunUploader:
    """
    又拍云上传器
    
    官网：https://www.upyun.com/
    
    特点：
    - 💎 10GB 免费存储
    - 📊 15GB/月 免费流量
    - 🚀 国内访问快
    
    依赖：pip install upyun
    """

    def __init__(self, bucket: str, username: str, password: str, domain: str):
        """
        初始化上传器
        
        :param bucket: 服务名称
        :param username: 操作员账号
        :param password: 操作员密码
        :param domain: 加速域名
        """
        try:
            import upyun
            self.up = upyun.UpYun(bucket, username, password, timeout=30)
            self.domain = domain
        except ImportError:
            raise ImportError("请先安装又拍云SDK: pip install upyun")

    def upload(self, image: ImageInput) -> str:
        """
        上传图片到又拍云
        
        :param image: 图片输入（支持多种格式）
        :return: CDN URL
        """
        try:
            # 转换为字节流
            file_data, filename = _image_to_bytes(image, format='PNG')

            # 生成路径
            timestamp = datetime.now().strftime('%Y%m%d/%H%M%S')
            file_hash = hashlib.md5(file_data).hexdigest()[:8]
            remote_path = f"/msimg/{timestamp}_{file_hash}_{filename}"

            # 上传
            result = self.up.put(remote_path, file_data)

            if result:
                url = f"http://{self.domain}{remote_path}"
                print(f"  ✅ 又拍云上传成功: {url}")
                return url
            else:
                raise Exception("又拍云上传失败")

        except Exception as e:
            print(f"  ❌ 又拍云上传失败: {e}")
            raise


# ============================================================================
# 特殊图床
# ============================================================================

class GitHubUploader:
    """
    GitHub 作为图床
    
    特点：
    - ✅ 完全免费
    - 🌍 不限流量
    - 🔑 需要 GitHub 账号
    - 🌐 国内访问可能较慢（建议配合 CDN）
    
    推荐配合 jsdelivr CDN 使用
    """

    def __init__(self, token: str, repo: str, branch: str = 'main',
                 use_jsdelivr: bool = True):
        """
        初始化上传器
        
        :param token: GitHub Personal Access Token
        :param repo: 仓库名（格式：username/repo）
        :param branch: 分支名
        :param use_jsdelivr: 是否使用 jsdelivr CDN
        """
        self.api_url = 'https://api.github.com/repos'
        self.token = token
        self.repo = repo
        self.branch = branch
        self.use_jsdelivr = use_jsdelivr

    def upload(self, image: ImageInput) -> str:
        """
        上传图片到 GitHub
        
        :param image: 图片输入（支持多种格式）
        :return: 图片URL
        """
        try:
            # 转换为字节流
            file_data, filename = _image_to_bytes(image, format='PNG')

            # Base64 编码
            content_base64 = base64.b64encode(file_data).decode('utf-8')

            # 生成路径
            timestamp = datetime.now().strftime('%Y%m%d')
            file_hash = hashlib.md5(file_data).hexdigest()[:8]
            path = f"msimg/{timestamp}/{file_hash}_{filename}"

            # 上传
            url = f"{self.api_url}/{self.repo}/contents/{path}"
            headers = {
                'Authorization': f'token {self.token}',
                'Content-Type': 'application/json'
            }
            data = {
                'message': f'Upload {filename} via msimg',
                'content': content_base64,
                'branch': self.branch
            }

            response = requests.put(
                url, json=data, headers=headers, timeout=30)
            result = response.json()

            if response.status_code == 201:
                # 使用 jsdelivr CDN
                if self.use_jsdelivr:
                    cdn_url = f"https://cdn.jsdelivr.net/gh/{self.repo}@{self.branch}/{path}"
                    print(f"  ✅ GitHub上传成功（jsdelivr CDN）: {cdn_url}")
                    return cdn_url
                else:
                    raw_url = result['content']['download_url']
                    print(f"  ✅ GitHub上传成功: {raw_url}")
                    return raw_url
            else:
                error_msg = result.get('message', '未知错误')
                raise Exception(f"GitHub上传失败: {error_msg}")

        except Exception as e:
            print(f"  ❌ GitHub上传失败: {e}")
            raise


class LocalStorageUploader:
    """
    本地存储上传器（复制到本地目录）
    
    适用场景：
    - 🏠 本地预览
    - 🌐 静态网站部署
    - 🖥️ 自己搭建的服务器
    """

    def __init__(self, storage_dir: str, base_url: str):
        """
        初始化上传器
        
        :param storage_dir: 本地存储目录
        :param base_url: 访问的基础URL
        """
        self.storage_dir = Path(storage_dir)
        self.base_url = base_url.rstrip('/')

        # 创建目录
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def upload(self, image: ImageInput) -> str:
        """
        复制图片到本地目录
        
        :param image: 图片输入（支持多种格式）
        :return: 访问URL
        """
        try:
            # 转换为字节流
            file_data, filename = _image_to_bytes(image, format='PNG')

            # 生成保存路径
            timestamp = datetime.now().strftime('%Y%m%d')
            file_hash = hashlib.md5(file_data).hexdigest()[:8]

            # 创建日期目录
            date_dir = self.storage_dir / timestamp
            date_dir.mkdir(exist_ok=True)

            # 保存文件
            save_path = date_dir / f"{file_hash}_{filename}"
            with open(save_path, 'wb') as f:
                f.write(file_data)

            # 生成URL
            relative_path = f"{timestamp}/{file_hash}_{filename}"
            url = f"{self.base_url}/{relative_path}"

            print(f"  ✅ 本地存储成功: {save_path}")
            return url

        except Exception as e:
            print(f"  ❌ 本地存储失败: {e}")
            raise


# ============================================================================
# 便捷创建函数
# ============================================================================

def create_smms_uploader(api_token: Optional[str] = None,
                         api_domain: str = 'https://smms.app') -> callable:
    """
    创建 SM.MS 图床上传函数
    
    :param api_token: API Token（可选，建议提供）
    :param api_domain: API 域名（默认 https://smms.app 国内优化）
    :return: 上传函数
    
    示例：
        >>> uploader = create_smms_uploader(api_token='YOUR_TOKEN')
        >>> 
        >>> # 上传本地图片
        >>> url = uploader('/path/to/image.jpg')
        >>> 
        >>> # 上传网络图片
        >>> url = uploader('https://example.com/image.jpg')
        >>> 
        >>> # 上传 PIL.Image
        >>> from PIL import Image
        >>> img = Image.open('test.jpg')
        >>> url = uploader(img)
        >>> 
        >>> # 上传 Base64
        >>> url = uploader('data:image/png;base64,iVBORw0KGgo...')
        >>> 
        >>> # 配合 msimg 使用
        >>> from msimg import generate_image
        >>> result = generate_image(
        ...     prompt="test",
        ...     api_configs="key",
        ...     image_upload_callbacks=[uploader],
        ...     upload_on_success=True
        ... )
    """
    uploader = SMUploader(api_token, api_domain)
    return uploader.upload


def create_imgurl_uploader(api_token: str, api_uid: str) -> callable:
    """
    创建 ImgURL 图床上传函数
    
    :param api_token: ImgURL API Token
    :param api_uid: ImgURL 用户 UID
    :return: 上传函数
    """
    uploader = ImgURLUploader(api_token, api_uid)
    return uploader.upload


def create_luoguo_uploader() -> callable:
    """
    创建路过图床上传函数（无需注册）
    
    :return: 上传函数
    
    示例：
        >>> # 独立使用
        >>> uploader = create_luoguo_uploader()
        >>> url = uploader('image.jpg')
        >>> 
        >>> # 配合 msimg 使用
        >>> from msimg import generate_image
        >>> result = generate_image(
        ...     prompt="test",
        ...     api_configs="key",
        ...     image_upload_callbacks=[uploader],
        ...     upload_on_success=True
        ... )
    """
    uploader = LuoGuoUploader()
    return uploader.upload


def create_qiniu_uploader(access_key: str, secret_key: str,
                          bucket: str, domain: str) -> callable:
    """
    创建七牛云上传函数
    
    :param access_key: AccessKey
    :param secret_key: SecretKey
    :param bucket: 存储空间
    :param domain: CDN域名
    :return: 上传函数
    """
    uploader = QiniuUploader(access_key, secret_key, bucket, domain)
    return uploader.upload


def create_aliyun_uploader(access_key_id: str, access_key_secret: str,
                           endpoint: str, bucket_name: str) -> callable:
    """
    创建阿里云 OSS 上传函数
    
    :param access_key_id: AccessKey ID
    :param access_key_secret: AccessKey Secret
    :param endpoint: Endpoint
    :param bucket_name: Bucket 名称
    :return: 上传函数
    """
    uploader = AliyunOSSUploader(
        access_key_id, access_key_secret, endpoint, bucket_name)
    return uploader.upload


def create_upyun_uploader(bucket: str, username: str,
                          password: str, domain: str) -> callable:
    """
    创建又拍云上传函数
    
    :param bucket: 服务名称
    :param username: 操作员账号
    :param password: 操作员密码
    :param domain: 加速域名
    :return: 上传函数
    """
    uploader = UpyunUploader(bucket, username, password, domain)
    return uploader.upload


def create_github_uploader(token: str, repo: str, branch: str = 'main',
                           use_jsdelivr: bool = True) -> callable:
    """
    创建 GitHub 图床上传函数
    
    :param token: GitHub Token
    :param repo: 仓库（username/repo）
    :param branch: 分支
    :param use_jsdelivr: 使用 jsdelivr CDN
    :return: 上传函数
    """
    uploader = GitHubUploader(token, repo, branch, use_jsdelivr)
    return uploader.upload


def create_local_uploader(storage_dir: str, base_url: str) -> callable:
    """
    创建本地存储上传函数
    
    :param storage_dir: 存储目录
    :param base_url: 访问URL
    :return: 上传函数
    """
    uploader = LocalStorageUploader(storage_dir, base_url)
    return uploader.upload
