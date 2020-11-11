from datetime import datetime, timedelta

from app import db, scheduler
from app.email import send_email
from app.models import Reading, Sensor
from app.tempy import bp
from app.tempy.forms import SensorForm
from flask import (
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required


@bp.route("/")
def index():
    return redirect(url_for("tempy.dashboard"))


@bp.route("/count")
def count():
    scheduler.add_job(id="count", func="app.jobs:count_to_ten")
    return "OK"


@bp.route("/email")
def email():
    scheduler.add_job(id="test_email", func="app.jobs:send_test_email")
    return "OK"


@bp.route("/dashboard")
def dashboard():
    sensor = Sensor.query.first()
    start_dt = datetime.now() - timedelta(hours=24)
    temp_readings = sensor.get_readings("temperature", start=start_dt)
    humidity_readings = sensor.get_readings("humidity", start=start_dt)
    return render_template(
        "tempy/dashboard.html",
        sensors=sensor,
        temp_readings=temp_readings,
        humidity_readings=humidity_readings,
    )


@bp.route("/sensors")
def sensor_list():
    sensors = Sensor.query.all()
    return render_template("tempy/sensor_list.html", sensors=sensors)


@bp.route("/sensors/<sensor_id>")
def sensor_detail(sensor_id):
    start_dt = datetime.now() - timedelta(hours=3)
    end_dt = datetime.now()
    if "start" in request.args:
        start_dt = datetime.strptime(request.args.get("start"), "%Y%m%d%H%M%S")
    if "end" in request.args:
        end_dt = datetime.strptime(request.args.get("end"), "%Y%m%d%H%M%S")
    sensor = Sensor.query.filter_by(id=sensor_id).first()
    temp_readings = sensor.get_readings("temperature", start=start_dt, end=end_dt)
    humidity_readings = sensor.get_readings("humidity", start=start_dt, end=end_dt)
    return render_template(
        "tempy/sensor_detail.html",
        sensor=sensor,
        temp_readings=temp_readings,
        humidity_readings=humidity_readings,
    )


@bp.route("/sensor", methods=["GET", "POST"])
@login_required
def add_sensor():
    form = SensorForm()
    if form.validate_on_submit():
        sensor = Sensor(name=form.name.data, user_id=current_user.id)
        sensor.notify_active = form.notify_active.data
        sensor.min_temp = form.min_temp.data
        sensor.max_temp = form.max_temp.data
        sensor.min_humidity = form.min_humidity.data
        sensor.max_humidity = form.max_humidity.data
        db.session.add(sensor)
        db.session.commit()
        flash(f"New sensor added: {sensor.name}")
        return redirect(url_for("tempy.dashboard"))
    return render_template(
        "tempy/add_sensor.html", title="Add a Sensor", form=form, update=False
    )


@bp.route("/sensors/<sensor_id>/edit", methods=["GET", "POST"])
@login_required
def edit_sensor(sensor_id):
    sensor = Sensor.query.filter_by(id=sensor_id).first_or_404()
    if sensor.user_id != current_user.id:
        abort(404)
    form = SensorForm(obj=sensor)
    if form.validate_on_submit():
        sensor.name = form.name.data
        sensor.notify_active = form.notify_active.data
        sensor.min_temp = form.min_temp.data
        sensor.max_temp = form.max_temp.data
        sensor.min_humidity = form.min_humidity.data
        sensor.max_humidity = form.max_humidity.data
        db.session.commit()
        flash(f"{sensor.name} updated!")
        return redirect(url_for("tempy.sensor_detail", sensor_id=sensor.id))
    return render_template(
        "tempy/add_sensor.html", title="Update Sensor", form=form, update=True
    )


@bp.route("/api/v1/readings", methods=["POST"])
def create_reading():
    if not request.json or not "sensor" in request.json:
        abort(400)
    try:
        sensor = Sensor.query.filter_by(uuid=request.json["sensor"]).first_or_404()
        temperature = float(request.json["temperature"])
        humidity = float(request.json["humidity"])
    except (KeyError, ValueError):
        abort(404, "Invalid sensor.")
    temp_reading = Reading(sensor_id=sensor.id, key="temperature", value=temperature)
    humidity_reading = Reading(sensor_id=sensor.id, key="humidity", value=humidity)
    sensor.last_seen = datetime.now()
    db.session.add(temp_reading)
    db.session.add(humidity_reading)
    db.session.commit()
    return (
        jsonify({"status": 201}),
        201,
    )


@bp.route("/api/v1/readings", methods=["GET"])
def get_readings():
    sensor_id = request.args["sensor"]
    key = request.args["key"]
    start = request.args.get("start")
    if start:
        start = datetime.fromisoformat(start)
    end = request.args.get("end")
    if end:
        end = datetime.fromisoformat(end)
    sensor = Sensor.query.get(sensor_id)
    readings = sensor.get_readings(key, start=start, end=end)
    serialized_readings = [
        {"timestamp": reading.timestamp.isoformat(), "value": reading.value}
        for reading in readings
    ]
    return {"sensor": sensor.id, "readings": serialized_readings}


@bp.route('/check')
def check():
    scheduler.run_job('temp_check')
    scheduler.run_job('humidity_check')
    return 'OK'
