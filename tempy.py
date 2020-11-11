from app import create_app, db, scheduler
from app.models import Reading, Sensor, User
from config import Config

app = create_app(Config)
scheduler.add_job(
    "temp_check",
    "app.jobs:check_readings",
    kwargs={"key": "temperature"},
    trigger="interval",
    hours=3,
)
scheduler.add_job(
    "humidity_check",
    "app.jobs:check_readings",
    kwargs={"key": "humidity"},
    trigger="interval",
    hours=3,
)
scheduler.start()


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "User": User, "Sensor": Sensor, "Reading": Reading}
