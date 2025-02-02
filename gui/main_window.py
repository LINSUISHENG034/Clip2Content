from PyQt6.QtWidgets import QMainWindow, QTabWidget
from gui.tabs.video_tab import VideoTab
from gui.tabs.summary_tab import SummaryTab
from gui.tabs.article_tab import ArticleTab
from gui.tabs.review_tab import ReviewTab
from gui.tabs.publish_tab import PublishTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("视频内容自动化处理系统")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Initialize tabs
        self.tabs.addTab(VideoTab(), "视频处理")
        self.tabs.addTab(SummaryTab(), "内容总结")
        self.tabs.addTab(ArticleTab(), "文章生成")
        self.tabs.addTab(ReviewTab(), "审核系统")
        self.tabs.addTab(PublishTab(), "发布管理")
