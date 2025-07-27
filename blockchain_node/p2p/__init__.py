from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask import Flask

from p2p import config

migrate = Migrate()
csrf = CSRFProtect()
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    csrf.init_app(app)
    db.init_app(app)

    migrate.init_app(app, db, render_as_batch=True)

    # Model import
    from p2p import models

    # Blueprint import
    from p2p.views import main_views
    app.register_blueprint(main_views.bp)


    return app