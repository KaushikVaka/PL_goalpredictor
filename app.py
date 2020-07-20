from flask import Flask, render_template, request
import pickle
import numpy as np
import pandas as pd
from random import choices

filename='Premier-League-Prediction-model.pkl'
rf_regressor=pickle.load(open(filename,'rb'))

PL_matchresults=pd.read_csv('All_stats.csv')
Players={"Man City":"Aguero,KevinDebruyne,Sterling,Mahrez,DavidSilva,Fernandinho,PhilFoden,Laporte,Mendy,Walker,Ederson",  
             "Liverpool":"Mane,Salah,Firminho,TrentAlexanderArnold,Robertson,OxladeChamberlain,Fabinho,Henderson,VanDijk,Gomez,Alisson",
             "Man United":"Rashford,Martial,BrunoFernandes,Greenwood,Pogba,Fred,WanBissaka,Maguire,Lindelof,Shaw,DeGea"}
app = Flask(__name__)

@app.route('/')
def home():
	return render_template('index.html')

@app.route('/result',methods=['POST'])
def predict():
    temp_array=list()
    
    
    
    
    teams=['Arsenal','Aston Villa','Bournemouth','Brighton','Burnley',
                    'Chelsea','Crystal Palace','Everton','Fulham',
                    'Huddersfield','Leicester','Liverpool','Man City','Man United',
                    'Newcastle','Southampton','Swansea','Tottenham','Watford','West Ham',
                     'Wolves']
    ones_array_1=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    ones_array_2=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    
    if request.method == 'POST':
        hometeam_shots=int(request.form['hometeam_shotsOnTarget'])
        awayteam_shots=int(request.form['awayteam_shotsOnTarget'])
        
        
        home_team=request.form['home_team']
        away_team=request.form['away_team']
        
        team_1=[home_team]
        team_2=[away_team]
        
       
        prob_home_team=PL_matchresults[PL_matchresults['HomeTeam'].isin(team_1) & PL_matchresults['AwayTeam'].isin(team_2)]['B365H'].mean()
        prob_away_team=PL_matchresults[PL_matchresults['HomeTeam'].isin(team_1) & PL_matchresults['AwayTeam'].isin(team_2)]['B365A'].mean()
        prob_draw=PL_matchresults[PL_matchresults['HomeTeam'].isin(team_1) & PL_matchresults['AwayTeam'].isin(team_2)]['B365D'].mean()

        temp_array=temp_array+[hometeam_shots,awayteam_shots,prob_home_team,prob_away_team,prob_draw]
       
        for team in range(len(teams)):
            if teams[team]==home_team:
                ones_array_1[team]=1
        temp_array=temp_array+ones_array_1
       
        
        for team in range(len(teams)):
            if teams[team]==away_team:
                ones_array_2[team]=1
        temp_array=temp_array+ones_array_2
       
        
        
        def GoalScorer_home(ht):
            weights=[0.2,0.2,0.15,0.15,0.05,0.05,0.05,0.05,0.05,0.05,0]
            return choices(ht,weights=weights)[0]
        
        def GoalScorer_away(at):
            weights=[0.2,0.2,0.15,0.15,0.05,0.05,0.05,0.05,0.05,0.05,0]
            return choices(at,weights=weights)[0]
        
        
        team_data=np.array([temp_array])
        prediction=rf_regressor.predict(team_data)[0]
        prediction=prediction.astype(int)
       
        
        homegoal_scorers=list()
        awaygoal_scorers=list()
        home_goals=0
        away_goals=0
        if home_team in Players.keys():
            while home_goals<prediction[0]:
                homegoal_scorers.append(GoalScorer_home(Players[home_team].split(",")))
                home_goals+=1
        
        if away_team in Players.keys():
            while away_goals<prediction[1]:
                awaygoal_scorers.append(GoalScorer_away(Players[away_team].split(",")))
                away_goals+=1
        
            
        
        
        
        return render_template('result.html', hometeam_goals =prediction[0],awayteam_goals =prediction[1],gsh=homegoal_scorers,gsa=awaygoal_scorers)
    
if __name__ == '__main__':
	app.run(debug=True)
