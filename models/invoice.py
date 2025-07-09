from models.database import execute_query
from datetime import datetime
from config import Config

class Invoice:
    def __init__(self, client_id, contractor_id, invoice_date, line_items):
        self.client_id = client_id
        self.contractor_id = contractor_id
        self.invoice_date = invoice_date
        self.line_items = line_items
        self.total = sum(item['quantity'] * item['rate'] for item in line_items)
    
    @staticmethod
    def get_all_invoices():
        """Get all invoices with client information"""
        query = '''
            SELECT i.invoice_number, c.name, 
                   (SELECT GROUP_CONCAT(ii.service_name, ', ') FROM invoice_items ii WHERE ii.invoice_id = i.id LIMIT 3) as services,
                   i.total, i.invoice_date, i.status, r.receipt_number
            FROM invoices i
            JOIN clients c ON i.client_id = c.id
            LEFT JOIN receipts r ON i.id = r.invoice_id
            ORDER BY i.date_created DESC
        '''
        return execute_query(query, fetch='all')
    
    @staticmethod
    def get_invoice_by_number(invoice_number):
        """Get invoice by invoice number with full details including line items"""
        # Get invoice header
        query = '''
            SELECT i.id, i.invoice_number, i.client_id, i.contractor_id, i.invoice_date,
                   i.total, i.date_created, i.status,
                   c.name as client_name, c.address as client_address, c.email as client_email, c.phone as client_phone, 
                   co.name as contractor_name, co.address as contractor_address, co.email as contractor_email, 
                   co.phone as contractor_phone, co.tax_id as contractor_tax_id, co.personal_tax_id as contractor_personal_tax_id
            FROM invoices i
            JOIN clients c ON i.client_id = c.id
            JOIN contractor_info co ON i.contractor_id = co.id
            WHERE i.invoice_number = ?
        '''
        invoice = execute_query(query, (invoice_number,), fetch='one')
        
        if invoice:
            # Get line items
            items_query = '''
                SELECT service_name, service_description, quantity, rate, amount
                FROM invoice_items
                WHERE invoice_id = ?
                ORDER BY sort_order, id
            '''
            items = execute_query(items_query, (invoice['id'],), fetch='all')
            
            # Convert to dict and add items
            invoice_dict = dict(invoice)
            invoice_dict['line_items'] = [dict(item) for item in items] if items else []
            return invoice_dict
        
        return None
    
    @staticmethod
    def create_invoice(data):
        """Create a new invoice with multiple line items"""
        # Generate invoice number
        count_query = "SELECT COUNT(*) as count FROM invoices"
        count_result = execute_query(count_query, fetch='one')
        invoice_number = f"{Config.INVOICE_PREFIX}{(count_result['count'] + 1):04d}"
        
        # Calculate total from line items
        total = sum(float(item['quantity']) * float(item['rate']) for item in data['line_items'])
        
        # Insert invoice header
        invoice_query = '''
            INSERT INTO invoices (invoice_number, client_id, contractor_id, invoice_date, total, date_created)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        invoice_params = (
            invoice_number, data['client_id'], data['contractor_id'], 
            data['invoice_date'], total, datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        invoice_id = execute_query(invoice_query, invoice_params)
        
        # Insert line items
        for index, item in enumerate(data['line_items']):
            item_query = '''
                INSERT INTO invoice_items (invoice_id, service_name, service_description, quantity, rate, amount, sort_order)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
            amount = float(item['quantity']) * float(item['rate'])
            item_params = (
                invoice_id, item['service_name'], item.get('service_description', ''),
                int(item['quantity']), float(item['rate']), amount, index
            )
            execute_query(item_query, item_params)
        
        return invoice_number
    
    @staticmethod
    def update_invoice(invoice_number, data):
        """Update an existing invoice (only if pending)"""
        # Get invoice ID
        invoice = Invoice.get_invoice_by_number(invoice_number)
        if not invoice or invoice['status'] != 'pending':
            return False
        
        invoice_id = invoice['id']
        
        # Calculate new total
        total = sum(float(item['quantity']) * float(item['rate']) for item in data['line_items'])
        
        # Update invoice header
        update_query = '''
            UPDATE invoices 
            SET client_id=?, invoice_date=?, total=?
            WHERE id=? AND status='pending'
        '''
        execute_query(update_query, (data['client_id'], data['invoice_date'], total, invoice_id))
        
        # Delete existing line items
        execute_query('DELETE FROM invoice_items WHERE invoice_id = ?', (invoice_id,))
        
        # Insert new line items
        for index, item in enumerate(data['line_items']):
            item_query = '''
                INSERT INTO invoice_items (invoice_id, service_name, service_description, quantity, rate, amount, sort_order)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
            amount = float(item['quantity']) * float(item['rate'])
            item_params = (
                invoice_id, item['service_name'], item.get('service_description', ''),
                int(item['quantity']), float(item['rate']), amount, index
            )
            execute_query(item_query, item_params)
        
        return True
    
    @staticmethod
    def mark_invoice_paid(invoice_number):
        """Mark an invoice as paid"""
        query = "UPDATE invoices SET status = 'paid' WHERE invoice_number = ?"
        return execute_query(query, (invoice_number,))
    
    @staticmethod
    def get_invoice_stats():
        """Get invoice statistics"""
        stats = {}
        
        # Total invoices
        query = "SELECT COUNT(*) as count FROM invoices"
        result = execute_query(query, fetch='one')
        stats['total_invoices'] = result['count']
        
        # Pending invoices
        query = "SELECT COUNT(*) as count FROM invoices WHERE status = 'pending'"
        result = execute_query(query, fetch='one')
        stats['pending_invoices'] = result['count']
        
        # Paid invoices
        query = "SELECT COUNT(*) as count FROM invoices WHERE status = 'paid'"
        result = execute_query(query, fetch='one')
        stats['paid_invoices'] = result['count']
        
        # Total amount
        query = "SELECT SUM(total) as total FROM invoices"
        result = execute_query(query, fetch='one')
        stats['total_amount'] = result['total'] or 0
        
        # Pending amount
        query = "SELECT SUM(total) as total FROM invoices WHERE status = 'pending'"
        result = execute_query(query, fetch='one')
        stats['pending_amount'] = result['total'] or 0
        
        # Paid amount
        query = "SELECT SUM(total) as total FROM invoices WHERE status = 'paid'"
        result = execute_query(query, fetch='one')
        stats['paid_amount'] = result['total'] or 0
        
        return stats
    
    @staticmethod
    def can_edit_invoice(invoice_number):
        """Check if an invoice can be edited (only pending invoices)"""
        query = "SELECT status FROM invoices WHERE invoice_number = ?"
        result = execute_query(query, (invoice_number,), fetch='one')
        return result and result['status'] == 'pending'
    
    @staticmethod
    def delete_invoice(invoice_number):
        """Delete an invoice (only if pending and no receipt exists)"""
        # Check if invoice is pending
        if not Invoice.can_edit_invoice(invoice_number):
            return False, "Only pending invoices can be deleted"
        
        # Check if receipt exists
        query = "SELECT COUNT(*) as count FROM receipts r JOIN invoices i ON r.invoice_id = i.id WHERE i.invoice_number = ?"
        result = execute_query(query, (invoice_number,), fetch='one')
        if result['count'] > 0:
            return False, "Cannot delete invoice with existing receipt"
        
        # Get invoice ID for deleting line items
        invoice = Invoice.get_invoice_by_number(invoice_number)
        if invoice:
            # Delete line items first (due to foreign key)
            execute_query('DELETE FROM invoice_items WHERE invoice_id = ?', (invoice['id'],))
            # Delete invoice
            execute_query('DELETE FROM invoices WHERE invoice_number = ?', (invoice_number,))
        
        return True, "Invoice deleted successfully"