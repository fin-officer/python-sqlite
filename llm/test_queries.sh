#!/bin/bash

# Test script for SmartLLM SQLite integration

echo "Testing SmartLLM SQLite integration..."
echo "------------------------------------"

# Test 1: Create a user
echo "Test 1: Creating a user named John"
python smart_llm.py --query "create user John"
echo "------------------------------------"

# Test 2: Show all users
echo "Test 2: Showing all users"
python smart_llm.py --query "show all users"
echo "------------------------------------"

# Test 3: Create a product
echo "Test 3: Creating a product named Laptop"
python smart_llm.py --query "create a product named Laptop price 999.99"
echo "------------------------------------"

# Test 4: Show all products
echo "Test 4: Showing all products"
python smart_llm.py --query "show all products"
echo "------------------------------------"

echo "Tests completed!"
