from flask import Flask, jsonify, abort, make_response, request, url_for
from flask_cors import CORS
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
cors = CORS(app, resources={r'/winners':{"origins":"*"}})

#configobj = ConfigURL()
parser = UFCParser()

class PredictionsResource(Resource):
    def get(self):

        subprocess.call(['python','predictions.py'])
        with open('pred_fights.json') as jf:
            data = json.load(jf)
        return jsonify(data)



api.add_resource(PredictionsResource,'/winners')

if __name__ == "__main__":
    app.run(host="0.0.0.0")
