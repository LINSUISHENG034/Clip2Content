from dataclasses import dataclass, field
from typing import List, Optional, Dict
from pathlib import Path
from enum import Enum

class SummaryStyle(Enum):
    """Enumeration of available summary styles"""
    ACADEMIC = "学术风格"
    NEWS = "新闻风格"
    TECH_BLOG = "技术博客"
    POPULAR_SCIENCE = "科普文章"
    MARKETING = "营销文案"

    @classmethod
    def from_display_name(cls, display_name: str) -> "SummaryStyle":
        """Get enum value from display name"""
        for style in cls:
            if style.value == display_name:
                return style
        raise ValueError(f"Unknown style: {display_name}")

@dataclass
class SummaryConfig:
    """Configuration for text summarization"""
    style: SummaryStyle
    max_length: int
    min_info_retention: float = 0.85  # 最低信息保留率要求
    custom_params: Dict = field(default_factory=dict)  # 自定义参数

@dataclass
class QualityMetrics:
    """Quality metrics for generated summary"""
    info_retention: float  # 信息保留率 (0-1)
    redundancy_score: float  # 重复内容评分 (0-1，越低越好)
    coherence_score: float  # 连贯性评分 (0-1)
    key_points_coverage: List[str]  # 关键信息点列表
    warnings: List[str] = field(default_factory=list)  # 质量警告信息

    @property
    def passed_threshold(self) -> bool:
        """Check if quality metrics pass minimum thresholds"""
        return (
            self.info_retention >= 0.85 and
            self.redundancy_score <= 0.2 and
            self.coherence_score >= 0.7
        )

@dataclass
class SummaryResult:
    """Result of text summarization"""
    original_text: str
    summary: str
    style: SummaryStyle
    metrics: QualityMetrics
    source_file: Optional[Path] = None  # 原始文件路径（如果有）
    word_count: int = field(init=False)
    
    def __post_init__(self):
        """Calculate word count after initialization"""
        self.word_count = len(self.summary)  # 简单字数统计，后续可改进
    
    @property
    def is_valid(self) -> bool:
        """Check if summary result is valid"""
        return bool(self.summary and self.metrics.passed_threshold)

    def to_dict(self) -> Dict:
        """Convert to dictionary format"""
        return {
            "style": self.style.value,
            "summary": self.summary,
            "word_count": self.word_count,
            "metrics": {
                "info_retention": self.metrics.info_retention,
                "redundancy_score": self.metrics.redundancy_score,
                "coherence_score": self.metrics.coherence_score,
                "key_points": self.metrics.key_points_coverage,
                "warnings": self.metrics.warnings
            }
        }