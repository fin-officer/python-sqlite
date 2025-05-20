#!/bin/bash
# quick_start.sh - Skrypt szybkiego startu dla Text2SQL

set -e

# Ustawienia kolorów dla lepszej czytelności
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}    Text2SQL - Szybki Start      ${NC}"
echo -e "${BLUE}=================================${NC}"
echo

# Funkcja do wyświetlania bannera
show_banner() {
    echo -e "${YELLOW}$1${NC}"
    echo -e "${YELLOW}$(printf '=%.0s' $(seq 1 ${#1}))${NC}"
}

# Funkcja do sprawdzania zależności
check_dependency() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}✗ $1 nie jest zainstalowany${NC}"
        return 1
    else
        echo -e "${GREEN}✓ $1 jest zainstalowany${NC}"
        return 0
    fi
}

# Sprawdź podstawowe zależności
show_banner "Sprawdzanie podstawowych zależności"
check_dependency python3 || {
    echo -e "${RED}Python 3 jest wymagany do działania Text2SQL.${NC}"
    echo -e "${YELLOW}Zainstaluj Python 3 i spróbuj ponownie.${NC}"
    exit 1
}
check_dependency pip3 || {
    echo -e "${YELLOW}pip3 nie jest zainstalowany. Spróbuję go zainstalować...${NC}"
    python3 -m ensurepip --upgrade || {
        echo -e "${RED}Nie udało się zainstalować pip3.${NC}"
        echo -e "${YELLOW}Zainstaluj go ręcznie i spróbuj ponownie.${NC}"
        exit 1
    }
}
echo

# Sprawdź, czy pliki projektu istnieją
show_banner "Sprawdzanie plików projektu"
required_files=("cli_client.py" "rest_api.py" "smart_llm.py")
missing_files=()

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}✗ Brak pliku: $file${NC}"
        missing_files+=("$file")
    else
        echo -e "${GREEN}✓ Znaleziono plik: $file${NC}"
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo -e "${RED}Brakuje niektórych plików projektu.${NC}"
    echo -e "${YELLOW}Upewnij się, że wszystkie pliki są dostępne przed kontynuowaniem.${NC}"

    # Pytanie o kontynuowanie mimo brakujących plików
    echo -e "${YELLOW}Czy chcesz kontynuować mimo to? (t/n)${NC}"
    read -r response
    if [[ ! "$response" =~ ^([tT][aA][kK]|[tT])$ ]]; then
        exit 1
    fi
fi
echo

# Przygotuj wirtualne środowisko
show_banner "Przygotowywanie środowiska"
if [ -d "venv" ]; then
    echo -e "${GREEN}Znaleziono istniejące wirtualne środowisko.${NC}"

    # Pytanie o aktualizację środowiska
    echo -e "${YELLOW}Czy chcesz zaktualizować wirtualne środowisko? (t/n)${NC}"
    read -r response
    if [[ "$response" =~ ^([tT][aA][kK]|[tT])$ ]]; then
        echo -e "${YELLOW}Aktualizowanie wirtualnego środowiska...${NC}"
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt || {
            echo -e "${RED}Nie udało się zainstalować zależności z requirements.txt.${NC}"
            echo -e "${YELLOW}Instalowanie podstawowych zależności...${NC}"
            pip install fastapi uvicorn pydantic requests
        }
    else
        source venv/bin/activate
    fi
else
    echo -e "${YELLOW}Tworzenie nowego wirtualnego środowiska...${NC}"
    python3 -m venv venv || {
        echo -e "${RED}Nie udało się utworzyć wirtualnego środowiska.${NC}"
        echo -e "${YELLOW}Kontynuowanie bez wirtualnego środowiska...${NC}"
    }

    if [ -d "venv" ]; then
        source venv/bin/activate
        pip install --upgrade pip

        if [ -f "requirements.txt" ]; then
            echo -e "${YELLOW}Instalowanie zależności z requirements.txt...${NC}"
            pip install -r requirements.txt || {
                echo -e "${RED}Nie udało się zainstalować zależności z requirements.txt.${NC}"
                echo -e "${YELLOW}Instalowanie podstawowych zależności...${NC}"
                pip install fastapi uvicorn pydantic requests
            }
        else
            echo -e "${YELLOW}Nie znaleziono pliku requirements.txt.${NC}"
            echo -e "${YELLOW}Instalowanie podstawowych zależności...${NC}"
            pip install fastapi uvicorn pydantic requests
        fi
    fi
fi
echo

# Nadaj uprawnienia wykonywania
show_banner "Nadawanie uprawnień"
echo -e "${YELLOW}Nadawanie uprawnień wykonywania skryptom...${NC}"
chmod +x *.py *.sh 2>/dev/null || echo -e "${YELLOW}Nie udało się nadać uprawnień niektórym plikom.${NC}"
echo

# Menu główne
show_banner "Menu główne"
echo "Wybierz, co chcesz zrobić:"
echo "1. Uruchom interaktywny shell"
echo "2. Uruchom API REST"
echo "3. Uruchom serwer SmartLLM"
echo "4. Uruchom wszystkie komponenty"
echo "5. Uruchom testy (jeśli dostępne)"
echo "0. Wyjście"

read -r option
case $option in
    1)
        show_banner "Uruchamianie interaktywnego shella"
        if [ -f "cli_client.py" ]; then
            python cli_client.py
        else
            echo -e "${RED}Nie znaleziono pliku cli_client.py.${NC}"
            exit 1
        fi
        ;;
    2)
        show_banner "Uruchamianie API REST"
        if [ -f "rest_api.py" ]; then
            python rest_api.py
        else
            echo -e "${RED}Nie znaleziono pliku rest_api.py.${NC}"
            exit 1
        fi
        ;;
    3)
        show_banner "Uruchamianie serwera SmartLLM"
        if [ -f "smart_llm.py" ]; then
            # Sprawdź, czy transformers jest zainstalowany
            python -c "import transformers" 2>/dev/null || {
                echo -e "${YELLOW}Pakiet transformers nie jest zainstalowany.${NC}"
                echo -e "${YELLOW}Próba instalacji...${NC}"
                pip install transformers || {
                    echo -e "${RED}Nie udało się zainstalować pakietu transformers.${NC}"
                    echo -e "${YELLOW}Serwer SmartLLM będzie działał w trybie ograniczonym.${NC}"
                }
            }

            python smart_llm.py --server
        else
            echo -e "${RED}Nie znaleziono pliku smart_llm.py.${NC}"
            exit 1
        fi
        ;;
    4)
        show_banner "Uruchamianie wszystkich komponentów"
        if [ -f "run.sh" ]; then
            ./run.sh all
        else
            echo -e "${YELLOW}Nie znaleziono pliku run.sh.${NC}"
            echo -e "${YELLOW}Uruchamianie komponentów ręcznie...${NC}"

            # Uruchom SmartLLM w tle
            if [ -f "smart_llm.py" ]; then
                echo -e "${YELLOW}Uruchamianie serwera SmartLLM...${NC}"
                python smart_llm.py --server --port 8080 &
                llm_pid=$!
                sleep 3
            else
                echo -e "${RED}Nie znaleziono pliku smart_llm.py.${NC}"
                llm_pid=""
            fi

            # Uruchom API REST w tle
            if [ -f "rest_api.py" ]; then
                echo -e "${YELLOW}Uruchamianie API REST...${NC}"
                python rest_api.py --port 8000 &
                api_pid=$!
            else
                echo -e "${RED}Nie znaleziono pliku rest_api.py.${NC}"
                api_pid=""
            fi

            # Uruchom klienta CLI
            if [ -f "cli_client.py" ]; then
                echo -e "${YELLOW}Uruchamianie interaktywnego shella...${NC}"
                python cli_client.py --llm-url http://localhost:8080
            else
                echo -e "${RED}Nie znaleziono pliku cli_client.py.${NC}"
            fi

            # Zatrzymaj procesy w tle
            if [ -n "$api_pid" ]; then
                echo -e "${YELLOW}Zatrzymywanie API REST...${NC}"
                kill $api_pid 2>/dev/null || true
            fi

            if [ -n "$llm_pid" ]; then
                echo -e "${YELLOW}Zatrzymywanie serwera SmartLLM...${NC}"
                kill $llm_pid 2>/dev/null || true
            fi
        fi
        ;;
    5)
        show_banner "Uruchamianie testów"
        if [ -f "test_text2sql.sh" ]; then
            ./test_text2sql.sh
        elif [ -f "prepare_and_run_tests.sh" ]; then
            ./prepare_and_run_tests.sh
        else
            echo -e "${RED}Nie znaleziono plików testowych.${NC}"
            exit 1
        fi
        ;;
    0|*)
        echo -e "${BLUE}Dziękujemy za korzystanie z Text2SQL!${NC}"
        exit 0
        ;;
esac

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}    Koniec działania skryptu     ${NC}"
echo -e "${BLUE}=================================${NC}"