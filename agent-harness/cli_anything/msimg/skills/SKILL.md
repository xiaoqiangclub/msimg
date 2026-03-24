"""
MSIMG CLI - 针对AI代理的技能定义

此文件为AI代理提供了关于MSIMG CLI工具的详细说明，包括命令、参数和使用示例。
"""

name: str = "msimg-cli"
version: str = "0.0.1"
description: str = "MSIMG CLI - 魔塔社区文生图API命令行工具，支持图片生成、配置管理、图床上传等功能"

commands: list = [
    {
        "name": "generate",
        "description": "生成图片",
        "options": [
            {"name": "--prompt, -p", "type": "TEXT", "required": True, "description": "图片生成的提示词"},
            {"name": "--api-key, -k", "type": "TEXT", "required": True, "description": "API密钥"},
            {"name": "--model, -m", "type": "TEXT", "default": "qwen", "description": "使用的模型"},
            {"name": "--size, -s", "type": "TEXT", "default": "16:9", "description": "图片尺寸"},
            {"name": "--save-path, -o", "type": "TEXT", "description": "保存路径"},
            {"name": "--enable-failover", "type": "FLAG", "description": "启用容错"},
            {"name": "--max-retries", "type": "INTEGER", "default": 3, "description": "最大重试次数"},
            {"name": "--verbose", "type": "FLAG", "description": "显示详细日志"},
            {"name": "--json", "type": "FLAG", "description": "JSON格式输出"}
        ],
        "examples": [
            "cli-anything-msimg generate --prompt \"一只金色的猫\" --api-key YOUR_API_KEY",
            "cli-anything-msimg generate -p \"赛博朋克城市\" -k YOUR_API_KEY -m flux-majic -s 16:9 -o ./output/cyberpunk.jpg"
        ]
    },
    {
        "name": "models",
        "description": "查看支持的模型",
        "options": [
            {"name": "--model, -m", "type": "TEXT", "description": "指定模型名称，不指定则显示所有预设模型"}
        ],
        "examples": [
            "cli-anything-msimg models",
            "cli-anything-msimg models -m qwen"
        ]
    },
    {
        "name": "sizes",
        "description": "查看支持的图片尺寸",
        "options": [
            {"name": "--size, -s", "type": "TEXT", "description": "指定尺寸名称，不指定则显示所有预设尺寸"}
        ],
        "examples": [
            "cli-anything-msimg sizes",
            "cli-anything-msimg sizes -s 16:9"
        ]
    },
    {
        "name": "config",
        "description": "配置管理命令组",
        "subcommands": [
            {
                "name": "set",
                "description": "设置配置项",
                "options": [
                    {"name": "--key, -k", "type": "TEXT", "required": True, "description": "配置项名称"},
                    {"name": "--value, -v", "type": "TEXT", "required": True, "description": "配置项值"}
                ],
                "examples": [
                    "cli-anything-msimg config set -k api_key -v YOUR_API_KEY",
                    "cli-anything-msimg config set -k default_model -v flux-majic"
                ]
            },
            {
                "name": "get",
                "description": "获取配置项",
                "options": [
                    {"name": "--key, -k", "type": "TEXT", "required": True, "description": "配置项名称"}
                ],
                "examples": [
                    "cli-anything-msimg config get -k api_key",
                    "cli-anything-msimg config get -k default_model"
                ]
            },
            {
                "name": "list",
                "description": "列出所有配置项",
                "examples": [
                    "cli-anything-msimg config list"
                ]
            },
            {
                "name": "reset",
                "description": "重置为默认配置",
                "examples": [
                    "cli-anything-msimg config reset"
                ]
            }
        ],
        "examples": [
            "cli-anything-msimg config set --key api_key --value YOUR_API_KEY",
            "cli-anything-msimg config get --key default_model",
            "cli-anything-msimg config list",
            "cli-anything-msimg config reset"
        ]
    }
]

# 预设模型列表
preset_models: dict = {
    "qwen": "Qwen/Qwen-Image",
    "flux-majic": "MAILAND/majicflus_v1",
    "flux-muse": "MusePublic/489_ckpt_FLUX_1",
    "flux-xiaohongshu": "yiwanji/FLUX_xiao_hong_shu_ji_zhi_zhen_shi_V2",
    "sdxl-muse": "MusePublic/42_ckpt_SD_XL"
}

# 预设尺寸列表
preset_sizes: dict = {
    "1:1": "1328x1328",
    "16:9": "1664x928",
    "9:16": "928x1664",
    "4:3": "1472x1140",
    "3:4": "1140x1472",
    "3:2": "1584x1056",
    "2:3": "1056x1584"
}

extended_config_options: dict = {
    "submit_timeout": {"type": "int", "default": 30, "description": "提交任务的超时时间（秒）"},
    "poll_timeout": {"type": "int", "default": 300, "description": "轮询任务状态的总超时时间（秒）"},
    "download_timeout": {"type": "int", "default": 60, "description": "下载图片的超时时间（秒）"},
    "poll_interval": {"type": "int", "default": 5, "description": "轮询间隔时间（秒）"},
    "retry_delay": {"type": "float", "default": 2.0, "description": "重试延迟时间（秒）"},
    "retry_on_network_error": {"type": "bool", "default": True, "description": "网络错误时是否重试"},
    "upload_on_success": {"type": "bool", "default": False, "description": "生成成功后是否自动上传"},
    "notification_mode": {"type": "str", "default": "NONE", "description": "通知模式（SUCCESS/ERROR/ALL/NONE）"}
}

image_upload_config: dict = {
    "default_uploader": {"type": "str", "default": "smms", "description": "默认图床上传器"},
    "smms_token": {"type": "str", "default": "", "description": "SM.MS图床API Token"},
    "imgurl_token": {"type": "str", "default": "", "description": "ImgURL图床API Token"},
    "imgurl_uid": {"type": "str", "default": "", "description": "ImgURL图床用户UID"},
    "luoguo_enabled": {"type": "bool", "default": True, "description": "是否启用路过图床"},
    "qiniu_access_key": {"type": "str", "default": "", "description": "七牛云Access Key"},
    "qiniu_secret_key": {"type": "str", "default": "", "description": "七牛云Secret Key"},
    "qiniu_bucket": {"type": "str", "default": "", "description": "七牛云存储空间"},
    "qiniu_domain": {"type": "str", "default": "", "description": "七牛云CDN域名"},
    "aliyun_access_key_id": {"type": "str", "default": "", "description": "阿里云Access Key ID"},
    "aliyun_access_key_secret": {"type": "str", "default": "", "description": "阿里云Access Key Secret"},
    "aliyun_endpoint": {"type": "str", "default": "", "description": "阿里云Endpoint"},
    "aliyun_bucket_name": {"type": "str", "default": "", "description": "阿里云Bucket名称"},
    "upyun_bucket": {"type": "str", "default": "", "description": "又拍云服务名称"},
    "upyun_username": {"type": "str", "default": "", "description": "又拍云操作员账号"},
    "upyun_password": {"type": "str", "default": "", "description": "又拍云操作员密码"},
    "upyun_domain": {"type": "str", "default": "", "description": "又拍云加速域名"},
    "github_token": {"type": "str", "default": "", "description": "GitHub Token"},
    "github_repo": {"type": "str", "default": "", "description": "GitHub仓库（用户名/仓库名）"},
    "github_branch": {"type": "str", "default": "main", "description": "GitHub分支"},
    "github_use_jsdelivr": {"type": "bool", "default": True, "description": "是否使用jsDelivr CDN"},
    "local_storage_dir": {"type": "str", "default": "./uploads", "description": "本地存储目录"},
    "local_base_url": {"type": "str", "default": "http://localhost/uploads", "description": "本地访问基础URL"}
}

usage_notes: str = """
使用注意事项：

1. API密钥获取：
   - 访问 https://www.modelscope.cn/my/myaccesstoken 获取API密钥
   - 每日有2000次免费调用额度

2. 模型选择：
   - 使用预设模型名称（如qwen, flux-majic）或完整模型ID
   - 支持多模型容错，按顺序尝试

3. 图片尺寸：
   - 支持预设比例（如16:9, 1:1）或自定义尺寸（如1920x1080）

4. 输出格式：
   - 支持普通文本输出和JSON格式输出（--json参数）
   - 支持保存生成的图片到本地

5. 错误处理：
   - 启用容错（--enable-failover）可在API或模型失败时自动切换
   - 可设置最大重试次数（--max-retries）

6. 配置管理：
   - 使用 config 命令组管理配置项
   - 支持设置API密钥、默认模型、超时参数等
   - 可通过 config list 查看所有配置项
   - 可通过 config reset 恢复默认配置
"""