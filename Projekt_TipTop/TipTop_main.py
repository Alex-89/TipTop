# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 22:16:06 2019

@author: Alexander Hobert
"""


from pandas import read_excel

from Datamining_modul.Scraping_modul import TipTop_scraper
from TipGeneration.TipTop_TipGeneration import TipTop_TipGeneration



def TipTop_main(df_parameter, df_analysis):
    
    obj_sraper = TipTop_scraper(df_parameter)
    obj_sraper.download_datas()
    
    obj_tipgeneratoin = TipTop_TipGeneration(df_parameter, df_analysis, obj_sraper) 
    obj_tipgeneratoin.calc_analysis()
    
    
    return obj_sraper, obj_tipgeneratoin

df_parameter = read_excel("TipTop_parameter.xlsx", index_col=0)
df_analysis = read_excel("TipTop_analysis.xlsx", index_col=0)
obj_scraper, obj_tipgeneration = TipTop_main(df_parameter, df_analysis)


df_games = obj_scraper.get_df_Football_games
df_games.to_excel("football_games.xlsx")

df_teams = obj_scraper.get_df_Football_teams
df_teams.to_excel("football_teams.xlsx")