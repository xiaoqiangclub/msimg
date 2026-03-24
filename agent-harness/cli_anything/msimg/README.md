# cli-anything-msimg

MSIMG CLI - 魔塔社区文生图API命令行工具

## 项目简介

这是一个为 MSIMG 库构建的命令行界面工具，允许用户通过命令行生成图像、管理配置和上传到图床。MSIMG 是一个优雅的魔塔社区文生图 API 调用库，支持多模型、多 API、容错重试、内置8种图床等高级特性。

## 功能特点

- 🖼️ **图片生成** - 通过命令行生成AI图片
- ⚙️ **配置管理** - 管理API密钥和其他配置
- 📤 **图床上传** - 支持多种图床服务
- 🤖 **多模型支持** - 支持qwen、flux-majic等多种模型
- 📐 **多种尺寸** - 支持多种预设图片尺寸
- 🔄 **容错重试** - 自动处理API错误和重试
- 📄 **JSON输出** - 支持机器可读的JSON格式输出

## 安装

```bash
pip install cli-anything-msimg
```

或者从源码安装：

```bash  # 进入项目根目录
pip install -e .
```

## 使用方法

### 生成图片

```bash
# 基本用法
cli-anything-msimg generate --prompt "一只金色的猫" --api-key YOUR_API_KEY

# 指定模型和尺寸
cli-anything-msimg generate -p "赛博朋克城市夜景" -k YOUR_API_KEY -m flux-majic -s 16:9

# 保存到指定路径
cli-anything-msimg generate -p "美丽的风景" -k YOUR_API_KEY -o ./output/landscape.jpg

# 启用容错和详细日志
cli-anything-msimg generate -p "抽象艺术" -k YOUR_API_KEY --enable-failover --verbose
```

### 查看支持的模型

```bash
# 查看所有预设模型
cli-anything-msimg models

# 查看特定模型
cli-anything-msimg models -m qwen
```

### 查看支持的尺寸

```bash
# 查看所有预设尺寸
cli-anything-msimg sizes

# 查看特定尺寸
cli-anything-msimg sizes -s 16:9
```

## 命令详情

### generate 命令

生成图片的主要命令，支持多种参数：

- `--prompt, -p` (必需): 图片生成的提示词
- `--api-key, -k` (必需): API密钥
- `--model, -m`: 使用的模型 (默认: qwen)
- `--size, -s`: 图片尺寸 (默认: 16:9)
- `--save-path, -o`: 保存路径
- `--enable-failover`: 启用容错
- `--max-retries`: 最大重试次数 (默认: 3)
- `--verbose`: 显示详细日志
- `--json`: JSON格式输出

### models 命令

查看支持的模型列表，可指定特定模型查看详细信息。

### sizes 命令

查看支持的图片尺寸列表，可指定特定尺寸查看详细信息。

## 预设模型

- `qwen`: 通义万相 - 阿里巴巴出品，综合能力强 (Qwen/Qwen-Image)
- `flux-majic`: FLUX 魔法模型 - 艺术风格出色 (MAILAND/majicflus_v1)
- `flux-muse`: FLUX Muse 版本 - 创意效果好 (MusePublic/489_ckpt_FLUX_1)
- `flux-xiaohongshu`: FLUX 小红书风格 - 适合社交媒体 (yiwanji/FLUX_xiao_hong_shu_ji_zhi_zhen_shi_V2)
- `sdxl-muse`: Stable Diffusion XL - 经典模型 (MusePublic/42_ckpt_SD_XL)

## 预设尺寸

- `1:1`: 1328x1328 - 社交媒体头像、方形图片
- `16:9`: 1664x928 - 横向壁纸、演示文稿
- `9:16`: 928x1664 - 手机壁纸、竖屏视频封面
- `4:3`: 1472x1140 - 传统照片、iPad 壁纸
- `3:4`: 1140x1472 - 竖向海报
- `3:2`: 1584x1056 - 相机标准比例
- `2:3`: 1056x1584 - 书籍封面、竖向印刷品

## 获取API密钥

1. 访问 [魔塔社区官网](https://www.modelscope.cn/)
2. 注册并登录账号
3. 访问 [API密钥管理页面](https://www.modelscope.cn/my/myaccesstoken)
4. 点击“新建访问令牌”生成API密钥

注意：魔塔社区提供每日2000次的免费调用额度。

## JSON输出格式

使用 `--json` 参数可以获得机器可读的JSON输出格式：

```json
{
  "success": true,
  "image_size": [1664, 928],
  "model_used": "qwen",
  "api_used": "YOUR_API_KEY",
  "saved_to": "./output/image.jpg"
}
```

## 开发

本工具遵循标准的Python包结构，主要组件位于 `cli_anything/msimg/core/` 目录下：

- `msimg_cli.py`: 主CLI入口点
- `project.py`: 项目管理
- `session.py`: 会话管理
- `generation.py`: 图片生成
- `upload.py`: 图床上传
- `config.py`: 配置管理
- `export.py`: 输出处理

## 许可证

本项目采用 MIT 许可证。