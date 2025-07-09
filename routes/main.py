from flask import Blueprint, render_template
from models.invoice import Invoice
from models.receipt import Receipt
from models.client import Client
from models.contractor import Contractor

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Dashboard/Home page"""
    # Get statistics
    invoice_stats = Invoice.get_invoice_stats()
    receipt_stats = Receipt.get_receipt_stats()
    
    # Get recent activities
    recent_invoices = Invoice.get_all_invoices()[:5]  # Last 5 invoices
    recent_receipts = Receipt.get_recent_receipts(5)
    
    # Get client count
    clients = Client.get_all_clients()
    client_count = len(clients)
    
    # Check if contractor is set up
    contractor = Contractor.get_contractor()
    contractor_setup = contractor is not None
    
    return render_template('index.html',
                         invoice_stats=invoice_stats,
                         receipt_stats=receipt_stats,
                         recent_invoices=recent_invoices,
                         recent_receipts=recent_receipts,
                         client_count=client_count,
                         contractor_setup=contractor_setup)

@main_bp.route('/dashboard')
def dashboard():
    """Alternative dashboard route"""
    return index()