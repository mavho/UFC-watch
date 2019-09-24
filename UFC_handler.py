from flask import Flask, jsonify, abort, make_response, request, url_for
from UFC_stats_parse import UFC_Stats_Parser as UFCParser
import json, sys

app = Flask(__name__)
class ConfigURL:
    stuff = "hello"
    def __init__(self):
        self.url = 'http://www.ufcstats.com/event-details/94a5aaf573f780ad'
        self.live_url = ""
    
    def alterLiveURL(self):
        self.live_url = "whatever"
        return self.live_url

configobj = ConfigURL()
parser = UFCParser()
class API():
    @app.route('/API/v1/events/list',methods=['GET'])
    def get_fights():
        data_bytes = parser.getRawHTML(configobj.url)
        result = parser.parse_event_fights(data_bytes) 
        return jsonify({'stats': result})

    def run(self, debug=True, port=5000):
        self.app.run(port=port, debug=debug)


if __name__ == '__main__':
    app = API()
    app.run()