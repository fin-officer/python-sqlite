#!/usr/bin/env python3
# rest_api.py - Rozszerzone API REST dla text2sql

import os
import sys
import json
import argparse
import sqlite3
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException, Body, Query, Depends
from pydantic import BaseModel
import uvicorn

# Importuj nasz SmartLLM
try:
    from llm import SmartLLM

    HAS_SMART_LLM = True
except ImportError:
    HAS_SMART_LLM = False


# Modele danych dla API
class SQLResult(BaseModel):
    sql: str
    message: str
    results: List[Dict[str, Any]] = []


class NaturalLanguageQuery(BaseModel):
    query: str
    use_llm: bool = True


class CreateTableRequest(BaseModel):
    table_name: str
    columns: List[Dict[str, str]]


# Inicjalizacja aplikacji FastAPI
app = FastAPI(
    title="Text2SQL API Extended",
    description="Rozszerzone API dla tłumaczenia zapytań języka naturalnego na SQL i wykonywania ich",
    version="1.0.0"
)

# Globalne zmienne
DB_PATH = "../text2sql.db"
llm = None

# Inicjalizacja SmartLLM, jeśli dostępny
if HAS_SMART_LLM:
    try:
        llm = SmartLLM()
        print("Używanie SmartLLM dla tłumaczenia zapytań.")
    except Exception as e:
        print(f"Błąd inicjalizacji SmartLLM: {str(e)}")
        llm = None


def get_db_connection():
    """Zwraca połączenie do bazy danych"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_db_if_not_exists(db_path):
    """Tworzy bazę danych, jeśli nie istnieje"""
    if not os.path.exists(db_path):
        print(f"Tworzenie nowej bazy danych: {db_path}")
        conn = sqlite3.connect(db_path)
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


def get_schema():
    """Pobiera schemat bazy danych"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
    schema_rows = cursor.fetchall()
    conn.close()

    return "\n".join(row[0] for row in schema_rows if row[0])


def translate_to_sql(query: str, use_llm: bool = True):
    """Tłumaczy zapytanie w języku naturalnym na SQL"""
    # Jeśli mamy dostęp do SmartLLM i użytkownik chce go użyć
    if HAS_SMART_LLM and llm and use_llm:
        try:
            schema = get_schema()
            return llm.translate(query, schema)
        except Exception as e:
            print(f"Błąd tłumaczenia z SmartLLM: {str(e)}")
            # Fallback do prostego mechanizmu

    # Prosty mechanizm tłumaczenia oparty na regułach
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

    # Obsługa wyszukiwania
    elif "find" in query:
        if "user" in query and "name" in query:
            words = query.split()
            name_index = words.index("name") if "name" in words else -1

            if name_index > 0 and name_index < len(words) - 1:
                name = words[name_index + 1]
                return f"SELECT * FROM users WHERE name LIKE '%{name}%'"

        elif "product" in query and "name" in query:
            words = query.split()
            name_index = words.index("name") if "name" in words else -1

            if name_index > 0 and name_index < len(words) - 1:
                name = words[name_index + 1]
                return f"SELECT * FROM products WHERE name LIKE '%{name}%'"

    # Obsługa usuwania
    elif "delete" in query:
        if "user" in query and "id" in query:
            words = query.split()
            id_index = words.index("id") if "id" in words else -1

            if id_index > 0 and id_index < len(words) - 1:
                user_id = words[id_index + 1]
                return f"DELETE FROM users WHERE id = {user_id}"

        elif "product" in query and "id" in query:
            words = query.split()
            id_index = words.index("id") if "id" in words else -1

            if id_index > 0 and id_index < len(words) - 1:
                product_id = words[id_index + 1]
                return f"DELETE FROM products WHERE id = {product_id}"

    return "-- Could not translate query to SQL"


def execute_query(sql: str) -> Dict[str, Any]:
    """Wykonuje zapytanie SQL na bazie danych"""
    conn = get_db_connection()
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


@app.on_event("startup")
async def startup_event():
    """Zdarzenie uruchamiane przy starcie aplikacji"""
    create_db_if_not_exists(DB_PATH)


@app.get("/", tags=["General"])
async def root():
    """Endpoint powitalny"""
    return {
        "message": "Text2SQL Extended API is running",
        "docs": "/docs",
        "version": "1.0.0",
        "llm_available": HAS_SMART_LLM and llm is not None
    }


@app.get("/schema", tags=["Schema"])
async def get_db_schema():
    """Pobiera schemat bazy danych"""
    try:
        schema = get_schema()
        return {"schema": schema}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to get schema: {str(e)}")


@app.get("/examples", tags=["Examples"])
async def get_examples():
    """Pobiera przykłady zapytań"""
    examples = """
    # Przykładowe zapytania:
    - create a user named John
    - show all users
    - create a product named Laptop price 999.99
    - show all products
    - find user with name John
    - update user with id 1 set name to Mike
    - delete user with id 2
    """
    return {"examples": examples}


@app.post("/translate", response_model=str, tags=["SQL"])
async def translate_natural_to_sql(query: NaturalLanguageQuery):
    """Tłumaczy zapytanie w języku naturalnym na SQL"""
    sql = translate_to_sql(query.query, query.use_llm)
    return sql


@app.post("/query", response_model=SQLResult, tags=["SQL"])
async def execute_sql_query(sql: str = Body(..., embed=True)):
    """Wykonuje zapytanie SQL"""
    result = execute_query(sql)
    return SQLResult(sql=sql, message=result["message"], results=result["results"])


@app.post("/natural", response_model=SQLResult, tags=["Natural Language"])
async def process_natural_language(query: NaturalLanguageQuery):
    """Przetwarza zapytanie w języku naturalnym, tłumaczy na SQL i wykonuje"""
    sql = translate_to_sql(query.query, query.use_llm)
    if sql.startswith("--"):
        return SQLResult(sql=sql, message=f"Failed to translate: {sql}")

    result = execute_query(sql)
    return SQLResult(sql=sql, message=result["message"], results=result["results"])


@app.post("/create-table", response_model=SQLResult, tags=["Schema"])
async def create_table(request: CreateTableRequest):
    """Tworzy nową tabelę w bazie danych"""
    column_defs = []
    for col in request.columns:
        name = col.get("name")
        type = col.get("type", "TEXT")
        constraints = col.get("constraints", "")
        column_defs.append(f"{name} {type} {constraints}".strip())

    sql = f"""
    CREATE TABLE IF NOT EXISTS {request.table_name} (
        id INTEGER PRIMARY KEY,
        {', '.join(column_defs)}
    )
    """

    result = execute_query(sql)
    return SQLResult(sql=sql, message=result["message"], results=result["results"])


@app.get("/tables", tags=["Schema"])
async def list_tables():
    """Pobiera listę tabel w bazie danych"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return {"tables": tables}


@app.get("/table/{table_name}", tags=["Schema"])
async def get_table_info(table_name: str):
    """Pobiera informacje o tabeli"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Pobierz schemat tabeli
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = []
        for row in cursor.fetchall():
            columns.append({
                "cid": row[0],
                "name": row[1],
                "type": row[2],
                "notnull": row[3],
                "default_value": row[4],
                "pk": row[5]
            })

        # Pobierz liczbę wierszy
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]

        conn.close()
        return {
            "table_name": table_name,
            "columns": columns,
            "row_count": row_count
        }
    except sqlite3.Error as e:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Table not found or error: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description='Text2SQL Extended REST API')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind the server to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind the server to')
    parser.add_argument('--db', default='text2sql.db', help='Path to SQLite database file')
    args = parser.parse_args()

    global DB_PATH
    DB_PATH = args.db

    print(f"Starting Text2SQL Extended API server at http://{args.host}:{args.port}")
    print(f"API documentation available at http://{args.host}:{args.port}/docs")
    print(f"Using database at {DB_PATH}")
    print(f"SmartLLM available: {HAS_SMART_LLM and llm is not None}")

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()