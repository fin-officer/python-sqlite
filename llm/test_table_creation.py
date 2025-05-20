#!/usr/bin/env python3
"""
Test script for table creation functionality in SmartLLM.
"""
import os
import sqlite3
from smart_llm import SmartLLM
from db_manager import DatabaseManager

def test_table_creation():
    """Test table creation with different table names."""
    # Create a test database
    test_db_path = "test_table_creation.db"
    
    # Remove existing test database if it exists
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Initialize database manager
    db_manager = DatabaseManager(test_db_path)
    
    # Initialize SmartLLM
    llm = SmartLLM(use_advanced=False)  # Use simple translation mode
    
    # Test different table creation queries
    test_queries = [
        "create dogs table",
        "create users table",
        "create products table",
        "create orders table",
        "create custom_table with name and description"
    ]
    
    print("=== Testing Table Creation ===\n")
    
    for query in test_queries:
        print(f"Query: {query}")
        sql = llm.translate(query)
        print(f"Generated SQL: {sql}")
        
        try:
            result = db_manager.execute_sql(sql)
            print(f"Result: {result}\n")
        except Exception as e:
            print(f"Error: {e}\n")
    
    # List all tables in the database
    print("=== Tables in Database ===\n")
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    for table in tables:
        print(f"Table: {table[0]}")
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        print()
    
    conn.close()

if __name__ == "__main__":
    test_table_creation()
