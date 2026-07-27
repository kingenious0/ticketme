"""
QR Code Generation Utility for TicketMe.
"""
import os
import qrcode
from flask import current_app

def generate_ticket_qr(ticket_number, verification_data=None):
    """
    Generates a QR code image for a ticket and saves it in app/static/uploads/qrcodes/.
    Returns the relative static path (e.g. 'uploads/qrcodes/TKT-2026-XXXXX.png').
    """
    qr_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'qrcodes')
    os.makedirs(qr_dir, exist_ok=True)

    filename = f"{ticket_number}.png"
    filepath = os.path.join(qr_dir, filename)

    data_to_encode = verification_data if verification_data else ticket_number

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(data_to_encode)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#1e293b", back_color="#ffffff")
    img.save(filepath)

    return f"uploads/qrcodes/{filename}"
