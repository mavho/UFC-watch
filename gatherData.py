#This py file is for grabbing the ufcstats with the webscraper, then populating a db.
#Then we run the predictions module.

from UFC_scraper.UFC_stats_parse import UFCWebScraper 
#from predictions import predictions
import asyncio
import UFC_scraper.db_helper as dh

from ufc_api import db


def main():
    scraper = UFCWebScraper()

    data = asyncio.run(scraper.get_results(start=2,end=3))

    dh.populate_bouts_fighters_table(data)


### run the predictions module too.


if __name__ == '__main__':
    main()
