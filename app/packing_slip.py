from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch


def create_packing_slip(filename, client, date, orders):
    # Create PDF
    doc = SimpleDocTemplate(filename, pagesize=letter,
                            rightMargin=30, leftMargin=30,
                            topMargin=30, bottomMargin=30)
    
    styles = getSampleStyleSheet()
    style_normal = styles["Normal"]
    style_heading = styles["Heading1"]


    elements = []

    logo = Image("app/static/images/mom-logo.png", width=1.5*inch, height=1.5*inch)
    elements.append(logo)

    company_paragraph = Paragraph(
        f"<b>{company_info['name']}</b><br/>{company_info['address']}<br/>{company_info['phone']}",
        style_normal,
    )
    elements.append(company_paragraph)

    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph("<b>Packing Slip</b>", styles['Heading1']))
    elements.append(Spacer(1, 0.2*inch))

    # Table data
    data = [["Customer", "Serving Date", "Item", "Order Amount"]] 
    # Wrap long text inside cells
    for order in orders:
        row = [
            Paragraph(str(order["Customer"]), styles['Normal']),
            Paragraph(str(order["Serving Date"]), styles['Normal']),
            Paragraph(str(order["Item"]), styles['Normal']),
            Paragraph(str(order["Order Amount"]), styles['Normal']),
        ]
        data.append(row)

    # Shrink column widths to fit page
    col_widths = [1*inch, 0.9*inch, 1.2*inch, 0.9*inch, 0.5*inch,
                  1*inch, 0.8*inch, 1.2*inch, 1.2*inch, 1*inch]

    # Create table
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.25, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),  # Ensure wrapping works vertically
    ]))


    elements.append(table)

    # Signature section
    elements.append(Paragraph("<b>Packed By:</b> ____________________________", style_normal))
    elements.append(Paragraph("<b>Checked By:</b> ____________________________", style_normal))
    elements.append(Paragraph("<b>Date:</b> ____________________________", style_normal))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("<i>Print Name:</i>", style_normal))
    elements.append(Paragraph("<i>Signature:</i>", style_normal))

    doc.build(elements)


company_info = {
    "name": "Meals On The Move",
    "address": "46 Hollinger Rd, Toronto ON M4B 3G5",
    "phone": "1-866-456-2121",
}
