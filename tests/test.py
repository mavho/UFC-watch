import unittest
import json
from unittest.mock import MagicMock,patch
import asyncio
import pprint
import os


from sqlalchemy import create_engine

from UFC_scraper.UFC_stats_parse import UFCWebScraper
from config import Config
import UFC_scraper.db_helper as dbhelp
from predictions.predictions import Predictions

class TestScrapper(unittest.TestCase):
    def _parse_listing(self):
        scraper = UFCWebScraper()


        #res = asyncio.run(scraper.get_results(2,end=3))
        #pprint.pprint(res)
        res = asyncio.run(scraper.get_results(1,end=2))
        pprint.pprint(res)


        path = os.getcwd()

        with open(path +'/bout_list.txt','w') as fopen:
            for e_link,event_data in res.items():
                fopen.write(event_data['name'])
                for bout_link,bout in event_data['bouts'].items():
                    fopen.write(f"{bout['r_fighter']}|{bout['b_fighter']}\n")

    def _parse_strikes(self):
        scraper = UFCWebScraper(concurrency=1)

        loop = asyncio.get_event_loop()

        url,links,html,data = loop.run_until_complete(
                scraper.crawl_page(
                # "http://ufcstats.com/fight-details/0b1460c666e66d39",
                # "http://ufcstats.com/fight-details/58080e8989927500",
                "http://ufcstats.com/fight-details/d14fea43712707f0",
                2
            )
        )

        print(data)

class TestDB(unittest.TestCase):
    def _test_parse_listing(self):
        scraper = UFCWebScraper()

        res = asyncio.run(scraper.get_results(6,end=8))

        dbhelp.populate_bouts_fighters_table(res)

class TestAPI(unittest.TestCase):

    def test_events_resource_fail(self):
        from ufc_api import app

        with app.test_client() as c:
            r = c.get('/events/extra')

            self.assertEqual(r.status_code,400)
            data = json.loads(r.get_data())

            self.assertEqual([],data['events'])

    def test_event_resource(self):
        from ufc_api import app

        with app.test_client() as c:
            r = c.get('/event/53')

            self.assertEqual(r.status_code,200)
            data = json.loads(r.get_data())
            print(data)
    def test_predictions(self):
        from ufc_api import app

        with app.test_client() as c:
            r = c.get('/predictions/1')

            self.assertEqual(r.status_code,200)
            data = json.loads(r.get_data())
            print(data)

            # self.assertEqual([],data['events'])

class TestPredictions(unittest.TestCase):
    # def test_training(self):
    #     db_engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    #     pm = Predictions(db_engine)

    #     X_train, X_test, y_train, y_test = pm.generate_data()
    #     pm.train_predictionModel('LR', X_train, X_test, y_train, y_test)
    #     #pm.train_predictionModel('clf', X_train, X_test, y_train, y_test)
    #     #pm.train_predictionModel('perp', X_train, X_test, y_train, y_test)
    #     #pm.train_predictionModel('SGD', X_train, X_test, y_train, y_test)

    def _test_predictions(self):
        db_engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        pm = Predictions(db_engine)

        # res = pm.predict('Israel Adesanya','Robert Whittaker')
        res = pm.predict('Abdul Razak Alhassan','Alessio Di Chirico')
        pprint.pprint(res)

        with self.assertRaises(Exception):
            pm.predict()
        with self.assertRaises(Exception):
            pm.predict(blue_fighter='ron')
        with self.assertRaises(Exception):
            pm.predict(red_fighter='ron')

        res = pm.predict(blue_fighter="'",red_fighter=";drop table events;--")
        print(res['predictions'])
        self.assertEqual(len(res['predictions']),1)

        res = pm.predict(blue_fighter="'",red_fighter="'; select true;--")
        print(res['predictions'])
        self.assertEqual(len(res['predictions']),1)
