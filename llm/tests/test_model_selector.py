import pytest
from llm.model_selector import ModelRegistry, select_model

def test_model_registration():
    """Test that models are properly registered"""
    models = ModelRegistry.list_models()
    assert "gpt2" in models
    assert "llama" in models

def test_model_selection():
    """Test model selection functionality"""
    context = select_model("gpt2")
    assert context.model_name == "gpt2"
    assert context.model is not None

def test_model_context():
    """Test model context functionality"""
    with select_model("gpt2") as context:
        context.add_to_context("This is a test.")
        assert len(context.context) == 1
        assert context.context[0] == "This is a test."
        
        # Test generation with context
        response = context.generate("Continue:")
        assert isinstance(response, str)
        assert len(response) > 0

def test_invalid_model():
    """Test behavior with invalid model name"""
    invalid_model = ModelRegistry.get_model("invalid_model_name")
    assert invalid_model is None
