from UFC_scraper.UFC_stats_parse import UFCWebScraper 
import asyncio
import UFC_scraper.db_helper as dh

def main():
    scraper = UFCWebScraper()

    data = asyncio.run(scraper.get_results(start=2,end=356))

    dh.populate_bouts_fighters_table(data)



if __name__ == '__main__':
    main()
