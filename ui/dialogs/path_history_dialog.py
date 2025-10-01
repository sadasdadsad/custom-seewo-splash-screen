# import os
from PyQt6.QtWidgets import QMessageBox, QInputDialog
from utils.path_detector import PathDetector
# from .message_helper import MessageHelper


class PathHistoryDialog:
    """历史路径对话框辅助类"""
    
    @staticmethod
    def show_and_select(parent, config_manager) -> tuple[str, bool]:
        """显示历史路径对话框并选择路径
        
        Args:
            parent: 父窗口
            config_manager: 配置管理器实例
            
        Returns:
            tuple: (选择的路径, 是否成功选择)
        """
        history = config_manager.get_path_history()
        
        if not history:
            QMessageBox.information(
                parent,
                "无历史记录",
                "暂无历史路径记录。\n\n请点击'检测路径'按钮检测启动图片路径。"
            )
            return "", False
        
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
                parent,
                "所有历史路径均无效",
                "历史记录中的所有路径都已失效。\n\n是否清理历史记录并重新检测?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                config_manager.clear_invalid_history()
                return "", False
            return "", False
        
        item, ok = QInputDialog.getItem(
            parent,
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
                return selected_path, True
            else:
                QMessageBox.warning(
                    parent,
                    "路径无效",
                    f"选择的路径已失效:\n{error_msg}\n\n请选择其他路径或重新检测。"
                )
                return "", False
        
        return "", False
