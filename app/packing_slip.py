from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def create_packing_slip(filename, client, date, orders):

    doc = SimpleDocTemplate(filename, pagesize=letter,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=40)

    styles = getSampleStyleSheet()
    style_normal = styles["Normal"]
    style_heading = styles["Heading1"]

    elements = []

    # Title
    elements.append(Paragraph("Packing Slip", style_heading))
    elements.append(Spacer(1, 12))

    # Client and date info
    elements.append(Paragraph(f"<b>Client:</b> {client}", style_normal))
    elements.append(Paragraph(f"<b>Shipment Date:</b> {date}", style_normal))
    elements.append(Spacer(1, 12))

    # Table data
    data = [
        ["Serving Date", "Item", "Meal", "Day", "Order Amount", "Client", "Quantity Shipped"]
    ]

    # Add rows
    for order in orders:
        data.append([
                order.get("Serving Date", "") or "",
                order.get("Item", "") or "",
                order.get("Meal", "") or "",
                order.get("Day", "") or "",
                order.get("Order Amount", "") or "",
                order.get("Client", "") or "",
                order.get("Quantity to Produce/Ship", "") or ""
        ])

    # Create table with style
    table = Table(data, repeatRows=1, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),

        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),

        ('BOTTOMPADDING', (0,0), (-1,0), 12),

        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 36))

    # Signature section
    elements.append(Paragraph("<b>Packed By:</b> ____________________________", style_normal))
    elements.append(Paragraph("<b>Checked By:</b> ____________________________", style_normal))
    elements.append(Paragraph("<b>Date:</b> ____________________________", style_normal))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("<i>Print Name:</i>", style_normal))
    elements.append(Paragraph("<i>Signature:</i>", style_normal))

    # Build PDF
    doc.build(elements)

# Example usage:
orders = [
    {'Serving Date': '2025-08-10', 'Item': 'Chicken', 'Meal': 'Lunch', 'Day': 'Monday',
     'Order Amount': 3, 'Client': 'ABC Corp', 'Quantity to Produce/Ship': 3},
    {'Serving Date': '2025-08-11', 'Item': 'Beef', 'Meal': 'Dinner', 'Day': 'Tuesday',
     'Order Amount': 2, 'Client': 'ABC Corp', 'Quantity to Produce/Ship': 2},
]

