#!/usr/bin/env python3
# rest_api.py - Uproszczone API REST dla text2sql

import os
import sys
import json
import argparse
import sqlite3
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException, Body, Query
from pydantic import BaseModel
import uvicorn


# Modele danych dla API
class SQLResult(BaseModel):
    sql: str
    message: str
    results: List[Dict[str, Any]] = []


class NaturalLanguageQuery(BaseModel):
    query: str


# Inicjalizacja aplikacji FastAPI
app = FastAPI(
    title="Text2SQL API",
    description="API dla tłumaczenia zapytań języka naturalnego na SQL i wykonywania ich",
    version="1.0.0"
)

# Ścieżka do bazy danych
DB_PATH = "text2sql.db"


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


def translate_to_sql(query: str) -> str:
    """Tłumaczy zapytanie w języku naturalnym na SQL (proste reguły)"""
    query = query.lower()

    if "create" in query and "user" in query and "named" in query:
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


def execute_query(sql: str) -> Dict[str, Any]:
    """Wykonuje zapytanie SQL na bazie danych"""
    conn = sqlite3.connect(DB_PATH)
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


@app.on_event("startup")
async def startup_event():
    """Zdarzenie uruchamiane przy starcie aplikacji"""
    create_db_if_not_exists(DB_PATH)


@app.get("/", tags=["General"])
async def root():
    """Endpoint powitalny"""
    return {
        "message": "Text2SQL API is running",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/schema", tags=["Schema"])
async def get_schema():
    """Pobiera schemat bazy danych"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
        rows = cursor.fetchall()
        schema = "\n".join(row[0] for row in rows if row[0])
        conn.close()
        return {"schema": schema}
    except sqlite3.Error as e:
        conn.close()
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
    """
    return {"examples": examples}


@app.post("/translate", response_model=str, tags=["SQL"])
async def translate_natural_to_sql(query: NaturalLanguageQuery):
    """Tłumaczy zapytanie w języku naturalnym na SQL"""
    sql = translate_to_sql(query.query)
    return sql


@app.post("/query", response_model=SQLResult, tags=["SQL"])
async def execute_sql(sql: str = Body(..., embed=True)):
    """Wykonuje zapytanie SQL"""
    result = execute_query(sql)
    return SQLResult(sql=sql, message=result["message"], results=result["results"])


@app.post("/natural", response_model=SQLResult, tags=["Natural Language"])
async def process_natural_language(query: NaturalLanguageQuery):
    """Przetwarza zapytanie w języku naturalnym, tłumaczy na SQL i wykonuje"""
    sql = translate_to_sql(query.query)
    if sql.startswith("--"):
        return SQLResult(sql=sql, message=f"Failed to translate: {sql}")

    result = execute_query(sql)
    return SQLResult(sql=sql, message=result["message"], results=result["results"])


def main():
    parser = argparse.ArgumentParser(description='Text2SQL REST API')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind the server to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind the server to')
    parser.add_argument('--db', default='text2sql.db', help='Path to SQLite database file')
    args = parser.parse_args()

    global DB_PATH
    DB_PATH = args.db

    print(f"Starting Text2SQL API server at http://{args.host}:{args.port}")
    print(f"API documentation available at http://{args.host}:{args.port}/docs")
    print(f"Using database at {DB_PATH}")

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()