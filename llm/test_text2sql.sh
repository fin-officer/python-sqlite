#!/bin/bash
# test_text2sql.sh - Skrypt testowy dla Text2SQL

# Ustawienia kolorów dla lepszej czytelności
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Liczniki testów
PASSED=0
FAILED=0
TOTAL=0

# Funkcja uruchamiająca pojedynczy test
run_test() {
    local test_name="$1"
    local command="$2"
    local expected_output="$3"

    echo -e "${YELLOW}Test: $test_name${NC}"
    echo "Wykonywanie: $command"

    # Wykonaj komendę i zapisz wynik
    local result
    if [[ "$command" == *"python "* ]]; then
        # Dla komend Pythona
        result=$(eval "$command" 2>&1)
    else
        # Dla zapytań SQL (używamy echo, aby symulować wprowadzanie przez użytkownika)
        # Ten fragment kodu zakłada, że mamy skrypt, który przyjmuje zapytanie jako argument
        result=$(echo "$command" | python cli_client.py --non-interactive 2>&1)
    fi

    # Sprawdź, czy wynik zawiera oczekiwany output
    if echo "$result" | grep -q "$expected_output"; then
        echo -e "${GREEN}✓ Test passed${NC}"
        PASSED=$((PASSED+1))
    else
        echo -e "${RED}✗ Test failed${NC}"
        echo -e "Oczekiwano: ${YELLOW}$expected_output${NC}"
        echo -e "Otrzymano: ${RED}$result${NC}"
        FAILED=$((FAILED+1))
    fi

    TOTAL=$((TOTAL+1))
    echo "----------------------------------------"
}

# Funkcja do sprawdzenia zależności
check_dependencies() {
    echo -e "${YELLOW}Sprawdzanie zależności...${NC}"

    # Sprawdź Python
    if command -v python3 &> /dev/null; then
        echo -e "${GREEN}✓ Python jest zainstalowany${NC}"
    else
        echo -e "${RED}✗ Python nie jest zainstalowany${NC}"
        return 1
    fi

    # Sprawdź wymagane pakiety
    local required_packages=("requests" "fastapi" "pydantic" "uvicorn")
    local missing_packages=()

    for package in "${required_packages[@]}"; do
        if ! python3 -c "import $package" &> /dev/null; then
            missing_packages+=("$package")
        fi
    done

    if [ ${#missing_packages[@]} -eq 0 ]; then
        echo -e "${GREEN}✓ Wszystkie wymagane pakiety są zainstalowane${NC}"
    else
        echo -e "${RED}✗ Brakujące pakiety: ${missing_packages[*]}${NC}"
        echo "Zainstaluj brakujące pakiety używając:"
        echo "pip install -r requirements.txt"
        return 1
    fi

    return 0
}

# Funkcja do przygotowania środowiska testowego
prepare_test_environment() {
    echo -e "${YELLOW}Przygotowywanie środowiska testowego...${NC}"

    # Utwórz tymczasową bazę danych dla testów
    export TEST_DB="test_text2sql.db"

    # Usuń bazę testową, jeśli istnieje
    if [ -f "$TEST_DB" ]; then
        rm "$TEST_DB"
        echo "Usunięto istniejącą bazę testową"
    fi

    # Sprawdź, czy plik cli_client.py istnieje
    if [ ! -f "cli_client.py" ]; then
        echo -e "${RED}✗ Plik cli_client.py nie istnieje${NC}"
        return 1
    fi

    # Modyfikacja cli_client.py, aby obsługiwał tryb nieinteraktywny (jeśli potrzebne)
    # Ten krok może wymagać dostosowania do konkretnej implementacji

    echo -e "${GREEN}✓ Środowisko testowe gotowe${NC}"
    return 0
}

# Funkcja do uruchomienia wszystkich testów
run_all_tests() {
    echo -e "${YELLOW}Uruchamianie testów...${NC}"

    # Test 1: Tworzenie użytkownika
    run_test "Tworzenie użytkownika" \
        "create a user named TestUser" \
        "Query executed successfully"

    # Test 2: Pobieranie wszystkich użytkowników
    run_test "Pobieranie wszystkich użytkowników" \
        "show all users" \
        "records found"

    # Test 3: Tworzenie produktu
    run_test "Tworzenie produktu" \
        "create a product named TestProduct price 99.99" \
        "Query executed successfully"

    # Test 4: Pobieranie wszystkich produktów
    run_test "Pobieranie wszystkich produktów" \
        "show all products" \
        "records found"

    # Test 5: Wyszukiwanie użytkownika
    run_test "Wyszukiwanie użytkownika" \
        "find user with name Test" \
        "records found"

    # Test 6: Aktualizacja użytkownika
    run_test "Aktualizacja użytkownika" \
        "update user with id 1 set name to UpdatedUser" \
        "Query executed successfully"

    # Test 7: Tworzenie tabeli
    run_test "Tworzenie tabeli" \
        "create table employees" \
        "Query executed successfully"

    # Test 8: Usuwanie użytkownika
    run_test "Usuwanie użytkownika" \
        "delete user with id 1" \
        "Query executed successfully"

    # Dodatkowe testy można dodać tutaj
}

# Funkcja podsumowująca wyniki testów
summarize_results() {
    echo "=========================================="
    echo -e "${YELLOW}Podsumowanie testów:${NC}"
    echo -e "Przeprowadzono: ${TOTAL}"
    echo -e "Zaliczono: ${GREEN}${PASSED}${NC}"
    echo -e "Nie zaliczono: ${RED}${FAILED}${NC}"

    # Oblicz procent zaliczonych testów
    if [ $TOTAL -gt 0 ]; then
        local percentage=$((PASSED * 100 / TOTAL))
        echo -e "Zaliczono: ${percentage}%"
    fi

    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}Wszystkie testy zaliczone!${NC}"
        return 0
    else
        echo -e "${RED}Niektóre testy nie powiodły się.${NC}"
        return 1
    fi
}

# Główna funkcja
main() {
    echo "=========================================="
    echo "Text2SQL - Testy systemu"
    echo "=========================================="

    # Sprawdź zależności
    check_dependencies || {
        echo -e "${RED}Nie można kontynuować z powodu błędów zależności.${NC}"
        exit 1
    }

    # Przygotuj środowisko testowe
    prepare_test_environment || {
        echo -e "${RED}Nie można przygotować środowiska testowego.${NC}"
        exit 1
    }

    # Uruchom testy
    run_all_tests

    # Podsumuj wyniki
    summarize_results
    exit_code=$?

    # Usuń tymczasową bazę danych
    if [ -f "$TEST_DB" ]; then
        rm "$TEST_DB"
        echo "Usunięto tymczasową bazę danych"
    fi

    exit $exit_code
}

# Uruchom główną funkcję
main
