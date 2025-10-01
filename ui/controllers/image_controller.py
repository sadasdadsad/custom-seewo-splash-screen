"""图片操作控制器 - 处理所有图片相关的业务逻辑"""

import os
from PyQt6.QtWidgets import QWidget, QFileDialog, QInputDialog
from core.config_manager import ConfigManager
from core.image_manager import ImageManager


class ImageController:
    """图片操作控制器"""
    
    def __init__(self, parent: QWidget, config_manager: ConfigManager, 
                 image_manager: ImageManager):
        self.parent = parent
        self.config_manager = config_manager
        self.image_manager = image_manager
    
    def import_single_image(self) -> tuple[bool, str, str]:
        """导入单个图片
        
        Returns:
            (成功标志, 消息, 文件路径)
        """
        file_dialog = QFileDialog(self.parent, "选择PNG图片", os.path.expanduser("~"))
        file_dialog.setNameFilter("PNG图片 (*.png)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                source_path = selected_files[0]
                success, msg = self.image_manager.import_image(source_path)
                return success, msg, source_path
        
        return False, "", ""
    
    def import_multiple_images(self, file_paths: list[str]) -> tuple[int, list]:
        """批量导入图片
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            (成功数量, 失败文件列表[(文件名, 错误信息)])
        """
        success_count = 0
        failed_files = []
        
        for file_path in file_paths:
            success, msg = self.image_manager.import_image(file_path)
            if success:
                success_count += 1
            else:
                failed_files.append((os.path.basename(file_path), msg))
        
        return success_count, failed_files
    
    def rename_image(self, image_info: dict) -> tuple[bool, str]:
        """重命名图片
        
        Args:
            image_info: 图片信息
            
        Returns:
            (成功标志, 消息)
        """
        if image_info["type"] != "custom":
            return False, "只能重命名自定义图片"
        
        new_name, ok = QInputDialog.getText(
            self.parent, "重命名图片",
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
                return True, f"已重命名为: {new_name}"
            return False, msg
        
        return False, ""
    
    def delete_image(self, image_info: dict) -> tuple[bool, str]:
        """删除图片
        
        Args:
            image_info: 图片信息
            
        Returns:
            (成功标志, 消息)
        """
        if image_info["type"] != "custom":
            return False, "只能删除自定义图片"
        
        success = self.image_manager.delete_custom_image(image_info["filename"])
        if success:
            self.config_manager.remove_custom_image(image_info["filename"])
            return True, f"已删除图片: {image_info['display_name']}"
        
        return False, "无法删除图片,请检查文件权限"
