from datetime import datetime
from time import time
from uuid import uuid4

from sqlalchemy.ext.hybrid import hybrid_property

import jwt
from app import db, login_manager
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


def new_uuid():
    return str(uuid4())


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    sensors = db.relationship("Sensor", backref="user", lazy="dynamic")

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.email}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        ).decode("utf-8")

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token, current_app.config["SECRET_KEY"], altorighms=["HS256"]
            )["reset_password"]
        except:
            return
        return User.query.get(id)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, nullable=False)
    uuid = db.Column(db.String(36), index=True, unique=True, default=new_uuid)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    readings = db.relationship(
        "Reading", backref="sensor", lazy="dynamic", order_by="desc(Reading.timestamp)"
    )
    notify_active = db.Column(db.Boolean, index=True)
    max_temp = db.Column(db.Integer)
    min_temp = db.Column(db.Integer)
    max_humidity = db.Column(db.Integer)
    min_humidity = db.Column(db.Integer)
    last_seen = db.Column(db.DateTime)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id}>"

    def get_readings(self, key, start=None, end=None, limit=None):
        q = self.readings.filter_by(key=key)
        if start:
            q = q.filter(Reading.timestamp >= start)
        if end:
            q = q.filter(Reading.timestamp <= end)
        if limit:
            q = q.limit(limit)
        return q.all()


class Reading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey("sensor.id"))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    key = db.Column(db.String(200), index=True, nullable=False)
    value = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id} {self.key}={self.value}>"
