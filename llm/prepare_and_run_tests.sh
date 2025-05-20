#!/bin/bash
# prepare_and_run_tests.sh - Skrypt przygotowujący i uruchamiający testy dla Text2SQL

set -e

# Ustawienia kolorów dla lepszej czytelności
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Text2SQL - Przygotowanie i uruchomienie testów ===${NC}"

# Sprawdź, czy wszystkie wymagane pliki istnieją
required_files=("cli_client.py" "rest_api.py" "smart_llm.py" "test_text2sql.sh" "update_client_for_testing.py")
missing_files=()

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo -e "${RED}Brakuje następujących plików:${NC}"
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
    echo "Upewnij się, że wszystkie pliki są dostępne przed kontynuowaniem."
    exit 1
fi

# Nadaj uprawnienia wykonywania wszystkim skryptom
echo -e "${YELLOW}Nadawanie uprawnień wykonywania skryptom...${NC}"
chmod +x *.py *.sh

# Sprawdź, czy Python jest zainstalowany
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 nie jest zainstalowany. Zainstaluj go przed kontynuowaniem.${NC}"
    exit 1
fi

# Sprawdź, czy istnieje wirtualne środowisko
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    echo -e "${GREEN}Znaleziono wirtualne środowisko.${NC}"
    source venv/bin/activate
else
    echo -e "${YELLOW}Nie znaleziono wirtualnego środowiska. Czy chcesz je utworzyć? (t/n)${NC}"
    read -r response
    if [[ "$response" =~ ^([tT][aA][kK]|[tT])$ ]]; then
        echo -e "${YELLOW}Tworzenie wirtualnego środowiska...${NC}"
        python3 -m venv venv
        source venv/bin/activate
    else
        echo -e "${YELLOW}Kontynuowanie bez wirtualnego środowiska...${NC}"
    fi
fi

# Sprawdź i zainstaluj zależności
echo -e "${YELLOW}Sprawdzanie zależności...${NC}"
if [ -f "requirements.txt" ]; then
    # Instaluj tylko brakujące zależności
    echo -e "${YELLOW}Instalowanie zależności z requirements.txt...${NC}"
    pip install -r requirements.txt
else
    echo -e "${RED}Nie znaleziono pliku requirements.txt.${NC}"
    echo -e "${YELLOW}Instalowanie podstawowych zależności...${NC}"
    pip install fastapi uvicorn pydantic requests
fi

# Aktualizuj klienta CLI dla trybu nieinteraktywnego
echo -e "${YELLOW}Aktualizowanie klienta CLI do trybu nieinteraktywnego...${NC}"
python update_client_for_testing.py

# Uruchom testy
echo -e "${YELLOW}Uruchamianie testów...${NC}"
./test_text2sql.sh

# Sprawdź kod wyjścia testów
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Wszystkie testy zakończone pomyślnie!${NC}"

    # Zapytaj, czy użytkownik chce uruchomić aplikację
    echo -e "${YELLOW}Czy chcesz teraz uruchomić Text2SQL? (t/n)${NC}"
    read -r response
    if [[ "$response" =~ ^([tT][aA][kK]|[tT])$ ]]; then
        echo -e "${YELLOW}Dostępne opcje:${NC}"
        echo "1. Uruchom interaktywny shell"
        echo "2. Uruchom API REST"
        echo "3. Uruchom serwer SmartLLM"
        echo "4. Uruchom wszystkie komponenty"
        echo "0. Anuluj"

        read -r option
        case $option in
            1)
                echo -e "${GREEN}Uruchamianie interaktywnego shella...${NC}"
                python cli_client.py
                ;;
            2)
                echo -e "${GREEN}Uruchamianie API REST...${NC}"
                python rest_api.py
                ;;
            3)
                echo -e "${GREEN}Uruchamianie serwera SmartLLM...${NC}"
                python smart_llm.py --server
                ;;
            4)
                echo -e "${GREEN}Uruchamianie wszystkich komponentów...${NC}"
                if [ -f "run.sh" ]; then
                    ./run.sh all
                else
                    echo -e "${RED}Nie znaleziono pliku run.sh.${NC}"
                    echo -e "${YELLOW}Uruchamianie wszystkich komponentów ręcznie...${NC}"

                    # Uruchom SmartLLM w tle
                    python smart_llm.py --server --port 8080 &
                    llm_pid=$!
                    sleep 3

                    # Uruchom API REST w tle
                    python rest_api.py --port 8000 &
                    api_pid=$!

                    # Uruchom klienta CLI
                    python cli_client.py --llm-url http://localhost:8080

                    # Zatrzymaj procesy w tle
                    kill $api_pid $llm_pid 2>/dev/null || true
                fi
                ;;
            0|*)
                echo -e "${YELLOW}Anulowano uruchomienie.${NC}"
                ;;
        esac
    fi
else
    echo -e "${RED}Niektóre testy nie powiodły się.${NC}"
    echo -e "${YELLOW}Sprawdź logi testów, aby zidentyfikować problem.${NC}"
fi

echo -e "${YELLOW}=== Koniec skryptu ===${NC}"