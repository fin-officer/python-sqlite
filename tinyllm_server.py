#!/usr/bin/env python3
# tinyllm_server.py - Serwer TinyLLM API

import sys
import os
import time
import argparse
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import json
from llama_cpp import Llama


# Modele danych dla API
class CompletionRequest(BaseModel):
    prompt: str
    max_tokens: int = 100
    temperature: float = 0.7
    stop: Optional[List[str]] = None


class CompletionChoice(BaseModel):
    text: str
    index: int = 0
    finish_reason: str = "stop"


class CompletionResponse(BaseModel):
    id: str
    object: str = "text_completion"
    created: int
    model: str
    choices: List[CompletionChoice]


# Inicjalizacja aplikacji FastAPI
app = FastAPI(title="TinyLLM API")

# Globalna zmienna dla modelu
llm = None
model_name = None


@app.get("/")
def read_root():
    """Endpoint powitalny"""
    return {"message": "TinyLLM API is running", "model": model_name}


@app.post("/v1/completions", response_model=CompletionResponse)
async def create_completion(request: CompletionRequest):
    """Endpoint dla uzupełniania tekstu"""
    try:
        # Uzyskaj uzupełnienie z modelu
        output = llm(
            request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stop=request.stop
        )

        # Formatuj odpowiedź
        text = output["choices"][0]["text"]

        return CompletionResponse(
            id=f"cmpl-{hash(text) & 0xffffffff}",
            created=int(time.time()),
            model=model_name,
            choices=[CompletionChoice(text=text)]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def load_model(model_path):
    """Ładuje model TinyLLM z podanej ścieżki"""
    global llm, model_name

    model_name = os.path.basename(model_path)
    print(f"Ładowanie modelu z {model_path}...")

    try:
        # Znajdź plik modelu w katalogu
        model_files = []
        for ext in [".gguf", ".bin"]:
            model_files.extend(list(Path(model_path).glob(f"*{ext}")))

        if not model_files:
            raise FileNotFoundError(f"Nie znaleziono pliku modelu w {model_path}")

        # Użyj pierwszego znalezionego pliku modelu
        model_file = str(model_files[0])
        print(f"Znaleziono plik modelu: {model_file}")

        # Załaduj model
        llm = Llama(model_path=model_file, n_ctx=2048)
        print(f"Model załadowany z {model_file}")
        return True
    except Exception as e:
        print(f"Błąd ładowania modelu: {e}")
        return False


def main():
    """Główna funkcja uruchamiająca serwer"""
    parser = argparse.ArgumentParser(description='TinyLLM Server')
    parser.add_argument('--model-path', required=True, help='Ścieżka do katalogu modelu')
    parser.add_argument('--port', type=int, default=8080, help='Port, na którym uruchomić serwer')
    parser.add_argument('--host', default='0.0.0.0', help='Host, na którym uruchomić serwer')
    args = parser.parse_args()

    # Załaduj model
    if not load_model(args.model_path):
        sys.exit(1)

    # Uruchom serwer
    print(f"Uruchamianie serwera TinyLLM na http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()