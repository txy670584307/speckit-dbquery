"""数据导出服务：将查询结果导出为 CSV 或 JSON 格式。"""

import csv
import io
import json
from typing import Any

from backend.models import ColumnInfo, ExportFormat


def generate_csv(columns: list[ColumnInfo], rows: list[list[Any]], include_bom: bool = True) -> str:
    """将查询结果生成为 RFC 4180 标准的 CSV 字符串。

    Args:
        columns: 列信息列表（用于生成表头）。
        rows: 行数据，每行与 columns 顺序对应。
        include_bom: 是否添加 UTF-8 BOM（便于 Excel 识别中文编码）。

    Returns:
        CSV 格式的完整文本内容。
    """
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)

    # 写入列名表头
    writer.writerow([col.name for col in columns])

    # 写入数据行
    for row in rows:
        writer.writerow([_serialize_cell(val) for val in row])

    content = output.getvalue()
    output.close()

    # 可选添加 UTF-8 BOM
    if include_bom:
        content = "\ufeff" + content

    return content


def generate_json(columns: list[ColumnInfo], rows: list[list[Any]]) -> str:
    """将查询结果生成为标准 JSON 数组字符串。

    输出格式: [{"colName": val, ...}, ...]，键名使用 camelCase（与 API 约定一致）。

    Args:
        columns: 列信息列表（用于生成对象键名）。
        rows: 行数据，每行与 columns 顺序对应。

    Returns:
        JSON 格式的完整文本内容。
    """
    records = []
    for row in rows:
        record = {}
        for i, col in enumerate(columns):
            record[col.name] = _serialize_cell(row[i])
        records.append(record)

    return json.dumps(records, ensure_ascii=False, indent=2, default=str)


def generate_export_content(
    columns: list[ColumnInfo],
    rows: list[list[Any]],
    fmt: ExportFormat,
) -> str:
    """根据导出格式生成文件内容。

    Args:
        columns: 列信息。
        rows: 行数据。
        fmt: 导出格式（CSV 或 JSON）。

    Returns:
        格式化的文件内容字符串。
    """
    if fmt == ExportFormat.CSV:
        return generate_csv(columns, rows)
    elif fmt == ExportFormat.JSON:
        return generate_json(columns, rows)
    else:
        raise ValueError(f"不支持的导出格式: {fmt}")


def build_filename(db_name: str, fmt: ExportFormat) -> str:
    """生成默认导出文件名。

    格式: {数据库名}_{yyyyMMdd_HHmmss}.{csv|json}
    """
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{db_name}_{timestamp}.{fmt.value}"


def _serialize_cell(val: Any) -> Any:
    """将单个单元格值序列化为可导出的形式。

    处理 None、二进制、大文本等特殊类型。
    """
    if val is None:
        return None

    # 布尔值转字符串（CSV 友好）
    if isinstance(val, bool):
        return str(val).lower()

    # 二进制/大文本截断（超过 65535 字符）
    if isinstance(val, str) and len(val) > 65535:
        return val[:65535] + "… [截断]"

    # 其他类型（数字、日期等）转字符串
    if not isinstance(val, (str, int, float)):
        return str(val)

    return val
