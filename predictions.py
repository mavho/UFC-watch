from UFC_handler import db
from config import Config
from sqlalchemy import create_engine
from models import Events, Bouts
import pandas as pd

#sklearn modules
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics

def main():
    #db i'm accessing
    db_engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    connection = db_engine.connect()
    #let's say i'm getting whittaker's stuff
    fighter = 'Yoel Romero'
    blue_payload = 'winner, method, result, end_round, b_KD, b_PASS, b_SIGSTR, b_SIGSTR_PRCT, b_SUB, b_TD, b_TD_PRCT, b_TTLSTR'
    red_payload = 'winner, method, result, end_round, r_KD, r_PASS, r_SIGSTR, r_SIGSTR_PRCT, r_SUB, r_TD, r_TD_PRCT, r_TTLSTR'

    #red_query = "SELECT * FROM bouts WHERE red_fighter='Robert Whittaker'" 
    red_query = "SELECT " + red_payload + " FROM bouts WHERE red_fighter='" + fighter + "'" 
    blue_query = "SELECT " + blue_payload + " FROM bouts WHERE blue_fighter='" + fighter + "'" 
    #blue_query = "SELECT * FROM bouts WHERE blue_fighter='Robert Whittaker'"

    ###
    #Currently no data is distinguished from the oponent.
    #all stats are recorded as red, since when u union it over laps
    #names are different but the reasoning is the same
    ###
    data_frame = pd.read_sql(red_query + ' UNION ' + blue_query, connection)
    for index, rows in data_frame.iterrows():
        if(rows['winner'] == fighter):
            data_frame.set_value(index,'winner', int(1))
        else:
            data_frame.set_value(index,'winner', int(0))
        try:
            data_frame.set_value(index,'r_TD',int(rows['r_TD'].split('/')[0]))
        except ValueError:
            data_frame.set_value(index,'r_TD',int(rows['r_TD'].split(' of ')[0]))

        data_frame.set_value(index,'r_TTLSTR',int(rows['r_TTLSTR'].split('/')[0]))
        data_frame.set_value(index,'r_SIGSTR',int(rows['r_SIGSTR'].split('/')[0]))
        data_frame.set_value(index,'r_SIGSTR_PRCT',int(rows['r_SIGSTR_PRCT'].strip('%')))
        data_frame.set_value(index,'r_TD_PRCT',int(rows['r_TD_PRCT'].strip('%')))

    #data_frame_red = pd.read_sql(red_query, connection)
    #data_frame_blue= pd.read_sql(blue_query, connection)
    print(data_frame)

    feature_col = ['winner', 'end_round', 'r_KD', 'r_PASS', 'r_SIGSTR', 'r_SIGSTR_PRCT', 'r_SUB', 'r_TD', 'r_TD_PRCT', 'r_TTLSTR']

    X = data_frame[feature_col]
    y = data_frame.winner
    #split X and y into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.25, random_state=0)

    # instantiate the model (using the default parameters)
    logreg = LogisticRegression()
    y_train = y_train.astype('int')
    # fit the model with data
    logreg.fit(X_train,y_train)
    #
    y_pred=logreg.predict(X_test)
    print(y_pred)
    cnf_matrix = metrics.confusion_matrix(y_test, y_pred)
    print(cnf_matrix)


if __name__ == '__main__':
    main()