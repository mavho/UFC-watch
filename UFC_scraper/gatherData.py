from UFC_stats_parse import UFCWebScraper 
import asyncio
import db_helper

def main():
    scraper = UFCWebScraper()

    data = asyncio.run(scraper.get_results(start=2,end=3))



if __name__ == '__main__':
    main()
