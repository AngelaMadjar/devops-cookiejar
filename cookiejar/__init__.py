from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from cookiejar import models  # models/__init__.py imports all model files

    from cookiejar.routes.tracker.tracker_routes import bp as tracker_bp
    from cookiejar.routes.vendor.vendor_routes import bp as vendor_bp
    from cookiejar.routes.database.database_routes import bp as db_bp
    from cookiejar.routes.meta.meta_routes import bp as meta_bp

    app.register_blueprint(tracker_bp)
    app.register_blueprint(vendor_bp)
    app.register_blueprint(db_bp)
    app.register_blueprint(meta_bp)

    db.init_app(app)
    migrate.init_app(app, db)

    # Creating db upon app creation for the sake of simplicity for this homework
    with app.app_context():
        db.create_all()

    return app
