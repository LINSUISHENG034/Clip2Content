import os
import json
import asyncio
import aiohttp
from typing import Optional, Callable, Dict, Any
from pathlib import Path

from .exceptions import (
    TextSummarizationError, OllamaError,
    ContentLengthError, EmptyContentError
)
from .models import SummaryConfig, SummaryResult, SummaryStyle
from .templates import TemplateManager
from .quality import QualityChecker
from utils.logger.setup import get_logger

class SummaryProcessor:
    """Process text summarization requests"""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.logger = get_logger("summary.processor")
        self.template_manager = TemplateManager()
        self.quality_checker = QualityChecker()
        self.processing = False
        self._progress_callback = None
        self._load_config(config_path)
    
    def _load_config(self, config_path: str):
        """Load configuration from file"""
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            self.ollama_config = config['models']['ollama']
            self.logger.info("配置加载成功")
            
        except Exception as e:
            self.logger.error(f"加载配置失败：{str(e)}")
            raise TextSummarizationError(f"Failed to load config: {str(e)}")
    
    def set_progress_callback(self, callback: Callable[[float, str], None]):
        """Set callback for progress updates"""
        self._progress_callback = callback
    
    def _update_progress(self, progress: float, status: str):
        """Update progress through callback if set"""
        if self._progress_callback:
            self._progress_callback(progress, status)
        self.logger.debug(f"进度更新：{progress:.1%} - {status}")
    
    async def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API to generate summary"""
        try:
            url = f"{self.ollama_config['base_url']}/api/generate"
            headers = {'Content-Type': 'application/json'}
            data = {
                'model': 'deepseek-r1:8b',  # 使用默认模型，后续可配置
                'prompt': prompt,
                'stream': False
            }
            
            timeout = aiohttp.ClientTimeout(total=self.ollama_config['timeout'])
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise OllamaError(f"Ollama API error: {error_text}")
                    
                    result = await response.json()
                    return result['response']
                    
        except Exception as e:
            self.logger.error(f"调用Ollama API失败：{str(e)}")
            raise OllamaError(f"Failed to call Ollama: {str(e)}")
    
    async def generate_summary(self, text: str, config: SummaryConfig) -> SummaryResult:
        """Generate summary for given text"""
        if not text.strip():
            raise EmptyContentError("Input text is empty")
        
        if len(text) > config.max_length:
            raise ContentLengthError(len(text), config.max_length)
        
        self.processing = True
        try:
            self._update_progress(0.1, "准备提示词模板...")
            prompt = self.template_manager.render_prompt(
                config.style,
                text,
                max_length=config.max_length,
                **config.custom_params
            )
            
            self._update_progress(0.3, "生成摘要...")
            summary = await self._call_ollama(prompt)
            
            self._update_progress(0.6, "检查质量...")
            metrics = self.quality_checker.check_quality(text, summary)
            
            # 如果质量不达标，尝试重新生成
            attempts = 1
            while (not metrics.passed_threshold and 
                   attempts < 3 and 
                   self.processing):
                self.logger.warning(f"质量检查未通过，尝试重新生成 (尝试 {attempts}/3)")
                self._update_progress(0.7, f"重新生成 (尝试 {attempts}/3)...")
                
                # 调整提示词以改进质量
                prompt = self._adjust_prompt_for_quality(
                    prompt, metrics, config.style
                )
                summary = await self._call_ollama(prompt)
                metrics = self.quality_checker.check_quality(text, summary)
                attempts += 1
            
            self._update_progress(0.9, "生成结果...")
            result = SummaryResult(
                original_text=text,
                summary=summary,
                style=config.style,
                metrics=metrics
            )
            
            self._update_progress(1.0, "完成")
            return result
            
        except Exception as e:
            self.logger.error(f"生成摘要失败：{str(e)}")
            raise
        finally:
            self.processing = False
    
    def _adjust_prompt_for_quality(
        self, original_prompt: str,
        metrics: QualityChecker,
        style: SummaryStyle
    ) -> str:
        """Adjust prompt based on quality metrics"""
        adjustments = []
        
        if metrics.info_retention < 0.85:
            adjustments.append("请确保包含更多原文中的关键信息")
        
        if metrics.redundancy_score > 0.2:
            adjustments.append("请避免重复内容")
        
        if metrics.coherence_score < 0.7:
            adjustments.append("请提高文本的连贯性，适当使用连接词")
        
        if adjustments:
            return original_prompt + "\n\n优化要求：\n" + "\n".join(
                f"- {adj}" for adj in adjustments
            )
        
        return original_prompt
    
    def cancel_processing(self):
        """Cancel ongoing processing"""
        self.logger.info("取消处理")
        self.processing = False