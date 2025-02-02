from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QLineEdit, QTextEdit

class PublishTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Publish Queue
        queue_group = QGroupBox("发布队列")
        queue_layout = QVBoxLayout()
        
        self.publish_table = QTableWidget()
        self.publish_table.setColumnCount(4)
        self.publish_table.setHorizontalHeaderLabels(["标题", "状态", "计划发布时间", "操作"])
        
        queue_layout.addWidget(self.publish_table)
        queue_group.setLayout(queue_layout)
        layout.addWidget(queue_group)
        
        # Publish Settings
        settings_group = QGroupBox("发布设置")
        settings_layout = QVBoxLayout()
        
        timing_layout = QHBoxLayout()
        timing_layout.addWidget(QLabel("发布时间:"))
        self.publish_time = QLineEdit()
        timing_layout.addWidget(self.publish_time)
        
        settings_layout.addLayout(timing_layout)
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Publish Logs
        logs_group = QGroupBox("发布日志")
        logs_layout = QVBoxLayout()
        
        self.publish_logs = QTextEdit()
        self.publish_logs.setReadOnly(True)
        
        logs_layout.addWidget(self.publish_logs)
        logs_group.setLayout(logs_layout)
        layout.addWidget(logs_group)
        
        self.setLayout(layout)