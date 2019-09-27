import json, sys, re
import urllib.request
from bs4 import BeautifulSoup
from flask import jsonify


class UFC_Stats_Parser():
    #used to get the raw bytes from a webpage
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
    
    #returns a json from the events page of ufc_stats with query set to all.
    #json contains links and event names
    def generate_url_list(self, data):
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

    def parse_event_list(self, data):
        soup = BeautifulSoup(data, 'lxml')
        payload = soup.find('table', {'class', 'b-statistics__table-events'})
        return payload

    #this is given an event page
    #returns a json with the fight stats
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
    #Do not call this!
    def parse_listing(self, data, fight_stats):
        print(data['data-link'])
        payload = data.find_all('td')
        fight_stats['Time'] = payload[9].get_text(strip=True)
        fight_stats['Round'] = payload[8].get_text(strip=True)
        fight_stats['Method'] = payload[7].get_text(strip=True)
        fight_stats['WeightClass'] = payload[6].get_text(strip=True)
        fighter_1 = payload[1].contents[1].get_text(strip=True)
        fighter_2 = payload[1].contents[3].get_text(strip=True)
        striking_json = {}
        striking_json2 = {}
        #now we populate striking,td,sub statistics
        fight_details_url = data['data-link']
        data_bytes = self.getRawHTML(fight_details_url)
        self.parse_striking_stats(data_bytes,fight_stats,striking_json,striking_json2) 
        result = payload[0].get_text(strip=True)

        if result == 'win':
            fight_stats['Winner'] = fighter_1
            fight_stats['Loser'] = fighter_2
        else:
            fight_stats['Result'] = result

    #given fight details, parse bout statistics    
    def parse_striking_stats(self, data,fight_stats,fighter1_stats, fighter2_stats):
        soup = BeautifulSoup(data, 'lxml')
        table = soup.find('table')
        columns = table.find_all('td')
        red_fighter = columns[0].contents[1].get_text(strip=True)
        blue_fighter = columns[0].contents[3].get_text(strip=True)

        fighter1_stats['COLOR'] = 'red' 
        fighter2_stats['COLOR'] = 'blue'        

        fighter1_stats['KD'] = columns[1].contents[1].get_text(strip=True)
        fighter2_stats['KD'] = columns[1].contents[3].get_text(strip=True)

        fighter1_stats['SIGSTR'] = re.sub(' of ', '/', columns[2].contents[1].get_text(strip=True))
        fighter2_stats['SIGSTR'] = re.sub(' of ', '/', columns[2].contents[3].get_text(strip=True))

        fighter1_stats['SIGSTR_PRCT'] = columns[3].contents[1].get_text(strip=True)
        fighter2_stats['SIGSTR_PRCT'] = columns[3].contents[3].get_text(strip=True)

        fighter1_stats['TTLSTR'] = re.sub(' of ', '/', columns[4].contents[1].get_text(strip=True))
        fighter2_stats['TTLSTR'] = re.sub(' of ', '/', columns[4].contents[3].get_text(strip=True))

        fighter1_stats['TTLSTR_PRCT'] = columns[5].contents[1].get_text(strip=True)
        fighter2_stats['TTLSTR_PRCT'] = columns[5].contents[3].get_text(strip=True)

        fighter1_stats['TD'] = re.sub(' of ', '/', columns[6].contents[1].get_text(strip=True))
        fighter2_stats['TD'] = re.sub(' of ', '/',columns[6].contents[3].get_text(strip=True))

        fighter1_stats['TD_PRCT'] = columns[7].contents[1].get_text(strip=True)
        fighter2_stats['TD_PRCT'] = columns[7].contents[3].get_text(strip=True)


        fighter1_stats['SUB'] = columns[8].contents[1].get_text(strip=True)
        fighter2_stats['SUB'] = columns[8].contents[3].get_text(strip=True)

        fighter1_stats['PASS'] = columns[9].contents[1].get_text(strip=True)
        fighter2_stats['PASS'] = columns[9].contents[3].get_text(strip=True)

        fight_stats[red_fighter] = fighter1_stats
        fight_stats[blue_fighter] = fighter2_stats



def main():
    #url = 'http://www.ufcstats.com/statistics/events/completed?page=all'
    url = 'http://www.ufcstats.com/fight-details/357a34207d70da69'
    parser = UFC_Stats_Parser()
    print('Get current fights test------------------')    


    #url = 'http://www.ufcstats.com/event-details/94a5aaf573f780ad'
    data_bytes = parser.getRawHTML(url)
    #result = parser.parse_event_fights(data_bytes)
    #result = parser.generate_url_list(data_bytes)
    payload = {}
    j1 = {}
    j2 = {}
    parser.parse_striking_stats(data_bytes,payload,j1, j2)
    print(payload)


if __name__ == '__main__':
    main()