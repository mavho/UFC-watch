from flask import Flask, jsonify, abort, make_response, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from ufc_api import app, db
from UFC_stats_parse import UFC_Stats_Parser as UFCParser
import json
###
###Set up app, config url, parser, db, and migration
###

from predictions import Predictions

#configobj = ConfigURL()
parser = UFCParser()

@app.route('/API/v1/predictions',methods=['GET'])
def get_event_list():
    pm = Predictions()
    data = pm.predict() 
    return jsonify({'events': data})

@app.route('/hello', methods=['GET'])
def hello():
    return 'hello'