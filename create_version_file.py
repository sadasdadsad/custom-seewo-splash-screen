"""
生成 PyInstaller 版本信息文件

此脚本会读取 app_info.py 中的信息，生成 Windows 可执行文件的版本资源。
"""

import os
from pathlib import Path
from core.app_info import __version__, __author__, __app_name__, __description__, __license__


def parse_version(version_string):
    """
    解析版本号字符串为四位数字
    例如: "1.0.0" -> (1, 0, 0, 0)
    """
    parts = version_string.split('.')
    # 确保有4位数字
    while len(parts) < 4:
        parts.append('0')
    
    # 只取前4位
    parts = parts[:4]
    
    # 转换为整数
    return tuple(int(p) for p in parts)


def create_version_file():
    """创建版本信息文件"""
    
    # 解析版本号
    file_version = parse_version(__version__)
    product_version = file_version
    
    # 将版本号转为字符串格式
    file_version_str = ', '.join(map(str, file_version))
    product_version_str = '.'.join(map(str, product_version[:3]))  # 显示为 x.y.z
    
    # 当前年份（用于版权信息）
    from datetime import datetime
    current_year = datetime.now().year
    
    # 版本信息模板
    version_info = f'''# UTF-8
#
# 此文件由 create_version_file.py 自动生成
# 包含 Windows 可执行文件的版本资源信息
#

VSVersionInfo(
  ffi=FixedFileInfo(
    # 文件版本号 (必须是 x.x.x.x 格式)
    filevers=({file_version_str}),
    # 产品版本号
    prodvers=({file_version_str}),
    # 文件标志掩码
    mask=0x3f,
    # 文件标志
    flags=0x0,
    # 操作系统类型
    OS=0x40004,
    # 文件类型
    fileType=0x1,
    # 文件子类型
    subtype=0x0,
    # 文件日期
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'080404b0',
        [
          StringStruct(u'CompanyName', u'{__author__}'),
          StringStruct(u'FileDescription', u'{__description__}'),
          StringStruct(u'FileVersion', u'{product_version_str}'),
          StringStruct(u'InternalName', u'{__app_name__}'),
          StringStruct(u'LegalCopyright', u'Copyright © {current_year} {__author__}. Licensed under {__license__}.'),
          StringStruct(u'OriginalFilename', u'{__app_name__}.exe'),
          StringStruct(u'ProductName', u'{__app_name__}'),
          StringStruct(u'ProductVersion', u'{product_version_str}'),
          StringStruct(u'LegalTrademarks', u''),
          StringStruct(u'Comments', u'{__description__}'),
        ]
      )
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [2052, 1200])])
  ]
)
'''
    
    # 写入文件
    output_file = Path(__file__).parent / 'version_info.txt'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(version_info)
    
    print(f"✓ 版本信息文件已生成: {output_file}")
    print(f"  应用名称: {__app_name__}")
    print(f"  版本号: {product_version_str}")
    print(f"  作者: {__author__}")
    print(f"  描述: {__description__}")
    print(f"  许可证: {__license__}")
    print(f"  版权年份: {current_year}")
    
    return output_file


if __name__ == '__main__':
    create_version_file()
