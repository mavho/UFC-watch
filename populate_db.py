from ufc_api import db, ConfigURL 
from UFC_stats_parse import UFC_Stats_Parser
from models import Events, Bouts

#should only be called with an empty events table
def populate_events_table(event_list):
    for event in event_list:
        db.session.add(Events(event=event['event']))
    
    db.session.commit()

#gets new event and commits to db
def update_events_table(event_list):
    e = Events(event=event_list[0]['event'])
    db.session.add(e)
    db.session.commit()

#Writes out the latest fighters to a text file
#each fighter on their seperate line
def get_latest_fighters(parser,event_list):
    event = event_list[0]['event']
    data_bytes = parser.getRawHTML(event_list[0]['link'])
    result = parser.generate_event_bout_list(data_bytes)
    print(result,flush=True)
    fopn = open('bout_list.txt', 'w')
    fopn.write(event+'\n')
    for bout in result:
        fopn.write(bout[0]+"\n")
        fopn.write(bout[1]+"\n")
    fopn.close()


def populate_bouts_fighters_table(parser,event_data):
    #Only the first 10 bouts
    #stopped at 140
    for bout in event_data[1:3]:
        print(bout['event'], flush=True)
        event = Events.query.filter_by(event=bout['event']).first()
        if event is None:
            event = 0
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
    parser = UFC_Stats_Parser()
    configobj = ConfigURL()

    print('populate event table',flush=True)
    #events list page
    data_bytes = parser.getRawHTML(configobj.url)
    result = parser.generate_url_list(data_bytes) 
    print('populate bouts table',flush=True)
    get_latest_fighters(parser,result)


    #update new events
    #update_events_table(result)
    #populate bouts for those events
    #populate_bouts_fighters_table(parser,result)
if __name__ == '__main__':
    main()
