# tests/test_llm.py
import pytest
from llm.model_selector import ModelRegistry, select_model

def test_model_registration():
    assert "gpt2" in ModelRegistry.list_models()
    assert "llama" in ModelRegistry.list_models()

def test_model_selection():
    with select_model("gpt2") as model:
        assert model is not None
        response = model.generate("Hello")
        assert isinstance(response, str)

def test_invalid_model():
    with pytest.raises(ValueError):
        select_model("invalid_model")