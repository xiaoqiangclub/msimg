"""
MSIMG CLI 核心模块 - 输出处理
"""

import json
import csv
from typing import Any, Dict, List, Optional

class ExportManager:
    """输出管理器"""

    def __init__(self):
        """初始化输出管理器"""
        pass

    def export_json(self, data: Any, output_path: str, indent: int = 2) -> bool:
        """
        导出为JSON格式

        Args:
            data: 要导出的数据
            output_path: 输出文件路径
            indent: JSON缩进

        Returns:
            是否导出成功
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
            print(f"✅ JSON数据已导出到: {output_path}")
            return True
        except Exception as e:
            print(f"❌ JSON导出失败: {str(e)}")
            return False

    def export_csv(self, data: List[Dict[str, Any]], output_path: str, headers: Optional[List[str]] = None) -> bool:
        """
        导出为CSV格式

        Args:
            data: 要导出的数据列表
            output_path: 输出文件路径
            headers: CSV列标题

        Returns:
            是否导出成功
        """
        try:
            if not data:
                print("⚠️  没有数据可导出")
                return False

            if headers is None:
                headers = list(data[0].keys()) if data else []

            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data)

            print(f"✅ CSV数据已导出到: {output_path}")
            return True
        except Exception as e:
            print(f"❌ CSV导出失败: {str(e)}")
            return False

    def export_text(self, data: str, output_path: str) -> bool:
        """
        导出为文本格式

        Args:
            data: 要导出的文本
            output_path: 输出文件路径

        Returns:
            是否导出成功
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(data)
            print(f"✅ 文本数据已导出到: {output_path}")
            return True
        except Exception as e:
            print(f"❌ 文本导出失败: {str(e)}")
            return False

    def format_output(self, data: Any, output_format: str = 'json', **kwargs) -> str:
        """
        格式化输出数据

        Args:
            data: 要格式化的数据
            output_format: 输出格式 ('json', 'text', 'table')
            **kwargs: 格式化选项

        Returns:
            格式化后的字符串
        """
        if output_format.lower() == 'json':
            indent = kwargs.get('indent', 2)
            return json.dumps(data, ensure_ascii=False, indent=indent)
        elif output_format.lower() == 'text':
            return str(data)
        elif output_format.lower() == 'table':
            # 简单的表格格式输出
            if isinstance(data, list) and data and isinstance(data[0], dict):
                headers = list(data[0].keys())
                # 计算每列最大宽度
                col_widths = {}
                for header in headers:
                    col_widths[header] = len(header)

                for row in data:
                    for header in headers:
                        if header in row:
                            col_widths[header] = max(col_widths[header], len(str(row[header])))

                # 构建表格
                lines = []
                # 表头
                header_line = " | ".join(header.ljust(col_widths[header]) for header in headers)
                lines.append(header_line)
                lines.append("-" * len(header_line))

                # 数据行
                for row in data:
                    data_line = " | ".join(str(row.get(header, "")).ljust(col_widths[header]) for header in headers)
                    lines.append(data_line)

                return "\n".join(lines)
            else:
                return str(data)
        else:
            return str(data)