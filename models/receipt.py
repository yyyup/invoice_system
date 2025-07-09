from models.database import execute_query
from datetime import datetime
from config import Config

class Receipt:
    def __init__(self, invoice_id, paid_amount):
        self.invoice_id = invoice_id
        self.paid_amount = paid_amount
    
    @staticmethod
    def get_all_receipts():
        """Get all receipts with invoice and client information"""
        query = '''
            SELECT r.receipt_number, i.invoice_number, c.name, i.service_name, 
                   r.paid_amount, r.payment_date
            FROM receipts r
            JOIN invoices i ON r.invoice_id = i.id
            JOIN clients c ON i.client_id = c.id
            ORDER BY r.payment_date DESC
        '''
        return execute_query(query, fetch='all')
    
    @staticmethod
    def get_receipt_by_number(receipt_number):
        """Get receipt by receipt number with full details"""
        query = '''
            SELECT r.id, r.receipt_number, r.paid_amount, r.payment_date,
                   i.invoice_number, i.service_name, i.service_description,
                   c.name as client_name, c.address as client_address, c.email as client_email, c.phone as client_phone,
                   co.name as contractor_name, co.address as contractor_address, co.email as contractor_email, 
                   co.phone as contractor_phone, co.tax_id as contractor_tax_id, co.personal_tax_id as contractor_personal_tax_id
            FROM receipts r
            JOIN invoices i ON r.invoice_id = i.id
            JOIN clients c ON i.client_id = c.id
            JOIN contractor_info co ON i.contractor_id = co.id
            WHERE r.receipt_number = ?
        '''
        return execute_query(query, (receipt_number,), fetch='one')
    
    @staticmethod
    def create_receipt(invoice_id, paid_amount):
        """Create a new receipt"""
        # Generate receipt number
        count_query = "SELECT COUNT(*) as count FROM receipts"
        count_result = execute_query(count_query, fetch='one')
        receipt_number = f"{Config.RECEIPT_PREFIX}{(count_result['count'] + 1):04d}"
        
        query = '''
            INSERT INTO receipts (invoice_id, receipt_number, paid_amount, payment_date)
            VALUES (?, ?, ?, ?)
        '''
        params = (
            invoice_id, receipt_number, paid_amount, 
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        execute_query(query, params)
        return receipt_number
    
    @staticmethod
    def get_receipt_by_invoice_id(invoice_id):
        """Get receipt by invoice ID"""
        query = "SELECT receipt_number FROM receipts WHERE invoice_id = ?"
        result = execute_query(query, (invoice_id,), fetch='one')
        return result['receipt_number'] if result else None
    
    @staticmethod
    def get_receipt_stats():
        """Get receipt statistics"""
        stats = {}
        
        # Total receipts
        query = "SELECT COUNT(*) as count FROM receipts"
        result = execute_query(query, fetch='one')
        stats['total_receipts'] = result['count']
        
        # Total received amount
        query = "SELECT SUM(paid_amount) as total FROM receipts"
        result = execute_query(query, fetch='one')
        stats['total_received'] = result['total'] or 0
        
        # Recent receipts (last 30 days)
        query = '''
            SELECT COUNT(*) as count FROM receipts 
            WHERE payment_date >= datetime('now', '-30 days')
        '''
        result = execute_query(query, fetch='one')
        stats['recent_receipts'] = result['count']
        
        return stats
    
    @staticmethod
    def get_recent_receipts(limit=5):
        """Get recent receipts"""
        query = '''
            SELECT r.receipt_number, i.invoice_number, c.name, r.paid_amount, r.payment_date
            FROM receipts r
            JOIN invoices i ON r.invoice_id = i.id
            JOIN clients c ON i.client_id = c.id
            ORDER BY r.payment_date DESC
            LIMIT ?
        '''
        return execute_query(query, (limit,), fetch='all')