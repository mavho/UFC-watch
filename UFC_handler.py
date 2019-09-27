from flask import Flask, jsonify, abort, make_response, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from UFC_stats_parse import UFC_Stats_Parser as UFCParser
import json
###
###Set up app, config url, parser, db, and migration
###

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app,db) 

from models import Events
class ConfigURL():
    stuff = "hello"
    def __init__(self):
        #self.url = 'http://www.ufcstats.com/event-details/94a5aaf573f780ad'
        self.url = 'http://www.ufcstats.com/statistics/events/completed?page=all'
        self.bout_url = 'http://www.ufcstats.com/event-details/a79bfbc01b2264d6'
        self.live_url = ""
    
    def alterLiveURL(self):
        self.live_url = "whatever"
        return self.live_url

configobj = ConfigURL()
parser = UFCParser()
class API():
    @staticmethod
    @app.route('/API/v1/events/list',methods=['GET'])
    def get_event_list():
        data_bytes = parser.getRawHTML(configobj.url)
        result = parser.generate_url_list(data_bytes)
        e = Events(event='Jesus Walks') 
        db.session.add(e)
        db.session.commit()
        return jsonify({'events': result})

    def run(self, debug=True, port=5000):
        self.app.run(port=port, debug=debug)


if __name__ == '__main__':
    app = API()
    app.run()