import os
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QListWidgetItem, QSizePolicy
from qfluentwidgets import ListWidget


class ImageListWidget(ListWidget):
    """图片列表组件"""
    
    imageSelected = pyqtSignal(dict)  # 发出选中图片信息的信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self.itemSelectionChanged.connect(self._on_selection_changed)
    
    def _init_ui(self):
        """初始化UI"""
        # 设置图标尺寸
        self.setIconSize(QSize(140, 140))
        
        # 设置网格尺寸
        self.setGridSize(QSize(180, 200))
        
        # 设置间距
        self.setSpacing(15)
        
        # 设置视图模式
        self.setViewMode(ListWidget.ViewMode.IconMode)
        self.setResizeMode(ListWidget.ResizeMode.Adjust)
        self.setMovement(ListWidget.Movement.Static)
        self.setWrapping(True)
        
        # 设置选择模式
        self.setSelectionMode(ListWidget.SelectionMode.SingleSelection)
        
        # 设置固定行高
        self.setUniformItemSizes(True)
        
        # 设置最小尺寸
        self.setMinimumHeight(450)
        self.setMinimumWidth(400)
        
        # 设置尺寸策略
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
    
    def load_images(self, preset_images: list, custom_images: list):
        """加载图片列表
        
        Args:
            preset_images: 预设图片列表
            custom_images: 自定义图片列表
        """
        self.clear()
        all_images = preset_images + custom_images
        
        for img_info in all_images:
            item = QListWidgetItem(img_info["display_name"])
            
            # 加载并设置图标
            if os.path.exists(img_info["path"]):
                pixmap = QPixmap(img_info["path"])
                if not pixmap.isNull():
                    # 缩放图片
                    scaled_pixmap = pixmap.scaled(
                        140, 140,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    item.setIcon(QIcon(scaled_pixmap))
            
            item.setData(Qt.ItemDataRole.UserRole, img_info)
            
            # 设置工具提示
            img_type = '预设' if img_info['type'] == 'preset' else '自定义'
            item.setToolTip(f"类型: {img_type}\n文件名: {img_info['filename']}")
            
            # 设置文本对齐
            item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            
            # 设置固定尺寸提示
            item.setSizeHint(QSize(180, 200))
            
            self.addItem(item)
    
    def get_selected_image_info(self):
        """获取选中的图片信息
        
        Returns:
            dict or None: 选中的图片信息字典,未选中返回None
        """
        items = self.selectedItems()
        return items[0].data(Qt.ItemDataRole.UserRole) if items else None
    
    def select_image_by_filename(self, filename: str):
        """根据文件名选中图片
        
        Args:
            filename: 要选中的图片文件名
        """
        for i in range(self.count()):
            item = self.item(i)
            if item.data(Qt.ItemDataRole.UserRole)["filename"] == filename:
                self.setCurrentItem(item)
                self.scrollToItem(item)
                break
    
    def _on_selection_changed(self):
        """选择改变时触发"""
        info = self.get_selected_image_info()
        if info:
            self.imageSelected.emit(info)
