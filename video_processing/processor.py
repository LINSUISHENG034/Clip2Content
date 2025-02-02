import os
import subprocess
import whisper
import yaml
from pathlib import Path
from typing import List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import torch
from .exceptions import FFmpegError, WhisperError, SilenceDetectionError, ConfidenceThresholdError
from .models import TranscriptionSegment, ProcessingResult
from utils.logger.setup import get_logger, get_ffmpeg_logger, get_whisper_logger

class VideoProcessor:
    def __init__(self, config_path: str = "config/settings.yaml", use_cuda: bool = False):
        self.logger = get_logger("video.processor")
        self.ffmpeg_logger = get_ffmpeg_logger()
        self.whisper_logger = get_whisper_logger()
        
        self.config = self._load_config(config_path)
        self.model = None
        self.processing = False
        self._progress_callback = None
        self.use_cuda = use_cuda and torch.cuda.is_available()
        self._ensure_directories()
        
        self.logger.info(f"初始化视频处理器，CUDA加速：{'启用' if self.use_cuda else '禁用'}")

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            self.logger.debug(f"加载配置文件成功：{config_path}")
            return config
        except Exception as e:
            self.logger.error(f"加载配置文件失败：{str(e)}")
            raise

    def _ensure_directories(self):
        """Ensure required directories exist"""
        try:
            Path(self.config['video_processing']['output_dir']).mkdir(parents=True, exist_ok=True)
            Path(self.config['video_processing']['temp_dir']).mkdir(parents=True, exist_ok=True)
            self.logger.debug("创建必要目录成功")
        except Exception as e:
            self.logger.error(f"创建目录失败：{str(e)}")
            raise

    def set_progress_callback(self, callback: Callable[[float, str], None]):
        """Set callback for progress updates"""
        self._progress_callback = callback

    def _update_progress(self, progress: float, status: str):
        """Update progress through callback if set"""
        if self._progress_callback:
            self._progress_callback(progress, status)
        self.logger.debug(f"进度更新：{progress:.1%} - {status}")

    def _split_video(self, video_path: str) -> List[str]:
        """Split video into segments using FFmpeg"""
        self.ffmpeg_logger.info(f"开始分割视频：{video_path}")
        
        temp_dir = Path(self.config['video_processing']['temp_dir'])
        segment_length = self.config['video_processing']['ffmpeg']['segment_length']
        
        # Create unique directory for this video's segments
        video_id = Path(video_path).stem
        segments_dir = temp_dir / video_id
        segments_dir.mkdir(exist_ok=True)
        
        # Split video into segments
        segment_pattern = str(segments_dir / f"segment_%03d.mp4")
        command = [
            "ffmpeg", "-i", video_path,
            "-f", "segment",
            "-segment_time", str(segment_length),
            "-reset_timestamps", "1",
            "-c", "copy",
            segment_pattern
        ]
        
        try:
            self.ffmpeg_logger.debug(f"执行FFmpeg命令：{' '.join(command)}")
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 实时记录FFmpeg输出
            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.ffmpeg_logger.debug(output.strip())
            
            if process.returncode != 0:
                raise FFmpegError(f"FFmpeg返回错误代码：{process.returncode}")
            
            # Return sorted list of segment paths
            segments = sorted(str(p) for p in segments_dir.glob("segment_*.mp4"))
            self.ffmpeg_logger.info(f"视频分割完成，共{len(segments)}个片段")
            return segments
            
        except Exception as e:
            self.ffmpeg_logger.error(f"视频分割失败：{str(e)}")
            raise FFmpegError(f"Failed to split video: {str(e)}")

    def _detect_silence(self, segment_path: str) -> bool:
        """Detect if segment contains silence longer than threshold"""
        self.ffmpeg_logger.debug(f"检测静音：{segment_path}")
        silence_threshold = self.config['video_processing']['ffmpeg']['silence_threshold']
        
        command = [
            "ffmpeg", "-i", segment_path,
            "-af", f"silencedetect=n=-50dB:d={silence_threshold}",
            "-f", "null", "-"
        ]
        
        try:
            self.ffmpeg_logger.debug(f"执行静音检测命令：{' '.join(command)}")
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            
            # Parse FFmpeg output to find silence duration
            for line in result.stderr.split('\n'):
                if "silence_duration" in line:
                    duration = float(line.split("silence_duration: ")[1])
                    if duration >= silence_threshold:
                        self.ffmpeg_logger.warning(f"检测到静音段：{duration}秒")
                        return True
            return False
            
        except subprocess.CalledProcessError as e:
            self.ffmpeg_logger.error(f"静音检测失败：{e.stderr}")
            raise SilenceDetectionError(f"Failed to detect silence: {e.stderr}")

    def _transcribe_segment(self, segment_path: str) -> List[TranscriptionSegment]:
        """Transcribe a video segment using Whisper"""
        try:
            self.whisper_logger.info(f"开始转写片段：{segment_path}")
            
            # Check for long silence
            if self._detect_silence(segment_path):
                raise SilenceDetectionError(f"Long silence detected in segment: {segment_path}")
            
            # Transcribe using Whisper
            self.whisper_logger.debug("调用Whisper模型")
            result = self.model.transcribe(
                segment_path,
                language=self.config['video_processing']['whisper']['language'],
                task=self.config['video_processing']['whisper']['task']
            )
            
            # Convert Whisper segments to our format
            segments = []
            for segment in result['segments']:
                confidence = segment.get('confidence', 0.0)
                
                # Check confidence threshold
                if confidence < self.config['video_processing']['whisper']['confidence_threshold']:
                    self.whisper_logger.warning(
                        f"片段置信度低于阈值：{confidence:.2f} < "
                        f"{self.config['video_processing']['whisper']['confidence_threshold']}"
                    )
                    raise ConfidenceThresholdError(confidence, 
                        self.config['video_processing']['whisper']['confidence_threshold'])
                
                segments.append(TranscriptionSegment(
                    start=segment['start'],
                    end=segment['end'],
                    text=segment['text'].strip(),
                    confidence=confidence
                ))
                self.whisper_logger.debug(
                    f"转写片段：{segment['start']:.1f}-{segment['end']:.1f} "
                    f"置信度：{confidence:.2f}"
                )
            
            self.whisper_logger.info(f"片段转写完成，共{len(segments)}个文本段")
            return segments
            
        except Exception as e:
            if isinstance(e, (SilenceDetectionError, ConfidenceThresholdError)):
                raise
            self.whisper_logger.error(f"转写失败：{str(e)}")
            raise WhisperError(f"Transcription failed: {str(e)}")

    def _save_results(self, result: ProcessingResult):
        """Save transcription results to files"""
        self.logger.info("保存处理结果")
        output_dir = Path(self.config['video_processing']['output_dir'])
        base_name = result.video_path.stem
        
        try:
            # Save SRT file
            srt_path = output_dir / f"{base_name}.srt"
            srt_path.write_text(result.get_srt_content(), encoding='utf-8')
            result.srt_path = srt_path
            self.logger.debug(f"保存SRT文件：{srt_path}")
            
            # Save plain text file
            text_path = output_dir / f"{base_name}.txt"
            text_path.write_text(result.get_full_text(), encoding='utf-8')
            result.text_path = text_path
            self.logger.debug(f"保存文本文件：{text_path}")
            
        except Exception as e:
            self.logger.error(f"保存结果失败：{str(e)}")
            raise

    def process_video(self, video_path: str) -> ProcessingResult:
        """Process video file and generate transcription"""
        self.logger.info(f"开始处理视频：{video_path}")
        
        if not os.path.exists(video_path):
            self.logger.error(f"视频文件不存在：{video_path}")
            raise FileNotFoundError(f"Video file not found: {video_path}")

        self.processing = True
        try:
            # Initialize result
            result = ProcessingResult(
                video_path=Path(video_path),
                segments=[]
            )

            # Load Whisper model
            self._update_progress(0.1, "加载Whisper模型...")
            if self.model is None:
                device = "cuda" if self.use_cuda else "cpu"
                self.whisper_logger.info(f"加载Whisper模型：{self.config['models']['whisper']['model_size']} ({device})")
                self.model = whisper.load_model(
                    self.config['models']['whisper']['model_size'],
                    device=device
                )

            # Process video segments
            self._update_progress(0.2, "处理视频分段...")
            segments = self._split_video(video_path)

            # Transcribe segments
            total_segments = len(segments)
            for i, segment_path in enumerate(segments, 1):
                if not self.processing:
                    self.logger.warning("处理被用户取消")
                    raise InterruptedError("Processing cancelled")

                progress = 0.2 + (0.7 * i / total_segments)
                self._update_progress(progress, f"转写分段 {i}/{total_segments}...")
                
                try:
                    segment_result = self._transcribe_segment(segment_path)
                    result.segments.extend(segment_result)
                except (SilenceDetectionError, ConfidenceThresholdError) as e:
                    self.logger.warning(f"片段处理警告：{str(e)}")
                    result.add_warning(str(e))

            # Generate output files
            self._update_progress(0.9, "生成输出文件...")
            self._save_results(result)

            self._update_progress(1.0, "处理完成")
            self.logger.info("视频处理完成")
            return result

        except Exception as e:
            self.logger.error(f"视频处理失败：{str(e)}", exc_info=True)
            raise
        finally:
            self.processing = False

    def cancel_processing(self):
        """Cancel ongoing processing"""
        self.logger.info("取消处理")
        self.processing = False

    @staticmethod
    def is_cuda_available() -> bool:
        """Check if CUDA is available on the system"""
        return torch.cuda.is_available()