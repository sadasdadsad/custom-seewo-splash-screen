# ui/dialogs/path_history_dialog.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from qfluentwidgets import (
    Dialog, MessageBox,
    BodyLabel, StrongBodyLabel, PushButton, 
    PrimaryPushButton, TransparentPushButton,
    ListWidget, FluentIcon
)
from utils.path_detector import PathDetector
from .message_helper import MessageHelper


class PathItemWidget(QWidget):
    """历史路径项组件"""
    
    def __init__(self, index: int, path: str, is_valid: bool, error_msg: str = "", parent=None):
        super().__init__(parent)
        self.path = path
        self.is_valid = is_valid
        self._init_ui(index, path, is_valid, error_msg)
    
    def _init_ui(self, index: int, path: str, is_valid: bool, error_msg: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        # 第一行：序号 + 状态
        top_layout = QHBoxLayout()
        
        # 序号标签
        index_label = BodyLabel(f"#{index}", self)
        index_label.setStyleSheet("color: #888; font-weight: bold;")
        top_layout.addWidget(index_label)
        
        # 状态标签
        if is_valid:
            status_label = BodyLabel("✓ 有效", self)
            status_label.setStyleSheet("color: #10b981; font-weight: 500;")
        else:
            status_label = BodyLabel("✗ 无效", self)
            status_label.setStyleSheet("color: #ef4444; font-weight: 500;")
        top_layout.addWidget(status_label)
        
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # 第二行：路径
        path_label = BodyLabel(path, self)
        path_label.setWordWrap(True)
        if not is_valid:
            path_label.setStyleSheet("color: #888;")
        layout.addWidget(path_label)
        
        # 第三行：错误信息（如果有）
        if not is_valid and error_msg:
            error_label = BodyLabel(f"原因: {error_msg}", self)
            error_label.setStyleSheet("color: #f59e0b; font-size: 12px;")
            layout.addWidget(error_label)


class PathHistoryDialog(Dialog):
    """历史路径选择对话框"""
    
    pathSelected = pyqtSignal(str)
    
    def __init__(self, config_manager, parent=None):
        super().__init__(
            title="历史路径",
            content="",
            parent=parent
        )
        self.config_manager = config_manager
        self.parent_window = parent
        self.selected_path = ""
        
        self.setFixedWidth(600)
        self._init_ui()
        self._load_history()
    
    def _init_ui(self):
        """初始化UI"""
        # 创建自定义内容区域
        content_widget = QWidget(self)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)
        
        # 说明文字
        self.info_label = StrongBodyLabel("", content_widget)
        content_layout.addWidget(self.info_label)
        
        # 路径列表
        self.list_widget = ListWidget(content_widget)
        self.list_widget.setMinimumHeight(300)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        content_layout.addWidget(self.list_widget)
        
        # 替换对话框的内容区域
        # Dialog 使用 textLayout 来放置内容文本
        # 我们需要在 textLayout 之前插入自定义内容
        try:
            # 尝试获取正确的布局
            if hasattr(self, 'textLayout'):
                # 隐藏原有的文本布局
                for i in range(self.textLayout.count()):
                    item = self.textLayout.itemAt(i)
                    if item and item.widget():
                        item.widget().setVisible(False)
                
                # 在正确的位置插入内容
                # 查找主布局
                main_layout = self.layout()
                if main_layout:
                    # 在标题和按钮之间插入内容
                    main_layout.insertWidget(1, content_widget)
            else:
                # 如果没有 textLayout,直接添加到主布局
                main_layout = self.layout()
                if main_layout:
                    main_layout.insertWidget(1, content_widget)
        except Exception as e:
            print(f"布局设置警告: {e}")
            # 兜底方案：直接设置为对话框的中心部件
            pass
        
        # 自定义按钮
        self.yesButton.setText("使用选中路径")
        self.yesButton.setEnabled(False)
        self.cancelButton.setText("取消")
        
        # 添加清理按钮
        self.clearButton = TransparentPushButton(FluentIcon.DELETE, "清理无效路径", self)
        self.clearButton.clicked.connect(self._on_clear_invalid)
        
        # 将清理按钮添加到按钮组
        if hasattr(self, 'buttonGroup') and hasattr(self.buttonGroup, 'insertWidget'):
            self.buttonGroup.insertWidget(0, self.clearButton)
        elif hasattr(self, 'buttonLayout'):
            self.buttonLayout.insertWidget(0, self.clearButton)
    
    def _load_history(self):
        """加载历史路径"""
        history = self.config_manager.get_path_history()
        
        if not history:
            self._show_empty_state()
            return
        
        # 验证并显示路径
        valid_count = 0
        for i, path in enumerate(history, 1):
            is_valid, error_msg = PathDetector.validate_target_path(path)
            if is_valid:
                valid_count += 1
            
            # 创建路径项
            item_widget = PathItemWidget(i, path, is_valid, error_msg)
            
            # 添加到列表
            from PyQt6.QtWidgets import QListWidgetItem
            item = QListWidgetItem(self.list_widget)
            item.setSizeHint(item_widget.sizeHint())
            item.setData(Qt.ItemDataRole.UserRole, path)
            item.setData(Qt.ItemDataRole.UserRole + 1, is_valid)
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, item_widget)
        
        # 更新说明文字
        self.info_label.setText(
            f"共有 {len(history)} 条历史记录,其中 {valid_count} 条有效"
        )
        
        # 如果没有有效路径,显示警告
        if valid_count == 0:
            self._show_all_invalid_state()
    
    def _show_empty_state(self):
        """显示空状态"""
        self.info_label.setText("暂无历史路径记录")
        
        empty_label = BodyLabel(
            "尚未保存任何路径。\n\n"
            "请先使用「检测路径」功能来自动检测希沃白板安装路径。",
            self
        )
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_label.setStyleSheet("color: #888; padding: 40px;")
        
        self.list_widget.setVisible(False)
        
        # 将空状态标签添加到列表位置
        self.list_widget.parent().layout().addWidget(empty_label)
        
        self.yesButton.setEnabled(False)
        self.clearButton.setEnabled(False)
    
    def _show_all_invalid_state(self):
        """所有路径都无效的状态"""
        self.yesButton.setEnabled(False)
        
        # 使用 MessageHelper 显示警告
        MessageHelper.show_warning(
            self.parent_window,
            "所有路径均无效",
            "历史记录中的所有路径都已失效,建议清理"
        )
    
    def _on_item_clicked(self, item):
        """列表项点击事件"""
        is_valid = item.data(Qt.ItemDataRole.UserRole + 1)
        self.yesButton.setEnabled(is_valid)
        
        if is_valid:
            self.selected_path = item.data(Qt.ItemDataRole.UserRole)
    
    def _on_item_double_clicked(self, item):
        """列表项双击事件"""
        is_valid = item.data(Qt.ItemDataRole.UserRole + 1)
        if is_valid:
            self.selected_path = item.data(Qt.ItemDataRole.UserRole)
            self.accept()
    
    def _on_clear_invalid(self):
        """清理无效路径"""
        # 统计无效路径数量
        invalid_count = sum(
            1 for i in range(self.list_widget.count())
            if not self.list_widget.item(i).data(Qt.ItemDataRole.UserRole + 1)
        )
        
        if invalid_count == 0:
            MessageHelper.show_warning(
                self.parent_window,
                "无需清理",
                "当前所有历史路径都是有效的"
            )
            return
        
        # 确认对话框
        w = MessageBox(
            "确认清理",
            f"将清理 {invalid_count} 条无效的历史路径记录\n\n此操作不可恢复,是否继续?",
            self
        )
        w.yesButton.setText("清理")
        w.cancelButton.setText("取消")
        
        if w.exec():
            self.config_manager.clear_invalid_history()
            
            # 使用 MessageHelper 显示成功消息
            MessageHelper.show_success(
                self.parent_window,
                f"已清理 {invalid_count} 条无效路径"
            )
            
            # 重新加载
            self.list_widget.clear()
            self._load_history()
    
    def get_selected_path(self) -> str:
        """获取选中的路径"""
        return self.selected_path


class PathHistoryHelper:
    """历史路径对话框辅助类 - 保持向后兼容"""
    
    @staticmethod
    def show_and_select(parent, config_manager) -> tuple[str, bool]:
        """显示历史路径对话框并选择路径
        
        Args:
            parent: 父窗口
            config_manager: 配置管理器实例
            
        Returns:
            tuple: (选择的路径, 是否成功选择)
        """
        # 检查是否有历史记录
        history = config_manager.get_path_history()
        
        if not history:
            MessageBox(
                "无历史记录",
                "暂无历史路径记录。\n\n请点击「检测路径」按钮检测启动图片路径。",
                parent
            ).exec()
            return "", False
        
        # 显示对话框
        dialog = PathHistoryDialog(config_manager, parent)
        
        if dialog.exec():
            selected_path = dialog.get_selected_path()
            
            if selected_path:
                # 再次验证路径
                is_valid, error_msg = PathDetector.validate_target_path(selected_path)
                
                if is_valid:
                    # 使用 MessageHelper 显示成功消息
                    MessageHelper.show_success(
                        parent,
                        f"已选择路径: {selected_path}"
                    )
                    return selected_path, True
                else:
                    # 使用 MessageHelper 显示错误消息
                    MessageHelper.show_error(
                        parent,
                        "路径无效",
                        f"选择的路径已失效: {error_msg}\n\n请选择其他路径或重新检测。"
                    )
                    return "", False
        
        return "", False
