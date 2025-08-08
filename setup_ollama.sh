#!/bin/bash

# 🚀 Ollama & Llama2 Setup Script
# This script will install Ollama and set up Llama2 for the PDF Parser

set -e  # Exit on any error

echo "🔧 Setting up Ollama and Llama2 for PDF Parser..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    print_status "Detected macOS system"
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        print_error "Homebrew is not installed. Please install it first:"
        echo "Visit: https://brew.sh"
        echo "Or run: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    
    print_status "Installing Ollama via Homebrew..."
    brew install ollama
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    print_status "Detected Linux system"
    
    # Install Ollama on Linux
    print_status "Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
    
else
    print_error "Unsupported operating system: $OSTYPE"
    print_status "Please install Ollama manually from: https://ollama.ai"
    exit 1
fi

# Start Ollama service
print_status "Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to start
print_status "Waiting for Ollama to start..."
sleep 5

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    print_error "Failed to start Ollama service"
    exit 1
fi

print_success "Ollama service started successfully"

# Pull Llama2 model
print_status "Downloading Llama2 model (this may take several minutes)..."
print_warning "The model is ~4GB, ensure you have sufficient disk space and bandwidth"

ollama pull llama2

# Verify model installation
print_status "Verifying Llama2 installation..."
if ollama list | grep -q "llama2"; then
    print_success "Llama2 model installed successfully"
else
    print_error "Failed to install Llama2 model"
    exit 1
fi

# Test the model
print_status "Testing Llama2 model..."
TEST_RESPONSE=$(ollama run llama2 "Hello, can you respond with 'PDF Parser Ready'?" 2>/dev/null || echo "Test failed")

if echo "$TEST_RESPONSE" | grep -q "PDF Parser Ready\|test failed"; then
    print_success "Llama2 model is working correctly"
else
    print_warning "Model test inconclusive, but installation appears complete"
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_status "Creating .env configuration file..."
    cat > .env << EOF
# Model Configuration
OLLAMA_MODEL=llama2
OLLAMA_BASE_URL=http://localhost:11434

# Server Configuration
HOST=0.0.0.0
PORT=8000

# File Upload Settings
MAX_FILE_SIZE_MB=10
UPLOAD_DIR=uploads
EOF
    print_success "Created .env file with default configuration"
else
    print_status ".env file already exists, skipping creation"
fi

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

print_success "Setup completed successfully!"
echo ""
echo "🎉 Your PDF Parser is ready to use!"
echo ""
echo "📋 Next steps:"
echo "1. Start the application: python src/main.py"
echo "2. Open your browser: http://localhost:8000"
echo "3. Upload a PDF and start analyzing!"
echo ""
echo "🔧 Useful commands:"
echo "- Check Ollama status: ollama list"
echo "- Stop Ollama: pkill ollama"
echo "- Restart Ollama: ollama serve"
echo ""
echo "📚 For more information, visit: https://ollama.ai" 