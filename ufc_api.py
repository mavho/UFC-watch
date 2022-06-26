from flask import Flask, jsonify, abort, make_response, request, url_for
from flask_restful import Resource, Api 
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from predictions.predictions import Predictions
from config import Config, DevConfig, ProdConfig
import os,sys, json,logging
from config_helpers import setup_logger

app = Flask(__name__)
app.config.from_object(Config)

if os.environ.get('FP_CONFIG',"DEV") == 'PROD':
    print("production")
    app.config.from_object(ProdConfig)
else:
    print("dev")
    app.config.from_object(DevConfig)

#User log
userformatter = logging.Formatter('%(asctime)s %(message)s')
app.logger= setup_logger('ufcwatch_api.log',userformatter, app.config['LOG_PATH'],level=logging.INFO)
app.logger.setLevel(logging.DEBUG)

app.debug = app.config['DEBUG']
api=Api(app)

db = SQLAlchemy(app)
migrate = Migrate(app,db) 
ma = Marshmallow(app)
cors = CORS(app)
from models import Bouts,Events,BoutSchema,EventSchema

class PredictionsResource(Resource):
    """
    for the predictions module
    """
    def get(self,event_id=None):
        if not event_id:
            with open(app.config['ROUTES']['basedir'] + '/pred_fights.json') as jf:
                data = json.load(jf)
            return make_response(jsonify(data), 200)

        msg = []
        if not isinstance(event_id, int):
            msg['Error'] = "Invalid event_id. Should be int"
            return make_response(msg,400)
        elif len(str(event_id)) >= 6:
            msg['Error'] = "Invalid event_id."
            return make_response(msg,400)

        PD = Predictions(db.get_engine())

        data = {'bouts':[]}
        rows = Bouts.query.filter_by(event_id=str(event_id)).all()
        for bout in rows:
            pred = PD.predict(red_fighter=bout.red_fighter,blue_fighter=bout.blue_fighter)
            data['bouts'].append(dict(
                prediction = pred['predictions'][0],
                actual = dict(winner=bout.winner,loser=bout.loser)
            ))

        event_schema = EventSchema()
        event = Events.query.filter_by(id=event_id).first()
        data['event'] = event_schema.dump(event)

        return make_response(jsonify(data), 200)


class EventResouce(Resource):
    """
    Get a specfic event
    """
    def get(self,event_id):
        msg = {}
        if not isinstance(event_id, int):
            msg['Error'] = "Invalid event_id. Should be int"
            return make_response(msg,400)
        elif len(str(event_id)) >= 6:
            msg['Error'] = "Invalid event_id."
            return make_response(msg,400)
        top_keys = set(['red_fighter','blue_fighter','winner','loser','result','time','method','end_round','event_id','blue_stats','red_stats'])
        bout_schema = BoutSchema(only=top_keys)
        event_schema = EventSchema()
        print("Recieved " + str(event_id), file=sys.stderr)
        rows = Bouts.query.filter_by(event_id=str(event_id)).all()
        event = Events.query.filter_by(id=event_id).first()
        msg['event'] = event_schema.dump(event)
        msg['bouts'] = []
        for bout in rows:
            #print(bout_schema.dump(bout),file=sys.stderr)
            msg['bouts'].append(bout_schema.dump(bout))
        return make_response(jsonify(msg),200)

class EventsResource(Resource):
    """
    Get all events with their corresponding id
    param: all gets all of the events, regardless if there are bouts available for them
    exist: only gets events that have bouts available
    """
    def get(self, param):
        msg = {}
        if not isinstance(param, str):
            msg['Error'] = "Invalid param. Should be string."
            return make_response(msg,400)
        elif len(param) >= 64:
            msg['Error'] = "Invalid param."
            return make_response(msg,400)
        

        event_schema = EventSchema()
        msg['events'] = []
        error_code = 200
        event_rows = Events.query.filter_by().all()
        if param == "all":
            for event in event_rows:
                msg['events'].append(event_schema.dump(event))
        else:
            msg['Error'] = "Invalid url, param needs to be all or existing."
            error_code = 400
            
        return make_response(jsonify(msg),error_code)

api.add_resource(PredictionsResource,'/predictions','/predictions/<int:event_id>')
api.add_resource(EventResouce,'/event/<int:event_id>')
api.add_resource(EventsResource,'/events/<string:param>')


@app.errorhandler(405)
def request_not_supported(e):
    return("this method is unsupported"), 405