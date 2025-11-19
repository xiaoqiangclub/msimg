# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# GitHub：https://github.com/xiaoqiangclub
# 邮箱：xiaoqiangclub@hotmail.com
# 创建时间：2025-01-20 10:00
# 文件描述：图片生成核心功能
# 文件路径：msimg/generator.py

from typing import Optional, List, Callable, Dict, Union
import requests
import time
import json
import re
from PIL import Image
from io import BytesIO

from .config import APIConfig
from .constants import (
    SIZE_PRESETS,
    MODEL_PRESETS,
    TASK_STATUS_MAP,
    DEFAULT_BASE_URL,
)
from .strategies import SelectionStrategy, NotificationMode
from .callbacks import ResourceSelector, NotificationManager, ImageUploadManager
from .exceptions import ValidationError


def get_status_display(status: str) -> str:
    """
    获取任务状态的显示文本
    
    :param status: 原始状态
    :return: 格式化后的状态显示文本
    """
    return TASK_STATUS_MAP.get(status, f"❓ {status}")


def _parse_api_configs(api_configs: Union[str, List[str], APIConfig, List[APIConfig]]) -> List[APIConfig]:
    """
    解析 API 配置参数
    
    :param api_configs: API 配置，支持多种格式
    :return: APIConfig 对象列表
    """
    if isinstance(api_configs, APIConfig):
        return [api_configs]
    
    if isinstance(api_configs, str):
        # 单个 API Key 字符串
        return [APIConfig(api_key=api_configs)]
    
    if isinstance(api_configs, list):
        result = []
        for item in api_configs:
            if isinstance(item, APIConfig):
                result.append(item)
            elif isinstance(item, str):
                result.append(APIConfig(api_key=item))
            else:
                raise ValidationError(f"不支持的 API 配置类型: {type(item)}")
        return result
    
    raise ValidationError(f"不支持的 API 配置类型: {type(api_configs)}")


def _parse_models(models: Union[str, List[str]]) -> List[str]:
    """
    解析模型参数，支持预设名称和完整 ID
    
    :param models: 模型配置
    :return: 完整模型 ID 列表
    """
    if isinstance(models, str):
        models = [models]
    
    result = []
    for model in models:
        # 检查是否为预设名称
        if model in MODEL_PRESETS:
            result.append(MODEL_PRESETS[model])
        else:
            # 直接使用完整 ID
            result.append(model)
    
    return result


def generate_image(
    prompt: str,
    api_configs: Union[str, List[str], APIConfig, List[APIConfig]],
    
    # ==================== 模型配置 ====================
    models: Union[str, List[str]] = "qwen",
    model_selection_strategy: SelectionStrategy = SelectionStrategy.SEQUENTIAL,
    
    # ==================== 图片配置 ====================
    size: str = "16:9",
    save_path: Optional[str] = None,
    
    # ==================== API 配置 ====================
    api_selection_strategy: SelectionStrategy = SelectionStrategy.SEQUENTIAL,
    
    # ==================== 容错和重试配置 ====================
    enable_failover: bool = True,
    max_retries: int = 3,
    retry_on_network_error: bool = True,
    retry_delay: float = 2.0,
    
    # ==================== 超时配置 ====================
    submit_timeout: int = 30,
    poll_timeout: int = 300,
    download_timeout: int = 60,
    poll_interval: int = 5,
    
    # ==================== 图床上传配置 ====================
    image_upload_callbacks: Optional[Union[Callable[[Image.Image], str], List[Callable[[Image.Image], str]]]] = None,
    upload_strategy: SelectionStrategy = SelectionStrategy.SEQUENTIAL,
    upload_on_success: bool = False,
    
    # ==================== 消息通知配置 ====================
    notification_callbacks: Optional[Union[Callable, List[Callable]]] = None,
    notification_mode: NotificationMode = NotificationMode.NONE,
    notification_strategy: SelectionStrategy = SelectionStrategy.SEQUENTIAL,
    
    # ==================== 其他配置 ====================
    verbose: bool = True,
    proxies: Optional[Dict[str, str]] = None,
    
) -> Optional[Dict]:
    """
    使用 ModelScope API 生成图片（支持多 API、多模型、容错、重试等高级特性）
    
    参数说明:
    
    === 基础参数 ===
    :param prompt: 图片生成的提示词（必需）
    :param api_configs: API 配置，支持多种格式:
                       - 单个 API Key 字符串: "your-api-key"
                       - API Key 列表: ["key1", "key2"]
                       - APIConfig 对象: APIConfig(api_key="key", base_url="...")
                       - APIConfig 对象列表: [APIConfig(...), APIConfig(...)]
    
    === 模型配置 ===
    :param models: 模型名称，支持:
                  - 预设名称: "qwen", "flux-majic" 等
                  - 完整 ID: "Qwen/Qwen-Image"
                  - 列表形式: ["qwen", "flux-majic"]
    :param model_selection_strategy: 模型选择策略（RANDOM/SEQUENTIAL/ROUND_ROBIN）
    
    === 图片配置 ===
    :param size: 图片尺寸，支持:
                - 预设比例: "1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3"
                - 自定义尺寸: "1920x1080"
    :param save_path: 图片保存路径，None 时不保存
    
    === API 配置 ===
    :param api_selection_strategy: API 选择策略（RANDOM/SEQUENTIAL/ROUND_ROBIN）
    
    === 容错和重试配置 ===
    :param enable_failover: 是否启用容错（API/模型失败时自动切换）
    :param max_retries: 网络错误时的最大重试次数
    :param retry_on_network_error: 是否在网络错误时重试
    :param retry_delay: 重试间隔时间（秒）
    
    === 超时配置 ===
    :param submit_timeout: 提交任务的超时时间（秒）
    :param poll_timeout: 轮询任务状态的总超时时间（秒）
    :param download_timeout: 下载图片的超时时间（秒）
    :param poll_interval: 轮询间隔时间（秒）
    
    === 图床上传配置 ===
    :param image_upload_callbacks: 图床上传函数，格式: func(image: Image.Image) -> str(url)
                                  支持单个函数或列表
    :param upload_strategy: 图床选择策略（SEQUENTIAL 为故障转移模式）
    :param upload_on_success: 是否在生成成功后自动上传
    
    === 消息通知配置 ===
    :param notification_callbacks: 消息通知函数，格式: func(data: dict) -> None
                                   data 包含: message, is_success, data
                                   支持单个函数或列表
    :param notification_mode: 通知模式（SUCCESS/ERROR/ALL/NONE）
    :param notification_strategy: 通知策略（SEQUENTIAL 为全部通知，RANDOM/ROUND_ROBIN 为单个通知）
    
    === 其他配置 ===
    :param verbose: 是否显示详细日志
    :param proxies: 代理配置，格式: {'http': 'http://...', 'https': 'https://...'}
    
    返回值:
    :return: 成功返回字典:
            {
                'image': PIL.Image 对象,
                'url': 图床 URL（如果上传）,
                'model': 使用的模型,
                'api': 使用的 API 名称,
                'size': 图片尺寸元组,
            }
            失败返回 None
    
    示例:
        # 最简单的用法
        result = generate_image(
            prompt="一只金色的猫",
            api_configs="your-api-key"
        )
        
        # 使用预设模型
        result = generate_image(
            prompt="美丽的日落",
            api_configs="your-api-key",
            models="flux-majic",
            size="16:9"
        )
        
        # 高级用法（多 API、容错、图床上传、消息通知）
        result = generate_image(
            prompt="赛博朋克城市",
            api_configs=["key1", "key2"],
            models=["qwen", "flux-majic"],
            enable_failover=True,
            image_upload_callbacks=[upload_imgur, upload_smms],
            upload_on_success=True,
            notification_callbacks=send_to_wechat,
            notification_mode=NotificationMode.ALL
        )
    """
    
    # ==================== 参数预处理 ====================
    
    # 解析 API 配置
    api_configs_list = _parse_api_configs(api_configs)
    
    # 解析模型配置
    models_list = _parse_models(models)
    
    # 统一转换为列表格式
    if image_upload_callbacks is not None and callable(image_upload_callbacks):
        image_upload_callbacks = [image_upload_callbacks]
    
    if notification_callbacks is not None and callable(notification_callbacks):
        notification_callbacks = [notification_callbacks]
    
    # 处理尺寸参数
    if size in SIZE_PRESETS:
        size_str = SIZE_PRESETS[size]
        if verbose:
            print(f"ℹ️  使用预设尺寸: {size} → {size_str}")
    elif re.match(r'^\d+x\d+$', size):
        size_str = size
        if verbose:
            print(f"ℹ️  使用自定义尺寸: {size_str}")
    else:
        error_msg = f"不支持的尺寸格式: {size}"
        print(f"❌ {error_msg}")
        print(f"ℹ️  支持的预设比例: {', '.join(SIZE_PRESETS.keys())}")
        print(f"ℹ️  或使用自定义格式: 宽度x高度 (例如: 1920x1080)")
        raise ValidationError(error_msg)
    
    # 创建选择器
    api_selector = ResourceSelector(api_selection_strategy)
    model_selector = ResourceSelector(model_selection_strategy)
    
    # 创建通知管理器
    notification_manager = NotificationManager(
        callbacks=notification_callbacks,
        mode=notification_mode,
        strategy=notification_strategy,
        verbose=verbose,
    )
    
    # ==================== 主循环（支持容错） ====================
    
    used_api_indices = set()
    used_model_indices = set()
    
    # 最大尝试次数 = API 数量 * 模型数量（如果启用容错）
    max_attempts = len(api_configs_list) * len(models_list) if enable_failover else 1
    
    for attempt in range(max_attempts):
        # 选择 API 和模型
        api_config, api_index = api_selector.select(
            api_configs_list,
            used_api_indices if enable_failover else None
        )
        model, model_index = model_selector.select(
            models_list,
            used_model_indices if enable_failover else None
        )
        
        if api_config is None or model is None:
            error_msg = "所有 API 和模型组合都已尝试，无可用资源"
            print(f"⚠️  {error_msg}")
            notification_manager.notify(error_msg, is_success=False)
            break
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"🔄 尝试次数: {attempt + 1}/{max_attempts}")
            print(f"🌐 使用 API: {api_config.name}")
            print(f"🤖 使用模型: {model}")
            print(f"{'='*60}\n")
        
        # 通知开始生成
        notification_manager.notify(
            f"开始生成图片 - API: {api_config.name}, 模型: {model}",
            is_success=True,
            data={'prompt': prompt, 'model': model, 'api': api_config.name}
        )
        
        # 尝试生成图片
        result_image = _generate_image_single(
            prompt=prompt,
            api_config=api_config,
            model=model,
            size_str=size_str,
            max_retries=max_retries,
            retry_on_network_error=retry_on_network_error,
            retry_delay=retry_delay,
            submit_timeout=submit_timeout,
            poll_timeout=poll_timeout,
            download_timeout=download_timeout,
            poll_interval=poll_interval,
            verbose=verbose,
            proxies=proxies,
        )
        
        if result_image is not None:
            # 生成成功
            image = result_image
            
            # 保存图片到本地
            if save_path:
                try:
                    image.save(save_path)
                    if verbose:
                        print(f"💾 图片已保存到: {save_path}")
                except Exception as e:
                    print(f"⚠️  保存图片失败: {str(e)}")
            
            # 上传到图床
            uploaded_url = None
            if upload_on_success and image_upload_callbacks:
                upload_manager = ImageUploadManager(
                    upload_callbacks=image_upload_callbacks,
                    strategy=upload_strategy,
                    verbose=verbose,
                )
                uploaded_url = upload_manager.upload(image)
            
            # 构建返回结果
            result = {
                'image': image,
                'url': uploaded_url,
                'model': model,
                'api': api_config.name,
                'size': image.size,
            }
            
            # 通知成功
            notification_manager.notify(
                f"图片生成成功！",
                is_success=True,
                data=result
            )
            
            return result
        
        # 生成失败，标记当前组合已使用
        notification_manager.notify(
            f"生成失败 - API: {api_config.name}, 模型: {model}",
            is_success=False,
            data={'prompt': prompt, 'model': model, 'api': api_config.name}
        )
        
        if enable_failover:
            # 标记当前模型已失败
            used_model_indices.add(model_index)
            
            # 如果所有模型都试过了，切换 API 并重置模型
            if len(used_model_indices) >= len(models_list):
                used_api_indices.add(api_index)
                used_model_indices.clear()
                if verbose:
                    print(f"⚠️  所有模型在当前 API 上都失败，切换到下一个 API")
        else:
            # 不启用容错，直接退出
            break
    
    error_msg = "图片生成失败，已尝试所有可用的 API 和模型组合"
    print(f"❌ {error_msg}")
    notification_manager.notify(error_msg, is_success=False)
    return None


def _generate_image_single(
    prompt: str,
    api_config: APIConfig,
    model: str,
    size_str: str,
    max_retries: int,
    retry_on_network_error: bool,
    retry_delay: float,
    submit_timeout: int,
    poll_timeout: int,
    download_timeout: int,
    poll_interval: int,
    verbose: bool,
    proxies: Optional[Dict[str, str]],
) -> Optional[Image.Image]:
    """
    使用单个 API 配置和模型生成图片（内部函数）
    
    :return: 成功返回 PIL Image 对象，失败返回 None
    """
    
    common_headers = {
        "Authorization": f"Bearer {api_config.api_key}",
        "Content-Type": "application/json",
    }
    
    # ==================== 提交任务（支持重试） ====================
    
    task_id = None
    for retry in range(max_retries + 1):
        try:
            if verbose and retry > 0:
                print(f"🔄 重试提交任务 ({retry}/{max_retries})...")
            
            if verbose and retry == 0:
                print(f"🚀 正在提交图片生成任务")
                print(f"ℹ️  提示词: {prompt}")
            
            response = requests.post(
                f"{api_config.base_url}v1/images/generations",
                headers={**common_headers, "X-ModelScope-Async-Mode": "true"},
                data=json.dumps({
                    "model": model,
                    "prompt": prompt,
                    "size": size_str
                }, ensure_ascii=False).encode('utf-8'),
                timeout=submit_timeout,
                proxies=proxies,
            )
            response.raise_for_status()
            task_id = response.json()["task_id"]
            
            if verbose:
                print(f"✅ 任务提交成功")
                print(f"🆔 任务ID: {task_id}")
            break
            
        except requests.exceptions.RequestException as e:
            is_network_error = isinstance(e, (requests.exceptions.ConnectionError, requests.exceptions.Timeout))
            
            if retry < max_retries and (retry_on_network_error or not is_network_error):
                if verbose:
                    print(f"⚠️  提交任务失败: {str(e)}")
                    print(f"⏰ {retry_delay}秒后重试...")
                time.sleep(retry_delay)
            else:
                print(f"❌ 提交任务失败: {str(e)}")
                return None
        except Exception as e:
            print(f"❌ 提交任务时发生未知错误: {str(e)}")
            return None
    
    if task_id is None:
        return None
    
    # ==================== 轮询任务状态 ====================
    
    start_time = time.time()
    last_status = None
    
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > poll_timeout:
            print(f"⚠️  任务执行超时 ({poll_timeout}秒)")
            return None
        
        # 查询任务状态（支持重试）
        data = None
        for retry in range(max_retries + 1):
            try:
                result = requests.get(
                    f"{api_config.base_url}v1/tasks/{task_id}",
                    headers={**common_headers, "X-ModelScope-Task-Type": "image_generation"},
                    timeout=submit_timeout,
                    proxies=proxies,
                )
                result.raise_for_status()
                data = result.json()
                break
                
            except requests.exceptions.RequestException as e:
                is_network_error = isinstance(e, (requests.exceptions.ConnectionError, requests.exceptions.Timeout))
                
                if retry < max_retries and (retry_on_network_error or not is_network_error):
                    if verbose:
                        print(f"⚠️  查询任务状态失败: {str(e)}")
                        print(f"⏰ {retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                else:
                    print(f"❌ 查询任务状态失败: {str(e)}")
                    return None
            except Exception as e:
                print(f"❌ 查询任务状态时发生未知错误: {str(e)}")
                return None
        
        if data is None:
            return None
        
        task_status = data["task_status"]
        
        # 只在状态变化时打印
        if task_status != last_status:
            status_display = get_status_display(task_status)
            elapsed = int(elapsed_time)
            if verbose:
                print(f"📊 当前任务状态: {status_display} (已耗时: {elapsed}秒)")
            last_status = task_status
        
        if task_status == "SUCCEED":
            if verbose:
                print("🎉 图片生成成功！")
            
            # 下载图片（支持重试）
            image_url = data["output_images"][0]
            for retry in range(max_retries + 1):
                try:
                    if verbose and retry == 0:
                        print(f"⬇️  正在下载图片...")
                    elif verbose:
                        print(f"🔄 重试下载图片 ({retry}/{max_retries})...")
                    
                    image_content = requests.get(
                        image_url,
                        timeout=download_timeout,
                        proxies=proxies,
                    ).content
                    image = Image.open(BytesIO(image_content))
                    
                    if verbose:
                        print(f"✅ 图片下载成功，尺寸: {image.size}")
                    return image
                    
                except Exception as e:
                    if retry < max_retries:
                        if verbose:
                            print(f"⚠️  下载图片失败: {str(e)}")
                            print(f"⏰ {retry_delay}秒后重试...")
                        time.sleep(retry_delay)
                    else:
                        print(f"❌ 下载图片失败: {str(e)}")
                        return None
            
        elif task_status == "FAILED":
            error_message = data.get("error_message", "未知错误")
            print(f"❌ 图片生成失败: {error_message}")
            return None
        
        elif task_status == "CANCELED":
            print(f"⚠️  任务已被取消")
            return None
        
        elif task_status == "TIMEOUT":
            print(f"⏰ 任务执行超时")
            return None
        
        # 任务仍在进行中，继续等待
        time.sleep(poll_interval)