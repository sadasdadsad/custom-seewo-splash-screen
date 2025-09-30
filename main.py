import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.main_window import MainWindow
from utils.admin_helper import is_admin


def main():
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # PyQt6 中高DPI支持默认启用，无需手动设置
    # 如果需要调整DPI策略，可以使用以下方式：
    # app.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    # 设置应用程序信息
    app.setApplicationName("希沃白板启动图片修改器")
    app.setOrganizationName("CustomSeewoSplash")
    app.setApplicationVersion("1.0.0")
    
    # 设置应用程序样式（可选）
    app.setStyle("Fusion")
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
