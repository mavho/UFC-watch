from UFC_handler import db, ConfigURL 
from UFC_stats_parse import UFC_Stats_Parser
from models import Events
def populate_events(event_list):
    for event in event_list:
#        print(event)
        db.session.add(Events(event=event['event']))
    
    db.session.commit()


def main():
    parser = UFC_Stats_Parser()
    configobj = ConfigURL()

    print('populate event table')
    data_bytes = parser.getRawHTML(configobj.url)
    result = parser.generate_url_list(data_bytes) 
    #print(result)
    populate_events(result)




if __name__ == '__main__':
    main()