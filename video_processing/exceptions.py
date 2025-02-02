class VideoProcessingError(Exception):
    """Base exception for video processing errors"""
    pass

class FFmpegError(VideoProcessingError):
    """Raised when FFmpeg encounters an error"""
    pass

class WhisperError(VideoProcessingError):
    """Raised when Whisper encounters an error"""
    pass

class SilenceDetectionError(VideoProcessingError):
    """Raised when silence detection encounters an error"""
    pass

class ConfidenceThresholdError(VideoProcessingError):
    """Raised when transcription confidence is below threshold"""
    def __init__(self, confidence: float, threshold: float):
        self.confidence = confidence
        self.threshold = threshold
        super().__init__(f"Transcription confidence {confidence} is below threshold {threshold}")