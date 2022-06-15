#activate_this = '/opt/PY_ENVS/UFC_ENV/bin/activate_this.py'
#with open(activate_this) as file_:
#	exec(file_.read(), dict(__file__=activate_this))
import sys
sys.path.append('/opt/PY_ENVS/UFC_ENV/lib/python3.8/site-packages/')
sys.path.append('/opt/PY_ENVS/UFC_ENV/lib64/python3.8/site-packages/')
sys.path.insert(0, '/opt/ufc-watch/UFC-API')
from ufc_api import app as application
