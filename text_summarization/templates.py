import yaml
from pathlib import Path
from typing import Dict, Optional
from .exceptions import TemplateError
from .models import SummaryStyle
from utils.logger.setup import get_logger

class TemplateManager:
    """Manager for summary templates"""
    
    def __init__(self, template_dir: str = "config/templates"):
        self.logger = get_logger("summary.templates")
        self.template_dir = Path(template_dir)
        self.templates: Dict[SummaryStyle, Dict] = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load all template files from template directory"""
        try:
            template_file = self.template_dir / "summary.yaml"
            if not template_file.exists():
                raise TemplateError(f"Template file not found: {template_file}")
            
            with open(template_file, 'r', encoding='utf-8') as f:
                templates_data = yaml.safe_load(f)
            
            # 验证并转换模板
            for style_name, template in templates_data.items():
                try:
                    style = SummaryStyle.from_display_name(style_name)
                    self._validate_template(template)
                    self.templates[style] = template
                except ValueError as e:
                    self.logger.warning(f"跳过无效的模板风格：{style_name} - {str(e)}")
            
            self.logger.info(f"成功加载{len(self.templates)}个模板")
            
        except Exception as e:
            self.logger.error(f"加载模板失败：{str(e)}")
            raise TemplateError(f"Failed to load templates: {str(e)}")
    
    def _validate_template(self, template: Dict):
        """Validate template structure"""
        required_fields = ['系统提示']
        for field in required_fields:
            if field not in template:
                raise TemplateError(f"Missing required field in template: {field}")
    
    def get_template(self, style: SummaryStyle) -> Optional[Dict]:
        """Get template for specified style"""
        return self.templates.get(style)
    
    def render_prompt(self, style: SummaryStyle, text: str, **kwargs) -> str:
        """Render prompt template with given parameters"""
        template = self.get_template(style)
        if not template:
            raise TemplateError(f"No template found for style: {style.value}")
        
        try:
            # 构建基础提示词
            prompt = template['系统提示']
            
            # 添加自定义参数（如果有）
            if kwargs:
                prompt += "\n\n附加要求："
                for key, value in kwargs.items():
                    prompt += f"\n- {key}: {value}"
            
            # 添加待总结的文本
            prompt += "\n\n待总结文本：\n" + text
            
            return prompt
            
        except Exception as e:
            self.logger.error(f"渲染模板失败：{str(e)}")
            raise TemplateError(f"Failed to render template: {str(e)}")
    
    def add_template(self, style: SummaryStyle, template: Dict):
        """Add or update template for a style"""
        try:
            self._validate_template(template)
            self.templates[style] = template
            self.logger.info(f"添加模板成功：{style.value}")
            
            # 保存到文件
            self._save_templates()
            
        except Exception as e:
            self.logger.error(f"添加模板失败：{str(e)}")
            raise TemplateError(f"Failed to add template: {str(e)}")
    
    def _save_templates(self):
        """Save templates back to file"""
        try:
            template_file = self.template_dir / "summary.yaml"
            templates_data = {
                style.value: template
                for style, template in self.templates.items()
            }
            
            with open(template_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(templates_data, f, allow_unicode=True)
            
            self.logger.info("保存模板文件成功")
            
        except Exception as e:
            self.logger.error(f"保存模板失败：{str(e)}")
            raise TemplateError(f"Failed to save templates: {str(e)}")
    
    def list_available_styles(self) -> list[str]:
        """List all available template styles"""
        return [style.value for style in self.templates.keys()]