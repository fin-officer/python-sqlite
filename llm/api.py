# api.py
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from model_selector import ModelRegistry, ModelContext

app = FastAPI(
    title="LLM API",
    description="API for interacting with various LLM models",
    version="1.0.0"
)


class CompletionRequest(BaseModel):
    model: str
    prompt: str
    max_tokens: int = 100
    temperature: float = 0.7
    context: Optional[List[str]] = None


class ModelInfo(BaseModel):
    name: str
    description: str
    supports_streaming: bool


@app.get("/v1/models", response_model=Dict[str, ModelInfo])
async def list_models():
    """List all available models"""
    return ModelRegistry.list_models()


@app.post("/v1/completions")
async def create_completion(request: CompletionRequest):
    """Create a completion for the provided prompt and parameters"""
    try:
        with ModelContext(request.model) as context:
            if request.context:
                for ctx in request.context:
                    context.add_to_context(ctx)

            response = context.generate(
                request.prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )

            return {
                "id": "cmpl-" + str(hash(request.prompt)),
                "object": "text_completion",
                "created": int(time.time()),
                "model": request.model,
                "choices": [{
                    "text": response,
                    "index": 0,
                    "logprobs": None,
                    "finish_reason": "length"
                }]
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))