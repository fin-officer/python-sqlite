# rest_api.py - API REST dla text2sql

import os
import sys
import json
import asyncio
import argparse
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException, Body, Query
from pydantic import BaseModel
from uvicorn import Config, Server

from mcp.client import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# Modele danych dla API
class SQLResult(BaseModel):
    sql: str
    message: str
    results: List[Dict[str, Any]] = []


class NaturalLanguageQuery(BaseModel):
    query: str
    llm_endpoint: Optional[str] = None


# Inicjalizacja aplikacji FastAPI
app = FastAPI(
    title="Text2SQL API",
    description="API dla tłumaczenia zapytań języka naturalnego na SQL i wykonywania ich",
    version="1.0.0"
)

# Globalna sesja MCP
mcp_session = None


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
    global mcp_session
    try:
        schema, _ = await mcp_session.read_resource("schema://main")
        return {"schema": schema}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get schema: {str(e)}")


@app.get("/examples", tags=["Examples"])
async def get_examples():
    """Pobiera przykłady zapytań"""
    global mcp_session
    try:
        examples, _ = await mcp_session.read_resource("examples://queries")
        return {"examples": examples}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get examples: {str(e)}")


@app.post("/translate", response_model=str, tags=["SQL"])
async def translate_to_sql(query: NaturalLanguageQuery):
    """Tłumaczy zapytanie w języku naturalnym na SQL"""
    global mcp_session
    try:
        sql = await mcp_session.call_tool(
            "translate_to_sql",
            {"query": query.query, "llm_endpoint": query.llm_endpoint}
        )
        return sql
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@app.post("/query", response_model=SQLResult, tags=["SQL"])
async def execute_sql(sql: str = Body(..., embed=True)):
    """Wykonuje zapytanie SQL"""
    global mcp_session
    try:
        result = await mcp_session.call_tool("query_sql", {"sql": sql})
        return SQLResult(sql=sql, message=result["message"], results=result["results"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")


@app.post("/natural", response_model=SQLResult, tags=["Natural Language"])
async def process_natural_language(query: NaturalLanguageQuery):
    """Przetwarza zapytanie w języku naturalnym, tłumaczy na SQL i wykonuje"""
    global mcp_session
    try:
        result = await mcp_session.call_tool(
            "process_natural_query",
            {"query": query.query, "llm_endpoint": query.llm_endpoint}
        )
        return SQLResult(
            sql=result.get("sql", ""),
            message=result.get("message", ""),
            results=result.get("results", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


async def setup_mcp_session(db_path: str, server_script: str):
    """Konfiguruje sesję MCP"""
    global mcp_session

    # Parametry dla połączenia stdio
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_script],
        env={"DB_PATH": db_path} if db_path else None,
    )

    # Nawiązanie połączenia
    read_stream, write_stream = await stdio_client(server_params)

    # Utworzenie sesji klienta
    mcp_session = ClientSession(read_stream, write_stream)
    await mcp_session.initialize()

    # Inicjalizacja bazy danych
    await mcp_session.call_tool("setup_database")

    return mcp_session


async def start_server(host: str, port: int, db_path: str, server_script: str):
    """Uruchamia serwer API"""
    # Konfiguracja sesji MCP
    await setup_mcp_session(db_path, server_script)

    # Konfiguracja i uruchomienie serwera
    config = Config(app=app, host=host, port=port, log_level="info")
    server = Server(config)

    print(f"Starting Text2SQL API server at http://{host}:{port}")
    print(f"API documentation available at http://{host}:{port}/docs")

    await server.serve()


def main():
    parser = argparse.ArgumentParser(description='Text2SQL REST API')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind the server to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind the server to')
    parser.add_argument('--db', default='text2sql.db', help='Path to SQLite database file')
    parser.add_argument('--server', default='mcp_server.py', help='Path to MCP server script')
    args = parser.parse_args()

    asyncio.run(start_server(args.host, args.port, args.db, args.server))


if __name__ == "__main__":
    main()