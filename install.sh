#!/bin/bash
# install.sh - Uproszczony skrypt instalacyjny dla text2sql

set -e

echo "Instalacja zależności projektu text2sql..."

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

# Tworzenie wirtualnego środowiska - prosta metoda
echo "Tworzenie wirtualnego środowiska Python..."
if [ -d "venv" ]; then
    echo "Wirtualne środowisko już istnieje, pomijanie..."
else
    python3 -m venv venv || {
        echo "Błąd przy tworzeniu środowiska wirtualnego. Spróbuj ręcznie:"
        echo "python3 -m venv venv"
        exit 1
    }
fi

# Aktywacja środowiska
source venv/bin/activate || {
    echo "Nie udało się aktywować środowiska wirtualnego."
    exit 1
}

# Instalacja zależności Pythona
echo "Instalacja zależności Pythona..."
pip install --upgrade pip
pip install fastapi uvicorn pydantic requests

# Nadawanie uprawnień wykonywania skryptom
echo "Nadawanie uprawnień wykonywania skryptom..."
chmod +x cli_client.py rest_api.py run_text2sql.sh

echo
echo "Instalacja zakończona pomyślnie!"
echo
echo "Aby uruchomić text2sql:"
echo
echo "1. Aktywuj wirtualne środowisko:"
echo "   source venv/bin/activate"
echo
echo "2. Uruchom interaktywny shell:"
echo "   ./run_text2sql.sh shell"
echo
echo "3. Lub uruchom API REST:"
echo "   ./run_text2sql.sh api"
echo
echo "4. Lub uruchom wszystko naraz:"
echo "   ./run_text2sql.sh all"
echo
echo "Przykładowe komendy w interaktywnym shellu:"
echo "- create a user named John"
echo "- show all users"
echo "- create a product named Laptop price 999.99"
echo "- show all products"
echo