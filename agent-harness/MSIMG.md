# MSIMG CLI 工具开发标准操作程序 (SOP)

## 项目概述
MSIMG 是一个优雅的魔塔社区文生图 API 调用库，支持多模型、多 API、容错重试、内置8种图床等高级特性。本项目旨在为其构建一个功能完备的 CLI 工具。

## CLI 架构设计

### 命令分组
- `generate`: 图片生成相关命令
- `config`: 配置管理命令
- `upload`: 图床上传命令
- `model`: 模型管理命令
- `status`: 任务状态查询命令

### 核心功能模块
1. **项目管理** (`project.py`)
2. **会话管理** (`session.py`)
3. **图片生成** (`generation.py`)
4. **图床上传** (`upload.py`)
5. **配置管理** (`config.py`)
6. **输出处理** (`export.py`)

### 输出格式
- 支持普通文本输出
- 支持 JSON 格式输出 (`--json`)
- 支持详细日志输出 (`--verbose`)

## 开发标准
- 使用 Click 构建 CLI 框架
- 支持单次命令和 REPL 模式
- 遵循 Python 最佳实践
- 包含完整的错误处理机制
- 支持配置文件管理

## 命令示例
```
# 生成图片
cli-anything-msimg generate --prompt "一只金色的猫" --model qwen

# 配置 API Key
cli-anything-msimg config set api_key your-api-key

# 上传图片到图床
cli-anything-msimg upload --image path/to/image.jpg
```