import os
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QFileDialog, QInputDialog, QMessageBox
from PyQt6.QtGui import QIcon
# from PyQt6.QtCore import Qt
from qfluentwidgets import FluentWindow, FluentIcon as FIF, ProgressBar, Theme, setTheme

from core.config_manager import ConfigManager
from core.image_manager import ImageManager
from core.replacer import ImageReplacer
from utils.path_detector import PathDetector
from utils.admin_helper import is_admin, request_admin_and_exit

from .widgets import PathInfoCard, ImageListWidget, ActionBar
from .dialogs import MessageHelper, PathHistoryDialog


class MainWindow(FluentWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self._init_window()
        self._init_managers()
        self._init_ui()
        self._connect_signals()
        self._load_initial_data()
        self._check_admin_status()
    
    def _init_window(self):
        """初始化窗口属性"""
        self.setWindowTitle("SeewoSplash")
        self.setWindowIcon(QIcon("assets/icon.ico"))
        self.resize(900, 650)
        # 设置主题 (可选)
        setTheme(Theme.AUTO)  # 自动跟随系统, 或使用 Theme.LIGHT/Theme.DARK
    
    def _init_managers(self):
        """初始化管理器"""
        self.config_manager = ConfigManager()
        self.image_manager = ImageManager()
        self.replacer = ImageReplacer()
        self.target_path = ""
    
    def _init_ui(self):
        """初始化UI"""
        # 创建主界面
        self.homeInterface = QWidget()
        self.homeInterface.setObjectName("homeInterface")
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页')
        
        # 主布局
        layout = QVBoxLayout(self.homeInterface)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 创建组件
        self.path_card = PathInfoCard(self.homeInterface)
        self.image_list = ImageListWidget(self.homeInterface)
        self.action_bar = ActionBar(self.homeInterface)
        self.progress_bar = ProgressBar(self.homeInterface)
        self.progress_bar.setVisible(False)
        
        # 添加到布局
        layout.addWidget(self.path_card)
        layout.addWidget(self.image_list, 1)
        layout.addWidget(self.action_bar)
        layout.addWidget(self.progress_bar)
    
    def _connect_signals(self):
        """连接信号槽"""
        # 路径卡片信号
        self.path_card.detect_button.clicked.connect(self.detect_target_path)
        self.path_card.history_button.clicked.connect(self.show_path_history)
        
        # 图片列表信号
        self.image_list.imageSelected.connect(self._on_image_selected)
        self.image_list.imagesDropped.connect(self._on_images_dropped)
        
        # 操作栏信号
        self.action_bar.importClicked.connect(self.import_image)
        self.action_bar.renameClicked.connect(self.rename_image)
        self.action_bar.deleteClicked.connect(self.delete_image)
        self.action_bar.replaceClicked.connect(self.replace_startup_image)
        self.action_bar.restoreClicked.connect(self.restore_from_backup)
    
    def _load_initial_data(self):
        """加载初始数据"""
        self.load_images()
        self.load_and_validate_target_path()
    
    def _check_admin_status(self):
        """检查管理员权限状态"""
        if is_admin():
            # 如果是管理员权限，在标题栏显示提示
            current_title = self.windowTitle()
            self.setWindowTitle(f"{current_title} [管理员]")
    
    def _on_image_selected(self, image_info: dict):
        """图片选中时的处理
        
        Args:
            image_info: 图片信息字典
        """
        self.config_manager.set_last_selected_image(image_info["filename"])
        is_custom = image_info["type"] == "custom"
        self.action_bar.set_rename_delete_enabled(is_custom)

    def _on_images_dropped(self, drop_data):
        """处理拖放的图片文件
        
        Args:
            drop_data: [file_paths, ignored_files] 列表
        """
        file_paths, ignored_files = drop_data
        
        # 如果有被忽略的非PNG文件，显示警告
        if ignored_files:
            ignored_str = "、".join(ignored_files[:3])  # 最多显示3个
            if len(ignored_files) > 3:
                ignored_str += f" 等{len(ignored_files)}个文件"
            
            MessageHelper.show_warning(
                self,
                "文件格式错误",
                f"以下文件不是PNG格式，已忽略：\n{ignored_str}"
            )
        
        # 如果没有有效的PNG文件，直接返回
        if not file_paths:
            return
        
        # 显示进度
        self.show_progress(f"正在导入 {len(file_paths)} 个文件...")
        
        # 导入所有PNG文件
        success_count = 0
        failed_files = []
        
        for file_path in file_paths:
            success, msg = self.image_manager.import_image(file_path)
            if success:
                success_count += 1
            else:
                failed_files.append((os.path.basename(file_path), msg))
        
        self.hide_progress()
        
        # 显示导入结果
        if success_count > 0:
            if success_count == len(file_paths):
                # 全部成功
                MessageHelper.show_success(
                    self,
                    f"成功导入 {success_count} 个图片",
                    3000
                )
            else:
                # 部分成功
                MessageHelper.show_success(
                    self,
                    f"成功导入 {success_count} 个图片，{len(failed_files)} 个失败",
                    3000
                )
            
            # 刷新图片列表
            self.load_images()
        
        # 如果有失败的，显示详细错误信息
        if failed_files:
            error_details = "\n".join([f"• {name}: {msg}" for name, msg in failed_files[:5]])
            if len(failed_files) > 5:
                error_details += f"\n... 还有 {len(failed_files) - 5} 个文件失败"
            
            MessageHelper.show_error(
                self,
                "部分文件导入失败",
                error_details
            )

    
    def show_progress(self, message: str):
        """显示进度
        
        Args:
            message: 进度消息
        """
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        MessageHelper.show_success(self, message, 2000)
    
    def hide_progress(self):
        """隐藏进度"""
        self.progress_bar.setVisible(False)
    
    def handle_permission_error(self, error_message: str):
        """处理权限错误
        
        Args:
            error_message: 错误消息
        """
        if is_admin():
            # 已经是管理员权限了，但还是权限不足
            QMessageBox.critical(
                self,
                "权限不足",
                f"{error_message}\n\n"
                "即使以管理员身份运行，仍然无法访问该文件。\n\n"
                "可能的原因：\n"
                "• 文件正在被希沃白板或其他程序使用\n"
                "• 文件被系统或杀毒软件保护\n"
                "• 磁盘权限配置问题\n\n"
                "建议：\n"
                "• 完全关闭希沃白板后重试\n"
                "• 检查文件是否被杀毒软件锁定\n"
                "• 尝试重启电脑后再操作"
            )
        else:
            # 不是管理员权限，询问是否以管理员身份重启
            reply = QMessageBox.question(
                self,
                "需要管理员权限",
                f"{error_message}\n\n"
                "此操作需要管理员权限才能完成。\n\n"
                "是否以管理员身份重新启动程序？\n\n"
                "注意：程序将会关闭并重新启动。",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # 请求管理员权限并重启
                if request_admin_and_exit():
                    # 成功请求，当前程序会退出
                    # 不需要额外操作，程序会自动关闭
                    pass
                else:
                    # 请求失败
                    QMessageBox.warning(
                        self,
                        "启动失败",
                        "无法以管理员身份重新启动程序。\n\n"
                        "请尝试以下方法：\n"
                        "• 右键点击程序图标\n"
                        "• 选择以管理员身份运行\n\n"
                        "或者关闭希沃白板后再试。"
                    )
    
    def load_and_validate_target_path(self):
        """加载并验证目标路径"""
        # 先尝试加载上次保存的路径
        saved_path = self.config_manager.get_target_path()
        
        if saved_path:
            # 验证路径是否仍然有效
            is_valid, error_msg = PathDetector.validate_target_path(saved_path)
            
            if is_valid:
                # 路径有效,直接使用
                self.target_path = saved_path
                self.path_card.update_path_display(self.target_path)
                MessageHelper.show_success(
                    self, 
                    f"已加载上次使用的路径: {os.path.basename(saved_path)}"
                )
                return
            else:
                # 路径无效,提示用户
                reply = QMessageBox.question(
                    self,
                    "路径已失效",
                    f"上次保存的路径已失效:\n{saved_path}\n\n"
                    f"失效原因: {error_msg}\n\n"
                    "是否需要重新检测路径?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.detect_target_path()
                    return
        
        # 没有保存的路径,尝试从历史记录中查找有效路径
        history = self.config_manager.get_path_history()
        for historical_path in history:
            is_valid, _ = PathDetector.validate_target_path(historical_path)
            if is_valid:
                self.target_path = historical_path
                self.config_manager.set_target_path(historical_path)
                self.path_card.update_path_display(self.target_path)
                MessageHelper.show_success(
                    self,
                    f"已从历史记录恢复路径: {os.path.basename(historical_path)}"
                )
                return
        
        # 清理无效的历史记录
        self.config_manager.clear_invalid_history()
        
        # 如果启用了自动检测,则自动检测
        if self.config_manager.get_auto_detect_on_startup():
            self.detect_target_path()
        else:
            self.path_card.update_path_display("")
    
    def detect_target_path(self):
        """检测目标路径"""
        self.show_progress("正在检测路径...")
        
        paths = PathDetector.detect_all_paths()
        
        self.hide_progress()
        
        if paths:
            # 如果检测到多个路径,让用户选择
            if len(paths) > 1:
                items = [f"{i+1}. {path}" for i, path in enumerate(paths)]
                item, ok = QInputDialog.getItem(
                    self,
                    "选择目标路径",
                    f"检测到 {len(paths)} 个可能的启动图片路径,\n请选择要使用的路径:",
                    items,
                    0,
                    False
                )
                if ok and item:
                    index = int(item.split('.')[0]) - 1
                    self.target_path = paths[index]
                else:
                    return
            else:
                self.target_path = paths[0]
            
            self.config_manager.set_target_path(self.target_path)
            self.path_card.update_path_display(self.target_path)
            MessageHelper.show_success(
                self,
                f"检测成功: {os.path.basename(self.target_path)}",
                5000
            )
        else:
            # 未检测到路径,提示用户手动选择
            self.target_path = PathDetector.manual_select_target_image(self)
            
            if self.target_path:
                # 验证选择的路径
                is_valid, error_msg = PathDetector.validate_target_path(self.target_path)
                
                if is_valid:
                    self.config_manager.set_target_path(self.target_path)
                    self.path_card.update_path_display(self.target_path)
                    MessageHelper.show_success(
                        self,
                        f"路径设置成功: {os.path.basename(self.target_path)}",
                        5000
                    )
                else:
                    QMessageBox.warning(
                        self, "路径无效",
                        f"选择的路径无效:\n{error_msg}\n\n请重新选择。"
                    )
                    self.target_path = ""
                    self.config_manager.set_target_path("")
                    self.path_card.update_path_display("")
            else:
                # 用户取消选择
                self.path_card.update_path_display("")
    
    def show_path_history(self):
        """显示历史路径选择对话框"""
        from ui.dialogs.path_history_dialog import PathHistoryHelper
        
        selected_path, success = PathHistoryHelper.show_and_select(
            self,
            self.config_manager
        )
        
        if success and selected_path:
            self.target_path = selected_path
            self.config_manager.set_target_path(selected_path)
            self.path_card.update_path_display(self.target_path)
            # PathHistoryHelper 内部已经显示了成功消息,这里不需要重复显示
    
    def load_images(self):
        """加载图片列表"""
        preset_images = self.image_manager.get_preset_images()
        custom_images = self.image_manager.get_custom_images()
        self.image_list.load_images(preset_images, custom_images)
        
        # 恢复上次选中的图片
        last_selected = self.config_manager.get_last_selected_image()
        if last_selected:
            self.image_list.select_image_by_filename(last_selected)
    
    def import_image(self):
        """导入图片"""
        file_dialog = QFileDialog(self, "选择PNG图片", os.path.expanduser("~"))
        file_dialog.setNameFilter("PNG图片 (*.png)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                source_path = selected_files[0]
                
                self.show_progress("正在导入...")
                
                success, msg = self.image_manager.import_image(source_path)
                
                self.hide_progress()
                
                if success:
                    MessageHelper.show_success(
                        self,
                        f"图片导入成功: {os.path.basename(source_path)}",
                        3000
                    )
                    self.load_images()
                else:
                    MessageHelper.show_error(self, "导入失败", msg)
    
    def rename_image(self):
        """重命名图片"""
        image_info = self.image_list.get_selected_image_info()
        
        if not image_info:
            MessageHelper.show_warning(self, "未选择图片", "请先选择要重命名的图片")
            return
        
        if image_info["type"] != "custom":
            MessageHelper.show_warning(self, "无法重命名", "只能重命名自定义图片")
            return
        
        new_name, ok = QInputDialog.getText(
            self, "重命名图片",
            "请输入新的显示名称:",
            text=image_info["display_name"]
        )
        
        if ok and new_name and new_name.strip():
            new_name = new_name.strip()
            success, msg = self.image_manager.rename_custom_image(
                image_info["filename"],
                new_name
            )
            if success:
                self.config_manager.update_custom_image_name(
                    image_info["filename"],
                    new_name
                )
                MessageHelper.show_success(self, f"已重命名为: {new_name}", 2000)
                self.load_images()
            else:
                MessageHelper.show_error(self, "重命名失败", msg)
    
    def delete_image(self):
        """删除图片"""
        image_info = self.image_list.get_selected_image_info()
        
        if not image_info:
            MessageHelper.show_warning(self, "未选择图片", "请先选择要删除的图片")
            return
        
        if image_info["type"] != "custom":
            MessageHelper.show_warning(self, "无法删除", "只能删除自定义图片")
            return
        
        # 直接删除
        success = self.image_manager.delete_custom_image(image_info["filename"])
        if success:
            self.config_manager.remove_custom_image(image_info["filename"])
            MessageHelper.show_success(
                self,
                f"已删除图片: {image_info['display_name']}",
                2000
            )
            self.load_images()
        else:
            MessageHelper.show_error(self, "删除失败", "无法删除图片,请检查文件权限")
    
    def replace_startup_image(self):
        """替换启动图片"""
        if not self.target_path:
            MessageHelper.show_warning(self, "未检测到路径", "请先点击'检测路径'按钮")
            return
        
        image_info = self.image_list.get_selected_image_info()
        if not image_info:
            MessageHelper.show_warning(
                self,
                "未选择图片",
                "请先从列表中选择要替换的图片"
            )
            return
        
        self.show_progress("正在替换...")
        
        success, msg, is_permission_error = self.replacer.replace_image(
            image_info["path"],
            self.target_path
        )
        
        self.hide_progress()
        
        if success:
            MessageHelper.show_success(
                self,
                f"启动图片已替换为: {image_info['display_name']}",
                3000
            )
        else:
            if is_permission_error:
                # 权限问题，提示用户以管理员身份运行
                self.handle_permission_error(msg)
            else:
                # 其他错误
                MessageHelper.show_error(self, "替换失败", msg)
    
    def restore_from_backup(self):
        """从备份还原"""
        if not self.target_path:
            MessageHelper.show_warning(self, "未检测到路径", "请先点击'检测路径'按钮")
            return
        
        self.show_progress("正在还原...")
        
        success, msg, is_permission_error = self.replacer.restore_backup(self.target_path)
        
        self.hide_progress()
        
        if success:
            MessageHelper.show_success(self, "已从备份还原启动图片", 3000)
        else:
            if is_permission_error:
                # 权限问题，提示用户以管理员身份运行
                self.handle_permission_error(msg)
            else:
                # 其他错误
                MessageHelper.show_error(self, "还原失败", msg)
