# Invoice System

A professional, local invoice and receipt management system built with Flask. Generate beautiful PDFs, manage clients, and track payments - all stored locally on your computer.

![Invoice System](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🌟 Features

### 📊 **Dashboard**
- Real-time statistics and financial overview
- Quick action buttons for common tasks
- Recent invoices and receipts display
- Visual status indicators

### 👤 **Client Management**
- Add, edit, and view client information
- Complete contact details storage
- Client history and invoice tracking
- Easy client selection for new invoices

### 📄 **Invoice Management**
- Create professional invoices with automatic numbering
- Edit pending invoices
- Service descriptions and detailed line items
- Real-time total calculations
- Status tracking (pending/paid)

### 🧾 **Receipt Generation**
- Automatic receipt creation when invoices are marked as paid
- Legal confirmation statements
- Professional PDF formatting
- Linked to original invoices

### 🎨 **Professional PDF Generation**
- Beautiful, business-ready invoice and receipt layouts
- Color-coded themes (blue for invoices, green for receipts)
- Separate sections for descriptions
- Tax ID fields for business compliance
- "Only" text for legal requirements

### 💼 **Contractor Management**
- Setup your business information
- Tax ID and Personal Tax ID fields
- Complete contact details
- Appears on all generated documents

### 💾 **Local Data Storage**
- SQLite database - no cloud dependency
- All data stored locally for privacy
- Easy backup and migration
- No monthly fees or data limits

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/invoice-system.git
   cd invoice-system
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv invoice_env
   
   # Windows
   invoice_env\Scripts\activate
   
   # Mac/Linux
   source invoice_env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open in browser**
   ```
   http://localhost:5000
   ```

## 📁 Project Structure

```
invoice_system/
├── app.py                    # Main application entry point
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── README.md                # Project documentation
├── 
├── models/                   # Data models
│   ├── __init__.py
│   ├── database.py          # Database operations
│   ├── contractor.py        # Contractor model
│   ├── client.py            # Client model
│   ├── invoice.py           # Invoice model
│   └── receipt.py           # Receipt model
├── 
├── routes/                   # Route handlers
│   ├── __init__.py
│   ├── main.py              # Dashboard routes
│   ├── contractor.py        # Contractor routes
│   ├── client.py            # Client routes
│   ├── invoice.py           # Invoice routes
│   └── receipt.py           # Receipt routes
├── 
├── services/                 # Business logic
│   ├── __init__.py
│   └── pdf_generator.py     # PDF generation service
├── 
├── templates/                # HTML templates
│   ├── base.html            # Base template
│   ├── index.html           # Dashboard
│   ├── contractor/
│   │   └── setup.html       # Contractor setup
│   ├── clients/
│   │   ├── list.html        # Client list
│   │   ├── add.html         # Add client
│   │   ├── edit.html        # Edit client
│   │   └── view.html        # View client
│   ├── invoices/
│   │   ├── list.html        # Invoice list
│   │   ├── create.html      # Create invoice
│   │   ├── edit.html        # Edit invoice
│   │   └── view.html        # View invoice
│   └── receipts/
│       ├── list.html        # Receipt list
│       └── view.html        # View receipt
├── 
├── static/                   # Static files
│   ├── css/
│   │   └── style.css        # Custom styles
│   └── js/
│       └── main.js          # JavaScript functionality
├── 
├── data/                     # Database (auto-created)
│   └── invoices.db          # SQLite database
└── 
└── pdfs/                     # Generated PDFs (auto-created)
    ├── invoices/
    └── receipts/
```

## 🎯 Usage Guide

### First Time Setup

1. **Setup Contractor Information**
   - Navigate to "Setup Contractor Info"
   - Fill in your business details
   - Add tax IDs if applicable

2. **Add Your First Client**
   - Go to "Manage Clients"
   - Click "Add New Client"
   - Fill in client information

3. **Create Your First Invoice**
   - Click "Create Invoice" from dashboard
   - Select client and fill in service details
   - Invoice will be auto-numbered (INV-0001, etc.)

4. **Mark Invoice as Paid**
   - Go to invoice details
   - Click "Mark as Paid"
   - Receipt will be automatically generated

### Daily Workflow

1. **Create invoices** for completed work
2. **Download PDF invoices** to send to clients
3. **Mark invoices as paid** when payment received
4. **Download receipt PDFs** for your records
5. **View dashboard** for financial overview

## 🔧 Configuration

### Environment Variables (Optional)
```bash
# Set custom secret key (recommended for production)
export SECRET_KEY=your-super-secret-key-here
```

### Database Location
The SQLite database is stored in `data/invoices.db`. To backup your data, simply copy this file.

### PDF Storage
Generated PDFs are stored in:
- `pdfs/invoices/` - Invoice PDFs
- `pdfs/receipts/` - Receipt PDFs

## 🎨 Customization

### Changing Colors
Edit `static/css/style.css` to modify the color scheme:
```css
:root {
    --primary-color: #007bff;    /* Main blue color */
    --success-color: #28a745;    /* Green for success */
    --warning-color: #ffc107;    /* Yellow for warnings */
}
```

### PDF Styling
Modify `services/pdf_generator.py` to change PDF layouts, colors, or add your logo.

### Invoice Numbering
Change the prefix in `config.py`:
```python
INVOICE_PREFIX = 'INV-'  # Change to your preferred prefix
RECEIPT_PREFIX = 'REC-'  # Change to your preferred prefix
```

## 📊 Database Schema

### Tables
- **contractor_info** - Your business information
- **clients** - Client contact details
- **invoices** - Invoice records with line items
- **receipts** - Payment receipts linked to invoices

### Key Features
- Automatic invoice numbering
- Status tracking (pending/paid)
- Foreign key relationships
- Audit trail with timestamps

## 🛡️ Security Features

- **Local storage only** - No cloud dependency
- **No external API calls** - All processing local
- **SQLite database** - File-based, easy to backup
- **Input validation** - Form validation on client and server
- **Error handling** - Graceful error management

## 🐛 Troubleshooting

### Common Issues

**Database errors on first run:**
- Ensure the `data/` directory exists
- Check file permissions

**PDF generation fails:**
- Verify `reportlab` is installed correctly
- Check `pdfs/` directory permissions

**Template not found errors:**
- Ensure all template files are in correct directories
- Check file names match route handlers

**Port already in use:**
```bash
# Run on different port
python app.py --port 5001
```

## 🚀 Deployment

### Local Network Access
To access from other devices on your network:
```python
# In app.py, change:
app.run(debug=True, host='0.0.0.0')
```

### Production Deployment
For production use, consider:
- Using a production WSGI server (gunicorn, waitress)
- Setting up proper logging
- Configuring environment variables
- Setting up automated backups

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Flask** - The web framework that powers this application
- **ReportLab** - For beautiful PDF generation
- **Bootstrap** - For responsive and professional UI
- **Font Awesome** - For beautiful icons

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/invoice-system/issues) page
2. Create a new issue with detailed description
3. Include error messages and steps to reproduce

## 🔄 Changelog

### Version 1.0.0
- Initial release
- Basic invoice and receipt management
- Professional PDF generation
- Client management
- Dashboard with statistics
- Local SQLite storage

---

**Made with ❤️ for small businesses and freelancers**