from UFC_handler import db
from config import Config
from sqlalchemy import create_engine
from models import Events, Bouts
import pandas as pd

#sklearn modules
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics

def p2f(str):
    return(float(str.strip('%'))/100)

def main():
    #db i'm accessing
    db_engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    connection = db_engine.connect()

    #weight class
    weight_class = 'Welterweight'
    blue_payload = 'blue_fighter,b_KD, b_PASS, b_SIGSTR, b_SIGSTR_PRCT, b_SUB, b_TD, b_TD_PRCT, b_TTLSTR'
    red_payload = 'red_fighter, r_KD, r_PASS, r_SIGSTR, r_SIGSTR_PRCT, r_SUB, r_TD, r_TD_PRCT, r_TTLSTR'
    stats_payload = 'winner, loser, end_round, time, method, result'

    #red_query = "SELECT * FROM bouts WHERE red_fighter='Robert Whittaker'" 
    red_query = "SELECT " + red_payload + " FROM bouts WHERE weight_class='" + weight_class+ "'" 
    blue_query = "SELECT " + blue_payload + " FROM bouts WHERE weight_class='" + weight_class + "'" 
    #blue_query = "SELECT * FROM bouts WHERE blue_fighter='Robert Whittaker'"

    ###
    #currently logistic regression doesn't distinguish on who the fighter is
    #there's no concept or reach, winstreak, or anything
    #Later iterations will include winstreaks
    #furthermore data frames will be created based on the fighter as well as the opponent.
    ###
    #data_frame = pd.read_sql(red_query + ' UNION ' + blue_query + ' UNION ' + stats_payload, connection)
    query = "SELECT * FROM bouts WHERE weight_class='" + weight_class +"'"
    data_frame = pd.read_sql(query, connection)
    data_frame["b_win"] = 0;
    data_frame["r_win"] = 0;
    for index, rows in data_frame.iterrows():
        if(rows['winner'] == rows['blue_fighter']):
            data_frame.set_value(index, 'b_win', int(1))
            data_frame.set_value(index, 'r_win', int(0))
        elif(rows['winner'] == rows['red_fighter']):
            data_frame.set_value(index, 'b_win', int(0))
            data_frame.set_value(index, 'r_win', int(1))
        else:
            data_frame.set_value(index, 'b_win', int(0))
            data_frame.set_value(index, 'r_win', int(0))

        #convert the strings to floats
        try:
            data_frame.set_value(index,'r_TD',int(rows['r_TD'].split('/')[1]))
        except (ValueError, IndexError):
            data_frame.set_value(index,'r_TD',int(rows['r_TD'].split(' of ')[1]))

        #data_frame.set_value(index,'r_TTLSTR',float(int(rows['r_TTLSTR'].split('/')[0])/int(rows['r_TTLSTR'].split('/')[1])))
        data_frame.set_value(index,'r_SIGSTR',int(rows['r_SIGSTR'].split('/')[1]))

        data_frame.set_value(index,'r_SIGSTR_PRCT',p2f(rows['r_SIGSTR_PRCT']))
        data_frame.set_value(index,'r_TD_PRCT',p2f(rows['r_TD_PRCT']))

        try:
            data_frame.set_value(index,'b_TD',int(rows['b_TD'].split('/')[1]))
        except (ValueError, IndexError):
            data_frame.set_value(index,'b_TD',int(rows['b_TD'].split(' of ')[1]))

        #data_frame.set_value(index,'b_TTLSTR',float(int(rows['b_TTLSTR'].split('/')[0])/int(rows['b_TTLSTR'].split('/')[1])))
        data_frame.set_value(index,'b_SIGSTR',int(rows['b_SIGSTR'].split('/')[1]))

        data_frame.set_value(index,'b_SIGSTR_PRCT',p2f(rows['b_SIGSTR_PRCT']))
        data_frame.set_value(index,'b_TD_PRCT',p2f(rows['b_TD_PRCT']))
    

    ##################################################################################################

    feature_col = ['b_KD', 'b_PASS', 'b_SIGSTR', 'b_SIGSTR_PRCT', 'b_SUB', 'b_TD', 'b_TD_PRCT',
            'r_KD', 'r_PASS', 'r_SIGSTR', 'r_SIGSTR_PRCT', 'r_SUB', 'r_TD', 'r_TD_PRCT']


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

    for index,rows in X_test.iterrows():
        print(data_frame.loc[index]['blue_fighter'] + ' : ' + data_frame.loc[index]['red_fighter'])



#    cnf_matrix = metrics.confusion_matrix(y_test, y_pred)
#    print(cnf_matrix)
    print("Accuracy:",metrics.accuracy_score(y_test, y_pred))
    print("Precision:",metrics.precision_score(y_test, y_pred))
    print("Recall:",metrics.recall_score(y_test, y_pred))

if __name__ == '__main__':
    main()