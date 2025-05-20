# Text2SQL z MCP i TinyLLM

Minimalistyczna implementacja systemu text2sql wykorzystująca architekturę MCP (Model-Controller-Protocol) zintegrowana z TinyLLM, umożliwiająca tłumaczenie zapytań w języku naturalnym na SQL i wykonywanie ich na bazie danych SQLite.

## Wymagania systemowe

- Fedora (lub inna dystrybucja Linuxa)
- Python 3.8+
- SQLite
- Wymagane pakiety zostaną zainstalowane przez skrypt instalacyjny

## Instalacja

1. Sklonuj repozytorium:
   ```bash
   git clone https://github.com/fin-officer/text2sql-mcp.git
   cd text2sql-mcp
   ```

2. Uruchom skrypt instalacyjny:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```




Lista plików projektu

```
text2sql-mcp/
├── README.md                # Dokumentacja projektu
├── cli_client.py            # Klient interaktywny
├── install_dependencies.sh  # Skrypt do instalacji zależności
├── mcp_server.py            # Serwer MCP
├── requirements.txt         # Lista zależności projektu
├── rest_api.py              # Klient API REST
├── run_text2sql.sh          # Skrypt do uruchamiania komponentów
├── setup.sh                 # Skrypt instalacyjny
├── start_tinyllm.py         # Skrypt do uruchomienia TinyLLM
├── test_text2sql.py         # Testy jednostkowe
├── tinyllm_client.py        # Klient TinyLLM
└── tinyllm_server.py        # Serwer TinyLLM
```

## Komponenty projektu

1. **MCP Server** (`mcp_server.py`) - Serwer MCP implementujący funkcjonalność text2sql
2. **CLI Client** (`cli_client.py`) - Interaktywny shell dla text2sql
3. **REST API** (`rest_api.py`) - API REST dla text2sql
4. **TinyLLM Client** (`tinyllm_client.py`) - Klient do usługi TinyLLM
5. **TinyLLM Server** (`start_tinyllm.py`) - Skrypt do uruchomienia serwisu TinyLLM

### Instrukcja instalacji zależności

Aby zainstalować wszystkie zależności projektu, wykonaj następujące kroki:

1. Nadaj uprawnienia wykonywania skryptowi instalacyjnemu:
   ```bash
   chmod +x install.sh
   ```

2. Uruchom skrypt instalacyjny:
   ```bash
   ./install.sh
   ```

Skrypt zainstaluje wszystkie wymagane pakiety systemowe (jeśli używasz Fedora lub systemu opartego na APT) oraz zależności Pythona wymienione w pliku `requirements.txt`.

Alternatywnie, możesz też ręcznie zainstalować zależności używając pip:
```bash
pip install -r requirements.txt
```

Jeśli chcesz zainstalować zależności w wirtualnym środowisku, możesz wykonać:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```


## Uruchamianie

Projekt można uruchomić na kilka sposobów:

### 1. Uruchomienie wszystkich komponentów naraz

```bash
./run_text2sql.sh all
```

### 2. Uruchomienie komponentów oddzielnie

#### Uruchomienie serwisu TinyLLM (w osobnym terminalu)
```bash
./run_text2sql.sh tinyllm
```

#### Uruchomienie API REST (w osobnym terminalu)
```bash
./run_text2sql.sh api
```

#### Uruchomienie interaktywnego shella
```bash
./run_text2sql.sh shell
```

## Użycie

### Interaktywny shell

W interaktywnym shellu możesz wpisywać zapytania w języku naturalnym:

```
text2sql> create a user named John
text2sql> show all users
text2sql> create a product named Laptop price 999.99
text2sql> show all products
```

### API REST

API REST jest dostępne pod adresem http://localhost:8000/ z następującymi endpointami:

- `GET /schema` - Pobiera schemat bazy danych
- `GET /examples` - Pobiera przykłady zapytań
- `POST /translate` - Tłumaczy zapytanie w języku naturalnym na SQL
- `POST /query` - Wykonuje zapytanie SQL
- `POST /natural` - Przetwarza zapytanie w języku naturalnym, tłumaczy na SQL i wykonuje

Dokumentacja API jest dostępna pod adresem http://localhost:8000/docs

### Przykłady użycia API REST

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

## Architektura

Projekt wykorzystuje architekturę MCP (Model-Controller-Protocol), która składa się z:

- **Model** - Odpowiada za operacje na bazie danych SQLite
- **Controller** - Zawiera logikę biznesową, w tym tłumaczenie języka naturalnego na SQL
- **Protocol** - Zarządza komunikacją między klientami a serwerem

Projekt jest zbudowany modułowo, co umożliwia łatwe rozszerzanie i integrację z innymi systemami.

## Rozszerzanie funkcjonalności

Aby rozszerzyć funkcjonalność projektu:

1. **Dodawanie nowych tabeli** - Zmodyfikuj funkcję `setup_database` w `mcp_server.py`
2. **Dodawanie nowych typów zapytań** - Rozszerz funkcję `translate_to_sql` w `mcp_server.py`
3. **Integracja z innymi modelami LLM** - Zmodyfikuj `tinyllm_client.py` i `start_tinyllm.py`



## Lista plików projektu

### Główne pliki:

1. **mcp_server.py** - Serwer MCP implementujący funkcjonalność text2sql
2. **cli_client.py** - Interaktywny shell dla text2sql
3. **rest_api.py** - API REST dla text2sql
4. **tinyllm_client.py** - Klient do usługi TinyLLM
5. **start_tinyllm.py** - Skrypt do uruchomienia serwisu TinyLLM
6. **tinyllm_server.py** - Serwer TinyLLM (wcześniej generowany dynamicznie)
7. **setup.sh** - Skrypt instalacyjny dla systemu Fedora
8. **run_text2sql.sh** - Skrypt do uruchamiania poszczególnych komponentów
9. **test_text2sql.py** - Testy jednostkowe
10. **README.md** - Dokumentacja projektu

Stwórzmy brakujący plik `run_text2sql.sh` jako osobny skrypt zamiast generować go dynamicznie:

Stwórzmy również plik `tinyllm_server.py`, który wcześniej był generowany dynamicznie:

Zaktualizujmy również skrypt `start_tinyllm.py`, aby używał predefiniowanego pliku `tinyllm_server.py` zamiast generować go dynamicznie:

Zaktualizujmy również skrypt instalacyjny `setup.sh`, aby był bardziej przejrzysty i nie generował innych skryptów:

## Struktura projektu Text2SQL z MCP i TinyLLM

Oto kompletna lista plików projektu text2sql w wersji z MCP i TinyLLM. Wszystkie pliki są bezpośrednio dostępne w projekcie, bez dynamicznego generowania ich w czasie wykonania:

### Główne pliki projektu:

1. **mcp_server.py**
   - Serwer MCP implementujący funkcjonalność text2sql
   - Zawiera definicje zasobów i narzędzi MCP
   - Łączy się z bazą danych SQLite

2. **cli_client.py**
   - Interaktywny klient CLI
   - Łączy się z serwerem MCP przez protokół stdio
   - Pozwala na wprowadzanie zapytań w języku naturalnym

3. **rest_api.py**
   - Klient API REST
   - Udostępnia funkcjonalność text2sql przez HTTP
   - Umożliwia integrację z innymi aplikacjami

4. **tinyllm_client.py**
   - Klient do usługi TinyLLM
   - Odpowiada za tłumaczenie zapytań w języku naturalnym na SQL
   - Komunikuje się z serwerem TinyLLM przez REST API

5. **tinyllm_server.py**
   - Serwer TinyLLM
   - Implementuje API kompatybilne z OpenAI
   - Wykorzystuje llama-cpp-python do ładowania i uruchamiania modelu

6. **start_tinyllm.py**
   - Skrypt do konfiguracji i uruchomienia lokalnego serwisu TinyLLM
   - Instaluje wymagane zależności
   - Pobiera model z HuggingFace, jeśli jest to konieczne
   - Uruchamia serwer TinyLLM

7. **run_text2sql.sh**
   - Skrypt pomocniczy do uruchamiania komponentów systemu
   - Zawiera funkcje do uruchamiania shella, API lub TinyLLM
   - Umożliwia uruchomienie wszystkich komponentów jednocześnie

8. **setup.sh**
   - Skrypt instalacyjny dla systemu Fedora
   - Konfiguruje wszystkie niezbędne zależności
   - Sprawdza, czy wszystkie pliki projektu są dostępne

9. **test_text2sql.py**
   - Testy jednostkowe dla weryfikacji poprawności działania implementacji
   - Zawiera testy dla serwera MCP i klienta

10. **README.md**
    - Dokumentacja projektu
    - Zawiera instrukcje instalacji i uruchomienia
    - Opisuje architekturę i funkcjonalność systemu




### 1. Przygotowanie plików projektu

Upewnij się, że masz następujące pliki w katalogu projektu:
- `cli_client.py` (uproszczona wersja)
- `rest_api.py` (uproszczona wersja)
- `run_text2sql.sh` (uproszczona wersja)
- `install.sh` (uproszczona wersja)

### 2. Instalacja zależności

Wykonaj poniższe polecenia:

```bash
chmod +x install.sh
./install.sh
```

Ten skrypt:
- Zainstaluje wymagane pakiety systemowe
- Utworzy wirtualne środowisko Python (o ile nie istnieje)
- Zainstaluje niezbędne zależności Pythona
- Nada uprawnienia wykonywania skryptom

### 3. Uruchomienie aplikacji

Najpierw aktywuj wirtualne środowisko:

```bash
source venv/bin/activate
```

Następnie uruchom aplikację:

```bash
# Uruchom interaktywny shell
./run_text2sql.sh shell

# Lub uruchom API REST
./run_text2sql.sh api

# Lub uruchom oba komponenty naraz
./run_text2sql.sh all
```

### 4. Korzystanie z aplikacji

W interaktywnym shellu możesz wprowadzać zapytania w języku naturalnym:

```
text2sql> create a user named John
text2sql> show all users
text2sql> create a product named Laptop price 999.99
text2sql> show all products
```

Jeśli uruchomiłeś API REST, możesz korzystać z endpointów:
- `GET http://localhost:8000/schema` - Pobiera schemat bazy danych
- `GET http://localhost:8000/examples` - Pobiera przykłady zapytań
- `POST http://localhost:8000/translate` - Tłumaczy zapytanie w języku naturalnym na SQL
- `POST http://localhost:8000/query` - Wykonuje zapytanie SQL
- `POST http://localhost:8000/natural` - Przetwarza zapytanie w języku naturalnym

Dokumentacja API dostępna jest pod adresem: `http://localhost:8000/docs`

### Uwagi:

- Ta uproszczona wersja nie używa MCP ani TinyLLM, więc nie ma problemów z instalacją tych zależności
- Używa podstawowego mechanizmu tłumaczenia opartego na regułach
- Obsługuje tylko proste zapytania (tworzenie użytkowników, wyświetlanie wszystkich użytkowników, itp.)
- Wszystkie dane są przechowywane w lokalnej bazie danych SQLite (`text2sql.db`)

