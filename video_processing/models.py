from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path

@dataclass
class TranscriptionSegment:
    """Represents a segment of transcribed text with timing information"""
    start: float  # Start time in seconds
    end: float    # End time in seconds
    text: str     # Transcribed text
    confidence: float  # Confidence score

@dataclass
class ProcessingResult:
    """Represents the result of video processing"""
    video_path: Path
    segments: List[TranscriptionSegment]
    srt_path: Optional[Path] = None
    text_path: Optional[Path] = None
    warnings: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []

    def add_warning(self, warning: str):
        """Add a warning message"""
        self.warnings.append(warning)

    def has_warnings(self) -> bool:
        """Check if there are any warnings"""
        return len(self.warnings) > 0

    def get_full_text(self) -> str:
        """Get the full transcribed text"""
        return "\n".join(segment.text for segment in self.segments)

    def get_srt_content(self) -> str:
        """Generate SRT format content"""
        srt_content = []
        for i, segment in enumerate(self.segments, 1):
            # Convert seconds to SRT time format (HH:MM:SS,mmm)
            start = self._format_time(segment.start)
            end = self._format_time(segment.end)
            
            srt_content.extend([
                str(i),
                f"{start} --> {end}",
                segment.text,
                ""  # Empty line between entries
            ])
        return "\n".join(srt_content)

    @staticmethod
    def _format_time(seconds: float) -> str:
        """Convert seconds to SRT time format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        milliseconds = int((seconds % 1) * 1000)
        seconds = int(seconds)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"