#This py file is for grabbing the ufcstats with the webscraper, then populating a db.
#Then we run the predictions module.

from pprint import pprint
from UFC_scraper.UFC_stats_parse import UFCWebScraper 
from predictions import predictions
import asyncio, os
import UFC_scraper.db_helper as dh
from predictions.predictions import Predictions
from sqlalchemy import create_engine
from config import Config


from ufc_api import db


def main():
    scraper = UFCWebScraper()
    #latest_event = asyncio.run(scraper.get_results(start=2,end=3))
#    dh.populate_bouts_fighters_table(latest_event)
 #   print("Finished latest event")
#    new_scapper = UFCWebScraper()
    upcoming_event = asyncio.run(scraper.get_results(start=1,end=2))
    print("Finished upcoming event")
    path = os.getcwd()

    ### create boutlist for this week
    with open(path +'/bout_list.txt','w') as fopen:
        for e_link,event_data in upcoming_event.items():
            fopen.write(event_data['name']+'\n')
            for bout_link,bout in event_data['bouts'].items():
                fopen.write(f"{bout['r_fighter']}|{bout['b_fighter']}\n")

    db_engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    ### Predict new boutlist.
    pm = Predictions(db_engine)
    res = pm.predict()
    pprint(res)


### run the predictions module too.


if __name__ == '__main__':
    main()
