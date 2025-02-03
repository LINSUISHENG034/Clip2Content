import asyncio
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, QComboBox,
    QLabel, QTextEdit, QSpinBox, QPushButton, QProgressBar,
    QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt

from text_summarization.processor import SummaryProcessor
from text_summarization.models import SummaryConfig, SummaryStyle
from text_summarization.exceptions import TextSummarizationError
from utils.logger.setup import get_logger

# 定义进度条样式
GOOD_STYLE = "QProgressBar::chunk { background-color: #4CAF50; }"
BAD_STYLE = "QProgressBar::chunk { background-color: #f44336; }"

class SummaryWorker(QThread):
    """Worker thread for summary generation"""
    finished = pyqtSignal(object)  # SummaryResult or Exception
    progress = pyqtSignal(float, str)  # progress value and status message

    def __init__(self, processor, text, config):
        super().__init__()
        self.processor = processor
        self.text = text
        self.config = config

    async def _generate(self):
        """Generate summary asynchronously"""
        return await self.processor.generate_summary(self.text, self.config)

    def run(self):
        """Run the worker thread"""
        try:
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._generate())
            loop.close()
            self.finished.emit(result)
        except Exception as e:
            self.finished.emit(e)

class SummaryTab(QWidget):
    def __init__(self):
        super().__init__()
        self.logger = get_logger("gui.summary_tab")
        self.processor = SummaryProcessor()
        self.current_worker = None
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout()
        
        # Style Selection
        style_group = QGroupBox("总结风格")
        style_layout = QVBoxLayout()
        
        self.style_combo = QComboBox()
        self.style_combo.addItems([
            style.value for style in SummaryStyle
        ])
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
        
        # 信息保留率
        retention_layout = QHBoxLayout()
        retention_layout.addWidget(QLabel("信息保留率:"))
        self.info_retention = QProgressBar()
        self.info_retention.setFormat("%p%")
        retention_layout.addWidget(self.info_retention)
        metrics_layout.addLayout(retention_layout)
        
        # 重复度
        redundancy_layout = QHBoxLayout()
        redundancy_layout.addWidget(QLabel("重复度:"))
        self.redundancy = QProgressBar()
        self.redundancy.setFormat("%p%")
        redundancy_layout.addWidget(self.redundancy)
        metrics_layout.addLayout(redundancy_layout)
        
        # 连贯性
        coherence_layout = QHBoxLayout()
        coherence_layout.addWidget(QLabel("连贯性:"))
        self.coherence = QProgressBar()
        self.coherence.setFormat("%p%")
        coherence_layout.addWidget(self.coherence)
        metrics_layout.addLayout(coherence_layout)
        
        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFormat("%p% - %v")
        layout.addWidget(self.progress_bar)
        
        # Control Buttons
        button_layout = QHBoxLayout()
        self.generate_button = QPushButton("生成总结")
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setEnabled(False)
        
        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.generate_button.clicked.connect(self.generate_summary)
        self.cancel_button.clicked.connect(self.cancel_generation)
        
        # 连接处理器的进度回调
        self.processor.set_progress_callback(self.update_progress)
    
    def update_progress(self, value: float, status: str):
        """Update progress bar"""
        self.progress_bar.setValue(int(value * 100))
        self.progress_bar.setFormat(f"{int(value * 100)}% - {status}")
    
    def update_metrics(self, result):
        """Update quality metrics display"""
        self.info_retention.setValue(int(result.metrics.info_retention * 100))
        self.redundancy.setValue(int(result.metrics.redundancy_score * 100))
        self.coherence.setValue(int(result.metrics.coherence_score * 100))
        
        # 设置进度条颜色
        self._set_progress_color(self.info_retention, result.metrics.info_retention >= 0.85)
        self._set_progress_color(self.redundancy, result.metrics.redundancy_score <= 0.2)
        self._set_progress_color(self.coherence, result.metrics.coherence_score >= 0.7)
    
    def _set_progress_color(self, progress_bar: QProgressBar, is_good: bool):
        """Set progress bar color based on value"""
        progress_bar.setStyleSheet(GOOD_STYLE if is_good else BAD_STYLE)
    
    def generate_summary(self):
        """Generate summary for current video result"""
        try:
            from gui.tabs.video_tab import VideoTab  # 避免循环导入
            
            # 获取视频处理结果
            main_window = self.window()
            video_tab = main_window.findChild(VideoTab)
            if not video_tab or not video_tab.current_result:
                QMessageBox.warning(
                    self,
                    "错误",
                    "请先在'视频处理'标签页处理视频并等待完成"
                )
                return
            
            # 准备配置
            style = SummaryStyle.from_display_name(self.style_combo.currentText())
            config = SummaryConfig(
                style=style,
                max_length=self.word_limit.value()
            )
            
            # 创建并启动工作线程
            self.current_worker = SummaryWorker(
                self.processor,
                video_tab.current_result.get_full_text(),
                config
            )
            self.current_worker.progress.connect(self.update_progress)
            self.current_worker.finished.connect(self.handle_result)
            
            # 更新UI状态
            self.generate_button.setEnabled(False)
            self.cancel_button.setEnabled(True)
            self.progress_bar.setValue(0)
            
            # 启动处理
            self.current_worker.start()
            
        except Exception as e:
            self.logger.error(f"生成总结失败：{str(e)}")
            QMessageBox.critical(self, "错误", f"生成总结失败：{str(e)}")
    
    def handle_result(self, result):
        """Handle summary generation result"""
        self.generate_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        
        if isinstance(result, Exception):
            QMessageBox.critical(self, "错误", f"生成总结失败：{str(result)}")
            return
        
        # 更新UI
        self.summary_text.setText(result.summary)
        self.update_metrics(result)
        
        # 显示警告（如果有）
        if result.metrics.warnings:
            QMessageBox.warning(
                self,
                "质量警告",
                "\n".join(result.metrics.warnings)
            )
    
    def cancel_generation(self):
        """Cancel ongoing summary generation"""
        if self.current_worker:
            self.processor.cancel_processing()
            self.current_worker.quit()
            self.current_worker = None
        
        self.generate_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("已取消")
