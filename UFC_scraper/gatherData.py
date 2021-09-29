from UFC_stats_parse import UFC_Stats_Parser
def main():
    #url = 'http://www.ufcstats.com/statistics/events/completed?page=all'
    url = 'http://http://www.ufcstats.com/statistics/events/completed'
    parser = UFC_Stats_Parser()
    print('Get current fights test------------------')    


    #url = 'http://www.ufcstats.com/event-details/94a5aaf573f780ad'
    data_bytes = parser.get_raw_html(url)
    url_list = parser.generate_url_list(data_bytes)
    fight_list=parser.generate_Event_Bout_list(url_list[0])
    print(fight_list)




if __name__ == '__main__':
    main()
