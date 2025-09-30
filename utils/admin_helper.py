import ctypes
import sys
# import os


def is_admin():
    """检查是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """请求以管理员权限重启程序"""
    try:
        if sys.argv[0].endswith('.py'):
            # 如果是Python脚本
            params = ' '.join([sys.executable] + sys.argv)
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, ' '.join(sys.argv), None, 1
            )
        else:
            # 如果是打包后的exe
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, ' '.join(sys.argv[1:]), None, 1
            )
        return True
    except:
        return False
