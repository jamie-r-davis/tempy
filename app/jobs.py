from datetime import datetime, timedelta

from sqlalchemy import or_

from app import create_app, scheduler
from app.email import send_email
from app.models import Reading, Sensor, User
from flask import current_app, render_template

app = create_app()
app.app_context().push()


def count_to_ten():
    logger = app.logger
    logger.info("Counting to 10...")
    for i in range(1, 11):
        logger.info(i)


def send_test_email():
    subject = "Test Email"
    sender = "noreply@cellobarn.com"
    to = ["jamjam@umich.edu"]
    body = render_template("email/test.txt", sync=False)
    html = render_template("email/test.html", sync=False)
    send_email(subject, sender, to, text_body=body, html_body=html, sync=True)
    app.logger.info("email sent")


def send_warning_email(key, user, sensor, readings, min_value, max_value):
    subject = f"[CelloBarn] {key.title()} Notification"
    sender = "noreply@cellobarn.com"
    to = [user.email]
    body = render_template(
        "email/warning.txt", key=key, sensor=sensor, readings=readings, min_value=min_value, max_value=max_value
    )
    html = render_template(
        "email/warning.html", key=key, sensor=sensor, readings=readings, min_value=min_value, max_value=max_value
    )
    send_email(subject, sender, to, text_body=body, html_body=html, sync=True)


def check_readings(key):
    app.logger.info(f"Starting {key} check...")
    start = datetime.now() - timedelta(hours=3)
    sensors = Sensor.query.filter(Sensor.notify_active == True)
    for sensor in sensors:
        send = False
        user = User.query.get(sensor.user_id)
        readings = sensor.get_readings(key, start=start)
        min_value = min(x.value for x in readings)
        max_value = max(x.value for x in readings)
        if key == "humidity":
            if min_value < sensor.min_humidity or max_value > sensor.max_humidity:
                send = True
        if key == "temperature":
            if min_value < sensor.min_temp or max_value > sensor.max_temp:
                send = True
        if send:
            send_warning_email(key=key, user=user, sensor=sensor, readings=readings, min_value=min_value, max_value=max_value)
    app.logger.info(f"{key.title()} check complete")
