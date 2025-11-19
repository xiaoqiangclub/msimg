# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# GitHub：https://github.com/xiaoqiangclub
# 邮箱：xiaoqiangclub@hotmail.com
# 创建时间：2025-01-20 10:00
# 文件描述：单元测试
# 文件路径：tests/test_generator.py

import pytest
from msimg import (
    generate_image,
    APIConfig,
    SelectionStrategy,
    NotificationMode,
    ValidationError,
)
from msimg.generator import _parse_api_configs, _parse_models


class TestParseAPIConfigs:
    """测试 API 配置解析"""
    
    def test_parse_single_string(self):
        """测试单个字符串"""
        result = _parse_api_configs("test-key")
        assert len(result) == 1
        assert result[0].api_key == "test-key"
    
    def test_parse_string_list(self):
        """测试字符串列表"""
        result = _parse_api_configs(["key1", "key2"])
        assert len(result) == 2
        assert result[0].api_key == "key1"
        assert result[1].api_key == "key2"
    
    def test_parse_api_config(self):
        """测试 APIConfig 对象"""
        config = APIConfig(api_key="test-key", name="Test")
        result = _parse_api_configs(config)
        assert len(result) == 1
        assert result[0].api_key == "test-key"
        assert result[0].name == "Test"
    
    def test_parse_mixed_list(self):
        """测试混合列表"""
        configs = [
            "key1",
            APIConfig(api_key="key2", name="API2")
        ]
        result = _parse_api_configs(configs)
        assert len(result) == 2
        assert result[0].api_key == "key1"
        assert result[1].name == "API2"


class TestParseModels:
    """测试模型解析"""
    
    def test_parse_preset_name(self):
        """测试预设名称"""
        result = _parse_models("qwen")
        assert result == ["Qwen/Qwen-Image"]
    
    def test_parse_full_id(self):
        """测试完整 ID"""
        result = _parse_models("Custom/Model-ID")
        assert result == ["Custom/Model-ID"]
    
    def test_parse_list(self):
        """测试列表"""
        result = _parse_models(["qwen", "flux-majic"])
        assert len(result) == 2
        assert "Qwen/Qwen-Image" in result


class TestValidation:
    """测试参数验证"""
    
    def test_invalid_size(self):
        """测试无效尺寸"""
        with pytest.raises(ValidationError):
            generate_image(
                prompt="test",
                api_configs="key",
                size="invalid-size"
            )


# 注意：以下测试需要真实的 API Key 才能运行
# 在实际环境中取消注释并配置

# class TestGeneration:
#     """测试图片生成"""
#     
#     def test_basic_generation(self):
#         """测试基础生成"""
#         result = generate_image(
#             prompt="test",
#             api_configs="your-real-api-key",
#             verbose=False
#         )
#         assert result is not None
#         assert 'image' in result