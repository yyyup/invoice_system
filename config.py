import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this-in-production'
    
    # Database
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'invoices.db')
    
    # File paths
    PDF_FOLDER = os.path.join(os.path.dirname(__file__), 'pdfs')
    INVOICE_PDF_FOLDER = os.path.join(PDF_FOLDER, 'invoices')
    RECEIPT_PDF_FOLDER = os.path.join(PDF_FOLDER, 'receipts')
    
    # Invoice settings
    INVOICE_PREFIX = 'INV-'
    RECEIPT_PREFIX = 'REC-'
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    
    # PDF settings
    PDF_PAGE_SIZE = 'letter'
    
    @staticmethod
    def init_app(app):
        # Create necessary directories
        os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
        os.makedirs(Config.PDF_FOLDER, exist_ok=True)
        os.makedirs(Config.INVOICE_PDF_FOLDER, exist_ok=True)
        os.makedirs(Config.RECEIPT_PDF_FOLDER, exist_ok=True)