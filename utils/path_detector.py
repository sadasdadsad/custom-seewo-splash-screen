import os
import glob
from qfluentwidgets import MessageBox, Dialog
from PyQt6.QtWidgets import QFileDialog


class PathDetector:
    """检测希沃白板启动图片路径"""
    
    @staticmethod
    def detect_banner_paths():
        """检测Banner.png路径"""
        paths = []
        users_dir = "C:\\Users"
        
        if os.path.exists(users_dir):
            for user_folder in os.listdir(users_dir):
                banner_path = os.path.join(
                    users_dir, 
                    user_folder, 
                    "AppData\\Roaming\\Seewo\\EasiNote5\\Resources\\Banner\\Banner.png"
                )
                if os.path.exists(banner_path):
                    paths.append(banner_path)
        
        return paths
    
    @staticmethod
    def detect_splashscreen_paths():
        """检测SplashScreen.png路径"""
        paths = []
        
        # 检测 Program Files (x86)
        base_path_x86 = "C:\\Program Files (x86)\\Seewo\\EasiNote5"
        if os.path.exists(base_path_x86):
            pattern = os.path.join(base_path_x86, "EasiNote5*", "Main", "Assets", "SplashScreen.png")
            paths.extend(glob.glob(pattern))
        
        # 检测 Program Files
        base_path = "C:\\Program Files\\Seewo\\EasiNote5"
        if os.path.exists(base_path):
            pattern = os.path.join(base_path, "EasiNote5*", "Main", "Assets", "SplashScreen.png")
            paths.extend(glob.glob(pattern))
        
        return paths
    
    @staticmethod
    def detect_all_paths():
        """检测所有可能的路径"""
        all_paths = []
        all_paths.extend(PathDetector.detect_banner_paths())
        all_paths.extend(PathDetector.detect_splashscreen_paths())
        return all_paths
    
    @staticmethod
    def manual_select_target_image(parent=None):
        """
        手动选择目标图片
        
        Args:
            parent: 父窗口对象
            
        Returns:
            str: 选中的图片路径,如果取消则返回空字符串
        """
        # 使用QFluentWidgets的MessageBox显示说明对话框
        content = (
            "无法自动检测到希沃白板的启动图片。\n\n"
            "您可以手动选择要替换的目标图片文件。\n"
            "目标图片通常位于以下位置之一:\n\n"
            "1. Banner.png:\n"
            "   C:\\Users\\[用户名]\\AppData\\Roaming\\Seewo\\EasiNote5\\Resources\\Banner\\Banner.png\n\n"
            "2. SplashScreen.png:\n"
            "   C:\\Program Files\\Seewo\\EasiNote5\\EasiNote5.xxx\\Main\\Assets\\SplashScreen.png\n\n"
            "是否现在手动选择目标图片?"
        )
        
        # 创建确认对话框
        dialog = MessageBox(
            title="手动选择目标图片",
            content=content,
            parent=parent
        )
        
        if dialog.exec():
            # 用户点击了确定按钮,打开文件选择对话框
            # 注意: QFluentWidgets目前没有提供文件选择对话框,仍使用PyQt6的QFileDialog
            file_dialog = QFileDialog(parent, "选择希沃白板启动图片")
            file_dialog.setNameFilter("PNG图片 (*.png);;所有文件 (*.*)")
            file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
            
            # 设置初始目录为常见路径
            initial_dir = "C:\\Program Files\\Seewo\\EasiNote5"
            if not os.path.exists(initial_dir):
                initial_dir = "C:\\Program Files (x86)\\Seewo\\EasiNote5"
            if not os.path.exists(initial_dir):
                initial_dir = os.path.join(os.environ.get("APPDATA", "C:\\"), "Seewo")
            if not os.path.exists(initial_dir):
                initial_dir = "C:\\"
            
            file_dialog.setDirectory(initial_dir)
            
            if file_dialog.exec():
                selected_files = file_dialog.selectedFiles()
                if selected_files:
                    selected_path = selected_files[0]
                    
                    # 验证选择的文件
                    if not selected_path.lower().endswith('.png'):
                        MessageBox(
                            title="文件类型错误",
                            content="请选择PNG格式的图片文件。",
                            parent=parent
                        ).exec()
                        return ""
                    
                    if not os.path.exists(selected_path):
                        MessageBox(
                            title="文件不存在",
                            content="选择的文件不存在,请重新选择。",
                            parent=parent
                        ).exec()
                        return ""
                    
                    # 确认选择
                    filename = os.path.basename(selected_path)
                    confirm_content = (
                        f"您选择的目标图片是:\n\n{selected_path}\n\n"
                        f"文件名: {filename}\n\n"
                        "确认使用此图片作为替换目标吗?"
                    )
                    
                    confirm_dialog = MessageBox(
                        title="确认目标图片",
                        content=confirm_content,
                        parent=parent
                    )
                    
                    if confirm_dialog.exec():
                        return selected_path
        
        return ""
    
    @staticmethod
    def validate_target_path(path):
        """
        验证目标路径是否有效
        
        Args:
            path: 要验证的路径
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        if not path:
            return False, "路径为空"
        
        if not os.path.exists(path):
            return False, "文件不存在"
        
        if not path.lower().endswith('.png'):
            return False, "不是PNG文件"
        
        if not os.path.isfile(path):
            return False, "不是文件"
        
        # 检查是否有读写权限
        if not os.access(path, os.R_OK):
            return False, "没有读取权限"
        
        # 检查文件大小(启动图片通常不会太小)
        file_size = os.path.getsize(path)
        if file_size < 1024:  # 小于1KB
            return False, "文件太小,可能不是有效的启动图片"
        
        return True, "路径有效"
