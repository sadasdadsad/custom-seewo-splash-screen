import os
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QInputDialog,
    QProgressBar
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize
from core.config_manager import ConfigManager
from core.image_manager import ImageManager
from core.replacer import ImageReplacer
from utils.admin_helper import is_admin, run_as_admin
from utils.path_detector import PathDetector
from qfluentwidgets import (
    # 窗口和布局
    FluentWindow, 
    # 按钮
    PrimaryPushButton, PushButton, TransparentToolButton,
    # 列表和卡片
    ListWidget, CardWidget, ImageLabel,
    # 信息提示
    InfoBar, InfoBarPosition,
    # 进度条
    IndeterminateProgressRing, ProgressBar,
    # 图标
    FluentIcon as FIF,
    # 其他
    BodyLabel, TitleLabel, StrongBodyLabel
)
from qfluentwidgets import Theme, setTheme

class MainWindow(FluentWindow):  # 改为继承 FluentWindow
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SeewoSplash")
        self.setWindowIcon(QIcon("assets/icon.ico"))
        self.resize(900, 650)  # 使用 resize 替代 setMinimumSize
        
        # 设置主题 (可选)
        # setTheme(Theme.AUTO)  # 自动跟随系统, 或使用 Theme.LIGHT/Theme.DARK
        
        self.config_manager = ConfigManager()
        self.image_manager = ImageManager()
        self.replacer = ImageReplacer()
        
        self.target_path = ""
        
        # 创建主界面
        self.homeInterface = QWidget()
        self.homeInterface.setObjectName("homeInterface")
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页')
        
        self.init_ui()
        self.load_images()
        
        # 启动时自动加载和验证路径
        self.load_and_validate_target_path()

    
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
                self.update_target_label()
                self.show_status_message(f"已加载上次使用的路径: {os.path.basename(saved_path)}")
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
                self.update_target_label()
                self.show_status_message(f"已从历史记录恢复路径: {os.path.basename(historical_path)}")
                return
        
        # 清理无效的历史记录
        self.config_manager.clear_invalid_history()
        
        # 如果启用了自动检测,则自动检测
        if self.config_manager.get_auto_detect_on_startup():
            self.detect_target_path()
        else:
            self.update_target_label()
    
    def show_status_message(self, message, duration=3000):
        """使用 InfoBar 显示消息"""
        InfoBar.success(
            title="",
            content=message,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=duration,
            parent=self
        )

    def show_error_message(self, title, message):
        """显示错误消息"""
        InfoBar.error(
            title=title,
            content=message,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self
        )

    def show_warning_message(self, title, message):
        """显示警告消息"""
        InfoBar.warning(
            title=title,
            content=message,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=4000,
            parent=self
        )

    def show_progress(self, message):
        """显示进度"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        # Fluent ProgressBar 会自动显示动画
        self.show_status_message(message, 10000)

    def hide_progress(self):
        """隐藏进度"""
        self.progress_bar.setVisible(False)
    
    def init_ui(self):
        # 使用 homeInterface 作为容器
        layout = QVBoxLayout(self.homeInterface)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 顶部信息卡片
        info_card = CardWidget(self.homeInterface)
        info_card.setFixedHeight(80)
        info_card_layout = QHBoxLayout(info_card)
        
        # 使用 Fluent 样式标签
        self.target_label = StrongBodyLabel()
        self.target_label.setWordWrap(True)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 使用 Fluent 按钮 (带图标)
        self.detect_button = PushButton(FIF.SEARCH, "检测路径")
        self.detect_button.clicked.connect(self.detect_target_path)
        self.detect_button.setToolTip("自动检测希沃白板启动图片路径")
        
        self.history_button = PushButton(FIF.HISTORY, "历史路径")
        self.history_button.clicked.connect(self.show_path_history)
        self.history_button.setToolTip("查看和选择历史路径")
        
        button_layout.addWidget(self.detect_button)
        button_layout.addWidget(self.history_button)
        
        info_card_layout.addWidget(self.target_label, 1)
        info_card_layout.addLayout(button_layout)
        
        # 更新目标路径标签显示
        self.update_target_label()
        
        # 图片列表 - 使用 Fluent ListWidget
        self.image_list = ListWidget(self.homeInterface)
        self.image_list.setIconSize(QSize(128, 128))
        self.image_list.setSpacing(10)
        self.image_list.setViewMode(ListWidget.ViewMode.IconMode)
        self.image_list.setResizeMode(ListWidget.ResizeMode.Adjust)
        self.image_list.setMovement(ListWidget.Movement.Static)
        self.image_list.itemSelectionChanged.connect(self.on_image_selected)
        
        # 底部操作按钮
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)
        
        # 使用 Fluent 按钮
        self.import_button = PushButton(FIF.ADD, "导入图片")
        self.import_button.clicked.connect(self.import_image)
        
        self.rename_button = PushButton(FIF.EDIT, "重命名")
        self.rename_button.clicked.connect(self.rename_image)
        
        self.delete_button= PushButton(FIF.DELETE, "删除")
        self.delete_button.clicked.connect(self.delete_image)
        
        # 主要操作按钮使用 PrimaryPushButton
        self.replace_button = PrimaryPushButton(FIF.UPDATE, "替换启动图片")
        self.replace_button.clicked.connect(self.replace_startup_image)
        
        self.restore_button = PushButton(FIF.SYNC, "从备份还原")
        self.restore_button.clicked.connect(self.restore_from_backup)
        
        bottom_layout.addWidget(self.import_button)
        bottom_layout.addWidget(self.rename_button)
        bottom_layout.addWidget(self.delete_button)
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(self.restore_button)
        bottom_layout.addWidget(self.replace_button)
        
        # 进度条 - 使用 Fluent ProgressBar
        self.progress_bar = ProgressBar(self.homeInterface)
        self.progress_bar.setVisible(False)
        
        # 添加到主布局
        layout.addWidget(info_card)
        layout.addWidget(self.image_list, 1)
        layout.addLayout(bottom_layout)
        layout.addWidget(self.progress_bar)

    
    def show_path_history(self):
        """显示历史路径选择对话框"""
        history = self.config_manager.get_path_history()
        
        if not history:
            QMessageBox.information(
                self, 
                "无历史记录", 
                "暂无历史路径记录。\n\n请点击'检测路径'按钮检测启动图片路径。"
            )
            return
        
        # 验证历史路径并标记有效性
        items = []
        valid_paths = []
        for i, path in enumerate(history):
            is_valid, error_msg = PathDetector.validate_target_path(path)
            status = "✓ 有效" if is_valid else f"✗ 无效 ({error_msg})"
            items.append(f"{i+1}. [{status}] {path}")
            if is_valid:
                valid_paths.append(path)
        
        if not valid_paths:
            reply = QMessageBox.question(
                self,
                "所有历史路径均无效",
                "历史记录中的所有路径都已失效。\n\n是否清理历史记录并重新检测?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.config_manager.clear_invalid_history()
                self.detect_target_path()
            return
        
        item, ok = QInputDialog.getItem(
            self,
            "选择历史路径",
            f"共有 {len(history)} 条历史记录,其中 {len(valid_paths)} 条有效:\n\n"
            "请选择要使用的路径:",
            items,
            0,
            False
        )
        
        if ok and item:
            index = int(item.split('.')[0]) - 1
            selected_path = history[index]
            
            # 验证选择的路径
            is_valid, error_msg = PathDetector.validate_target_path(selected_path)
            
            if is_valid:
                self.target_path = selected_path
                self.config_manager.set_target_path(selected_path)
                self.update_target_label()
                # 改为状态栏提示
                self.show_status_message(f"已设置目标路径: {os.path.basename(selected_path)}", 5000)
            else:
                QMessageBox.warning(
                    self,
                    "路径无效",
                    f"选择的路径已失效:\n{error_msg}\n\n请选择其他路径或重新检测。"
                )
    
    def load_images(self):
        """加载图片列表"""
        preset_images = self.image_manager.get_preset_images()
        custom_images = self.image_manager.get_custom_images()
        all_images = preset_images + custom_images
        
        self.image_list.clear()
        for img_info in all_images:
            item = QListWidgetItem(img_info["display_name"])
            
            # 加载并设置图标
            if os.path.exists(img_info["path"]):
                pixmap = QPixmap(img_info["path"])
                if not pixmap.isNull():
                    item.setIcon(QIcon(pixmap))
            
            item.setData(Qt.ItemDataRole.UserRole, img_info)
            item.setToolTip(f"类型: {'预设' if img_info['type'] == 'preset' else '自定义'}\n文件名: {img_info['filename']}")
            self.image_list.addItem(item)
        
        # 恢复上次选中的图片
        last_selected = self.config_manager.get_last_selected_image()
        if last_selected:
            for i in range(self.image_list.count()):
                item = self.image_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole)["filename"] == last_selected:
                    self.image_list.setCurrentItem(item)
                    break
    
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
            self.update_target_label()
            # 改为状态栏提示
            self.show_status_message(f"检测成功: {os.path.basename(self.target_path)}", 5000)
        else:
            # 未检测到路径,提示用户手动选择
            self.target_path = PathDetector.manual_select_target_image(self)
            
            if self.target_path:
                # 验证选择的路径
                is_valid, error_msg = PathDetector.validate_target_path(self.target_path)
                
                if is_valid:
                    self.config_manager.set_target_path(self.target_path)
                    self.update_target_label()
                    # 改为状态栏提示
                    self.show_status_message(f"路径设置成功: {os.path.basename(self.target_path)}", 5000)
                else:
                    QMessageBox.warning(
                        self, "路径无效",
                        f"选择的路径无效:\n{error_msg}\n\n请重新选择。"
                    )
                    self.target_path = ""
                    self.config_manager.set_target_path("")
                    self.update_target_label()
            else:
                # 用户取消选择
                self.update_target_label()
    
    def update_target_label(self):
        """更新目标路径标签"""
        if self.target_path:
            path_parts = self.target_path.split(os.sep)
            if len(path_parts) > 3:
                short_path = "..." + os.sep + os.sep.join(path_parts[-3:])
            else:
                short_path = self.target_path
            
            self.target_label.setText(f"✓ 当前路径: {short_path}")
            self.target_label.setToolTip(f"完整路径:\n{self.target_path}")
        else:
            self.target_label.setText("⚠ 未检测到启动图片路径 (点击右侧按钮进行检测)")
            self.target_label.setToolTip("请点击'检测路径'或'历史路径'按钮")
    
    def on_image_selected(self):
        """当图片被选中时"""
        selected_items = self.image_list.selectedItems()
        if selected_items:
            image_info = selected_items[0].data(Qt.ItemDataRole.UserRole)
            self.config_manager.set_last_selected_image(image_info["filename"])
            
            # 更新按钮状态
            is_custom = image_info["type"] == "custom"
            self.rename_button.setEnabled(is_custom)
            self.delete_button.setEnabled(is_custom)
    
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
                    # 改为状态栏提示
                    self.show_status_message(f"图片导入成功: {os.path.basename(source_path)}", 3000)
                    self.load_images()
                else:
                    # 失败保留弹窗
                    self.show_error_message("导入失败", msg)
    
    def rename_image(self):
        """重命名图片"""
        selected_items = self.image_list.selectedItems()
        if not selected_items:
            self.show_warning_message("未选择图片", "请先选择要重命名的图片")
            return
        
        image_info = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        if image_info["type"] != "custom":
            self.show_warning_message("无法重命名", "只能重命名自定义图片")
            return
        
        new_name, ok = QInputDialog.getText(
            self, "重命名图片", 
            "请输入新的显示名称:", 
            text=image_info["display_name"]
        )
        
        if ok and new_name and new_name.strip():
            new_name = new_name.strip()
            success, msg = self.image_manager.rename_custom_image(image_info["filename"], new_name)
            if success:
                self.config_manager.update_custom_image_name(image_info["filename"], new_name)
                # 改为状态栏提示
                self.show_status_message(f"已重命名为: {new_name}", 2000)
                self.load_images()
            else:
                # 失败保留弹窗
                self.show_error_message("重命名失败", msg)
    
    def delete_image(self):
        """删除图片"""
        selected_items = self.image_list.selectedItems()
        if not selected_items:
            self.show_warning_message("未选择图片", "请先选择要删除的图片")
            return
        
        image_info = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        if image_info["type"] != "custom":
            self.show_warning_message("无法删除", "只能删除自定义图片")
            return
        
        # 注释掉二次确认
        # reply = QMessageBox.question(
        #     self, "删除图片",
        #     f"确定要删除图片 '{image_info['display_name']}' 吗?\n\n此操作不可恢复!",
        #     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        #     QMessageBox.StandardButton.No
        # )
        # 
        # if reply == QMessageBox.StandardButton.Yes:
        
        # 直接删除
        success = self.image_manager.delete_custom_image(image_info["filename"])
        if success:
            self.config_manager.remove_custom_image(image_info["filename"])
            # 改为状态栏提示
            self.show_status_message(f"已删除图片: {image_info['display_name']}", 2000)
            self.load_images()
        else:
            # 失败保留弹窗
            self.show_error_message("删除失败", "无法删除图片,请检查文件权限")
    
    def replace_startup_image(self):
        """替换启动图片"""
        if not self.target_path:
            self.show_warning_message("未检测到路径", "请先点击'检测路径'按钮")
            return
        
        selected_items = self.image_list.selectedItems()
        if not selected_items:
            self.show_warning_message("未选择图片", "请先从列表中选择要替换的图片")
            return
        
        image_info = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        # 注释掉二次确认
        # reply = QMessageBox.question(
        #     self, "确认替换",
        #     f"确定要将启动图片替换为:\n'{image_info['display_name']}' 吗?\n\n原始图片将自动备份。",
        #     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        #     QMessageBox.StandardButton.No
        # )
        # 
        # if reply == QMessageBox.StandardButton.No:
        #     return
        
        self.show_progress("正在替换...")
        
        success, msg = self.replacer.replace_image(image_info["path"], self.target_path)
        
        self.hide_progress()
        
        if success:
            self.show_status_message(f"启动图片已替换为: {image_info['display_name']}", 3000)
        else:
            self.show_error_message("替换失败", msg)
    
    def restore_from_backup(self):
        """从备份还原"""
        if not self.target_path:
            self.show_warning_message("未检测到路径", "请先点击'检测路径'按钮")
            return
        
        # 注释掉二次确认
        # reply = QMessageBox.question(
        #     self, "确认还原",
        #     "确定要从备份还原启动图片吗?\n\n当前的启动图片将被覆盖。",
        #     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        #     QMessageBox.StandardButton.No
        # )
        # 
        # if reply == QMessageBox.StandardButton.No:
        #     return
        
        self.show_progress("正在还原...")
        
        success, msg = self.replacer.restore_backup(self.target_path)
        
        self.hide_progress()
        
        if success:
            self.show_status_message("已从备份还原启动图片", 3000)
        else:
            self.show_error_message("还原失败", msg)
