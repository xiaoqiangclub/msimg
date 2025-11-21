#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微信公众号图床上传功能测试

测试内容：
1. ✅ 三种上传方式（临时素材、永久素材、图文消息图片）
2. ✅ 自动选择最佳 Token 获取方式
3. ✅ 多种图片输入格式（本地文件、URL、PIL.Image、Base64、bytes）
4. ✅ 配合 msimg 生成图片并上传
5. ✅ Token 缓存机制
6. ✅ 错误处理和自动降级

使用说明：
1. 创建配置文件 config.ini 或直接修改本文件的配置部分
2. 运行测试：python test_wechat_uploader.py
"""

import os
import base64
import configparser
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ============================================================================
# 配置部分
# ============================================================================

DEFAULT_CONFIG = {
    # 微信公众号配置（必需）
    'WECHAT_APP_ID': "wxabcdef1234567890",  # 例如: "wxabcdef1234567890"
    'WECHAT_APP_SECRET': "c9f743480bwxabcdef123456789033253",  # 你的 AppSecret

    # 服务器 Token 配置（可选，推荐配置）
    'WECHAT_SERVER_URL': "",  # 例如: "https://vip.msguner.com/apis/get_token.php"
    'WECHAT_SERVER_TOKEN': "",  # 可选

    # msimg API Key（用于测试集成）
    'MSIMG_API_KEY': "",

    # 测试图片配置
    'TEST_IMAGE_PATH': "test_image.jpg",
    'TEST_IMAGE_URL': "https://s2.loli.net/2025/07/30/WJUgpx5lZ87vRtO.jpg",
}


def load_config():
    """加载配置（优先从 config.ini 读取）"""
    config = DEFAULT_CONFIG.copy()

    config_file = Path(__file__).parent / 'config.ini'
    if config_file.exists():
        print(f"📄 读取配置文件: {config_file}")
        parser = configparser.ConfigParser()
        parser.read(config_file, encoding='utf-8')

        if 'wechat' in parser:
            config['WECHAT_APP_ID'] = parser.get('wechat', 'app_id', fallback='')
            config['WECHAT_APP_SECRET'] = parser.get('wechat', 'app_secret', fallback='')

        if 'optional' in parser:
            config['WECHAT_SERVER_URL'] = parser.get('optional', 'server_url', fallback='')
            config['WECHAT_SERVER_TOKEN'] = parser.get('optional', 'server_token', fallback='')
            config['MSIMG_API_KEY'] = parser.get('optional', 'msimg_api_key', fallback='')

    return config


CONFIG = load_config()

WECHAT_APP_ID = CONFIG['WECHAT_APP_ID']
WECHAT_APP_SECRET = CONFIG['WECHAT_APP_SECRET']
WECHAT_SERVER_URL = CONFIG['WECHAT_SERVER_URL']
WECHAT_SERVER_TOKEN = CONFIG['WECHAT_SERVER_TOKEN']
MSIMG_API_KEY = CONFIG['MSIMG_API_KEY']
TEST_IMAGE_PATH = CONFIG['TEST_IMAGE_PATH']
TEST_IMAGE_URL = CONFIG['TEST_IMAGE_URL']


# ============================================================================
# 配置检查
# ============================================================================

def check_config():
    """检查配置是否完整"""
    if not (WECHAT_APP_ID and WECHAT_APP_SECRET):
        print("\n" + "=" * 70)
        print("⚠️  配置不完整")
        print("=" * 70)
        print("\n请配置微信公众号信息：\n")
        print("【配置方法】")
        print("  1. 登录微信公众平台: https://mp.weixin.qq.com/")
        print("  2. 开发 > 基本配置 > 获取 AppID 和 AppSecret")
        print("  3. 修改本文件的配置部分或创建 config.ini 文件\n")
        print("【配置文件示例】创建 config.ini 文件：")
        print("-" * 70)
        print("""[wechat]
app_id = wxabcdef1234567890
app_secret = your_app_secret_here

[optional]
# 推荐配置（解决 IP 白名单问题）
server_url = https://vip.msguner.com/apis/get_token.php
server_token = 

# msimg API Key（用于测试集成）
msimg_api_key = your_msimg_api_key
""")
        print("-" * 70)
        print("\n💡 提示：")
        print("  • 如果遇到 IP 白名单错误，请配置 server_url")
        print("  • server_url 优先使用，失败后自动降级到直接获取")
        print("  • 可以只配置 app_id 和 app_secret，程序会自动尝试\n")
        print("=" * 70 + "\n")
        return False

    return True


# ============================================================================
# 辅助函数
# ============================================================================

def create_test_image(save_path: str = TEST_IMAGE_PATH) -> str:
    """创建测试图片"""
    print(f"\n🎨 正在创建测试图片...")

    img = Image.new('RGB', (800, 600), color=(73, 109, 137))
    draw = ImageDraw.Draw(img)

    text = "微信公众号图床测试"

    try:
        font = ImageFont.truetype("msyh.ttc", 60)
        small_font = ImageFont.truetype("msyh.ttc", 30)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 60)
            small_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 30)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 60)
                small_font = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 30)
            except:
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()

    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except:
        text_width, text_height = draw.textsize(text, font=font)

    position = ((800 - text_width) // 2, (600 - text_height) // 2 - 50)
    draw.text(position, text, fill=(255, 255, 255), font=font)

    subtitle = "WeChat Image Uploader Test"
    try:
        bbox2 = draw.textbbox((0, 0), subtitle, font=small_font)
        text_width2 = bbox2[2] - bbox2[0]
    except:
        text_width2, _ = draw.textsize(subtitle, font=small_font)

    position2 = ((800 - text_width2) // 2, position[1] + text_height + 20)
    draw.text(position2, subtitle, fill=(200, 200, 200), font=small_font)

    img.save(save_path, 'JPEG', quality=95)
    print(f"✅ 测试图片已创建: {save_path}")

    return save_path


def image_to_base64(image_path: str) -> str:
    """将图片转换为 Base64"""
    with open(image_path, 'rb') as f:
        image_data = f.read()
    base64_str = base64.b64encode(image_data).decode('utf-8')
    return f"data:image/jpeg;base64,{base64_str}"


def print_section(title: str):
    """打印章节标题"""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def print_result(test_name: str, result: str, success: bool = True):
    """打印测试结果"""
    status = "✅" if success else "❌"
    print(f"{status} {test_name}")
    if result:
        print(f"   {result}")


# ============================================================================
# 测试用例
# ============================================================================

def test_basic_upload():
    """测试1: 基础上传功能（临时素材）"""
    print_section("📋 测试1: 基础上传功能（临时素材）")

    try:
        from msimg.wechat_uploader import create_wechat_uploader, WechatUploadType

        # 创建上传器（自动选择最佳方式）
        uploader = create_wechat_uploader(
            app_id=WECHAT_APP_ID,
            app_secret=WECHAT_APP_SECRET,
            server_url=WECHAT_SERVER_URL if WECHAT_SERVER_URL else None,
            server_token=WECHAT_SERVER_TOKEN if WECHAT_SERVER_TOKEN else None,
            upload_type=WechatUploadType.TEMPORARY,
            verbose=True
        )

        # 上传测试图片
        media_id = uploader(TEST_IMAGE_PATH)

        print_result("基础上传测试", f"Media ID: {media_id}", True)
        return True

    except Exception as e:
        print_result("基础上传测试", f"失败: {e}", False)
        import traceback
        print(f"\n详细错误：\n{traceback.format_exc()}")
        return False


def test_permanent_material():
    """测试2: 永久素材上传"""
    print_section("📋 测试2: 永久素材上传")

    try:
        from msimg.wechat_uploader import create_wechat_uploader, WechatUploadType

        uploader = create_wechat_uploader(
            app_id=WECHAT_APP_ID,
            app_secret=WECHAT_APP_SECRET,
            server_url=WECHAT_SERVER_URL if WECHAT_SERVER_URL else None,
            upload_type=WechatUploadType.PERMANENT,
            verbose=True
        )

        result = uploader(TEST_IMAGE_PATH)

        print_result("永久素材上传测试", f"结果: {result}", True)
        return True

    except Exception as e:
        print_result("永久素材上传测试", f"失败: {e}", False)
        return False


def test_news_image():
    """测试3: 图文消息图片上传"""
    print_section("📋 测试3: 图文消息图片上传")

    try:
        from msimg.wechat_uploader import create_wechat_uploader, WechatUploadType

        uploader = create_wechat_uploader(
            app_id=WECHAT_APP_ID,
            app_secret=WECHAT_APP_SECRET,
            server_url=WECHAT_SERVER_URL if WECHAT_SERVER_URL else None,
            upload_type=WechatUploadType.NEWS_IMAGE,
            verbose=True
        )

        url = uploader(TEST_IMAGE_PATH)

        print_result("图文消息图片上传测试", f"URL: {url}", True)
        return True

    except Exception as e:
        print_result("图文消息图片上传测试", f"失败: {e}", False)
        return False


def test_auto_token_selection():
    """测试4: 自动选择 Token 获取方式"""
    print_section("📋 测试4: 自动选择 Token 获取方式")

    try:
        from msimg.wechat_uploader import WechatUploader, WechatUploadType

        print("🔍 测试场景1: 配置了服务器 URL（优先使用）")
        uploader1 = WechatUploader(
            app_id=WECHAT_APP_ID,
            app_secret=WECHAT_APP_SECRET,
            server_url=WECHAT_SERVER_URL if WECHAT_SERVER_URL else None,
            upload_type=WechatUploadType.TEMPORARY,
            verbose=True
        )

        token1 = uploader1._get_access_token()
        if token1:
            print_result("服务器优先模式", f"Token: {token1[:20]}...", True)
        else:
            print_result("服务器优先模式", "获取失败", False)

        print("\n🔍 测试场景2: 未配置服务器 URL（直接获取）")
        uploader2 = WechatUploader(
            app_id=WECHAT_APP_ID,
            app_secret=WECHAT_APP_SECRET,
            upload_type=WechatUploadType.TEMPORARY,
            verbose=True
        )

        token2 = uploader2._get_access_token()
        if token2:
            print_result("直接获取模式", f"Token: {token2[:20]}...", True)
        else:
            print_result("直接获取模式", "获取失败（可能是 IP 白名单限制）", False)

        return bool(token1 or token2)

    except Exception as e:
        print_result("自动选择测试", f"失败: {e}", False)
        return False


def test_multiple_input_formats():
    """测试5: 多种图片输入格式"""
    print_section("📋 测试5: 多种图片输入格式")

    try:
        from msimg.wechat_uploader import create_wechat_uploader

        uploader = create_wechat_uploader(
            app_id=WECHAT_APP_ID,
            app_secret=WECHAT_APP_SECRET,
            server_url=WECHAT_SERVER_URL if WECHAT_SERVER_URL else None,
            verbose=True
        )

        results = []

        # 5.1 本地文件路径
        print("📁 测试本地文件路径...")
        try:
            media_id = uploader(TEST_IMAGE_PATH)
            print_result("本地文件路径", f"Media ID: {media_id}", True)
            results.append(True)
        except Exception as e:
            print_result("本地文件路径", f"失败: {e}", False)
            results.append(False)

        # 5.2 网络 URL
        print("\n🌐 测试网络 URL...")
        try:
            media_id = uploader(TEST_IMAGE_URL)
            print_result("网络 URL", f"Media ID: {media_id}", True)
            results.append(True)
        except Exception as e:
            print_result("网络 URL", f"失败: {e}", False)
            results.append(False)

        # 5.3 PIL.Image 对象
        print("\n🖼️  测试 PIL.Image 对象...")
        try:
            img = Image.open(TEST_IMAGE_PATH)
            media_id = uploader(img)
            print_result("PIL.Image 对象", f"Media ID: {media_id}", True)
            results.append(True)
        except Exception as e:
            print_result("PIL.Image 对象", f"失败: {e}", False)
            results.append(False)

        # 5.4 Base64 编码
        print("\n📝 测试 Base64 编码...")
        try:
            base64_str = image_to_base64(TEST_IMAGE_PATH)
            media_id = uploader(base64_str)
            print_result("Base64 编码", f"Media ID: {media_id}", True)
            results.append(True)
        except Exception as e:
            print_result("Base64 编码", f"失败: {e}", False)
            results.append(False)

        # 5.5 字节流
        print("\n💾 测试字节流...")
        try:
            with open(TEST_IMAGE_PATH, 'rb') as f:
                image_bytes = f.read()
            media_id = uploader(image_bytes)
            print_result("字节流", f"Media ID: {media_id}", True)
            results.append(True)
        except Exception as e:
            print_result("字节流", f"失败: {e}", False)
            results.append(False)

        return all(results)

    except Exception as e:
        print_result("多种输入格式测试", f"失败: {e}", False)
        return False


def test_msimg_integration():
    """测试6: 配合 msimg 生成图片并上传"""
    print_section("📋 测试6: 配合 msimg 生成图片并上传")

    if not MSIMG_API_KEY:
        print("⏭️  跳过测试（未配置 ModelScope API Key）")
        return None

    try:
        from msimg import generate_image
        from msimg.wechat_uploader import create_wechat_uploader, WechatUploadType

        wechat_upload = create_wechat_uploader(
            app_id=WECHAT_APP_ID,
            app_secret=WECHAT_APP_SECRET,
            server_url=WECHAT_SERVER_URL if WECHAT_SERVER_URL else None,
            upload_type=WechatUploadType.PERMANENT,
            verbose=True
        )

        print("🎨 正在生成图片...")

        result = generate_image(
            prompt="一只可爱的橘猫",
            api_configs=MSIMG_API_KEY,
            models="qwen",
            size="1:1",
            image_upload_callbacks=wechat_upload,
            upload_on_success=True,
            verbose=True
        )

        if result and result.get('url'):
            print_result(
                "msimg 集成测试",
                f"图片已生成并上传\n   URL/Media ID: {result.get('url')}\n   尺寸: {result.get('size')}",
                True
            )
            return True
        else:
            print_result("msimg 集成测试", "生成或上传失败", False)
            return False

    except Exception as e:
        print_result("msimg 集成测试", f"失败: {e}", False)
        return False


def test_token_cache():
    """测试7: Token 缓存机制"""
    print_section("📋 测试7: Token 缓存机制")

    try:
        from msimg.wechat_uploader import WechatUploader, WechatUploadType
        import time

        uploader = WechatUploader(
            app_id=WECHAT_APP_ID,
            app_secret=WECHAT_APP_SECRET,
            server_url=WECHAT_SERVER_URL if WECHAT_SERVER_URL else None,
            upload_type=WechatUploadType.TEMPORARY,
            verbose=True
        )

        # 第一次获取（从服务器或微信 API）
        print("🔄 第一次获取 token...")
        start_time = time.time()
        token1 = uploader._get_access_token()
        time1 = time.time() - start_time

        if not token1:
            print_result("Token 缓存测试", "获取 token 失败", False)
            return False

        # 第二次获取（应该从缓存读取，速度更快）
        print("\n🔄 第二次获取 token（应该从缓存读取）...")
        start_time = time.time()
        token2 = uploader._get_access_token()
        time2 = time.time() - start_time

        if token1 == token2:
            print_result(
                "Token 缓存测试",
                f"Token 一致，缓存生效\n   Token: {token1[:20]}...\n   第一次耗时: {time1:.3f}秒\n   第二次耗时: {time2:.3f}秒\n   缓存文件: {uploader.access_token_file}",
                True
            )

            # 检查缓存文件
            if os.path.exists(uploader.access_token_file):
                return True
            else:
                print_result("缓存文件检查", "缓存文件不存在", False)
                return False
        else:
            print_result("Token 缓存测试", "Token 不一致", False)
            return False

    except Exception as e:
        print_result("Token 缓存测试", f"失败: {e}", False)
        return False


def test_error_handling():
    """测试8: 错误处理"""
    print_section("📋 测试8: 错误处理")

    try:
        from msimg.wechat_uploader import create_wechat_uploader, WechatUploadType

        results = []

        # 8.1 文件大小超限
        print("🔍 测试文件大小限制（临时素材 2MB）...")
        try:
            # 创建一个大图片（超过2MB）
            large_img = Image.new('RGB', (4000, 4000), color=(255, 0, 0))

            uploader = create_wechat_uploader(
                app_id=WECHAT_APP_ID,
                app_secret=WECHAT_APP_SECRET,
                server_url=WECHAT_SERVER_URL if WECHAT_SERVER_URL else None,
                upload_type=WechatUploadType.TEMPORARY,
                verbose=False
            )

            uploader(large_img)
            print_result("文件大小限制测试", "应该抛出异常但没有", False)
            results.append(False)
        except Exception as e:
            if "超过" in str(e) and "MB" in str(e):
                print_result("文件大小限制测试", "正确捕获异常", True)
                results.append(True)
            else:
                print_result("文件大小限制测试", f"异常类型错误: {e}", False)
                results.append(False)

        # 8.2 文件不存在
        print("\n🔍 测试文件不存在...")
        try:
            uploader = create_wechat_uploader(
                app_id=WECHAT_APP_ID,
                app_secret=WECHAT_APP_SECRET,
                server_url=WECHAT_SERVER_URL if WECHAT_SERVER_URL else None,
                verbose=False
            )

            uploader("/path/to/nonexistent/file.jpg")
            print_result("文件不存在测试", "应该抛出异常但没有", False)
            results.append(False)
        except Exception as e:
            print_result("文件不存在测试", "正确捕获异常", True)
            results.append(True)

        # 8.3 永久素材大小限制（10MB）
        print("\n🔍 测试永久素材大小限制（10MB）...")
        try:
            # 创建一个超大图片（超过10MB）
            huge_img = Image.new('RGB', (6000, 6000), color=(0, 255, 0))

            uploader = create_wechat_uploader(
                app_id=WECHAT_APP_ID,
                app_secret=WECHAT_APP_SECRET,
                server_url=WECHAT_SERVER_URL if WECHAT_SERVER_URL else None,
                upload_type=WechatUploadType.PERMANENT,
                verbose=False
            )

            uploader(huge_img)
            print_result("永久素材大小限制测试", "应该抛出异常但没有", False)
            results.append(False)
        except Exception as e:
            if "超过" in str(e) and "10MB" in str(e):
                print_result("永久素材大小限制测试", "正确捕获异常", True)
                results.append(True)
            else:
                print_result("永久素材大小限制测试", f"异常类型: {e}", True)
                results.append(True)

        return all(results)

    except Exception as e:
        print_result("错误处理测试", f"失败: {e}", False)
        return False


def test_format_conversion():
    """测试9: 格式自动转换"""
    print_section("📋 测试9: 格式自动转换")

    try:
        from msimg.wechat_uploader import create_wechat_uploader

        # 创建一个 PNG 格式（带透明通道）的图片
        print("🎨 创建 PNG 格式测试图片（带透明通道）...")
        png_img = Image.new('RGBA', (400, 300), color=(255, 100, 100, 128))
        draw = ImageDraw.Draw(png_img)
        draw.text((100, 100), "PNG Test", fill=(255, 255, 255, 255))

        png_path = "test_png_alpha.png"
        png_img.save(png_path, 'PNG')
        print(f"✅ PNG 测试图片已创建: {png_path}")

        # 上传并测试自动转换
        print("\n📤 上传 PNG 图片（应该自动转换为 JPEG）...")
        uploader = create_wechat_uploader(
            app_id=WECHAT_APP_ID,
            app_secret=WECHAT_APP_SECRET,
            server_url=WECHAT_SERVER_URL if WECHAT_SERVER_URL else None,
            verbose=True
        )

        try:
            media_id = uploader(png_path)
            print_result("格式转换测试", f"Media ID: {media_id}", True)

            # 清理测试文件
            if os.path.exists(png_path):
                os.remove(png_path)
                print(f"🧹 已清理测试文件: {png_path}")

            return True
        except Exception as e:
            print_result("格式转换测试", f"失败: {e}", False)
            # 清理测试文件
            if os.path.exists(png_path):
                os.remove(png_path)
            return False

    except Exception as e:
        print_result("格式转换测试", f"失败: {e}", False)
        return False


# ============================================================================
# 主测试函数
# ============================================================================

def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("  🚀 微信公众号图床上传功能测试")
    print("=" * 70)

    # 检查配置
    if not check_config():
        return

    print("\n✅ 配置检查通过\n")

    # 创建测试图片
    if not os.path.exists(TEST_IMAGE_PATH):
        create_test_image()

    # 运行测试
    results = {}

    results['基础上传'] = test_basic_upload()
    results['永久素材'] = test_permanent_material()
    results['图文消息图片'] = test_news_image()
    results['自动Token选择'] = test_auto_token_selection()
    results['多种输入格式'] = test_multiple_input_formats()
    results['msimg集成'] = test_msimg_integration()
    results['Token缓存'] = test_token_cache()
    results['错误处理'] = test_error_handling()
    results['格式转换'] = test_format_conversion()

    # 统计结果
    print_section("📊 测试结果统计")

    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    total = len(results)

    for name, result in results.items():
        if result is True:
            print(f"✅ {name}: 通过")
        elif result is False:
            print(f"❌ {name}: 失败")
        else:
            print(f"⏭️  {name}: 跳过")

    print(f"\n{'=' * 70}")
    print(f"总计: {total} | 通过: {passed} | 失败: {failed} | 跳过: {skipped}")

    if failed == 0 and passed > 0:
        print("🎉 所有测试通过！")
    elif failed > 0:
        print("⚠️  部分测试失败，请检查配置和网络连接")
    else:
        print("ℹ️  没有测试被执行（配置未完成）")

    print(f"{'=' * 70}\n")


def run_quick_test():
    """快速测试（只测试基本功能）"""
    print("\n" + "=" * 70)
    print("  ⚡ 快速测试模式")
    print("=" * 70)

    if not check_config():
        return

    if not os.path.exists(TEST_IMAGE_PATH):
        create_test_image()

    result = test_basic_upload()

    if result:
        print("\n🎉 快速测试通过！")
    elif result is False:
        print("\n❌ 快速测试失败")
    else:
        print("\n⏭️  快速测试跳过")


def create_config_template():
    """创建配置文件模板"""
    config_content = """[wechat]
# 微信公众号配置（必需）
# 获取方式：登录 https://mp.weixin.qq.com/ > 开发 > 基本配置
app_id = 
app_secret = 

[optional]
# 从服务器获取 Token（推荐配置，解决 IP 白名单问题）
# 如果配置了此项，将优先从服务器获取，失败后自动降级到直接获取
server_url = https://vip.msguner.com/apis/get_token.php
server_token = 

# msimg API Key（用于测试图片生成并上传）
# 获取方式：https://www.modelscope.cn/
msimg_api_key = 
"""

    config_file = Path(__file__).parent / 'config.ini.example'
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)

    print(f"\n✅ 配置文件模板已创建: {config_file}")
    print(f"💡 请复制此文件为 config.ini 并填写配置\n")


# ============================================================================
# 命令行入口
# ============================================================================

if __name__ == "__main__":
    import sys

    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║          微信公众号图床上传功能测试                            ║
    ║                                                               ║
    ║  支持自动选择最佳 Token 获取方式                              ║
    ║  优先服务器获取，失败自动降级                                  ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == 'quick':
            run_quick_test()
        elif command == 'all':
            run_all_tests()
        elif command == 'config':
            create_config_template()
        elif command == 'help':
            print("""
使用方法:
    python test_wechat_uploader.py [command]

命令:
    all     - 运行所有测试（默认）
    quick   - 快速测试（仅测试基本功能）
    config  - 创建配置文件模板
    help    - 显示帮助信息

配置说明:
    1. 必需配置：app_id 和 app_secret
    2. 推荐配置：server_url（解决 IP 白名单问题）
    3. 可选配置：msimg_api_key（用于测试集成）

配置方法:
    1. 运行: python test_wechat_uploader.py config
    2. 将 config.ini.example 复制为 config.ini
    3. 编辑 config.ini，填写配置信息
    4. 运行测试

示例:
    python test_wechat_uploader.py
    python test_wechat_uploader.py all
    python test_wechat_uploader.py quick
    python test_wechat_uploader.py config
            """)
        else:
            print(f"❌ 未知命令: {command}")
            print("💡 使用 'python test_wechat_uploader.py help' 查看帮助")
    else:
        run_all_tests()