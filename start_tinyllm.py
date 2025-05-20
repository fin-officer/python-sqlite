#!/usr/bin/env python3
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
    # Sprawdź, czy plik serwera istnieje
    server_file = "tinyllm_server.py"
    if not os.path.exists(server_file):
        print(f"Błąd: Plik serwera {server_file} nie istnieje")
        return None

    # Uruchom serwer
    print(f"Uruchamianie serwera TinyLLM na porcie {port}...")
    process = subprocess.Popen([
        sys.executable,
        server_file,
        "--model-path", model_path,
        "--port", str(port)
    ])

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
    if not server_process:
        sys.exit(1)

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