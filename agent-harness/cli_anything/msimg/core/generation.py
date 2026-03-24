"""
MSIMG CLI 核心模块 - 图片生成
"""

import os
from typing import Optional, List, Dict, Any

class ImageGenerator:
    """图片生成器"""

    def __init__(self, api_key: str):
        """
        初始化图片生成器

        Args:
            api_key: API密钥
        """
        self.api_key = api_key

    def generate(self,
                prompt: str,
                model: str = "qwen",
                size: str = "16:9",
                save_path: Optional[str] = None,
                enable_failover: bool = True,
                max_retries: int = 3,
                verbose: bool = True) -> Optional[Dict[str, Any]]:
        """
        生成图片

        Args:
            prompt: 提示词
            model: 模型名称
            size: 图片尺寸
            save_path: 保存路径
            enable_failover: 是否启用容错
            max_retries: 最大重试次数
            verbose: 是否显示详细日志

        Returns:
            生成结果字典或None
        """
        # 导入msimg库中的generate_image函数
        from msimg import generate_image

        result = generate_image(
            prompt=prompt,
            api_configs=self.api_key,
            models=model,
            size=size,
            save_path=save_path,
            enable_failover=enable_failover,
            max_retries=max_retries,
            verbose=verbose
        )

        return result

    def batch_generate(self,
                     prompts: List[str],
                     model: str = "qwen",
                     size: str = "16:9",
                     output_dir: str = "./output",
                     enable_failover: bool = True,
                     max_retries: int = 3) -> List[Optional[Dict[str, Any]]]:
        """
        批量生成图片

        Args:
            prompts: 提示词列表
            model: 模型名称
            size: 图片尺寸
            output_dir: 输出目录
            enable_failover: 是否启用容错
            max_retries: 最大重试次数

        Returns:
            生成结果列表
        """
        os.makedirs(output_dir, exist_ok=True)

        results = []
        for i, prompt in enumerate(prompts):
            save_path = os.path.join(output_dir, f"image_{i+1:03d}.jpg")
            print(f"🎨 正在生成第 {i+1}/{len(prompts)} 张图片: {prompt}")

            result = self.generate(
                prompt=prompt,
                model=model,
                size=size,
                save_path=save_path,
                enable_failover=enable_failover,
                max_retries=max_retries
            )

            results.append(result)

        return results