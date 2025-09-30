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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("希沃白板启动图片修改器")
        # self.setWindowIcon(QIcon("assets/icon.png"))  # 如果没有图标文件可以先注释掉
        self.setMinimumSize(800, 600)
        
        self.config_manager = ConfigManager()
        self.image_manager = ImageManager()
        self.replacer = ImageReplacer()
        
        self.target_path = self.config_manager.get_target_path()
        
        self.init_ui()
        self.load_images()
        
        if not self.target_path:
            self.detect_target_path()
    
    def init_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        # 顶部信息区域
        info_layout = QHBoxLayout()
        self.target_label = QLabel()
        self.target_label.setStyleSheet("font-weight: bold; padding: 10px;")
        self.target_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.detect_button = QPushButton("检测路径")
        self.detect_button.setMinimumHeight(30)
        self.detect_button.clicked.connect(self.detect_target_path)
        info_layout.addWidget(self.target_label, 1)
        info_layout.addWidget(self.detect_button)
        
        # 更新目标路径标签显示
        self.update_target_label()
        
        # 中间图片列表区域
        self.image_list = QListWidget()
        self.image_list.setIconSize(QSize(128, 128))
        self.image_list.setSpacing(5)
        self.image_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.image_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.image_list.setMovement(QListWidget.Movement.Static)
        self.image_list.itemSelectionChanged.connect(self.on_image_selected)
        
        # 底部操作区域
        bottom_layout = QHBoxLayout()
        self.import_button = QPushButton("导入图片")
        self.import_button.setMinimumHeight(35)
        self.import_button.clicked.connect(self.import_image)
        
        self.rename_button = QPushButton("重命名")
        self.rename_button.setMinimumHeight(35)
        self.rename_button.clicked.connect(self.rename_image)
        
        self.delete_button = QPushButton("删除")
        self.delete_button.setMinimumHeight(35)
        self.delete_button.clicked.connect(self.delete_image)
        
        self.replace_button = QPushButton("替换启动图片")
        self.replace_button.setMinimumHeight(35)
        self.replace_button.setStyleSheet("background-color: #0078D4; color: white; font-weight: bold;")
        self.replace_button.clicked.connect(self.replace_startup_image)
        
        self.restore_button = QPushButton("从备份还原")
        self.restore_button.setMinimumHeight(35)
        self.restore_button.clicked.connect(self.restore_from_backup)
        
        bottom_layout.addWidget(self.import_button)
        bottom_layout.addWidget(self.rename_button)
        bottom_layout.addWidget(self.delete_button)
        bottom_layout.addWidget(self.replace_button)
        bottom_layout.addWidget(self.restore_button)
        
        # 进度条 - 使用PyQt6原生的QProgressBar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setVisible(False)
        
        layout.addLayout(info_layout)
        layout.addWidget(self.image_list)
        layout.addLayout(bottom_layout)
        layout.addWidget(self.progress_bar)
    
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
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        
        paths = PathDetector.detect_all_paths()
        
        self.progress_bar.setVisible(False)
        
        if paths:
            self.target_path = paths[0]
            self.config_manager.set_target_path(self.target_path)
            self.update_target_label()
            QMessageBox.information(
                self, "检测成功", 
                f"已检测到启动图片路径:\n{self.target_path}"
            )
        else:
            self.target_path = ""
            self.config_manager.set_target_path("")
            self.update_target_label()
            QMessageBox.warning(
                self, "未检测到启动图片路径",
                "未能自动检测到希沃白板的启动图片路径。\n\n可能的原因：\n1. 希沃白板未安装\n2. 安装路径非标准路径\n3. 权限不足\n\n建议手动指定路径或联系技术支持。"
            )
    
    def update_target_label(self):
        """更新目标路径标签"""
        if self.target_path:
            self.target_label.setText(f"当前启动图片路径: {self.target_path}")
            self.target_label.setStyleSheet("font-weight: bold; padding: 10px; color: green;")
        else:
            self.target_label.setText("未检测到启动图片路径 (点击右侧按钮进行检测)")
            self.target_label.setStyleSheet("font-weight: bold; padding: 10px; color: red;")
    
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
                
                self.progress_bar.setVisible(True)
                self.progress_bar.setRange(0, 0)
                
                success, msg = self.image_manager.import_image(source_path)
                
                self.progress_bar.setVisible(False)
                
                if success:
                    QMessageBox.information(self, "导入成功", f"图片已导入到自定义目录:\n{msg}")
                    self.load_images()
                else:
                    QMessageBox.warning(self, "导入失败", msg)
    
    def rename_image(self):
        """重命名图片"""
        selected_items = self.image_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "未选择图片", "请先选择要重命名的图片")
            return
        
        image_info = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        if image_info["type"] != "custom":
            QMessageBox.warning(self, "无法重命名", "只能重命名自定义图片")
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
                QMessageBox.information(self, "重命名成功", f"已重命名为: {new_name}")
                self.load_images()
            else:
                QMessageBox.warning(self, "重命名失败", msg)
    
    def delete_image(self):
        """删除图片"""
        selected_items = self.image_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "未选择图片", "请先选择要删除的图片")
            return
        
        image_info = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        if image_info["type"] != "custom":
            QMessageBox.warning(self, "无法删除", "只能删除自定义图片")
            return
        
        reply = QMessageBox.question(
            self, "删除图片",
            f"确定要删除图片 '{image_info['display_name']}' 吗？\n\n此操作不可恢复！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success = self.image_manager.delete_custom_image(image_info["filename"])
            if success:
                self.config_manager.remove_custom_image(image_info["filename"])
                QMessageBox.information(self, "删除成功", "图片已删除")
                self.load_images()
            else:
                QMessageBox.warning(self, "删除失败", "无法删除图片，请检查文件权限")
    
    def replace_startup_image(self):
        """替换启动图片"""
        if not self.target_path:
            QMessageBox.warning(
                self, "未检测到启动图片路径", 
                "请先点击'检测路径'按钮检测启动图片路径"
            )
            return
        
        selected_items = self.image_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "未选择图片", "请先从列表中选择要替换的图片")
            return
        
        image_info = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        # 确认对话框
        reply = QMessageBox.question(
            self, "确认替换",
            f"确定要将启动图片替换为:\n'{image_info['display_name']}' 吗？\n\n原始图片将自动备份。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFormat("正在替换...")
        
        success, msg = self.replacer.replace_image(image_info["path"], self.target_path)
        
        self.progress_bar.setVisible(False)
        
        if success:
            QMessageBox.information(self, "替换成功", msg)
        else:
            QMessageBox.critical(self, "替换失败", msg)
    
    def restore_from_backup(self):
        """从备份还原"""
        if not self.target_path:
            QMessageBox.warning(
                self, "未检测到启动图片路径", 
                "请先点击'检测路径'按钮检测启动图片路径"
            )
            return
        
        # 确认对话框
        reply = QMessageBox.question(
            self, "确认还原",
            "确定要从备份还原启动图片吗？\n\n当前的启动图片将被覆盖。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFormat("正在还原...")
        
        success, msg = self.replacer.restore_backup(self.target_path)
        
        self.progress_bar.setVisible(False)
        
        if success:
            QMessageBox.information(self, "还原成功", msg)
        else:
            QMessageBox.critical(self, "还原失败", msg)
