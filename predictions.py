from ufc_api import db
from config import Config
from sqlalchemy import create_engine
from models import Events, Bouts
import pandas as pd
import pickle
import sys

#sklearn modules
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics

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

    def train_predictionModel(self):
        #weight class
        weight_class = 'Welterweight'
        blue_payload = 'blue_fighter,b_KD, b_PASS, b_SIGSTR, b_SIGSTR_PRCT, b_SUB, b_TD, b_TD_PRCT, b_TTLSTR'
        red_payload = 'red_fighter, r_KD, r_PASS, r_SIGSTR, r_SIGSTR_PRCT, r_SUB, r_TD, r_TD_PRCT, r_TTLSTR'
        stats_payload = 'winner, loser, end_round, time, method, result'
        ###dataframe for fighter averages in the predict list

        #query for weight class
        weight_query = "SELECT * FROM bouts WHERE weight_class='Welterweight' or weight_class='Light Heavyweight' or weight_class='Bantamweight' or weight_class LIKE '%Strawweight'"
        
        #queries for the fighters in some bout
        weight_frame = pd.read_sql(weight_query, self.connection)
        weight_frame["b_win"] = 0
        weight_frame["r_win"] = 0

        self.populate_dataframes(weight_frame, '','', self.connection)


        X = weight_frame[self.feature_col]
        y = weight_frame.r_win

        #split X and y into training and testing sets
        #X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.25, random_state=0)
        X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.25, random_state=0)


        # instantiate the model (using the default parameters)
        logreg = LogisticRegression()
        y_train = y_train.astype('int')
        # fit the model with data
        logreg.fit(X_train,y_train)
        #
        y_pred=logreg.predict(X_test)

        filename = 'trained_Kev.sav'
        pickle.dump(logreg, open(filename, 'wb'))
        print('################################################################################')
        count = 0
        print("Accuracy:",metrics.accuracy_score(y_test, y_pred))
        print("Precision:",metrics.precision_score(y_test, y_pred))
        print("Recall:",metrics.recall_score(y_test, y_pred))

    def predict(self):
        filename = 'trained_Kev.sav'
        loaded_module = pickle.load(open(filename,'rb'))

        #(blue, red)
        fobj = open("bout_list.txt", "r")
        odd=True
        red_fighter=''
        blue_fighter=''
        fight_list = []
        for line in fobj:
            if(odd):
                red_fighter = line
                odd=False
            elif(not odd):
                blue_fighter = line
                fight_list.append((red_fighter.strip('\n'),blue_fighter.strip('\n')))
                odd=True

        data = []
        for(blue_fighter, red_fighter) in fight_list:
            blue_fighter_query = "SELECT * FROM bouts WHERE blue_fighter='" + blue_fighter +"' or red_fighter='" + blue_fighter + "'"
            red_fighter_query = "SELECT * FROM bouts WHERE blue_fighter='" + red_fighter +"' or red_fighter='" + red_fighter + "'"
            union_query = blue_fighter_query + ' UNION ' + red_fighter_query
            fighter_frame = pd.read_sql(union_query, self.connection)
            fighter_frame["b_win"] = 0
            fighter_frame["r_win"] = 0
            #out_fighters is a dataframe with all the averages of the to-be predicted fighters

            data.append(self.populate_dataframes(fighter_frame, blue_fighter,red_fighter, self.connection))
        out_fighters = pd.DataFrame(data,columns=self.columns)

        prediction = loaded_module.predict(out_fighters[self.feature_col])
        count = 0
        payload = [] 
        
        for res in prediction:
            fight = {'Winner':'', 'Loser':''} 
            if res == 1:
                fight['Winner'] = (fight_list[count][0])
                fight['Loser'] = (fight_list[count][1])
            else:
                fight['Winner'] = (fight_list[count][0])
                fight['Loser'] = (fight_list[count][1])
            count+=1
            payload.append(fight)

        return payload 

def main():
    pm = Predictions()
    data = pm.predict()
    to_json={}
    to_json['bouts']=data
    with(open('pred_fights.json','w')) as f:
            json.dump(to_json,f)


if __name__ == '__main__':
    main()