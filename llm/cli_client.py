#!/usr/bin/env python3
# cli_client.py - Rozszerzony interaktywny klient CLI dla Text2SQL

import os
import sys
import argparse
import readline  # Dla historii komend
import sqlite3
import subprocess
import json
import requests
from typing import Dict, List, Optional, Any

# Importuj nasz SmartLLM
try:
    from llm import SmartLLM

    HAS_SMART_LLM = True
except ImportError:
    HAS_SMART_LLM = False


class Text2SQLShell:
    """Rozszerzony interaktywny shell dla text2sql"""

    def __init__(self, db_path="text2sql.db", llm_url=None, use_local_llm=True):
        """Inicjalizacja klienta shell"""
        self.db_path = db_path
        self.llm_url = llm_url
        self.use_local_llm = use_local_llm and HAS_SMART_LLM
        self.schema = None

        # Inicjalizuj lokalny LLM, jeśli dostępny
        if self.use_local_llm:
            try:
                self.llm = SmartLLM()
                print("Używanie lokalnego SmartLLM dla tłumaczenia zapytań.")
            except Exception as e:
                print(f"Błąd inicjalizacji SmartLLM: {str(e)}")
                self.use_local_llm = False

        # Stwórz bazę danych, jeśli nie istnieje
        self.create_db_if_not_exists()

        # Pobierz schemat bazy danych
        self.load_schema()

    def create_db_if_not_exists(self):
        """Tworzy bazę danych, jeśli nie istnieje"""
        if not os.path.exists(self.db_path):
            print(f"Tworzenie nowej bazy danych: {self.db_path}")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Tworzenie tabeli users
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS users
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY,
                               name
                               TEXT
                               NOT
                               NULL,
                               email
                               TEXT,
                               created_at
                               TIMESTAMP
                               DEFAULT
                               CURRENT_TIMESTAMP
                           )
                           ''')

            # Tworzenie tabeli products
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS products
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY,
                               name
                               TEXT
                               NOT
                               NULL,
                               price
                               REAL
                               NOT
                               NULL,
                               description
                               TEXT
                           )
                           ''')

            conn.commit()
            conn.close()

    def load_schema(self):
        """Ładuje schemat bazy danych"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
        schema_rows = cursor.fetchall()
        conn.close()

        self.schema = "\n".join(row[0] for row in schema_rows if row[0])

    def translate_to_sql(self, query):
        """Tłumaczy zapytanie w języku naturalnym na SQL"""
        # Najpierw spróbuj użyć lokalnego LLM, jeśli dostępny
        if self.use_local_llm:
            try:
                return self.llm.translate(query, self.schema)
            except Exception as e:
                print(f"Błąd tłumaczenia z lokalnym LLM: {str(e)}")
                # Kontynuuj z pozostałymi metodami

        # Następnie spróbuj użyć zdalnego LLM API, jeśli URL jest podany
        if self.llm_url:
            try:
                response = requests.post(
                    f"{self.llm_url}/translate",
                    json={"query": query, "schema": self.schema},
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    return data.get("sql", "-- Error: No SQL in API response")
                else:
                    return f"-- Error: LLM API returned status code {response.status_code}"
            except requests.RequestException as e:
                print(f"Błąd komunikacji z API LLM: {str(e)}")
                # Kontynuuj z prostym mechanizmem

        # Fallback do prostego mechanizmu tłumaczenia
        return self._simple_translate(query)

    def _simple_translate(self, query):
        """Prosty mechanizm tłumaczenia oparty na regułach (fallback)"""
        query = query.lower()

        # Obsługa zapytań typu CREATE TABLE
        if "create table" in query or ("create" in query and "table" in query):
            words = query.split()
            table_index = words.index("table") if "table" in words else -1

            if table_index > 0 and table_index < len(words) - 1:
                table_name = words[table_index + 1]
                return f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """

        elif "create" in query and "user" in query and "named" in query:
            parts = query.split("named")
            if len(parts) > 1:
                name = parts[1].strip().split()[0]
                return f"INSERT INTO users (name) VALUES ('{name}')"

        elif "show all users" in query:
            return "SELECT * FROM users"

        elif "create" in query and "product" in query:
            words = query.split()
            name_index = words.index("named") if "named" in words else -1
            price_index = words.index("price") if "price" in words else -1

            if name_index > 0 and price_index > 0 and name_index < len(words) - 1 and price_index < len(words) - 1:
                name = words[name_index + 1]
                price = words[price_index + 1]
                return f"INSERT INTO products (name, price) VALUES ('{name}', {price})"

        elif "show all products" in query:
            return "SELECT * FROM products"

        return "-- Could not translate query to SQL"

    def execute_query(self, sql):
        """Wykonuje zapytanie SQL na bazie danych"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute(sql)
            conn.commit()

            # Sprawdź, czy to zapytanie SELECT (które zwraca dane)
            if sql.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                column_names = [description[0] for description in cursor.description]
                result = []
                for row in rows:
                    result.append(dict(zip(column_names, row)))
                message = f"Query executed successfully. {len(result)} records found."
                conn.close()
                return {"results": result, "message": message}
            else:
                rowcount = cursor.rowcount
                message = f"Query executed successfully. Affected rows: {rowcount}"
                conn.close()
                return {"results": [], "message": message}
        except sqlite3.Error as e:
            conn.close()
            return {"results": [], "message": f"Database error: {str(e)}"}

    def process_query(self, query):
        """Przetwarza zapytanie w języku naturalnym, tłumaczy na SQL i wykonuje"""
        sql = self.translate_to_sql(query)
        if sql.startswith("--"):
            return {"results": [], "message": f"Failed to translate: {sql}", "sql": sql}

        result = self.execute_query(sql)
        result["sql"] = sql
        return result

    def run_shell(self):
        """Uruchamia interaktywny shell"""
        model_info = "SmartLLM" if self.use_local_llm else "Simple Rules"
        print(f"\n=== Text2SQL Interactive Shell (using {model_info}) ===")
        print("Type natural language queries to interact with the database.")
        print("Examples: 'create a user named John', 'show all users'")
        print("Type 'help' for more information or 'exit' to end the session.\n")

        while True:
            try:
                user_input = input("text2sql> ").strip()

                if user_input.lower() in ('exit', 'quit'):
                    break
                elif not user_input:
                    continue
                elif user_input.lower() == 'help':
                    self.print_help()
                    continue
                elif user_input.lower() == 'schema':
                    self.show_schema()
                    continue

                # Przetwarzanie zapytania
                result = self.process_query(user_input)

                # Wyświetlenie wyników
                self.display_results(result)

                # Odśwież schemat w przypadku zmian w strukturze
                if "CREATE TABLE" in result.get("sql", "").upper():
                    self.load_schema()

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {str(e)}")

    def display_results(self, result):
        """Wyświetla wyniki zapytania w sformatowany sposób"""
        sql = result.get("sql", "")
        message = result.get("message", "")
        results = result.get("results", [])

        print(f"\nGenerated SQL: {sql}\n")
        print(message)

        if results:
            # Wydrukuj nagłówki
            headers = results[0].keys()
            header_row = " | ".join(str(h) for h in headers)
            separator = "-" * len(header_row)

            print("\n" + separator)
            print(header_row)
            print(separator)

            # Wydrukuj wiersze danych
            for row in results:
                print(" | ".join(str(row[h]) for h in headers))
            print(separator + "\n")

    def show_schema(self):
        """Wyświetla schemat bazy danych"""
        print("\nDatabase Schema:")
        print("----------------")
        print(self.schema)
        print()

    def print_help(self):
        """Wyświetla pomoc dla użytkownika"""
        print("\nAvailable commands:")
        print("  help                    - Display this help message")
        print("  schema                  - Display database schema")
        print("  exit, quit              - Exit the shell")
        print("  <natural language>      - Any natural language query to the database\n")
        print("\nSupported query types:")
        print("  create table <name>")
        print("  create a user named <name>")
        print("  show all users")
        print("  create a product named <name> price <price>")
        print("  show all products")
        print("  find user with name <name>")
        print("  update user with id <id> set <field> to <value>")
        print("  delete user with id <id>")
        print("  ... and more via SmartLLM translation\n")


def main():
    parser = argparse.ArgumentParser(description='Text2SQL Interactive Shell')
    parser.add_argument('--db', default='text2sql.db', help='Path to SQLite database file')
    parser.add_argument('--llm-url', default=None, help='URL of LLM API service (optional)')
    parser.add_argument('--no-local-llm', action='store_true', help='Disable local LLM usage')
    args = parser.parse_args()

    shell = Text2SQLShell(
        db_path=args.db,
        llm_url=args.llm_url,
        use_local_llm=not args.no_local_llm
    )
    shell.run_shell()


if __name__ == "__main__":
    main()