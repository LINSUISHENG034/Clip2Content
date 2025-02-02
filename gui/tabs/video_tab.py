from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, QLineEdit, QPushButton, QFileDialog, QProgressBar, QLabel, QTextEdit, QComboBox, QSpinBox, QCheckBox

class VideoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Video Input Section
        input_group = QGroupBox("视频输入")
        input_layout = QHBoxLayout()
        
        self.video_path = QLineEdit()
        self.video_path.setPlaceholderText("选择视频文件...")
        self.browse_button = QPushButton("浏览")
        self.browse_button.clicked.connect(self.browse_video)
        
        input_layout.addWidget(self.video_path)
        input_layout.addWidget(self.browse_button)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Processing Options
        options_group = QGroupBox("处理选项")
        options_layout = QVBoxLayout()
        
        # Whisper Model Selection
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Whisper模型:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium", "large-v2"])
        model_layout.addWidget(self.model_combo)
        options_layout.addLayout(model_layout)
        
        self.auto_split = QCheckBox("自动分段处理")
        self.auto_split.setChecked(True)
        options_layout.addWidget(self.auto_split)
        
        self.confidence_threshold = QSpinBox()
        self.confidence_threshold.setRange(0, 100)
        self.confidence_threshold.setValue(60)
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("置信度阈值:"))
        threshold_layout.addWidget(self.confidence_threshold)
        threshold_layout.addWidget(QLabel("%"))
        options_layout.addLayout(threshold_layout)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Progress Section
        progress_group = QGroupBox("处理进度")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.status_label = QLabel("就绪")
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Results Section
        results_group = QGroupBox("处理结果")
        results_layout = QVBoxLayout()
        
        self.transcription_text = QTextEdit()
        self.transcription_text.setReadOnly(True)
        self.transcription_text.setPlaceholderText("字幕将在这里显示...")
        
        results_layout.addWidget(self.transcription_text)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        # Control Buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("开始处理")
        self.cancel_button = QPushButton("取消")
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def browse_video(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择视频文件",
            "",
            "Video Files (*.mp4 *.avi *.mkv);;All Files (*)"
        )
        if file_name:
            self.video_path.setText(file_name)