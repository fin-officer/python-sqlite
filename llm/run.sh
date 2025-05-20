#!/bin/bash
# run.sh - Comprehensive script for running text2sql components

# Function to display help
show_help() {
    echo "Text2SQL - Natural language to SQL translation tool"
    echo ""
    echo "Usage:"
    echo "  ./run.sh [option]"
    echo ""
    echo "Options:"
    echo "  shell       Run the interactive SQL shell with LLM integration"
    echo "  api         Run the FastAPI REST server"
    echo "  llm         Run the SmartLLM API server"
    echo "  models      Run the model selector shell"
    echo "  all         Run all components together"
    echo "  install     Install all dependencies"
    echo "  test        Run the test suite"
    echo "  help        Display this help message"
    echo ""
}

# Function to install dependencies
install_dependencies() {
    echo "Installing dependencies..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
    else
        source venv/bin/activate
    fi
    
    # Install dependencies
    pip install -r requirements.txt
    
    echo "Dependencies installed successfully!"
}

# Function to create default database
create_database() {
    if [ ! -f "database.db" ]; then
        echo "Creating default database..."
        sqlite3 database.db "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT);"
        sqlite3 database.db "CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL, description TEXT);"
        echo "Created default database with users and products tables"
    fi
}

# Function to check if a package is installed
check_package() {
    if python -c "import $1" &>/dev/null; then
        return 0  # Installed
    else
        return 1  # Not installed
    fi
}

# Activate virtual environment if it exists
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Funkcja do wyświetlania pomocy
show_help() {
    echo "Text2SQL Extended - Narzędzie do tłumaczenia języka naturalnego na SQL"
    echo ""
    echo "Użycie:"
    echo "  ./run.sh [opcja]"
    echo ""
    echo "Opcje:"
    echo "  shell       Uruchamia rozszerzony interaktywny shell"
    echo "  api         Uruchamia rozszerzony serwer API REST"
    echo "  llm         Uruchamia serwer SmartLLM API"
    echo "  all         Uruchamia wszystkie komponenty razem"
    echo "  help        Wyświetla tę pomoc"
    echo ""
}

# Aktywacja wirtualnego środowiska, jeśli istnieje
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Sprawdź, czy pakiet transformers jest zainstalowany
check_transformers() {
    if python3 -c "import transformers" &>/dev/null; then
        return 0  # Zainstalowany
    else
        return 1  # Nie zainstalowany
    fi
}

# Obsługa argumentów
case "$1" in
    shell)
        echo "Uruchamianie rozszerzonego interaktywnego shella..."
        python3 cli_client.py
        ;;
    api)
        echo "Uruchamianie rozszerzonego serwera API REST..."
        python3 rest_api.py
        ;;
    llm)
        echo "Uruchamianie serwera SmartLLM API..."
        if check_transformers; then
            python3 smart_llm.py --server
        else
            echo "Błąd: Pakiet transformers nie jest zainstalowany."
            echo "Zainstaluj go używając: pip install transformers"
            exit 1
        fi
        ;;
    all)
        echo "Uruchamianie wszystkich komponentów..."

        # Uruchamianie SmartLLM w tle (jeśli zainstalowany)
        if check_transformers; then
            echo "Uruchamianie serwera SmartLLM API..."
            python3 smart_llm.py --server --port 8080 &
            llm_pid=$!
            sleep 3  # Daj czas na uruchomienie
        else
            echo "UWAGA: Pakiet transformers nie jest zainstalowany. Tryb SmartLLM będzie ograniczony."
            llm_pid=""
        fi

        # Uruchamianie API REST w tle
        echo "Uruchamianie rozszerzonego serwera API REST..."
        python3 rest_api.py --port 8000 &
        api_pid=$!

        # Uruchamianie shella w pierwszym planie
        echo "Uruchamianie rozszerzonego interaktywnego shella..."
        python3 cli_client.py --llm-url http://localhost:8080

        # Zatrzymywanie procesów uruchomionych w tle
        if [ -n "$api_pid" ]; then
            echo "Zatrzymywanie serwera API..."
            kill $api_pid 2>/dev/null || true
        fi

        if [ -n "$llm_pid" ]; then
            echo "Zatrzymywanie serwera SmartLLM..."
            kill $llm_pid 2>/dev/null || true
        fi
        ;;
    help|*)
        show_help
        ;;
esac