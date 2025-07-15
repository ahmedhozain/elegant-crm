#!/bin/bash

# ELEGANT CRM Deployment Script
echo "🚀 Starting ELEGANT CRM deployment..."

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found!"
    exit 1
fi

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found!"
    exit 1
fi

# Check if Procfile exists
if [ ! -f "Procfile" ]; then
    echo "❌ Error: Procfile not found!"
    exit 1
fi

echo "✅ All required files found!"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Test the application
echo "🧪 Testing application..."
python -c "import app; print('✅ App imports successfully')"

echo "🎉 Deployment preparation complete!"
echo "📋 Next steps:"
echo "1. Push to GitHub: git add . && git commit -m 'Deploy to Render' && git push"
echo "2. Deploy on Render: https://dashboard.render.com"
echo "3. Use build command: pip install -r requirements.txt"
echo "4. Use start command: gunicorn app:app --bind 0.0.0.0:\$PORT" 