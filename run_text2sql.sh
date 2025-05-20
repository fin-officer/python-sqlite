#!/bin/bash
# run_text2sql.sh - Uproszczony skrypt do uruchamiania komponentów text2sql

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
    echo "  all         Uruchamia wszystkie komponenty (shell i API)"
    echo "  help        Wyświetla tę pomoc"
    echo ""
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
    all)
        echo "Uruchamianie wszystkich komponentów..."
        # Uruchamianie API w tle
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