import json, sys
import urllib.request
from bs4 import BeautifulSoup
from flask import jsonify


class UFC_Stats_Parser():
    def getRawHTML(self,url):
        req = urllib.request.Request(
            url = url,
            data = None,
            headers = {
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
            } 
        )
        endpoint = urllib.request.urlopen(req) 
        #endpoint = request.get(url)
        mybytes = endpoint.read()
        #mybytes = endpoint.content
        endpoint.close()
        return mybytes
    
    def generate_url_list(self, data):
        soup = BeautifulSoup(data,'lxml') 
        payload = soup.find('table', {'class', 'b-statistics__table-events'})
        payload = payload.find_all('a', href=True)

        for listing in payload:
            print(listing['href'])

    def parse_event_list(self, data):
        soup = BeautifulSoup(data, 'lxml')
        payload = soup.find('table', {'class', 'b-statistics__table-events'})
        return payload

    #this is given an event page
    def parse_event_fights(self, data):
        soup = BeautifulSoup(data, 'lxml')
        payload = soup.find('tbody', {'class', 'b-fight-details__table-body'})

        payload = payload.find_all('tr', {'class', 'b-fight-details__table-row'})
        
        fight_list = []
        for listing in payload:
            fight_stats = {}
            self.parse_listing(listing, fight_stats)
            fight_list.append(fight_stats)

        return fight_list
    #parse the contents section of a td, populates fight_stats
    def parse_listing(self, data, fight_stats):
        payload = data.find_all('td')
        fight_stats['Time'] = payload[9].get_text(strip=True)
        fight_stats['Round'] = payload[8].get_text(strip=True)
        fight_stats['Method'] = payload[7].get_text(strip=True)
        fight_stats['WeightClass'] = payload[6].get_text(strip=True)
        fighter_1 = payload[1].contents[1].get_text(strip=True)
        fighter_2 = payload[1].contents[3].get_text(strip=True)
        striking_json = {}
        striking_json2 = {}
        striking_json['Strikes'] = payload[2].contents[1].get_text(strip=True)
        striking_json['TakeDown'] = payload[3].contents[1].get_text(strip=True)
        striking_json['SubAtt'] = payload[4].contents[1].get_text(strip=True)
        striking_json['PassGrd'] = payload[5].contents[1].get_text(strip=True)
        fight_stats[fighter_1] = striking_json
        striking_json2['Strikes'] = payload[2].contents[3].get_text(strip=True)
        striking_json2['TakeDown'] = payload[3].contents[3].get_text(strip=True)
        striking_json2['SubAtt'] = payload[4].contents[3].get_text(strip=True)
        striking_json2['PassGrd'] = payload[5].contents[3].get_text(strip=True)
        fight_stats[fighter_2] = striking_json2
        result = payload[0].get_text(strip=True)
        if result == 'win':
            fight_stats['Winner'] = fighter_1
            fight_stats['Loser'] = fighter_2
        else:
            fight_stats['Result'] = result

def main():
    url = 'http://www.ufcstats.com/statistics/events/completed?page=all'
    parser = UFC_Stats_Parser()
    print('Get current fights test------------------')    


    #url = 'http://www.ufcstats.com/event-details/94a5aaf573f780ad'
    data_bytes = parser.getRawHTML(url)
    #result = parser.parse_event_fights(data_bytes)
    result = parser.generate_url_list(data_bytes)
    print(result)


if __name__ == '__main__':
    main()