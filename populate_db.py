from UFC_handler import db, ConfigURL 
from UFC_stats_parse import UFC_Stats_Parser
from models import Events, Bouts
def populate_events_table(event_list):
    for event in event_list:
        #flag = Events.query.filter_by(event=event_data[1]['event']).first()
        if flag is not None:
            continue
        else:
            db.session.add(Events(event=event['event']))
    
    db.session.commit()

def populate_bouts_fighters_table(parser,event_data):
    for bout in event_data[1:10]:
        print(bout['event'])
        event = Events.query.filter_by(event=bout['event']).first()
        if event is None:
            event = 0
        #else:
        #    print(int(event.id))
        data_bytes = parser.getRawHTML(bout['link'])
        result = parser.parse_event_fights(data_bytes)
        for bout in result:
            db.session.add(Bouts(event_id=int(event.id),time=bout['Time'],end_round=bout['Round'],
                method=bout['Method'],result=bout['Result'],weight_class=bout['WeightClass'],
                winner=bout['Winner'], loser=bout['Loser'],
                red_fighter=bout['Red']['fighter'], blue_fighter=bout['Blue']['fighter']))
    
    db.session.commit()

def main():
    parser = UFC_Stats_Parser()
    configobj = ConfigURL()

    print('populate event table')
    data_bytes = parser.getRawHTML(configobj.url)
    result = parser.generate_url_list(data_bytes) 
    #populate_events_table(result)
    print('populate bouts table')
    populate_bouts_fighters_table(parser,result)
    #data_bytes = parser.getRawHTML(configobj.bout_url)
    #result = parser.parse_event_fights(data_bytes)






if __name__ == '__main__':
    main()