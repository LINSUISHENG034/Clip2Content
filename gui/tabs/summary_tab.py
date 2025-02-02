from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, QComboBox, QLabel, QTextEdit, QSpinBox, QPushButton, QProgressBar

class SummaryTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Style Selection
        style_group = QGroupBox("总结风格")
        style_layout = QVBoxLayout()
        
        self.style_combo = QComboBox()
        self.style_combo.addItems(["学术风格", "新闻风格", "技术博客", "科普文章", "营销文案"])
        style_layout.addWidget(self.style_combo)
        
        # Style Parameters
        params_layout = QHBoxLayout()
        params_layout.addWidget(QLabel("字数限制:"))
        self.word_limit = QSpinBox()
        self.word_limit.setRange(100, 5000)
        self.word_limit.setValue(300)
        params_layout.addWidget(self.word_limit)
        
        style_layout.addLayout(params_layout)
        style_group.setLayout(style_layout)
        layout.addWidget(style_group)
        
        # Summary Content
        content_group = QGroupBox("总结内容")
        content_layout = QVBoxLayout()
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setPlaceholderText("总结内容将在这里显示...")
        
        content_layout.addWidget(self.summary_text)
        content_group.setLayout(content_layout)
        layout.addWidget(content_group)
        
        # Quality Metrics
        metrics_group = QGroupBox("质量指标")
        metrics_layout = QVBoxLayout()
        
        self.info_retention = QProgressBar()
        self.info_retention.setFormat("信息保留率: %p%")
        metrics_layout.addWidget(self.info_retention)
        
        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)
        
        # Control Buttons
        button_layout = QHBoxLayout()
        self.generate_summary_button = QPushButton("生成总结")
        self.regenerate_button = QPushButton("重新生成")
        
        button_layout.addWidget(self.generate_summary_button)
        button_layout.addWidget(self.regenerate_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
