from bs4 import BeautifulSoup
import random
import pickle
import time

from dataclasses import dataclass 
from typing import Set, Iterable, List, Tuple, Dict, Optional

import asyncio, re
import traceback

from rotatingProxy.rotatingProxy import RotatingProxy

@dataclass
class TaskQueueMessage:
    """
    Represents a Task for the async Queue.
    """
    url: str
    parent_url: str
    depth: int
    retry_count: int

@dataclass
class FighterStats:
    """_summary_
    fighter: fighter name
    CNTRL_SEC: is control time in seconds
    """
    fighter:str
    KD:int
    SIGSTR_LAND:int
    SIGSTR_TTL:int
    TTLSTR_LAND:int
    TTLSTR_TTL:int
    TD_LAND:int
    TD_TTL:int
    SUB:int
    REV:int
    CNTRL_SEC:int
    
class RetryException(Exception):
    pass

class UFCWebScraper():
    """
    Web crawler dedicated to the ufc stats events page ;)
    """
    pickled_queue_file = "scrape_q.pickle"
    pickled_failed_tasks_file = "failed_tasks.pickle"
    def __init__(self, concurrency=20,start=0,end=None,proxy_list:List[str]=None):
        """
        concurrency (int) -> Int to specify how many workers.\n
        Takes in listfile, which is the location of the proxy_list.txt
        """
        self.r_proxies = [
            RotatingProxy(proxy_list=proxy_list),
            RotatingProxy(proxy_list=proxy_list),
            RotatingProxy(proxy_list=proxy_list),
            RotatingProxy(proxy_list=proxy_list),
        ]
        # self.r_proxy = RotatingProxy(proxy_list=proxy_list)

        ### Base events URL that contains all UFC events.
        self.events_all_url = 'http://ufcstats.com/statistics/events/completed?page=all'

        self.crawled_urls = set() 

        self.concurrency = concurrency
        ### Start and end.
        self.start=start
        if end:
            self.end = end

        ### Result Dictionary.
        self.results = {}

        self.failed_urls:List[TaskQueueMessage] = []

        self.loop=None
        self.task_queue :asyncio.Queue[TaskQueueMessage] = asyncio.Queue()

    def pickle_queue(self):
        """_summary_
        Saves the current task queue into a pickle file as a list.
        
        This queue can be used to replay the past parsed url's.
        """

        print(f"Saving task queue with {self.task_queue.qsize()} items into {self.pickled_queue_file}")
        with open(self.pickled_queue_file,'wb+') as f:

            q_list = []
            while self.task_queue:
                try:
                    task = self.task_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
                q_list.append(task)
            pickle.dump(q_list,f)

    def pickle_failed_tasks(self):
        """_summary_
        Saves the current task queue into a pickle file as a list.
        
        This queue can be used to replay the past parsed url's.
        """

        if len(self.failed_urls) == 0:
            print("No failed urls recorded.")
            return

        print(f"Saving failed tasks with {len(self.failed_urls)} items into {self.pickled_failed_tasks_file}")
        with open(self.pickled_failed_tasks_file,'wb+') as f:
            q_list = []
            for task in self.failed_urls:
                q_list.append(task)
            pickle.dump(q_list,f)

    def load_queue(self):
        """_summary_
        Loads the pickled file into a queue.
        
        This queue can be used to replay the past parsed url's.
        """
        with open(self.pickled_queue_file,'rb') as f:

            q_list = pickle.load(f)
            for task in q_list:
                print(f"Putting {task.url} at depth {task.depth} in Q.")
                self.task_queue.put_nowait(task)

    def load_failed_queue(self):
        """_summary_
        Loads the pickled file into a queue.
        
        This queue can be used to replay the past parsed url's.
        """
        with open(self.pickled_failed_tasks_file,'rb') as f:

            q_list = pickle.load(f)
            for task in q_list:
                print(f"Putting failed {task.url} at depth {task.depth} in Q.")
                self.task_queue.put_nowait(task)
 
    async def crawl(self) -> None:
        """
        Starts concurrent workers, and starts scrapping.
        """
        print("Starting workers")
        workers = [asyncio.create_task(self.worker()) for _ in range(self.concurrency)]

        try:
            await self.task_queue.join()

            for w in workers:
                w.cancel()
            print("Finished")
        finally:
            for proxy in self.r_proxies:
                await proxy.session.close()
            # if self.r_proxy.session:
            #     await self.r_proxy.session.close()

            self.pickle_failed_tasks()

    async def worker(self) -> None:
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
                
            print(f"Q size: {self.task_queue.qsize()}")

            ### crawl the page.
            try:
                url,links,html,data = await self.crawl_page(task.url,task.depth)
            except RetryException:
                ### retry the task
                # if task.retry_count == 10:
                #     print(f"{task.url} Ran into Exception")
                #     self.failed_urls.append(task)
                # else:
                print(f"{task.url} retrying")
                task.retry_count += 1
                await self.task_queue.put(task)

            except Exception as e:
                print("#######################")
                print(f"{task.url} Ran into Exception")
                print(traceback.format_exc())
                print("#######################")
                self.failed_urls.append(task)
            else:
                ### update results based on depth.
                ### results will be hashed by links

                self.crawled_urls.add(task.url)
                
                if task.depth == 0:
                    ### This depth inserts every event detail into results. Set key to event link
                    for it,event in enumerate(data):
                        self.results[event['link']] = event
                elif task.depth == 1:
                    ### Next depth inserts overall bout statistics to the corresponding event URL.
                    ### Data here is a dictionary hashed by FIGHT URL.
                    self.results[url]['bouts'] = data
                elif task.depth == 2:
                    ### This depth inserts fighting statistics to the corresponding FIGHT URL.
                    ### parent url in this case is event URL.
                    self.results[task.parent_url]['bouts'][url].update(data)
                        
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
        ### Depth 0 -> events_all_url page. What we do here is generate the url list.
        ### Depth 1 -> An events page with all the bouts.
        ### Depth 2 -> a Bouts page.

        print(url,depth)


        if not self.loop:
            self.loop = asyncio.get_event_loop()

        if depth == 0:
            await asyncio.sleep(random.randrange(0,3))
            t = time.perf_counter()
            proxy = random.choice(self.r_proxies)
            html = await proxy._make_request(url)

            # html = await self.r_proxy._make_request(url)

            if html is None:
                print(f"Req failed at {time.perf_counter() - t}")
                raise RetryException(f'{url} failed, retry')
            print(f"Req done at {time.perf_counter() - t}")
            ### links -> a set of all event URLs that need to be scrapped in depth 1.
            ### data -> List of general event information. dict(link,location,name,date)
            # links, data = self.parse_all_events_page(html)

            # links, data = await asyncio.to_thread(self.parse_all_events_page(html))
            links, data = await self.loop.run_in_executor(
                None,
                self.parse_all_events_page,
                html
            )
        elif depth == 1:
            await asyncio.sleep(random.randrange(0,6))
            # html = await self.r_proxy._make_request(url)
            t = time.perf_counter()
            proxy = random.choice(self.r_proxies)
            html = await proxy._make_request(url)
            # html = await self.r_proxy._make_request(url)
            if html is None:
                print(f"Req failed at {time.perf_counter() - t}")
                raise RetryException(f'{url} failed, retry')
            print(f"Req done at {time.perf_counter() - t}")
            ### links -> a set of all BOUT URLs that need to be scrapped in depth 2
            ### data (dict) -> Data on all bouts that contain general bout info.
            ### Data is hashed by the particular BOUT URL
            # links, data = self.parse_event_page(html)
            # links, data = await asyncio.to_thread(self.parse_event_page(html))
            links, data = await self.loop.run_in_executor(
                None,
                self.parse_event_page,
                html
            )
        elif depth == 2:
            await asyncio.sleep(random.randrange(0,5))
            # html = await self.r_proxy._make_request(url)
            t = time.perf_counter()

            proxy = random.choice(self.r_proxies)
            html = await proxy._make_request(url)
            # html = await self.r_proxy._make_request(url)

            if html is None:
                print(f"Req failed at {time.perf_counter() - t}")
                raise RetryException(f'{url} failed, retry')
            print(f"Req done at {time.perf_counter() - t}")
            ### data -> Fight stastics on a particular bout

            data = await self.loop.run_in_executor(
                None,
                self._parse_striking_stats,
                html
            )
            links = set()
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
        if isinstance(data,bytes):
            data = data.decode()
        soup = BeautifulSoup(data,'lxml') 
        payload = soup.find('table', {'class', 'b-statistics__table-events'})
        payload = payload.find_all('tr')

        event_links = set() 
        event_data = []
        for row in payload[self.start:self.end]:
            try:
                ### Grab href and anchor text.
                link_el = row.find('a',href=True)
                event_name = link_el.get_text(strip=True)
                link = link_el['href']
                event_links.add(link)

                ### grab date
                date_el = row.find('span')
                date= date_el.get_text(strip=True)

                ### grab location
                loc_el = row.find_all('td')[1]
                loc = loc_el.get_text(strip=True)
            except AttributeError:
                print("Unable to parse current row.")
                continue
            else:
                event_data.append(dict(link=link,name=event_name,date=date,location=loc))

        return event_links,event_data

    def parse_event_page(self, data:str) -> Tuple[Set[str],List[dict]]:
        """
        Given html data of an event page.
        
        Create a listing of all fights.
        """
        if isinstance(data,bytes):
            data = data.decode()
        soup = BeautifulSoup(data, 'lxml')
        payload = soup.find('tbody', {'class', 'b-fight-details__table-body'})

        payload = payload.find_all('tr', {'class', 'b-fight-details__table-row'})
        
        fight_dict = {} 
        bout_links = set() 
        for listing in payload:
            ### populate general bout information
            url,bout_stats = self._parse_listing(listing)
            fight_dict[url] = bout_stats
        
            bout_links.add(url)

        return bout_links,fight_dict
    
    def _parse_listing(self, data:str) -> Tuple[str,dict]:
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
        fight_stats['r_fighter'] = fighter_1
        fight_stats['b_fighter'] = fighter_2

        if result == 'win':
            fight_stats['Winner'] = fighter_1
            fight_stats['Loser'] = fighter_2
            fight_stats['Result'] = result 
        else:
            fight_stats['Winner'] = 'NA' 
            fight_stats['Loser'] = 'NA' 
            fight_stats['Result'] = result

        fight_details_url = data['data-link']

        return fight_details_url,fight_stats

    def _parse_striking_stats(self, data:str) -> Dict[str,FighterStats]:
        """
        Parses striking statistics from a data HTML

        Returns a Dict with {
            'Red': FighterStats,
            'Blue': FighterStats
        }
        """
        if isinstance(data,bytes):
            data = data.decode()
        fight_stats = {}

        soup = BeautifulSoup(data, 'lxml')
        table = soup.find('table')
        columns = table.find_all('td')
        
        red_fighter = columns[0].contents[1].get_text(strip=True)


        blue_fighter = columns[0].contents[3].get_text(strip=True)
     

        red_KD = columns[1].contents[1].get_text(strip=True)
        blue_KD = columns[1].contents[3].get_text(strip=True)
        ### parse sig str
        red_sig_str = columns[2].contents[1].get_text(strip=True)
        red_sig_str_land, red_sig_str_total = red_sig_str.split('of',1)

        blue_sig_str = columns[2].contents[3].get_text(strip=True)
        blue_sig_str_land, blue_sig_str_total = blue_sig_str.split('of',1)

        ### parsing total strikes
        red_ttl_str = columns[4].contents[1].get_text(strip=True)
        red_ttl_str_land, red_ttl_str_total = red_ttl_str.split('of',1)
        blue_ttl_str = columns[4].contents[3].get_text(strip=True)
        blue_ttl_str_land, blue_ttl_str_total = blue_ttl_str.split('of',1)

        red_td = columns[5].contents[1].get_text(strip=True)
        red_td_land, red_td_total = red_td.split('of',1)

        blue_td = columns[5].contents[3].get_text(strip=True)
        blue_td_land, blue_td_total = blue_td.split('of',1)

        red_SUB = columns[7].contents[1].get_text(strip=True)
        blue_SUB = columns[7].contents[3].get_text(strip=True)

        red_REV = columns[8].contents[1].get_text(strip=True)
        blue_REV = columns[8].contents[3].get_text(strip=True)

        red_CNTRL = columns[9].contents[1].get_text(strip=True)

        ### older fights do not have control, and sometimes opt for '--'
        ### we count those as 0 seconds
        try:
            min,sec = red_CNTRL.split(":",1)
        except ValueError as e:
            red_CNTRL = 0
        else:
            red_CNTRL = (int(min) * 60) + int(sec)

        blue_CNTRL = columns[9].contents[3].get_text(strip=True)
        try:
            min,sec = blue_CNTRL.split(":",1)
        except ValueError:
            blue_CNTRL = 0
        else:
            blue_CNTRL = (int(min) * 60) + int(sec)


        red_stats = FighterStats(
            fighter=red_fighter,
            KD=red_KD,
            SIGSTR_LAND=red_sig_str_land,
            SIGSTR_TTL=red_sig_str_total,
            TTLSTR_LAND=red_ttl_str_land,
            TTLSTR_TTL=red_ttl_str_total,
            TD_LAND=red_td_land,
            TD_TTL=red_td_total,
            SUB=red_SUB,
            REV=red_REV,
            CNTRL_SEC=red_CNTRL
        )
        blue_stats = FighterStats(
            fighter=blue_fighter,
            KD=blue_KD,
            SIGSTR_LAND=blue_sig_str_land,
            SIGSTR_TTL=blue_sig_str_total,
            TTLSTR_LAND=blue_ttl_str_land,
            TTLSTR_TTL=blue_ttl_str_total,
            TD_LAND=blue_td_land,
            TD_TTL=blue_td_total,
            SUB=blue_SUB,
            REV=blue_REV,
            CNTRL_SEC=blue_CNTRL
        )

        fight_stats['Red'] = red_stats
        fight_stats['Blue'] = blue_stats

        return fight_stats


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
    
    async def get_results(self,start,end=None,loop:asyncio.AbstractEventLoop=None) -> List:
        """
        Crawl from start -> end from the events_all_url.
        
        If you want the most recent bout information, start=2, end = 3

        If you want the upcoming bout information, start = 1, end = 2

        if You want everything, start = 0, don't specify end

        Args:
            start ([int]): [Bout to start at.]
            end ([int]): [Bout to end.]

        Returns:
            List: [description]
        """
        ### set the event loop if passed in
        self.loop = loop

        ### initial message.
        task_message = TaskQueueMessage(self.events_all_url,'', 0, 0)
        ### put it into the Q.
        self.task_queue.put_nowait(task_message)

        self.start = start + 1
        if end is not None:
            self.end = end + 1
        else:
            self.end = end
        
        await self.crawl()
        
        return self.results
        