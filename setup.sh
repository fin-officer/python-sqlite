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

# Tworzenie katalogu projektu, jeśli nie istnieje
mkdir -p text2sql_mcp
cd text2sql_mcp

# Sprawdzenie, czy pliki projektu istnieją w bieżącym katalogu
files_to_check=("mcp_server.py" "cli_client.py" "rest_api.py" "tinyllm_client.py" "start_tinyllm.py")
all_files_exist=true

for file in "${files_to_check[@]}"; do
    if [ ! -f "$file" ]; then
        all_files_exist=false
        break
    fi
done

if [ "$all_files_exist" = true ]; then
    echo "Pliki projektu już istnieją w bieżącym katalogu."
else
    echo "Pobieranie plików projektu..."
    # W rzeczywistej implementacji tutaj byłoby pobieranie plików z repozytorium
    # Dla uproszczenia, zakładamy, że pliki już są dostępne
    echo "UWAGA: Pliki projektu muszą być dostępne w bieżącym katalogu."
fi

# Nadawanie uprawnień wykonywania skryptom
echo "Nadawanie uprawnień wykonywania skryptom..."
chmod +x mcp_server.py cli_client.py rest_api.py tinyllm_client.py start_tinyllm.py

# Tworzenie skryptu pomocniczego do uruchamiania
cat > run_text2sql.sh << 'EOF'
#!/bin/bash

# Funkcja do wyświetlania pomocy
show_help() {
    echo "Text2SQL - Narzędzie do tłumaczenia języka naturalnego na SQL"
    echo ""
    echo "Użycie:"
    echo "  ./run_text2sql.sh [opcja]"
    echo ""
    echo "Opcje:"
    echo "  shell       Uruchamia interaktywny shell"
    echo "  api         Uruchamia serwer API REST"
    echo "  tinyllm     Uruchamia serwis TinyLLM"
    echo "  all         Uruchamia wszystkie komponenty"
    echo "  help        Wyświetla tę pomoc"
    echo ""
}

# Aktywacja wirtualnego środowiska
source venv/bin/activate

# Obsługa argumentów
case "$1" in
    shell)
        echo "Uruchamianie interaktywnego shella..."
        python cli_client.py
        ;;
    api)
        echo "Uruchamianie serwera API REST..."
        python rest_api.py
        ;;
    tinyllm)
        echo "Uruchamianie serwisu TinyLLM..."
        python start_tinyllm.py
        ;;
    all)
        echo "Uruchamianie wszystkich komponentów..."
        # Uruchamianie w tle
        python start_tinyllm.py &
        tinyllm_pid=$!
        sleep 5

        python rest_api.py &
        api_pid=$!

        # Uruchamianie shella w pierwszym planie
        python cli_client.py

        # Zatrzymywanie procesów uruchomionych w tle
        kill $api_pid $tinyllm_pid
        ;;
    help|*)
        show_help
        ;;
esac
EOF

chmod +x run_text2sql.sh

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