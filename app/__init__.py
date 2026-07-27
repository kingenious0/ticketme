"""
Application Factory for TicketMe Event Ticket Booking & Management System.
"""
import os
import click
from datetime import datetime, date
from flask import Flask, render_template
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from app.config import Config, config_by_name
from app.extensions import db, migrate, login_manager, csrf

def create_app(config_name=None):
    """
    Flask Application Factory.
    Initializes configuration, extensions, blueprints, error handlers, and CLI commands.
    """
    app = Flask(__name__)

    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app_config = config_by_name.get(config_name, Config)
    app.config.from_object(app_config)

    # Automatic Database Connection Health Check & Fallback to SQLite
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_uri.startswith('mysql'):
        try:
            test_engine = create_engine(db_uri, connect_args={'connect_timeout': 3})
            with test_engine.connect() as conn:
                pass
            test_engine.dispose()
        except OperationalError as e:
            sqlite_db_path = os.path.abspath(os.path.join(app.root_path, '..', 'instance', 'ticketme.db'))
            app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{sqlite_db_path}'
            app.logger.warning(
                f"MySQL connection failed ({e}). Falling back to SQLite: {app.config['SQLALCHEMY_DATABASE_URI']}"
            )

    # Ensure required directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.root_path, '..', 'instance'), exist_ok=True)

    # Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register Flask-Login user loader
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Context Processor for Global Settings
    from app.models.setting import Setting
    @app.context_processor
    def inject_settings():
        setting = Setting.query.first()
        if not setting:
            setting = Setting(business_name='TicketMe Events')
        return dict(system_setting=setting)

    # Register Blueprints
    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.users.routes import users_bp
    from app.customers.routes import customers_bp
    from app.events.routes import events_bp
    from app.ticket_types.routes import ticket_types_bp
    from app.bookings.routes import bookings_bp
    from app.payments.routes import payments_bp
    from app.tickets.routes import tickets_bp
    from app.verification.routes import verification_bp
    from app.reports.routes import reports_bp
    from app.settings.routes import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(ticket_types_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(verification_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500

    # CLI: seed admin command
    @app.cli.command("seed-admin")
    def seed_admin():
        """Seeds default administrator account."""
        db.create_all()
        admin_email = "admin@ticketme.com"
        existing = User.query.filter_by(email=admin_email).first()
        if not existing:
            admin = User(
                full_name="System Administrator",
                email=admin_email,
                phone_number="0200000000",
                role="Administrator",
                status="Active"
            )
            admin.set_password("Admin123!")
            db.session.add(admin)
            db.session.commit()
            click.echo(f"Created administrator: {admin_email} / Admin123!")
        else:
            click.echo(f"Administrator '{admin_email}' already exists.")

    # CLI: seed sample data command
    @app.cli.command("seed-data")
    def seed_data():
        """Seeds sample event, ticket types, customer, and settings."""
        db.create_all()
        from app.models.event import Event
        from app.models.ticket_type import TicketType
        from app.models.customer import Customer
        from app.models.setting import Setting

        if not Setting.query.first():
            s = Setting(
                business_name='TicketMe Events Ghana',
                business_phone='0201234567',
                business_email='contact@ticketme.com',
                business_address='Independence Square, Accra',
                currency='GHS',
                receipt_footer='Thank you for booking with TicketMe. Keep your ticket QR safe for entrance scanning!'
            )
            db.session.add(s)

        if not Event.query.first():
            ev = Event(
                name='Accra Music & Arts Festival 2026',
                venue='Independence Square, Accra',
                event_date=date(2026, 12, 24),
                start_time=datetime.strptime('18:00', '%H:%M').time(),
                end_time=datetime.strptime('23:59', '%H:%M').time(),
                description='Annual music celebration featuring live bands, food stalls, and cultural performances.',
                status='Upcoming'
            )
            db.session.add(ev)
            db.session.flush()

            tt1 = TicketType(event_id=ev.id, name='Regular', price=100.00, total_quantity=500, available_quantity=500, status='Active')
            tt2 = TicketType(event_id=ev.id, name='VIP', price=250.00, total_quantity=150, available_quantity=150, status='Active')
            tt3 = TicketType(event_id=ev.id, name='VVIP', price=500.00, total_quantity=50, available_quantity=50, status='Active')
            db.session.add_all([tt1, tt2, tt3])

        if not Customer.query.first():
            c = Customer(name='Kwame Mensah', phone_number='0244123456', email='kwame@example.com', notes='VIP attendee')
            db.session.add(c)

        db.session.commit()
        click.echo("Sample event data seeded successfully.")

    return app
