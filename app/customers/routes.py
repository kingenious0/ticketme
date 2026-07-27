"""
Customer Management Blueprint for TicketMe.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models.customer import Customer
from app.utils.decorators import role_required

customers_bp = Blueprint('customers', __name__, url_prefix='/customers')

@customers_bp.route('/')
@login_required
@role_required('Administrator', 'Manager', 'Ticket Officer')
def index():
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)

    query = Customer.query
    if search:
        query = query.filter(
            (Customer.name.ilike(f'%{search}%')) |
            (Customer.phone_number.ilike(f'%{search}%')) |
            (Customer.email.ilike(f'%{search}%'))
        )

    pagination = query.order_by(Customer.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    return render_template('customers/index.html', pagination=pagination, search=search)

@customers_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('Administrator', 'Manager', 'Ticket Officer')
def create():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone_number = request.form.get('phone_number', '').strip()
        email = request.form.get('email', '').strip()
        notes = request.form.get('notes', '').strip()

        if not name or not phone_number:
            flash('Customer Name and Phone Number are required.', 'warning')
            return redirect(url_for('customers.create'))

        customer = Customer(
            name=name,
            phone_number=phone_number,
            email=email if email else None,
            notes=notes if notes else None
        )
        db.session.add(customer)
        db.session.commit()

        flash(f'Customer "{name}" added successfully.', 'success')
        return redirect(url_for('customers.index'))

    return render_template('customers/create.html')

@customers_bp.route('/<int:customer_id>')
@login_required
@role_required('Administrator', 'Manager', 'Ticket Officer')
def detail(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return render_template('customers/detail.html', customer=customer)

@customers_bp.route('/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('Administrator', 'Manager', 'Ticket Officer')
def edit(customer_id):
    customer = Customer.query.get_or_404(customer_id)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone_number = request.form.get('phone_number', '').strip()
        email = request.form.get('email', '').strip()
        notes = request.form.get('notes', '').strip()

        if not name or not phone_number:
            flash('Customer Name and Phone Number are required.', 'warning')
            return redirect(url_for('customers.edit', customer_id=customer_id))

        customer.name = name
        customer.phone_number = phone_number
        customer.email = email if email else None
        customer.notes = notes if notes else None
        db.session.commit()

        flash(f'Customer "{name}" updated successfully.', 'success')
        return redirect(url_for('customers.detail', customer_id=customer.id))

    return render_template('customers/edit.html', customer=customer)

@customers_bp.route('/<int:customer_id>/delete', methods=['POST'])
@login_required
@role_required('Administrator', 'Manager')
def delete(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    name = customer.name
    db.session.delete(customer)
    db.session.commit()
    flash(f'Customer "{name}" deleted successfully.', 'success')
    return redirect(url_for('customers.index'))

