# llm/sql_helper.py
from typing import List, Dict, Any, Tuple
import re
import sqlite3


class SQLHelper:
    @staticmethod
    def execute_sql(conn: sqlite3.Connection, query: str) -> Tuple[List[Dict[str, Any]], str]:
        """Execute SQL query with error handling and fallbacks."""
        try:
            cursor = conn.cursor()

            # Try direct execution first
            try:
                cursor.execute(query)
                if query.strip().upper().startswith('SELECT'):
                    columns = [desc[0] for desc in cursor.description]
                    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    return rows, ""
                else:
                    conn.commit()
                    return [{"rows_affected": cursor.rowcount}], ""

            except sqlite3.Error as e:
                # Try to suggest fixes for common errors
                error_msg = str(e).lower()
                if "no such table" in error_msg:
                    table_match = re.search(r"no such table: (\w+)", error_msg)
                    if table_match:
                        return [], f"Table '{table_match.group(1)}' doesn't exist. Available tables: {SQLHelper._get_table_names(conn)}"

                return [], str(e)

        except Exception as e:
            return [], f"Unexpected error: {str(e)}"

    @staticmethod
    def _get_table_names(conn: sqlite3.Connection) -> List[str]:
        """Get list of all table names in the database."""
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in cursor.fetchall()]

    @staticmethod
    def suggest_fixes(query: str, error: str) -> List[str]:
        """Suggest possible fixes for SQL queries."""
        query = query.lower()
        suggestions = []

        if "no such table" in error.lower():
            suggestions.append("Check if the table name is spelled correctly")
            suggestions.append("Use 'SHOW TABLES' to list available tables")

        if "syntax error" in error.lower():
            if "near" in error.lower():
                suggestions.append("Check the syntax around the highlighted part of your query")
            suggestions.append("Make sure all SQL keywords are in uppercase")
            suggestions.append("Check that all strings are properly quoted")

        if "ambiguous column" in error.lower():
            suggestions.append("Specify table name for ambiguous columns (e.g., table.column)")

        return suggestions