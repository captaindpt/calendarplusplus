#!/bin/bash

# Navigate to the project root directory
cd "$(dirname "$0")"

echo "Installing frontend dependencies..."
cd frontend
npm install

echo "Building React app..."
npm run build
echo "React build complete."

echo "Copying files to backend..."
cd ..
rm -rf backend/static
mkdir -p backend/static
cp -r frontend/build/* backend/static/
echo "Files copied successfully."

echo "Setting up Python virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate

echo "Installing backend dependencies..."
pip install -r requirements.txt

echo "Starting Flask server..."
python app.py
