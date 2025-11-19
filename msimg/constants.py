# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# GitHub：https://github.com/xiaoqiangclub
# 邮箱：xiaoqiangclub@hotmail.com
# 创建时间：2025-01-20 10:00
# 文件描述：常量定义
# 文件路径：msimg/constants.py

# 默认 API 基础 URL
DEFAULT_BASE_URL = "https://api-inference.modelscope.cn/"

# 支持的图片尺寸比例映射（快速设置）
SIZE_PRESETS = {
    "1:1": "1328x1328",
    "16:9": "1664x928",
    "9:16": "928x1664",
    "4:3": "1472x1140",
    "3:4": "1140x1472",
    "3:2": "1584x1056",
    "2:3": "1056x1584",
}

# 预设模型列表
MODEL_PRESETS = {
    # 通义万相
    "qwen": "Qwen/Qwen-Image",
    "qwen-image": "Qwen/Qwen-Image",
    
    # FLUX 系列
    "flux-majic": "MAILAND/majicflus_v1",
    "flux-muse": "MusePublic/489_ckpt_FLUX_1",
    "flux-xiaohongshu": "yiwanji/FLUX_xiao_hong_shu_ji_zhi_zhen_shi_V2",
    
    # Stable Diffusion XL
    "sdxl-muse": "MusePublic/42_ckpt_SD_XL",
}

# 完整模型 ID（用于验证）
FULL_MODEL_IDS = {
    "Qwen/Qwen-Image",
    "MAILAND/majicflus_v1",
    "MusePublic/489_ckpt_FLUX_1",
    "yiwanji/FLUX_xiao_hong_shu_ji_zhi_zhen_shi_V2",
    "MusePublic/42_ckpt_SD_XL",
}

# 任务状态映射
TASK_STATUS_MAP = {
    "PENDING": "⏳ 等待中",
    "PROCESSING": "🎨 生成中",
    "RUNNING": "🏃 执行中",
    "SUCCEED": "✅ 成功",
    "FAILED": "❌ 失败",
    "CANCELED": "⚠️ 已取消",
    "TIMEOUT": "⏰ 超时",
}