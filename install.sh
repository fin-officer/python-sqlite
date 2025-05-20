#!/bin/bash
# install_dependencies.sh - Skrypt do instalacji zależności projektu text2sql

set -e

echo "Instalacja zależności projektu text2sql..."

# Sprawdź, czy requirements.txt istnieje
if [ ! -f "requirements.txt" ]; then
    echo "Błąd: Plik requirements.txt nie istnieje."
    exit 1
fi

# Sprawdź, czy Python jest zainstalowany
if ! command -v python3 &> /dev/null; then
    echo "Błąd: Python 3 nie jest zainstalowany. Zainstaluj go przed kontynuowaniem."
    exit 1
fi

# Instalacja pakietów systemowych na Fedora (jeśli to potrzebne)
if command -v dnf &> /dev/null; then
    echo "Wykryto system Fedora, instalacja pakietów systemowych..."
    sudo dnf install -y python3-devel sqlite-devel gcc gcc-c++
elif command -v apt-get &> /dev/null; then
    echo "Wykryto system z APT, instalacja pakietów systemowych..."
    sudo apt-get update
    sudo apt-get install -y python3-dev libsqlite3-dev gcc g++
fi

# Instalacja zależności Pythona
echo "Instalacja zależności Pythona..."

# Sprawdź, czy pip jest zainstalowany
if ! command -v pip3 &> /dev/null; then
    echo "Instalacja pip..."
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py
    rm get-pip.py
fi

# Instalacja zależności z requirements.txt
echo "Instalacja pakietów z requirements.txt..."
pip3 install -r requirements.txt

echo
echo "Zależności zostały pomyślnie zainstalowane!"
echo