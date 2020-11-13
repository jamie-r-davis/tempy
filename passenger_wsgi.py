import os
import subprocess
import sys

INTERP = subprocess.check_output(['pipenv', 'run', 'which', 'python3']).strip().decode('utf-8')

if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.getcwd())

from tempy import app as application


if __name__ == "__main__":
    application.run(debug=False)