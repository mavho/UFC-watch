from flask import Flask, jsonify, abort, make_response, request, url_for
from bs4 import BeautifulSoup
from UFC_stats_parse import UFC_Stats_Parser as UFCParser
#import urllib.request
import json
import requests
import sys

#need lxml parser for accurate results
class ConfigURL:
    stuff = "hello"
    def __init__(self):
        self.event_page_url = "https://www.ufc.com/events"
        self.live_url = ""
    
    def alterLiveURL(self):
        self.live_url = "whatever"
        return self.live_url

configobj = ConfigURL()

app = Flask(__name__)

class API():

    @app.route('/ufc/api/v1.0/events/PenaVPeterson', methods=['GET'])
    def get_fight_stats():
        parser = UFCParser()
        raw_html = parser.getRawHTML('https://www.ufc.com/matchup/912/7762/post')
        stats = parser.getLiveFightStats(raw_html)
        return jsonify({'stats': stats})

    #hopefully find the live fight, and give statistics on it.
    @app.route('/ufc/api/v1.0/live_events/current', methods=['GET'])
    def get_live_fight():
        configobj = ConfigURL()
        parser = UFCParser()
        raw_html = parser.getRawHTML(configobj.event_page_url) 

        event = parser.getLiveEvent(raw_html)
        live_html = parser.getRawHTML("https://www.ufc.com/"+ event)
        live_fight_url = parser.getliveFightURL(live_html) 
        live_results = parser.liveFight(parser.getRawHTML(live_fight_url)) 
        return jsonify({'fights': live_results})

    #blanket command, get all the fights on the current card
    @app.route('/ufc/api/v1.0/live_events/all', methods=['GET'])
    def get_all_events():
        #we start with the initial URL
        configobj = ConfigURL()
        parser = UFCParser()
        raw_html = parser.getRawHTML(configobj.event_page_url) 
        event = parser.getLiveEvent(raw_html)

        live_html = parser.getRawHTML("https://www.ufc.com/"+ event)
        live_results = parser.parseEvent(live_html) 
        return jsonify({'fights': live_results})



    #Section if given a current working link"
    #Though this api is for getting the live events automatically, I thought it would be a good
    #idea, of when specified an event page, I'm able to parse it hopefully. 
    #user will type part of the link into the curl url
    #This also reduces the two or three requests needed to find the live event/fight

    #format goes like /ufc/api/v1.0/ufc-fight-night-march-30-2019/all
    #gets the basic bout information on everything
    @app.route('/ufc/api/v1.0/<link>/all', methods=['GET'])
    def get_specified_events(link):
        parser = UFCParser()
        try:
            live_html = parser.getRawHTML("https://www.ufc.com/event/"+ link )
        except:
            abort(404)
        live_results = parser.parseEvent(live_html) 
        return jsonify({'fights': live_results})

    #format goes like /ufc/api/v1.0/ufc-fight-night-march-30-2019/current
    #this gets the live fight stats if there is one, else return not happening or something
    @app.route('/ufc/api/v1.0/<link>/current', methods=['GET'])
    def get_specified_event(link):
        parser = UFCParser()
        try:
            live_html = parser.getRawHTML("https://www.ufc.com/event/"+ link )
        except:
            abort(404)
        live_results = parser.getLiveFightStats(live_html) 
        return jsonify({'fights': live_results})

    #catch an error, most likely given from a wrong link
    @app.errorhandler(404)
    def page_not_found(e):
        response = jsonify({'status': 404,'error': 'not found',
                        'message': 'invalid resource URI'})
        response.status_code = 404
        return response

    def run(self, debug=True, port=5000):
        self.app.run(port=port, debug=debug)


if __name__ == '__main__':
    app = API()
    app.run()