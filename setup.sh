#!/bin/bash
# setup.sh - Skrypt instalacyjny dla text2sql na Fedora

set -e

echo "Konfiguracja text2sql na Fedora..."

# Sprawdź, czy skrypt jest uruchamiany jako root
if [ "$(id -u)" -eq 0 ]; then
    echo "Proszę uruchomić ten skrypt jako zwykły użytkownik, nie jako root."
    exit 1
fi

# Instalacja zależności systemowych
echo "Instalacja zależności systemowych..."
sudo dnf install -y python3 python3-pip python3-devel sqlite sqlite-devel gcc gcc-c++

# Tworzenie wirtualnego środowiska
echo "Tworzenie wirtualnego środowiska Python..."
python3 -m venv venv
source venv/bin/activate

# Instalacja zależności Pythona
echo "Instalacja zależności Pythona..."
pip install --upgrade pip
pip install mcp fastapi uvicorn pydantic requests

# Sprawdzenie, czy pliki projektu istnieją w bieżącym katalogu
files_to_check=(
    "mcp_server.py"
    "cli_client.py"
    "rest_api.py"
    "tinyllm_client.py"
    "start_tinyllm.py"
    "tinyllm_server.py"
    "run_text2sql.sh"
    "test_text2sql.py"
    "README.md"
)

missing_files=()
for file in "${files_to_check[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo "UWAGA: Brakuje następujących plików projektu:"
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
    echo "Upewnij się, że wszystkie pliki projektu są dostępne przed kontynuowaniem."
    read -p "Czy chcesz kontynuować mimo to? (t/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Tt]$ ]]; then
        exit 1
    fi
fi

# Nadawanie uprawnień wykonywania skryptom
echo "Nadawanie uprawnień wykonywania skryptom..."
chmod +x mcp_server.py cli_client.py rest_api.py tinyllm_client.py start_tinyllm.py tinyllm_server.py run_text2sql.sh

echo
echo "Instalacja zakończona pomyślnie!"
echo
echo "Aby uruchomić text2sql:"
echo
echo "1. Uruchom serwis TinyLLM (w osobnym terminalu):"
echo "   ./run_text2sql.sh tinyllm"
echo
echo "2. Uruchom interfejs API REST (opcjonalnie, w osobnym terminalu):"
echo "   ./run_text2sql.sh api"
echo
echo "3. Uruchom interaktywny shell:"
echo "   ./run_text2sql.sh shell"
echo
echo "Lub uruchom wszystko naraz:"
echo "   ./run_text2sql.sh all"
echo
echo "Przykładowe komendy w interaktywnym shellu:"
echo "- create a user named John"
echo "- show all users"
echo "- create a product named Laptop price 999.99"
echo "- show all products"
echo