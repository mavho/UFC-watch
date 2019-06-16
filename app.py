from flask import Flask, jsonify, abort, make_response, request, url_for
from bs4 import BeautifulSoup
#import urllib.request
import json
import requests
import sys

#need lxml parser for accurate results
    

class UFCParser():

    #gets the raw bytes from the page
    def getRawHTML(self,url):
        #endpoint = urllib.request.urlopen(url) 
        endpoint = requests.get(url)
        #mybytes = endpoint.read()
        mybytes = endpoint.content
        endpoint.close()
        return mybytes

    #this gets the first event link within the event list
    #future funct: needs to determine whether or not it is live 
    #success boolean? maybe do check later on
    def getLiveEvent(self,data):
        soup = BeautifulSoup(data, "lxml")
        event_url = (soup.find('ul', {'class':'l-listing__group'})).find('li')
        return (event_url.find('a', href=True)['href'])

    #tries to find the live fight URL given an event listing.
    def findLiveFightURL(self, data):
        event_json = [] 
        soup = BeautifulSoup(data, "lxml")
        #find the live fight
        #open another page for it...
        for listing in soup.find_all('div', {'class':'c-listing-fight'}):
            print(listing['data-fmid'])
        return

    #helper method to insert time, round and method
    def endStats(self, data):
        end_stats = {}
        end_stats['Time'] = data.find('div', {'class':'c-listing-fight__result-text time'}).get_text()
        end_stats['Round'] = data.find('div', {'class':'c-listing-fight__result-text round'}).get_text()
        end_stats['Method'] = data.find('div', {'class':'c-listing-fight__result-text method'}).get_text()

        return end_stats

    #given raw_html of some event page, parse it
    def parseEvent(self, data):
        event_json = [] 
        soup = BeautifulSoup(data, "lxml")
        #this data to be parsed
        payload = soup.find_all('div', {'class':'c-listing-fight'})
        for listing in payload: 
            fight = {}

            red_fighter = listing.find('div', {'class':'c-listing-fight__corner--red'})
            blue_fighter = listing.find('div', {'class':'c-listing-fight__corner--blue'})

            red_name = red_fighter.find('div', {'class':'c-listing-fight__corner-name'})
            blue_name = blue_fighter.find('div', {'class':'c-listing-fight__corner-name'})

            if((red_fighter.find('div',{'class':'c-listing-fight__outcome-wrapper'})).get_text(strip=True) == 'Loss'):
                fight['Loser'] = red_name.get_text(strip=True)
                fight['Winner'] = blue_name.get_text(strip=True)
            elif((blue_fighter.find('div',{'class':'c-listing-fight__outcome-wrapper'})).get_text(strip=True) == 'Loss'):
                fight['Loser'] = blue_name.get_text(strip=True)
                fight['Winner'] = red_name.get_text(strip=True)
            else:
                fight['Loser'] = 'unknown'
                fight['Winner'] = 'unkown'
                
            weight_class = listing.find('div', {'class': 'c-listing-fight__class'})
            end_stats = listing.find('div', {'class':'js-listing-fight__results'})

            fight['end_stats'] = self.endStats(end_stats)
            fight['weight-class'] = weight_class.get_text(strip=True)
            fight['red-corner'] = red_name.get_text(strip=True)
            fight['blue-corner'] = blue_name.get_text(strip=True)
            event_json.append(fight)

        return event_json

    # steps, determine if bout is live.
    # extract data-fmid
    # ^^^^^^^^^^ may not occur here, currently just extracts based on page mentioned below
    # I guess we don't need to return a request, we just open one up here
    # This funct will be based on a url link like "/matchup/912/7762/post"
    # there is a post and pre, I have to see if it is something different when live
    def getLiveFightStats(self, data):
        event_json = [] 

        soup = BeautifulSoup(data, 'lxml')
        fightdata = soup.find_all('div', {'class':'c-listing-fight'})
        for listings in fightdata:
            event_json.append(listings['data-fmid'])

        #event_json.append(soup.find('div').get_text())

        return event_json


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
        #live_results = parser.liveFight(parser.getRawHTML(live_fight_url)) 
        return jsonify({'fights': 'none'})

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