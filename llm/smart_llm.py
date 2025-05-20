#!/usr/bin/env python3
# smart_llm.py - Poprawiona wersja SmartLLM z obsługą TinyLLM

import os
import sys
import time
import argparse
import json
import re
from typing import Dict, Any, List, Optional

# Flaga, która określa, czy używamy zaawansowanego modelu
try:
    import transformers
    from transformers import pipeline

    HAS_ADVANCED_MODEL = True
except ImportError:
    HAS_ADVANCED_MODEL = False


class SmartLLM:
    """Inteligentny model językowy dla tłumaczenia zapytań na SQL"""

    def __init__(self, model_name: str = "t5-small", use_advanced: bool = True):
        """Inicjalizacja modelu językowego"""
        self.model_name = model_name
        self.use_advanced = use_advanced and HAS_ADVANCED_MODEL
        self.model = None

        if self.use_advanced:
            try:
                print(f"Ładowanie modelu {model_name}...")
                self.model = pipeline(
                    "text2text-generation",
                    model=model_name,
                    device="cpu"  # Używamy CPU, bo nie wszyscy mają GPU
                )
                print(f"Model załadowany pomyślnie!")
            except Exception as e:
                print(f"Błąd ładowania modelu: {str(e)}")
                print("Używanie prostego mechanizmu tłumaczenia opartego na regułach.")
                self.use_advanced = False

    def _clean_sql_output(self, sql_text: str) -> str:
        """Czyści wyjście z modelu, usuwając niepotrzebne prefiksy i suffiksy"""
        # Najpierw sprawdź, czy mamy jakieś kluczowe słowa SQL
        sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE"]

        # Sprawdź, czy wyjście już zawiera poprawne zapytanie SQL z simple_translate
        for keyword in sql_keywords:
            if keyword in sql_text.upper():
                # Wyodrębnij zapytanie zaczynające się od tego słowa kluczowego
                pattern = f"({keyword}[^;]+);"
                match = re.search(pattern, sql_text, re.IGNORECASE)
                if match:
                    return match.group(1) + ";"

        # Usuń wszystkie linie niezawierające istotnych informacji SQL
        filtered_lines = []
        for line in sql_text.split('\n'):
            line = line.strip()
            if any(keyword in line.upper() for keyword in sql_keywords):
                filtered_lines.append(line)

        if filtered_lines:
            sql_text = ' '.join(filtered_lines)

        # Usuń prefiksy typu "SQLite SQL statement:" lub "Query:" lub "SQL:"
        prefixes_to_remove = [
            "SQLite SQL statement:",
            "Query:",
            "SQL:",
            "SQL (only return the SQL statement without explanation):",
            "Only return the SQL statement without any explanation or additional text:",
            "Natural language query:"
        ]

        for prefix in prefixes_to_remove:
            sql_text = sql_text.replace(prefix, "")

        # Usuń wszystko po pierwszym średniku
        semicolon_index = sql_text.find(";")
        if semicolon_index > 0:
            sql_text = sql_text[:semicolon_index + 1]

        # Jeśli brakuje kluczowych słów SQL, użyj fallbacku
        if not any(keyword in sql_text.upper() for keyword in sql_keywords):
            return "-- Could not clean SQL output"

        # Usuń wszystko, co zawiera "Natural language query:"
        nl_query_index = sql_text.find("Natural language query:")
        if nl_query_index > 0:
            sql_text = sql_text[:nl_query_index].strip()

        # Usuń niepotrzebne białe znaki
        sql_text = ' '.join(sql_text.split())

        # Upewnij się, że kończy się średnikiem
        if not sql_text.strip().endswith(";"):
            sql_text = sql_text.strip() + ";"

        return sql_text

    def translate(self, query: str, schema: Optional[str] = None) -> str:
        """Tłumaczy zapytanie w języku naturalnym na SQL"""
        if not query:
            return "-- Empty query"

        # Przygotuj kontekst z schematem bazy danych
        if not schema:
            schema = """
            users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, created_at TIMESTAMP)
            products (id INTEGER PRIMARY KEY, name TEXT, price REAL, description TEXT)
            """

        # Jeśli jest dostępny zaawansowany model, użyj go
        if self.use_advanced and self.model:
            prompt = f"""
            Translate the following natural language query to a valid SQLite SQL statement.

            Database schema:
            {schema}

            Natural language query: {query}

            Only return the SQL statement without any explanation or additional text:
            """

            try:
                outputs = self.model(prompt, max_length=200, temperature=0.1, do_sample=True)
                sql_raw = outputs[0]["generated_text"].strip()

                # Wyczyść i popraw wyjście
                sql = self._clean_sql_output(sql_raw)

                # Sprawdź, czy output wygląda jak SQL
                if not any(keyword in sql.upper() for keyword in ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE"]):
                    # Jeśli nie, spróbuj z prostym mechanizmem
                    return self._simple_translate(query)

                return sql
            except Exception as e:
                print(f"Błąd generowania SQL: {str(e)}")
                # Fallback do prostego mechanizmu
                return self._simple_translate(query)
        else:
            # Użyj prostego mechanizmu tłumaczenia
            return self._simple_translate(query)

    def _simple_translate(self, query: str) -> str:
        """Prosty mechanizm tłumaczenia oparty na regułach"""
        query = query.lower()

        # Obsługa zapytań typu CREATE TABLE
        if "create table" in query or ("create" in query and "table" in query):
            words = query.split()
            table_index = words.index("table") if "table" in words else -1

            if table_index > 0 and table_index < len(words) - 1:
                table_name = words[table_index + 1]

                # Sprawdź, czy określono kolumny
                columns = []
                if "with" in words and words.index("with") > table_index:
                    # Parsuj kolumny po "with"
                    with_index = words.index("with")
                    column_part = " ".join(words[with_index + 1:])

                    # Sprawdź, czy mamy "and" jako separator
                    if "and" in column_part:
                        column_names = [col.strip() for col in column_part.split("and")]
                        for col in column_names:
                            col = col.strip()
                            if col:
                                if "email" in col:
                                    columns.append(f"{col} TEXT")
                                elif "price" in col or "amount" in col or "cost" in col:
                                    columns.append(f"{col} REAL")
                                elif "date" in col or "time" in col:
                                    columns.append(f"{col} TIMESTAMP")
                                else:
                                    columns.append(f"{col} TEXT")

                if columns:
                    column_defs = ", ".join(columns)
                    return f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id INTEGER PRIMARY KEY,
                        {column_defs},
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    """
                else:
                    if "user" in table_name or "users" in table_name:
                        return f"""
                        CREATE TABLE IF NOT EXISTS {table_name} (
                            id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL,
                            email TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                        """
                    elif "product" in table_name or "products" in table_name:
                        return f"""
                        CREATE TABLE IF NOT EXISTS {table_name} (
                            id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL,
                            price REAL NOT NULL,
                            description TEXT
                        );
                        """
                    else:
                        return f"""
                        CREATE TABLE IF NOT EXISTS {table_name} (
                            id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                        """

        # Obsługa zapytań typu CREATE USER
        elif "create" in query and "user" in query and "named" in query:
            parts = query.split("named")
            if len(parts) > 1:
                name = parts[1].strip().split()[0]

                # Sprawdź, czy podano email
                email = None
                if "email" in query:
                    email_parts = query.split("email")
                    if len(email_parts) > 1:
                        email = email_parts[1].strip().split()[0]

                if email:
                    return f"INSERT INTO users (name, email) VALUES ('{name}', '{email}');"
                else:
                    return f"INSERT INTO users (name) VALUES ('{name}');"

        # Obsługa zapytań typu SHOW ALL USERS
        elif "show" in query and "all" in query and "users" in query:
            return "SELECT * FROM users;"

        # Obsługa zapytań typu CREATE PRODUCT
        elif "create" in query and "product" in query:
            words = query.split()
            name_index = words.index("named") if "named" in words else -1
            price_index = words.index("price") if "price" in words else -1

            if name_index > 0 and price_index > 0 and name_index < len(words) - 1 and price_index < len(words) - 1:
                name = words[name_index + 1]
                price = words[price_index + 1]

                # Sprawdź, czy podano opis
                description = None
                if "description" in words:
                    desc_index = words.index("description")
                    if desc_index < len(words) - 1:
                        # Pobierz opis, obsługując cudzysłowy
                        if desc_index + 1 < len(words) and words[desc_index + 1].startswith('"'):
                            # Znajdź zamykający cudzysłów
                            desc_end = 0
                            for i in range(desc_index + 1, len(words)):
                                if words[i].endswith('"'):
                                    desc_end = i
                                    break

                            if desc_end > 0:
                                description = " ".join(words[desc_index + 1:desc_end + 1])
                                # Usuń cudzysłowy
                                description = description.strip('"')
                        else:
                            description = words[desc_index + 1]

                if description:
                    return f"INSERT INTO products (name, price, description) VALUES ('{name}', {price}, '{description}');"
                else:
                    return f"INSERT INTO products (name, price) VALUES ('{name}', {price});"

        # Obsługa zapytań typu SHOW ALL PRODUCTS
        elif "show" in query and "all" in query and "products" in query:
            return "SELECT * FROM products;"

        # Obsługa zapytań typu UPDATE
        elif "update" in query:
            if "user" in query:
                # Przykład: update user with id 1 set name to John
                words = query.split()
                id_index = words.index("id") if "id" in words else -1
                set_index = words.index("set") if "set" in words else -1

                if id_index > 0 and set_index > 0 and id_index < len(words) - 1 and set_index < len(words) - 1:
                    user_id = words[id_index + 1]
                    field = words[set_index + 1]
                    to_index = words.index("to") if "to" in words else -1

                    if to_index > 0 and to_index < len(words) - 1:
                        value = words[to_index + 1]
                        return f"UPDATE users SET {field} = '{value}' WHERE id = {user_id};"

            elif "product" in query:
                # Podobna logika dla produktów
                words = query.split()
                id_index = words.index("id") if "id" in words else -1
                set_index = words.index("set") if "set" in words else -1

                if id_index > 0 and set_index > 0 and id_index < len(words) - 1 and set_index < len(words) - 1:
                    product_id = words[id_index + 1]
                    field = words[set_index + 1]
                    to_index = words.index("to") if "to" in words else -1

                    if to_index > 0 and to_index < len(words) - 1:
                        value = words[to_index + 1]
                        # Jeśli field to price, nie dodawaj apostrofów
                        if field == "price":
                            return f"UPDATE products SET {field} = {value} WHERE id = {product_id};"
                        else:
                            return f"UPDATE products SET {field} = '{value}' WHERE id = {product_id};"

        # Obsługa zapytań typu DELETE
        elif "delete" in query:
            if "user" in query:
                # Przykład: delete user with id 1
                words = query.split()
                id_index = words.index("id") if "id" in words else -1

                if id_index > 0 and id_index < len(words) - 1:
                    user_id = words[id_index + 1]
                    return f"DELETE FROM users WHERE id = {user_id};"

            elif "product" in query:
                words = query.split()
                id_index = words.index("id") if "id" in words else -1

                if id_index > 0 and id_index < len(words) - 1:
                    product_id = words[id_index + 1]
                    return f"DELETE FROM products WHERE id = {product_id};"

        # Obsługa zapytań typu FIND
        elif "find" in query:
            if "user" in query:
                # Przykład: find user with name John
                words = query.split()
                name_index = words.index("name") if "name" in words else -1

                if name_index > 0 and name_index < len(words) - 1:
                    name = words[name_index + 1]
                    return f"SELECT * FROM users WHERE name LIKE '%{name}%';"

            elif "product" in query:
                words = query.split()
                name_index = words.index("name") if "name" in words else -1

                if name_index > 0 and name_index < len(words) - 1:
                    name = words[name_index + 1]
                    return f"SELECT * FROM products WHERE name LIKE '%{name}%';"

        # Jeśli nie dopasowano żadnego wzorca
        return "-- Could not translate query to SQL"


def start_server(port=8080):
    """Uruchamia serwer API dla SmartLLM"""
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    import uvicorn

    app = FastAPI(title="SmartLLM API")

    class TranslationRequest(BaseModel):
        query: str
        schema: Optional[str] = None

    # Inicjalizuj model
    llm = SmartLLM()

    @app.get("/")
    def read_root():
        return {"message": "SmartLLM API is running"}

    @app.post("/translate")
    def translate_query(request: TranslationRequest):
        sql = llm.translate(request.query, request.schema)
        return {"sql": sql}

    print(f"Starting SmartLLM API server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)


def main():
    parser = argparse.ArgumentParser(description='SmartLLM for Text2SQL')
    parser.add_argument('--server', action='store_true', help='Run as API server')
    parser.add_argument('--port', type=int, default=8080, help='Server port (if running as server)')
    parser.add_argument('--query', type=str, help='Translate a single query and exit')
    args = parser.parse_args()

    if args.server:
        start_server(args.port)
    elif args.query:
        llm = SmartLLM()
        sql = llm.translate(args.query)
        print(f"Query: {args.query}")
        print(f"SQL: {sql}")
    else:
        # Interaktywny tryb
        llm = SmartLLM()
        print("SmartLLM Interactive Mode (type 'exit' to quit)")
        while True:
            query = input("Query> ")
            if query.lower() == 'exit':
                break
            sql = llm.translate(query)
            print(f"SQL: {sql}")


if __name__ == "__main__":
    main()