import json, sys, re, time, random
import urllib.request
from bs4 import BeautifulSoup
from flask import jsonify

from dataclasses import dataclass 
from typing import Set, Iterable, List, Tuple, Dict, Optional

import asyncio

from rotatingProxy.rotatingProxy import RotatingProxy

@dataclass
class TaskQueueMessage:
    url: str
    parent_url: str
    depth: int
    retry_count: int

class UFCWebScraper():
    """
    Web crawler dedicated to the ufc stats events page ;)
    """

    def __init__(self):
        """
        Takes in plistfile, which is the location of the proxy_list.txt
        """
        self.r_proxy = RotatingProxy()

        self.events_all_url = 'http://ufcstats.com/statistics/events/completed?page=all'

        self.crawled_urls = set() 

        self.concurrency = 20

        self.results = {}

        self.loop = asyncio.get_event_loop()

 
    async def crawl(self) -> None:
        ### crawl through the links.

        ### download the bytes needed to process the listing, 
        ### submit the task to worker threads, where they then process with beautiful soup, and commit to the DB.

        self.task_queue = asyncio.Queue()

        task_message = TaskQueueMessage(self.events_all_url,'', 0, 0)

        self.task_queue.put_nowait(task_message)

        print("Starting workers")
        workers = [asyncio.create_task(self.worker()) for i in range(self.concurrency)]

        print("Working")
        await self.task_queue.join()

        for w in workers:
            w.cancel()
        print("Finished")
            
        if self.r_proxy.session:
            await self.r_proxy.session.close()

    async def worker(self):
        """
        Gets a url from the task queue, and then crawls on the page.
        """
        while True:

            ### if queue is empty, leave
            if not self.task_queue:
                break

            ### get task
            task = await self.task_queue.get()
            
            ### If we've already seen this url, skip it. 
            if task.url in self.crawled_urls:
                self.task_queue.task_done()
                continue
                
            self.crawled_urls.add(task.url)

            ### crawl the page.
            try:
                url,links,html,data = await self.crawl_page(task.url,task.depth)
            except Exception as e:
                print("Ran into Exception")
                print(e)
            else:
                ### update results
                if task.depth == 0:
                    for it,event in enumerate(data):
                        self.results[event['link']] = event
                elif task.depth == 1:
                    self.results[task.url]['bouts'] = data
                elif task.depth == 2:
                    self.results[task.parent_url]['bouts'] = data
                        

                ### insert new links into the queue.
                for link in links.difference(self.crawled_urls):
                    task_message = TaskQueueMessage(link,task.url, task.depth + 1, 0)
                    await self.task_queue.put(task_message)
            finally:
                self.task_queue.task_done()

    async def crawl_page(self,url:str,depth:int) -> Tuple[str,Set[str],str,dict]:
        """
        Grabs a webpage and returns all data from it.

        Args:
            url (str): url as a string.

            depth (int): current depth we're at. Depth will also specify how we parse the html.
        Returns:
            Tuple[str,Set[str],str]: [description]
        """
        #print(url,depth)
        ### Depth 0 -> events_all_url page. What we do here is generate the url list.
        ### Depth 1 -> An events page with all the bouts.
        ### Depth 2 -> a Bouts page.

        if depth == 0:
            html = await self.r_proxy._make_request(url)
            links, data = self.parse_all_events_page(html)
        elif depth == 1:
            html = await self.r_proxy._make_request(url)
            links, data = self.parse_event_page(html)
        elif depth == 2:
            html = await self.r_proxy._make_request(url)
            links, data = self.parse_event_page(html)
            
        else:
            html = ''
            links = set()
            data = None

        return url,links,html,data

    def parse_all_events_page(self, data:str) -> Tuple[Set[str],List[str]]:
        """
        Given html data of the event list on the UFC website,

        generates a URL set of all the events and all their urls
        """
        soup = BeautifulSoup(data,'lxml') 
        payload = soup.find('table', {'class', 'b-statistics__table-events'})
        payload = payload.find_all('tr')

        links = set() 
        event_data = []
        for row in payload[3:4]:
            try:
                link_el = row.find('a',href=True)
                event_name = link_el.get_text(strip=True)
                link = link_el['href']
                links.add(link)

                date_el = row.find('span')
                date= date_el.get_text(strip=True)

                loc_el = row.find_all('td')[1]
                loc = loc_el.get_text(strip=True)
            except AttributeError as e:
                print("Unable to parse current row.")
                continue
            else:
                event_data.append(dict(link=link,name=event_name,date=date,locaction=loc))

        return links,event_data

    def parse_event_page(self, data:str) -> Tuple[List[str],List[dict]]:
        """
        Given html data of an event page.
        
        Create a listing of all fights.
        """
        soup = BeautifulSoup(data, 'lxml')
        payload = soup.find('tbody', {'class', 'b-fight-details__table-body'})

        payload = payload.find_all('tr', {'class', 'b-fight-details__table-row'})
        
        fight_list = []
        bout_links = []
        for it,listing in enumerate(payload):
            bout_stats,url = self._parse_listing(listing)
            ### this is the bout number
            #bout_stats['num'] = it
            fight_list.append(bout_stats)
        
            bout_links.append(url)
           

        return bout_links,fight_list
    
    def _parse_listing(self, data:str) -> Tuple[dict,str]:
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

        result = payload[0].get_text(strip=True)

        if result == 'win':
            fight_stats['Winner'] = fighter_1
            fight_stats['Loser'] = fighter_2
            fight_stats['Result'] = result 
        else:
            fight_stats['Winner'] = 'NA' 
            fight_stats['Loser'] = 'NA' 
            fight_stats['Result'] = result

        #now we populate striking,td,sub statistics
        #striking_json = {}
        #striking_json2 = {}
        fight_details_url = data['data-link']
        #data_bytes = self.r_proxy.getRawHTML(fight_details_url)
        #self._parse_striking_stats(data_bytes,fight_stats) 

        print(fight_stats)
        return fight_stats,fight_details_url

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
    
    async def get_results(self) -> List:
        await self.crawl()
        
        return self.results
        