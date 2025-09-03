import os
from typing import Dict

from ufc_api import db,app 
from .UFC_stats_parse import FighterStats
from models import Events, Bouts

def populate_bouts_fighters_table(event_data):
    """
    Args: UFC_PARSER, event_list

    Uses the UFC Parser to go through event page as event_data
    Looks at all bouts in the data and commits the result to the DB
    """

    with app.app_context():
        for link,event in event_data.items():

            event_name = event['name']
            date = event['date']
            location = event['location']


            # for link,bout in bouts.items():
            #     print(link)
            #     print(bout)

            ### See if this event is in the DB.
            event_q = Events.query.filter_by(event=event_name).first()
            ### if event is not in the DB, insert it
            if event_q is None:
                ### id is auto incrementing
                db.session.add(Events(event=event_name,date=date,location=location))
                db.session.commit()
                ### grab the event.
                event_q = Events.query.filter_by(event=event_name).first()
            else:
                ### check if we have any bouts under this event.
                bouts_q = Bouts.query.filter_by(event_id=int(event_q.id)).all()
                if bouts_q:
                    print(f"event: {event_name} already exists and has bouts")
                    return
                else:
                    print(f"event: {event_name} already exists, but has no bouts.")

            if 'bouts' not in event:
                print(f"No bouts recorded for {event_name}")
                continue
            else:
                print(f"Bouts recorded for {event_name}")
            
            bouts:Dict[str,Dict[str,FighterStats]] = event['bouts']

            for link,bout in bouts.items():
                try:
                    db.session.add(
                        Bouts(
                            event_id=int(event_q.id),
                            time=bout['Time'],end_round=bout['Round'],
                            method=bout['Method'],
                            result=bout['Result'],
                            weight_class=bout['WeightClass'],
                            winner=bout['Winner'],
                            loser=bout['Loser'],
                            red_fighter=bout['Red'].fighter,
                            r_KD=bout['Red'].KD,
                            r_LAND_SIGSTR=bout['Red'].SIGSTR_LAND,
                            r_TTL_SIGSTR=bout['Red'].SIGSTR_TTL,
                            r_TTL_STR=bout['Red'].TTLSTR_TTL,
                            r_LAND_STR=bout['Red'].TTLSTR_LAND,
                            r_LAND_TD=bout['Red'].TD_LAND,
                            r_TTL_TD=bout['Red'].TD_TTL,
                            r_SUB=bout['Red'].SUB,
                            r_REV=bout['Red'].REV,
                            r_CNTRL_SEC=bout['Red'].CNTRL_SEC,

                            blue_fighter=bout['Blue'].fighter,
                            b_KD=bout['Blue'].KD,
                            b_LAND_SIGSTR=bout['Blue'].SIGSTR_LAND,
                            b_TTL_SIGSTR=bout['Blue'].SIGSTR_TTL,
                            b_TTL_STR=bout['Blue'].TTLSTR_TTL,
                            b_LAND_STR=bout['Blue'].TTLSTR_LAND,
                            b_LAND_TD=bout['Blue'].TD_LAND,
                            b_TTL_TD=bout['Blue'].TD_TTL,
                            b_SUB=bout['Blue'].SUB,
                            b_REV=bout['Blue'].REV,
                            b_CNTRL_SEC=bout['Blue'].CNTRL_SEC,

                        ))
                ### key error is generally produced from the new fight (we don't know who is red)
                except KeyError:
                    pass

        db.session.commit()
