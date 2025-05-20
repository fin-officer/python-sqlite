# llm/model_selector.py
from typing import Dict, Type, Optional
from abc import ABC, abstractmethod


class BaseLLM(ABC):
    """Base class for all LLM models"""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text based on the prompt"""
        pass

    @classmethod
    @abstractmethod
    def get_model_info(cls) -> Dict:
        """Get information about the model"""
        pass


class ModelRegistry:
    """Registry for all available models"""

    _models: Dict[str, Type[BaseLLM]] = {}

    @classmethod
    def register(cls, name: str):
        """Decorator to register a new model"""

        def wrapper(model_class: Type[BaseLLM]):
            cls._models[name] = model_class
            return model_class

        return wrapper

    @classmethod
    def get_model(cls, name: str, **kwargs) -> Optional[BaseLLM]:
        """Get an instance of the specified model"""
        if name not in cls._models:
            return None
        return cls._models[name](**kwargs)

    @classmethod
    def list_models(cls) -> Dict[str, Dict]:
        """List all available models with their info"""
        return {
            name: model_class.get_model_info()
            for name, model_class in cls._models.items()
        }


# Example model implementations
@ModelRegistry.register("gpt2")
class GPT2Model(BaseLLM):
    def generate(self, prompt: str, **kwargs) -> str:
        # Implementation for GPT-2
        return "Generated text from GPT-2"

    @classmethod
    def get_model_info(cls) -> Dict:
        return {
            "name": "GPT-2",
            "description": "Smaller, faster model with 1.5B parameters",
            "supports_streaming": True
        }


@ModelRegistry.register("llama")
class LlamaModel(BaseLLM):
    def generate(self, prompt: str, **kwargs) -> str:
        # Implementation for LLaMA
        return "Generated text from LLaMA"

    @classmethod
    def get_model_info(cls) -> Dict:
        return {
            "name": "LLaMA",
            "description": "Open source model from Meta with various sizes",
            "supports_streaming": True
        }


class ModelContext:
    """Context manager for model execution"""

    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.model = ModelRegistry.get_model(model_name, **kwargs)
        self.context = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.context.clear()

    def add_to_context(self, text: str):
        """Add text to the context window"""
        self.context.append(text)

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using the current context"""
        full_prompt = "\n".join(self.context + [prompt])
        return self.model.generate(full_prompt, **kwargs)


def select_model(model_name: str, **kwargs) -> ModelContext:
    """Create a new model context with the specified model"""
    return ModelContext(model_name, **kwargs)