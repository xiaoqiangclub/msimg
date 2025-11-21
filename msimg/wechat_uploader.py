# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# GitHub：https://github.com/xiaoqiangclub
# 邮箱：xiaoqiangclub@hotmail.com
# 创建时间：2025-11-18 10:08:08
# 文件描述：微信公众号图床上传器
# 文件路径：msimg/wechat_uploader.py

"""
微信公众号图床上传模块

支持三种上传方式：
1. 临时素材（默认）：有效期3天，返回 media_id
2. 永久素材：永久保存，返回 media_id 和 url
3. 图文消息图片：用于图文消息内容，返回 url

支持两种 Token 获取方式（自动选择）：
- 方式1：使用 app_id + app_secret 直接获取（需要IP在白名单）
- 方式2：从服务器获取（适用于IP白名单限制的场景）

快速开始：
    >>> from msimg.wechat_uploader import create_wechat_uploader, WechatUploadType
    >>>
    >>> # 创建上传器（临时素材）
    >>> uploader = create_wechat_uploader(
    ...     app_id="wx1234567890",
    ...     app_secret="abcdef1234567890"
    ... )
    >>>
    >>> # 上传本地图片
    >>> media_id = uploader('/path/to/image.jpg')
"""

import os
import json
import time
import tempfile
import requests
from typing import Optional
from enum import Enum
from io import BytesIO

try:
    from PIL import Image
except ImportError:
    raise ImportError("❌ 请安装 Pillow: pip install Pillow")

# 导入图片转换工具函数
try:
    from .image_uploader import _image_to_bytes
except ImportError:
    raise ImportError(
        "❌ 无法导入 image_uploader 模块，请确保 msimg 包已正确安装"
    )


# ============================================================================
# 类型定义
# ============================================================================

class WechatUploadType(Enum):
    """微信上传类型枚举"""
    TEMPORARY = "temporary"  # 临时素材（3天有效期）
    PERMANENT = "permanent"  # 永久素材
    NEWS_IMAGE = "news_image"  # 图文消息图片


# ============================================================================
# 微信公众号上传器
# ============================================================================

class WechatUploader:
    """
    微信公众号图床上传器

    官网：https://mp.weixin.qq.com/
    文档：https://developers.weixin.qq.com/doc/offiaccount/Asset_Management/New_temporary_materials.html

    支持三种上传方式：
    1. 临时素材（默认）：有效期3天，返回 media_id
       API: https://developers.weixin.qq.com/doc/offiaccount/Asset_Management/New_temporary_materials.html

    2. 永久素材：永久保存，返回 media_id 和 url
       API: https://developers.weixin.qq.com/doc/offiaccount/Asset_Management/Adding_Permanent_Assets.html

    3. 图文消息图片：用于图文消息内容，返回 url
       API: https://developers.weixin.qq.com/doc/offiaccount/Asset_Management/New_temporary_materials.html

    支持两种 Token 获取方式（自动选择）：
    - 方式1：使用 app_id + app_secret 直接获取（需要IP在白名单）
    - 方式2：从服务器获取（适用于IP白名单限制）

    特点：
    - 🔐 需要公众号认证
    - 📦 临时素材：图片大小限制 2MB
    - 📦 永久素材：图片大小限制 10MB
    - 📦 图文图片：图片大小限制 1MB
    - 📝 支持 JPG、PNG、GIF 格式
    - ⏰ 临时素材有效期 3 天
    - 💾 永久素材数量限制 100000 个
    """

    # API 端点
    TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token"
    UPLOAD_TEMP_URL = "https://api.weixin.qq.com/cgi-bin/media/upload"
    UPLOAD_PERMANENT_URL = "https://api.weixin.qq.com/cgi-bin/material/add_material"
    UPLOAD_NEWS_IMAGE_URL = "https://api.weixin.qq.com/cgi-bin/media/uploadimg"

    # Token 缓存过期时间（提前5分钟刷新）
    TOKEN_EXPIRE_MARGIN = 300

    def __init__(
            self,
            app_id: str,
            app_secret: str,
            upload_type: WechatUploadType = WechatUploadType.TEMPORARY,
            access_token_file: Optional[str] = None,
            server_url: Optional[str] = None,
            server_token: Optional[str] = None,
            verbose: bool = True,
            proxies: Optional[dict] = None,
    ):
        """
        初始化微信公众号图床上传器

        :param app_id: 公众号 AppID（必需）
        :param app_secret: 公众号 AppSecret（必需）
        :param upload_type: 上传类型（TEMPORARY/PERMANENT/NEWS_IMAGE），默认 TEMPORARY
        :param access_token_file: access_token 缓存文件路径，默认保存在系统临时目录
        :param server_url: 从服务器获取 access_token 的 URL（可选）
        :param server_token: 服务器认证令牌（可选）
        :param verbose: 是否显示详细日志
        :param proxies: 代理配置

        示例：
            >>> # 自动获取 Token（优先从服务器，失败则直接获取）
            >>> uploader = WechatUploader(
            ...     app_id="wx1234567890",
            ...     app_secret="abcdef1234567890",
            ...     server_url="https://your-server.com/api/token",
            ...     upload_type=WechatUploadType.PERMANENT
            ... )
        """
        # 保存配置
        self.app_id = app_id
        self.app_secret = app_secret
        self.upload_type = upload_type
        self.verbose = verbose
        self.proxies = proxies

        # 服务器获取 token 配置
        self.server_url = server_url
        self.server_token = server_token

        # 设置 token 缓存文件路径
        if access_token_file:
            self.access_token_file = access_token_file
        else:
            # 默认保存在系统临时目录
            temp_dir = tempfile.gettempdir()
            cache_name = f"wechat_upload_token_{self.app_id}.json"
            self.access_token_file = os.path.join(temp_dir, cache_name)

        # Token 缓存
        self._access_token = None
        self._token_expires_at = 0

    def upload(self, image) -> str:
        """
        上传图片到微信公众号

        :param image: 图片输入，支持：
                     - PIL.Image.Image 对象
                     - 本地文件路径 (str)
                     - 网络图片 URL (str, http/https)
                     - Base64 编码 (str, data:image/... 或纯 Base64)
                     - 图片字节流 (bytes)
        :return: media_id 或 url（根据上传类型）

        示例：
            >>> uploader = WechatUploader(app_id="wx123", app_secret="abc")
            >>>
            >>> # 上传本地图片
            >>> media_id = uploader.upload('/path/to/image.jpg')
            >>>
            >>> # 上传 PIL.Image
            >>> from PIL import Image
            >>> img = Image.open('test.jpg')
            >>> media_id = uploader.upload(img)
        """
        try:
            # 获取 access_token
            access_token = self._get_access_token()
            if not access_token:
                raise Exception("❌ 获取 access_token 失败")

            # 使用 image_uploader 的工具函数转换图片
            file_data, filename = _image_to_bytes(image, format='JPEG')

            # 根据上传类型检查文件大小
            max_size_mb = self._get_max_size()
            file_size_mb = len(file_data) / 1024 / 1024
            if file_size_mb > max_size_mb:
                raise ValueError(
                    f"❌ 文件大小超过 {max_size_mb}MB 限制: {file_size_mb:.2f}MB")

            # 确保图片格式符合微信要求
            file_data, filename = self._ensure_valid_format(file_data, filename)

            # 根据上传类型选择不同的上传方式
            if self.upload_type == WechatUploadType.TEMPORARY:
                return self._upload_temporary(access_token, file_data, filename)
            elif self.upload_type == WechatUploadType.PERMANENT:
                return self._upload_permanent(access_token, file_data, filename)
            elif self.upload_type == WechatUploadType.NEWS_IMAGE:
                return self._upload_news_image(access_token, file_data, filename)
            else:
                raise ValueError(f"❌ 不支持的上传类型: {self.upload_type}")

        except Exception as e:
            if self.verbose:
                print(f"  ❌ 微信图片上传失败: {e}")
            raise

    def _get_max_size(self) -> int:
        """获取不同上传类型的最大文件大小限制（MB）"""
        if self.upload_type == WechatUploadType.TEMPORARY:
            return 2  # 临时素材 2MB
        elif self.upload_type == WechatUploadType.PERMANENT:
            return 10  # 永久素材 10MB
        elif self.upload_type == WechatUploadType.NEWS_IMAGE:
            return 1  # 图文消息图片 1MB
        return 2

    def _ensure_valid_format(self, file_data: bytes, filename: str) -> tuple:
        """确保图片格式符合微信要求（只支持 JPG、PNG、GIF）"""
        try:
            img_buffer = BytesIO(file_data)
            img = Image.open(img_buffer)

            # 获取或转换图片格式
            img_format = img.format if img.format else 'JPEG'

            if img_format.upper() not in ['JPEG', 'JPG', 'PNG', 'GIF']:
                # 转换为 JPEG
                if self.verbose:
                    print(f"  ℹ️  将 {img_format} 格式转换为 JPEG")

                output = BytesIO()
                if img.mode in ('RGBA', 'LA', 'P'):
                    # 处理透明通道
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])
                    else:
                        background.paste(img)
                    background.save(output, format='JPEG', quality=95)
                else:
                    img.save(output, format='JPEG', quality=95)

                file_data = output.getvalue()
                filename = os.path.splitext(filename)[0] + '.jpg'

            return file_data, filename

        except Exception as e:
            if self.verbose:
                print(f"  ⚠️  图片格式检查失败: {e}")
            return file_data, filename

    def _upload_temporary(
            self,
            access_token: str,
            file_data: bytes,
            filename: str
    ) -> str:
        """上传临时素材"""
        try:
            url = f"{self.UPLOAD_TEMP_URL}?access_token={access_token}&type=image"

            # 获取 MIME 类型
            mime_type = self._get_mime_type(filename)
            files = {'media': (filename, file_data, mime_type)}

            if self.verbose:
                print(f"  📤 正在上传临时素材到微信公众号...")

            response = requests.post(
                url, files=files, proxies=self.proxies, timeout=30)
            response.raise_for_status()

            result = response.json()

            if 'errcode' in result and result['errcode'] != 0:
                raise Exception(
                    f"{result.get('errmsg', '未知错误')} (errcode: {result['errcode']})")

            media_id = result.get('media_id')
            if self.verbose:
                print(f"  ✅ 微信临时素材上传成功！")
                print(f"     Media ID: {media_id}")
                print(f"     有效期: 3天")

            return media_id

        except Exception as e:
            if self.verbose:
                print(f"  ❌ 上传临时素材失败: {e}")
            raise

    def _upload_permanent(
            self,
            access_token: str,
            file_data: bytes,
            filename: str
    ) -> str:
        """上传永久素材"""
        try:
            url = f"{self.UPLOAD_PERMANENT_URL}?access_token={access_token}&type=image"

            # 获取 MIME 类型
            mime_type = self._get_mime_type(filename)
            files = {'media': (filename, file_data, mime_type)}

            if self.verbose:
                print(f"  📤 正在上传永久素材到微信公众号...")

            response = requests.post(
                url, files=files, proxies=self.proxies, timeout=30)
            response.raise_for_status()

            result = response.json()

            if 'errcode' in result and result['errcode'] != 0:
                raise Exception(
                    f"{result.get('errmsg', '未知错误')} (errcode: {result['errcode']})")

            media_id = result.get('media_id')
            image_url = result.get('url')

            if self.verbose:
                print(f"  ✅ 微信永久素材上传成功！")
                if media_id:
                    print(f"     Media ID: {media_id}")
                if image_url:
                    print(f"     URL: {image_url}")

            # 返回 URL（如果有），否则返回 media_id
            return image_url if image_url else media_id

        except Exception as e:
            if self.verbose:
                print(f"  ❌ 上传永久素材失败: {e}")
            raise

    def _upload_news_image(
            self,
            access_token: str,
            file_data: bytes,
            filename: str
    ) -> str:
        """上传图文消息图片"""
        try:
            url = f"{self.UPLOAD_NEWS_IMAGE_URL}?access_token={access_token}"

            # 获取 MIME 类型
            mime_type = self._get_mime_type(filename)
            files = {'media': (filename, file_data, mime_type)}

            if self.verbose:
                print(f"  📤 正在上传图文消息图片到微信公众号...")

            response = requests.post(
                url, files=files, proxies=self.proxies, timeout=30)
            response.raise_for_status()

            result = response.json()

            if 'errcode' in result and result['errcode'] != 0:
                raise Exception(
                    f"{result.get('errmsg', '未知错误')} (errcode: {result['errcode']})")

            image_url = result.get('url')
            if self.verbose:
                print(f"  ✅ 微信图文消息图片上传成功！")
                print(f"     URL: {image_url}")

            return image_url

        except Exception as e:
            if self.verbose:
                print(f"  ❌ 上传图文消息图片失败: {e}")
            raise

    def _get_mime_type(self, filename: str) -> str:
        """根据文件名获取 MIME 类型"""
        ext = filename.rsplit('.', 1)[-1].lower()
        mime_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif'
        }
        return mime_types.get(ext, 'image/jpeg')

    def _get_access_token(self) -> Optional[str]:
        """
        获取 access_token（自动选择最佳方式）

        优先级：
        1. 内存缓存（未过期）
        2. 文件缓存（未过期）
        3. 从服务器获取（如果配置了 server_url）
        4. 从微信 API 获取

        :return: access_token 或 None
        """
        # 1. 检查内存缓存
        if self._access_token and time.time() < self._token_expires_at:
            if self.verbose:
                print(f"  ℹ️  使用内存缓存的 access_token")
            return self._access_token

        # 2. 尝试从文件加载
        token = self._load_token_from_file()
        if token:
            return token

        # 3. 如果配置了服务器 URL，优先从服务器获取
        if self.server_url:
            token = self._get_token_from_server()
            if token:
                return token

            if self.verbose:
                print(f"  ⚠️  从服务器获取 token 失败，尝试直接从微信 API 获取...")

        # 4. 从微信 API 获取
        return self._refresh_access_token()

    def _get_token_from_server(self, retries: int = 2) -> Optional[str]:
        """
        从服务器获取 access_token

        :param retries: 重试次数
        :return: access_token 或 None
        """
        if not self.server_url:
            return None

        for i in range(retries + 1):
            try:
                if self.verbose:
                    if i == 0:
                        print(f"  🌐 正在从服务器获取 access_token...")
                    else:
                        print(f"  🔄 重试从服务器获取 access_token ({i}/{retries})...")

                headers = {'Content-Type': 'application/json'}
                data = {}

                # 如果有 server_token，添加到请求中
                if self.server_token:
                    data['token'] = self.server_token

                response = requests.post(
                    self.server_url,
                    headers=headers,
                    json=data if data else None,
                    proxies=self.proxies,
                    timeout=10
                )
                response.raise_for_status()
                result = response.json()

                # 检查错误信息
                if result.get("detail"):
                    if self.verbose:
                        print(f"  ⚠️  服务器返回错误: {result['detail']}")
                    if i < retries:
                        time.sleep(1)
                        continue
                    return None

                # 提取 token
                access_token = result.get('access_token')
                expires_in = result.get('expires_in', 7200)

                if not access_token:
                    if self.verbose:
                        print(f"  ⚠️  服务器响应中未找到 access_token")
                    if i < retries:
                        time.sleep(1)
                        continue
                    return None

                # 缓存 token
                self._access_token = access_token
                self._token_expires_at = time.time() + expires_in - self.TOKEN_EXPIRE_MARGIN

                # 保存到文件
                self._save_token_to_file(access_token, expires_in)

                if self.verbose:
                    print(f"  ✅ 从服务器获取 access_token 成功")
                    print(f"     有效期: {expires_in}秒")

                return access_token

            except requests.exceptions.RequestException as e:
                if self.verbose:
                    print(f"  ⚠️  请求服务器失败: {e}")
                if i < retries:
                    time.sleep(1)
                    continue
                return None
            except json.JSONDecodeError as e:
                if self.verbose:
                    print(f"  ⚠️  服务器响应解析失败: {e}")
                if i < retries:
                    time.sleep(1)
                    continue
                return None
            except Exception as e:
                if self.verbose:
                    print(f"  ⚠️  从服务器获取 token 时发生错误: {e}")
                if i < retries:
                    time.sleep(1)
                    continue
                return None

        return None

    def _refresh_access_token(self) -> Optional[str]:
        """使用 AppID 和 AppSecret 从微信 API 获取 access_token"""
        try:
            if self.verbose:
                print(f"  🔄 正在从微信 API 获取 access_token...")

            url = f"{self.TOKEN_URL}?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"

            response = requests.get(url, proxies=self.proxies, timeout=10)
            response.raise_for_status()

            result = response.json()

            if 'errcode' in result:
                error_msg = result.get('errmsg', '未知错误')
                if self.verbose:
                    print(f"  ❌ 获取 access_token 失败: {error_msg}")
                return None

            access_token = result.get('access_token')
            expires_in = result.get('expires_in', 7200)

            if not access_token:
                if self.verbose:
                    print(f"  ❌ 响应中未找到 access_token")
                return None

            # 缓存 token
            self._access_token = access_token
            self._token_expires_at = time.time() + expires_in - self.TOKEN_EXPIRE_MARGIN

            # 保存到文件
            self._save_token_to_file(access_token, expires_in)

            if self.verbose:
                print(f"  ✅ 从微信 API 获取 access_token 成功")
                print(f"     有效期: {expires_in}秒")

            return access_token

        except Exception as e:
            if self.verbose:
                print(f"  ❌ 从微信 API 获取 access_token 失败: {e}")
            return None

    def _load_token_from_file(self) -> Optional[str]:
        """从文件加载 access_token"""
        try:
            if not os.path.exists(self.access_token_file):
                return None

            with open(self.access_token_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            access_token = data.get('access_token')
            expires_at = data.get('expire_time', 0)

            # 检查是否过期
            if time.time() < expires_at:
                self._access_token = access_token
                self._token_expires_at = expires_at
                if self.verbose:
                    print(f"  ✅ 从缓存文件加载 access_token 成功")
                return access_token
            else:
                if self.verbose:
                    print(f"  ⚠️  缓存的 access_token 已过期")
                return None

        except json.JSONDecodeError:
            if self.verbose:
                print(f"  ⚠️  缓存文件解析失败")
            return None
        except Exception as e:
            if self.verbose:
                print(f"  ⚠️  加载缓存文件失败: {e}")
            return None

    def _save_token_to_file(self, access_token: str, expires_in: int):
        """保存 access_token 到文件"""
        try:
            # 确保目录存在
            dir_path = os.path.dirname(self.access_token_file)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)

            data = {
                'access_token': access_token,
                'expire_time': time.time() + expires_in - self.TOKEN_EXPIRE_MARGIN,
                'expires_in': expires_in,
                'updated_at': time.time(),
            }

            with open(self.access_token_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            if self.verbose:
                print(f"  💾 access_token 已缓存到: {self.access_token_file}")

        except Exception as e:
            if self.verbose:
                print(f"  ⚠️  保存 access_token 缓存失败: {e}")


# ============================================================================
# 便捷创建函数
# ============================================================================

def create_wechat_uploader(
        app_id: str,
        app_secret: str,
        upload_type: WechatUploadType = WechatUploadType.TEMPORARY,
        server_url: Optional[str] = None,
        server_token: Optional[str] = None,
        **kwargs
) -> callable:
    """
    创建微信公众号图床上传函数

    :param app_id: 公众号 AppID（必需）
    :param app_secret: 公众号 AppSecret（必需）
    :param upload_type: 上传类型（TEMPORARY/PERMANENT/NEWS_IMAGE），默认 TEMPORARY
    :param server_url: 从服务器获取 access_token 的 URL（可选）
    :param server_token: 服务器认证令牌（可选）
    :param kwargs: 其他参数传递给 WechatUploader
    :return: 上传函数

    示例：
        >>> from msimg import generate_image
        >>> from msimg.wechat_uploader import create_wechat_uploader, WechatUploadType
        >>>
        >>> # 自动选择最佳 Token 获取方式
        >>> wechat_upload = create_wechat_uploader(
        ...     app_id="wx1234567890",
        ...     app_secret="abcdef1234567890",
        ...     server_url="https://your-server.com/api/token",  # 可选
        ...     upload_type=WechatUploadType.PERMANENT
        ... )
        >>>
        >>> # 生成图片并上传
        >>> result = generate_image(
        ...     prompt="一只可爱的猫",
        ...     api_configs="your-api-key",
        ...     image_upload_callbacks=wechat_upload,
        ...     upload_on_success=True
        ... )
    """
    uploader = WechatUploader(
        app_id=app_id,
        app_secret=app_secret,
        upload_type=upload_type,
        server_url=server_url,
        server_token=server_token,
        **kwargs
    )

    return uploader.upload