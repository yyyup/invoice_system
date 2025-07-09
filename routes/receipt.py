from flask import Blueprint, render_template, redirect, url_for, flash, send_file
from models.receipt import Receipt
from services.pdf_generator import generate_receipt_pdf

receipt_bp = Blueprint('receipt', __name__)

def row_to_dict(row):
    """Convert SQLite Row to dictionary"""
    if row is None:
        return None
    return dict(row)

@receipt_bp.route('/')
def list_receipts():
    """List all receipts"""
    receipts = Receipt.get_all_receipts()
    return render_template('receipts/list.html', receipts=receipts)

@receipt_bp.route('/view/<receipt_number>')
def view_receipt(receipt_number):
    """View receipt details"""
    receipt = Receipt.get_receipt_by_number(receipt_number)
    if not receipt:
        flash('Receipt not found!', 'error')
        return redirect(url_for('receipt.list_receipts'))
    
    # Convert to dict for template
    receipt_dict = row_to_dict(receipt)
    
    return render_template('receipts/view.html', receipt=receipt_dict)

@receipt_bp.route('/download/<receipt_number>')
def download_receipt(receipt_number):
    """Download receipt PDF"""
    receipt = Receipt.get_receipt_by_number(receipt_number)
    if not receipt:
        flash('Receipt not found!', 'error')
        return redirect(url_for('receipt.list_receipts'))
    
    # Convert to dict for PDF generator
    receipt_dict = row_to_dict(receipt)
    
    try:
        filepath = generate_receipt_pdf(receipt_dict)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'error')
        return redirect(url_for('receipt.view_receipt', receipt_number=receipt_number))