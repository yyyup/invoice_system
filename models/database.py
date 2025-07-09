import sqlite3
import os
from flask import current_app

def get_db_connection():
    """Get database connection"""
    from config import Config
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
    return conn

def init_db():
    """Initialize database with all tables"""
    from config import Config
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create contractor_info table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contractor_info (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT,
            email TEXT,
            phone TEXT,
            tax_id TEXT,
            personal_tax_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create clients table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT,
            email TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create invoices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY,
            invoice_number TEXT UNIQUE NOT NULL,
            client_id INTEGER,
            contractor_id INTEGER,
            service_name TEXT NOT NULL,
            service_description TEXT,
            quantity INTEGER DEFAULT 1,
            rate REAL NOT NULL,
            total REAL NOT NULL,
            date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (client_id) REFERENCES clients (id),
            FOREIGN KEY (contractor_id) REFERENCES contractor_info (id)
        )
    ''')
    
    # Create receipts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY,
            invoice_id INTEGER,
            receipt_number TEXT UNIQUE NOT NULL,
            paid_amount REAL NOT NULL,
            payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (invoice_id) REFERENCES invoices (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def execute_query(query, params=None, fetch=None):
    """Execute a database query with proper error handling"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch == 'one':
            result = cursor.fetchone()
        elif fetch == 'all':
            result = cursor.fetchall()
        else:
            result = cursor.lastrowid
        
        conn.commit()
        return result
    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        conn.close()