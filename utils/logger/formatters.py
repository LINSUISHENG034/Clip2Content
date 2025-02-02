import logging
from typing import Dict, Optional

class ColoredFormatter(logging.Formatter):
    """为不同级别的日志添加颜色的格式化器"""
    
    # 颜色代码
    COLORS = {
        'DEBUG': '\033[0;36m',    # 青色
        'INFO': '\033[0;32m',     # 绿色
        'WARNING': '\033[0;33m',  # 黄色
        'ERROR': '\033[0;31m',    # 红色
        'CRITICAL': '\033[0;35m', # 紫色
        'RESET': '\033[0m',       # 重置
    }
    
    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: str = '%',
        validate: bool = True
    ):
        """初始化格式化器"""
        super().__init__(fmt, datefmt, style)
        
    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录"""
        # 保存原始的格式化消息
        original_msg = record.msg
        
        # 为不同级别添加颜色
        if record.levelname in self.COLORS:
            color_start = self.COLORS[record.levelname]
            color_end = self.COLORS['RESET']
            record.msg = f"{color_start}{record.msg}{color_end}"
            
            # 同时为级别名称添加颜色
            record.levelname = f"{color_start}{record.levelname}{color_end}"
        
        # 调用父类的format方法
        result = super().format(record)
        
        # 恢复原始消息，避免影响其他格式化器
        record.msg = original_msg
        
        return result
        
    def formatException(self, ei) -> str:
        """为异常添加红色"""
        exception = super().formatException(ei)
        return f"{self.COLORS['ERROR']}{exception}{self.COLORS['RESET']}"
        
class FileFormatter(logging.Formatter):
    """文件日志格式化器，提供更详细的信息"""
    
    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: str = '%',
        validate: bool = True
    ):
        if fmt is None:
            fmt = (
                "%(asctime)s [%(levelname)s] "
                "%(name)s:%(funcName)s:%(lineno)d - "
                "%(message)s"
            )
        super().__init__(fmt, datefmt, style)
        
    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录，添加额外的上下文信息"""
        # 添加进程ID和线程ID
        record.process_thread = f"{record.process}:{record.thread}"
        
        # 如果有异常信息，确保它被正确格式化
        if record.exc_info:
            record.exc_text = self.formatException(record.exc_info)
            
        return super().format(record)
        
    def formatException(self, ei) -> str:
        """提供更详细的异常格式化"""
        exception = super().formatException(ei)
        return f"\nException:\n{exception}\n"