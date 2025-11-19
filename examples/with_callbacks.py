# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# GitHub：https://github.com/xiaoqiangclub
# 邮箱：xiaoqiangclub@hotmail.com
# 创建时间：2025-01-20 10:00
# 文件描述：回调函数使用示例
# 文件路径：examples/with_callbacks.py

import time
from msimg import (
    generate_image,
    SelectionStrategy,
    NotificationMode,
)

# ==================== 图床上传回调示例 ====================

def upload_to_imgur(image):
    """上传到 Imgur（示例）"""
    print("  📤 正在上传到 Imgur...")
    time.sleep(1)  # 模拟上传过程
    # 实际使用时需要实现真实的上传逻辑
    # return "https://i.imgur.com/xxxxx.jpg"
    raise Exception("Imgur 上传失败（示例）")

def upload_to_smms(image):
    """上传到 SM.MS（示例）"""
    print("  📤 正在上传到 SM.MS...")
    time.sleep(1)
    # 实际使用时需要实现真实的上传逻辑
    return "https://sm.ms/xxxxx.jpg"

def upload_to_custom(image):
    """上传到自定义图床（示例）"""
    print(" 📤 正在上传到自定义图床...")
    time.sleep(1)
    return "https://custom.img/xxxxx.jpg"

# ==================== 消息通知回调示例 ====================

def send_to_wechat(data):
    """发送到微信（示例）"""
    message = data['message']
    is_success = data['is_success']
    extra_data = data.get('data', {})
    
    emoji = "✅" if is_success else "❌"
    print(f"\n📱 [微信通知] {emoji} {message}")
    
    if extra_data:
        if 'model' in extra_data:
            print(f"   模型: {extra_data.get('model')}")
        if 'url' in extra_data:
            print(f"   URL: {extra_data.get('url')}")

def send_to_email(data):
    """发送到邮箱（示例）"""
    message = data['message']
    is_success = data['is_success']
    
    print(f"\n📧 [邮件通知] {'成功' if is_success else '失败'}: {message}")

def send_to_slack(data):
    """发送到 Slack（示例）"""
    message = data['message']
    print(f"\n💬 [Slack通知] {message}")

# ==================== 示例 1: 图床上传（故障转移） ====================
print("=" * 60)
print("示例 1: 图床上传（自动故障转移）")
print("=" * 60)

result = generate_image(
    prompt="美丽的风景",
    api_configs="your-api-key",
    models="qwen",
    size="16:9",
    
    # 配置多个图床（按顺序尝试，直到成功）
    image_upload_callbacks=[
        upload_to_imgur,   # 第一个尝试 Imgur
        upload_to_smms,    # Imgur 失败后尝试 SM.MS
        upload_to_custom,  # SM.MS 失败后尝试自定义图床
    ],
    upload_strategy=SelectionStrategy.SEQUENTIAL,  # 顺序故障转移
    upload_on_success=True,  # 生成成功后自动上传
    
    verbose=True
)

if result and result['url']:
    print(f"\n🎉 图片已上传！")
    print(f"   URL: {result['url']}")

# ==================== 示例 2: 消息通知（仅成功） ====================
print("\n\n" + "=" * 60)
print("示例 2: 消息通知（仅发送成功消息）")
print("=" * 60)

result = generate_image(
    prompt="可爱的小狗",
    api_configs="your-api-key",
    models="qwen",
    
    # 消息通知配置
    notification_callbacks=[send_to_wechat, send_to_email],
    notification_mode=NotificationMode.SUCCESS,  # 仅发送成功消息
    notification_strategy=SelectionStrategy.SEQUENTIAL,  # 调用所有回调
    
    verbose=False
)

# ==================== 示例 3: 消息通知（仅错误） ====================
print("\n\n" + "=" * 60)
print("示例 3: 消息通知（仅发送错误消息）")
print("=" * 60)

result = generate_image(
    prompt="测试",
    api_configs="invalid-key",  # 故意使用无效 key 触发错误
    models="qwen",
    
    notification_callbacks=[send_to_wechat],
    notification_mode=NotificationMode.ERROR,  # 仅发送错误消息
    
    verbose=False
)

# ==================== 示例 4: 消息通知（全部） ====================
print("\n\n" + "=" * 60)
print("示例 4: 消息通知（发送所有消息）")
print("=" * 60)

result = generate_image(
    prompt="太空站",
    api_configs="your-api-key",
    models=["flux-majic", "qwen"],
    
    notification_callbacks=[send_to_wechat, send_to_slack],
    notification_mode=NotificationMode.ALL,  # 发送所有消息（成功和失败）
    notification_strategy=SelectionStrategy.SEQUENTIAL,
    
    enable_failover=True,
    verbose=False
)

# ==================== 示例 5: 消息通知（随机选择一个） ====================
print("\n\n" + "=" * 60)
print("示例 5: 消息通知（随机选择一个通知渠道）")
print("=" * 60)

result = generate_image(
    prompt="森林",
    api_configs="your-api-key",
    models="qwen",
    
    notification_callbacks=[send_to_wechat, send_to_email, send_to_slack],
    notification_mode=NotificationMode.ALL,
    notification_strategy=SelectionStrategy.RANDOM,  # 随机选择一个回调
    
    verbose=False
)

# ==================== 示例 6: 完整回调配置 ====================
print("\n\n" + "=" * 60)
print("示例 6: 完整回调配置（图床 + 消息通知）")
print("=" * 60)

result = generate_image(
    prompt="未来城市",
    api_configs=["key1", "key2"],
    models=["flux-majic", "qwen"],
    size="16:9",
    save_path="future_city.jpg",
    
    # 容错配置
    enable_failover=True,
    max_retries=3,
    
    # 图床上传
    image_upload_callbacks=[upload_to_smms, upload_to_custom],
    upload_strategy=SelectionStrategy.SEQUENTIAL,
    upload_on_success=True,
    
    # 消息通知
    notification_callbacks=[send_to_wechat, send_to_email],
    notification_mode=NotificationMode.ALL,
    notification_strategy=SelectionStrategy.SEQUENTIAL,
    
    verbose=True
)

if result:
    print(f"\n🎉 完整流程执行成功！")
    print(f"   本地文件: {save_path if 'save_path' in locals() else '未保存'}")
    print(f"   图床URL: {result['url'] if result['url'] else '未上传'}")
    print(f"   使用模型: {result['model']}")
    print(f"   使用API: {result['api']}")