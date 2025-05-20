#!/usr/bin/env python3
# smart_llm.py - Enhanced version of SmartLLM with SQLite database integration

import os
import sys
import time
import argparse
import json
import re
from typing import Dict, Any, List, Optional, Union

# Import the database manager
from db_manager import DatabaseManager

# Flaga, która określa, czy używamy zaawansowanego modelu
try:
    import transformers
    from transformers import pipeline

    HAS_ADVANCED_MODEL = True
except ImportError:
    HAS_ADVANCED_MODEL = False


class SmartLLM:
    """Inteligentny model językowy dla tłumaczenia zapytań na SQL"""

    def __init__(self, model_name: str = "t5-small", use_advanced: bool = False):  # Domyślnie False dla niezawodności
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
        """Clean up the model output, removing unnecessary prefixes and suffixes."""
        if not sql_text or not sql_text.strip():
            return "-- Empty SQL output"
            
        # First, try to find a complete SQL statement
        sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER"]
        
        # Extract the first complete SQL statement
        for keyword in sql_keywords:
            # Look for the keyword followed by text until a semicolon or end of string
            pattern = f"({keyword}[^;]*;?)"
            matches = re.finditer(pattern, sql_text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                sql = match.group(1).strip()
                # Ensure it ends with a semicolon
                if not sql.endswith(';'):
                    sql += ';'
                # Basic validation - the statement should be more than just the keyword
                if len(sql) > len(keyword) + 2:  # +2 for space and semicolon
                    return sql
        
        # If no complete statement found, clean up the text and try to extract
        # Remove common prefixes and suffixes
        prefixes_to_remove = [
            "SQLite SQL statement:",
            "Query:",
            "SQL:",
            "SQL (only return the SQL statement without explanation):",
            "Only return the SQL statement without any explanation or additional text:",
            "Natural language query:",
            "Generated SQL:",
            "Here is the SQL query:",
            "The SQL query is:",
            "```sql",
            "```"
        ]
        
        # Remove everything before the first SQL keyword
        for keyword in sql_keywords:
            idx = sql_text.upper().find(keyword)
            if idx >= 0:
                sql_text = sql_text[idx:]
                break
        
        # Remove common prefixes
        for prefix in prefixes_to_remove:
            sql_text = re.sub(f'^{re.escape(prefix)}', '', sql_text, flags=re.IGNORECASE)
            sql_text = re.sub(re.escape(prefix), '', sql_text, flags=re.IGNORECASE)
        
        # Clean up the text
        sql_text = ' '.join(sql_text.split())
        
        # Extract the first complete statement
        for keyword in sql_keywords:
            if sql_text.upper().startswith(keyword):
                # Find the end of the statement
                end_idx = sql_text.find(';')
                if end_idx > 0:
                    return sql_text[:end_idx+1].strip()
                else:
                    return sql_text + ';'
        
        # If we get here, we couldn't extract a valid SQL statement
        return "-- Could not generate valid SQL from: " + sql_text[:100] + ("..." if len(sql_text) > 100 else "")

    def translate(self, query: str, schema: Optional[str] = None) -> str:
        """Tłumaczy zapytanie w języku naturalnym na SQL"""
        if not query:
            return "-- Empty query"

        # Najpierw spróbuj z prostym mechanizmem tłumaczenia
        simple_sql = self._simple_translate(query)
        if not simple_sql.startswith("--"):
            return simple_sql

        # Jeśli prosty mechanizm nie zadziałał, a jest dostępny zaawansowany model, użyj go
        if self.use_advanced and self.model:
            # Przygotuj kontekst z schematem bazy danych
            if not schema:
                schema = """
                users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, created_at TIMESTAMP)
                products (id INTEGER PRIMARY KEY, name TEXT, price REAL, description TEXT)
                """

            # Przygotuj prompt dla modelu
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
                if sql.startswith("--"):
                    # Jeśli nie, zwróć komunikat błędu z simple_translate
                    return simple_sql

                return sql
            except Exception as e:
                print(f"Błąd generowania SQL: {str(e)}")
                # Fallback do komunikatu błędu z simple_translate
                return simple_sql
        else:
            # Jeśli nie ma zaawansowanego modelu, zwróć komunikat błędu z simple_translate
            return simple_sql

    def _simple_translate(self, query: str) -> str:
        """Prosty mechanizm tłumaczenia oparty na regułach"""
        query = query.lower()

        # Obsługa zapytań typu CREATE TABLE
        if "create table" in query:
            words = query.split()
            table_index = words.index("table")

            if table_index < len(words) - 1:
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

        # Alternatywna składnia dla create table
        elif "create" in query and "table" in query:
            words = query.split()
            create_index = words.index("create")

            if "table" in words and create_index < len(words) - 2:
                table_index = words.index("table")
                if table_index < len(words) - 1:
                    table_name = words[table_index + 1]
                    return f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    """

        # Handle CREATE USER queries
        elif "create" in query and "user" in query:
            # Extract the name
            name = ""
            email = None
            
            # Try to find the name after "named" or after "user"
            if "named" in query:
                named_idx = query.find("named")
                if named_idx > 0:
                    name_part = query[named_idx + 5:].strip()
                    name = name_part.split()[0] if name_part else ""
            
            # If name not found with "named", try to find it after "user"
            if not name:
                words = query.split()
                if "user" in words:
                    user_idx = words.index("user")
                    if user_idx < len(words) - 1:
                        name = words[user_idx + 1]
            
            # Clean up the name (remove any punctuation)
            if name:
                name = name.strip(".,!?\"'()[]{}<>")
            
            # Extract email if present
            email_match = re.search(r'email\s+([^\s]+@[^\s]+)', query, re.IGNORECASE)
            if email_match:
                email = email_match.group(1).strip()
            
            # Build the SQL query
            if name and email:
                return f"INSERT INTO users (name, email) VALUES ('{name}', '{email}');"
            elif name:
                return f"INSERT INTO users (name) VALUES ('{name}');"

        # Obsługa zapytań typu SHOW ALL USERS
        elif "show" in query and "all" in query and "users" in query:
            return "SELECT * FROM users;"

        # Obsługa alternatywnych zapytań dla wyświetlania użytkowników
        elif "show" in query and "users" in query:
            return "SELECT * FROM users;"
        elif "list" in query and "users" in query:
            return "SELECT * FROM users;"
        elif "get" in query and "users" in query:
            return "SELECT * FROM users;"

        # Obsługa zapytań typu CREATE PRODUCT
        elif "create" in query and "product" in query and "named" in query:
            # Znajdź nazwę po "named"
            named_index = query.find("named")
            if named_index > 0:
                name_part = query[named_index + 5:].strip()
                name = name_part.split()[0] if name_part else ""

                # Znajdź cenę po "price"
                price = None
                if "price" in query:
                    price_index = query.find("price")
                    if price_index > 0:
                        price_part = query[price_index + 5:].strip()
                        price = price_part.split()[0] if price_part else None

                # Sprawdź, czy podano opis
                description = None
                if "description" in query:
                    desc_index = query.find("description")
                    if desc_index > 0:
                        desc_part = query[desc_index + 11:].strip()

                        # Sprawdź, czy opis jest w cudzysłowie
                        if desc_part.startswith('"') and '"' in desc_part[1:]:
                            end_quote = desc_part[1:].find('"') + 1
                            description = desc_part[1:end_quote]
                        else:
                            description = desc_part.split()[0] if desc_part else None

                if name and price and description:
                    return f"INSERT INTO products (name, price, description) VALUES ('{name}', {price}, '{description}');"
                elif name and price:
                    return f"INSERT INTO products (name, price) VALUES ('{name}', {price});"

        # Obsługa zapytań typu SHOW ALL PRODUCTS
        elif "show" in query and "all" in query and "products" in query:
            return "SELECT * FROM products;"

        # Obsługa alternatywnych zapytań dla wyświetlania produktów
        elif "show" in query and "products" in query:
            return "SELECT * FROM products;"
        elif "list" in query and "products" in query:
            return "SELECT * FROM products;"
        elif "get" in query and "products" in query:
            return "SELECT * FROM products;"

        # Obsługa zapytań typu UPDATE
        elif "update" in query:
            if "user" in query:
                # Przykład: update user with id 1 set name to John
                words = query.split()

                # Znajdź ID
                id_value = None
                if "id" in words:
                    id_index = words.index("id")
                    if id_index < len(words) - 1:
                        id_value = words[id_index + 1]

                # Znajdź pole i wartość
                field = None
                value = None
                if "set" in words:
                    set_index = words.index("set")
                    if set_index < len(words) - 1:
                        field = words[set_index + 1]

                        # Znajdź wartość po "to"
                        if "to" in words and words.index("to") > set_index:
                            to_index = words.index("to")
                            if to_index < len(words) - 1:
                                value = words[to_index + 1]

                if id_value and field and value:
                    return f"UPDATE users SET {field} = '{value}' WHERE id = {id_value};"

            elif "product" in query:
                # Podobna logika dla produktów
                words = query.split()

                # Znajdź ID
                id_value = None
                if "id" in words:
                    id_index = words.index("id")
                    if id_index < len(words) - 1:
                        id_value = words[id_index + 1]

                # Znajdź pole i wartość
                field = None
                value = None
                if "set" in words:
                    set_index = words.index("set")
                    if set_index < len(words) - 1:
                        field = words[set_index + 1]

                        # Znajdź wartość po "to"
                        if "to" in words and words.index("to") > set_index:
                            to_index = words.index("to")
                            if to_index < len(words) - 1:
                                value = words[to_index + 1]

                if id_value and field and value:
                    # Jeśli field to price, nie dodawaj apostrofów
                    if field == "price":
                        return f"UPDATE products SET {field} = {value} WHERE id = {id_value};"
                    else:
                        return f"UPDATE products SET {field} = '{value}' WHERE id = {id_value};"

        # Obsługa zapytań typu DELETE
        elif "delete" in query:
            if "user" in query:
                # Przykład: delete user with id 1
                words = query.split()

                # Znajdź ID
                id_value = None
                if "id" in words:
                    id_index = words.index("id")
                    if id_index < len(words) - 1:
                        id_value = words[id_index + 1]

                if id_value:
                    return f"DELETE FROM users WHERE id = {id_value};"

            elif "product" in query:
                words = query.split()

                # Znajdź ID
                id_value = None
                if "id" in words:
                    id_index = words.index("id")
                    if id_index < len(words) - 1:
                        id_value = words[id_index + 1]

                if id_value:
                    return f"DELETE FROM products WHERE id = {id_value};"

        # Obsługa zapytań typu FIND
        elif "find" in query:
            if "user" in query:
                # Przykład: find user with name John
                words = query.split()

                # Znajdź wartość po "name"
                name_value = None
                if "name" in words:
                    name_index = words.index("name")
                    if name_index < len(words) - 1:
                        name_value = words[name_index + 1]

                if name_value:
                    return f"SELECT * FROM users WHERE name LIKE '%{name_value}%';"

            elif "product" in query:
                words = query.split()

                # Znajdź wartość po "name"
                name_value = None
                if "name" in words:
                    name_index = words.index("name")
                    if name_index < len(words) - 1:
                        name_value = words[name_index + 1]

                if name_value:
                    return f"SELECT * FROM products WHERE name LIKE '%{name_value}%';"

        # Obsługa zapytań typu SEARCH (alternatywa dla FIND)
        elif "search" in query:
            if "user" in query:
                # Przykład: search user with name John
                words = query.split()

                # Znajdź wartość po "name"
                name_value = None
                if "name" in words:
                    name_index = words.index("name")
                    if name_index < len(words) - 1:
                        name_value = words[name_index + 1]

                if name_value:
                    return f"SELECT * FROM users WHERE name LIKE '%{name_value}%';"

            elif "product" in query:
                words = query.split()

                # Znajdź wartość po "name"
                name_value = None
                if "name" in words:
                    name_index = words.index("name")
                    if name_index < len(words) - 1:
                        name_value = words[name_index + 1]

                if name_value:
                    return f"SELECT * FROM products WHERE name LIKE '%{name_value}%';"

        # Jeśli nie dopasowano żadnego wzorca
        return "-- Could not translate query to SQL"


def start_server(port=8080):
    """Start the SmartLLM API server with database integration"""
    from fastapi import FastAPI, HTTPException, status
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn

    app = FastAPI(title="SmartLLM API")
    
    # Enable CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class TranslationRequest(BaseModel):
        query: str
        schema: Optional[str] = None
        execute: bool = True

    # Initialize the model and database
    llm = SmartLLM()
    db = DatabaseManager()

    @app.get("/")
    def read_root():
        return {"message": "SmartLLM API is running"}

    @app.post("/translate")
    def translate_query(request: TranslationRequest):
        """Translate natural language to SQL and optionally execute it"""
        try:
            # Translate the query to SQL
            sql = llm.translate(request.query, request.schema)
            
            response = {
                "query": request.query,
                "sql": sql,
                "executed": False,
                "result": None,
                "error": None
            }
            
            # Execute the SQL if requested and it's a valid query
            if request.execute and not sql.startswith('--'):
                try:
                    result = db.execute_sql(sql)
                    response["executed"] = True
                    response["result"] = result
                except Exception as e:
                    response["error"] = str(e)
            
            return response
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": str(e)}
            )
    
    @app.post("/execute")
    def execute_sql_endpoint(request: TranslationRequest):
        """Execute raw SQL query"""
        try:
            sql = request.query.strip()
            if not sql:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"error": "Empty SQL query"}
                )
                
            result = db.execute_sql(sql)
            return {
                "sql": sql,
                "result": result,
                "error": None
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": str(e)}
            )

    print(f"Starting SmartLLM API server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)


def execute_sql(sql: str) -> str:
    """Execute SQL query using the database manager."""
    db = DatabaseManager()
    return db.execute_sql(sql)

def main():
    parser = argparse.ArgumentParser(description='SmartLLM for Text2SQL')
    parser.add_argument('--server', action='store_true', help='Run as API server')
    parser.add_argument('--port', type=int, default=8080, help='Server port (if running as server)')
    parser.add_argument('--query', type=str, help='Translate and execute a single query and exit')
    parser.add_argument('--execute-only', action='store_true', help='Execute the SQL directly without translation')
    args = parser.parse_args()

    if args.server:
        start_server(args.port)
    elif args.query:
        if args.execute_only:
            # Execute the query directly
            print(f"Executing SQL: {args.query}")
            result = execute_sql(args.query)
            print(result)
        else:
            # Translate and execute the query
            llm = SmartLLM()
            sql = llm.translate(args.query)
            print(f"Query: {args.query}")
            print(f"SQL: {sql}")
            if not sql.startswith('--'):  # If it's a valid SQL query
                result = execute_sql(sql)
                print("\nResult:")
                print(result)
    else:
        # Interactive mode
        llm = SmartLLM()
        db = DatabaseManager()
        print("SmartLLM Interactive Mode (type 'exit' to quit)")
        print("Enter a natural language query or SQL command (prefix with 'sql:' to execute raw SQL)")
        
        while True:
            try:
                user_input = input("\nQuery> ").strip()
                
                if user_input.lower() == 'exit':
                    break
                    
                if not user_input:
                    continue
                    
                # Check if it's a raw SQL command
                if user_input.lower().startswith('sql:'):
                    sql = user_input[4:].strip()
                    print(f"Executing SQL: {sql}")
                else:
                    # Translate natural language to SQL
                    sql = llm.translate(user_input)
                    print(f"SQL: {sql}")
                
                # Execute the SQL if it's valid
                if not sql.startswith('--'):
                    result = db.execute_sql(sql)
                    print("\nResult:")
                    print(result)
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()