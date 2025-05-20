Teraz stwórzmy zaktualizowany skrypt uruchomieniowy:

Na koniec, zaktualizowany skrypt instalacyjny:

## Rozszerzona wersja Text2SQL z zaawansowanymi funkcjami LLM

Przygotowałem rozszerzoną wersję projektu Text2SQL, która oferuje pełniejszą kontrolę poprzez zaawansowane tłumaczenie języka naturalnego na SQL. Zamiast polegać na problematycznych zależnościach MCP i llama-cpp-python, które powodowały problemy na Fedora, stworzyłem własne rozwiązanie oparte na popularnych bibliotekach transformers i huggingface_hub.

### Główne pliki projektu:

1. **smart_llm.py** - Własna implementacja modelu językowego do tłumaczenia zapytań
   - Wykorzystuje modele Hugging Face (np. T5)
   - Działa w dwóch trybach: jako moduł lokalny lub jako serwer API
   - Ma wbudowany mechanizm fallback na wypadek problemów

2. **cli_client.py** - Rozszerzony klient interaktywny
   - Może korzystać z lokalnego SmartLLM lub z zewnętrznego serwera API
   - Obsługuje szerszy zakres zapytań w języku naturalnym
   - Wyświetla schemat bazy danych

3. **rest_api.py** - Rozszerzone API REST
   - Dodatkowe endpointy do zarządzania schematem bazy danych
   - Integracja z SmartLLM
   - Szczegółowa dokumentacja API w Swagger

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


