from UFC_handler import db
from config import Config
from sqlalchemy import create_engine
from models import Events, Bouts
import pandas as pd
import sys

#sklearn modules
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics

def p2f(str):
    return(float(str.strip('%'))/100)

def populate_dataframes(data_frame, in_fighters, blue_fighter, red_fighter):
    #vars to calculate avgs of respective fighters
    avg_rsigstr = avg_rsigstr_prct = avg_rTD_prct = avg_rTD = avg_rKD = avg_rpass = avg_rsub = avg_rttlstr = 0 
    avg_bsigstr = avg_bsigstr_prct = avg_bTD_prct = avg_bTD = avg_bKD = avg_bpass = avg_bsub = avg_bttlstr = 0 
    #count how many fights each fighter had
    red_cnt = 0
    blue_cnt = 0

    for index, rows in data_frame.iterrows():
        if(rows['winner'] == rows['blue_fighter']):
            data_frame.at[index, 'b_win']=int(1)
            data_frame.at[index, 'r_win']=int(0)
        elif(rows['winner'] == rows['red_fighter']):
            data_frame.at[index, 'b_win']=int(0)
            data_frame.at[index, 'r_win']=int(1)
        else:
            data_frame.at[index, 'b_win']=int(0)
            data_frame.at[index, 'r_win']=int(0)

        #local vars for the loop, don't wanna calculate every time
        TD=0
        try:
            TD = int(rows['r_TD'].split('/')[1])
        except (ValueError, IndexError):
            TD = int(rows['r_TD'].split('of')[1])
        TD_PRCT = p2f(rows['r_TD_PRCT'])
        TTLSTR = int(rows['r_TTLSTR'].split('/')[1])
        TTLSTR_PRCT = float(int(rows['r_TTLSTR'].split('/')[0])/int(rows['r_TTLSTR'].split('/')[1]))
        SIGSTR = int(rows['r_SIGSTR'].split('/')[1])
        SIGSTR_PRCT = p2f(rows['r_SIGSTR_PRCT'])

        data_frame.at[index,'r_TD']=TD
        data_frame.at[index,'r_TTLSTR']=TTLSTR
        data_frame.at[index,'r_TTLSTR_PRCT']=TTLSTR_PRCT
        data_frame.at[index,'r_SIGSTR']=SIGSTR
        data_frame.at[index,'r_SIGSTR_PRCT']=SIGSTR_PRCT
        data_frame.at[index,'r_TD_PRCT']=TD_PRCT

        if rows['red_fighter'] == red_fighter:
            avg_rTD += TD
            avg_rsigstr += SIGSTR
            avg_rsigstr_prct += SIGSTR_PRCT
            avg_rTD_prct += TD_PRCT 
            avg_rKD += rows['r_KD']
            avg_rpass += rows['r_PASS']
            avg_rsub += rows['r_SUB']
            avg_rttlstr += TTLSTR  
            red_cnt +=1

        if rows['red_fighter'] == blue_fighter:
            avg_bTD += TD
            avg_bsigstr += SIGSTR
            avg_bsigstr_prct += SIGSTR_PRCT
            avg_bTD_prct += TD_PRCT 
            avg_bKD += rows['b_KD']
            avg_bpass += rows['b_PASS']
            avg_bsub += rows['b_SUB']
            avg_bttlstr += TTLSTR  
            blue_cnt+=1

        #################Blue side#################################################    
        TD=0
        try:
            TD = int(rows['b_TD'].split('/')[1])
        except (ValueError, IndexError):
            TD = int(rows['b_TD'].split('of')[1])
        TD_PRCT = p2f(rows['b_TD_PRCT'])
        TTLSTR = int(rows['b_TTLSTR'].split('/')[1])
        TTLSTR_PRCT = float(int(rows['b_TTLSTR'].split('/')[0])/int(rows['b_TTLSTR'].split('/')[1]))
        SIGSTR = int(rows['b_SIGSTR'].split('/')[1])
        SIGSTR_PRCT = p2f(rows['b_SIGSTR_PRCT'])

        data_frame.at[index,'b_TD'] = TD
        data_frame.at[index,'b_TTLSTR'] = TTLSTR
        data_frame.at[index,'b_TTLSTR_PRCT']=TTLSTR_PRCT
        data_frame.at[index,'b_SIGSTR']=SIGSTR
        data_frame.at[index,'b_SIGSTR_PRCT']=SIGSTR_PRCT
        data_frame.at[index,'b_TD_PRCT']=TD_PRCT

        #correspond fighter's info throughout different dataframes
        if rows['blue_fighter'] == blue_fighter:
            avg_bTD += TD
            avg_bsigstr += SIGSTR
            avg_bsigstr_prct += SIGSTR_PRCT
            avg_bTD_prct += TD_PRCT 
            avg_bKD += rows['b_KD']
            avg_bpass += rows['b_PASS']
            avg_bsub += rows['b_SUB']
            avg_bttlstr += TTLSTR  
            blue_cnt+=1
        if rows['blue_fighter'] == red_fighter:
            avg_rTD += TD
            avg_rsigstr += SIGSTR
            avg_rsigstr_prct += SIGSTR_PRCT
            avg_rTD_prct += TD_PRCT 
            avg_rKD += rows['r_KD']
            avg_rpass += rows['r_PASS']
            avg_rsub += rows['r_SUB']
            avg_rttlstr += TTLSTR  
            red_cnt +=1
    return in_fighters.append({'blue_fighter':blue_fighter,'b_KD':avg_bKD/blue_cnt, 'b_PASS':avg_bpass/blue_cnt,
     'b_SIGSTR':avg_bsigstr/blue_cnt, 'b_SIGSTR_PRCT':avg_bsigstr_prct/blue_cnt
        , 'b_SUB':avg_bsub/blue_cnt, 'b_TD': avg_bTD/blue_cnt, 'b_TD_PRCT':avg_bTD_prct/blue_cnt
        ,'red_fighter':red_fighter,'r_KD':avg_rKD/red_cnt, 'r_PASS':avg_rpass/red_cnt,
         'r_SIGSTR':avg_rsigstr/red_cnt, 'r_SIGSTR_PRCT':avg_rsigstr_prct/red_cnt, 'r_SUB':avg_rsub/red_cnt,
          'r_TD':avg_rTD/red_cnt, 'r_TD_PRCT':avg_rTD_prct/red_cnt},ignore_index=True)


def main():
    #db i'm accessing
    db_engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    connection = db_engine.connect()

    #weight class
    weight_class = 'Welterweight'
    blue_payload = 'blue_fighter,b_KD, b_PASS, b_SIGSTR, b_SIGSTR_PRCT, b_SUB, b_TD, b_TD_PRCT, b_TTLSTR'
    red_payload = 'red_fighter, r_KD, r_PASS, r_SIGSTR, r_SIGSTR_PRCT, r_SUB, r_TD, r_TD_PRCT, r_TTLSTR'
    stats_payload = 'winner, loser, end_round, time, method, result'

    ###
    #currently logistic regression doesn't distinguish on who the fighter is
    #there's no concept or reach, winstreak, or anything
    #Later iterations will include winstreaks
    #furthermore data frames will be created based on the fighter as well as the opponent.
    ###
    #data_frame = pd.read_sql(red_query + ' UNION ' + blue_query + ' UNION ' + stats_payload, connection)
    blue_fighter = 'Gregor Gillespie'
    red_fighter = 'Kevin Lee'


    ###dataframe for fighter averages in the predict list
    in_fighters = pd.DataFrame(columns=['blue_fighter','b_KD', 'b_PASS', 'b_SIGSTR', 'b_SIGSTR_PRCT', 'b_SUB', 'b_TD', 'b_TD_PRCT'
            ,'red_fighter','r_KD', 'r_PASS', 'r_SIGSTR', 'r_SIGSTR_PRCT', 'r_SUB', 'r_TD', 'r_TD_PRCT'])
#    in_fighters.at[0, 'blue_fighter']=blue_fighter
#    in_fighters.at[0, 'red_fighter']=red_fighter
            
    #query for weight class
    weight_query = "SELECT * FROM bouts WHERE weight_class='" + weight_class +"'"

    #queries for the fighters in some bout
    blue_fighter_query = "SELECT * FROM bouts WHERE blue_fighter='" + blue_fighter +"' or red_fighter='" + blue_fighter + "'"
    red_fighter_query = "SELECT * FROM bouts WHERE blue_fighter='" + red_fighter +"' or red_fighter='" + red_fighter + "'"

    union_query = blue_fighter_query + ' UNION ' + red_fighter_query


    data_frame = pd.read_sql(union_query, connection)

    data_frame["b_win"] = 0;
    data_frame["r_win"] = 0;
    out_fighters = populate_dataframes(data_frame, in_fighters, blue_fighter, red_fighter)
    
    print(data_frame)
    print(out_fighters)
    in_fighters._clear_item_cache()

    ##################################################################################################

    feature_col = ['b_KD', 'b_PASS', 'b_SIGSTR', 'b_SIGSTR_PRCT', 'b_SUB', 'b_TD', 'b_TD_PRCT', 'b_TTLSTR', 'b_TTLSTR_PRCT'
            'r_KD', 'r_PASS', 'r_SIGSTR', 'r_SIGSTR_PRCT', 'r_SUB', 'r_TD', 'r_TD_PRCT', 'r_TTLSTR', 'r_TTLSTR_PRCT']

    sys.exit()

    X = data_frame[feature_col]
    y = data_frame.r_win

    #split X and y into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.25, random_state=0)


    # instantiate the model (using the default parameters)
    logreg = LogisticRegression()
    y_train = y_train.astype('int')
    # fit the model with data
    logreg.fit(X_train,y_train)
    #
    y_pred=logreg.predict(X_test)

    print(y_test)
    print('################################################################################')
    print(y_pred)
    print(X_test)

    count = 0;
    for index,rows in X_test.iterrows():
        print(data_frame.loc[index]['blue_fighter'] + ' : ' + data_frame.loc[index]['red_fighter'])
        if y_pred[count] == 1:
            print('winner: ' +data_frame.loc[index]['red_fighter'])
        else:
            print('winner: ' + data_frame.loc[index]['blue_fighter'])
        print('actual winner: ' + data_frame.loc[index]['winner'])
        count += 1




#    cnf_matrix = metrics.confusion_matrix(y_test, y_pred)
#    print(cnf_matrix)
    print("Accuracy:",metrics.accuracy_score(y_test, y_pred))
    print("Precision:",metrics.precision_score(y_test, y_pred))
    print("Recall:",metrics.recall_score(y_test, y_pred))

if __name__ == '__main__':
    main()