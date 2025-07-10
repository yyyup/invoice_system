import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib import colors
from config import Config

def get_custom_styles():
    """Get custom styles for professional documents"""
    styles = getSampleStyleSheet()
    
    # Title style
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    # Subtitle style
    styles.add(ParagraphStyle(
        name='Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    # Section header style
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#2980b9'),
        spaceBefore=15,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    ))
    
    # Address style
    styles.add(ParagraphStyle(
        name='Address',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=5,
        leftIndent=10
    ))
    
    # Description style
    styles.add(ParagraphStyle(
        name='Description',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#555555'),
        spaceAfter=10,
        alignment=TA_JUSTIFY,
        leftIndent=10,
        rightIndent=10
    ))
    
    # Total style
    styles.add(ParagraphStyle(
        name='Total',
        parent=styles['Normal'],
        fontSize=16,
        textColor=colors.HexColor('#27ae60'),
        spaceBefore=20,
        spaceAfter=20,
        alignment=TA_RIGHT,
        fontName='Helvetica-Bold'
    ))
    
    return styles

def generate_invoice_pdf(invoice_data):
    """Generate professional invoice PDF"""
    # Format: Invoice_INV-0001_2025-07-12.pdf
    invoice_date = invoice_data['invoice_date'].replace('-', '')  # Remove dashes: 20250712
    filename = f"Invoice_{invoice_data['invoice_number']}_{invoice_date}.pdf"
    filepath = os.path.join(Config.INVOICE_PDF_FOLDER, filename)
    
    # Ensure directory exists
    os.makedirs(Config.INVOICE_PDF_FOLDER, exist_ok=True)
    
    doc = SimpleDocTemplate(
        filepath, 
        pagesize=letter,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch
    )
    
    styles = get_custom_styles()
    story = []
    
    # Header with title
    title = Paragraph(f"INVOICE", styles['CustomTitle'])
    story.append(title)
    
    invoice_number = Paragraph(f"#{invoice_data['invoice_number']}", styles['Subtitle'])
    story.append(invoice_number)
    
    # Add horizontal line
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#3498db')))
    story.append(Spacer(1, 20))
    
    # Create two-column layout for FROM and TO
    contact_data = [
        [
            Paragraph('<b>FROM:</b>', styles['SectionHeader']),
            Paragraph('<b>TO:</b>', styles['SectionHeader'])
        ],
        [
            Paragraph(f"""
                <b>{invoice_data['contractor_name']}</b><br/>
                {invoice_data['contractor_address'].replace(chr(10), '<br/>')}<br/>
                <b>Email:</b> {invoice_data['contractor_email']}<br/>
                <b>Phone:</b> {invoice_data['contractor_phone']}<br/>
                {f"<b>Tax ID:</b> {invoice_data['contractor_tax_id']}<br/>" if invoice_data.get('contractor_tax_id') else ""}
                {f"<b>Personal Tax ID:</b> {invoice_data['contractor_personal_tax_id']}<br/>" if invoice_data.get('contractor_personal_tax_id') else ""}
            """, styles['Address']),
            Paragraph(f"""
                <b>{invoice_data['client_name']}</b><br/>
                {invoice_data['client_address'].replace(chr(10), '<br/>')}<br/>
                <b>Email:</b> {invoice_data['client_email']}<br/>
                <b>Phone:</b> {invoice_data['client_phone']}<br/>
            """, styles['Address'])
        ]
    ]
    
    contact_table = Table(contact_data, colWidths=[3.5*inch, 3.5*inch])
    contact_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(contact_table)
    story.append(Spacer(1, 20))
    
    # Invoice details - with option for blank dates
    invoice_date_display = invoice_data.get('leave_date_blank', False) and "________________" or invoice_data['invoice_date']
    
    details_data = [
        ['Invoice Date:', invoice_date_display],  # Show blank line or actual date
        ['Status:', 'Pending Payment' if invoice_data.get('status') == 'pending' else 'Paid']
    ]
    
    details_table = Table(details_data, colWidths=[2*inch, 2*inch])
    details_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2980b9')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(details_table)
    story.append(Spacer(1, 30))
    
    # Service section header
    service_header = Paragraph('SERVICE DETAILS', styles['SectionHeader'])
    story.append(service_header)
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#bdc3c7')))
    story.append(Spacer(1, 15))
    
    # Service table with multiple line items
    service_data = [
        ['Service', 'Description', 'Quantity', 'Rate', 'Total']
    ]
    
    # Add line items to table
    for item in invoice_data.get('line_items', []):
        # Use Paragraph for description to enable text wrapping
        desc_text = item.get('service_description', '')
        if desc_text:
            desc_paragraph = Paragraph(desc_text, ParagraphStyle(
                'WrappedText',
                parent=styles['Normal'],
                fontSize=8,
                leading=10,
                alignment=TA_LEFT
            ))
        else:
            desc_paragraph = ''
        
        service_data.append([
            item['service_name'],
            desc_paragraph,  # Use Paragraph instead of plain text
            str(item['quantity']),
            f"${item['rate']:.2f}",
            f"${item['amount']:.2f}"
        ])
    
    # Column widths: Service smaller, Description gets space, others stay same
    service_table = Table(service_data, colWidths=[1.8*inch, 1.8*inch, 0.8*inch, 1.2*inch, 1.2*inch])
    service_table.setStyle(TableStyle([
        # Header row - smaller font
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),  # Smaller header font
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),  # Smaller data font
        ('ALIGN', (2, 1), (-1, -1), 'CENTER'),  # Center quantity, rate, total
        ('ALIGN', (0, 1), (1, -1), 'LEFT'),     # Left align service and description
        ('VALIGN', (0, 1), (-1, -1), 'TOP'),    # Top align content for proper wrapping
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 10),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#2980b9')),
    ]))
    
    story.append(service_table)
    story.append(Spacer(1, 20))
    
    # Total section
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2980b9')))
    story.append(Spacer(1, 15))
    
    total_data = [
        ['', 'TOTAL DUE:', f"${invoice_data['total']:.2f} only"]
    ]
    
    total_table = Table(total_data, colWidths=[4*inch, 1.5*inch, 1.5*inch])
    total_table.setStyle(TableStyle([
        ('FONTNAME', (1, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (1, 0), (-1, 0), 14),
        ('TEXTCOLOR', (1, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('ALIGN', (1, 0), (-1, 0), 'RIGHT'),
        ('PADDING', (1, 0), (-1, 0), 12),
    ]))
    
    story.append(total_table)
    story.append(Spacer(1, 30))
    
    # Footer - different message based on status
    if invoice_data.get('status') == 'paid':
        footer_text = "Thank you for your business! This invoice has been paid in full."
    else:
        footer_text = "Thank you for your business! Please remit payment by the due date."
    
    footer = Paragraph(footer_text, styles['Description'])
    story.append(footer)
    
    doc.build(story)
    return filepath

def generate_receipt_pdf(receipt_data):
    """Generate professional receipt PDF - optimized for single page"""
    # Format: Receipt_REC-0001_2025-07-12.pdf
    payment_date = receipt_data['payment_date'].split(' ')[0].replace('-', '')  # Remove dashes: 20250712
    filename = f"Receipt_{receipt_data['receipt_number']}_{payment_date}.pdf"
    filepath = os.path.join(Config.RECEIPT_PDF_FOLDER, filename)
    
    # Ensure directory exists
    os.makedirs(Config.RECEIPT_PDF_FOLDER, exist_ok=True)
    
    doc = SimpleDocTemplate(
        filepath, 
        pagesize=letter,
        topMargin=0.4*inch,      # Reduced top margin
        bottomMargin=0.4*inch,   # Reduced bottom margin
        leftMargin=0.6*inch,     # Reduced left margin
        rightMargin=0.6*inch     # Reduced right margin
    )
    
    styles = get_custom_styles()
    story = []
    
    # Header with title - more compact
    title = Paragraph(f"PAYMENT RECEIPT", styles['CustomTitle'])
    story.append(title)
    
    receipt_number = Paragraph(f"#{receipt_data['receipt_number']}", styles['Subtitle'])
    story.append(receipt_number)
    
    # Add horizontal line
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#27ae60')))
    story.append(Spacer(1, 12))  # Reduced spacing
    
    # Create two-column layout for FROM and TO - more compact
    contact_data = [
        [
            Paragraph('<b>FROM:</b>', styles['SectionHeader']),
            Paragraph('<b>TO:</b>', styles['SectionHeader'])
        ],
        [
            Paragraph(f"""
                <b>{receipt_data['contractor_name']}</b><br/>
                {receipt_data['contractor_address'].replace(chr(10), '<br/>')}<br/>
                <b>Email:</b> {receipt_data['contractor_email']}<br/>
                <b>Phone:</b> {receipt_data['contractor_phone']}<br/>
                {f"<b>Tax ID:</b> {receipt_data['contractor_tax_id']}<br/>" if receipt_data.get('contractor_tax_id') else ""}
                {f"<b>Personal Tax ID:</b> {receipt_data['contractor_personal_tax_id']}<br/>" if receipt_data.get('contractor_personal_tax_id') else ""}
            """, styles['Address']),
            Paragraph(f"""
                <b>{receipt_data['client_name']}</b><br/>
                {receipt_data['client_address'].replace(chr(10), '<br/>')}<br/>
                <b>Email:</b> {receipt_data['client_email']}<br/>
                <b>Phone:</b> {receipt_data['client_phone']}<br/>
            """, styles['Address'])
        ]
    ]
    
    contact_table = Table(contact_data, colWidths=[4*inch, 4*inch])  # Wider columns
    contact_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),  # Reduced padding
    ]))
    
    story.append(contact_table)
    story.append(Spacer(1, 12))  # Reduced spacing
    
    # Payment details - with option for blank dates
    payment_date_display = receipt_data.get('leave_date_blank', False) and "________________" or receipt_data['payment_date'].split(' ')[0]
    
    details_data = [
        ['Payment Date:', payment_date_display],  # Show blank line or actual date
        ['Invoice Number:', receipt_data['invoice_number']],
        ['Services:', f"{len(receipt_data.get('line_items', []))} item(s)" if receipt_data.get('line_items') else receipt_data.get('service_name', 'Services Rendered')]
    ]
    
    details_table = Table(details_data, colWidths=[1.5*inch, 2.5*inch])  # Adjusted widths
    details_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),  # Smaller font
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#27ae60')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),  # Reduced padding
    ]))
    
    story.append(details_table)
    story.append(Spacer(1, 15))  # Reduced spacing
    
    # Services section - show line items if available
    if receipt_data.get('line_items'):
        service_header = Paragraph('SERVICES PROVIDED', styles['SectionHeader'])
        story.append(service_header)
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#bdc3c7')))
        story.append(Spacer(1, 8))  # Reduced spacing
        
        # Service table with multiple line items - more compact
        service_data = [
            ['Service', 'Description', 'Qty', 'Rate', 'Amount']
        ]
        
        # Add line items to table
        for item in receipt_data['line_items']:
            # Use Paragraph for description to enable text wrapping
            desc_text = item.get('service_description', '')
            if desc_text:
                desc_paragraph = Paragraph(desc_text, ParagraphStyle(
                    'WrappedText',
                    parent=styles['Normal'],
                    fontSize=7,  # Smaller font for receipt
                    leading=9,
                    alignment=TA_LEFT
                ))
            else:
                desc_paragraph = ''
            
            service_data.append([
                item['service_name'],
                desc_paragraph,  # Use Paragraph instead of truncated text
                str(item['quantity']),
                f"${item['rate']:.2f}",
                f"${item['amount']:.2f}"
            ])
        
        # More compact column widths
        service_table = Table(service_data, colWidths=[2.2*inch, 2.2*inch, 0.6*inch, 1*inch, 1*inch])
        service_table.setStyle(TableStyle([
            # Header row - compact
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),  # Smaller header font
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),  # Reduced padding
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            
            # Data rows - compact
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),  # Smaller data font
            ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (1, -1), 'LEFT'),
            ('VALIGN', (0, 1), (-1, -1), 'TOP'),  # Top align for proper text wrapping
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),  # Increased padding for wrapped text
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),  # Thinner grid lines
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#27ae60')),
        ]))
        
        story.append(service_table)
        story.append(Spacer(1, 12))  # Reduced spacing
    
    # Description section (if exists and only one service) - more compact
    elif receipt_data.get('service_description'):
        desc_header = Paragraph('SERVICE DESCRIPTION', styles['SectionHeader'])
        story.append(desc_header)
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#bdc3c7')))
        story.append(Spacer(1, 6))  # Reduced spacing
        
        description = Paragraph(receipt_data['service_description'], styles['Description'])
        story.append(description)
        story.append(Spacer(1, 12))  # Reduced spacing
    
    # Amount received section - more compact
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#27ae60')))
    story.append(Spacer(1, 10))  # Reduced spacing
    
    amount_data = [
        ['', 'AMOUNT RECEIVED:', f"${receipt_data['paid_amount']:.2f} only"]
    ]
    
    amount_table = Table(amount_data, colWidths=[3.5*inch, 1.8*inch, 1.7*inch])  # Adjusted widths
    amount_table.setStyle(TableStyle([
        ('FONTNAME', (1, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (1, 0), (-1, 0), 12),  # Smaller font
        ('TEXTCOLOR', (1, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('ALIGN', (1, 0), (-1, 0), 'RIGHT'),
        ('PADDING', (1, 0), (-1, 0), 8),  # Reduced padding
    ]))
    
    story.append(amount_table)
    story.append(Spacer(1, 15))  # Reduced spacing
    
    # Legal confirmation section - more compact
    confirmation_header = Paragraph('PAYMENT CONFIRMATION', styles['SectionHeader'])
    story.append(confirmation_header)
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#bdc3c7')))
    story.append(Spacer(1, 8))  # Reduced spacing
    
    confirmation_text = f"""
    I, <b>{receipt_data['contractor_name']}</b>, hereby confirm that I have received the payment of 
    <b>${receipt_data['paid_amount']:.2f} only</b> in full from <b>{receipt_data['client_name']}</b> 
    for the services rendered as described above.
    """
    
    confirmation = Paragraph(confirmation_text, styles['Description'])
    story.append(confirmation)
    story.append(Spacer(1, 15))  # Reduced spacing
    
    # Thank you message - more compact
    thank_you = Paragraph(
        "<b>Thank you for your payment!</b><br/>This receipt serves as proof of payment.",
        styles['Description']
    )
    story.append(thank_you)
    
    doc.build(story)
    return filepath