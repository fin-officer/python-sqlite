# llm/shell.py
import cmd
from typing import List, Dict, Any
import sqlite3
from dataclasses import dataclass

# Import from the same package
from .sql_helper import SQLHelper
from .model_selector import ModelRegistry, ModelContext

@dataclass
class LLMModel:
    name: str
    size: int  # in millions of parameters
    context_window: int
    supports_sql: bool = True

class LLMModelSelector:
    def __init__(self):
        self.models = [
            LLMModel("GPT-2 Small", 124, 1024),
            LLMModel("GPT-2 Medium", 355, 1024),
            LLMModel("GPT-2 Large", 774, 1024),
            LLMModel("GPT-2 XL", 1500, 1024),
            LLMModel("T5-Small", 60, 512),
            LLMModel("T5-Base", 220, 512),
            LLMModel("DistilGPT-2", 82, 1024),
        ]
        
    def get_available_models(self, max_size_mb: int = 2000):
        return [m for m in self.models if m.size <= max_size_mb]
        
    def save_model_context(self, model_name: str, context: str):
        # In a real implementation, this would save to a database
        print(f"Context saved for {model_name}")
        return True


class LLMSQLShell(cmd.Cmd):
    intro = "LLM SQL Shell. Type 'help' for commands, 'exit' to quit."
    prompt = "SQL> "

    def __init__(self, db_path: str = "database.db"):
        super().__init__()
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.model_selector = LLMModelSelector()
        self.current_model = None
        self.context = ""

    def do_models(self, arg):
        """List available LLM models."""
        models = self.model_selector.get_available_models(max_size_mb=2000)
        for i, model in enumerate(models, 1):
            print(f"{i}. {model.name} ({model.size}M params, {model.context_window} tokens)")

    def do_use(self, arg):
        """Select a model by number or name."""
        if not arg:
            print("Please specify a model number or name")
            return

        models = self.model_selector.get_available_models()

        # Try to match by number
        try:
            model_num = int(arg) - 1
            if 0 <= model_num < len(models):
                self.current_model = models[model_num]
                print(f"Selected model: {self.current_model.name}")
                return
        except ValueError:
            pass

        # Try to match by name
        for model in models:
            if arg.lower() in model.name.lower():
                self.current_model = model
                print(f"Selected model: {self.current_model.name}")
                return

        print("Model not found. Use 'models' to see available models.")

    def do_context(self, arg):
        """Show or set the current context."""
        if not arg:
            print("Current context:", self.context)
        else:
            self.context = arg
            if self.current_model:
                self.model_selector.save_model_context(self.current_model.name, arg)
            print("Context updated.")

    def do_tables(self, arg):
        """List all tables in the database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print("\n".join(tables) if tables else "No tables found")

    def do_exit(self, arg):
        """Exit the shell."""
        print("Goodbye!")
        self.conn.close()
        return True

    def default(self, line):
        """Handle SQL queries."""
        if not line.strip():
            return

        # Handle special commands
        if line.lower() in ("tables", "show tables", "list tables"):
            self.do_tables("")
            return

        # Execute SQL
        results, error = SQLHelper.execute_sql(self.conn, line)

        if error:
            print(f"Error: {error}")
            suggestions = SQLHelper.suggest_fixes(line, error)
            if suggestions:
                print("\nSuggestions:")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"{i}. {suggestion}")
        else:
            self._display_results(results)

    def _display_results(self, results: List[Dict[str, Any]]) -> None:
        """Display query results in a formatted table."""
        if not results:
            print("No results")
            return

        # Handle non-SELECT queries
        if len(results) == 1 and "rows_affected" in results[0]:
            print(f"\n{results[0]['rows_affected']} row(s) affected.\n")
            return

        # Display SELECT results
        headers = list(results[0].keys())
        rows = [[str(row[col] if row[col] is not None else "NULL") for col in headers]
                for row in results]

        # Calculate column widths
        col_widths = [
            max(len(headers[i]), *(len(row[i]) for row in rows))
            for i in range(len(headers))
        ]

        # Print header
        header = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
        print("\n" + header)
        print("-" * len(header))

        # Print rows
        for row in rows:
            print(" | ".join(val.ljust(w) for val, w in zip(row, col_widths)))

        print(f"\n{len(rows)} row(s) returned.\n")


def main():
    import sys
    db_path = sys.argv[1] if len(sys.argv) > 1 else "database.db"
    LLMSQLShell(db_path).cmdloop()


if __name__ == "__main__":
    main()