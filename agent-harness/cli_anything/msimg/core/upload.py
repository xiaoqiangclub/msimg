"""
MSIMG CLI 核心模块 - 图床上传
"""

from typing import Union, List, Optional
from PIL import Image
from pathlib import Path


class ImageUploader:
    """图片上传器"""

    def __init__(self):
        """初始化图片上传器"""
        pass

    def upload(self,
              image_path: Union[str, Path, Image.Image],
              uploader_type: str = "smms",
              **kwargs) -> Optional[str]:
        """
        上传图片到图床

        Args:
            image_path: 图片路径、PIL Image对象或图床上传器
            uploader_type: 上传器类型
            **kwargs: 上传器特定参数

        Returns:
            图片URL或None
        """
        # 根据上传器类型创建相应的上传器
        from msimg import (
            create_smms_uploader,
            create_imgurl_uploader,
            create_luoguo_uploader,
            create_qiniu_uploader,
            create_aliyun_uploader,
            create_upyun_uploader,
            create_github_uploader,
            create_local_uploader,
            create_wechat_uploader
        )

        try:
            if uploader_type == "smms":
                uploader = create_smms_uploader(
                    api_token=kwargs.get("api_token", ""),
                    api_domain=kwargs.get("api_domain", "https://smms.app")
                )
            elif uploader_type == "imgurl":
                uploader = create_imgurl_uploader(
                    api_token=kwargs.get("api_token", ""),
                    api_uid=kwargs.get("api_uid", "")
                )
            elif uploader_type == "luoguo":
                uploader = create_luoguo_uploader()
            elif uploader_type == "qiniu":
                uploader = create_qiniu_uploader(
                    access_key=kwargs.get("access_key", ""),
                    secret_key=kwargs.get("secret_key", ""),
                    bucket=kwargs.get("bucket", ""),
                    domain=kwargs.get("domain", "")
                )
            elif uploader_type == "aliyun":
                uploader = create_aliyun_uploader(
                    access_key_id=kwargs.get("access_key_id", ""),
                    access_key_secret=kwargs.get("access_key_secret", ""),
                    endpoint=kwargs.get("endpoint", ""),
                    bucket_name=kwargs.get("bucket_name", "")
                )
            elif uploader_type == "upyun":
                uploader = create_upyun_uploader(
                    bucket=kwargs.get("bucket", ""),
                    username=kwargs.get("username", ""),
                    password=kwargs.get("password", ""),
                    domain=kwargs.get("domain", "")
                )
            elif uploader_type == "github":
                uploader = create_github_uploader(
                    token=kwargs.get("token", ""),
                    repo=kwargs.get("repo", ""),
                    branch=kwargs.get("branch", "main"),
                    use_jsdelivr=kwargs.get("use_jsdelivr", True)
                )
            elif uploader_type == "local":
                uploader = create_local_uploader(
                    storage_dir=kwargs.get("storage_dir", "./uploads"),
                    base_url=kwargs.get("base_url", "http://localhost/uploads")
                )
            elif uploader_type == "wechat":
                uploader = create_wechat_uploader(
                    app_id=kwargs.get("app_id", ""),
                    app_secret=kwargs.get("app_secret", ""),
                    server_url=kwargs.get("server_url"),
                    upload_type=kwargs.get("upload_type")
                )
            else:
                print(f"❌ 不支持的上传器类型: {uploader_type}")
                return None

            # 执行上传
            result = uploader(image_path)
            return result

        except Exception as e:
            print(f"❌ 上传失败: {str(e)}")
            return None

    def batch_upload(self,
                   image_paths: List[Union[str, Path, Image.Image]],
                   uploader_type: str = "smms",
                   **kwargs) -> List[Optional[str]]:
        """
        批量上传图片

        Args:
            image_paths: 图片路径列表
            uploader_type: 上传器类型
            **kwargs: 上传器特定参数

        Returns:
            图片URL列表
        """
        results = []
        for i, image_path in enumerate(image_paths):
            print(f"🔄 正在上传第 {i+1}/{len(image_paths)} 张图片...")
            result = self.upload(image_path, uploader_type, **kwargs)
            results.append(result)

        return results