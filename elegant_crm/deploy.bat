@echo off
echo 🚀 Starting ELEGANT CRM deployment...

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo ❌ Error: requirements.txt not found!
    pause
    exit /b 1
)

REM Check if app.py exists
if not exist "app.py" (
    echo ❌ Error: app.py not found!
    pause
    exit /b 1
)

REM Check if Procfile exists
if not exist "Procfile" (
    echo ❌ Error: Procfile not found!
    pause
    exit /b 1
)

echo ✅ All required files found!

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Test the application
echo 🧪 Testing application...
python -c "import app; print('✅ App imports successfully')"

echo 🎉 Deployment preparation complete!
echo 📋 Next steps:
echo 1. Push to GitHub: git add . ^&^& git commit -m "Deploy to Render" ^&^& git push
echo 2. Deploy on Render: https://dashboard.render.com
echo 3. Use build command: pip install -r requirements.txt
echo 4. Use start command: gunicorn app:app --bind 0.0.0.0:%%PORT%%
pause 