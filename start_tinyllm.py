# start_tinyllm.py - Skrypt do uruchomienia serwisu TinyLLM

import os
import sys
import argparse
import subprocess
import time
from pathlib import Path

# Domyślny model do użycia (mały model, który może działać na CPU)
DEFAULT_MODEL = "TinyLlama-1.1B-Chat-v1.0"
DEFAULT_PORT = 8080


def check_dependencies():
    """Sprawdza, czy wymagane zależności są zainstalowane"""
    dependencies = ["pip", "python"]

    for dep in dependencies:
        try:
            subprocess.run([dep, "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except (subprocess.SubprocessError, FileNotFoundError):
            print(f"Błąd: {dep} nie jest zainstalowany lub nie znajduje się w PATH")
            return False

    return True


def install_packages():
    """Instaluje wymagane pakiety"""
    packages = ["llama-cpp-python", "fastapi", "uvicorn", "huggingface_hub"]

    print(f"Instalowanie wymaganych pakietów: {', '.join(packages)}")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install"] + packages, check=True)
        return True
    except subprocess.SubprocessError as e:
        print(f"Błąd instalacji pakietów: {e}")
        return False


def start_tinyllm_server(model_path, port):
    """Uruchamia serwer TinyLLM"""
    server_code = """
import sys
import os
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
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

# Ładowanie modelu
model_path = "{model_path}"
model_name = os.path.basename(model_path)

print(f"Ładowanie modelu z {model_path}...")

try:
    # Znajdź plik .gguf w katalogu modelu
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
except Exception as e:
    print(f"Błąd ładowania modelu: {e}")
    sys.exit(1)

@app.get("/")
def read_root():
    return {"message": "TinyLLM API is running", "model": model_name}

@app.post("/v1/completions", response_model=CompletionResponse)
async def create_completion(request: CompletionRequest):
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
            id=f"cmpl-{{hash(text) & 0xffffffff}}", 
            created=int(time.time()),
            model=model_name,
            choices=[CompletionChoice(text=text)]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Uruchom serwer
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port={port})
    """.format(model_path=model_path, port=port)

    # Zapisz kod serwera do pliku
    server_file = "tinyllm_server.py"
    with open(server_file, "w") as f:
        f.write(server_code)

    # Uruchom serwer
    print(f"Uruchamianie serwera TinyLLM na porcie {port}...")
    process = subprocess.Popen([sys.executable, server_file])

    # Poczekaj na uruchomienie serwera
    print("Czekanie na uruchomienie serwera...")
    time.sleep(5)

    return process


def main():
    parser = argparse.ArgumentParser(description='Uruchomienie serwisu TinyLLM')
    parser.add_argument('--model', default=DEFAULT_MODEL, help='Nazwa modelu do użycia')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help='Port, na którym uruchomić serwer')
    parser.add_argument('--model-dir', default='./models', help='Katalog przechowywania modeli')
    args = parser.parse_args()

    print("Konfiguracja serwisu TinyLLM...")

    # Sprawdź zależności
    if not check_dependencies():
        sys.exit(1)

    # Zainstaluj wymagane pakiety
    if not install_packages():
        sys.exit(1)

    # Przygotuj ścieżkę do modelu
    model_path = os.path.join(args.model_dir, args.model)
    os.makedirs(model_path, exist_ok=True)

    # Pobierz model z HuggingFace, jeśli to konieczne
    try:
        print(f"Sprawdzanie modelu {args.model}...")
        import huggingface_hub

        # Sprawdź, czy katalog modelu istnieje i czy zawiera pliki modelu
        if not any(Path(model_path).glob("*.gguf")) and not any(Path(model_path).glob("*.bin")):
            print(f"Pobieranie modelu {args.model} do {model_path}...")
            huggingface_hub.snapshot_download(
                repo_id=f"TinyLlama/{args.model}",
                local_dir=model_path
            )
    except Exception as e:
        print(f"Ostrzeżenie: Nie udało się pobrać modelu: {e}")
        print("Kontynuowanie bez pobierania modelu...")

    # Uruchom serwer
    server_process = start_tinyllm_server(model_path, args.port)

    print(f"Serwis TinyLLM działa na http://localhost:{args.port}")
    print("Naciśnij Ctrl+C, aby zatrzymać serwis")

    try:
        server_process.wait()
    except KeyboardInterrupt:
        print("Zatrzymywanie serwisu TinyLLM...")
        server_process.terminate()
        server_process.wait()


if __name__ == "__main__":
    main()