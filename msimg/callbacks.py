# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# GitHub：https://github.com/xiaoqiangclub
# 邮箱：xiaoqiangclub@hotmail.com
# 创建时间：2025-01-20 10:00:00
# 文件描述：回调函数处理，包括资源选择器、通知管理器、图床上传管理器
# 文件路径：msimg/callbacks.py

from typing import List, Callable, Dict, Any, Optional, Union
from PIL import Image
import random

from .strategies import SelectionStrategy, NotificationMode


class ResourceSelector:
    """
    资源选择器（用于 API、模型、回调函数的选择策略）
    
    支持三种选择策略：
    - SEQUENTIAL: 顺序选择（从第一个开始）
    - RANDOM: 随机选择
    - ROUND_ROBIN: 轮询选择（记住上次位置）
    """

    def __init__(self, strategy: SelectionStrategy):
        """
        初始化选择器
        
        :param strategy: 选择策略
        """
        self.strategy = strategy
        self.round_robin_index = 0

    def select(self, resources: List, used_indices: set = None) -> tuple:
        """
        选择资源
        
        :param resources: 资源列表
        :param used_indices: 已使用过的索引集合（用于容错时跳过已失败的）
        :return: (选中的资源, 索引)
        """
        if not resources:
            return None, -1

        if used_indices is None:
            used_indices = set()

        # 获取可用的索引
        available_indices = [i for i in range(
            len(resources)) if i not in used_indices]
        if not available_indices:
            return None, -1

        if self.strategy == SelectionStrategy.RANDOM:
            # 随机选择
            index = random.choice(available_indices)
        elif self.strategy == SelectionStrategy.SEQUENTIAL:
            # 顺序选择（第一个可用的）
            index = available_indices[0]
        elif self.strategy == SelectionStrategy.ROUND_ROBIN:
            # 轮询选择
            # 从当前位置开始找下一个可用的
            for _ in range(len(resources)):
                if self.round_robin_index in available_indices:
                    index = self.round_robin_index
                    self.round_robin_index = (
                        self.round_robin_index + 1) % len(resources)
                    break
                self.round_robin_index = (
                    self.round_robin_index + 1) % len(resources)
            else:
                index = available_indices[0]
        else:
            index = available_indices[0]

        return resources[index], index


class NotificationManager:
    """
    通知管理器
    
    负责管理消息通知的发送，支持多种通知模式和策略
    """

    def __init__(
        self,
        callbacks: Optional[List[Callable]] = None,
        mode: NotificationMode = NotificationMode.NONE,
        strategy: SelectionStrategy = SelectionStrategy.SEQUENTIAL,
        verbose: bool = True,
    ):
        """
        初始化通知管理器
        
        :param callbacks: 回调函数列表
        :param mode: 通知模式（SUCCESS/ERROR/ALL/NONE）
        :param strategy: 回调函数选择策略
        :param verbose: 是否显示详细日志
        """
        self.callbacks = callbacks or []
        self.mode = mode
        self.strategy = strategy
        self.verbose = verbose
        self.selector = ResourceSelector(strategy)

    def notify(self, message: str, is_success: bool = True, data: Optional[Dict[str, Any]] = None):
        """
        发送通知
        
        :param message: 消息内容
        :param is_success: 是否为成功消息
        :param data: 附加数据
        """
        # 根据模式判断是否需要发送
        if self.mode == NotificationMode.NONE:
            return

        if self.mode == NotificationMode.SUCCESS and not is_success:
            return

        if self.mode == NotificationMode.ERROR and is_success:
            return

        if not self.callbacks:
            return

        # 根据策略选择回调函数
        if self.strategy == SelectionStrategy.SEQUENTIAL:
            # 顺序调用所有回调
            self._notify_all(message, is_success, data)
        elif self.strategy == SelectionStrategy.RANDOM:
            # 随机选择一个回调
            self._notify_single(message, is_success, data)
        elif self.strategy == SelectionStrategy.ROUND_ROBIN:
            # 轮询选择回调
            self._notify_single(message, is_success, data)
        else:
            # 默认调用所有
            self._notify_all(message, is_success, data)

    def _notify_all(self, message: str, is_success: bool, data: Optional[Dict[str, Any]]):
        """调用所有回调函数"""
        for index, callback in enumerate(self.callbacks):
            self._call_callback(callback, index, message, is_success, data)

    def _notify_single(self, message: str, is_success: bool, data: Optional[Dict[str, Any]]):
        """调用单个回调函数"""
        callback, index = self.selector.select(self.callbacks)
        if callback:
            self._call_callback(callback, index, message, is_success, data)

    def _call_callback(
        self,
        callback: Callable,
        index: int,
        message: str,
        is_success: bool,
        data: Optional[Dict[str, Any]]
    ):
        """调用回调函数"""
        try:
            callback_name = getattr(callback, '__name__', f'回调函数{index+1}')

            # 构建通知数据
            notification_data = {
                'message': message,
                'is_success': is_success,
                'data': data or {},
            }

            # 调用回调函数
            callback(notification_data)

            if self.verbose:
                print(f"📢 通知已发送到: {callback_name}")

        except Exception as e:
            if self.verbose:
                print(f"⚠️  调用回调函数失败: {str(e)}")


class ImageUploadManager:
    """
    图床上传管理器
    
    负责管理图片上传到图床的过程，支持多图床和不同的上传策略
    """

    def __init__(
        self,
        upload_callbacks: Optional[List[Callable[[
            Union[str, bytes, Image.Image]], str]]] = None,
        strategy: SelectionStrategy = SelectionStrategy.SEQUENTIAL,
        verbose: bool = True,
    ):
        """
        初始化上传管理器
        
        :param upload_callbacks: 上传回调函数列表，函数签名为 func(image) -> str(url)
        :param strategy: 上传策略
        :param verbose: 是否显示详细日志
        """
        self.upload_callbacks = upload_callbacks or []
        self.strategy = strategy
        self.verbose = verbose
        self.selector = ResourceSelector(strategy)

    def upload(self, image: Union[str, bytes, Image.Image]) -> Optional[str]:
        """
        上传图片到图床
        
        :param image: 图片输入，支持：
                     - PIL.Image.Image 对象
                     - 本地文件路径 (str)
                     - 网络图片 URL (str)
                     - Base64 编码 (str)
                     - 图片字节流 (bytes)
        :return: 成功返回图片 URL，失败返回 None
        """
        if not self.upload_callbacks:
            return None

        if self.verbose:
            print(f"\n📤 开始上传图片到图床...")

        # 根据策略上传
        if self.strategy == SelectionStrategy.SEQUENTIAL:
            # 顺序尝试所有图床（故障转移）
            return self._upload_with_failover(image)
        else:
            # 选择单个图床上传
            return self._upload_single(image)

    def _upload_with_failover(self, image: Union[str, bytes, Image.Image]) -> Optional[str]:
        """顺序尝试所有图床（故障转移）"""
        for index, callback in enumerate(self.upload_callbacks):
            url = self._call_upload_callback(callback, index, image)
            if url:
                return url

        print(f"❌ 所有图床上传均失败")
        return None

    def _upload_single(self, image: Union[str, bytes, Image.Image]) -> Optional[str]:
        """上传到单个选中的图床"""
        callback, index = self.selector.select(self.upload_callbacks)
        if callback:
            return self._call_upload_callback(callback, index, image)
        return None

    def _call_upload_callback(
        self,
        callback: Callable[[Union[str, bytes, Image.Image]], str],
        index: int,
        image: Union[str, bytes, Image.Image]
    ) -> Optional[str]:
        """调用上传回调函数"""
        try:
            callback_name = getattr(callback, '__name__', f'图床{index+1}')
            if self.verbose:
                print(f"🔄 尝试使用: {callback_name}")

            url = callback(image)

            if url:
                if self.verbose:
                    print(f"✅ 上传成功！")
                    print(f"🔗 图片URL: {url}")
                return url
            else:
                if self.verbose:
                    print(f"⚠️  {callback_name} 返回空URL")
                return None

        except Exception as e:
            if self.verbose:
                print(f"⚠️  {callback_name} 上传失败: {str(e)}")
            return None
