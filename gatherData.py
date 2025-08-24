#This py file is for grabbing the ufcstats with the webscraper, then populating a db.
#Then we run the predictions module to write the predictions out.

import asyncio
import os
import json
from config import Config
from argparse import ArgumentParser,Namespace
import pickle

from sqlalchemy import create_engine

from UFC_scraper.UFC_stats_parse import UFCWebScraper 
import UFC_scraper.db_helper as dh
from predictions.predictions import Predictions

LAST_SCRAPE_RESULTS_PICKLE = 'last_scaped_results.pickle'

def main(args:Namespace):

    if args.replay:
        with open(LAST_SCRAPE_RESULTS_PICKLE,'rb') as f:
            # pickle.dump(latest_event,LAST_SCRAPE_RESULTS_PICKLE)
            latest_event = pickle.load(f)
    else:
        ### load in the proxy list
        proxy_list = []
        with open('proxy_list.txt','r') as f:
            lines = f.readlines()
            for line in lines:
                proxy_list.append(line.strip())
                
        ### Get the latest UFC event (that just finished) and add it to the DB.
        scraper = UFCWebScraper(proxy_list=proxy_list)

        loop = asyncio.get_event_loop()

        latest_event = loop.run_until_complete(
            scraper.get_results(start=args.start,end=args.end)
        )

        print("Finished latest event")
        with open(LAST_SCRAPE_RESULTS_PICKLE,'wb+') as f:
            pickle.dump(latest_event,f)


        if args.bouts:
            upcoming_event = asyncio.run(scraper.get_results(start=1,end=2))
            print("Finished upcoming event")
            path = os.getcwd()

            ### create boutlist for this week with upcoming event data.
            with open(path +'/bout_list.txt','w') as fopen:
                for e_link,event_data in upcoming_event.items():
                    fopen.write(event_data['name']+'\n')
                    for bout_link,bout in event_data['bouts'].items():
                        fopen.write(f"{bout['r_fighter']}|{bout['b_fighter']}\n")

    if args.write:
        print("Writing results to SQL table")
        dh.populate_bouts_fighters_table(latest_event)
    


    if args.predict:
        db_engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        ### Predict new boutlist.
        pm = Predictions(db_engine)
        pred_json = pm.predict()

        #### Write results to pred fights json.
        json_obj = json.dumps(pred_json)
        with open(path + "/pred_fights.json","w") as fopen:
            fopen.write(json_obj)

if __name__ == '__main__':

    args = ArgumentParser()

    
    args.add_argument(
        '-s','--start',
        type=int,
        help='Integer that denotes where to start parsing on the bout page'
    )

    args.add_argument(
        '-e','--end',
        type=int,
        help='Integer that denotes where to stop parsing on the bout page'
    )

    args.add_argument(
        '--replay',
        action='store_true',
        help="Uses the last scrape results to insert into the DB"
    )

    args.add_argument(
        '--write',
        action='store_true',
        help="Writes the bouts into the SQL DB"
    )

    args.add_argument(
        '--bouts',
        action='store_true',
        help="Get the latest upcoming event and write them to bout_list.txt.\
            If -r is set this option does nothing"
    )

    args.add_argument(
        '--predict',
        action='store_true',
        help="Generates a predictions JSON file that predicts on the scrapped results"
    )

    main(args.parse_args())
