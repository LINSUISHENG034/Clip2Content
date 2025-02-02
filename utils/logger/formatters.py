import logging
import re
from typing import Dict, Optional, Set
from enum import Enum, auto

class LogStage(Enum):
    """日志阶段枚举"""
    VIDEO = auto()      # 视频处理
    SPLIT = auto()      # 视频分割
    FFMPEG = auto()     # FFmpeg操作
    WHISPER = auto()    # Whisper模型
    METADATA = auto()   # 元数据处理
    PROGRESS = auto()   # 进度更新
    QUALITY = auto()    # 质量检查
    OUTPUT = auto()     # 输出处理
    COMPLETE = auto()   # 完成状态

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

class StructuredFormatter(ColoredFormatter):
    """结构化日志格式化器，提供更清晰的日志输出格式"""
    
    # FFmpeg配置信息的正则表达式
    FFMPEG_CONFIG_PATTERN = re.compile(r'(--enable-\w+|--disable-\w+)')
    
    # 已知的重复消息集合
    _seen_messages: Set[str] = set()
    
    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: str = '%',
        validate: bool = True,
        bilingual: bool = True
    ):
        if fmt is None:
            fmt = "%(asctime)s - %(levelname)s - %(message)s"
        super().__init__(fmt, datefmt, style, validate)
        self.bilingual = bilingual
    
    def format(self, record: logging.LogRecord) -> str:
        """增强的日志格式化"""
        # 检查是否是重复消息
        if hasattr(record, 'msg'):
            msg_hash = f"{record.levelname}:{record.msg}"
            if msg_hash in self._seen_messages:
                return ""  # 跳过重复消息
            self._seen_messages.add(msg_hash)
        
        # 处理FFmpeg配置信息
        if record.levelno == logging.DEBUG and isinstance(record.msg, str):
            if self.FFMPEG_CONFIG_PATTERN.search(record.msg):
                return ""  # 跳过详细配置信息
        
        # 添加结构化标记
        if hasattr(record, 'stage') and isinstance(record.stage, LogStage):
            record.msg = f"[{record.stage.name}] {record.msg}"
        
        # 处理进度信息
        if 'progress' in getattr(record, 'extra', {}):
            progress = record.extra['progress']
            record.msg = f"[PROGRESS] {progress:.1f}% - {record.msg}"
        
        # 处理命令执行信息
        if record.levelno == logging.DEBUG and '执行FFmpeg命令' in str(record.msg):
            cmd = str(record.msg).split('：', 1)[1] if '：' in str(record.msg) else str(record.msg)
            record.msg = f"[COMMAND] FFmpeg: {cmd}"
        
        return super().format(record)
    
    def _format_bilingual(self, msg: str) -> str:
        """处理双语消息格式"""
        if not self.bilingual:
            return msg
            
        # 如果消息已经是双语格式，保持不变
        if ' | ' in msg:
            return msg
            
        # 尝试翻译常见消息（这里可以扩展为更完整的翻译映射）
        translations = {
            "开始处理": "Processing Started",
            "处理完成": "Processing Complete",
            "出现错误": "Error Occurred",
            # 可以添加更多翻译
        }
        
        for cn, en in translations.items():
            if cn in msg:
                return f"{msg} | {en}"
        
        return msg

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