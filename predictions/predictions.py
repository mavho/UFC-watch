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
        self.columns = [
            'blue_fighter',
            'b_KD',
            'b_REV',
            'b_LAND_SIGSTR',
            'b_TTL_SIGSTR',
            'b_SUB',
            'b_LAND_TD',
            'b_TTL_TD',
            'b_TTL_STR',
            'b_LAND_STR',
            'b_CNTRL_SEC',
            'red_fighter',
            'r_KD',
            'r_REV',
            'r_LAND_SIGSTR',
            'r_TTL_SIGSTR',
            'r_SUB',
            'r_LAND_TD',
            'r_TTL_TD',
            'r_TTL_STR',
            'r_LAND_STR',
            'r_CNTRL_SEC',
        ]
        self.feature_col = [
            'b_KD',
            'b_REV',
            'b_LAND_SIGSTR',
            'b_TTL_SIGSTR',
            'b_SUB',
            'b_LAND_TD',
            'b_LAND_STR',
            'b_CNTRL_SEC',
            'r_KD',
            'r_REV',
            'r_LAND_SIGSTR',
            'r_TTL_SIGSTR',
            'r_SUB',
            'r_LAND_TD',
            'r_LAND_STR',
            'r_CNTRL_SEC',
        ]

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

        If both of the fighter's names are specified, it computes the average for those fighters and returns a payload. 
        If the both names are '' then it won't return anything. 
        """
        #blue fighter, red fighter
        #vars to calculate avgs of respective fighters
        avg_rsigstr_land = avg_rsigstr_ttl = avg_rTD_land = avg_rTD_ttl = avg_rKD = avg_rrev = avg_rsub = avg_rstr_land = avg_rstr_ttl = 0 
        avg_bsigstr_land = avg_bsigstr_ttl = avg_bTD_land = avg_bTD_ttl = avg_bKD = avg_brev = avg_bsub = avg_bstr_land = avg_bstr_ttl = 0 
        avg_rcntrl_sec = 0
        avg_bcntrl_sec = 0
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

            data_frame.at[index,'r_LAND_STR']=rows['r_LAND_STR']
            data_frame.at[index,'r_TTL_STR']=rows['r_TTL_STR']
            data_frame.at[index,'r_LAND_SIGSTR']=rows['r_LAND_SIGSTR']
            data_frame.at[index,'r_TTL_SIGSTR']=rows['r_TTL_SIGSTR']
            data_frame.at[index,'r_LAND_TD']=rows['r_LAND_TD']
            data_frame.at[index,'r_TTL_LAND']=rows['r_TTL_TD']
            data_frame.at[index,'r_CNTRL_SEC']=rows['r_CNTRL_SEC']

            ### if red fighter was red fighter in this fight, add up the red stats
            if rows['red_fighter'] == red_fighter:
                avg_rTD_land += rows['r_LAND_TD']
                avg_rTD_ttl += rows['r_TTL_TD']

                avg_rsigstr_land += rows['r_LAND_SIGSTR']

                avg_rsigstr_ttl += rows['r_TTL_SIGSTR']

                avg_rstr_land+= rows['r_LAND_STR']

                avg_rstr_ttl += rows['r_TTL_STR']

                avg_rKD += rows['r_KD']
                avg_rrev += rows['r_REV']
                avg_rsub += rows['r_SUB']
                avg_rcntrl_sec += rows['r_CNTRL_SEC']
                red_cnt +=1

            ### if red fighter was blue fighter in this fight, add up the blue stats
            if rows['blue_fighter'] == red_fighter:
                avg_rTD_land += rows['b_LAND_TD']
                avg_rTD_ttl += rows['b_TTL_TD']

                avg_rsigstr_land += rows['b_LAND_SIGSTR']

                avg_rsigstr_ttl += rows['b_TTL_SIGSTR']

                avg_rstr_land+= rows['b_LAND_STR']

                avg_rstr_ttl += rows['b_TTL_STR']

                avg_rKD += rows['b_KD']
                avg_rrev += rows['b_REV']
                avg_rsub += rows['b_SUB']
                avg_rcntrl_sec += rows['b_CNTRL_SEC']

                blue_cnt+=1

                #################Blue side#################################################    

            data_frame.at[index,'b_LAND_STR']=rows['b_LAND_STR']
            data_frame.at[index,'b_TTL_STR']=rows['b_TTL_STR']
            data_frame.at[index,'b_LAND_SIGSTR']=rows['b_LAND_SIGSTR']
            data_frame.at[index,'b_TTL_SIGSTR']=rows['b_TTL_SIGSTR']
            data_frame.at[index,'b_LAND_TD']=rows['b_LAND_TD']
            data_frame.at[index,'b_TTL_LAND']=rows['b_TTL_TD']
            data_frame.at[index,'b_CNTRL_SEC']=rows['b_CNTRL_SEC']

            if rows['blue_fighter'] == blue_fighter:
                avg_bTD_land += rows['b_LAND_TD']
                avg_bTD_ttl += rows['b_TTL_TD']

                avg_bsigstr_land += rows['b_LAND_SIGSTR']

                avg_bsigstr_ttl += rows['b_TTL_SIGSTR']

                avg_bstr_land+= rows['b_LAND_STR']

                avg_bstr_ttl += rows['b_TTL_STR']

                avg_bKD += rows['b_KD']
                avg_brev += rows['b_REV']
                avg_bsub += rows['b_SUB']
                avg_bcntrl_sec += rows['b_CNTRL_SEC']
                blue_cnt +=1

            if rows['red_fighter'] == blue_fighter:
                avg_bTD_land += rows['r_LAND_TD']
                avg_bTD_ttl += rows['r_TTL_TD']

                avg_bsigstr_land += rows['r_LAND_SIGSTR']

                avg_bsigstr_ttl += rows['r_TTL_SIGSTR']

                avg_bstr_land+= rows['r_LAND_STR']

                avg_bstr_ttl += rows['r_TTL_STR']

                avg_bKD += rows['r_KD']
                avg_brev += rows['r_REV']
                avg_bsub += rows['r_SUB']
                avg_bcntrl_sec += rows['r_CNTRL_SEC']
                blue_cnt+=1

        if(blue_fighter == '' and red_fighter == ''):
            return {}

            # 'blue_fighter',
            # 'b_KD',
            # 'b_REV',
            # 'b_LAND_SIGSTR',
            # 'b_TTL_SIGSTR',
            # 'b_SUB',
            # 'b_LAND_TD',
            # 'b_TTL_STR',
            # 'b_LAND_STR',
            # 'b_CNTRL_SEC',
            # 'red_fighter',
            # 'r_KD',
            # 'r_REV',
            # 'r_LAND_SIGSTR',
            # 'r_TTL_SIG_STR',
            # 'r_SUB',
            # 'r_LAND_TD',
            # 'r_TTL_STR',
            # 'r_LAND_STR',
            # 'r_CNTRL_SEC',
        else:
            return {
                'blue_fighter':blue_fighter,
                'b_KD':self.weird_div(avg_bKD,blue_cnt),
                'b_REV':self.weird_div(avg_brev,blue_cnt),
                'b_LAND_SIGSTR':self.weird_div(avg_bsigstr_land,blue_cnt),
                'b_TTL_SIGSTR':self.weird_div(avg_bsigstr_ttl,blue_cnt),
                'b_SUB':self.weird_div(avg_bsub,blue_cnt),
                'b_LAND_TD': self.weird_div(avg_bTD_land,blue_cnt),
                'b_TTL_TD':self.weird_div(avg_bTD_land,blue_cnt),
                'b_TTL_STR':self.weird_div(avg_bstr_ttl,blue_cnt),
                'b_LAND_STR':self.weird_div(avg_bstr_land,blue_cnt),
                'b_CNTRL_SEC':self.weird_div(avg_rcntrl_sec,blue_cnt),

                'red_fighter':red_fighter,
                'r_KD':self.weird_div(avg_rKD,red_cnt),
                'r_REV':self.weird_div(avg_rrev,red_cnt),
                'r_LAND_SIGSTR':self.weird_div(avg_rsigstr_land,red_cnt),
                'r_TTL_SIGSTR':self.weird_div(avg_rsigstr_ttl,red_cnt),
                'r_SUB':self.weird_div(avg_rsub,red_cnt),
                'r_LAND_TD': self.weird_div(avg_rTD_land,red_cnt),
                'r_TTL_TD':self.weird_div(avg_rTD_ttl,red_cnt),
                'r_TTL_STR':self.weird_div(avg_rstr_ttl,red_cnt),
                'r_LAND_STR':self.weird_div(avg_rstr_land,red_cnt),
                'r_CNTRL_SEC':self.weird_div(avg_rcntrl_sec,red_cnt),
            }



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

    def train_predictionModel(self,model_type:str, X_train, X_test, y_train, y_test) -> List[float]:
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

        accuracy = metrics.accuracy_score(y_test,y_pred)
        # precision = metrics.precision(y_test,y_pred)
        precision = metrics.precision_score(y_test,y_pred)
        recall = metrics.recall_score(y_test,y_pred)
        print('################################################################################')
        print("Accuracy:",accuracy)
        print("Precision:",precision)
        print("Recall:",recall)

        return accuracy,precision,recall

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
            print(self.columns)
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
