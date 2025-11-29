from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os

COMPANY_NAME = "DHAYA DHARSAN RUBBER PRODUCTS"
COMPANY_ADDRESS = "385/1, CODIA Park, Kurumbapalayam,"
COMPANY_ADDRESS_2 = "Sathy main road, Coimbatore 641107."
COMPANY_GSTIN = "GSTIN No. 33AADPD5877J1Z6"
COMPANY_PHONE = "CELL: 90035 91255, 73737 86664"

def number_to_words(num):
    """Convert number to Indian rupees in words"""
    ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
    tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
    teens = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
    
    def convert_less_than_thousand(n):
        if n == 0:
            return ''
        elif n < 10:
            return ones[n]
        elif n < 20:
            return teens[n - 10]
        elif n < 100:
            return tens[n // 10] + (' ' + ones[n % 10] if n % 10 != 0 else '')
        else:
            return ones[n // 100] + ' Hundred' + (' ' + convert_less_than_thousand(n % 100) if n % 100 != 0 else '')
    
    if num == 0:
        return 'Zero Rupees Only'
    
    # Split into rupees and paise
    rupees = int(num)
    paise = int(round((num - rupees) * 100))
    
    # Convert rupees
    crore = rupees // 10000000
    rupees %= 10000000
    lakh = rupees // 100000
    rupees %= 100000
    thousand = rupees // 1000
    rupees %= 1000
    
    result = []
    if crore > 0:
        result.append(convert_less_than_thousand(crore) + ' Crore')
    if lakh > 0:
        result.append(convert_less_than_thousand(lakh) + ' Lakh')
    if thousand > 0:
        result.append(convert_less_than_thousand(thousand) + ' Thousand')
    if rupees > 0:
        result.append(convert_less_than_thousand(rupees))
    
    words = ' '.join(result) + ' Rupees'
    
    if paise > 0:
        words += ' and ' + convert_less_than_thousand(paise) + ' Paise'
    
    return words + ' Only'

def generate_invoice_pdf(invoice):
    invoice_dir = "invoices"
    if not os.path.exists(invoice_dir):
        os.makedirs(invoice_dir)

    filename = f"invoice_{invoice.invoice_number}.pdf"
    filepath = os.path.join(invoice_dir, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch,
                           leftMargin=0.5*inch, rightMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        alignment=TA_LEFT
    )
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Normal'],
        fontSize=14,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT
    )
    
    small_style = ParagraphStyle(
        'SmallStyle',
        parent=styles['Normal'],
        fontSize=8,
        leading=10
    )
    
    badge_style = ParagraphStyle(
        'BadgeStyle',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    )
    
    # Header section with company info and TAX INVOICE badge
    header_data = [
        [
            Paragraph(f"<b>{COMPANY_GSTIN}</b><br/><b>{COMPANY_NAME}</b><br/>{COMPANY_ADDRESS}<br/>{COMPANY_ADDRESS_2}<br/>{COMPANY_PHONE}", header_style),
            Paragraph("<b>TAX INVOICE</b>", badge_style)
        ]
    ]
    
    header_table = Table(header_data, colWidths=[5*inch, 2*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('VALIGN', (1, 0), (1, 0), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(header_table)
    
    # Invoice metadata section
    metadata_data = [
        ['No.', invoice.invoice_number or '', 'Date', invoice.issue_date.strftime('%d/%m/%Y') if invoice.issue_date else ''],
        ['Delivery Note No.', invoice.delivery_note_no or '', 'Date', ''],
        ['Buyer Order No.', invoice.buyer_order_no or '', 'Date', ''],
        ['Despatched Through', invoice.dispatch_through or '', 'Destination', ''],
        ['Dispatch Document No.', invoice.dispatch_doc_no or '', 'Terms & Conditions', '']
    ]
    
    metadata_table = Table(metadata_data, colWidths=[1.3*inch, 1.9*inch, 1.3*inch, 2.5*inch])
    metadata_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(metadata_table)
    
    # Customer section
    customer_text = f"<b>To</b><br/>M/s. {invoice.customer_name}"
    if invoice.customer_address:
        customer_text += f"<br/>{invoice.customer_address}"
    if invoice.customer_gstin:
        customer_text += f"<br/><b>GSTIN No.</b> {invoice.customer_gstin}"
    
    customer_data = [[Paragraph(customer_text, small_style)]]
    customer_table = Table(customer_data, colWidths=[7*inch])
    customer_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(customer_table)
    
    # Line items table
    line_items_header = ['S.No', 'Description of Goods', 'HSN CODE', 'Quantity', 'Rate', 'Amount\nRs.    P']
    line_items_data = [line_items_header]
    
    for idx, item in enumerate(invoice.line_items, 1):
        # Split amount into rupees and paise
        rupees = int(item.amount)
        paise = int(round((item.amount - rupees) * 100))
        amount_str = f"{rupees}    {paise:02d}" if paise > 0 else f"{rupees}    -"
        
        line_items_data.append([
            str(idx),
            item.description,
            item.hsn_code,
            str(item.quantity),
            f"{item.rate:.2f}",
            amount_str
        ])
    
    # Add empty rows to fill space if needed
    while len(line_items_data) < 12:  # Minimum 11 rows + header
        line_items_data.append(['', '', '', '', '', ''])
    
    line_items_table = Table(line_items_data, colWidths=[0.4*inch, 2.8*inch, 0.8*inch, 0.7*inch, 0.8*inch, 1.5*inch])
    line_items_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),
        ('ALIGN', (4, 0), (5, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    story.append(line_items_table)
    
    # Totals section
    sgst_percent = (invoice.total_sgst / invoice.subtotal * 100) if invoice.subtotal > 0 else 0
    cgst_percent = (invoice.total_cgst / invoice.subtotal * 100) if invoice.subtotal > 0 else 0
    igst_percent = (invoice.total_igst / invoice.subtotal * 100) if invoice.subtotal > 0 else 0
    
    # Format amounts with rupees and paise
    def format_amount(amount):
        rupees = int(amount)
        paise = int(round((amount - rupees) * 100))
        return f"{rupees}    {paise:02d}" if paise > 0 else f"{rupees}    -"
    
    totals_data = [
        ['', '', '', '', 'Total', format_amount(invoice.subtotal)],
    ]
    
    if invoice.total_sgst > 0:
        totals_data.append(['', '', '', '', f'SGST {sgst_percent:.0f}%', format_amount(invoice.total_sgst)])
    if invoice.total_cgst > 0:
        totals_data.append(['', '', '', '', f'CGST {cgst_percent:.0f}%', format_amount(invoice.total_cgst)])
    if invoice.total_igst > 0:
        totals_data.append(['', '', '', '', f'IGST {igst_percent:.0f}%', format_amount(invoice.total_igst)])
    
    totals_data.append(['', '', '', '', 'Gr Total', format_amount(invoice.final_amount)])
    
    totals_table = Table(totals_data, colWidths=[0.4*inch, 2.8*inch, 0.8*inch, 0.7*inch, 0.8*inch, 1.5*inch])
    totals_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (4, 0), (5, -1), 'RIGHT'),
        ('FONTNAME', (4, -1), (5, -1), 'Helvetica-Bold'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(totals_table)
    
    # Amount in words
    amount_words = number_to_words(invoice.final_amount)
    words_data = [[Paragraph(f"<b>Rupees in words:</b> {amount_words}", small_style)]]
    words_table = Table(words_data, colWidths=[7*inch])
    words_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(words_table)
    
    # Footer section
    footer_data = [
        [
            Paragraph("<b>Terms and condition:</b><br/>Our responsibility ceases the moment the goods leave<br/>our premises, goods once sold will not be taken back.<br/><br/>Disputes are subject to Coimbatore Jurisdiction.", small_style),
            Paragraph("Received the goods in good condition<br/><br/><br/><br/><b>For DHAYA DHARSANN RUBBER PRODUCTS</b>", small_style)
        ]
    ]
    
    footer_table = Table(footer_data, colWidths=[3.5*inch, 3.5*inch])
    footer_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(footer_table)
    
    doc.build(story)
    return filepath
