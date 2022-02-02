from ufc_api import db 
import os
from models import Events, Bouts

def populate_bouts_fighters_table(event_data):
    """
    Args: UFC_PARSER, event_list

    Uses the UFC Parser to go through event page as event_data
    Looks at all boutes in the data and commits the result to the DB
    """
    for link,event in event_data.items():
        bouts = event['bouts']
        event_name = event['name']
        date = event['date']
        location = event['location']


        ### See if this event is in the DB.
        event_q = Events.query.filter_by(event=event_name).first()
        ### if event is not in the DB, insert it
        if event_q is None:
            ### id is auto incrementing
            db.session.add(Events(event=event_name,date=event['date'],location=event['location']))
            db.session.commit()
            ### grab the event.
            event_q = Events.query.filter_by(event=event_name).first()

            for link,bout in bouts.items():

                db.session.add(Bouts(event_id=int(event_q.id),time=bout['Time'],end_round=bout['Round'],
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
        else:
            print(f"event: {event_name} already exists.")
    db.session.commit()
