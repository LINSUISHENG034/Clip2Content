from typing import List, Tuple
import re
from difflib import SequenceMatcher
from .models import QualityMetrics
from .exceptions import QualityCheckError
from utils.logger.setup import get_logger

class QualityChecker:
    """Check quality of generated summaries"""
    
    def __init__(self):
        self.logger = get_logger("summary.quality")
    
    def check_quality(self, original_text: str, summary: str) -> QualityMetrics:
        """Perform comprehensive quality check"""
        try:
            # 计算各项指标
            info_retention = self._calculate_info_retention(original_text, summary)
            redundancy_score = self._check_redundancy(summary)
            coherence_score = self._check_coherence(summary)
            key_points = self._extract_key_points(original_text, summary)
            
            # 收集警告信息
            warnings = []
            if info_retention < 0.85:
                warnings.append(f"信息保留率较低: {info_retention:.2%}")
            if redundancy_score > 0.2:
                warnings.append(f"存在重复内容: {redundancy_score:.2%}")
            if coherence_score < 0.7:
                warnings.append(f"文本连贯性不足: {coherence_score:.2%}")
            
            metrics = QualityMetrics(
                info_retention=info_retention,
                redundancy_score=redundancy_score,
                coherence_score=coherence_score,
                key_points_coverage=key_points,
                warnings=warnings
            )
            
            self.logger.info(f"质量检查完成：信息保留率={info_retention:.2%}, "
                           f"重复度={redundancy_score:.2%}, "
                           f"连贯性={coherence_score:.2%}")
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"质量检查失败：{str(e)}")
            raise QualityCheckError(0, 0.85)  # 使用默认阈值
    
    def _calculate_info_retention(self, original: str, summary: str) -> float:
        """Calculate information retention rate"""
        # 1. 提取关键词和短语
        original_keywords = self._extract_keywords(original)
        summary_keywords = self._extract_keywords(summary)
        
        # 2. 计算关键信息覆盖率
        matched_keywords = set(original_keywords) & set(summary_keywords)
        retention_rate = len(matched_keywords) / len(original_keywords) if original_keywords else 0
        
        return retention_rate
    
    def _check_redundancy(self, text: str) -> float:
        """Check for redundant content"""
        # 1. 分句
        sentences = self._split_sentences(text)
        if len(sentences) <= 1:
            return 0.0
        
        # 2. 计算句子间的相似度
        total_similarity = 0
        comparisons = 0
        
        for i in range(len(sentences)):
            for j in range(i + 1, len(sentences)):
                similarity = SequenceMatcher(None, sentences[i], sentences[j]).ratio()
                total_similarity += similarity
                comparisons += 1
        
        # 3. 计算平均相似度
        avg_similarity = total_similarity / comparisons if comparisons > 0 else 0
        return avg_similarity
    
    def _check_coherence(self, text: str) -> float:
        """Check text coherence"""
        # 1. 分句
        sentences = self._split_sentences(text)
        if len(sentences) <= 1:
            return 1.0
        
        # 2. 检查句子间的连接词和指示词
        coherence_markers = [
            r'因此', r'所以', r'然而', r'但是', r'此外',
            r'另外', r'同时', r'接着', r'最后', r'总之'
        ]
        
        # 3. 计算使用连接词的句子比例
        connected_sentences = 0
        for sentence in sentences[1:]:  # 跳过第一句
            if any(re.search(marker, sentence) for marker in coherence_markers):
                connected_sentences += 1
        
        coherence_score = (connected_sentences + 1) / len(sentences)  # +1 确保第一句也计入
        return coherence_score
    
    def _extract_key_points(self, original: str, summary: str) -> List[str]:
        """Extract and compare key points"""
        # 使用简单的句子作为关键点
        original_sentences = self._split_sentences(original)
        summary_sentences = self._split_sentences(summary)
        
        # 找出原文中最重要的句子（基于关键词密度）
        key_points = []
        for sentence in summary_sentences:
            # 检查该句子是否包含原文的重要信息
            if any(self._sentence_similarity(sentence, orig) > 0.5 for orig in original_sentences):
                key_points.append(sentence)
        
        return key_points
    
    @staticmethod
    def _extract_keywords(text: str) -> List[str]:
        """Extract keywords from text"""
        # 简单实现，后续可以使用更复杂的算法
        # 1. 移除标点符号
        text = re.sub(r'[^\w\s]', '', text)
        # 2. 分词
        words = text.split()
        # 3. 移除停用词（示例）
        stopwords = {'的', '了', '和', '是', '在', '我', '有', '就', '不', '也', '这', '到', '那'}
        keywords = [word for word in words if word not in stopwords]
        return keywords
    
    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        """Split text into sentences"""
        # 处理常见的中文句末标点
        return re.split(r'[。！？]', text)
    
    @staticmethod
    def _sentence_similarity(s1: str, s2: str) -> float:
        """Calculate similarity between two sentences"""
        return SequenceMatcher(None, s1, s2).ratio()