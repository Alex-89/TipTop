# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 23:17:36 2019

@author: Alexa
"""

from ipdb import set_trace

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

import matplotlib.pyplot as plt
import matplotlib

import numpy as np

#import seaborn as sns

class TipTop_TipGeneration():
    def __init__(self, parameter, df_analysis, obj_scraper):
        self.__df_parameter = parameter
        self.__df_analysis = df_analysis
        
        self.__obj_scraper = obj_scraper
        
    def calc_analysis(self):        
        
        
        self.__dict_analysis = dict()
        for index_tab, row in self.__df_analysis.iterrows():            
            self.__dict_analysis[row.Description] = dict()
            
            team1, team2 = row.Team_1, row.Team_2

            df = self.__obj_scraper.get_df_Football_games            
            
            df_first_leg = df[(df["str_Team1"]==team1) & (df["str_Team2"]==team2)][["int_Scour_Team1", "int_Scour_Team2"]]
            df_return_leg = df[(df["str_Team2"]==team1) & (df["str_Team1"]==team2)][["int_Scour_Team1", "int_Scour_Team2"]]
            

            df_first_leg = df_first_leg.rename(columns={"int_Scour_Team1": team1, "int_Scour_Team2": team2})        
            df_return_leg = df_return_leg.rename(columns={"int_Scour_Team2": team1, "int_Scour_Team1": team2})  
            
            df_first_leg.to_excel("first_leg.xlsx")
            df_return_leg.to_excel("return_leg.xlsx")
           
            
            self.calc_statistic_key_performance_indicator(row.Description, df_first_leg,df_return_leg)      
            
            self.calc_histogram(df_first_leg, df_return_leg, team1, team2, row.Description)
            
            self.plot_scatter(df_first_leg, df_return_leg, team1, team2, row.Description)
            
    
    def calc_statistic_key_performance_indicator(self, analysis_descirption, df_first_leg, df_return_leg):
        
        count_games = len(df_first_leg.index) + len(df_return_leg.index)
        
        self.__dict_analysis[analysis_descirption]["count_games"] = count_games
        
    
    def calc_histogram(self, df_first_leg, df_return_leg, team1, team2, str_description):
        
        font = {'family' : "Times New Roman"}
        matplotlib.rc('font', **font)                
                
#        sns.set_style("whitegrid")
        df_games = df_first_leg.append(df_return_leg)
        int_count_games = len(df_games.index)
                
        df_games_count_probability = df_games.groupby([team1, team2]).size() / int_count_games *100
        df_games_count_probability.columns = ["Score"]
        
        df_games_count_probability.to_excel("groupby_" + str_description + ".xlsx")
        
        fig, ax = plt.subplots()
        fig.set_size_inches(25,8)
        
#        sns.distplot(df_games_count_probability.values, 
#                     ax=ax, bins=len(df_games_count_probability.values),
#                     rug=True, hist=False)
        
        ax.set_xlim(0, len(df_games_count_probability.index))
        ax.bar(len(df_games_count_probability.values), df_games_count_probability.values)
       
        ax.set_xlabel("Football results", fontsize=35)
        ax.set_ylabel("Probability", fontsize=35)
        ax.set_title(str_description + " probability plot", fontsize=40)
                
        ax.set_xticks(list(range(0,len(df_games_count_probability.index)+1)))
        ax.set_xticklabels([str(tup_label) for tup_label in df_games_count_probability.index])
        
        ax.tick_params(labelsize=20)
        ax.tick_params(labelsize=20)
        
        fig.savefig(str_description + "_hist_plot.pdf")
        
        
    
    def plot_scatter(self, df_first_leg, df_return_leg, team1, team2, str_description):
        
        plt.rcParams["font.family"] = "Times New Roman"
        
#        sns.set_style("whitegrid")
        
        
        font = {'family' : "Times New Roman"}

        matplotlib.rc('font', **font)
        
        fig, ax = plt.subplots()
        fig.set_size_inches(18,8)
                        
        ax.scatter( x = df_first_leg[team1], y = df_return_leg[team2], color="#a83232", label="first leg")
        ax.scatter( x = df_return_leg[team1], y = df_return_leg[team2],  color="#9aa832", label="return leg")
                   
        arr1 = df_first_leg.values
        arr2 = df_return_leg.values
        
        arr = np.append(arr1, arr2, axis=0)
        
        X_train, X_test, y_train, y_test = train_test_split(arr[:,0], 
                                                            arr[:,1], 
                                                            test_size=0.2, 
                                                            random_state=0)
                
        regressor = LinearRegression()
        regressor.fit(X_train.reshape(-1,1), y_train.reshape(-1,1))
                           
        X_values = X_train
        X_values.sort()
        Y_values = regressor.predict(X_values.reshape(-1,1))
        
        ax.plot(X_values, Y_values, label="Regressions",  color="#ff6200")
        
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels, fontsize=30)
        
        ax.set_xlabel(team1, fontsize=35)
        ax.set_ylabel(team2, fontsize=35)
        ax.set_title(str_description, fontsize=40)
        
        ax.tick_params(labelsize=20)
        ax.tick_params(labelsize=20)
        
        self.__dict_analysis[str_description]["scatter_plot"] = (fig, ax)
                           
        fig.savefig(str_description + "_scatter_plot.pdf")
        
                
    @property
    def get_analysis(self):
        return self.__dict_analysis