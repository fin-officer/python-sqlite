# mcp_server.py - Serwer MCP dla text2sql

import sqlite3
import os
from mcp.server.fastmcp import FastMCP


class Text2SQLServer:
    """Serwer MCP implementujący funkcjonalność text2sql"""

    def __init__(self, db_path="text2sql.db"):
        """Inicjalizacja serwera z określoną ścieżką do bazy danych"""
        self.db_path = db_path
        self.mcp = FastMCP("Text2SQL")
        self._setup_resources()
        self._setup_tools()

    def _setup_resources(self):
        """Konfiguracja zasobów MCP"""

        @self.mcp.resource("schema://main")
        def get_schema():
            """Udostępnia schemat bazy danych jako zasób"""
            conn = self._get_connection()
            schema = conn.execute("SELECT sql FROM sqlite_master WHERE type='table'").fetchall()
            conn.close()
            return "\n".join(sql[0] for sql in schema if sql[0])

        @self.mcp.resource("examples://queries")
        def get_example_queries():
            """Udostępnia przykładowe zapytania jako zasób"""
            return """
            # Przykładowe zapytania:
            - create a user named John
            - show all users
            - create a product named Laptop price 999.99
            - show all products
            """

    def _setup_tools(self):
        """Konfiguracja narzędzi MCP"""

        @self.mcp.tool()
        def setup_database():
            """Tworzy podstawowe tabele w bazie danych"""
            conn = self._get_connection()
            conn.execute('''
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

            conn.execute('''
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
            return "Baza danych została zainicjalizowana."

        @self.mcp.tool()
        def query_sql(sql: str):
            """Wykonuje zapytanie SQL na bazie danych"""
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
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

        @self.mcp.tool()
        def translate_to_sql(query: str, llm_endpoint: str = None):
            """Tłumaczy zapytanie w języku naturalnym na SQL"""
            # Prosta implementacja pattern-matching jako fallback
            # W rzeczywistej implementacji użylibyśmy LLM API, jeśli endpoint jest dostępny
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

        @self.mcp.tool()
        def process_natural_query(query: str, llm_endpoint: str = None):
            """Przetwarza zapytanie w języku naturalnym, tłumaczy na SQL i wykonuje"""
            sql = self.mcp.call_tool("translate_to_sql", {"query": query, "llm_endpoint": llm_endpoint})
            if sql.startswith("--"):
                return {"results": [], "message": f"Failed to translate: {sql}", "sql": sql}

            result = self.mcp.call_tool("query_sql", {"sql": sql})
            result["sql"] = sql
            return result

    def _get_connection(self):
        """Zwraca połączenie do bazy danych"""
        # Upewnij się, że katalog dla bazy danych istnieje
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def run(self):
        """Uruchamia serwer MCP"""
        # Upewnij się, że baza danych jest zainicjalizowana
        self.mcp.call_tool("setup_database")
        self.mcp.run()


if __name__ == "__main__":
    server = Text2SQLServer()
    server.run()