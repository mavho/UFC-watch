from flask import Flask, jsonify, abort, make_response, request, url_for
from bs4 import BeautifulSoup
import urllib.request
import sys

#need lxml parser for accurate results
    

class UFCParser():

    def getRawHTML(self,url):
        endpoint = urllib.request.urlopen(url) 
        mybytes = endpoint.read()
        endpoint.close()
        return mybytes

    #this gets the first event link within the event list
    #future funct: needs to determine whether or not it is live 
    #success boolean? maybe do check later on
    def getLiveEvent(self,data):
        soup = BeautifulSoup(data, "lxml")
        event_url = (soup.find('ul', {'class':'l-listing__group'})).find('li')
        return (event_url.find('a', href=True)['href'])

    def getliveFightURL(self, data):
        event_json = [] 
        soup = BeautifulSoup(data, "lxml")
        #find the live fight
        #open another page for it...
        for listing in soup.find_all('div', {'class':'c-listing-fight'}):
            print(listing['data-fmid'])
        return
    def dumpStats(self, data):
        end_stats = {}
        end_stats['Time'] = data.find('div', {'class':'c-listing-fight__result-text time'}).get_text()
        end_stats['Round'] = data.find('div', {'class':'c-listing-fight__result-text round'}).get_text()
        end_stats['Method'] = data.find('div', {'class':'c-listing-fight__result-text method'}).get_text()

        return end_stats
    #given raw_html of some event page, parse it
    def parseEvent(self, data):
        event_json = [] 
        soup = BeautifulSoup(data, "lxml")

        for listing in soup.find_all('div', {'class':'c-listing-fight'}):
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

            fight['end_stats'] = self.dumpStats(end_stats)
            fight['weight-class'] = weight_class.get_text(strip=True)
            fight['red-corner'] = red_name.get_text(strip=True)
            fight['blue-corner'] = blue_name.get_text(strip=True)
            event_json.append(fight)

        return event_json
    
    def getLiveFightStats(self, data):
        event_json = [] 

        soup = BeautifulSoup(data, 'lxml')
        fightdata = soup.find_all('div', {'class': ''})
        print('poopoop', file=sys.stderr)
        for listings in fightdata:
            print('poopoop', file=sys.stderr)
            print(listings.get_text(),file=sys.stderr)

        event_json.append(soup.find('div').get_text())

        return event_json


class ConfigURL:
    def __init__(self):
        self.event_page_url = "https://www.ufc.com/events"
        self.live_url = ""
    
    def alterLiveURL(self):
        self.live_url = "whatever"
        return self.live_url


class API():
    app = Flask(__name__)

    @app.route('/ufc/api/v1.0/event/current', methods=['GET'])
    def thomposVpettis():
        parser = UFCParser()
        html = parser.getRawHTML('https://www.ufc.com/matchup/912/7698/post')
        data = parser.getLiveFightStats(html)
        return jsonify({'fight': data}) 

    @app.route('/ufc/api/v1.0/events/current', methods=['GET'])
    def get_live_fight():
        configobj = ConfigURL()
        parser = UFCParser()
        raw_html = parser.getRawHTML(configobj.event_page_url) 

        event = parser.getLiveEvent(raw_html)

        live_html = parser.getRawHTML("https://www.ufc.com/"+ event)
        live_fight_url = parser.getliveFightURL(live_html) 
        #live_results = parser.liveFight(parser.getRawHTML(live_fight_url)) 
        return jsonify({'fights': 'none'})

    @app.route('/ufc/api/v1.0/events/all', methods=['GET'])
    def get_all_events():
        #we start with the initial URL
        configobj = ConfigURL()
        parser = UFCParser()
        raw_html = parser.getRawHTML(configobj.event_page_url) 
        event = parser.getLiveEvent(raw_html)

        live_html = parser.getRawHTML("https://www.ufc.com/"+ event)
        live_results = parser.parseEvent(live_html) 
        return jsonify({'fights': live_results})


    @app.errorhandler(404)
    def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)

    def run(self, debug=True, port=5000):
        self.app.run(port=port, debug=debug)


if __name__ == '__main__':
    app = API()
    app.run()