from .setup import get_video_logger, get_ffmpeg_logger
from .formatters import LogStage
import logging

# 获取日志器
video_logger = get_video_logger()
ffmpeg_logger = get_ffmpeg_logger()

# 示例：处理视频文件
def process_video_example(video_path: str):
    """展示改进后的日志使用方式"""
    
    # 开始处理视频
    video_logger.info("开始处理视频：%s", video_path, extra={'stage': LogStage.VIDEO})
    
    # FFmpeg命令执行
    ffmpeg_cmd = f"ffmpeg -i {video_path} -f segment ..."
    ffmpeg_logger.debug(f"执行FFmpeg命令：{ffmpeg_cmd}", extra={'stage': LogStage.FFMPEG})
    
    # 进度更新
    video_logger.info("视频分割进行中...", 
                     extra={'stage': LogStage.SPLIT, 'progress': 25.0})
    
    # 质量警告
    video_logger.warning("检测到低质量片段",
                        extra={'stage': LogStage.QUALITY})
    
    # 完成处理
    video_logger.info("视频处理完成",
                     extra={'stage': LogStage.COMPLETE})

"""
输出示例：
2025-02-03 00:20:00 - INFO - [VIDEO] 开始处理视频：example.mp4 | Processing video: example.mp4
2025-02-03 00:20:01 - DEBUG - [FFMPEG] Executing command: ffmpeg -i example.mp4 -f segment ...
2025-02-03 00:20:02 - INFO - [SPLIT] [25.0%] 视频分割进行中... | Video splitting in progress...
2025-02-03 00:20:03 - WARNING - [QUALITY] 检测到低质量片段 | Low quality segment detected
2025-02-03 00:20:04 - INFO - [COMPLETE] 视频处理完成 | Processing complete
"""