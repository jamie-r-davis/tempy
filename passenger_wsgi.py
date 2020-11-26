import os
import subprocess
import sys

from tempy import app as application

INTERP = (
    subprocess.check_output(["pipenv", "run", "which", "python3"])
    .strip()
    .decode("utf-8")
)

if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.getcwd())


if __name__ == "__main__":
    application.run(debug=False)
