#!/bin/bash
# install_simple.sh - Prosty skrypt instalacyjny bez TinyLLM

set -e

echo "Instalacja podstawowych zależności projektu text2sql (bez TinyLLM)..."

# Sprawdź, czy requirements-simple.txt istnieje
if [ ! -f "requirements-simple.txt" ]; then
    echo "Tworzenie pliku requirements-simple.txt..."
    cat > requirements-simple.txt << EOL
# Podstawowe zależności
mcp>=0.1.0
fastapi>=0.104.0
uvicorn>=0.23.0
pydantic>=2.0.0
requests>=2.31.0

# Zależności testowe
pytest>=7.0.0
pytest-asyncio>=0.21.0
EOL
fi

# Sprawdź, czy Python jest zainstalowany
if ! command -v python3 &> /dev/null; then
    echo "Błąd: Python 3 nie jest zainstalowany. Zainstaluj go przed kontynuowaniem."
    exit 1
fi

# Instalacja pakietów systemowych na Fedora
if command -v dnf &> /dev/null; then
    echo "Wykryto system Fedora, instalacja pakietów systemowych..."
    sudo dnf install -y python3-devel sqlite-devel gcc gcc-c++
elif command -v apt-get &> /dev/null; then
    echo "Wykryto system z APT, instalacja pakietów systemowych..."
    sudo apt-get update
    sudo apt-get install -y python3-dev libsqlite3-dev gcc g++
fi

# Instalacja zależności Pythona
echo "Instalacja podstawowych zależności Pythona..."

# Sprawdź, czy pip jest zainstalowany
if ! command -v pip3 &> /dev/null; then
    echo "Instalacja pip..."
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py
    rm get-pip.py
fi

# Instalacja standardowych zależności bez TinyLLM
echo "Instalacja pakietów z requirements-simple.txt..."
pip3 install -r requirements-simple.txt

echo
echo "Podstawowe zależności zostały pomyślnie zainstalowane!"
echo
echo "UWAGA: Ta instalacja nie zawiera TinyLLM. Funkcjonalność tłumaczenia"
echo "języka naturalnego na SQL będzie ograniczona do prostego mechanizmu"
echo "opartego na regułach."
echo