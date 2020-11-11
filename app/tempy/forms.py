from app.models import Reading, Sensor
from flask_wtf import FlaskForm
from wtforms.fields import (
    BooleanField, DateTimeField, DecimalField, HiddenField, IntegerField, StringField, SubmitField)
from wtforms.validators import DataRequired, NumberRange, ValidationError


class ReadingForm(FlaskForm):
    sensor_uuid = StringField("Sensor UUID", validators=[DataRequired()])
    timestamp = DateTimeField("Timestamp", validators=[DataRequired()])
    temperature = DecimalField("Temperature", validators=[DataRequired()])
    humidity = DecimalField("Humidity", validators=[DataRequired()])
    submit = SubmitField("Submit")

    def validate_sensor_uuid(self, sensor_uuid):
        sensor = Sensor.query.filter_by(uuid=sensor_uuid).first()
        if sensor is None:
            raise ValidationError("Invalid Sensor UUID")


class SensorForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    notify_active = BooleanField("Send alerts")
    min_temp = IntegerField("Min Temp", validators=[NumberRange(0, 212)])
    max_temp = IntegerField("Max Temp", validators=[NumberRange(0, 212)])
    min_humidity = IntegerField("Min Humidity", validators=[NumberRange(0, 100)])
    max_humidity = IntegerField("Max Humidity", validators=[NumberRange(0, 100)])
    submit = SubmitField("Submit")
