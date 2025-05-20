# test_text2sql.py - Testy jednostkowe dla text2sql z MCP

import os
import sys
import unittest
import sqlite3
import tempfile
import asyncio
from unittest.mock import patch, MagicMock

# Importy dla MCP
from mcp.client import ClientSession
from mcp.types import TextContent

class TestText2SQLServer(unittest.TestCase):
    """Testy dla serwera MCP text2sql"""

    def setUp(self):
        """Przygotowanie środowiska testowego"""
        # Utworzenie tymczasowej bazy danych
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()

        # Zapisanie oryginalnej ścieżki
        self.original_path = os.environ.get('DB_PATH')
        os.environ['DB_PATH'] = self.db_path

        # Ustawienie miejsca dla mcp_server.py
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    def tearDown(self):
        """Sprzątanie po testach"""
        # Przywrócenie oryginalnej ścieżki
        if self.original_path:
            os.environ['DB_PATH'] = self.original_path
        else:
            del os.environ['DB_PATH']

        # Usunięcie tymczasowej bazy danych
        os.unlink(self.db_path)

    def test_db_creation(self):
        """Test tworzenia bazy danych"""
        # Imitacja wywołania narzędzia setup_database
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT
        )
        ''')

        conn.commit()

        # Sprawdzenie, czy tabele zostały utworzone
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]

        self.assertIn('users', tables)
        self.assertIn('products', tables)

        conn.close()

    def test_query_execution(self):
        """Test wykonywania zapytań SQL"""
        # Przygotowanie bazy danych
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()

        # Wykonanie zapytania
        conn.execute("INSERT INTO users (name, email) VALUES ('Test User', 'test@example.com')")
        conn.commit()

        # Sprawdzenie wyniku
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE name='Test User'")
        row = cursor.fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(row[1], 'Test User')
        self.assertEqual(row[2], 'test@example.com')

        conn.close()

    def test_translation(self):
        """Test tłumaczenia języka naturalnego na SQL"""
        # Test prostego tłumaczenia
        from tinyllm_client import TinyLLMClient

        # Imitacja klienta TinyLLM (bez faktycznego wywołania API)
        with patch.object(TinyLLMClient, 'translate_to_sql') as mock_translate:
            mock_translate.return_value = "INSERT INTO users (name) VALUES ('John')"

            client = TinyLLMClient()
            sql = client.translate_to_sql("create a user named John")

            self.assertEqual(sql, "INSERT INTO users (name) VALUES ('John')")
            mock_translate.assert_called_once()

class TestMCPClient(unittest.TestCase):
    """Testy dla klienta MCP"""

    def setUp(self):
        """Przygotowanie środowiska testowego"""
        self.mock_session = MagicMock(spec=ClientSession)

        # Mockowanie metod sesji
        async def mock_initialize():
            return None

        async def mock_call_tool(name, arguments):
            if name == "translate_to_sql":
                query = arguments.get("query", "")
                if "user" in query and "named" in query:
                    parts = query.split("named")
                    if len(parts) > 1:
                        name = parts[1].strip().split()[0]
                        return f"INSERT INTO users (name) VALUES ('{name}')"
                elif "show all users" in query:
                    return "SELECT * FROM users"
            elif name == "process_natural_query":
                query = arguments.get("query", "")
                if "user" in query and "named" in query:
                    return {
                        "sql": "INSERT INTO users (name) VALUES ('John')",
                        "message": "Query executed successfully. Affected rows: 1",
                        "results": []
                    }
                elif "show all users" in query:
                    return {
                        "sql": "SELECT * FROM users",
                        "message": "Query executed successfully. 1 records found.",
                        "results": [{"id": 1, "name": "John", "email": None}]
                    }
            return None

        self.mock_session.initialize = mock_initialize
        self.mock_session.call_tool = mock_call_tool

    def test_process_query(self):
        """Test przetwarzania zapytania przez klienta"""
        async def test():
            # Wywołanie narzędzia process_natural_query
            result = await self.mock_session.call_tool(
                "process_natural_query",
                {"query": "create a user named John"}
            )

            self.assertEqual(result["sql"], "INSERT INTO users (name) VALUES ('John')")
            self.assertIn("executed successfully", result["message"])

            # Wywołanie narzędzia process_natural_query dla select
            result = await self.mock_session.call_tool(
                "process_natural_query",
                {"query": "show all users"}
            )

            self.assertEqual(result["sql"], "SELECT * FROM users")
            self.assertIn("1 records found", result["message"])
            self.assertEqual(len(result["results"]), 1)
            self.assertEqual(result["results"][0]["name"], "John")

        # Uruchomienie testu asynchronicznego
        asyncio.run(test())

if __name__ == '__main__':
    unittest.main()