"""
PDF Ticket Generator using ReportLab.
"""
import os
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from flask import current_app

def generate_ticket_pdf(ticket):
    """
    Generates an in-memory PDF binary stream for a Ticket.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TicketTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#0f172a'),
        alignment=1, # Center
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'TicketSubTitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#64748b'),
        alignment=1,
        spaceAfter=20
    )
    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        fontName='Helvetica-Bold'
    )
    value_style = ParagraphStyle(
        'Value',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#0f172a')
    )

    story = []

    story.append(Paragraph("TICKETME ADMISSION PASS", title_style))
    story.append(Paragraph(f"Official Entry Ticket • {ticket.ticket_number}", subtitle_style))
    story.append(Spacer(1, 10))

    # Details table
    data = [
        [Paragraph("EVENT NAME:", label_style), Paragraph(ticket.event.name, value_style)],
        [Paragraph("VENUE:", label_style), Paragraph(ticket.event.venue, value_style)],
        [Paragraph("DATE & TIME:", label_style), Paragraph(f"{ticket.event.event_date.strftime('%b %d, %Y')} at {ticket.event.start_time.strftime('%I:%M %p')}", value_style)],
        [Paragraph("ATTENDEE:", label_style), Paragraph(ticket.customer.name, value_style)],
        [Paragraph("PHONE:", label_style), Paragraph(ticket.customer.phone_number, value_style)],
        [Paragraph("TICKET TYPE:", label_style), Paragraph(ticket.ticket_type.name.upper(), value_style)],
        [Paragraph("BOOKING REF:", label_style), Paragraph(ticket.booking.booking_number, value_style)],
        [Paragraph("STATUS:", label_style), Paragraph(ticket.status.upper(), value_style)],
    ]

    t = Table(data, colWidths=[120, 300])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    # Add QR code if available
    if ticket.qr_code_path:
        abs_qr_path = os.path.join(current_app.root_path, 'static', ticket.qr_code_path)
        if os.path.exists(abs_qr_path):
            img = Image(abs_qr_path, width=150, height=150)
            img.hAlign = 'CENTER'
            story.append(img)
            story.append(Spacer(1, 10))

    story.append(Paragraph("Scan QR Code at entry gate. Present along with a valid ID.", subtitle_style))

    doc.build(story)
    buffer.seek(0)
    return buffer
