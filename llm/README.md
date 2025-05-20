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