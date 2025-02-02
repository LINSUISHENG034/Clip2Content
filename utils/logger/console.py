import logging
import sys
from datetime import datetime
from typing import Optional, List
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
                           QPushButton, QComboBox, QLabel, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QTextCursor, QColor, QTextCharFormat

class LogStream(QObject):
    """自定义日志流，用于将日志重定向到QTextEdit"""
    log_received = pyqtSignal(str, str)  # (消息, 级别)

    def __init__(self):
        super().__init__()
        self.buffer = []

    def write(self, text: str):
        """写入日志文本"""
        if text and text.strip():
            # 尝试解析日志级别
            level = "INFO"  # 默认级别
            for level_name in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                if level_name in text:
                    level = level_name
                    break
            self.log_received.emit(text.strip(), level)

    def flush(self):
        """刷新缓冲区"""
        pass

class LogWindow(QWidget):
    """独立的日志窗口"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("应用日志")
        self.setGeometry(100, 100, 800, 600)

        # 设置窗口标志
        self.setWindowFlags(Qt.WindowType.Window)

        self.init_ui()
        self.setup_log_handler()

    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()

        # 控制区域
        control_layout = QHBoxLayout()

        # 日志级别选择
        self.level_combo = QComboBox()
        self.level_combo.addItems(['ALL', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
        self.level_combo.currentTextChanged.connect(self.filter_logs)
        control_layout.addWidget(QLabel("日志级别:"))
        control_layout.addWidget(self.level_combo)

        # 清除按钮
        clear_button = QPushButton("清除")
        clear_button.clicked.connect(self.clear_logs)
        control_layout.addWidget(clear_button)

        # 导出按钮
        export_button = QPushButton("导出")
        export_button.clicked.connect(self.export_logs)
        control_layout.addWidget(export_button)

        control_layout.addStretch()
        layout.addLayout(control_layout)

        # 日志显示区域
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self.log_display)

        self.setLayout(layout)

        # 存储所有日志
        self.all_logs: List[tuple] = []  # [(text, level), ...]

    def setup_log_handler(self):
        """设置日志处理器"""
        self.log_stream = LogStream()
        self.log_stream.log_received.connect(self.append_log)

    def append_log(self, text: str, level: str):
        """添加日志到显示区域"""
        self.all_logs.append((text, level))

        # 检查是否需要根据当前过滤显示
        if self.level_combo.currentText() == 'ALL' or level == self.level_combo.currentText():
            cursor = self.log_display.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)

            # 设置颜色
            format = QTextCharFormat()
            color = self.get_level_color(level)
            format.setForeground(color)

            cursor.insertText(f"{text}\n", format)
            self.log_display.setTextCursor(cursor)
            self.log_display.ensureCursorVisible()

    def get_level_color(self, level: str) -> QColor:
        """获取日志级别对应的颜色"""
        colors = {
            'DEBUG': QColor(0, 150, 150),    # 青色
            'INFO': QColor(0, 150, 0),       # 绿色
            'WARNING': QColor(150, 150, 0),  # 黄色
            'ERROR': QColor(150, 0, 0),      # 红色
            'CRITICAL': QColor(150, 0, 150)  # 紫色
        }
        return colors.get(level, QColor(0, 0, 0))  # 默认黑色

    def filter_logs(self, level: str):
        """根据级别过滤日志"""
        self.log_display.clear()
        for text, log_level in self.all_logs:
            if level == 'ALL' or log_level == level:
                cursor = self.log_display.textCursor()
                format = QTextCharFormat()
                format.setForeground(self.get_level_color(log_level))
                cursor.insertText(f"{text}\n", format)

    def clear_logs(self):
        """清除所有日志"""
        self.all_logs.clear()
        self.log_display.clear()

    def export_logs(self):
        """导出日志到文件"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "导出日志",
            f"log_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    for text, _ in self.all_logs:
                        f.write(f"{text}\n")
            except Exception as e:
                self.append_log(f"导出日志失败: {str(e)}", "ERROR")

    def closeEvent(self, event):
        """窗口关闭事件"""
        # 只是隐藏窗口而不是真正关闭
        self.hide()
        event.ignore()