from flask import Flask, jsonify, abort, make_response, request, url_for
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config, DevConfig, ProdConfig
import os,sys, json

app = Flask(__name__)
app.config.from_object(Config)
if os.environ.get('FP_CONFIG',"DEV") == 'PROD':
    app.config.from_object(ProdConfig)
else:
    app.config.from_object(DevConfig)
api=Api(app)

db = SQLAlchemy(app)
migrate = Migrate(app,db) 
cors = CORS(app)
import models

class PredictionsResource(Resource):
    def get(self):
        print(app.config['HELLO'],file=sys.stderr)
        print(app.config['ROUTES']['basedir'],file=sys.stderr)
        print(app.config['HOST'],file=sys.stderr)
        #subprocess.call(['python3','predictions.py'])
        with open(app.config['ROUTES']['basedir'] + 'pred_fights.json') as jf:
            data = json.load(jf)
        return jsonify(data)

api.add_resource(PredictionsResource,'/winners')

class ConfigURL():
    """
    HOlds all the URLS needed to find the webpages, etc
    """
    def __init__(self):	
        #self.url = 'http://www.ufcstats.com/event-details/94a5aaf573f780ad'	
        self.completed_page_url = 'http://www.ufcstats.com/statistics/events/completed?page=all'	
        self.bout_url = 'http://www.ufcstats.com/event-details/a79bfbc01b2264d6'	
        self.live_url = ""	

    def alterLiveURL(self):	
        self.live_url = "whatever"	
        return self.live_url

if __name__ == '__main__':
    app.run(host=app.config['HOST'], debug=app.config['DEBUG'])
