import pytest
import sqlite3
from llm.sql_helper import SQLHelper

@pytest.fixture
def test_db():
    """Create a test database with sample tables"""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Create test tables
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL,
            description TEXT
        )
    """)
    
    # Insert sample data
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("John Doe", "john@example.com"))
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Jane Smith", "jane@example.com"))
    cursor.execute("INSERT INTO products (name, price, description) VALUES (?, ?, ?)", 
                  ("Laptop", 999.99, "High-performance laptop"))
    
    conn.commit()
    return conn

def test_execute_sql_select(test_db):
    """Test executing a SELECT query"""
    results, error = SQLHelper.execute_sql(test_db, "SELECT * FROM users")
    
    assert error == ""
    assert len(results) == 2
    assert results[0]["name"] == "John Doe"
    assert results[1]["email"] == "jane@example.com"

def test_execute_sql_insert(test_db):
    """Test executing an INSERT query"""
    results, error = SQLHelper.execute_sql(test_db, 
                                         "INSERT INTO users (name, email) VALUES ('Bob Johnson', 'bob@example.com')")
    
    assert error == ""
    assert results[0]["rows_affected"] == 1
    
    # Verify the insert worked
    cursor = test_db.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    assert count == 3

def test_execute_sql_error(test_db):
    """Test handling SQL errors"""
    results, error = SQLHelper.execute_sql(test_db, "SELECT * FROM nonexistent_table")
    
    assert results == []
    assert "no such table" in error.lower()

def test_suggest_fixes():
    """Test SQL error suggestion functionality"""
    suggestions = SQLHelper.suggest_fixes(
        "SELECT * FROM nonexistent_table", 
        "no such table: nonexistent_table"
    )
    
    assert len(suggestions) > 0
    assert any("table name" in s.lower() for s in suggestions)
    
    syntax_suggestions = SQLHelper.suggest_fixes(
        "SELECT FROM users", 
        "syntax error near FROM"
    )
    
    assert len(syntax_suggestions) > 0
    assert any("syntax" in s.lower() for s in syntax_suggestions)
