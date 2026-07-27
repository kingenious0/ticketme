"""
Event Management Blueprint for TicketMe.
"""
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from app.extensions import db
from app.models.event import Event
from app.utils.decorators import role_required

events_bp = Blueprint('events', __name__, url_prefix='/events')

@events_bp.route('/')
@login_required
def index():
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()
    page = request.args.get('page', 1, type=int)

    query = Event.query
    if search:
        query = query.filter((Event.name.ilike(f'%{search}%')) | (Event.venue.ilike(f'%{search}%')))
    if status:
        query = query.filter(Event.status == status)

    pagination = query.order_by(Event.event_date.desc()).paginate(page=page, per_page=12, error_out=False)
    return render_template('events/index.html', pagination=pagination, search=search, selected_status=status)

@events_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('Administrator', 'Manager')
def create():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        venue = request.form.get('venue', '').strip()
        event_date_str = request.form.get('event_date', '').strip()
        start_time_str = request.form.get('start_time', '').strip()
        end_time_str = request.form.get('end_time', '').strip()
        description = request.form.get('description', '').strip()
        status = request.form.get('status', 'Upcoming')

        if not name or not venue or not event_date_str or not start_time_str:
            flash('Event Name, Venue, Date, and Start Time are required.', 'warning')
            return redirect(url_for('events.create'))

        event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time() if end_time_str else None

        banner_filename = None
        # Banner image upload commented out per UI requirement
        # if 'banner_image' in request.files:
        #     file = request.files['banner_image']
        #     if file and file.filename != '':
        #         filename = secure_filename(file.filename)
        #         ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        #         if ext in current_app.config['ALLOWED_EXTENSIONS']:
        #             new_filename = f"event_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
        #             upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'banners')
        #             os.makedirs(upload_path, exist_ok=True)
        #             file.save(os.path.join(upload_path, new_filename))
        #             banner_filename = f"uploads/banners/{new_filename}"

        event = Event(
            name=name,
            venue=venue,
            event_date=event_date,
            start_time=start_time,
            end_time=end_time,
            banner_image=banner_filename,
            description=description,
            status=status
        )
        db.session.add(event)
        db.session.commit()

        flash(f'Event "{name}" created successfully.', 'success')
        return redirect(url_for('events.detail', event_id=event.id))

    return render_template('events/create.html')

@events_bp.route('/<int:event_id>')
@login_required
def detail(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('events/detail.html', event=event)

@events_bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('Administrator', 'Manager')
def edit(event_id):
    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        event.name = request.form.get('name', '').strip()
        event.venue = request.form.get('venue', '').strip()
        event_date_str = request.form.get('event_date', '').strip()
        start_time_str = request.form.get('start_time', '').strip()
        end_time_str = request.form.get('end_time', '').strip()
        event.description = request.form.get('description', '').strip()
        event.status = request.form.get('status', event.status)

        if event_date_str:
            event.event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
        if start_time_str:
            event.start_time = datetime.strptime(start_time_str, '%H:%M').time()
        if end_time_str:
            event.end_time = datetime.strptime(end_time_str, '%H:%M').time()
        else:
            event.end_time = None

        # Banner image upload commented out per UI requirement
        # if 'banner_image' in request.files:
        #     file = request.files['banner_image']
        #     if file and file.filename != '':
        #         filename = secure_filename(file.filename)
        #         ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        #         if ext in current_app.config['ALLOWED_EXTENSIONS']:
        #             new_filename = f"event_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
        #             upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'banners')
        #             os.makedirs(upload_path, exist_ok=True)
        #             file.save(os.path.join(upload_path, new_filename))
        #             event.banner_image = f"uploads/banners/{new_filename}"

        db.session.commit()
        flash(f'Event "{event.name}" updated successfully.', 'success')
        return redirect(url_for('events.detail', event_id=event.id))

    return render_template('events/edit.html', event=event)

@events_bp.route('/<int:event_id>/delete', methods=['POST'])
@login_required
@role_required('Administrator', 'Manager')
def delete(event_id):
    event = Event.query.get_or_404(event_id)
    event_name = event.name
    db.session.delete(event)
    db.session.commit()
    flash(f'Event "{event_name}" deleted successfully.', 'success')
    return redirect(url_for('events.index'))

