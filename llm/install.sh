#!/bin/bash
# install.sh - Rozszerzony skrypt instalacyjny dla text2sql

set -e

echo "Instalacja rozszerzonej wersji text2sql..."

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

# Sprawdzenie, czy plik requirements.txt istnieje
if [ ! -f "requirements.txt" ]; then
    echo "Tworzenie pliku requirements.txt..."
    cat > requirements.txt << EOL
# Podstawowe zależności
fastapi>=0.104.0
uvicorn>=0.23.0
pydantic>=2.0.0
requests>=2.31.0

# Zależności dla LLM (bez llama-cpp-python)
huggingface_hub>=0.19.0
transformers>=4.35.0
sentence-transformers>=2.2.2
EOL
fi

# Instalacja zależności Pythona
echo "Instalacja zależności Pythona..."
pip install --upgrade pip
pip install -r requirements.txt

# Opcjonalna instalacja transformers z cuda
read -p "Czy chcesz zainstalować wsparcie dla CUDA w transformers? (t/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Tt]$ ]]; then
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
fi

# Sprawdzenie, czy wszystkie pliki istnieją
files=(
    "smart_llm.py"
    "cli_client.py"
    "rest_api.py"
    "run.sh"
)

missing=()
for file in "${files[@]}"; do
    if [ ! -f "$file" ]; then
        missing+=("$file")
    fi
done

if [ ${#missing[@]} -gt 0 ]; then
    echo "UWAGA: Brakuje następujących plików projektu:"
    for file in "${missing[@]}"; do
        echo "  - $file"
    done
    echo "Upewnij się, że wszystkie pliki projektu są dostępne przed kontynuowaniem."
    exit 1
fi

# Nadawanie uprawnień wykonywania skryptom
echo "Nadawanie uprawnień wykonywania skryptom..."
chmod +x smart_llm.py cli_client.py rest_api.py run.sh

echo
echo "Instalacja zakończona pomyślnie!"
echo
echo "Aby uruchomić rozszerzone text2sql:"
echo
echo "1. Aktywuj wirtualne środowisko:"
echo "   source venv/bin/activate"
echo
echo "2. Uruchom rozszerzony interaktywny shell:"
echo "   ./run.sh shell"
echo
echo "3. Lub uruchom rozszerzone API REST:"
echo "   ./run.sh api"
echo
echo "4. Lub uruchom serwer SmartLLM API:"
echo "   ./run.sh llm"
echo
echo "5. Lub uruchom wszystko naraz:"
echo "   ./run.sh all"
echo
echo "Przykładowe komendy w interaktywnym shellu:"
echo "- create a user named John"
echo "- show all users"
echo "- create a product named Laptop price 999.99"
echo "- show all products"
echo "- find user with name John"
echo "- update user with id 1 set name to Mike"
echo "- delete user with id 2"
echo "- create table employees"
echo