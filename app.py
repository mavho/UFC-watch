from flask import Flask, jsonify, abort, make_response, request, url_for
from bs4 import BeautifulSoup
import urllib.request

#need lxml parser for accurate results
    

class UFCParser():

    def getRawHTML(url):
        endpoint = urllib.request.urlopen(url) 
        mybytes = endpoint.read()
        endpoint.close()
        return mybytes

    #this gets the first event link within the event list
    #future funct: needs to determine whether or not it is live 
    #success boolean? maybe do check later on
    def getLiveEvent(data):
        soup = BeautifulSoup(data, "lxml")
        event_url = (soup.find('ul', {'class':'l-listing__group'})).find('li')
        return (event_url.find('a', href=True)['href'])


    #given raw_html of some event page, parse it
    def parseEvent(data):
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

                
            weight_class = (listing.find('div', {'class': 'c-listing-fight__class'}))
            end_stats = listing.find('div', {'class':'js-listing-fight__results'})

            fight['weight-class'] = weight_class.get_text(strip=True)
            fight['red-corner'] = red_name.get_text(strip=True)
            fight['blue-corner'] = blue_name.get_text(strip=True)
            fight['end_stats'] = end_stats.get_text(strip=True)
            #fight['data-fmid'] = listing['data-fmid']
            event_json.append(fight)

        return event_json

class ConfigURL:
    url = "https://www.ufc.com/events"


class API():
    app = Flask(__name__)

    @app.route('/ufc/api/v1.0/events/all', methods=['GET'])
    def get_live_event():
        #we start with the initial URL
        configobj = ConfigURL()
        raw_html = UFCParser.getRawHTML(configobj.url) 
        event = UFCParser.getLiveEvent(raw_html)
        live_html = UFCParser.getRawHTML("https://www.ufc.com/"+ event)
        live_results = UFCParser.parseEvent(live_html) 
        return jsonify({'fights': live_results})


    @app.errorhandler(404)
    def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)

    def run(self, debug=True, port=5000):
        self.app.run(port=port, debug=debug)


if __name__ == '__main__':
    app = API()
    app.run()