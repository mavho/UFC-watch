import json, sys, re, time, random
import urllib.request
from bs4 import BeautifulSoup
from flask import jsonify

import asyncio

from rotatingProxy.rotatingProxy import RotatingProxy

class UFCWebScraper():
    """
    Web crawler dedicated to the ufc stats events page ;)
    """

    def __init__(self,proxy_path):
        """
        Takes in plistfile, which is the location of the proxy_list.txt
        """
        self.r_proxy = RotatingProxy(proxy_path)


        self.events_all_url = 'http://ufcstats.com/statistics/events/completed?page=all'

        self.loop = asyncio.get_event_loop()
 
    def generate_url_list(self, data):
        """
        Given html data of the event list on the UFC website,
        generates a URL list of all the events and all their urls
        """
        soup = BeautifulSoup(data,'lxml') 
        payload = soup.find('table', {'class', 'b-statistics__table-events'})
        payload = payload.find_all('a', href=True)

        result = []
        for listing in payload:
            row = {}
            #listing['href']
            row['event'] = listing.get_text(strip=True)
            row['link'] = listing['href']
            result.append(row)
            #print(listing['href'] + ' ' + listing.get_text(strip=True))
        return result

    def parse_event_fights(self, data):
        """
        Returns a list with all of the fight stats of each bout
        """
        soup = BeautifulSoup(data, 'lxml')
        payload = soup.find('tbody', {'class', 'b-fight-details__table-body'})

        payload = payload.find_all('tr', {'class', 'b-fight-details__table-row'})
        
        fight_list = []
        for listing in payload:
            fight_list.append(self._parse_listing(listing))
           
        return fight_list
    
    def generate_event_bout_list(self,payload):
        """
        Returns a list with all of the fighter's names as a tuple
        [(Mcgregor, Diaz)]
        """
        soup = BeautifulSoup(payload, 'lxml')
        payload = soup.find('tbody', {'class', 'b-fight-details__table-body'})

        payload = payload.find_all('tr', {'class', 'b-fight-details__table-row'})
        
        fight_list = []
        for listing in payload:
            payload = listing.find_all('td')
            fighter_1 = payload[1].contents[1].get_text(strip=True)
            fighter_2 = payload[1].contents[3].get_text(strip=True)
            bout = (fighter_1,fighter_2)
            fight_list.append(bout)

        return fight_list
    
    def _parse_listing(self, data):
        """
        Parse the contents section of a td. Populates a json called fight_stats
        This looks at main bout info: Time, Round, Method, WeightClass, winner,loser, res

        Do not call this outside the file!
        """
        fight_stats = {}
        payload = data.find_all('td')
        fight_stats['Time'] = payload[9].get_text(strip=True)
        fight_stats['Round'] = payload[8].get_text(strip=True)
        fight_stats['Method'] = payload[7].get_text(strip=True)
        fight_stats['WeightClass'] = payload[6].get_text(strip=True)

        ### fighter name as string
        fighter_1 = payload[1].contents[1].get_text(strip=True)
        fighter_2 = payload[1].contents[3].get_text(strip=True)

        striking_json = {}
        striking_json2 = {}
        #now we populate striking,td,sub statistics
        fight_details_url = data['data-link']
        data_bytes = self.r_proxy.getRawHTML(fight_details_url)
        self._parse_striking_stats(data_bytes,fight_stats) 


        result = payload[0].get_text(strip=True)

        if result == 'win':
            fight_stats['Winner'] = fighter_1
            fight_stats['Loser'] = fighter_2
            fight_stats['Result'] = result 
        else:
            fight_stats['Winner'] = 'NA' 
            fight_stats['Loser'] = 'NA' 
            fight_stats['Result'] = result

        return fight_stats

    #given fight details, parse bout statistics    
    #New link so have to open another soup obj
    def _parse_striking_stats(self, data,fight_stats):
        """
        Parses striking statistics. Populates two json's
        """
        red_stats = {}
        blue_stats = {}

        soup = BeautifulSoup(data, 'lxml')
        table = soup.find('table')
        columns = table.find_all('td')

        red_fighter = columns[0].contents[1].get_text(strip=True)
        blue_fighter = columns[0].contents[3].get_text(strip=True)

        red_stats['fighter'] = red_fighter 
        blue_stats['fighter'] = blue_fighter        

        red_stats['KD'] = columns[1].contents[1].get_text(strip=True)
        blue_stats['KD'] = columns[1].contents[3].get_text(strip=True)

        red_stats['SIGSTR'] = re.sub(' of ', '/', columns[2].contents[1].get_text(strip=True))
        blue_stats['SIGSTR'] = re.sub(' of ', '/', columns[2].contents[3].get_text(strip=True))

        red_stats['SIGSTR_PRCT'] = columns[3].contents[1].get_text(strip=True)
        blue_stats['SIGSTR_PRCT'] = columns[3].contents[3].get_text(strip=True)

        red_stats['TTLSTR'] = re.sub(' of ', '/', columns[4].contents[1].get_text(strip=True))
        blue_stats['TTLSTR'] = re.sub(' of ', '/', columns[4].contents[3].get_text(strip=True))

        red_stats['TD'] = re.sub(' of ', '/', columns[5].contents[1].get_text(strip=True))
        blue_stats['TD'] = re.sub(' of ', '/',columns[5].contents[3].get_text(strip=True))

        red_stats['TD_PRCT'] = columns[6].contents[1].get_text(strip=True)
        blue_stats['TD_PRCT'] = columns[6].contents[3].get_text(strip=True)

        red_stats['SUB'] = columns[7].contents[1].get_text(strip=True)
        blue_stats['SUB'] = columns[7].contents[3].get_text(strip=True)

        red_stats['PASS'] = columns[8].contents[1].get_text(strip=True)
        blue_stats['PASS'] = columns[8].contents[3].get_text(strip=True)

        fight_stats['Red'] = red_stats
        fight_stats['Blue'] = blue_stats

def main():
    #url = 'http://www.ufcstats.com/statistics/events/completed?page=all'
    url = 'http://http://www.ufcstats.com/statistics/events/completed'
    parser = UFC_Stats_Parser()
    print('Get current fights test------------------')    


    #url = 'http://www.ufcstats.com/event-details/94a5aaf573f780ad'
    data_bytes = parser.getRawHTML(url)
    url_list = parser.generate_url_list(data_bytes)
    fight_list=parser.generate_event_bout_list(url_list[0])
    print(fight_list)




if __name__ == '__main__':
    main()
