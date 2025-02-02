import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict
from .formatters import ColoredFormatter

class LogManager:
    """Manages application-wide logging configuration and functionality."""
    
    def __init__(self, app_name: str = "clip2content"):
        self.app_name = app_name
        self.loggers: Dict[str, logging.Logger] = {}
        
        # 设置基础日志目录
        self.base_log_dir = Path("logs")
        self.base_log_dir.mkdir(exist_ok=True)
        
        # 创建子目录
        self.processing_log_dir = self.base_log_dir / "processing"
        self.video_log_dir = self.processing_log_dir / "video"
        self.system_log_dir = self.base_log_dir / "system"
        
        for directory in [self.processing_log_dir, self.video_log_dir, self.system_log_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # 初始化主日志器
        self.setup_main_logger()
        
    def setup_main_logger(self):
        """设置主应用日志器"""
        logger = logging.getLogger(self.app_name)
        logger.setLevel(logging.DEBUG)
        
        # 确保日志器没有重复的处理器
        logger.handlers = []
        
        # 添加文件处理器
        file_handler = self._create_file_handler(
            self.base_log_dir / "app.log",
            formatter=logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
        logger.addHandler(file_handler)
        
        # 添加控制台处理器
        console_handler = self._create_console_handler()
        logger.addHandler(console_handler)
        
        self.loggers["main"] = logger
        
    def get_logger(self, name: str) -> logging.Logger:
        """获取或创建一个命名日志器"""
        if name in self.loggers:
            return self.loggers[name]
            
        logger = logging.getLogger(f"{self.app_name}.{name}")
        logger.setLevel(logging.DEBUG)
        
        # 根据名称确定日志文件位置
        if name.startswith("video"):
            log_file = self.video_log_dir / f"{name}.log"
        elif name.startswith("system"):
            log_file = self.system_log_dir / f"{name}.log"
        else:
            log_file = self.processing_log_dir / f"{name}.log"
            
        # 添加文件处理器
        file_handler = self._create_file_handler(
            log_file,
            formatter=logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
            )
        )
        logger.addHandler(file_handler)
        
        # 添加控制台处理器
        console_handler = self._create_console_handler()
        logger.addHandler(console_handler)
        
        self.loggers[name] = logger
        return logger
        
    def _create_file_handler(
        self,
        log_file: Path,
        formatter: logging.Formatter,
        max_bytes: int = 5 * 1024 * 1024,  # 5MB
        backup_count: int = 5
    ) -> logging.Handler:
        """创建文件日志处理器"""
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        handler.setFormatter(formatter)
        return handler
        
    def _create_console_handler(self) -> logging.Handler:
        """创建控制台日志处理器"""
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(ColoredFormatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        return handler
        
    def get_video_logger(self) -> logging.Logger:
        """获取视频处理专用日志器"""
        return self.get_logger("video.processing")
        
    def get_ffmpeg_logger(self) -> logging.Logger:
        """获取FFmpeg专用日志器"""
        return self.get_logger("video.ffmpeg")
        
    def get_whisper_logger(self) -> logging.Logger:
        """获取Whisper专用日志器"""
        return self.get_logger("video.whisper")
        
    def cleanup_old_logs(self, days: int = 30):
        """清理指定天数之前的日志文件"""
        current_time = datetime.now().timestamp()
        
        def cleanup_directory(directory: Path):
            for file in directory.glob("*.log*"):
                if file.stat().st_mtime < current_time - (days * 86400):
                    file.unlink()
                    
        for directory in [self.base_log_dir, self.processing_log_dir,
                         self.video_log_dir, self.system_log_dir]:
            cleanup_directory(directory)
            
    def set_level(self, level: int):
        """设置所有日志器的日志级别"""
        for logger in self.loggers.values():
            logger.setLevel(level)
            
    def close(self):
        """关闭所有日志处理器"""
        for logger in self.loggers.values():
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)