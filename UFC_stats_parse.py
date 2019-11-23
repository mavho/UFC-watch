import json, sys, re, time, random
import urllib.request
from proxy import Proxy
from bs4 import BeautifulSoup
from flask import jsonify


class UFC_Stats_Parser():

    def __init__(self):
        self.working_proxy = ''
        self.proxy_list = []
        self.generateProxyList(self.proxy_list)
    
    def generateProxyList(self, proxy_list):
        fobj = open("proxy_list.txt", "r")
        for line in fobj:
            self.proxy_list.append(Proxy(line))


    #used to get the raw bytes from a webpage
    def getRawHTML(self,url):
        success=False
        for proxy in self.proxy_list[:]:
            proxy.generateHeader() 
            req = urllib.request.Request(
                url = url,
                data = None,
                headers = proxy.header,
            )
            authinfo = urllib.request.HTTPBasicAuthHandler()
            if self.working_proxy is not '':
                proxy_support = urllib.request.ProxyHandler({'http': self.working_proxy})
            else:
                proxy_support = urllib.request.ProxyHandler({'http': proxy.ip})
            opener = urllib.request.build_opener(proxy_support,authinfo,urllib.request.CacheFTPHandler)
            print('opener', flush=True)

            #urllib.request.install_opener(opener)
            try:
                endpoint = opener.open(req)
                #endpoint = urllib.request.urlopen(req) 
                mybytes = endpoint.read()
                endpoint.close()
                print('Able to open ' + proxy.ip,flush=True)
                self.working_proxy = proxy.ip
                success=True
                time.sleep(random.randrange(20))
                break
            except Exception as e:
                success=False
                print(e ,flush=True)
                self.working_proxy = ''
                #proxy_list.remove(proxy)
                time.sleep(random.randrange(20))
        #endpoint = request.get(url) #mybytes = endpoint.content
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
    
    #This returns a list of all the fighters
    def generate_event_bout_list(self,payload):
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
    
    #parse the contents section of a td, populates fight_stats
    #Do not call this!
    def parse_listing(self, data, fight_stats):
        #print(data['data-link'])
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
            fight_stats['Result'] = result 
        else:
            fight_stats['Winner'] = 'NA' 
            fight_stats['Loser'] = 'NA' 
            fight_stats['Result'] = result

    #given fight details, parse bout statistics    
    #New link so have to open another soup obj
    def parse_striking_stats(self, data,fight_stats,fighter1_stats, fighter2_stats):
        soup = BeautifulSoup(data, 'lxml')
        table = soup.find('table')
        columns = table.find_all('td')
        red_fighter = columns[0].contents[1].get_text(strip=True)
        blue_fighter = columns[0].contents[3].get_text(strip=True)

        fighter1_stats['fighter'] = red_fighter 
        fighter2_stats['fighter'] = blue_fighter        

        fighter1_stats['KD'] = columns[1].contents[1].get_text(strip=True)
        fighter2_stats['KD'] = columns[1].contents[3].get_text(strip=True)

        fighter1_stats['SIGSTR'] = re.sub(' of ', '/', columns[2].contents[1].get_text(strip=True))
        fighter2_stats['SIGSTR'] = re.sub(' of ', '/', columns[2].contents[3].get_text(strip=True))

        fighter1_stats['SIGSTR_PRCT'] = columns[3].contents[1].get_text(strip=True)
        fighter2_stats['SIGSTR_PRCT'] = columns[3].contents[3].get_text(strip=True)

        fighter1_stats['TTLSTR'] = re.sub(' of ', '/', columns[4].contents[1].get_text(strip=True))
        fighter2_stats['TTLSTR'] = re.sub(' of ', '/', columns[4].contents[3].get_text(strip=True))

        fighter1_stats['TD'] = re.sub(' of ', '/', columns[5].contents[1].get_text(strip=True))
        fighter2_stats['TD'] = re.sub(' of ', '/',columns[5].contents[3].get_text(strip=True))

        fighter1_stats['TD_PRCT'] = columns[6].contents[1].get_text(strip=True)
        fighter2_stats['TD_PRCT'] = columns[6].contents[3].get_text(strip=True)

        fighter1_stats['SUB'] = columns[7].contents[1].get_text(strip=True)
        fighter2_stats['SUB'] = columns[7].contents[3].get_text(strip=True)

        fighter1_stats['PASS'] = columns[8].contents[1].get_text(strip=True)
        fighter2_stats['PASS'] = columns[8].contents[3].get_text(strip=True)

        fight_stats['Red'] = fighter1_stats
        fight_stats['Blue'] = fighter2_stats



def main():
    #url = 'http://www.ufcstats.com/statistics/events/completed?page=all'
    url = 'http://http://www.ufcstats.com/statistics/events/completed'
    parser = UFC_Stats_Parser()
    print('Get current fights test------------------')    


    #url = 'http://www.ufcstats.com/event-details/94a5aaf573f780ad'
    data_bytes = parser.getRawHTML(url)
    url_list = parser.generate_url_list(data_bytes)
    fight_list=parser.generate_Event_Bout_list(url_list[0])
    print(fight_list)




if __name__ == '__main__':
    main()