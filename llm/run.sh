#!/bin/bash
# run.sh - Comprehensive script for running text2sql components

# Function to display help
show_help() {
    echo "Text2SQL - Natural language to SQL translation tool"
    echo ""
    echo "Usage:"
    echo "  ./run.sh [option] [arguments]"
    echo ""
    echo "Options:"
    echo "  shell                Run the interactive SQL shell with LLM integration"
    echo "  api                  Run the FastAPI REST server"
    echo "  llm                  Run the SmartLLM API server"
    echo "  models               Run the model selector shell"
    echo "  all                  Run all components together"
    echo "  install              Install all dependencies"
    echo "  install-model MODEL  Install a specific model (t5-small, gpt2, llama-cpp, all)"
    echo "  test                 Run the test suite"
    echo "  help                 Display this help message"
    echo ""
    echo "Environment Variables (can be set in .env file):"
    echo "  DB_PATH              Path to the SQLite database file (default: smart_llm.db)"
    echo "  MODEL_NAME           Name of the model to use (default: t5-small)"
    echo "  USE_ADVANCED         Whether to use advanced features (default: true)"
    echo "  DEBUG                Enable debug mode (default: false)"
    echo ""
}

# Function to install dependencies
install_dependencies() {
    echo "Installing dependencies..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
    else
        source venv/bin/activate
    fi
    
    # Install dependencies
    pip install -r requirements.txt
    
    echo "Dependencies installed successfully!"
}

# Function to install specific models
install_model() {
    model=$1
    echo "Installing model: $model"
    
    # Activate virtual environment
    if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        echo "Error: Virtual environment not found. Run './run.sh install' first."
        exit 1
    fi
    
    case "$model" in
        t5-small)
            pip install transformers sentencepiece
            python -c "from transformers import AutoTokenizer, AutoModelForSeq2SeqLM; AutoTokenizer.from_pretrained('t5-small'); AutoModelForSeq2SeqLM.from_pretrained('t5-small')"
            echo "T5-small model installed successfully!"
            ;;
        gpt2)
            pip install transformers
            python -c "from transformers import AutoTokenizer, AutoModelForCausalLM; AutoTokenizer.from_pretrained('gpt2'); AutoModelForCausalLM.from_pretrained('gpt2')"
            echo "GPT-2 model installed successfully!"
            ;;
        llama-cpp)
            # Try to install llama-cpp-python with system compiler
            echo "Attempting to install llama-cpp-python..."
            # Set environment variables to use system compiler
            export CC="gcc"
            export CXX="g++"
            # Try installation with CPU only
            pip install llama-cpp-python --no-cache-dir --verbose || {
                echo "Standard installation failed, trying with pre-built wheels..."
                pip install --force-reinstall --extra-index-url https://download.pytorch.org/whl/cpu llama-cpp-python==0.2.11+cpuavx2 || {
                    echo "WARNING: Could not install llama-cpp-python. This is optional and the system will still work without it."
                    echo "If you want to use llama-cpp models, you may need to install gcc/g++ or use a pre-built wheel."
                    echo "See https://github.com/abetlen/llama-cpp-python for more details."
                    return 1
                }
            }
            echo "llama-cpp installed successfully!"
            ;;
        all)
            # Install transformers and related packages
            pip install transformers sentencepiece
            
            # Install models
            python -c "from transformers import AutoTokenizer, AutoModelForSeq2SeqLM; AutoTokenizer.from_pretrained('t5-small'); AutoModelForSeq2SeqLM.from_pretrained('t5-small')"
            python -c "from transformers import AutoTokenizer, AutoModelForCausalLM; AutoTokenizer.from_pretrained('gpt2'); AutoModelForCausalLM.from_pretrained('gpt2')"
            
            # Try to install llama-cpp-python with system compiler
            echo "Attempting to install llama-cpp-python..."
            # Set environment variables to use system compiler
            export CC="gcc"
            export CXX="g++"
            # Try installation with CPU only
            pip install llama-cpp-python --no-cache-dir --verbose || {
                echo "Standard installation failed, trying with pre-built wheels..."
                pip install --force-reinstall --extra-index-url https://download.pytorch.org/whl/cpu llama-cpp-python==0.2.11+cpuavx2 || {
                    echo "WARNING: Could not install llama-cpp-python. This is optional and the system will still work without it."
                }
            }
            
            echo "All models installed successfully!"
            ;;
        *)
            echo "Unknown model: $model"
            echo "Available models: t5-small, gpt2, llama-cpp, all"
            exit 1
            ;;
    esac
}

# Function to create default database
create_database() {
    if [ ! -f "database.db" ]; then
        echo "Creating default database..."
        sqlite3 database.db "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT);"
        sqlite3 database.db "CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL, description TEXT);"
        echo "Created default database with users and products tables"
    fi
}

# Function to check if a package is installed
check_package() {
    if python -c "import $1" &>/dev/null; then
        return 0  # Installed
    else
        return 1  # Not installed
    fi
}

# Activate virtual environment if it exists
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Command line argument handling
case "$1" in
    shell)
        echo "Starting interactive SQL shell..."
        create_database
        # Run the shell directly instead of as a module
        python shell.py
        ;;
    api)
        echo "Starting FastAPI REST server..."
        if ! check_package "fastapi"; then
            echo "Error: fastapi package is not installed."
            echo "Run './run.sh install' first."
            exit 1
        fi
        uvicorn api:app --reload
        ;;
    llm)
        echo "Starting SmartLLM API server..."
        if ! check_package "transformers"; then
            echo "Error: transformers package is not installed."
            echo "Run './run.sh install' first."
            exit 1
        fi
        python smart_llm.py --server
        ;;
    models)
        echo "Starting model selector shell..."
        # Use a simple Python script to avoid module import issues
        python -c "
# Import directly from current directory
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

# Now import the module
from model_selector import ModelRegistry

# Print available models
print('Available models:')
for name, info in ModelRegistry.list_models().items():
    print(f\"- {name}: {info['description']}\")
        "
        ;;
    all)
        echo "Starting all components..."
        
        # Start SmartLLM in the background (if installed)
        if check_package "transformers"; then
            echo "Starting SmartLLM API server..."
            python smart_llm.py --server --port 8080 &
            llm_pid=$!
            sleep 3  # Give it time to start
        else
            echo "WARNING: transformers package is not installed. SmartLLM mode will be limited."
            llm_pid=""
        fi
        
        # Start FastAPI server in the background
        if check_package "fastapi"; then
            echo "Starting FastAPI REST server..."
            uvicorn api:app --port 8000 &
            api_pid=$!
            sleep 2  # Give it time to start
        else
            echo "WARNING: fastapi package is not installed. API server will not be available."
            api_pid=""
        fi
        
        # Start shell in the foreground
        echo "Starting interactive SQL shell..."
        create_database
        python shell.py
        
        # Stop background processes when shell exits
        if [ -n "$api_pid" ]; then
            echo "Stopping API server..."
            kill $api_pid 2>/dev/null || true
        fi
        
        if [ -n "$llm_pid" ]; then
            echo "Stopping SmartLLM server..."
            kill $llm_pid 2>/dev/null || true
        fi
        ;;
    install)
        install_dependencies
        ;;
    install-model)
        if [ -z "$2" ]; then
            echo "Error: No model specified."
            echo "Usage: ./run.sh install-model MODEL"
            echo "Available models: t5-small, gpt2, llama-cpp, all"
            exit 1
        fi
        install_model "$2"
        ;;
    test)
        echo "Running test suite..."
        if ! check_package "pytest"; then
            echo "Error: pytest package is not installed."
            echo "Run './run.sh install' first."
            exit 1
        fi
        PYTHONPATH=. pytest tests/
        ;;
    help|*)
        show_help
        ;;
esac