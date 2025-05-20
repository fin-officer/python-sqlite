#!/usr/bin/env python3
"""
Comprehensive test script for database operations in SmartLLM.
"""
import os
import sqlite3
import time
from typing import List, Dict, Any
from db_manager import DatabaseManager

class DatabaseTester:
    """Class to test database operations."""
    
    def __init__(self, db_path: str = "test_db.sqlite"):
        """Initialize the tester with a database path."""
        # Remove existing test database if it exists
        if os.path.exists(db_path):
            os.remove(db_path)
            
        self.db = DatabaseManager(db_path)
    
    def print_table(self, table_name: str) -> None:
        """Print all rows from a table."""
        try:
            rows = self.db.execute_query(f"SELECT * FROM {table_name}")
            print(f"\n--- {table_name.upper()} ---")
            if not rows:
                print("No rows found")
                return
                
            # Print headers
            headers = list(rows[0].keys())
            print(" | ".join(headers))
            print("-" * (sum(len(h) for h in headers) + 3 * (len(headers) - 1)))
            
            # Print rows
            for row in rows:
                print(" | ".join(str(row[h]) for h in headers))
                
        except sqlite3.Error as e:
            print(f"Error reading {table_name}: {e}")
    
    def test_users(self) -> None:
        """Test user-related operations."""
        print("\n=== Testing User Operations ===")
        
        # Insert test users
        test_users = [
            ("John Doe", "john@example.com"),
            ("Jane Smith", "jane@example.com"),
            ("Bob Johnson", None)
        ]
        
        for name, email in test_users:
            if email:
                result = self.db.execute_query(
                    "INSERT INTO users (name, email) VALUES (?, ?) RETURNING id",
                    (name, email)
                )
            else:
                result = self.db.execute_query(
                    "INSERT INTO users (name) VALUES (?) RETURNING id",
                    (name,)
                )
            print(f"Added user: {name}" if not isinstance(result, list) or not any('error' in r for r in result) 
                  else f"Error adding user {name}: {result}")
        
        # Print all users
        self.print_table("users")
    
    def test_products(self) -> None:
        """Test product-related operations."""
        print("\n=== Testing Product Operations ===")
        
        # Insert test products
        test_products = [
            ("Laptop", 999.99, "High-performance laptop"),
            ("Mouse", 29.99, "Wireless mouse"),
            ("Keyboard", 59.99, "Mechanical keyboard")
        ]
        
        for name, price, description in test_products:
            result = self.db.execute_query(
                """INSERT INTO products (name, price, description) 
                   VALUES (?, ?, ?) RETURNING id""",
                (name, price, description)
            )
            print(f"Added product: {name}" if not isinstance(result, list) or not any('error' in r for r in result)
                  else f"Error adding product {name}: {result}")
        
        # Print all products
        self.print_table("products")
    
    def test_orders(self) -> None:
        """Test order-related operations."""
        print("\n=== Testing Order Operations ===")
        
        # First, get a user ID
        users = self.db.execute_query("SELECT id FROM users LIMIT 1")
        if not users or 'error' in users[0]:
            print("No users found. Please add users first.")
            return
            
        user_id = users[0]['id']
        
        # Create an order
        result = self.db.execute_query(
            "INSERT INTO orders (user_id, status) VALUES (?, ?) RETURNING id",
            (user_id, 'pending')
        )
        
        if isinstance(result, list) and 'error' in result[0]:
            print(f"Error creating order: {result}")
            return
            
        order_id = result[0]['id']
        print(f"Created order with ID: {order_id}")
        
        # Add items to the order
        products = self.db.execute_query("SELECT id, price FROM products")
        if not products or 'error' in products[0]:
            print("No products found. Please add products first.")
            return
            
        for i, product in enumerate(products[:2], 1):  # Add first 2 products to the order
            self.db.execute_query(
                """INSERT INTO order_items 
                   (order_id, product_id, quantity, price)
                   VALUES (?, ?, ?, ?)""",
                (order_id, product['id'], i, product['price'])
            )
        
        # Print the order details
        self.print_table("orders")
        self.print_table("order_items")
    
    def run_all_tests(self) -> None:
        """Run all test cases."""
        print("Starting database tests...")
        
        try:
            self.test_users()
            self.test_products()
            self.test_orders()
            
            print("\n=== Final Database State ===")
            for table in ["users", "products", "orders", "order_items"]:
                self.print_table(table)
                
            print("\nAll tests completed successfully!")
            
        except Exception as e:
            print(f"\nTest failed with error: {e}")
            raise

if __name__ == "__main__":
    tester = DatabaseTester("test_db.sqlite")
    tester.run_all_tests()
