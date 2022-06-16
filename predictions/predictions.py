from cgitb import text
from json import load
import pandas as pd
import pickle, os
from typing import Any,Dict, Sequence, Tuple, List

#sklearn modules
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import Perceptron
from sklearn.linear_model import SGDClassifier 

from sklearn import metrics, tree

class Predictions():
    """
    Provides methods to help train models and use them with DB data.
    """
    def __init__(self,db_engine:Any):
        """
        connection -> connection to the DB specified by db_engine.
        columns -> DB columns as a list

        Args:
            db_engine (Engine): Engine created from create_engine()
        """
        #db i'm accessing
        self.db_engine = db_engine
        self.connection = self.db_engine.connect()
        self.columns = ['blue_fighter','b_KD', 'b_PASS', 'b_SIGSTR', 'b_SIGSTR_PRCT', 'b_SUB', 'b_TD', 'b_TD_PRCT','b_TTLSTR', 'b_TTLSTR_PRCT'
                ,'red_fighter','r_KD', 'r_PASS', 'r_SIGSTR', 'r_SIGSTR_PRCT', 'r_SUB', 'r_TD', 'r_TD_PRCT', 'r_TTLSTR', 'r_TTLSTR_PRCT']
        self.feature_col = ['b_KD', 'b_PASS', 'b_SIGSTR', 'b_SIGSTR_PRCT', 'b_SUB', 'b_TD', 'b_TD_PRCT', 'b_TTLSTR', 'b_TTLSTR_PRCT',
                'r_KD', 'r_PASS', 'r_SIGSTR', 'r_SIGSTR_PRCT', 'r_SUB', 'r_TD', 'r_TD_PRCT', 'r_TTLSTR', 'r_TTLSTR_PRCT']

    def p2f(self,s:str) -> float:
        """
        Given a string like 23%, return the float value of it, 0.23
        """
        if s == '---':
            return float(0.0)
        return float(s.strip('%'))/100

    def weird_div(self,n,d):
        """
        compute n/d, but if d is 0, return 0.
        """
        return n/d if d else 0

    def populate_dataframes(self,data_frame:pd.DataFrame, red_fighter:str, blue_fighter:str,connection) -> Dict[str,float]:
        """
        Converts values from the data_frame into ints for numpy and sklearn to use it in predictions.

        If both of the fighter's names are specified, it computes the average for those figthers and returns a playload. 
        If the both names are '' then it won't return anything. 
        """
        #blue fighter, red fighter
        #vars to calculate avgs of respective fighters
        avg_rsigstr = avg_rsigstr_prct = avg_rTD_prct = avg_rTD = avg_rKD = avg_rpass = avg_rsub = avg_rttlstr = avg_rttlstr_prct = 0 
        avg_bsigstr = avg_bsigstr_prct = avg_bTD_prct = avg_bTD = avg_bKD = avg_bpass = avg_bsub = avg_bttlstr = avg_bttlstr_prct = 0 
        #count how many fights each fighter had
        red_cnt = 0
        blue_cnt = 0
        for index, rows in data_frame.iterrows():
            ### Set b_win or r_win depending on who won this bout.
            if(rows['winner'] == rows['blue_fighter']):
                data_frame.at[index, 'b_win']= 1
                data_frame.at[index, 'r_win']= 0
            elif(rows['winner'] == rows['red_fighter']):
                data_frame.at[index, 'b_win']= 0
                data_frame.at[index, 'r_win']= 1
            else:
                data_frame.at[index, 'b_win']= 0
                data_frame.at[index, 'r_win']= 0

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

    def generate_data(self) -> Tuple[Sequence,Any,List]:
        """
        Processes the data from the SQL DB, and performs preprocessing
        
        Returns X_train, X_test,Y_train,y_test
        """
        #query for weight class
        weight_query = "SELECT * FROM bouts"

        #queries for the fighters in some bout
        weight_frame = pd.read_sql(weight_query, self.connection)
        weight_frame["b_win"] = 0
        weight_frame["r_win"] = 0

        self.populate_dataframes(weight_frame, '','', self.connection)

        X = weight_frame[self.feature_col]
        y = weight_frame.r_win
        #split X and y into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.32, random_state=0)
        return X_train, X_test, y_train, y_test

    def train_predictionModel(self,model_type:str, X_train, X_test, y_train, y_test):
        """
        Given the training sets, and model_type, trains a prediction model based on that model type.

        ModelTypes: LR, clf, perp, SGD

        Writes to a pickle obj called trained_Kev.sav
        """
        y_train = y_train.astype('int')
        if(model_type == 'LR'):
            # instantiate the model (using the default parameters)
            model = LogisticRegression(max_iter=1500)
        elif(model_type =='clf'):
            model = tree.DecisionTreeRegressor()
        elif(model_type =='perp'):
            model = Perceptron(penalty='l2') 
        elif(model_type == 'SGD'):
            model = SGDClassifier(warm_start=True)
        else:
            raise Exception("Invalid model type.")

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

    def predict(self, red_fighter=None,blue_fighter=None) -> Dict[str,Any]:
        """
        Predicts fights from the boutlist generated by the gatherData program.
        If red fighter and blue fighter are specified, will only predict for red and blue.

        Returns a json with the prediction results.

        Parameters:
        red_fighter (str): Name of red fighter.
        blue_fighter (str): Name of blue fighter.
        """
        if (not red_fighter or not blue_fighter):
            raise Exception("Both red fighter and blue fighter must be filled.")

        def predict_from_boutListing(fight_list):
            #(blue, red)

            with open(path + "/bout_list.txt", "r") as fobj:
                blue_fighter=''
                out_json['event'] = fobj.readline().strip('\n')
                ### fobj, each line is a fighter name.
                ### every 2 lines is one bout.
                for line in fobj:
                    red_fighter,blue_fighter = line.split('|')

                    red_fighter = red_fighter.replace("'","''").strip('\n')
                    blue_fighter = blue_fighter.replace("'","''").strip('\n')
                    fight_list.append((red_fighter,blue_fighter))

            data = []
            for(red_fighter,blue_fighter) in fight_list:
                ### sqlalchemy parameterized query syntax is :parameter
                blue_fighter_query = "SELECT * FROM bouts WHERE blue_fighter= :blue_fighter or red_fighter= :blue_fighter"
                red_fighter_query = "SELECT * FROM bouts WHERE blue_fighter= :red_fighter or red_fighter= :red_fighter"
                union_query = blue_fighter_query + ' UNION ' + red_fighter_query
                fighter_frame = pd.read_sql(union_query, self.connection, params={'blue_fighter':blue_fighter,'red_fighter':red_fighter})
                fighter_frame["b_win"] = 0
                fighter_frame["r_win"] = 0

                #out_fighters is a dataframe with all the averages of the to-be predicted fighters
                data.append(self.populate_dataframes(fighter_frame, blue_fighter,red_fighter, self.connection))
            #print(data)
            out_fighters = pd.DataFrame(data,columns=self.columns)
            return out_fighters
        def predict_two_fighters(red_fighter,blue_fighter,fight_list):
            fight_list.append((red_fighter.strip('\n'), blue_fighter.strip('\n')))
            data = []
            ### sqlalchemy parameterized query syntax is :parameter
            blue_fighter_query = "SELECT * FROM bouts WHERE blue_fighter= :blue_fighter or red_fighter= :blue_fighter"
            red_fighter_query = "SELECT * FROM bouts WHERE blue_fighter= :red_fighter or red_fighter= :red_fighter"
            union_query = blue_fighter_query + ' UNION ' + red_fighter_query
            fighter_frame = pd.read_sql(union_query, self.connection, params={'blue_fighter':red_fighter,'red_fighter':blue_fighter})
            fighter_frame["b_win"] = 0
            fighter_frame["r_win"] = 0
            #out_fighters is a dataframe with all the averages of the to-be predicted fighters

            data.append(self.populate_dataframes(fighter_frame, blue_fighter,red_fighter, self.connection))
            print(data)
            out_fighters = pd.DataFrame(data,columns=self.columns)
            return out_fighters


        path = os.getcwd()
        model_filename = '/trained_Kev.sav'
        
        with open(path + model_filename,'rb') as pkl_f:
            prediction_module = pickle.load(pkl_f)

            out_json = {}
            ### List to store each bout,needed to link back to predict.
            fight_list = []

            if red_fighter and blue_fighter:
                out_fighters = predict_two_fighters(red_fighter,blue_fighter,fight_list)
                prediction = prediction_module.predict(out_fighters[self.feature_col])
            else:
                out_fighters = predict_from_boutListing(fight_list)
                prediction = prediction_module.predict(out_fighters[self.feature_col])

            payload = [] 
            ## Prediction will have values 0 or 1. If 1 it means RED fighter in that bout will win, else the BLUE fighter will win.
            for idx,res in enumerate(prediction):
                fight = {} 
                if res == 1:
                    fight['Winner'] = (fight_list[idx][1])
                    fight['Loser'] = (fight_list[idx][0])
                else:
                    fight['Winner'] = (fight_list[idx][0])
                    fight['Loser'] = (fight_list[idx][1])
                payload.append(fight)

            out_json['predictions'] = payload
            return out_json 
