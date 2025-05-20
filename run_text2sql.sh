#!/bin/bash
# run_text2sql.sh - Skrypt do uruchamiania komponentów text2sql

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