# SmartLLM: Natural Language to SQL with Model Context Protocol

## Overview

SmartLLM is an enhanced natural language to SQL translation system that integrates with SQLite databases. It uses language models to translate natural language queries into SQL commands and executes them against a database.

## Features

- **Multiple LLM Model Support**: Supports various models up to 2B parameters
- **Model Context Protocol Integration**: Maintains context between queries for better results
- **SQLite Database Integration**: Automatically creates and manages database tables
- **Interactive Shell**: Command-line interface for natural language queries
- **REST API**: FastAPI-based API with OpenAPI documentation
- **Error Handling**: Provides helpful suggestions when SQL queries fail

## Project Structure

```
llm/
├── api.py              # FastAPI REST API
├── db_manager.py       # Database management
├── model_selector.py   # Model selection and context management
├── shell.py           # Interactive command-line interface
├── smart_llm.py       # Core language model for translation
├── sql_helper.py      # SQL execution and error handling
├── run.sh             # Script to run various components
├── requirements.txt   # Python dependencies
└── .env.example       # Example environment variables
```

## Installation

### Prerequisites

- Python 3.8+
- SQLite3

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/fin-officer.git
   cd fin-officer/python-sqlite/llm
   ```

2. Install dependencies:
   ```bash
   ./run.sh install
   ```

3. Install specific models (optional):
   ```bash
   ./run.sh install-model t5-small  # For T5-small model
   ./run.sh install-model gpt2      # For GPT-2 model
   ./run.sh install-model llama-cpp  # For llama-cpp
   ./run.sh install-model all       # For all models
   ```

4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

## Usage

### Running the Interactive Shell

```bash
./run.sh shell
```

This starts the interactive SQL shell where you can enter natural language queries:

```
SQL> create dogs table
Generated SQL: CREATE TABLE IF NOT EXISTS dogs (
    id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

1 row(s) affected.

SQL> show all tables

users
products
orders
order_items
dogs

SQL> exit
```

### Running the API Server

```bash
./run.sh api
```

This starts the FastAPI server on http://localhost:8000. You can access the API documentation at http://localhost:8000/docs.

### Running the SmartLLM Server

```bash
./run.sh llm
```

This starts the SmartLLM server which provides natural language to SQL translation services.

### Running All Components

```bash
./run.sh all
```

This starts all components (SmartLLM server, API server, and interactive shell) together.

### Viewing Available Models

```bash
./run.sh models
```

This displays all available language models that can be used for translation.

## Environment Variables

The following environment variables can be set in the `.env` file:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| DB_PATH | Path to the SQLite database file | smart_llm.db |
| MODEL_NAME | Name of the model to use | t5-small |
| USE_ADVANCED | Whether to use advanced features | true |
| DEBUG | Enable debug mode | false |
| API_HOST | Host for the API server | 0.0.0.0 |
| API_PORT | Port for the API server | 8000 |

## Examples

### Creating Tables

```
SQL> create users table
SQL> create products table
SQL> create orders table
SQL> create custom_table with name and description
```

### Querying Data

```
SQL> show all users
SQL> find user with name John
SQL> list all products with price greater than 100
```

### Modifying Data

```
SQL> create user named John with email john@example.com
SQL> update user with id 1 set email to new@example.com
SQL> delete user with id 2
```

4. **run.sh** - Skrypt do uruchamiania komponentów
   - Opcje uruchamiania shell, api, llm lub all
   - Wykrywanie zainstalowanych zależności

5. **install.sh** - Rozszerzony skrypt instalacyjny
   - Instaluje wszystkie wymagane zależności
   - Opcja wsparcia dla CUDA (dla szybszej inferecji modeli)
   - Sprawdza, czy wszystkie pliki projektu są dostępne

6. **requirements-extended.txt** - Lista zależności
   - Podstawowe zależności (FastAPI, uvicorn, pydantic)
   - Zależności dla modeli językowych (transformers, huggingface_hub)

### Kluczowe funkcje:

1. **Szeroki zakres zapytań w języku naturalnym**:
   - Tworzenie tabel: `create table employees`
   - Tworzenie rekordów: `create a user named John with email john@example.com`
   - Wyszukiwanie: `find user with name John`
   - Aktualizacja: `update user with id 1 set name to Mike`
   - Usuwanie: `delete user with id 2`

2. **Elastyczna architektura**:
   - Można używać lokalnego SmartLLM lub zewnętrznego serwera API
   - Tryb fallback w przypadku braku wymaganych zależności
   - Pełna kontrola poprzez API REST i klienta CLI

3. **Zarządzanie bazą danych**:
   - Wyświetlanie schematu bazy danych
   - Tworzenie niestandardowych tabel
   - Szczegółowa informacja o błędach

### Jak zainstalować i uruchomić:

1. Zainstaluj rozszerzoną wersję:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

2. Aktywuj wirtualne środowisko:
   ```bash
   source venv/bin/activate
   ```

3. Uruchom wybrany komponent:
   ```bash
   # Uruchom shell
   ./run.sh shell
   
   # Uruchom API REST
   ./run.sh api
   
   # Uruchom serwer SmartLLM
   ./run.sh llm
   
   # Uruchom wszystko naraz
   ./run.sh all
   ```

4. Korzystaj z rozszerzonego zakresu zapytań:
   ```
   text2sql> create table employees
   text2sql> create a user named John with email john@example.com
   text2sql> show all users
   text2sql> find user with name Jo
   text2sql> update user with id 1 set name to Mike
   text2sql> delete user with id 2
   text2sql> schema  # Wyświetla schemat bazy danych
   ```

Ta rozszerzona wersja oferuje znacznie większe możliwości tłumaczenia języka naturalnego na SQL i pozwala na pełniejszą kontrolę nad bazą danych, jednocześnie rozwiązując problemy z zależnościami, które występowały wcześniej. Zamiast polegać na trudnych do zainstalowania komponentach TinyLLM i MCP, wykorzystuje popularniejsze i łatwiejsze w instalacji biblioteki.

# Text2SQL - Dokumentacja Użytkownika

## Spis treści
1. [Wprowadzenie](#wprowadzenie)
2. [Instalacja](#instalacja)
3. [Uruchamianie](#uruchamianie)
4. [Używanie interaktywnego shella](#używanie-interaktywnego-shella)
5. [Używanie API REST](#używanie-api-rest)
6. [Obsługiwane typy zapytań](#obsługiwane-typy-zapytań)
7. [Zaawansowane funkcje](#zaawansowane-funkcje)
8. [Rozwiązywanie problemów](#rozwiązywanie-problemów)
9. [Testowanie](#testowanie)

## Wprowadzenie

Text2SQL to narzędzie, które pozwala na tłumaczenie zapytań w języku naturalnym na SQL i wykonywanie ich na bazie danych SQLite. Dzięki temu możesz zarządzać bazą danych bez znajomości składni SQL, używając prostych poleceń w języku naturalnym.

Główne funkcje:
- Tłumaczenie zapytań z języka naturalnego na SQL
- Wykonywanie zapytań SQL na bazie danych
- Interaktywny shell do wprowadzania zapytań
- API REST do integracji z innymi aplikacjami
- Obsługa modeli językowych (LLM) do zaawansowanego tłumaczenia

## Instalacja

### Wymagania wstępne
- Python 3.8 lub nowszy
- SQLite
- Git (opcjonalnie, do klonowania repozytorium)

### Kroki instalacji

1. Sklonuj repozytorium lub pobierz pliki projektu:
   ```bash
   git clone https://github.com/yourusername/text2sql.git
   cd text2sql
   ```

2. Zainstaluj zależności przy użyciu skryptu instalacyjnego:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

Alternatywnie, możesz ręcznie zainstalować zależności:
   ```bash
   # Stwórz wirtualne środowisko (opcjonalnie, ale zalecane)
   python -m venv venv
   source venv/bin/activate  # Na Linuxie/macOS
   # lub
   venv\Scripts\activate  # Na Windows
   
   # Zainstaluj zależności
   pip install -r requirements.txt
   ```

## Uruchamianie

Po zainstalowaniu zależności możesz uruchomić Text2SQL na kilka sposobów:

### Używając skryptu run.sh

```bash
# Aktywuj wirtualne środowisko, jeśli zostało utworzone
source venv/bin/activate

# Uruchom interaktywny shell
./run.sh shell

# Uruchom API REST
./run.sh api

# Uruchom serwer SmartLLM
./run.sh llm

# Uruchom wszystkie komponenty
./run.sh all
```

### Ręczne uruchamianie komponentów

```bash
# Aktywuj wirtualne środowisko, jeśli zostało utworzone
source venv/bin/activate

# Uruchom interaktywny shell
python cli_client.py

# Uruchom API REST
python rest_api.py

# Uruchom serwer SmartLLM
python smart_llm.py --server
```

## Używanie interaktywnego shella

Interaktywny shell to najprostszy sposób na korzystanie z Text2SQL. Po uruchomieniu zobaczysz prompt `text2sql>`, w którym możesz wprowadzać zapytania w języku naturalnym.

### Podstawowe komendy

```
text2sql> create a user named John
text2sql> show all users
text2sql> create a product named Laptop price 999.99
text2sql> show all products
text2sql> find user with name Jo
text2sql> update user with id 1 set name to Mike
text2sql> delete user with id 2
text2sql> schema                 # Wyświetla schemat bazy danych
text2sql> help                   # Wyświetla pomoc
text2sql> exit                   # Wyjście z shella
```

### Przykładowa sesja

```
=== Text2SQL Interactive Shell (using SmartLLM) ===
Type natural language queries to interact with the database.
Examples: 'create a user named John', 'show all users'
Type 'help' for more information or 'exit' to end the session.

text2sql> create a user named John
Generated SQL: INSERT INTO users (name) VALUES ('John')
Query executed successfully. Affected rows: 1

text2sql> show all users
Generated SQL: SELECT * FROM users
Query executed successfully. 1 records found.
------------------------------
id | name | email | created_at
------------------------------
1 | John | None | 2025-05-20 12:10:02
------------------------------

text2sql> create a product named Laptop price 999.99
Generated SQL: INSERT INTO products (name, price) VALUES ('Laptop', 999.99)
Query executed successfully. Affected rows: 1

text2sql> help
Available commands:
  help                    - Display this help message
  schema                  - Display database schema
  exit, quit              - Exit the shell
  <natural language>      - Any natural language query to the database

Supported query types:
  create table <n>
  create a user named <n>
  show all users
  create a product named <n> price <price>
  show all products
  find user with name <n>
  update user with id <id> set <field> to <value>
  delete user with id <id>
  ... and more via SmartLLM translation
```

## Używanie API REST

API REST pozwala na integrację Text2SQL z innymi aplikacjami. Po uruchomieniu API, dokumentacja jest dostępna pod adresem `http://localhost:8000/docs`.

### Główne endpointy

- `GET /` - Informacje o API
- `GET /schema` - Pobiera schemat bazy danych
- `GET /examples` - Pobiera przykłady zapytań
- `POST /translate` - Tłumaczy zapytanie w języku naturalnym na SQL
- `POST /query` - Wykonuje zapytanie SQL
- `POST /natural` - Przetwarza zapytanie w języku naturalnym, tłumaczy na SQL i wykonuje
- `GET /tables` - Pobiera listę tabel w bazie danych
- `GET /table/{table_name}` - Pobiera informacje o tabeli
- `POST /create-table` - Tworzy nową tabelę w bazie danych

### Przykłady użycia API z curl

#### Tłumaczenie zapytania na SQL
```bash
curl -X POST "http://localhost:8000/translate" \
     -H "Content-Type: application/json" \
     -d '{"query": "create a user named John"}'
```

#### Wykonanie zapytania w języku naturalnym
```bash
curl -X POST "http://localhost:8000/natural" \
     -H "Content-Type: application/json" \
     -d '{"query": "show all users"}'
```

#### Pobieranie schematu bazy danych
```bash
curl -X GET "http://localhost:8000/schema"
```

#### Tworzenie nowej tabeli
```bash
curl -X POST "http://localhost:8000/create-table" \
     -H "Content-Type: application/json" \
     -d '{
        "table_name": "employees",
        "columns": [
            {"name": "name", "type": "TEXT", "constraints": "NOT NULL"},
            {"name": "position", "type": "TEXT"},
            {"name": "salary", "type": "REAL"}
        ]
     }'
```

## Obsługiwane typy zapytań

Text2SQL obsługuje szeroką gamę zapytań w języku naturalnym. Poniżej znajduje się lista głównych typów zapytań:

### Operacje na tabelach
- `create table <n>` - Tworzy nową tabelę
- `show all tables` - Wyświetla wszystkie tabele

### Operacje na użytkownikach
- `create a user named <n>` - Tworzy nowego użytkownika
- `create a user named <n> with email <email>` - Tworzy nowego użytkownika z emailem
- `show all users` - Wyświetla wszystkich użytkowników
- `find user with name <n>` - Wyszukuje użytkownika po nazwie
- `update user with id <id> set name to <new_name>` - Aktualizuje nazwę użytkownika
- `update user with id <id> set email to <email>` - Aktualizuje email użytkownika
- `delete user with id <id>` - Usuwa użytkownika

### Operacje na produktach
- `create a product named <n> price <price>` - Tworzy nowy produkt
- `create a product named <n> price <price> description <desc>` - Tworzy nowy produkt z opisem
- `show all products` - Wyświetla wszystkie produkty
- `find product with name <n>` - Wyszukuje produkt po nazwie
- `update product with id <id> set price to <price>` - Aktualizuje cenę produktu
- `delete product with id <id>` - Usuwa produkt

### Zapytania SmartLLM

Przy użyciu SmartLLM, system obsługuje również bardziej złożone zapytania, np.:
- `show users who registered after May 2024`
- `find products cheaper than 500`
- `show me the average price of all products`
- `count how many users we have`

## Zaawansowane funkcje

### Używanie SmartLLM

SmartLLM to moduł, który wykorzystuje modele językowe do zaawansowanego tłumaczenia zapytań. Aby korzystać z pełnych możliwości SmartLLM, upewnij się, że pakiet `transformers` jest zainstalowany:

```bash
pip install transformers sentence-transformers
```

Możesz uruchomić SmartLLM jako osobny serwer lub używać go bezpośrednio w kliencie CLI:

```bash
# Uruchom jako serwer
python smart_llm.py --server

# Użyj bezpośrednio w kliencie CLI
python cli_client.py
```

### Niestandardowe tabele

Możesz tworzyć niestandardowe tabele za pomocą API REST lub języka naturalnego:

```bash
# Przez API REST
curl -X POST "http://localhost:8000/create-table" \
     -H "Content-Type: application/json" \
     -d '{
        "table_name": "custom_table",
        "columns": [
            {"name": "field1", "type": "TEXT", "constraints": "NOT NULL"},
            {"name": "field2", "type": "INTEGER"}
        ]
     }'

# Przez język naturalny
text2sql> create table custom_table
```

## Rozwiązywanie problemów

### Problemy z zależnościami

Jeśli napotkasz problemy z zależnościami, sprawdź następujące rzeczy:

1. Upewnij się, że masz aktywowane wirtualne środowisko:
   ```bash
   source venv/bin/activate
   ```

2. Sprawdź, czy wszystkie zależności są zainstalowane:
   ```bash
   pip list
   ```

3. Spróbuj ponownie zainstalować zależności:
   ```bash
   pip install -r requirements.txt
   ```

4. Jeśli nadal masz problemy z `sqlite3`, pamiętaj, że jest to moduł wbudowany w Pythona i nie trzeba go instalować przez pip.

### Problemy z uruchomieniem

1. Upewnij się, że wszystkie pliki mają uprawnienia do wykonywania:
   ```bash
   chmod +x *.py *.sh
   ```

2. Sprawdź, czy ścieżki do plików są poprawne.

3. Sprawdź logi błędów, aby zidentyfikować problem.

## Testowanie

Aby przetestować system Text2SQL, możesz użyć dołączonego skryptu testowego:

```bash
# Nadaj uprawnienia do wykonywania
chmod +x test_text2sql.sh

# Uruchom testy
./test_text2sql.sh
```

### Przygotowanie skryptu testowego

Przed uruchomieniem testów, upewnij się, że klient CLI obsługuje tryb nieinteraktywny. Możesz zaktualizować go za pomocą skryptu:

```bash
python update_client_for_testing.py
```

### Typy testów

Skrypt testowy sprawdza różne aspekty systemu Text2SQL:

1. **Testy zależności** - sprawdzają, czy wszystkie wymagane pakiety są zainstalowane
2. **Testy funkcjonalne** - testują podstawowe operacje (tworzenie, odczytywanie, aktualizacja, usuwanie)
3. **Testy integracyjne** - sprawdzają współpracę różnych komponentów systemu

### Dodawanie własnych testów

Możesz dodać własne testy, edytując funkcję `run_all_tests()` w pliku `test_text2sql.sh`. Na przykład:

```bash
# Test dodatkowej funkcjonalności
run_test "Mój dodatkowy test" \
    "moje zapytanie testowe" \
    "oczekiwany fragment wyniku"
```

### Automatyczne testy w CI/CD

Jeśli używasz CI/CD, możesz zintegrować testy Text2SQL z pipeline'em, dodając następujący krok:

```yaml
- name: Run Text2SQL tests
  run: |
    ./test_text2sql.sh
```

## Przykłady użycia w praktyce

### Scenariusz 1: Zarządzanie użytkownikami

```
# Tworzenie użytkowników
text2sql> create a user named John with email john@example.com
text2sql> create a user named Alice with email alice@example.com

# Wyświetlanie użytkowników
text2sql> show all users

# Wyszukiwanie użytkowników
text2sql> find user with name Al

# Aktualizacja użytkownika
text2sql> update user with id 2 set email to newalice@example.com

# Usuwanie użytkownika
text2sql> delete user with id 1
```

### Scenariusz 2: Zarządzanie produktami

```
# Tworzenie produktów
text2sql> create a product named Laptop price 999.99 description "High performance laptop"
text2sql> create a product named Mouse price 19.99

# Wyświetlanie produktów
text2sql> show all products

# Wyszukiwanie produktów
text2sql> find product with name Lap

# Aktualizacja produktu
text2sql> update product with id 1 set price to 899.99

# Usuwanie produktu
text2sql> delete product with id 2
```

### Scenariusz 3: Tworzenie niestandardowej tabeli i zapytań

```
# Tworzenie niestandardowej tabeli
text2sql> create table employees

# Dodawanie rekordów
text2sql> INSERT INTO employees (name, position, salary) VALUES ('John Doe', 'Developer', 5000)
text2sql> INSERT INTO employees (name, position, salary) VALUES ('Jane Smith', 'Manager', 7000)

# Wykonywanie zapytań
text2sql> SELECT * FROM employees WHERE salary > 6000
```

## Rozszerzanie funkcjonalności

### Dodawanie obsługi nowych typów zapytań

Aby dodać obsługę nowych typów zapytań, zmodyfikuj funkcję `translate_to_sql` w pliku `smart_llm.py`. Na przykład, aby dodać obsługę zapytań o średnią cenę produktów:

```python
# W metodzie _simple_translate klasy SmartLLM
elif "average" in query and "price" in query and "products" in query:
    return "SELECT AVG(price) AS average_price FROM products"
```

### Dodawanie nowych tabel domyślnych

Aby dodać nowe tabele domyślne, zmodyfikuj funkcję `create_db_if_not_exists` w plikach `cli_client.py` i `rest_api.py`:

```python
# Tworzenie nowej tabeli domyślnej
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (product_id) REFERENCES products (id)
)
''')
```

### Integracja z innymi bazami danych

Domyślnie Text2SQL używa SQLite, ale możesz zmodyfikować kod, aby obsługiwał inne bazy danych, np. PostgreSQL czy MySQL. W tym celu musisz:

1. Zainstalować odpowiedni sterownik bazy danych (np. `psycopg2` dla PostgreSQL)
2. Zmodyfikować funkcje połączenia z bazą danych
3. Dostosować zapytania SQL do składni docelowej bazy danych

## Kontakt i wsparcie

Jeśli masz pytania lub potrzebujesz wsparcia, możesz:
- Otworzyć Issue w repozytorium GitHub
- Skontaktować się z twórcami przez email: support@text2sql.example.com



# Integracja TinyLLM z Text2SQL

## Spis treści
1. [Wprowadzenie](#wprowadzenie)
2. [Wymagania](#wymagania)
3. [Instalacja](#instalacja)
4. [Uruchamianie](#uruchamianie)
5. [Rozwiązywanie problemów](#rozwiązywanie-problemów)
6. [Zaawansowana konfiguracja](#zaawansowana-konfiguracja)

## Wprowadzenie

TinyLLM to lekki model językowy, który można zintegrować z Text2SQL, aby umożliwić bardziej zaawansowane tłumaczenie zapytań z języka naturalnego na SQL. Ta dokumentacja opisuje, jak skonfigurować i uruchomić tę integrację.

## Wymagania

### Minimalne wymagania systemowe
- Python 3.8 lub nowszy
- SQLite
- min. 4GB RAM
- Miejsce na dysku: ~300MB (dla modelu T5-small)

### Wymagane pakiety
- transformers
- sentence-transformers (opcjonalnie, dla lepszego kodowania zapytań)
- fastapi
- uvicorn
- pydantic
- requests

## Instalacja

1. **Napraw integrację TinyLLM**

   Użyj dostarczonego skryptu naprawczego, aby zaktualizować moduł SmartLLM:
   ```bash
   chmod +x fix_tinyllm.sh
   ./fix_tinyllm.sh
   ```

   Ten skrypt:
   - Utworzy kopię zapasową istniejącego pliku `smart_llm.py` (jeśli istnieje)
   - Zastąpi go naprawioną wersją
   - Sprawdzi i zainstaluje wymagane zależności

2. **Zainstaluj zależności ręcznie**

   Alternatywnie, możesz zainstalować zależności ręcznie:
   ```bash
   pip install transformers sentence-transformers fastapi uvicorn pydantic requests
   ```

   Lub użyć pliku `requirements-full.txt`:
   ```bash
   pip install -r requirements-full.txt
   ```

## Uruchamianie

### 1. Testowanie modułu SmartLLM

Aby przetestować, czy moduł SmartLLM działa poprawnie:
```bash
python smart_llm.py --query "create a user named John"
```

Powinieneś zobaczyć wygenerowane zapytanie SQL:
```
Query: create a user named John
SQL: INSERT INTO users (name) VALUES ('John');
```

### 2. Uruchamianie interaktywnego shella z TinyLLM

Użyj skryptu `run.sh`, aby uruchomić interaktywny shell:
```bash
./run.sh shell
```

Przykłady zapytań:
```
text2sql> create table employees with name and position and salary
text2sql> create a user named John with email john@example.com
text2sql> show all users
text2sql> create a product named Laptop price 999.99 description "High performance laptop"
text2sql> find user with name Jo
text2sql> update product with id 1 set price to 899.99
```
```
create table employees with name and position and salary
create a user named John with email john@example.com
show all users
create a product named Laptop price 999.99 description "High performance laptop"
find user with name Jo
update product with id 1 set price to 899.99
```

### 3. Uruchamianie serwera SmartLLM API

Aby uruchomić SmartLLM jako oddzielny serwer API:
```bash
python smart_llm.py --server --port 8080
```

Ten serwer udostępnia endpoint `/translate` do tłumaczenia zapytań.

### 4. Uruchamianie wszystkich komponentów

Aby uruchomić wszystkie komponenty razem:
```bash
./run.sh all
```

## Rozwiązywanie problemów

### Problem: SmartLLM generuje niepoprawne zapytania SQL

**Symptom**: Model generuje SQL z niepotrzebnymi prefiksami, które powodują błędy składni.

**Rozwiązanie**: Użyj skryptu naprawczego `fix_tinyllm.sh`, który implementuje czyszczenie wyjścia z modelu.

### Problem: Problemy z instalacją transformers

**Symptom**: Błędy podczas instalacji pakietu transformers.

**Rozwiązanie**:
1. Upewnij się, że masz zainstalowany Python 3.8 lub nowszy.
2. Spróbuj zainstalować minimalną wersję:
   ```bash
   pip install transformers --no-deps
   pip install torch --index-url https://download.pytorch.org/whl/cpu
   ```

### Problem: Duże zużycie pamięci

**Symptom**: System zwalnia lub występują błędy braku pamięci.

**Rozwiązanie**:
1. Użyj mniejszego modelu, np. zmieniając parametr w konstruktorze SmartLLM:
   ```python
   llm = SmartLLM(model_name="distilbert-base-uncased")
   ```
2. Ograniczyć użycie pamięci przy inicjalizacji modelu:
   ```python
   llm = SmartLLM(low_memory=True)
   ```

## Zaawansowana konfiguracja

### Używanie własnych modeli

Możesz dostosować SmartLLM do używania innych modeli z Hugging Face:

1. **Zmiana modelu w pliku `smart_llm.py`**:
   ```python
   def __init__(self, model_name: str = "t5-small", use_advanced: bool = True):
   ```
   Zmień `t5-small` na nazwę innego modelu z Hugging Face, np.:
   - `"distilbert-base-uncased"` - lżejszy model, mniejszy rozmiar
   - `"t5-base"` - większy model, lepsze wyniki
   - `"microsoft/Phi-3-mini-4k-instruct"` - model instrukcyjny

2. **Dodawanie własnego modelu w czasie wykonania**:
   ```bash
   python smart_llm.py --model "twój/model" --query "create a user named John"
   ```

3. **Modyfikacja skryptu uruchomieniowego**:
   W pliku `run.sh` dodaj opcję do wyboru modelu, np.:
   ```bash
   CUSTOM_MODEL="t5-small"
   # ...
   python smart_llm.py --server --port 8080 --model "$CUSTOM_MODEL"
   ```

### Konfiguracja pamięci podręcznej modelu

Aby przyspieszyć ładowanie modelu i zmniejszyć zużycie zasobów, możesz skonfigurować pamięć podręczną:

1. **Dodaj zmienną środowiskową**:
   ```bash
   export TRANSFORMERS_CACHE="/ścieżka/do/cache"
   ```

2. **Dodaj do pliku konfiguracyjnego**:
   ```python
   # W smart_llm.py
   os.environ["TRANSFORMERS_CACHE"] = "/ścieżka/do/cache"
   ```

### Dostosowanie promptów dla modelu

Możesz dostosować prompt używany do tłumaczenia zapytań:

1. **Edytuj template promptu** w metodzie `translate` klasy `SmartLLM`:
   ```python
   prompt = f"""
   Translate the following natural language query to a valid SQLite SQL statement.
   
   Database schema:
   {schema}
   
   Natural language query: {query}
   
   Only return the SQL statement without any explanation or additional text:
   """
   ```

2. **Dostosuj pod kątem swojej domeny** - na przykład, jeśli używasz systemu do zarządzania zamówieniami:
   ```python
   prompt = f"""
   Translate the following query to SQL for an order management system.
   
   Database schema:
   {schema}
   
   Query: {query}
   
   Return only the SQL statement:
   """
   ```

### Integracja z zewnętrznymi bazami danych

Domyślna implementacja używa SQLite, ale możesz ją dostosować do innych baz danych:

1. **Dla PostgreSQL**:
   ```python
   # Zainstaluj psycopg2: pip install psycopg2-binary
   
   import psycopg2
   
   # Zmień metodę _get_connection w klasie Text2SQLShell (cli_client.py)
   def _get_connection(self):
       """Zwraca połączenie do bazy danych"""
       return psycopg2.connect(
           host="localhost",
           database="text2sql",
           user="username",
           password="password"
       )
   ```

2. **Dla MySQL**:
   ```python
   # Zainstaluj mysql-connector-python: pip install mysql-connector-python
   
   import mysql.connector
   
   # Zmień metodę _get_connection
   def _get_connection(self):
       """Zwraca połączenie do bazy danych"""
       return mysql.connector.connect(
           host="localhost",
           database="text2sql",
           user="username",
           password="password"
       )
   ```

### Optymalizacja generowania zapytań SQL

Aby poprawić jakość generowanych zapytań SQL:

1. **Dodaj więcej przykładów do promptu**:
   ```python
   prompt = f"""
   Translate the following natural language query to a valid SQLite SQL statement.
   
   Database schema:
   {schema}
   
   Examples:
   - "show all users" -> SELECT * FROM users;
   - "create a user named John" -> INSERT INTO users (name) VALUES ('John');
   - "find products cheaper than 100" -> SELECT * FROM products WHERE price < 100;
   
   Natural language query: {query}
   
   Only return the SQL statement:
   """
   ```

2. **Dostosuj parametry generowania tekstu**:
   ```python
   outputs = self.model(
       prompt,
       max_length=200,
       temperature=0.2,  # Niższa temperatura = bardziej przewidywalne wyniki
       do_sample=True,
       top_p=0.9,  # Filtrowanie nieprawdopodobnych tokenów
       num_return_sequences=1
   )
   ```

## Testowanie i debugowanie

### Tworzenie testów dla niestandardowych zapytań

Możesz stworzyć plik testowy z niestandardowymi zapytaniami:

```python
# test_custom_queries.py
from smart_llm import SmartLLM

def test_queries():
    llm = SmartLLM()
    
    test_cases = [
        ("create a table for employees with columns for name, position and salary", 
         "CREATE TABLE"),
        ("show me all users who registered after January", 
         "SELECT * FROM users WHERE"),
        ("delete the product with id 5", 
         "DELETE FROM products WHERE id = 5"),
    ]
    
    for query, expected_substring in test_cases:
        sql = llm.translate(query)
        print(f"Query: {query}")
        print(f"SQL: {sql}")
        assert expected_substring in sql, f"Expected {expected_substring} in {sql}"
        print("Test passed!\n")

if __name__ == "__main__":
    test_queries()
```

### Debugowanie wyjścia modelu

Aby lepiej zrozumieć, co generuje model, dodaj tymczasowe debugowanie do pliku `smart_llm.py`:

```python
def translate(self, query: str, schema: Optional[str] = None) -> str:
    # ... (istniejący kod)
    
    if self.use_advanced and self.model:
        try:
            outputs = self.model(prompt, max_length=200, temperature=0.1, do_sample=True)
            sql_raw = outputs[0]["generated_text"].strip()
            
            # Dodaj debugowanie
            print("\n--- RAW MODEL OUTPUT ---")
            print(sql_raw)
            print("------------------------\n")
            
            # Wyczyść i popraw wyjście
            sql = self._clean_sql_output(sql_raw)
            
            # Dodaj debugowanie
            print("--- CLEANED OUTPUT ---")
            print(sql)
            print("----------------------\n")
            
            # ... (reszta kodu)
```

## Przykłady zaawansowanych zapytań

Z poprawną integracją TinyLLM, system Text2SQL powinien obsługiwać bardziej złożone zapytania:

```
text2sql> find all users who registered after January 2024
text2sql> show products sorted by price from highest to lowest
text2sql> create a new invoice for user 1 with product 2 quantity 3
text2sql> calculate the average price of all products
text2sql> find users who have made more than 5 purchases
text2sql> update all products to increase price by 10%
```

## Dalszy rozwój

### Dodawanie obsługi bardziej złożonych zapytań SQL

W metodzie `_clean_sql_output` w `smart_llm.py`, możesz dodać obsługę bardziej złożonych zapytań SQL:

```python
def _clean_sql_output(self, sql_text: str) -> str:
    # ... (istniejący kod)
    
    # Obsługa zapytań GROUP BY
    if "GROUP BY" in sql_text.upper():
        match = re.search(r"(SELECT [^;]+GROUP BY[^;]+)", sql_text, re.IGNORECASE)
        if match:
            sql_text = match.group(1)
    
    # Obsługa JOIN
    if " JOIN " in sql_text.upper():
        match = re.search(r"(SELECT [^;]+JOIN[^;]+)", sql_text, re.IGNORECASE)
        if match:
            sql_text = match.group(1)
            
    # ... (reszta kodu)
```

### Tworzenie własnego fine-tuned modelu

Dla najlepszych wyników, możesz stworzyć własny fine-tuned model:

1. Przygotuj dane treningowe w formacie:
   ```json
   {
     "instruction": "Translate this query to SQL: show all users",
     "input": "",
     "output": "SELECT * FROM users;"
   }
   ```

2. Użyj Hugging Face Transformers do fine-tuningu:
   ```python
   from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer

   # Załaduj model bazowy
   model = AutoModelForCausalLM.from_pretrained("t5-small")
   tokenizer = AutoTokenizer.from_pretrained("t5-small")

   # Przygotuj dane treningowe
   # ...

   # Fine-tuning
   trainer = Trainer(
       model=model,
       train_dataset=train_dataset,
       args=TrainingArguments(
           output_dir="./text2sql-model",
           per_device_train_batch_size=4,
           num_train_epochs=3,
           save_strategy="epoch",
       )
   )
   trainer.train()

   # Zapisz model
   model.save_pretrained("./my-text2sql-model")
   tokenizer.save_pretrained("./my-text2sql-model")
   ```

3. Użyj własnego modelu w SmartLLM:
   ```python
   llm = SmartLLM(model_name="./my-text2sql-model")
   ```

## Podsumowanie

Integracja TinyLLM z Text2SQL pozwala na zaawansowane tłumaczenie zapytań z języka naturalnego na SQL. Dzięki poprawce wyjścia modelu, system może skutecznie obsługiwać różnorodne zapytania użytkownika.

Postępując zgodnie z tą dokumentacją, powinieneś być w stanie:
1. Zainstalować i skonfigurować niezbędne komponenty
2. Uruchomić system z integracją TinyLLM
3. Używać zaawansowanych zapytań w języku naturalnym
4. Rozwiązywać potencjalne problemy
5. Dostosować system do własnych potrzeb

Jeśli masz problemy lub pytania, sprawdź sekcję [Rozwiązywanie problemów](#rozwiązywanie-problemów) lub skontaktuj się z twórcami projektu.