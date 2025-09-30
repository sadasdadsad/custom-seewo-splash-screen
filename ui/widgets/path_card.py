import os
from PyQt6.QtWidgets import QHBoxLayout
from qfluentwidgets import CardWidget, StrongBodyLabel, PushButton, FluentIcon as FIF


class PathInfoCard(CardWidget):
    """路径信息卡片组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        
        # 路径标签
        self.path_label = StrongBodyLabel()
        self.path_label.setWordWrap(True)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        self.detect_button = PushButton(FIF.SEARCH, "检测路径")
        self.detect_button.setToolTip("自动检测希沃白板启动图片路径")
        
        self.history_button = PushButton(FIF.HISTORY, "历史路径")
        self.history_button.setToolTip("查看和选择历史路径")
        
        button_layout.addWidget(self.detect_button)
        button_layout.addWidget(self.history_button)
        
        layout.addWidget(self.path_label, 1)
        layout.addLayout(button_layout)
    
    def update_path_display(self, path: str):
        """更新路径显示
        
        Args:
            path: 目标路径,空字符串表示未设置路径
        """
        if path:
            # 缩短路径显示
            path_parts = path.split(os.sep)
            if len(path_parts) > 3:
                short_path = "..." + os.sep + os.sep.join(path_parts[-3:])
            else:
                short_path = path
            
            self.path_label.setText(f"✓ 当前路径: {short_path}")
            self.path_label.setToolTip(f"完整路径:\n{path}")
        else:
            self.path_label.setText("⚠ 未检测到启动图片路径 (点击右侧按钮进行检测)")
            self.path_label.setToolTip("请点击'检测路径'或'历史路径'按钮")
