#!/bin/bash

# Parse options
install_playwright=false
while getopts "p" opt; do
    case ${opt} in
        p ) install_playwright=true ;;
        \? ) echo "Usage: install.sh [-p]" ;;
    esac
done

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "🤖 Installing Agent-E..."

# Check Python version
if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.10 or higher."
    exit 1
fi

# Playwright installation check
if [ "$install_playwright" = false ]; then
    read -p "Would you like to install Playwright drivers? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_playwright=true
    fi
fi

# Install uv if not present
if ! command_exists uv; then
    echo "📦 Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add uv to current shell session
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create and activate virtual environment
echo "🔧 Creating virtual environment..."
uv venv --python 3.11

# Determine the activation script based on OS
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    if [ -f .venv/Scripts/activate ]; then
        source .venv/Scripts/activate
    else
        echo "❌ Virtual environment activation script not found. Ensure virtual environment is created successfully."
        exit 1
    fi
else
    if [ -f .venv/bin/activate ]; then
        source .venv/bin/activate
    else
        echo "❌ Virtual environment activation script not found. Ensure virtual environment is created successfully."
        exit 1
    fi
fi

# Install dependencies
echo "📚 Installing dependencies..."
uv pip compile pyproject.toml -o requirements.txt
uv pip install -r requirements.txt

# Install development dependencies
echo "🛠️ Installing development dependencies..."
uv pip install -r pyproject.toml --extra dev

# Optional Playwright installation
if [ "$install_playwright" = true ]; then
    echo "🎭 Installing Playwright..."
    playwright install
fi

# Create .env file if it doesn't exist
new_env_file_created=false
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env-example .env
    new_env_file_created=true
fi

# Create agents_llm_config.json if it doesn't exist
new_agents_llm_config=false
if [ ! -f agents_llm_config.json ]; then
    echo "📝 Creating agents_llm_config.json file..."
    cp agents_llm_config-example.json agents_llm_config.json
    new_agents_llm_config=true
fi

echo "✅ Installation complete!"

# Configuration guidance
if [ "$new_env_file_created" = true ]; then
    echo "⚠️ Please edit the .env file with your API keys and configuration."
fi

if [ "$new_agents_llm_config" = true ]; then
    echo "⚠️ Please edit the agents_llm_config.json file with your LLM configuration."
fi

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "🚀 To start Agent-E, activate the virtual environment (source .venv/Scripts/activate) and run: python -m ae.main"
else
    echo "🚀 To start Agent-E, activate the virtual environment (source .venv/bin/activate) and run: python -u -m ae.main"
fi
