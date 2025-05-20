import sqlite3
from typing import List, Dict, Any, Optional
import os

class DatabaseManager:
    def __init__(self, db_path: str = "smart_llm.db"):
        """Initialize the database manager with a SQLite database."""
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _get_connection(self):
        """Create and return a new database connection."""
        return sqlite3.connect(self.db_path)
    
    def _ensure_db_exists(self):
        """Ensure the database file exists with required tables."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Enable foreign keys
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # Create users table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create products table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create orders table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # Create order_items table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER,
                    product_id INTEGER,
                    quantity INTEGER DEFAULT 1,
                    price REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
                )
            """)
            
            conn.commit()
            print(f"Database initialized successfully at: {self.db_path}")
            
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Error initializing database: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return the results as a list of dictionaries.
        
        Args:
            query: The SQL query to execute
            params: Optional parameters for the query
            
        Returns:
            List of dictionaries representing the query results
        """
        conn = None
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row  # This enables column access by name
            cursor = conn.cursor()
            
            # Check if it's a SELECT query
            is_select = query.strip().upper().startswith('SELECT')
            
            if is_select:
                cursor.execute(query, params)
                results = cursor.fetchall()
                # Convert rows to dictionaries
                return [dict(row) for row in results]
            else:
                # For non-SELECT queries (INSERT, UPDATE, DELETE, etc.)
                cursor.execute(query, params)
                conn.commit()
                
                # For INSERT with RETURNING clause
                if 'RETURNING' in query.upper():
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
                
                # Return the number of affected rows
                return [{"rows_affected": cursor.rowcount}]
                
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            return [{"error": str(e)}]
        finally:
            if conn:
                conn.close()
    
    def execute_sql(self, sql: str) -> str:
        """
        Execute SQL and return results as a formatted string.
        
        Args:
            sql: The SQL query to execute
            
        Returns:
            Formatted string with the query results
        """
        if not sql or not sql.strip() or sql.startswith('--'):
            return "No valid SQL query provided"
            
        try:
            results = self.execute_query(sql)
            
            if not results:
                return "Query executed successfully. No results to display."
                
            if "error" in results[0]:
                return f"Error: {results[0]['error']}"
                
            # Format the results as a table
            if not results:
                return "No results found."
                
            # Get column names
            columns = list(results[0].keys())
            
            # Format the output
            output = []
            
            # Add header
            header = " | ".join(columns)
            separator = "-" * len(header)
            output.append(header)
            output.append(separator)
            
            # Add rows
            for row in results:
                row_str = " | ".join(str(row.get(col, '')) for col in columns)
                output.append(row_str)
            
            # Add summary
            if len(results) == 1 and "rows_affected" in results[0]:
                output.append(f"\n{results[0]['rows_affected']} row(s) affected.")
            else:
                output.append(f"\n{len(results)} row(s) returned.")
                
            return "\n".join(output)
            
        except Exception as e:
            return f"Error executing query: {str(e)}"
