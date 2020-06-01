from ufc_api import db, ConfigURL
import os
from UFC_stats_parse import UFC_Stats_Parser
from models import Events, Bouts

def _populate_events_table(event_list):
    """
    Args: event_list
    Addes every event in the event_list to the database
    really a one time thing
    """
    for event in event_list:
        db.session.add(Events(event=event['event']))
    
    db.session.commit()

def update_events_table(event_list):
    """
    Args: event_list
    Grabs the first event in the event_list and commits it to the DB
    """
    e = Events(event=event_list[0]['event'])
    db.session.add(e)
    db.session.commit()

def get_latest_fighters(UFC_parser,event_list):
    """
    Args: UFC_PARSER, event_list
    Uses the UFC Parser to open up a link from the event list,
    and write out the bouts from that event to bout_list.txt
    """
    event = event_list[0]['event']
    data_bytes = UFC_parser.getRawHTML(event_list[0]['link'])
    result = UFC_parser.generate_event_bout_list(data_bytes)
    print(result,flush=True)
    fopn = open('/home/homaverick/UFC_API/bout_list.txt', 'w')
    fopn.write(event+'\n')
    for bout in result:
        fopn.write(bout[0]+"\n")
        fopn.write(bout[1]+"\n")
    fopn.close()


def populate_bouts_fighters_table(parser,event_data,end=2):
    """
    Args: UFC_PARSER, event_list

    Uses the UFC Parser to go through event page as event_data
    Looks at all boutes in the data and commits the result to the DB
    """
    #Only the first 10 bouts
    #stopped at 140
    for bout in event_data[1:end]:
        print(bout['event'], flush=True)
        event = Events.query.filter_by(event=bout['event']).first()
        if event is None:
            db.session.add(Events(event=bout['event']))
            db.session.commit()
            event = Events.query.filter_by(event=bout['event']).first()
        try:
            data_bytes = parser.getRawHTML(bout['link'])
            result = parser.parse_event_fights(data_bytes)
        except:
            print('Crashed on ' + event.id, flush=True)
            db.session.commit()
            continue

        for bout in result:
            db.session.add(Bouts(event_id=int(event.id),time=bout['Time'],end_round=bout['Round'],
                method=bout['Method'],result=bout['Result'],weight_class=bout['WeightClass'],
                winner=bout['Winner'], loser=bout['Loser'],
                red_fighter=bout['Red']['fighter'], blue_fighter=bout['Blue']['fighter'],
                b_KD=bout['Blue']['KD'],r_KD=bout['Red']['KD'],
                b_SIGSTR=bout['Blue']['SIGSTR'], r_SIGSTR=bout['Red']['SIGSTR'],
                b_SIGSTR_PRCT=bout['Blue']['SIGSTR_PRCT'], r_SIGSTR_PRCT=bout['Red']['SIGSTR_PRCT'],
                b_TTLSTR=bout['Blue']['TTLSTR'], r_TTLSTR=bout['Red']['TTLSTR'],
                b_TD=bout['Blue']['TD'], r_TD=bout['Red']['TD'],
                b_TD_PRCT=bout['Blue']['TD_PRCT'], r_TD_PRCT=bout['Red']['TD_PRCT'],
                b_SUB=bout['Blue']['SUB'], r_SUB=bout['Red']['SUB'],
                b_PASS=bout['Blue']['PASS'], r_PASS=bout['Red']['PASS']
                ))
    db.session.commit()


def main():
    basedir = os.path.abspath(os.path.dirname(__file__))
    parser = UFC_Stats_Parser(basedir + '/proxy_list.txt')

    CU = ConfigURL()
    #print('populate event table',flush=True)
    #events list page
    data_bytes = parser.getRawHTML( CU.completed_page_url)
    url_list = parser.generate_url_list(data_bytes) 
    #print('populate bouts table',flush=True)

    #get_latest_fighters(parser,result)

    #update new events
    #update_events_table(url_list)

    #populate bouts for those events
    populate_bouts_fighters_table(parser,url_list,end=5)
if __name__ == '__main__':
    main()
