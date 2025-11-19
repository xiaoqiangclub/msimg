# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# GitHub：https://github.com/xiaoqiangclub
# 邮箱：xiaoqiangclub@hotmail.com
# 创建时间：2025-01-20 10:00
# 文件描述：基础使用示例
# 文件路径：examples/basic_usage.py

from msimg import generate_image

# ==================== 示例 1: 最简单的用法 ====================
print("=" * 60)
print("示例 1: 最简单的用法")
print("=" * 60)

result = generate_image(
    prompt="一只金色的猫坐在云朵上",
    api_configs="your-api-key-here"  # 替换为你的 API Key
)

if result:
    print(f"\n✅ 生成成功！")
    print(f"   模型: {result['model']}")
    print(f"   尺寸: {result['size']}")
    result['image'].save("cat_on_cloud.jpg")
    print(f"   已保存到: cat_on_cloud.jpg")
else:
    print("\n❌ 生成失败")

# ==================== 示例 2: 使用预设模型 ====================
print("\n\n" + "=" * 60)
print("示例 2: 使用预设模型")
print("=" * 60)

result = generate_image(
    prompt="赛博朋克城市夜景，霓虹灯，未来感",
    api_configs="your-api-key-here",
    models="flux-majic",  # 使用 FLUX 魔法模型
    size="16:9",
    save_path="cyberpunk_city.jpg"
)

if result:
    print(f"\n✅ 生成成功！保存到: cyberpunk_city.jpg")

# ==================== 示例 3: 自定义尺寸 ====================
print("\n\n" + "=" * 60)
print("示例 3: 自定义尺寸")
print("=" * 60)

result = generate_image(
    prompt="美丽的日落海景",
    api_configs="your-api-key-here",
    models="qwen",
    size="1920x1080",  # 自定义尺寸
    save_path="sunset.jpg"
)

if result:
    print(f"\n✅ 生成成功！")

# ==================== 示例 4: 多种预设模型 ====================
print("\n\n" + "=" * 60)
print("示例 4: 尝试不同的预设模型")
print("=" * 60)

# 可用的预设模型
presets = {
    "qwen": "通义万相",
    "flux-majic": "FLUX 魔法模型",
}

for preset_name, description in presets.items():
    print(f"\n使用模型: {description} ({preset_name})")
    
    result = generate_image(
        prompt="可爱的小猫咪",
        api_configs="your-api-key-here",
        models=preset_name,
        size="1:1",
        verbose=False  # 关闭详细日志
    )
    
    if result:
        filename = f"cat_{preset_name}.jpg"
        result['image'].save(filename)
        print(f"✅ 生成成功！保存到: {filename}")
    else:
        print(f"❌ 生成失败")