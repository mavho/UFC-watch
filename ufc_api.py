from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app,db) 
import routes, models

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