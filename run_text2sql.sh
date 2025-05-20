#!/bin/bash
# run_text2sql.sh - Zaktualizowany skrypt do uruchamiania komponentów text2sql

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
    echo "  tinyllm     Uruchamia serwis TinyLLM (jeśli zainstalowany)"
    echo "  all         Uruchamia wszystkie komponenty (z TinyLLM, jeśli zainstalowany)"
    echo "  simple      Uruchamia komponenty w trybie prostym (bez TinyLLM)"
    echo "  help        Wyświetla tę pomoc"
    echo ""
}

# Sprawdź, czy llama-cpp-python jest zainstalowany
check_tinyllm() {
    if python3 -c "import llama_cpp" &>/dev/null; then
        return 0  # Zainstalowany
    else
        return 1  # Nie zainstalowany
    fi
}

# Aktywacja wirtualnego środowiska, jeśli istnieje
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Obsługa argumentów
case "$1" in
    shell)
        echo "Uruchamianie interaktywnego shella..."
        python3 cli_client.py
        ;;
    api)
        echo "Uruchamianie serwera API REST..."
        python3 rest_api.py
        ;;
    tinyllm)
        if check_tinyllm; then
            echo "Uruchamianie serwisu TinyLLM..."
            python3 start_tinyllm.py
        else
            echo "Błąd: TinyLLM (llama-cpp-python) nie jest zainstalowany."
            echo "Zainstaluj go używając skryptu install_dependencies.sh."
            exit 1
        fi
        ;;
    all)
        if check_tinyllm; then
            echo "Uruchamianie wszystkich komponentów z TinyLLM..."
            # Uruchamianie w tle
            python3 start_tinyllm.py &
            tinyllm_pid=$!
            sleep 5

            python3 rest_api.py &
            api_pid=$!

            # Uruchamianie shella w pierwszym planie
            python3 cli_client.py

            # Zatrzymywanie procesów uruchomionych w tle
            kill $api_pid $tinyllm_pid 2>/dev/null || true
        else
            echo "UWAGA: TinyLLM nie jest zainstalowany. Uruchamianie w trybie prostym..."
            python3 rest_api.py &
            api_pid=$!

            # Uruchamianie shella w pierwszym planie
            python3 cli_client.py

            # Zatrzymywanie procesów uruchomionych w tle
            kill $api_pid 2>/dev/null || true
        fi
        ;;
    simple)
        echo "Uruchamianie komponentów w trybie prostym (bez TinyLLM)..."
        python3 rest_api.py &
        api_pid=$!

        # Uruchamianie shella w pierwszym planie
        python3 cli_client.py

        # Zatrzymywanie procesów uruchomionych w tle
        kill $api_pid 2>/dev/null || true
        ;;
    help|*)
        show_help
        ;;
esac