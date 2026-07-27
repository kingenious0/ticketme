"""
Settings Blueprint for TicketMe.
"""
import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from app.extensions import db
from app.models.setting import Setting
from app.utils.decorators import role_required

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
@role_required('Manager')
def index():
    setting = Setting.query.first()
    if not setting:
        setting = Setting()
        db.session.add(setting)
        db.session.commit()

    if request.method == 'POST':
        setting.business_name = request.form.get('business_name', '').strip()
        setting.business_phone = request.form.get('business_phone', '').strip()
        setting.business_email = request.form.get('business_email', '').strip()
        setting.business_address = request.form.get('business_address', '').strip()
        setting.currency = request.form.get('currency', 'GHS').strip()
        setting.receipt_footer = request.form.get('receipt_footer', '').strip()

        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                if ext in current_app.config['ALLOWED_EXTENSIONS']:
                    new_filename = f"logo.{ext}"
                    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'logo')
                    os.makedirs(upload_path, exist_ok=True)
                    file.save(os.path.join(upload_path, new_filename))
                    setting.logo_path = f"uploads/logo/{new_filename}"

        db.session.commit()
        flash('System settings updated successfully.', 'success')
        return redirect(url_for('settings.index'))

    return render_template('settings/index.html', setting=setting)
