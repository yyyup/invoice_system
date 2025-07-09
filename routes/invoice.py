from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from models.invoice import Invoice
from models.client import Client
from models.contractor import Contractor
from models.receipt import Receipt
from services.pdf_generator import generate_invoice_pdf
import json

invoice_bp = Blueprint('invoice', __name__)

def row_to_dict(row):
    """Convert SQLite Row to dictionary"""
    if row is None:
        return None
    return dict(row)

@invoice_bp.route('/')
def list_invoices():
    """List all invoices"""
    invoices = Invoice.get_all_invoices()
    return render_template('invoices/list.html', invoices=invoices)

@invoice_bp.route('/create', methods=['GET', 'POST'])
def create_invoice():
    """Create a new invoice with multiple line items"""
    if request.method == 'POST':
        # Get contractor info
        contractor = Contractor.get_contractor()
        if not contractor:
            flash('Please setup contractor information first!', 'error')
            return redirect(url_for('contractor.setup'))
        
        # Process line items from form
        line_items = []
        form_data = request.form.to_dict()
        
        # Extract line items from form data
        item_indices = set()
        for key in form_data.keys():
            if key.startswith('line_items[') and '][' in key:
                # Extract the index from line_items[INDEX][field]
                index = key.split('[')[1].split(']')[0]
                item_indices.add(index)
        
        # Build line items
        for index in sorted(item_indices):
            service_name = form_data.get(f'line_items[{index}][service_name]', '').strip()
            if service_name:  # Only add items with service names
                line_item = {
                    'service_name': service_name,
                    'service_description': form_data.get(f'line_items[{index}][service_description]', '').strip(),
                    'quantity': int(form_data.get(f'line_items[{index}][quantity]', 1)),
                    'rate': float(form_data.get(f'line_items[{index}][rate]', 0))
                }
                line_items.append(line_item)
        
        if not line_items:
            flash('Please add at least one line item!', 'error')
            return redirect(url_for('invoice.create_invoice'))
        
        data = {
            'client_id': request.form['client_id'],
            'contractor_id': contractor['id'],
            'invoice_date': request.form['invoice_date'],
            'line_items': line_items
        }
        
        try:
            invoice_number = Invoice.create_invoice(data)
            flash(f'Invoice {invoice_number} created successfully!', 'success')
            return redirect(url_for('invoice.view_invoice', invoice_number=invoice_number))
        except Exception as e:
            flash(f'Error creating invoice: {str(e)}', 'error')
    
    # Get clients for dropdown
    clients = Client.get_clients_for_dropdown()
    if not clients:
        flash('Please add at least one client before creating an invoice!', 'warning')
        return redirect(url_for('client.add_client'))
    
    return render_template('invoices/create.html', clients=clients)

@invoice_bp.route('/view/<invoice_number>')
def view_invoice(invoice_number):
    """View invoice details"""
    invoice = Invoice.get_invoice_by_number(invoice_number)
    if not invoice:
        flash('Invoice not found!', 'error')
        return redirect(url_for('invoice.list_invoices'))
    
    # Get receipt number if paid
    receipt_number = None
    if invoice['status'] == 'paid':
        receipt_number = Receipt.get_receipt_by_invoice_id(invoice['id'])
    
    return render_template('invoices/view.html', invoice=invoice, receipt_number=receipt_number)

@invoice_bp.route('/edit/<invoice_number>', methods=['GET', 'POST'])
def edit_invoice(invoice_number):
    """Edit an existing invoice"""
    invoice = Invoice.get_invoice_by_number(invoice_number)
    if not invoice:
        flash('Invoice not found!', 'error')
        return redirect(url_for('invoice.list_invoices'))
    
    # Check if invoice can be edited
    if not Invoice.can_edit_invoice(invoice_number):
        flash('Only pending invoices can be edited!', 'error')
        return redirect(url_for('invoice.view_invoice', invoice_number=invoice_number))
    
    if request.method == 'POST':
        # Process line items from form (same as create)
        line_items = []
        form_data = request.form.to_dict()
        
        # Extract line items from form data
        item_indices = set()
        for key in form_data.keys():
            if key.startswith('line_items[') and '][' in key:
                index = key.split('[')[1].split(']')[0]
                item_indices.add(index)
        
        # Build line items
        for index in sorted(item_indices):
            service_name = form_data.get(f'line_items[{index}][service_name]', '').strip()
            if service_name:
                line_item = {
                    'service_name': service_name,
                    'service_description': form_data.get(f'line_items[{index}][service_description]', '').strip(),
                    'quantity': int(form_data.get(f'line_items[{index}][quantity]', 1)),
                    'rate': float(form_data.get(f'line_items[{index}][rate]', 0))
                }
                line_items.append(line_item)
        
        if not line_items:
            flash('Please add at least one line item!', 'error')
            return redirect(url_for('invoice.edit_invoice', invoice_number=invoice_number))
        
        data = {
            'client_id': request.form['client_id'],
            'invoice_date': request.form['invoice_date'],
            'line_items': line_items
        }
        
        try:
            Invoice.update_invoice(invoice_number, data)
            flash(f'Invoice {invoice_number} updated successfully!', 'success')
            return redirect(url_for('invoice.view_invoice', invoice_number=invoice_number))
        except Exception as e:
            flash(f'Error updating invoice: {str(e)}', 'error')
    
    # Get clients for dropdown
    clients = Client.get_clients_for_dropdown()
    
    return render_template('invoices/edit.html', invoice=invoice, clients=clients)

@invoice_bp.route('/delete/<invoice_number>')
def delete_invoice(invoice_number):
    """Delete an invoice"""
    try:
        success, message = Invoice.delete_invoice(invoice_number)
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
    except Exception as e:
        flash(f'Error deleting invoice: {str(e)}', 'error')
    
    return redirect(url_for('invoice.list_invoices'))

@invoice_bp.route('/download/<invoice_number>')
def download_invoice(invoice_number):
    """Download invoice PDF"""
    invoice = Invoice.get_invoice_by_number(invoice_number)
    if not invoice:
        flash('Invoice not found!', 'error')
        return redirect(url_for('invoice.list_invoices'))
    
    try:
        filepath = generate_invoice_pdf(invoice)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'error')
        return redirect(url_for('invoice.view_invoice', invoice_number=invoice_number))

@invoice_bp.route('/mark-paid/<invoice_number>')
def mark_paid(invoice_number):
    """Mark invoice as paid and create receipt"""
    invoice = Invoice.get_invoice_by_number(invoice_number)
    if not invoice:
        flash('Invoice not found!', 'error')
        return redirect(url_for('invoice.list_invoices'))
    
    if invoice['status'] != 'pending':
        flash('Invoice is already paid!', 'warning')
        return redirect(url_for('invoice.view_invoice', invoice_number=invoice_number))
    
    try:
        # Mark invoice as paid
        Invoice.mark_invoice_paid(invoice_number)
        
        # Create receipt
        receipt_number = Receipt.create_receipt(invoice['id'], invoice['total'])
        
        flash(f'Invoice marked as paid! Receipt {receipt_number} generated.', 'success')
        return redirect(url_for('invoice.view_invoice', invoice_number=invoice_number))
    except Exception as e:
        flash(f'Error marking invoice as paid: {str(e)}', 'error')
        return redirect(url_for('invoice.view_invoice', invoice_number=invoice_number))