"""
MSIMG CLI 核心模块 - 会话管理
"""

import time
from typing import Dict, Any, Optional
from datetime import datetime


class SessionManager:
    """会话管理器"""

    def __init__(self):
        """初始化会话管理器"""
        self.session_start = time.time()
        self.active_session = False
        self.session_data: Dict[str, Any] = {}

    def start_session(self, session_name: Optional[str] = None) -> str:
        """启动新会话"""
        session_id = f"session_{int(time.time())}_{session_name or 'default'}"
        self.active_session = True
        self.session_data = {
            "id": session_id,
            "start_time": datetime.now().isoformat(),
            "commands_executed": 0,
            "last_activity": time.time()
        }
        print(f"✅ 会话已启动: {session_id}")
        return session_id

    def end_session(self) -> bool:
        """结束当前会话"""
        if not self.active_session:
            print("⚠️  当前没有活跃会话")
            return False

        session_duration = time.time() - self.session_start
        print(f"✅ 会话已结束: {self.session_data['id']}")
        print(f"⏱️  会话时长: {session_duration:.2f}秒")

        self.active_session = False
        self.session_data = {}
        return True

    def get_session_info(self) -> Dict[str, Any]:
        """获取会话信息"""
        if not self.active_session:
            return {}

        current_time = time.time()
        session_duration = current_time - self.session_start

        info = self.session_data.copy()
        info["duration_seconds"] = session_duration
        info["is_active"] = self.active_session
        return info

    def record_command(self, command: str) -> None:
        """记录执行的命令"""
        if self.active_session:
            self.session_data["commands_executed"] += 1
            self.session_data["last_activity"] = time.time()

    def is_session_active(self) -> bool:
        """检查会话是否活跃"""
        return self.active_session