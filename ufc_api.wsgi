activate_this = '/var/www/UFC_API/KENV/bin/activate_this.py'
with open(activate_this) as file_:
	exec(file_.read(), dict(__file__=activate_this))
import sys
sys.path.insert(0, '/var/www/UFC_API')
from ufc_api import app as application
