from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, QListWidget, QTextEdit, QLabel, QProgressBar, QPushButton, QComboBox

class ReviewTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Article List
        list_group = QGroupBox("待审核文章")
        list_layout = QVBoxLayout()
        
        self.article_list = QListWidget()
        list_layout.addWidget(self.article_list)
        
        # Filter Options
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("状态筛选:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["全部", "待审核", "已通过", "已驳回"])
        filter_layout.addWidget(self.status_filter)
        
        list_layout.addLayout(filter_layout)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # Version Comparison
        comparison_group = QGroupBox("版本对比")
        comparison_layout = QHBoxLayout()
        
        # Old Version
        old_version_layout = QVBoxLayout()
        old_version_layout.addWidget(QLabel("原始版本"))
        self.old_version = QTextEdit()
        self.old_version.setReadOnly(True)
        old_version_layout.addWidget(self.old_version)
        comparison_layout.addLayout(old_version_layout)
        
        # New Version
        new_version_layout = QVBoxLayout()
        new_version_layout.addWidget(QLabel("当前版本"))
        self.new_version = QTextEdit()
        self.new_version.setReadOnly(True)
        new_version_layout.addWidget(self.new_version)
        comparison_layout.addLayout(new_version_layout)
        
        comparison_group.setLayout(comparison_layout)
        layout.addWidget(comparison_group)
        
        # Review Details
        details_group = QGroupBox("审核详情")
        details_layout = QVBoxLayout()
        
        # Quality Metrics
        metrics_layout = QHBoxLayout()
        metrics_layout.addWidget(QLabel("信息保留率:"))
        self.retention_rate = QProgressBar()
        self.retention_rate.setFormat("%p%")
        metrics_layout.addWidget(self.retention_rate)
        
        details_layout.addLayout(metrics_layout)
        
        # Review Comments
        details_layout.addWidget(QLabel("审核意见"))
        self.review_comments = QTextEdit()
        details_layout.addWidget(self.review_comments)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        # Control Buttons
        button_layout = QHBoxLayout()
        self.approve_button = QPushButton("通过")
        self.reject_button = QPushButton("驳回")
        self.request_revision_button = QPushButton("请求修改")
        
        button_layout.addWidget(self.approve_button)
        button_layout.addWidget(self.reject_button)
        button_layout.addWidget(self.request_revision_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)