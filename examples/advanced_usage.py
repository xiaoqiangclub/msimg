# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# GitHub：https://github.com/xiaoqiangclub
# 邮箱：xiaoqiangclub@hotmail.com
# 创建时间：2025-01-20 10:00
# 文件描述：高级使用示例
# 文件路径：examples/advanced_usage.py

from msimg import (
    generate_image,
    APIConfig,
    SelectionStrategy,
)

# ==================== 示例 1: 多 API 配置 ====================
print("=" * 60)
print("示例 1: 多 API 配置（自动故障转移）")
print("=" * 60)

result = generate_image(
    prompt="壮丽的山脉风景",
    
    # 方式 1: 使用字符串列表（使用默认 base_url）
    api_configs=["api-key-1", "api-key-2"],
    
    # 方式 2: 使用 APIConfig 对象（可自定义 base_url）
    # api_configs=[
    #     APIConfig(api_key="key1", name="主站"),
    #     APIConfig(api_key="key2", base_url="https://backup.api.com/", name="备用站"),
    # ],
    
    models="qwen",
    enable_failover=True,  # 启用容错
)

if result:
    print(f"\n✅ 使用的 API: {result['api']}")

# ==================== 示例 2: 多模型配置 ====================
print("\n\n" + "=" * 60)
print("示例 2: 多模型配置（优先级排序）")
print("=" * 60)

result = generate_image(
    prompt="梦幻般的星空",
    api_configs="your-api-key",
    
    # 按优先级排列多个模型
    models=["flux-majic", "qwen", "sdxl-muse"],
    model_selection_strategy=SelectionStrategy.SEQUENTIAL,
    
    enable_failover=True,
    size="16:9",
    save_path="starry_sky.jpg"
)

if result:
    print(f"\n✅ 实际使用的模型: {result['model']}")

# ==================== 示例 3: 选择策略 ====================
print("\n\n" + "=" * 60)
print("示例 3: 不同的选择策略")
print("=" * 60)

# 随机选择模型
result = generate_image(
    prompt="可爱的动物",
    api_configs="your-api-key",
    models=["qwen", "flux-majic"],
    model_selection_strategy=SelectionStrategy.RANDOM,  # 随机选择
    verbose=False
)

if result:
    print(f"✅ 随机选择的模型: {result['model']}")

# ==================== 示例 4: 网络重试配置 ====================
print("\n\n" + "=" * 60)
print("示例 4: 网络重试配置")
print("=" * 60)

result = generate_image(
    prompt="未来科技",
    api_configs="your-api-key",
    models="qwen",
    
    # 重试配置
    max_retries=5,              # 最大重试 5 次
    retry_on_network_error=True,  # 遇到网络错误时重试
    retry_delay=3.0,             # 重试间隔 3 秒
    
    # 超时配置
    submit_timeout=30,           # 提交超时 30 秒
    poll_timeout=600,            # 轮询超时 600 秒（10 分钟）
    download_timeout=60,         # 下载超时 60 秒
)

# ==================== 示例 5: 使用代理 ====================
print("\n\n" + "=" * 60)
print("示例 5: 使用代理")
print("=" * 60)

result = generate_image(
    prompt="美丽的花朵",
    api_configs="your-api-key",
    models="qwen",
    
    # 代理配置
    proxies={
        'http': 'http://proxy.example.com:8080',
        'https': 'https://proxy.example.com:8080',
    },
    
    verbose=False
)

# ==================== 示例 6: 完整的高级配置 ====================
print("\n\n" + "=" * 60)
print("示例 6: 完整的高级配置")
print("=" * 60)

result = generate_image(
    # 基础配置
    prompt="史诗般的幻想世界",
    api_configs=[
        APIConfig(api_key="key1", name="主站"),
        APIConfig(api_key="key2", name="备用站"),
    ],
    
    # 模型配置
    models=["flux-majic", "qwen", "sdxl-muse"],
    model_selection_strategy=SelectionStrategy.SEQUENTIAL,
    
    # 图片配置
    size="1920x1080",
    save_path="fantasy_world.jpg",
    
    # API 配置
    api_selection_strategy=SelectionStrategy.SEQUENTIAL,
    
    # 容错和重试
    enable_failover=True,
    max_retries=3,
    retry_on_network_error=True,
    retry_delay=2.0,
    
    # 超时配置
    submit_timeout=30,
    poll_timeout=300,
    download_timeout=60,
    poll_interval=5,
    
    # 详细日志
    verbose=True,
)

if result:
    print(f"\n🎉 大功告成！")
    print(f"   API: {result['api']}")
    print(f"   模型: {result['model']}")
    print(f"   尺寸: {result['size']}")