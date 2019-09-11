import json, sys
import urllib.request
from bs4 import BeautifulSoup
class UFCParser():
    #gets the raw bytes from the page
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

    #this gets the first event link within the event list
    def getLiveEvent(self,data):
        #get body class, and find the main class
        soup = BeautifulSoup(data, "lxml").find('body').find('main', {'class':'l-page__main'})
        #find the section and the group underneath it
        event_url = (soup.find('section', {'class':'l-listing--stacked'})).find('ul', {'class': 'l-listing__group'})
        #find the first item, and parse out the result section
        event_url = (event_url.find('li', {'class':'l-listing__item'})).find('article', {'class':'c-card-event--result'})
        #for listings in event_url.find_all('a', href=True):
        #    print(listings.encode('utf-8'))
        
        #print(event_url.encode('utf-8'))
        #return the first link
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



def main():
    parser = UFCParser()
    url = 'https://www.ufc.com/events'
    print('Get current fights test------------------')    
    data_bytes = parser.getRawHTML(url)
    result = parser.getLiveEvent(data_bytes)
    print(result)


if __name__ == '__main__':
    main()

