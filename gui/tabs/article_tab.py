from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, QComboBox, QLabel, QTextEdit, QCheckBox, QSpinBox, QPushButton

class ArticleTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Template Selection
        template_group = QGroupBox("模板选择")
        template_layout = QHBoxLayout()
        
        self.template_combo = QComboBox()
        self.template_combo.addItems(["基础模板", "图文模板", "视频号模板", "专题模板"])
        template_layout.addWidget(self.template_combo)
        
        template_group.setLayout(template_layout)
        layout.addWidget(template_group)
        
        # Article Preview
        preview_group = QGroupBox("文章预览")
        preview_layout = QVBoxLayout()
        
        self.article_preview = QTextEdit()
        self.article_preview.setReadOnly(True)
        self.article_preview.setPlaceholderText("文章预览将在这里显示...")
        
        preview_layout.addWidget(self.article_preview)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Components
        components_group = QGroupBox("组件配置")
        components_layout = QVBoxLayout()
        
        self.add_qrcode = QCheckBox("添加二维码")
        self.add_header = QCheckBox("添加头图")
        self.add_qrcode.setChecked(True)
        self.add_header.setChecked(True)
        
        components_layout.addWidget(self.add_qrcode)
        components_layout.addWidget(self.add_header)
        
        # Format Settings
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("段落长度限制:"))
        self.paragraph_limit = QSpinBox()
        self.paragraph_limit.setRange(100, 1000)
        self.paragraph_limit.setValue(500)
        format_layout.addWidget(self.paragraph_limit)
        format_layout.addWidget(QLabel("字符"))
        
        components_layout.addLayout(format_layout)
        components_group.setLayout(components_layout)
        layout.addWidget(components_group)
        
        # Control Buttons
        button_layout = QHBoxLayout()
        self.preview_button = QPushButton("预览")
        self.save_button = QPushButton("保存")
        
        button_layout.addWidget(self.preview_button)
        button_layout.addWidget(self.save_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)