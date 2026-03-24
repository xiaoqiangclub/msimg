"""
MSIMG CLI - 魔塔社区文生图API命令行工具

此模块实现了MSIMG库的命令行接口，支持图片生成、配置管理、图床上传等功能。
"""

import click
import sys
import os
from typing import Optional
import json

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from msimg import generate_image, APIConfig, SelectionStrategy, NotificationMode
from msimg.constants import MODEL_PRESETS, SIZE_PRESETS


@click.group()
@click.version_option(version='0.0.1')
def cli():
    """MSIMG CLI - 魔塔社区文生图API命令行工具"""
    pass


@cli.command()
@click.option('--prompt', '-p', required=True, help='图片生成的提示词')
@click.option('--api-key', '-k', required=True, help='API密钥')
@click.option('--model', '-m', default='qwen', help='使用的模型，默认为qwen')
@click.option('--size', '-s', default='16:9', help='图片尺寸，默认为16:9')
@click.option('--save-path', '-o', help='保存路径')
@click.option('--enable-failover', is_flag=True, help='启用容错')
@click.option('--max-retries', default=3, help='最大重试次数')
@click.option('--verbose', is_flag=True, help='显示详细日志')
@click.option('--json', 'json_output', is_flag=True, help='JSON格式输出')
def generate(prompt: str, api_key: str, model: str, size: str, save_path: str,
           enable_failover: bool, max_retries: int, verbose: bool, json_output: bool):
    """生成图片"""
    try:
        result = generate_image(
            prompt=prompt,
            api_configs=api_key,
            models=model,
            size=size,
            save_path=save_path,
            enable_failover=enable_failover,
            max_retries=max_retries,
            verbose=verbose
        )

        if json_output:
            if result:
                output = {
                    'success': True,
                    'image_size': result['size'],
                    'model_used': result['model'],
                    'api_used': result['api'],
                    'saved_to': save_path
                }
            else:
                output = {'success': False, 'error': '图片生成失败'}
            click.echo(json.dumps(output))
        else:
            if result:
                click.echo("✅ 图片生成成功！")
                click.echo(f"📁 尺寸: {result['size']}")
                click.echo(f"🤖 模型: {result['model']}")
                if save_path:
                    click.echo(f"💾 保存到: {save_path}")
            else:
                click.echo("❌ 图片生成失败")

    except Exception as e:
        if json_output:
            click.echo(json.dumps({'success': False, 'error': str(e)}))
        else:
            click.echo(f"❌ 错误: {str(e)}")


@cli.command()
@click.option('--model', '-m', help='指定模型名称，不指定则显示所有预设模型')
def models(model: str):
    """查看支持的模型"""
    if model:
        if model in MODEL_PRESETS:
            click.echo(f"{model}: {MODEL_PRESETS[model]}")
        else:
            click.echo(f"未找到模型: {model}")
            click.echo("支持的预设模型:")
            for preset, full_id in MODEL_PRESETS.items():
                click.echo(f"  {preset}: {full_id}")
    else:
        click.echo("支持的预设模型:")
        for preset, full_id in MODEL_PRESETS.items():
            click.echo(f"  {preset}: {full_id}")


@cli.command()
@click.option('--size', '-s', help='指定尺寸名称，不指定则显示所有预设尺寸')
def sizes(size: str):
    """查看支持的图片尺寸"""
    if size:
        if size in SIZE_PRESETS:
            click.echo(f"{size}: {SIZE_PRESETS[size]}")
        else:
            click.echo(f"未找到尺寸: {size}")
            click.echo("支持的预设尺寸:")
            for preset, dimension in SIZE_PRESETS.items():
                click.echo(f"  {preset}: {dimension}")
    else:
        click.echo("支持的预设尺寸:")
        for preset, dimension in SIZE_PRESETS.items():
            click.echo(f"  {preset}: {dimension}")


@cli.group()
def config():
    """配置管理命令"""
    pass


@config.command()
@click.option('--key', '-k', required=True, help='配置项名称')
@click.option('--value', '-v', required=True, help='配置项值')
def set(key: str, value: str):
    """设置配置项"""
    from cli_anything.msimg.core.config import ConfigManager
    config_manager = ConfigManager()

    # 尝试将值转换为适当的数据类型
    if value.lower() in ('true', 'false'):
        value = value.lower() == 'true'
    elif value.isdigit():
        value = int(value)
    elif value.replace('.', '').isdigit():
        value = float(value)

    success = config_manager.set(key, value)
    if success:
        click.echo(f"✅ 配置项 {key} 已设置为 {value}")
    else:
        click.echo(f"❌ 配置项 {key} 设置失败")


@config.command()
@click.option('--key', '-k', required=True, help='配置项名称')
def get(key: str):
    """获取配置项"""
    from cli_anything.msimg.core.config import ConfigManager
    config_manager = ConfigManager()
    value = config_manager.get(key)
    click.echo(f"{key}: {value}")


@config.command()
def list():
    """列出所有配置项"""
    from cli_anything.msimg.core.config import ConfigManager
    config_manager = ConfigManager()
    config = config_manager.load_config()

    def print_dict(d, prefix=""):
        for k, v in d.items():
            if isinstance(v, dict):
                click.echo(f"{prefix}{k}:")
                print_dict(v, prefix + "  ")
            else:
                click.echo(f"{prefix}{k}: {v}")

    print_dict(config)


@config.command()
def reset():
    """重置为默认配置"""
    from cli_anything.msimg.core.config import ConfigManager
    config_manager = ConfigManager()
    success = config_manager.reset()
    if success:
        click.echo("✅ 配置已重置为默认值")
    else:
        click.echo("❌ 配置重置失败")


if __name__ == '__main__':
    cli()