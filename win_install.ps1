param (
    [switch]$p  # Short flag to install Playwright
)

Write-Output "Installing Agent-E..."

# Function to check if a command exists
function Command-Exists {
    param (
        [string]$Command
    )
    return $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

# Check Python version
if (-not (Command-Exists 'python3')) {
    Write-Output "Python 3 is required but not installed. Please install Python 3.10 or higher."
    exit 1
}

# Ask the user about Playwright installation if the flag is not provided
$installPlaywright = $false
if (-not $p) {
    $response = Read-Host "Would you like to install Playwright drivers? (y/n)"
    if ($response -match '^[Yy]$') {
        $installPlaywright = $true
    }
} else {
    $installPlaywright = $true
}

# Install `uv` if not present
if (-not (Command-Exists 'uv')) {
    Write-Output "Installing uv package manager..."
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://astral.sh/uv/install.ps1'))

    # Add uv to current session
    $cargoBinPath = Join-Path $HOME ".cargo/bin"
    $env:PATH = "$env:PATH;$cargoBinPath"
}

# Create and activate virtual environment
Write-Output "Creating virtual environment..."
uv venv --python 3.11

# Activate virtual environment
if (Test-Path ".venv\Scripts\Activate.ps1") {
    . .venv\Scripts\Activate.ps1
} else {
    Write-Output "Virtual environment activation script not found. Ensure virtual environment is created successfully."
    exit 1
}

# Install dependencies
Write-Output "Installing dependencies..."
uv pip compile pyproject.toml -o requirements.txt
uv pip install -r requirements.txt

# Install development dependencies
Write-Output "Installing development dependencies..."
uv pip install -r pyproject.toml --extra dev

# Optional Playwright installation
if ($installPlaywright) {
    Write-Output "Installing Playwright..."
    playwright install
}

$new_env_file_created = $false
# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    $new_env_file_created = $true
    Write-Output "Creating .env file..."
    Copy-Item ".env-example" ".env"
    Write-Output "Please edit .env file with your API keys and configuration"
}

$new_agents_llm_config = $false
if (-not (Test-Path "agents_llm_config.json")) {
    $new_agents_llm_config = $true
    Write-Output "Creating agents_llm_config.json"
    Copy-Item "agents_llm_config-example.json" "agents_llm_config.json"
    Write-Output "Please edit agents_llm_config.json file with your LLM config"
}

Write-Output "Installation complete!"
Write-Output "To start Agent-E, activate the virtual environment (source .venv/Scripts/activate) and run: python -m ae.main"

if ($new_env_file_created) {
    Write-Output "Don't forget to configure your .env file with the necessary API keys and settings."
}

if ($new_agents_llm_config) {
    Write-Output "Don't forget to configure agents_llm_config.json"
}
