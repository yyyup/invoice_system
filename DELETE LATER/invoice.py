import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for, send_file, flash
from datetime import datetime
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
import tempfile

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Database setup
def init_db():
    conn = sqlite3.connect('invoices.db')
    cursor = conn.cursor()
    
    # Create tables with all the new columns
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

# PDF Generation Functions
def generate_invoice_pdf(invoice_data):
    filename = f"invoice_{invoice_data['invoice_number']}.pdf"
    filepath = os.path.join('pdfs', filename)
    
    # Create pdfs directory if it doesn't exist
    if not os.path.exists('pdfs'):
        os.makedirs('pdfs')
    
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Header
    title = Paragraph(f"<b>INVOICE #{invoice_data['invoice_number']}</b>", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 20))
    
    # From and To sections
    contractor_info = f"<b>From:</b><br/>{invoice_data['contractor_name']}<br/>{invoice_data['contractor_address']}<br/>{invoice_data['contractor_email']}<br/>{invoice_data['contractor_phone']}"
    if invoice_data.get('contractor_tax_id'):
        contractor_info += f"<br/><b>Tax ID:</b> {invoice_data['contractor_tax_id']}"
    if invoice_data.get('contractor_personal_tax_id'):
        contractor_info += f"<br/><b>Personal Tax ID:</b> {invoice_data['contractor_personal_tax_id']}"
    
    from_section = Paragraph(contractor_info, styles['Normal'])
    story.append(from_section)
    story.append(Spacer(1, 20))
    
    to_section = Paragraph(f"<b>To:</b><br/>{invoice_data['client_name']}<br/>{invoice_data['client_address']}<br/>{invoice_data['client_email']}<br/>{invoice_data['client_phone']}", styles['Normal'])
    story.append(to_section)
    story.append(Spacer(1, 20))
    
    # Date
    date_para = Paragraph(f"<b>Date:</b> {invoice_data['date_created'].split(' ')[0]}", styles['Normal'])
    story.append(date_para)
    story.append(Spacer(1, 20))
    
    # Service details table
    service_cell = invoice_data['service_name']
    if invoice_data.get('service_description'):
        service_cell += f"\n{invoice_data['service_description']}"
    
    data = [
        ['Service', 'Quantity', 'Rate', 'Total'],
        [service_cell, str(invoice_data['quantity']), f"${invoice_data['rate']:.2f}", f"${invoice_data['total']:.2f} only"]
    ]
    
    table = Table(data, colWidths=[3*inch, 1*inch, 1*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Total
    total_para = Paragraph(f"<b>Total Due: ${invoice_data['total']:.2f} only</b>", styles['Heading2'])
    story.append(total_para)
    
    doc.build(story)
    return filepath

def generate_receipt_pdf(receipt_data):
    filename = f"receipt_{receipt_data['receipt_number']}.pdf"
    filepath = os.path.join('pdfs', filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Header
    title = Paragraph(f"<b>RECEIPT #{receipt_data['receipt_number']}</b>", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 20))
    
    # From and To sections
    contractor_info = f"<b>From:</b><br/>{receipt_data['contractor_name']}<br/>{receipt_data['contractor_address']}<br/>{receipt_data['contractor_email']}<br/>{receipt_data['contractor_phone']}"
    if receipt_data.get('contractor_tax_id'):
        contractor_info += f"<br/><b>Tax ID:</b> {receipt_data['contractor_tax_id']}"
    if receipt_data.get('contractor_personal_tax_id'):
        contractor_info += f"<br/><b>Personal Tax ID:</b> {receipt_data['contractor_personal_tax_id']}"
    
    from_section = Paragraph(contractor_info, styles['Normal'])
    story.append(from_section)
    story.append(Spacer(1, 20))
    
    to_section = Paragraph(f"<b>To:</b><br/>{receipt_data['client_name']}<br/>{receipt_data['client_address']}<br/>{receipt_data['client_email']}<br/>{receipt_data['client_phone']}", styles['Normal'])
    story.append(to_section)
    story.append(Spacer(1, 20))
    
    # Payment details
    payment_para = Paragraph(f"<b>Payment Date:</b> {receipt_data['payment_date'].split(' ')[0]}", styles['Normal'])
    story.append(payment_para)
    story.append(Spacer(1, 10))
    
    invoice_para = Paragraph(f"<b>Invoice Number:</b> {receipt_data['invoice_number']}", styles['Normal'])
    story.append(invoice_para)
    story.append(Spacer(1, 10))
    
    service_para = Paragraph(f"<b>Service:</b> {receipt_data['service_name']}", styles['Normal'])
    story.append(service_para)
    story.append(Spacer(1, 10))
    
    if receipt_data.get('service_description'):
        description_para = Paragraph(f"<b>Description:</b> {receipt_data['service_description']}", styles['Normal'])
        story.append(description_para)
        story.append(Spacer(1, 10))
    story.append(Spacer(1, 10))
    
    # Amount received
    amount_para = Paragraph(f"<b>Amount Received: ${receipt_data['paid_amount']:.2f} only</b>", styles['Heading2'])
    story.append(amount_para)
    story.append(Spacer(1, 20))
    
    # Confirmation statement
    confirmation_para = Paragraph(f"I, {receipt_data['contractor_name']}, confirm that I have received the payment of ${receipt_data['paid_amount']:.2f} only in full from {receipt_data['client_name']}.", styles['Normal'])
    story.append(confirmation_para)
    story.append(Spacer(1, 20))
    
    # Thank you message
    thank_you = Paragraph("Thank you for your payment!", styles['Normal'])
    story.append(thank_you)
    
    doc.build(story)
    return filepath

# Routes
@app.route('/')
def index():
    return render_template_string('''
    <html>
    <head>
        <title>Invoice System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 50px; }
            .btn { padding: 10px 20px; margin: 10px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; }
            .btn:hover { background-color: #0056b3; }
        </style>
    </head>
    <body>
        <h1>Invoice and Receipt System</h1>
        <div>
            <a href="/setup" class="btn">Setup Contractor Info</a>
            <a href="/clients" class="btn">Manage Clients</a>
            <a href="/invoices" class="btn">View Invoices</a>
            <a href="/receipts" class="btn">View Receipts</a>
            <a href="/create-invoice" class="btn">Create Invoice</a>
        </div>
    </body>
    </html>
    ''')

@app.route('/setup', methods=['GET', 'POST'])
def setup_contractor():
    if request.method == 'POST':
        conn = sqlite3.connect('invoices.db')
        cursor = conn.cursor()
        
        # Check if contractor info already exists
        cursor.execute('SELECT id FROM contractor_info')
        existing = cursor.fetchone()
        
        if existing:
            # Update existing info
            cursor.execute('''
                UPDATE contractor_info 
                SET name=?, address=?, email=?, phone=?, tax_id=?, personal_tax_id=?
                WHERE id=?
            ''', (request.form['name'], request.form['address'], 
                  request.form['email'], request.form['phone'], 
                  request.form['tax_id'], request.form['personal_tax_id'], existing[0]))
            flash('Contractor info updated successfully!')
        else:
            # Insert new info
            cursor.execute('''
                INSERT INTO contractor_info (name, address, email, phone, tax_id, personal_tax_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (request.form['name'], request.form['address'], 
                  request.form['email'], request.form['phone'],
                  request.form['tax_id'], request.form['personal_tax_id']))
            flash('Contractor info saved successfully!')
        
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    # Get existing contractor info
    conn = sqlite3.connect('invoices.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contractor_info LIMIT 1')
    contractor = cursor.fetchone()
    conn.close()
    
    return render_template_string('''
    <html>
    <head>
        <title>Setup Contractor Info</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 50px; }
            .form-group { margin: 10px 0; }
            input, textarea { width: 300px; padding: 8px; }
            .btn { padding: 10px 20px; background-color: #007bff; color: white; border: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>Setup Contractor Information</h1>
        <form method="POST">
            <div class="form-group">
                <label>Name:</label><br>
                <input type="text" name="name" value="{{ contractor[1] if contractor else '' }}" required>
            </div>
            <div class="form-group">
                <label>Address:</label><br>
                <textarea name="address">{{ contractor[2] if contractor else '' }}</textarea>
            </div>
            <div class="form-group">
                <label>Email:</label><br>
                <input type="email" name="email" value="{{ contractor[3] if contractor else '' }}">
            </div>
            <div class="form-group">
                <label>Phone:</label><br>
                <input type="text" name="phone" value="{{ contractor[4] if contractor else '' }}">
            </div>
            <div class="form-group">
                <label>Tax ID:</label><br>
                <input type="text" name="tax_id" value="{{ contractor[5] if contractor else '' }}">
            </div>
            <div class="form-group">
                <label>Personal Tax ID:</label><br>
                <input type="text" name="personal_tax_id" value="{{ contractor[6] if contractor else '' }}">
            </div>
            <button type="submit" class="btn">Save</button>
        </form>
        <a href="/">Back to Home</a>
    </body>
    </html>
    ''', contractor=contractor)

@app.route('/clients')
def manage_clients():
    conn = sqlite3.connect('invoices.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients ORDER BY name')
    clients = cursor.fetchall()
    conn.close()
    
    return render_template_string('''
    <html>
    <head>
        <title>Manage Clients</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 50px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .btn { padding: 5px 10px; margin: 2px; background-color: #007bff; color: white; text-decoration: none; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>Manage Clients</h1>
        <a href="/add-client" class="btn">Add New Client</a>
        <table>
            <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Actions</th>
            </tr>
            {% for client in clients %}
            <tr>
                <td>{{ client[1] }}</td>
                <td>{{ client[3] }}</td>
                <td>{{ client[4] }}</td>
                <td>
                    <a href="/edit-client/{{ client[0] }}" class="btn">Edit</a>
                </td>
            </tr>
            {% endfor %}
        </table>
        <a href="/">Back to Home</a>
    </body>
    </html>
    ''', clients=clients)

@app.route('/add-client', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        conn = sqlite3.connect('invoices.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO clients (name, address, email, phone)
            VALUES (?, ?, ?, ?)
        ''', (request.form['name'], request.form['address'], 
              request.form['email'], request.form['phone']))
        conn.commit()
        conn.close()
        flash('Client added successfully!')
        return redirect(url_for('manage_clients'))
    
    return render_template_string('''
    <html>
    <head>
        <title>Add Client</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 50px; }
            .form-group { margin: 10px 0; }
            input, textarea { width: 300px; padding: 8px; }
            .btn { padding: 10px 20px; background-color: #007bff; color: white; border: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>Add New Client</h1>
        <form method="POST">
            <div class="form-group">
                <label>Name:</label><br>
                <input type="text" name="name" required>
            </div>
            <div class="form-group">
                <label>Address:</label><br>
                <textarea name="address"></textarea>
            </div>
            <div class="form-group">
                <label>Email:</label><br>
                <input type="email" name="email">
            </div>
            <div class="form-group">
                <label>Phone:</label><br>
                <input type="text" name="phone">
            </div>
            <button type="submit" class="btn">Add Client</button>
        </form>
        <a href="/clients">Back to Clients</a>
    </body>
    </html>
    ''')

@app.route('/create-invoice', methods=['GET', 'POST'])
def create_invoice():
    if request.method == 'POST':
        conn = sqlite3.connect('invoices.db')
        cursor = conn.cursor()
        
        # Generate invoice number
        cursor.execute('SELECT COUNT(*) FROM invoices')
        count = cursor.fetchone()[0]
        invoice_number = f"INV-{(count + 1):04d}"
        
        # Get contractor info
        cursor.execute('SELECT id FROM contractor_info LIMIT 1')
        contractor = cursor.fetchone()
        if not contractor:
            flash('Please setup contractor information first!')
            return redirect(url_for('setup_contractor'))
        
        # Calculate total
        rate = float(request.form['rate'])
        quantity = int(request.form['quantity'])
        total = rate * quantity
        
        # Insert invoice
        cursor.execute('''
            INSERT INTO invoices (invoice_number, client_id, contractor_id, service_name, 
                               service_description, quantity, rate, total, date_created)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (invoice_number, request.form['client_id'], contractor[0], 
              request.form['service_name'], request.form['service_description'],
              quantity, rate, total, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        conn.commit()
        conn.close()
        
        flash(f'Invoice {invoice_number} created successfully!')
        return redirect(url_for('view_invoice', invoice_number=invoice_number))
    
    # Get clients for dropdown
    conn = sqlite3.connect('invoices.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM clients ORDER BY name')
    clients = cursor.fetchall()
    conn.close()
    
    return render_template_string('''
    <html>
    <head>
        <title>Create Invoice</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 50px; }
            .form-group { margin: 10px 0; }
            input, select, textarea { width: 300px; padding: 8px; }
            .btn { padding: 10px 20px; background-color: #007bff; color: white; border: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>Create Invoice</h1>
        <form method="POST">
            <div class="form-group">
                <label>Client:</label><br>
                <select name="client_id" required>
                    <option value="">Select Client</option>
                    {% for client in clients %}
                    <option value="{{ client[0] }}">{{ client[1] }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group">
                <label>Service/Product Name:</label><br>
                <input type="text" name="service_name" required>
            </div>
            <div class="form-group">
                <label>Service Description:</label><br>
                <textarea name="service_description" rows="3" placeholder="Detailed description of the service/product"></textarea>
            </div>
            <div class="form-group">
                <label>Quantity:</label><br>
                <input type="number" name="quantity" value="1" min="1" required>
            </div>
            <div class="form-group">
                <label>Rate:</label><br>
                <input type="number" name="rate" step="0.01" required>
            </div>
            <button type="submit" class="btn">Create Invoice</button>
        </form>
        <a href="/">Back to Home</a>
    </body>
    </html>
    ''', clients=clients)

@app.route('/invoices')
def list_invoices():
    conn = sqlite3.connect('invoices.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT i.invoice_number, c.name, i.service_name, i.total, i.date_created, i.status, r.receipt_number
        FROM invoices i
        JOIN clients c ON i.client_id = c.id
        LEFT JOIN receipts r ON i.id = r.invoice_id
        ORDER BY i.date_created DESC
    ''')
    invoices = cursor.fetchall()
    conn.close()
    
    return render_template_string('''
    <html>
    <head>
        <title>All Invoices</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 50px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .btn { padding: 5px 10px; margin: 2px; background-color: #007bff; color: white; text-decoration: none; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>All Invoices</h1>
        <table>
            <tr>
                <th>Invoice #</th>
                <th>Client</th>
                <th>Service</th>
                <th>Total</th>
                <th>Date</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
            {% for invoice in invoices %}
            <tr>
                <td>{{ invoice[0] }}</td>
                <td>{{ invoice[1] }}</td>
                <td>{{ invoice[2] }}</td>
                <td>${{ "%.2f"|format(invoice[3]) }}</td>
                <td>{{ invoice[4].split(' ')[0] }}</td>
                <td>{{ invoice[5] }}</td>
                <td>
                    <a href="/invoice/{{ invoice[0] }}" class="btn">View</a>
                    <a href="/download-invoice/{{ invoice[0] }}" class="btn">Download</a>
                    {% if invoice[5] == 'pending' %}
                    <a href="/edit-invoice/{{ invoice[0] }}" class="btn">Edit</a>
                    <a href="/mark-paid/{{ invoice[0] }}" class="btn">Mark as Paid</a>
                    {% elif invoice[6] %}
                    <a href="/download-receipt/{{ invoice[6] }}" class="btn">Download Receipt</a>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </table>
        <a href="/">Back to Home</a>
    </body>
    </html>
    ''', invoices=invoices)

@app.route('/invoice/<invoice_number>')
def view_invoice(invoice_number):
    conn = sqlite3.connect('invoices.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT i.id, i.invoice_number, i.client_id, i.contractor_id, i.service_name, 
               i.service_description, i.quantity, i.rate, i.total, i.date_created, i.status,
               c.name, c.address, c.email, c.phone, 
               co.name, co.address, co.email, co.phone, co.tax_id, co.personal_tax_id
        FROM invoices i
        JOIN clients c ON i.client_id = c.id
        JOIN contractor_info co ON i.contractor_id = co.id
        WHERE i.invoice_number = ?
    ''', (invoice_number,))
    invoice = cursor.fetchone()
    
    # Get receipt number if paid
    receipt_number = None
    if invoice and invoice[10] == 'paid':
        cursor.execute('SELECT receipt_number FROM receipts WHERE invoice_id = ?', (invoice[0],))
        receipt_result = cursor.fetchone()
        if receipt_result:
            receipt_number = receipt_result[0]
    
    conn.close()
    
    if not invoice:
        flash('Invoice not found!')
        return redirect(url_for('list_invoices'))
    
    return render_template_string('''
    <html>
    <head>
        <title>Invoice {{ invoice[1] }}</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 50px; }
            .invoice-header { text-align: center; margin-bottom: 30px; }
            .invoice-details { margin: 20px 0; }
            .btn { padding: 10px 20px; margin: 5px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="invoice-header">
            <h1>Invoice #{{ invoice[1] }}</h1>
        </div>
        
        <div class="invoice-details">
            <strong>From:</strong><br>
            {{ invoice[15] }}<br>
            {{ invoice[16] }}<br>
            {{ invoice[17] }}<br>
            {{ invoice[18] }}<br>
            {% if invoice[19] %}<strong>Tax ID:</strong> {{ invoice[19] }}<br>{% endif %}
            {% if invoice[20] %}<strong>Personal Tax ID:</strong> {{ invoice[20] }}<br>{% endif %}
        </div>
        
        <div class="invoice-details">
            <strong>To:</strong><br>
            {{ invoice[11] }}<br>
            {{ invoice[12] }}<br>
            {{ invoice[13] }}<br>
            {{ invoice[14] }}<br>
        </div>
        
        <div class="invoice-details">
            <strong>Date:</strong> {{ invoice[9].split(' ')[0] if invoice[9] else 'N/A' }}<br>
            <strong>Service:</strong> {{ invoice[4] }}<br>
            {% if invoice[5] %}<strong>Description:</strong> {{ invoice[5] }}<br>{% endif %}
            <strong>Quantity:</strong> {{ invoice[6] }}<br>
            <strong>Rate:</strong> ${{ "%.2f"|format(invoice[7]) }}<br>
            <strong>Total:</strong> ${{ "%.2f"|format(invoice[8]) }} only<br>
            <strong>Status:</strong> {{ invoice[10] }}<br>
        </div>
        
        <div>
            <a href="/download-invoice/{{ invoice[1] }}" class="btn">Download Invoice PDF</a>
            {% if invoice[10] == 'pending' %}
            <a href="/edit-invoice/{{ invoice[1] }}" class="btn">Edit Invoice</a>
            <a href="/mark-paid/{{ invoice[1] }}" class="btn">Mark as Paid</a>
            {% elif invoice[10] == 'paid' and receipt_number %}
            <a href="/download-receipt/{{ receipt_number }}" class="btn">Download Receipt PDF</a>
            {% endif %}
            <a href="/invoices" class="btn">Back to Invoices</a>
        </div>
    </body>
    </html>
    ''', invoice=invoice, receipt_number=receipt_number)

@app.route('/edit-invoice/<invoice_number>', methods=['GET', 'POST'])
def edit_invoice(invoice_number):
    conn = sqlite3.connect('invoices.db')
    cursor = conn.cursor()
    
    if request.method == 'POST':
        # Calculate new total
        rate = float(request.form['rate'])
        quantity = int(request.form['quantity'])
        total = rate * quantity
        
        # Update invoice
        cursor.execute('''
            UPDATE invoices 
            SET client_id=?, service_name=?, service_description=?, quantity=?, rate=?, total=?
            WHERE invoice_number=? AND status='pending'
        ''', (request.form['client_id'], request.form['service_name'], 
              request.form['service_description'], quantity, rate, total, invoice_number))
        
        conn.commit()
        conn.close()
        
        flash(f'Invoice {invoice_number} updated successfully!')
        return redirect(url_for('view_invoice', invoice_number=invoice_number))
    
    # Get invoice details for editing
    cursor.execute('''
        SELECT i.id, i.invoice_number, i.client_id, i.contractor_id, i.service_name, 
               i.service_description, i.quantity, i.rate, i.total, i.date_created, i.status,
               c.name, c.address, c.email, c.phone, 
               co.name, co.address, co.email, co.phone, co.tax_id, co.personal_tax_id
        FROM invoices i
        JOIN clients c ON i.client_id = c.id
        JOIN contractor_info co ON i.contractor_id = co.id
        WHERE i.invoice_number = ?
    ''', (invoice_number,))
    invoice = cursor.fetchone()
    
    if not invoice:
        flash('Invoice not found!')
        conn.close()
        return redirect(url_for('list_invoices'))
    
    # Check if invoice is still editable (pending status)
    if invoice[10] != 'pending':
        flash('Only pending invoices can be edited!')
        conn.close()
        return redirect(url_for('view_invoice', invoice_number=invoice_number))
    
    # Get clients for dropdown
    cursor.execute('SELECT id, name FROM clients ORDER BY name')
    clients = cursor.fetchall()
    conn.close()
    
    return render_template_string('''
    <html>
    <head>
        <title>Edit Invoice {{ invoice[1] }}</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 50px; }
            .form-group { margin: 10px 0; }
            input, select, textarea { width: 300px; padding: 8px; }
            .btn { padding: 10px 20px; background-color: #007bff; color: white; border: none; border-radius: 5px; margin: 5px; text-decoration: none; }
            .btn-secondary { background-color: #6c757d; }
            .alert { padding: 10px; margin: 10px 0; background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>Edit Invoice #{{ invoice[1] }}</h1>
        
        <div class="alert">
            <strong>Note:</strong> Only pending invoices can be edited. Once marked as paid, invoices cannot be modified.
        </div>
        
        <form method="POST">
            <div class="form-group">
                <label>Client:</label><br>
                <select name="client_id" required>
                    {% for client in clients %}
                    <option value="{{ client[0] }}" {% if client[0] == invoice[2] %}selected{% endif %}>{{ client[1] }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group">
                <label>Service/Product Name:</label><br>
                <input type="text" name="service_name" value="{{ invoice[4] }}" required>
            </div>
            <div class="form-group">
                <label>Service Description:</label><br>
                <textarea name="service_description" rows="3" placeholder="Detailed description of the service/product">{{ invoice[5] or '' }}</textarea>
            </div>
            <div class="form-group">
                <label>Quantity:</label><br>
                <input type="number" name="quantity" value="{{ invoice[6] }}" min="1" required>
            </div>
            <div class="form-group">
                <label>Rate:</label><br>
                <input type="number" name="rate" value="{{ invoice[7] }}" step="0.01" required>
            </div>
            <div class="form-group">
                <strong>Current Total: ${{ "%.2f"|format(invoice[8]) }}</strong>
            </div>
            <button type="submit" class="btn">Update Invoice</button>
            <a href="/invoice/{{ invoice[1] }}" class="btn btn-secondary">Cancel</a>
        </form>
        
        <script>
            // Auto-calculate total when quantity or rate changes
            function updateTotal() {
                const quantity = parseFloat(document.querySelector('input[name="quantity"]').value) || 0;
                const rate = parseFloat(document.querySelector('input[name="rate"]').value) || 0;
                const total = quantity * rate;
                document.querySelector('.form-group strong').textContent = `Current Total: ${total.toFixed(2)}`;
            }
            
            document.querySelector('input[name="quantity"]').addEventListener('input', updateTotal);
            document.querySelector('input[name="rate"]').addEventListener('input', updateTotal);
        </script>
    </body>
    </html>
    ''', invoice=invoice, clients=clients)

@app.route('/download-invoice/<invoice_number>')
def download_invoice(invoice_number):
    conn = sqlite3.connect('invoices.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT i.id, i.invoice_number, i.client_id, i.contractor_id, i.service_name, 
               i.service_description, i.quantity, i.rate, i.total, i.date_created, i.status,
               c.name, c.address, c.email, c.phone, 
               co.name, co.address, co.email, co.phone, co.tax_id, co.personal_tax_id
        FROM invoices i
        JOIN clients c ON i.client_id = c.id
        JOIN contractor_info co ON i.contractor_id = co.id
        WHERE i.invoice_number = ?
    ''', (invoice_number,))
    invoice = cursor.fetchone()
    conn.close()
    
    if not invoice:
        flash('Invoice not found!')
        return redirect(url_for('list_invoices'))
    
    # Create invoice data dictionary
    invoice_data = {
        'invoice_number': invoice[1],
        'client_name': invoice[11],
        'client_address': invoice[12],
        'client_email': invoice[13],
        'client_phone': invoice[14],
        'contractor_name': invoice[15],
        'contractor_address': invoice[16],
        'contractor_email': invoice[17],
        'contractor_phone': invoice[18],
        'contractor_tax_id': invoice[19],
        'contractor_personal_tax_id': invoice[20],
        'service_name': invoice[4],
        'service_description': invoice[5],
        'quantity': invoice[6],
        'rate': invoice[7],
        'total': invoice[8],
        'date_created': invoice[9]
    }
    
    try:
        filepath = generate_invoice_pdf(invoice_data)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}')
        return redirect(url_for('view_invoice', invoice_number=invoice_number))

@app.route('/mark-paid/<invoice_number>')
def mark_paid(invoice_number):
    conn = sqlite3.connect('invoices.db')
    cursor = conn.cursor()
    
    # Update invoice status
    cursor.execute('UPDATE invoices SET status = ? WHERE invoice_number = ?', 
                   ('paid', invoice_number))
    
    # Get invoice details for receipt
    cursor.execute('''
        SELECT i.id, i.invoice_number, i.client_id, i.contractor_id, i.service_name, 
               i.service_description, i.quantity, i.rate, i.total, i.date_created, i.status,
               c.name, c.address, c.email, c.phone, 
               co.name, co.address, co.email, co.phone, co.tax_id, co.personal_tax_id
        FROM invoices i
        JOIN clients c ON i.client_id = c.id
        JOIN contractor_info co ON i.contractor_id = co.id
        WHERE i.invoice_number = ?
    ''', (invoice_number,))
    invoice = cursor.fetchone()
    
    # Generate receipt number
    cursor.execute('SELECT COUNT(*) FROM receipts')
    count = cursor.fetchone()[0]
    receipt_number = f"REC-{(count + 1):04d}"
    
    # Insert receipt
    cursor.execute('''
        INSERT INTO receipts (invoice_id, receipt_number, paid_amount, payment_date)
        VALUES (?, ?, ?, ?)
    ''', (invoice[0], receipt_number, invoice[8], datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    conn.commit()
    conn.close()
    
    flash(f'Invoice marked as paid! Receipt {receipt_number} generated.')
    return redirect(url_for('view_invoice', invoice_number=invoice_number))

@app.route('/download-receipt/<receipt_number>')
def download_receipt(receipt_number):
    conn = sqlite3.connect('invoices.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.*, i.invoice_number, i.service_name, i.service_description, c.name, c.address, c.email, c.phone,
               co.name, co.address, co.email, co.phone, co.tax_id, co.personal_tax_id
        FROM receipts r
        JOIN invoices i ON r.invoice_id = i.id
        JOIN clients c ON i.client_id = c.id
        JOIN contractor_info co ON i.contractor_id = co.id
        WHERE r.receipt_number = ?
    ''', (receipt_number,))
    receipt = cursor.fetchone()
    conn.close()
    
    if not receipt:
        flash('Receipt not found!')
        return redirect(url_for('list_invoices'))
    
    # Create receipt data dictionary
    receipt_data = {
        'receipt_number': receipt[2],
        'invoice_number': receipt[5],
        'service_name': receipt[6],
        'service_description': receipt[7],
        'paid_amount': receipt[3],
        'payment_date': receipt[4],
        'client_name': receipt[8],
        'client_address': receipt[9],
        'client_email': receipt[10],
        'client_phone': receipt[11],
        'contractor_name': receipt[12],
        'contractor_address': receipt[13],
        'contractor_email': receipt[14],
        'contractor_phone': receipt[15],
        'contractor_tax_id': receipt[16],
        'contractor_personal_tax_id': receipt[17]
    }
    
    try:
        filepath = generate_receipt_pdf(receipt_data)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}')
        return redirect(url_for('list_invoices'))

@app.route('/receipts')
def list_receipts():
    conn = sqlite3.connect('invoices.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.receipt_number, i.invoice_number, c.name, i.service_name, 
               r.paid_amount, r.payment_date
        FROM receipts r
        JOIN invoices i ON r.invoice_id = i.id
        JOIN clients c ON i.client_id = c.id
        ORDER BY r.payment_date DESC
    ''')
    receipts = cursor.fetchall()
    conn.close()
    
    return render_template_string('''
    <html>
    <head>
        <title>All Receipts</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 50px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .btn { padding: 5px 10px; margin: 2px; background-color: #007bff; color: white; text-decoration: none; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>All Receipts</h1>
        <table>
            <tr>
                <th>Receipt #</th>
                <th>Invoice #</th>
                <th>Client</th>
                <th>Service</th>
                <th>Amount</th>
                <th>Payment Date</th>
                <th>Actions</th>
            </tr>
            {% for receipt in receipts %}
            <tr>
                <td>{{ receipt[0] }}</td>
                <td>{{ receipt[1] }}</td>
                <td>{{ receipt[2] }}</td>
                <td>{{ receipt[3] }}</td>
                <td>${{ "%.2f"|format(receipt[4]) }}</td>
                <td>{{ receipt[5].split(' ')[0] }}</td>
                <td>
                    <a href="/download-receipt/{{ receipt[0] }}" class="btn">Download</a>
                </td>
            </tr>
            {% endfor %}
        </table>
        <a href="/">Back to Home</a>
    </body>
    </html>
    ''', receipts=receipts)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)