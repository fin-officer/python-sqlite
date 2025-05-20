#!/usr/bin/env python3
# smart_llm_refactored.py - Refactored version of SmartLLM with cleaner structure

import os
import sys
import time
import argparse
import json
import re
from typing import Dict, Any, List, Optional, Union

# Import the database manager
from db_manager import DatabaseManager

# Check if advanced models are available
try:
    import transformers
    from transformers import pipeline
    HAS_ADVANCED_MODEL = True
except ImportError:
    HAS_ADVANCED_MODEL = False


class SmartLLM:
    """Smart language model for translating natural language to SQL"""

    def __init__(self, model_name: str = "t5-small", use_advanced: bool = False):
        """Initialize the language model"""
        self.model_name = model_name
        self.use_advanced = use_advanced and HAS_ADVANCED_MODEL
        self.model = None

        if self.use_advanced:
            try:
                print(f"Loading model {model_name}...")
                self.model = pipeline(
                    "text2text-generation",
                    model=model_name,
                    device="cpu"  # Use CPU for compatibility
                )
                print(f"Model loaded successfully!")
            except Exception as e:
                print(f"Error loading model: {str(e)}")
                print("Using simple rule-based translation mechanism.")
                self.use_advanced = False

    def _clean_sql_output(self, sql_text: str) -> str:
        """Clean up the model output, removing unnecessary prefixes and suffixes."""
        if not sql_text or not sql_text.strip():
            return "-- Empty SQL output"

        # List of SQL keywords to detect valid SQL statements
        sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER", "PRAGMA"]
        
        # Extract the first complete statement
        for keyword in sql_keywords:
            if sql_text.upper().startswith(keyword):
                # Find the end of the statement
                end_idx = sql_text.find(';')
                if end_idx > 0:
                    return sql_text[:end_idx+1].strip()
                else:
                    return sql_text + ';'
        
        # If we get here, we couldn't extract a valid SQL statement
        return "-- Could not generate valid SQL from: " + sql_text[:100] + ("..." if len(sql_text) > 100 else "")

    def translate(self, query: str, schema: Optional[str] = None) -> str:
        """Translate natural language query to SQL"""
        if not query:
            return "-- Empty query"

        # First try with simple translation mechanism
        simple_sql = self._simple_translate(query)
        if not simple_sql.startswith("--"):
            return simple_sql

        # If simple mechanism failed and advanced model is available, use it
        if self.use_advanced and self.model:
            # Prepare context with database schema
            if not schema:
                schema = """
                users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, created_at TIMESTAMP)
                products (id INTEGER PRIMARY KEY, name TEXT, price REAL, description TEXT)
                """

            # Prepare prompt for the model
            prompt = f"""
            Translate the following natural language query to a valid SQLite SQL statement.

            Database schema:
            {schema}

            Natural language query: {query}

            Only return the SQL statement without any explanation or additional text:
            """

            try:
                outputs = self.model(prompt, max_length=200, temperature=0.1, do_sample=True)
                sql_raw = outputs[0]["generated_text"].strip()

                # Clean and fix the output
                sql = self._clean_sql_output(sql_raw)
                return sql
            except Exception as e:
                return f"-- Error using advanced model: {str(e)}\n{simple_sql}"
        else:
            # If no advanced model, return the error message from simple_translate
            return simple_sql

    def _simple_translate(self, query: str) -> str:
        """Simple rule-based translation mechanism for natural language to SQL"""
        # Normalize the query
        query = query.lower().strip()

        # ============================================================
        # TABLE LISTING COMMANDS
        # ============================================================
        
        # Handle 'show tables' or 'list tables' commands
        if any(phrase in query for phrase in ["show tables", "list tables", "show all tables", "list all tables", "display tables"]):
            return "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
            
        # Handle 'describe table' or 'show table structure' commands
        if any(phrase in query for phrase in ["describe table", "show table structure", "table info", "table schema"]):
            words = query.split()
            table_name = None
            
            # Look for table name after keywords
            for keyword in ["table", "for"]:
                if keyword in words and words.index(keyword) < len(words) - 1:
                    table_name = words[words.index(keyword) + 1]
                    break
            
            if table_name:
                return f"PRAGMA table_info({table_name});"
            else:
                return "-- Could not determine which table to describe"
        
        # ============================================================
        # TABLE CREATION COMMANDS
        # ============================================================
        
        # Handle 'create table' commands
        if "create table" in query or ("create" in query and "table" in query):
            words = query.split()
            table_index = words.index("table") if "table" in words else -1
            
            # Find table name
            table_name = None
            if table_index >= 0 and table_index < len(words) - 1:
                table_name = words[table_index + 1]
            elif "create" in words and words.index("create") < len(words) - 1:
                # Try to get name after 'create'
                possible_name = words[words.index("create") + 1]
                if possible_name != "table" and possible_name != "a" and possible_name != "new":
                    table_name = possible_name
            
            if not table_name:
                return "-- Could not determine table name from query"

            # Parse columns if specified with 'with' keyword
            columns = []
            if "with" in words:
                with_index = words.index("with")
                if with_index < len(words) - 1:
                    column_part = " ".join(words[with_index + 1:])
                    
                    # Parse columns separated by 'and'
                    if "and" in column_part:
                        column_names = [col.strip() for col in column_part.split("and")]
                        for col in column_names:
                            col = col.strip()
                            if col:
                                if "email" in col:
                                    columns.append(f"{col} TEXT")
                                elif any(term in col for term in ["price", "amount", "cost", "salary", "budget"]):
                                    columns.append(f"{col} REAL")
                                elif any(term in col for term in ["date", "time", "created", "updated"]):
                                    columns.append(f"{col} TIMESTAMP")
                                else:
                                    columns.append(f"{col} TEXT")
                    else:
                        # Single column without 'and'
                        col = column_part.strip()
                        if col:
                            if "email" in col:
                                columns.append(f"{col} TEXT")
                            elif any(term in col for term in ["price", "amount", "cost", "salary", "budget"]):
                                columns.append(f"{col} REAL")
                            elif any(term in col for term in ["date", "time", "created", "updated"]):
                                columns.append(f"{col} TIMESTAMP")
                            else:
                                columns.append(f"{col} TEXT")
            
            # Generate SQL based on table name and columns
            if columns:
                # Custom table with specified columns
                column_defs = ",\n                    ".join(columns)
                return f"""CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY,
                    {column_defs},
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );""".strip()
            else:
                # Predefined schemas for common tables
                if table_name.lower() in ["user", "users"]:
                    # User table schema
                    return f"""CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );""".strip()
                elif table_name.lower() in ["product", "products"]:
                    # Product table schema
                    return f"""CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    price REAL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );""".strip()
                elif table_name.lower() in ["order", "orders"]:
                    # Order table schema
                    return f"""CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );""".strip()
                else:
                    # Generic table schema
                    return f"""CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );""".strip()

        # ============================================================
        # DATA RETRIEVAL COMMANDS
        # ============================================================
        
        # Handle 'show all' or 'list all' commands
        if any(phrase in query for phrase in ["show all", "list all", "get all", "display all", "select all"]):
            for table in ["users", "products", "orders", "customers", "employees", "dogs"]:
                if table in query:
                    return f"SELECT * FROM {table};"
            
            # If no specific table found, try to extract it
            words = query.split()
            if "from" in words and words.index("from") < len(words) - 1:
                table = words[words.index("from") + 1]
                return f"SELECT * FROM {table};"
            
            # If we can't determine the table, return an error
            return "-- Could not determine which table to query"
        
        # Handle 'find' or 'search' commands
        if any(word in query for word in ["find", "search", "get", "where", "filter"]):
            # Try to determine the table
            table = None
            for possible_table in ["users", "products", "orders", "customers", "employees", "dogs"]:
                if possible_table in query:
                    table = possible_table
                    break
            
            if not table:
                return "-- Could not determine which table to search in"
            
            # Try to extract conditions
            conditions = []
            
            # Check for common condition patterns
            if "with" in query and query.index("with") < len(query) - 1:
                condition_part = query[query.index("with") + 4:]
                
                # Look for field=value patterns
                for field in ["id", "name", "email", "price", "status"]:
                    if field in condition_part:
                        # Try to extract the value
                        field_index = condition_part.index(field)
                        after_field = condition_part[field_index + len(field):].strip()
                        
                        # Look for patterns like "= value" or "is value"
                        if "=" in after_field:
                            value = after_field.split("=")[1].strip().split()[0]
                            conditions.append(f"{field} = '{value}'")
                        elif "is" in after_field:
                            value = after_field.split("is")[1].strip().split()[0]
                            conditions.append(f"{field} = '{value}'")
                        elif after_field.startswith(" "):
                            value = after_field.strip().split()[0]
                            conditions.append(f"{field} = '{value}'")
            
            # If we found conditions, build the query
            if conditions:
                where_clause = " AND ".join(conditions)
                return f"SELECT * FROM {table} WHERE {where_clause};"
            else:
                # If no conditions, return all rows
                return f"SELECT * FROM {table};"

        # ============================================================
        # DATA MODIFICATION COMMANDS
        # ============================================================
        
        # Handle 'create' or 'add' commands for records
        if ("create" in query or "add" in query) and "table" not in query:
            # Check for common entity types
            entity = None
            words = query.split()
            
            # Special case for 'add bird' type queries
            if "add" in words and len(words) >= 3:
                entity = words[1]  # Get the entity type (e.g., 'bird')
                name = words[2] if len(words) >= 3 else ""  # Get the name (e.g., 'sokół')
                
                # Make entity plural for table name
                table = f"{entity}s"
                
                # Create an insert statement
                return f"INSERT INTO {table} (name) VALUES ('{name}');"
            
            # Check for common entity types
            for possible_entity in ["user", "product", "order", "customer", "employee", "dog", "bird"]:
                if possible_entity in query:
                    entity = possible_entity
                    break
            
            if not entity:
                return "-- Could not determine what entity to create"
            
            # Make entity plural for table name
            table = f"{entity}s"
            
            # Try to extract fields and values
            fields = []
            values = []
            
            # Look for common field patterns
            if "named" in query and query.index("named") < len(query) - 1:
                name_part = query[query.index("named") + 5:].strip()
                name = name_part.split()[0] if name_part else ""
                if name:
                    fields.append("name")
                    values.append(f"'{name}'")
            
            if "with email" in query:
                email_part = query[query.index("with email") + 10:].strip()
                email = email_part.split()[0] if email_part else ""
                if email:
                    fields.append("email")
                    values.append(f"'{email}'")
            
            if "with price" in query:
                price_part = query[query.index("with price") + 10:].strip()
                price = price_part.split()[0] if price_part else ""
                if price:
                    fields.append("price")
                    values.append(price)
            
            # If we found fields and values, build the query
            if fields and values:
                fields_str = ", ".join(fields)
                values_str = ", ".join(values)
                return f"INSERT INTO {table} ({fields_str}) VALUES ({values_str});"
            else:
                return f"-- Could not extract fields and values for {entity}"
        
        # Handle 'update' commands
        if "update" in query:
            # Check for common entity types
            entity = None
            for possible_entity in ["user", "product", "order", "customer", "employee", "dog"]:
                if possible_entity in query:
                    entity = possible_entity
                    break
            
            if not entity:
                return "-- Could not determine what entity to update"
            
            # Make entity plural for table name
            table = f"{entity}s"
            
            # Try to extract condition and update values
            condition = None
            update_field = None
            update_value = None
            
            # Look for common condition patterns
            if "with id" in query:
                id_part = query[query.index("with id") + 7:].strip()
                id_value = id_part.split()[0] if id_part else ""
                if id_value and id_value.isdigit():
                    condition = f"id = {id_value}"
            
            # Look for update patterns
            if "set" in query and query.index("set") < len(query) - 1:
                set_part = query[query.index("set") + 3:].strip()
                
                # Look for field=value patterns
                for field in ["name", "email", "price", "status"]:
                    if field in set_part:
                        # Try to extract the value
                        field_index = set_part.index(field)
                        after_field = set_part[field_index + len(field):].strip()
                        
                        # Look for patterns like "to value" or "= value"
                        if "to" in after_field:
                            value = after_field.split("to")[1].strip().split()[0]
                            update_field = field
                            update_value = f"'{value}'"
                            break
                        elif "=" in after_field:
                            value = after_field.split("=")[1].strip().split()[0]
                            update_field = field
                            update_value = f"'{value}'"
                            break
            
            # If we found condition and update values, build the query
            if condition and update_field and update_value:
                return f"UPDATE {table} SET {update_field} = {update_value} WHERE {condition};"
            else:
                return f"-- Could not extract condition and update values for {entity}"
        
        # Handle 'delete' commands
        if "delete" in query or "remove" in query:
            # Special case for 'remove all tables with name X'
            if "remove all tables" in query or "delete all tables" in query:
                table_name = None
                # Extract table name after 'with name' or 'named'
                if "with name" in query:
                    name_part = query.split("with name")[1].strip()
                    table_name = name_part.split()[0] if name_part else None
                elif "named" in query:
                    name_part = query.split("named")[1].strip()
                    table_name = name_part.split()[0] if name_part else None
                
                if table_name:
                    return f"DROP TABLE IF EXISTS {table_name};"
                else:
                    return "-- Could not determine which table to remove"
            
            # Check for common entity types
            entity = None
            for possible_entity in ["user", "product", "order", "customer", "employee", "dog", "bird", "cat"]:
                if possible_entity in query:
                    entity = possible_entity
                    break
            
            if not entity:
                return "-- Could not determine what entity to delete"
            
            # Make entity plural for table name
            table = f"{entity}s"
            
            # Try to extract condition
            condition = None
            
            # Look for common condition patterns
            if "with id" in query:
                id_part = query[query.index("with id") + 7:].strip()
                id_value = id_part.split()[0] if id_part else ""
                if id_value and id_value.isdigit():
                    condition = f"id = {id_value}"
            
            # If we found a condition, build the query
            if condition:
                return f"DELETE FROM {table} WHERE {condition};"
            else:
                return f"-- Could not extract condition for deleting from {table}"
        
        # If we get here, we couldn't translate the query
        return "-- Could not translate query to SQL"


# API server components
class TranslationRequest:
    query: str
    schema: Optional[str] = None
    execute: bool = True


def main():
    parser = argparse.ArgumentParser(description="Smart LLM for natural language to SQL translation")
    parser.add_argument("--server", action="store_true", help="Run as API server")
    parser.add_argument("--port", type=int, default=8080, help="Port for API server")
    parser.add_argument("--query", type=str, help="Query to translate")
    args = parser.parse_args()

    # Initialize the model
    llm = SmartLLM(use_advanced=True)

    if args.server:
        # Import FastAPI components only when needed
        try:
            import uvicorn
            from fastapi import FastAPI, HTTPException
            from pydantic import BaseModel
            
            app = FastAPI(title="SmartLLM API", description="API for translating natural language to SQL")
            
            class TranslationRequest(BaseModel):
                query: str
                schema: Optional[str] = None
                execute: bool = True
            
            @app.get("/")
            def read_root():
                return {"message": "SmartLLM API is running"}
            
            @app.post("/translate")
            def translate_query(request: TranslationRequest):
                try:
                    sql = llm.translate(request.query, request.schema)
                    
                    response = {"sql": sql}
                    
                    if request.execute and not sql.startswith("--"):
                        # Execute the SQL if requested
                        db = DatabaseManager()
                        results = db.execute_sql(sql)
                        response["results"] = results
                    
                    return response
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))
            
            print(f"Starting SmartLLM API server on port {args.port}...")
            uvicorn.run(app, host="0.0.0.0", port=args.port)
            
        except ImportError:
            print("Error: FastAPI or Uvicorn not installed. Install with 'pip install fastapi uvicorn'.")
            sys.exit(1)
    elif args.query:
        # Translate the query
        sql = llm.translate(args.query)
        print(f"Query: {args.query}")
        print(f"SQL: {sql}")
        
        # Ask if the user wants to execute the SQL
        if not sql.startswith("--"):
            execute = input("Execute SQL? (y/n): ").lower() == "y"
            if execute:
                db = DatabaseManager()
                results = db.execute_sql(sql)
                print("Results:")
                print(json.dumps(results, indent=2))
    else:
        # Interactive mode
        print("SmartLLM Interactive Mode")
        print("Type 'exit' to quit")
        
        while True:
            query = input("Query: ")
            if query.lower() in ["exit", "quit"]:
                break
            
            sql = llm.translate(query)
            print(f"SQL: {sql}")
            
            if not sql.startswith("--"):
                execute = input("Execute SQL? (y/n): ").lower() == "y"
                if execute:
                    db = DatabaseManager()
                    results = db.execute_sql(sql)
                    print("Results:")
                    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
