@echo off
echo Creating directory structure...
mkdir models routes services templates static data pdfs
mkdir templates\contractor templates\clients templates\invoices templates\receipts
mkdir static\css static\js
mkdir pdfs\invoices pdfs\receipts

echo Creating empty __init__.py files...
type nul > models\__init__.py
type nul > routes\__init__.py
type nul > services\__init__.py

echo Directory structure created successfully!
echo.
echo Next steps:
echo 1. Save all the Python files in their respective directories
echo 2. Run: pip install -r requirements.txt
echo 3. Run: python app.py
echo.
pause