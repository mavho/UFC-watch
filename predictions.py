from ufc_api import db
from config import Config
from sqlalchemy import create_engine
from models import Events, Bouts
import pandas as pd
import pickle
import sys, json

#sklearn modules
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import Perceptron
from sklearn.linear_model import SGDClassifier 

from sklearn import metrics, tree

class Predictions():
    def __init__(self):
        #db i'm accessing
        self.db_engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        self.connection = self.db_engine.connect()
        self.columns = ['blue_fighter','b_KD', 'b_PASS', 'b_SIGSTR', 'b_SIGSTR_PRCT', 'b_SUB', 'b_TD', 'b_TD_PRCT','b_TTLSTR', 'b_TTLSTR_PRCT'
                ,'red_fighter','r_KD', 'r_PASS', 'r_SIGSTR', 'r_SIGSTR_PRCT', 'r_SUB', 'r_TD', 'r_TD_PRCT', 'r_TTLSTR', 'r_TTLSTR_PRCT']
        self.feature_col = ['b_KD', 'b_PASS', 'b_SIGSTR', 'b_SIGSTR_PRCT', 'b_SUB', 'b_TD', 'b_TD_PRCT', 'b_TTLSTR', 'b_TTLSTR_PRCT',
                'r_KD', 'r_PASS', 'r_SIGSTR', 'r_SIGSTR_PRCT', 'r_SUB', 'r_TD', 'r_TD_PRCT', 'r_TTLSTR', 'r_TTLSTR_PRCT']

    def p2f(self,str):
        return(float(str.strip('%'))/100)
    def weird_div(self,n,d):
        return n/d if d else 0

    ### Populate the dataframe with the averages of fighters
    ### selects winners, formats data 

    ### if both of the fighter's names are filled, it computes the average and returns a playload 
    ### if the both names are '' then it collects all of the fights
    def populate_dataframes(self,data_frame, red_fighter, blue_fighter,connection):
        #blue fighter, red fighter
        #vars to calculate avgs of respective fighters
        avg_rsigstr = avg_rsigstr_prct = avg_rTD_prct = avg_rTD = avg_rKD = avg_rpass = avg_rsub = avg_rttlstr = avg_rttlstr_prct = 0 
        avg_bsigstr = avg_bsigstr_prct = avg_bTD_prct = avg_bTD = avg_bKD = avg_bpass = avg_bsub = avg_bttlstr = avg_bttlstr_prct = 0 
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
            TD_PRCT = self.p2f(rows['r_TD_PRCT'])
            TTLSTR = int(rows['r_TTLSTR'].split('/')[1])
            try:
                TTLSTR_PRCT = float(int(rows['r_TTLSTR'].split('/')[0])/int(rows['r_TTLSTR'].split('/')[1]))
            except ZeroDivisionError:
                TTLSTR_PRCT = float(0)
            SIGSTR = int(rows['r_SIGSTR'].split('/')[1])
            SIGSTR_PRCT = self.p2f(rows['r_SIGSTR_PRCT'])

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
                avg_rttlstr_prct +=TTLSTR_PRCT
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
                avg_bttlstr_prct += TTLSTR_PRCT
                blue_cnt+=1

                #################Blue side#################################################    
            TD=0
            try:
                TD = int(rows['b_TD'].split('/')[1])
            except (ValueError, IndexError):
                TD = int(rows['b_TD'].split('of')[1])
            TD_PRCT = self.p2f(rows['b_TD_PRCT'])
            TTLSTR = int(rows['b_TTLSTR'].split('/')[1])
            try:
                TTLSTR_PRCT = float(int(rows['b_TTLSTR'].split('/')[0])/int(rows['b_TTLSTR'].split('/')[1]))
            except (ZeroDivisionError):
                TTLSTR_PRCT = float(0)
            SIGSTR = int(rows['b_SIGSTR'].split('/')[1])
            SIGSTR_PRCT = self.p2f(rows['b_SIGSTR_PRCT'])

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
                avg_bttlstr_prct += TTLSTR_PRCT
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
                avg_rttlstr_prct += TTLSTR_PRCT
                red_cnt +=1

        if(blue_fighter == '' and red_fighter == ''):
            return {}
        else:
            return {'blue_fighter':blue_fighter,'b_KD':self.weird_div(avg_bKD,blue_cnt), 'b_PASS':self.weird_div(avg_bpass,blue_cnt),
                'b_SIGSTR':self.weird_div(avg_bsigstr,blue_cnt), 'b_SIGSTR_PRCT':self.weird_div(avg_bsigstr_prct,blue_cnt)
                , 'b_SUB':self.weird_div(avg_bsub,blue_cnt), 'b_TD': self.weird_div(avg_bTD,blue_cnt), 'b_TD_PRCT':self.weird_div(avg_bTD_prct,blue_cnt),
                 'b_TTLSTR':self.weird_div(avg_bttlstr,blue_cnt) ,'b_TTLSTR_PRCT':self.weird_div(avg_bttlstr_prct,blue_cnt),
                'red_fighter':red_fighter,'r_KD':self.weird_div(avg_rKD,red_cnt), 'r_PASS':self.weird_div(avg_rpass,red_cnt),
                'r_SIGSTR':self.weird_div(avg_rsigstr,red_cnt), 'r_SIGSTR_PRCT':self.weird_div(avg_rsigstr_prct,red_cnt), 'r_SUB':self.weird_div(avg_rsub,red_cnt),
                'r_TD':self.weird_div(avg_rTD,red_cnt), 'r_TD_PRCT':self.weird_div(avg_rTD_prct,red_cnt),
                'r_TTLSTR':self.weird_div(avg_rttlstr,red_cnt),'r_TTLSTR_PRCT':self.weird_div(avg_rttlstr_prct,red_cnt)}

    ### Grabs the data from the sql DB and performs preprocessing.
    ### returns the training sets.
    def generate_data(self):
        #weight class
        weight_class = 'Welterweight'
        blue_payload = 'blue_fighter,b_KD, b_PASS, b_SIGSTR, b_SIGSTR_PRCT, b_SUB, b_TD, b_TD_PRCT, b_TTLSTR'
        red_payload = 'red_fighter, r_KD, r_PASS, r_SIGSTR, r_SIGSTR_PRCT, r_SUB, r_TD, r_TD_PRCT, r_TTLSTR'
        stats_payload = 'winner, loser, end_round, time, method, result'
        ###dataframe for fighter averages in the predict list

        #query for weight class
        weight_query = "SELECT * FROM bouts WHERE weight_class='Welterweight' or weight_class='Light Heavyweight' or weight_class='Bantamweight' or weight_class LIKE '%Strawweight'"
        weight_query = "SELECT * FROM bouts"
        #weight_query = "SELECT * FROM bouts WHERE red_fighter='Macy Chiasson' or blue_fighter='Macy Chiasson'" 
        
        #queries for the fighters in some bout
        weight_frame = pd.read_sql(weight_query, self.connection)
        weight_frame["b_win"] = 0
        weight_frame["r_win"] = 0

        self.populate_dataframes(weight_frame, '','', self.connection)

        X = weight_frame[self.feature_col]
        y = weight_frame.r_win
        #weight_frame.to_csv('test.csv')
        #print(X,y)
        #split X and y into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.32, random_state=0)
        return X_train, X_test, y_train, y_test

    def train_predictionModel(self,model_type, X_train, X_test, y_train, y_test):
        y_train = y_train.astype('int')
        if(model_type == 'LR'):
            # instantiate the model (using the default parameters)
            model = LogisticRegression()
        elif(model_type =='clf'):
            model = tree.DecisionTreeRegressor()
        elif(model_type =='perp'):
            model = Perceptron(penalty='l2') 
        elif(model_type == 'SGD'):
            model = SGDClassifier(warm_start=True)

        # fit the model with data
        model.fit(X_train,y_train)
        #
        y_pred = model.predict(X_test)
        filename = 'trained_Kev.sav'
        pickle.dump(model, open(filename, 'wb'))

        print('################################################################################')
        print("Accuracy:",metrics.accuracy_score(y_test, y_pred))
        print("Precision:",metrics.precision_score(y_test, y_pred))
        print("Recall:",metrics.recall_score(y_test, y_pred))

    def predict(self):
        #path = '/var/www/UFC_API/'
        path = 'C:/Users/maverick/Documents/VS_Workspace/UFC_API/'
        filename = 'trained_Kev.sav'
        loaded_module = pickle.load(open(path + filename,'rb'))
        out_json = {}

        #(blue, red)
        fobj = open(path + "bout_list3.txt", "r")
        odd=False
        red_fighter=''
        blue_fighter=''
        fight_list = []
        out_json['event'] = fobj.readline().strip('\n')
        for line in fobj:
            if(odd):
                blue_fighter = line.replace("'","''")
                fight_list.append((red_fighter.strip('\n'),blue_fighter.strip('\n')))
                odd=False
            elif(not odd):
                red_fighter = line.replace("'","''")
                odd=True

        data = []
        for(red_fighter,blue_fighter) in fight_list:
            blue_fighter_query = "SELECT * FROM bouts WHERE blue_fighter='" + blue_fighter +"' or red_fighter='" + blue_fighter + "'"
            red_fighter_query = "SELECT * FROM bouts WHERE blue_fighter='" + red_fighter +"' or red_fighter='" + red_fighter + "'"
            #blue_fighter_query = "SELECT * FROM bouts WHERE blue_fighter=%(blue_fighter)s or red_fighter=%(blue_fighter)s"
            #red_fighter_query = "SELECT * FROM bouts WHERE blue_fighter=%(red_fighter)s or red_fighter=%(red_fighter)s"
            union_query = blue_fighter_query + ' UNION ' + red_fighter_query
            fighter_frame = pd.read_sql(union_query, self.connection, params={'blue_fighter':"'" + blue_fighter + "'",'red_fighter':"'"+ red_fighter+ "'"})
            #print(fighter_frame)
            fighter_frame["b_win"] = 0
            fighter_frame["r_win"] = 0
            #out_fighters is a dataframe with all the averages of the to-be predicted fighters

            data.append(self.populate_dataframes(fighter_frame, blue_fighter,red_fighter, self.connection))
        print(data)
        out_fighters = pd.DataFrame(data,columns=self.columns)
        print(out_fighters)

        prediction = loaded_module.predict(out_fighters[self.feature_col])
        count = 0
        payload = [] 
        
        print("###############################################################################################")
        for res in prediction:
            fight = {'Winner':'', 'Loser':''} 
            print(res)
            print(fight_list[count])
            if res == 1:
                fight['Winner'] = (fight_list[count][0])
                fight['Loser'] = (fight_list[count][1])
            else:
                fight['Winner'] = (fight_list[count][1])
                fight['Loser'] = (fight_list[count][0])
            count+=1
            payload.append(fight)

        out_json['bouts'] = payload
        return out_json 

def main():
    pm = Predictions()
    X_train, X_test, y_train, y_test = pm.generate_data()
    pm.train_predictionModel('LR', X_train, X_test, y_train, y_test)
    path = '/var/www/UFC_API/'
    data = pm.predict()
    
    with(open(path + 'pred_fights.json','w')) as f:
            json.dump(data,f)


if __name__ == '__main__':
    main()
