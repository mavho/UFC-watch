from flask import Flask, jsonify, abort, make_response, request, url_for,render_template
from flask_restful import Resource, Api 
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from config import Config, DevConfig, ProdConfig
import os,sys, json

app = Flask(__name__)
app.config.from_object(Config)

if os.environ.get('FP_CONFIG',"PROD") == 'DEV':
    app.config.from_object(DevConfig)
else:
    app.config.from_object(ProdConfig)

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
    def get(self):
        with open(app.config['ROUTES']['basedir'] + 'pred_fights.json') as jf:
            data = json.load(jf)
        return make_response(jsonify(data), 200)


class EventResouce(Resource):
    """
    Get a specfic event
    """
    def get(self,event_id):
        msg = {}
        bout_schema = BoutSchema()
        event_schema = EventSchema()
        #print("Recieved " + str(event_id), file=sys.stderr)
        rows = Bouts.query.filter_by(event_id=str(event_id)).all()
        event = Events.query.filter_by(id=event_id).first()
        msg['event'] = event_schema.dump(event)
        msg['bouts'] = []
        for bout in rows:
            #print(bout_schema.dump(bout),file=sys.stderr)
            msg['bouts'].append(bout_schema.dump(bout))
        return msg, 200

class EventsResource(Resource):
    """
    Get all events with their corresponding id
    param: all gets all of the events, regardless if there are bouts available for them
    exist: only gets events that have bouts available
    """
    def get(self, param):
        msg = {}
        event_schema = EventSchema()
        msg['events'] = []
        event_rows = Events.query.filter_by().all()
        if param == "all":
            for event in event_rows:
                msg['events'].append(event_schema.dump(event))
        elif param == "existing":
            for event in event_rows:
                if Bouts.query.filter_by(event_id=event.id).first() != None:
                    msg['events'].append(event_schema.dump(event))
        return msg,200


class FrontEndResource(Resource):
    def get(self):
        headers = {'Content-Type':'text/html'}
        return make_response(render_template('_layouts/front_layout.html'),200,headers)

api.add_resource(PredictionsResource,'/api/predictions')
api.add_resource(EventResouce,'/api/event/<int:event_id>')
api.add_resource(EventsResource,'/api/events/<string:param>')
api.add_resource(FrontEndResource,'/web')

@app.errorhandler(405)
def request_not_supported(e):
    return("this method is unsupported"), 405
if __name__ == '__main__':
    app.run(host=app.config['HOST'], debug=app.config['DEBUG'])
