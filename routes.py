from flask import Flask, jsonify, abort, make_response, request, url_for
from flask_restful import Resource, Api
#from flask_sqlalchemy import SQLAlchemy
#from flask_migrate import Migrate
#from config import Config
from ufc_api import app, db, api 
from UFC_stats_parse import UFC_Stats_Parser as UFCParser
import json
import subprocess
###
###Set up app, config url, parser, db, and migration
###

#from predictions import Predictions

#configobj = ConfigURL()
parser = UFCParser()

class PredictionsResource(Resource):
    def get(self):
        
        #data = trained_model.predict() 
        subprocess.call(['python3','predictions.py'])
        with open('/var/www/UFC_API/pred_fights.json') as jf:
            data = json.load(jf)
        return jsonify({'predicted wins': data, 'Event':'UFC Fight Night: Overeem vs. Rozenstruik'})
class Test(Resource):
    def get(self):
        return({'Hello':'World'})

api.add_resource(PredictionsResource,'/winners')
api.add_resource(Test, '/test')
if __name__ == "__main__":
    app.run(host="0.0.0.0")
