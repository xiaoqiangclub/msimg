# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# GitHub：https://github.com/xiaoqiangclub
# 邮箱：xiaoqiangclub@hotmail.com
# 创建时间：2025-01-20 10:00:00
# 文件描述：图床上传器独立使用示例（不依赖 generate_image）
# 文件路径：examples/standalone_image_uploader.py

"""
本示例展示如何独立使用 msimg 的图床上传功能
无需调用 generate_image，可以直接上传各种格式的图片
"""

from io import BytesIO
from msimg.image_uploader import (
    create_smms_uploader,
    create_luoguo_uploader,
    create_github_uploader,
)
from PIL import Image
import base64

# ==================== 示例 1: 上传本地图片 ====================
print("=" * 60)
print("📤 示例 1: 上传本地图片")
print("=" * 60)

# 创建上传器
uploader = create_smms_uploader(api_token='your-smms-token')

# 上传本地图片
try:
    url = uploader('/path/to/your/image.jpg')
    print(f"✅ 上传成功: {url}")
except Exception as e:
    print(f"❌ 上传失败: {e}")

# ==================== 示例 2: 上传网络图片 ====================
print("\n" + "=" * 60)
print("📤 示例 2: 上传网络图片")
print("=" * 60)

uploader = create_luoguo_uploader()

# 上传网络图片
try:
    network_url = 'https://picsum.photos/200/300'
    url = uploader(network_url)
    print(f"✅ 上传成功: {url}")
except Exception as e:
    print(f"❌ 上传失败: {e}")

# ==================== 示例 3: 上传 PIL.Image 对象 ====================
print("\n" + "=" * 60)
print("📤 示例 3: 上传 PIL.Image 对象")
print("=" * 60)

# 创建一个简单的图片
img = Image.new('RGB', (200, 200), color='red')

uploader = create_luoguo_uploader()

try:
    url = uploader(img)
    print(f"✅ 上传成功: {url}")
except Exception as e:
    print(f"❌ 上传失败: {e}")

# ==================== 示例 4: 上传 Base64 图片 ====================
print("\n" + "=" * 60)
print("📤 示例 4: 上传 Base64 图片")
print("=" * 60)

# 生成一个 Base64 图片（这里用示例数据）
# 实际使用时替换为真实的 Base64 数据
img = Image.new('RGB', (100, 100), color='blue')
buffer = BytesIO()
img.save(buffer, format='PNG')
img_bytes = buffer.getvalue()
base64_str = base64.b64encode(img_bytes).decode('utf-8')

# 方式 1: data URI 格式
data_uri = f"data:image/png;base64,{base64_str}"

uploader = create_luoguo_uploader()

try:
    url = uploader(data_uri)
    print(f"✅ Data URI 上传成功: {url}")
except Exception as e:
    print(f"❌ 上传失败: {e}")

# 方式 2: 纯 Base64 字符串
try:
    url = uploader(base64_str)
    print(f"✅ Base64 上传成功: {url}")
except Exception as e:
    print(f"❌ 上传失败: {e}")

# ==================== 示例 5: 上传字节流 ====================
print("\n" + "=" * 60)
print("📤 示例 5: 上传字节流")
print("=" * 60)

# 读取文件为字节流
with open('/path/to/your/image.jpg', 'rb') as f:
    image_bytes = f.read()

uploader = create_luoguo_uploader()

try:
    url = uploader(image_bytes)
    print(f"✅ 上传成功: {url}")
except Exception as e:
    print(f"❌ 上传失败: {e}")

# ==================== 示例 6: 批量上传不同格式 ====================
print("\n" + "=" * 60)
print("📤 示例 6: 批量上传不同格式的图片")
print("=" * 60)

uploader = create_luoguo_uploader()

images = [
    '/path/to/local/image1.jpg',           # 本地路径
    'https://picsum.photos/300/200',       # 网络 URL
    Image.new('RGB', (150, 150), 'green'),  # PIL.Image
]

for i, img in enumerate(images, 1):
    try:
        url = uploader(img)
        print(f"✅ 图片 {i} 上传成功: {url}")
    except Exception as e:
        print(f"❌ 图片 {i} 上传失败: {e}")

# ==================== 示例 7: 使用多个图床（故障转移）====================
print("\n" + "=" * 60)
print("📤 示例 7: 多图床故障转移")
print("=" * 60)

# 创建多个上传器
uploaders = [
    create_smms_uploader(api_token='your-token'),
    create_luoguo_uploader(),
    create_github_uploader(token='github-token', repo='user/repo'),
]

img = Image.new('RGB', (200, 200), color='yellow')

# 尝试多个图床
for i, uploader in enumerate(uploaders, 1):
    try:
        url = uploader(img)
        print(f"✅ 使用图床 {i} 上传成功: {url}")
        break  # 成功后退出
    except Exception as e:
        print(f"⚠️  图床 {i} 上传失败: {e}")
        if i < len(uploaders):
            print(f"🔄 尝试下一个图床...")
        else:
            print(f"❌ 所有图床上传失败")

# ==================== 示例 8: 集成到自己的项目中 ====================
print("\n" + "=" * 60)
print("📤 示例 8: 集成到自己的项目")
print("=" * 60)


def upload_image_to_cloud(image, retries=3):
    """
    将图片上传到云端（带重试机制）
    
    :param image: 图片（支持多种格式）
    :param retries: 重试次数
    :return: 图片 URL
    """
    uploader = create_luoguo_uploader()

    for attempt in range(retries):
        try:
            url = uploader(image)
            return url
        except Exception as e:
            if attempt < retries - 1:
                print(f"⚠️  第 {attempt + 1} 次上传失败，重试中...")
            else:
                print(f"❌ 上传失败（已重试 {retries} 次）: {e}")
                raise

    return None


# 使用
try:
    img = Image.new('RGB', (100, 100), color='purple')
    url = upload_image_to_cloud(img)
    print(f"✅ 集成上传成功: {url}")
except Exception as e:
    print(f"❌ 集成上传失败: {e}")

print("\n" + "=" * 60)
print("✅ 所有示例演示完毕！")
print("=" * 60)
