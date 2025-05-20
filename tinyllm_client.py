# tinyllm_client.py - Klient do TinyLLM dla text2sql

import os
import sys
import json
import requests
from typing import Dict, Optional, Any


class TinyLLMClient:
    """Klient do usługi TinyLLM dla tłumaczenia języka naturalnego na SQL"""

    def __init__(self, endpoint="http://localhost:8080/v1/completions"):
        """Inicjalizacja klienta TinyLLM z określonym endpointem"""
        self.endpoint = endpoint

    def translate_to_sql(self, query: str, db_schema: Optional[str] = None) -> str:
        """Tłumaczy zapytanie w języku naturalnym na SQL używając TinyLLM"""
        # Tworzenie promptu dla modelu językowego
        if not db_schema:
            db_schema = """
            users (id, name, email, created_at)
            products (id, name, price, description)
            """

        prompt = f"""
        You are a Text-to-SQL converter.
        Convert the following natural language query to a valid SQLite SQL statement.
        The database has these tables:

        {db_schema}

        Natural language query: {query}

        Return ONLY the SQL statement without any explanation, comments, or backticks.
        """

        try:
            # Wywołanie usługi TinyLLM
            response = requests.post(
                self.endpoint,
                json={
                    "prompt": prompt,
                    "max_tokens": 200,
                    "temperature": 0.1
                },
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                # Wyciągnięcie SQL z odpowiedzi
                sql = result.get("choices", [{}])[0].get("text", "").strip()
                return sql
            else:
                return f"-- Error: TinyLLM service returned status code {response.status_code}"

        except requests.RequestException as e:
            return f"-- Error: Failed to connect to TinyLLM service: {str(e)}"


def main():
    # Przykładowe użycie klienta
    if len(sys.argv) < 2:
        print("Usage: python tinyllm_client.py 'natural language query'")
        return

    client = TinyLLMClient()
    query = " ".join(sys.argv[1:])

    print(f"Query: {query}")
    sql = client.translate_to_sql(query)
    print(f"SQL: {sql}")


if __name__ == "__main__":
    main()