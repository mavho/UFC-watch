#This py file is for grabbing the ufcstats with the webscraper, then populating a db.
#Then we run the predictions module to write the predictions out.

from pprint import pprint
from UFC_scraper.UFC_stats_parse import UFCWebScraper 
import asyncio, os, json
import UFC_scraper.db_helper as dh
from predictions.predictions import Predictions
from sqlalchemy import create_engine
from config import Config


from ufc_api import db


def main():
    ### Get the latest UFC event (that just finished) and add it to the DB.
    scraper = UFCWebScraper()
    latest_event = asyncio.run(scraper.get_results(start=2,end=3))
    dh.populate_bouts_fighters_table(latest_event)
    print("Finished latest event")
    ### Grab the upcoming event
    upcoming_event = asyncio.run(scraper.get_results(start=1,end=2))
    print("Finished upcoming event")
    path = os.getcwd()

    ### create boutlist for this week with upcoming event data.
    with open(path +'/bout_list.txt','w') as fopen:
        for e_link,event_data in upcoming_event.items():
            fopen.write(event_data['name']+'\n')
            for bout_link,bout in event_data['bouts'].items():
                fopen.write(f"{bout['r_fighter']}|{bout['b_fighter']}\n")

    db_engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    ### Predict new boutlist.
    pm = Predictions(db_engine)
    pred_json = pm.predict()

    #### Write results to pred fights json.
    json_obj = json.dumps(pred_json)
    with open(path + "/pred_fights.json","w") as fopen:
        fopen.write(json_obj)

if __name__ == '__main__':
    main()
