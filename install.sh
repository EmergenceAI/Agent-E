#!/bin/bash

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
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# Install dependencies
echo "📚 Installing dependencies..."
uv pip compile pyproject.toml -o requirements.txt
uv pip install -r requirements.txt

# Install development dependencies
echo "🛠️ Installing development dependencies..."
uv pip install -r pyproject.toml --extra dev

# Install Playwright (optional)
read -p "Would you like to install Playwright drivers? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🎭 Installing Playwright..."
    playwright install
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env-example .env
    echo "⚠️ Please edit .env file with your API keys and configuration"
fi

echo "✅ Installation complete!"
echo "🚀 To start Agent-E, activate the virtual environment and run: python -m ae.main"
echo "📝 Don't forget to configure your .env file with the necessary API keys and settings"
