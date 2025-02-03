from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, 
                                    QLineEdit, QPushButton, QFileDialog, QProgressBar, 
                                    QLabel, QTextEdit, QComboBox, QSpinBox, QCheckBox,
                                    QMessageBox)
from PyQt6.QtCore import QThread, pyqtSignal
from pathlib import Path
import traceback
from video_processing.processor import VideoProcessor
from video_processing.exceptions import VideoProcessingError

class VideoProcessingThread(QThread):
    progress_updated = pyqtSignal(float, str)
    processing_finished = pyqtSignal(object)
    processing_error = pyqtSignal(str)

    def __init__(self, processor: VideoProcessor, video_path: str):
        super().__init__()
        self.processor = processor
        self.video_path = video_path

    def run(self):
        try:
            self.processor.set_progress_callback(
                lambda progress, status: self.progress_updated.emit(progress, status)
            )
            result = self.processor.process_video(self.video_path)
            self.processing_finished.emit(result)
        except Exception as e:
            self.processing_error.emit(str(e))
            traceback.print_exc()

class VideoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.processor = None
        self.processing_thread = None
        self.current_result = None  # 存储当前处理结果
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
        self.model_combo.setCurrentIndex(3)  # 设置默认选择为 'medium' (索引从0开始，'medium'是第四个)
        model_layout.addWidget(self.model_combo)
        options_layout.addLayout(model_layout)
        
        # CUDA Acceleration Option
        cuda_layout = QHBoxLayout()
        self.use_cuda = QCheckBox("使用CUDA加速")
        # 检查CUDA是否可用
        cuda_available = VideoProcessor.is_cuda_available()
        self.use_cuda.setEnabled(cuda_available)
        if not cuda_available:
            self.use_cuda.setToolTip("当前系统不支持CUDA加速")
        else:
            self.use_cuda.setToolTip("使用GPU加速处理（推荐）")
            self.use_cuda.setChecked(True)  # 如果CUDA可用，默认启用
        cuda_layout.addWidget(self.use_cuda)
        options_layout.addLayout(cuda_layout)
        
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
        self.start_button.clicked.connect(self.start_processing)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.cancel_processing)
        self.cancel_button.setEnabled(False)
        
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

    def start_processing(self):
        video_path = self.video_path.text()
        if not video_path:
            QMessageBox.warning(self, "错误", "请先选择视频文件")
            return
        
        if not Path(video_path).exists():
            QMessageBox.warning(self, "错误", "所选视频文件不存在")
            return

        # 创建处理器实例，传入CUDA选项
        self.processor = VideoProcessor(use_cuda=self.use_cuda.isChecked())
        
        # Update processor configuration based on UI settings
        self.processor.config['models']['whisper']['model_size'] = self.model_combo.currentText()
        self.processor.config['video_processing']['whisper']['confidence_threshold'] = self.confidence_threshold.value() / 100

        # Disable UI elements
        self.start_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.video_path.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.model_combo.setEnabled(False)
        self.confidence_threshold.setEnabled(False)
        self.auto_split.setEnabled(False)
        self.use_cuda.setEnabled(False)

        # Start processing in a separate thread
        self.processing_thread = VideoProcessingThread(self.processor, video_path)
        self.processing_thread.progress_updated.connect(self.update_progress)
        self.processing_thread.processing_finished.connect(self.processing_complete)
        self.processing_thread.processing_error.connect(self.processing_error)
        self.processing_thread.start()

    def cancel_processing(self):
        if self.processing_thread and self.processing_thread.isRunning():
            self.processor.cancel_processing()
            self.cancel_button.setEnabled(False)
            self.status_label.setText("正在取消...")

    def update_progress(self, progress: float, status: str):
        self.progress_bar.setValue(int(progress * 100))
        self.status_label.setText(status)

    def processing_complete(self, result):
        # Save the result
        self.current_result = result
        
        # Re-enable UI elements
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.video_path.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.model_combo.setEnabled(True)
        self.confidence_threshold.setEnabled(True)
        self.auto_split.setEnabled(True)
        self.use_cuda.setEnabled(VideoProcessor.is_cuda_available())

        # Display results
        self.transcription_text.setText(result.get_full_text())
        
        # Show warnings if any
        if result.has_warnings():
            QMessageBox.warning(
                self,
                "处理完成（有警告）",
                f"视频处理已完成，但存在以下警告：\n\n" + "\n".join(result.warnings)
            )
        else:
            QMessageBox.information(
                self,
                "处理完成",
                f"视频处理已完成！\n\n"
                f"SRT文件保存至：{result.srt_path}\n"
                f"文本文件保存至：{result.text_path}"
            )

    def processing_error(self, error_msg: str):
        # Clear current result
        self.current_result = None
        
        # Re-enable UI elements
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.video_path.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.model_combo.setEnabled(True)
        self.confidence_threshold.setEnabled(True)
        self.auto_split.setEnabled(True)
        self.use_cuda.setEnabled(VideoProcessor.is_cuda_available())

        # Reset progress
        self.progress_bar.setValue(0)
        self.status_label.setText("处理失败")

        # Show error message
        QMessageBox.critical(self, "错误", f"处理视频时发生错误：\n{error_msg}")