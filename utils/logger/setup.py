import logging
import sys
from pathlib import Path
from typing import Optional
from .manager import LogManager
from .console import LogWindow

class AppLogger:
    """应用日志管理器单例"""
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.log_manager = LogManager()
            self.log_window = None  # 延迟创建窗口
            self.main_logger = self.log_manager.get_logger("main")
            self._initialized = True
            
            # 设置全局异常处理
            sys.excepthook = self.handle_exception
    
    def init_window(self):
        """初始化日志窗口（在QApplication创建后调用）"""
        if self.log_window is None:
            self.log_window = LogWindow()
    
    @property
    def window(self) -> Optional[LogWindow]:
        """获取日志窗口实例"""
        return self.log_window
    
    def get_logger(self, name: str) -> logging.Logger:
        """获取指定名称的日志器"""
        return self.log_manager.get_logger(name)
    
    def get_video_logger(self) -> logging.Logger:
        """获取视频处理专用日志器"""
        return self.log_manager.get_video_logger()
    
    def get_ffmpeg_logger(self) -> logging.Logger:
        """获取FFmpeg专用日志器"""
        return self.log_manager.get_ffmpeg_logger()
    
    def get_whisper_logger(self) -> logging.Logger:
        """获取Whisper专用日志器"""
        return self.log_manager.get_whisper_logger()
    
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """处理未捕获的异常"""
        # 忽略KeyboardInterrupt异常
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        self.main_logger.critical(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
    
    def setup_file_logging(self, log_dir: Optional[Path] = None):
        """设置文件日志"""
        if log_dir:
            self.log_manager.base_log_dir = log_dir
            self.log_manager.setup_main_logger()
    
    def cleanup(self):
        """清理日志系统"""
        self.log_manager.cleanup_old_logs()
        self.log_manager.close()

# 创建全局日志实例
app_logger = AppLogger()

def get_logger(name: str = "main") -> logging.Logger:
    """获取日志器的便捷方法"""
    return app_logger.get_logger(name)

def init_log_window():
    """初始化日志窗口的便捷方法"""
    app_logger.init_window()

def show_log_window():
    """显示日志窗口的便捷方法"""
    if app_logger.window:
        app_logger.window.show()

def setup_logging(log_dir: Optional[Path] = None):
    """设置日志系统的便捷方法"""
    app_logger.setup_file_logging(log_dir)

# 导出常用的日志获取方法
get_video_logger = app_logger.get_video_logger
get_ffmpeg_logger = app_logger.get_ffmpeg_logger
get_whisper_logger = app_logger.get_whisper_logger