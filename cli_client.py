# cli_client.py - Interaktywny klient CLI dla text2sql

import os
import sys
import argparse
import readline  # Dla historii komend
import asyncio
from mcp.client import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class Text2SQLShell:
    """Interaktywny shell dla text2sql"""

    def __init__(self, db_path="text2sql.db", server_script="mcp_server.py"):
        """Inicjalizacja klienta shell"""
        self.db_path = db_path
        self.server_script = server_script
        self.llm_endpoint = None

    async def connect(self):
        """Nawiązuje połączenie z serwerem MCP"""
        # Parametry dla połączenia stdio
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[self.server_script],
            env={"DB_PATH": self.db_path} if self.db_path else None,
        )

        # Nawiązanie połączenia
        read_stream, write_stream = await stdio_client(server_params)

        # Utworzenie sesji klienta
        self.session = ClientSession(read_stream, write_stream)
        await self.session.initialize()

        # Sprawdzenie, czy serwer jest dostępny
        tools = await self.session.list_tools()
        if not tools:
            print("Error: Failed to connect to MCP server.")
            sys.exit(1)

        # Sprawdzenie, czy udało się połączyć z bazą danych
        try:
            await self.session.call_tool("setup_database")
        except Exception as e:
            print(f"Error initializing database: {e}")
            sys.exit(1)

        return self.session

    async def run_shell(self):
        """Uruchamia interaktywny shell"""
        print("\n=== Text2SQL Interactive Shell (MCP) ===")
        print("Type natural language queries to interact with the database.")

        # Pobierz przykładowe zapytania
        try:
            examples, _ = await self.session.read_resource("examples://queries")
            print(examples)
        except:
            print("Examples: 'create a user named John', 'show all users'")

        print("Type 'exit' or 'quit' to end the session.\n")

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
                elif user_input.lower().startswith('llm '):
                    # Ustawienie endpointu LLM
                    self.llm_endpoint = user_input[4:].strip()
                    print(f"LLM endpoint set to: {self.llm_endpoint}")
                    continue

                # Wywołanie narzędzia do przetwarzania zapytania
                result = await self.session.call_tool(
                    "process_natural_query",
                    {"query": user_input, "llm_endpoint": self.llm_endpoint}
                )

                # Wyświetlenie wyników
                self.display_results(result)

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

    def print_help(self):
        """Wyświetla pomoc dla użytkownika"""
        print("\nAvailable commands:")
        print("  help                    - Display this help message")
        print("  exit, quit              - Exit the shell")
        print("  llm <endpoint>          - Set LLM endpoint (optional)")
        print("  <natural language>      - Any natural language query to the database\n")


async def main():
    parser = argparse.ArgumentParser(description='Text2SQL Interactive Shell')
    parser.add_argument('--db', default='text2sql.db', help='Path to SQLite database file')
    parser.add_argument('--server', default='mcp_server.py', help='Path to MCP server script')
    args = parser.parse_args()

    shell = Text2SQLShell(args.db, args.server)
    await shell.connect()
    await shell.run_shell()


if __name__ == "__main__":
    asyncio.run(main())