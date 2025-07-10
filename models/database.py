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
            invoice_date DATE,
            leave_date_blank INTEGER DEFAULT 0,
            total REAL NOT NULL,
            date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (client_id) REFERENCES clients (id),
            FOREIGN KEY (contractor_id) REFERENCES contractor_info (id)
        )
    ''')
    
    # Create invoice_items table for multiple line items per invoice
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY,
            invoice_id INTEGER NOT NULL,
            service_name TEXT NOT NULL,
            service_description TEXT,
            quantity INTEGER DEFAULT 1,
            rate REAL NOT NULL,
            amount REAL NOT NULL,
            sort_order INTEGER DEFAULT 0,
            FOREIGN KEY (invoice_id) REFERENCES invoices (id) ON DELETE CASCADE
        )
    ''')
    
    # Create receipts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY,
            invoice_id INTEGER,
            receipt_number TEXT UNIQUE NOT NULL,
            paid_amount REAL NOT NULL,
            leave_date_blank INTEGER DEFAULT 0,
            payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (invoice_id) REFERENCES invoices (id)
        )
    ''')
    
    # If there are any legacy invoices without line items, migrate them
    # Check if we have invoices but no invoice items (legacy data)
    cursor.execute('SELECT COUNT(*) as invoice_count FROM invoices')
    invoice_count = cursor.fetchone()['invoice_count']
    
    cursor.execute('SELECT COUNT(*) as item_count FROM invoice_items')
    item_count = cursor.fetchone()['item_count']
    
    # If we have invoices but no items, migrate legacy data
    if invoice_count > 0 and item_count == 0:
        print("Migrating legacy invoice data to new line items structure...")
        
        # Get all invoices that have the old structure
        cursor.execute('''
            SELECT id, service_name, service_description, quantity, rate, total
            FROM invoices 
            WHERE service_name IS NOT NULL
        ''')
        legacy_invoices = cursor.fetchall()
        
        for invoice in legacy_invoices:
            # Create a line item for each legacy invoice
            cursor.execute('''
                INSERT INTO invoice_items (invoice_id, service_name, service_description, quantity, rate, amount, sort_order)
                VALUES (?, ?, ?, ?, ?, ?, 0)
            ''', (
                invoice['id'],
                invoice['service_name'],
                invoice['service_description'],
                invoice['quantity'] or 1,
                invoice['rate'],
                invoice['total']
            ))
        
        # Remove the old columns from invoices table (optional - for cleanup)
        # Note: SQLite doesn't support DROP COLUMN directly, so we'll leave them for now
        print(f"Migrated {len(legacy_invoices)} legacy invoices to new structure")
    
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