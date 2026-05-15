#!/bin/bash
# Quick start script for backend

echo "🚀 Starting AI Interview Coach Backend..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Run setup validation
echo ""
echo "🔍 Validating setup..."
python setup.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Starting server..."
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
else
    echo ""
    echo "❌ Setup validation failed. Please fix the issues above."
    exit 1
fi
