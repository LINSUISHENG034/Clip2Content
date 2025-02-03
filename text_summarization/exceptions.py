class TextSummarizationError(Exception):
    """Base exception for text summarization errors"""
    pass

class TemplateError(TextSummarizationError):
    """Raised when there is an error with summary templates"""
    pass

class OllamaError(TextSummarizationError):
    """Raised when there is an error with Ollama API"""
    pass

class QualityCheckError(TextSummarizationError):
    """Raised when summary quality check fails"""
    def __init__(self, score: float, threshold: float):
        self.score = score
        self.threshold = threshold
        super().__init__(f"Quality check failed: score {score} is below threshold {threshold}")

class ContentLengthError(TextSummarizationError):
    """Raised when content length exceeds limits"""
    def __init__(self, current_length: int, max_length: int):
        self.current_length = current_length
        self.max_length = max_length
        super().__init__(f"Content length {current_length} exceeds maximum {max_length}")

class EmptyContentError(TextSummarizationError):
    """Raised when input content is empty"""
    pass