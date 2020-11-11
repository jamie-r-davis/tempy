import logging
import os
from logging.handlers import RotatingFileHandler, SMTPHandler

from app import filters
from config import Config
from flask import Flask, current_app, request
from flask_apscheduler import APScheduler
from flask_bs4 import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

boostrap = Bootstrap()
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please login to access this page."
mail = Mail()
scheduler = APScheduler()


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    boostrap.init_app(app)

    mail.init_app(app)

    scheduler.init_app(app)

    # register custom jinja filters
    app.jinja_env.filters["celsius"] = filters.celsius

    from app.errors import bp as errors_bp  # isort:skip

    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp  # isort:skip

    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.tempy import bp as tempy_bp  # isort:skip

    app.register_blueprint(tempy_bp)

    if not app.debug and not app.testing:
        if app.config["MAIL_SERVER"]:
            auth = None
            if app.config["MAIL_USERNAME"] or app.config["MAIL_PASSWORD"]:
                auth = (auth.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
            secure = None
            if app.config["MAIL_USE_SSL"]:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
                fromaddr="no-reply@" + app.config["MAIL_SERVER"],
                toaddrs=app.config["ADMINS"],
                subject="Tempy Failure",
                credentials=auth,
                secure=secure,
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHanlder(mail_handler)

        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler(
            "logs/tempy.log", maxBytes=10240, backupCount=10
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("Tempy startup")

    return app


from app import models, jobs  # isort:skip
