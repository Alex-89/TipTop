# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 22:18:17 2019

@author: Alexander Hobert
"""

import requests
from bs4 import BeautifulSoup

from pandas import DataFrame

import numpy as np

import sqlite3

from ipdb import set_trace

from datetime import date, datetime

import string


class TipTop_scraper:
    
    def __init__(self, df_data_scources):
        self.__df_data_scources = df_data_scources
        
        self.__dict_Saisons = dict()
            
    def download_datas(self):
        print("Download championship overview")
        self.download_championship_overview(url = self.__df_data_scources.loc["url_Bundesliga_Tabelle", "Value"],
                                       source = self.__df_data_scources.loc["str_source", "Value"],
                                       url_base_source= self.__df_data_scources.loc["url_base_source", "Value"])
        
        self.download_saison_games()
        
        self.convert_obj_in_DataFrame()
        self.export_database()
    
    def download_obj(self, url):        
        response = requests.get(url)
        
        response.encoding = "cp1252"
        
        soup = BeautifulSoup(response.text, 'lxml')
        soup.decode('utf-8', 'ignore')
                    
        return soup
    
    def download_championship_overview(self, url, source, url_base_source):
        
        print("\tSelect the data scource")
        if source == "bulibox":        
            
            soup = self.download_obj(url)
            
            table_ = soup.find_all("table")[0]
            table = table_.find_all("tr")
            
            print("\tDownload the championship table")
            for i in range(len(table)):       
                row = table[i].find_all("td")       
                
                obj_championship = Championship()     
                
                for num_column, obj_column in enumerate(row):
                    
                    if num_column == 0:
                        str_saison_description = obj_column.text
                        obj_championship.set_description(str_saison_description)
                                                
                    elif num_column == 1:                        
                        obj_championship.set_final_table(str_final_table=obj_column.a.get("title"), 
                                                         url_final_table=url_base_source +   obj_column.a.get("href"))                        
                        
                        obj_championship.set_year(year_begin=obj_column.a.get("title").split()[1].replace("/", " ").split()[0],
                                                  year_end=obj_column.a.get("title").split()[1].replace("/", " ").split()[1]) 
                                            
                    elif num_column == 2:                        
                        obj_championship.set_result_table(str_results_table=obj_column.a.get("title"),
                                                          url_results_table=url_base_source + obj_column.a.get("href").replace(".",""))
                               
                    elif num_column == 3:
                        obj_championship.set_master(obj_column.text)
                        
                        self.__dict_Saisons[str_saison_description] = obj_championship
     
    def download_saison_games(self):
        print("Download saison Games")
        
        dict_teams = dict()   
        dict_football_game = dict()
        num_football_game = 0
        for championship_id, (championship_label, obj_championship) in enumerate(self.__dict_Saisons.items()):
            print("\tSaison: " + championship_label)
            
            soup = self.download_obj(obj_championship.get_url_result_table)            
            table_ = soup.find_all("table")            
#            table_ = soup.find_all("div")[15]
#            table = table_.find_all("tr")
                        
#            
#            if "/" in table[-1].text:
#                table = table[1:-1]
#            else:
#                table = table[1:]            
            
            dict_games = dict()
            dict_championship_game = dict()
            num_championship_football_game = 0 

            
            for num_championship_day, obj_championship_day in enumerate(table_):
                for num_row, obj_row in enumerate(obj_championship_day.find_all("tr")[1:]):                                      
                    
                    
                    obj_game = football_game()    
                    obj_game.set_saison(championship_id, obj_game)
                    
                    for num_column, obj_column in enumerate(obj_row.find_all("td")):                        

                        if num_column == 0:                            
                            obj_game.set_teams(obj_column.text)
                            
                            if obj_game.get_team1 not in dict_teams.keys():                                                      
                                dict_teams[obj_game.get_team1] = football_team(obj_game.get_team1)
                            
                            if obj_game.get_team2 not in dict_teams.keys():
                                dict_teams[obj_game.get_team2] = football_team(obj_game.get_team2)                            
                            
                        elif num_column == 1:                            
                            obj_game.set_scoure(obj_column.text)
                        
                        elif num_column == 2:
                            obj_game.set_date(obj_column.text)
                        
                        elif num_column == 3:
                            obj_game.set_url_statistic(obj_column.a.get("href"))

                    dict_championship_game[num_championship_football_game] = obj_game
                    dict_football_game[num_football_game] = obj_game
                    
                    num_championship_football_game += 1
                    num_football_game += 1
        
            obj_championship.set_dict_games(dict_championship_game)
            self.__dict_Saisons[championship_label] = obj_championship
            

                
            
        
        self.__dict_teams = dict_teams        
        self.__dict_foot_ball_games = dict_football_game
        
#        self.__dict_foot_ball_games = {(id_saison+1)*id_game: game for id_saison, (key_saison, championship) in enumerate(self.__dict_Saisons.items()) 
#                                                                       for id_game, (key_game, game) in enumerate(championship.get_dict_games.items())}
     
    def replace_column(self, str_column):
        
       str_chars = string.ascii_letters + string.digits + "ÄäÜüÖöß" + "-." + " "
       
       result = str_column.text
       
       list_chars = [string for string in result if string not in str_chars]
       
       
       while len(list_chars) > 0:         
           
           if "Ã¼" in result:    
    #           set_trace()
               result = result.replace("Ã¼", "ü")
           
           if "Ã¶" in result:    
    #           set_trace()
               result = result.replace("Ã¶", "ö")   
                
            
           if "Ã" in result:
    #           set_trace()
               result = result.replace("Ã", "")
                
            
           if "ÃŸ" in result:            
    #           set_trace()
               result = result.replace("ÃŸ", "ß")
               
           if "Ÿ" in result:
               result = result.replace("Ÿ", "ß")
                
            
           if "Â\xa0" in result:               
    #           set_trace()
               result = result.replace("Â\xa0", " ")
               
           list_chars = [string for string in result if string not in str_chars]


           
       if "- Blau" in result:        
           result = result.replace("- Blau", "")
           
       if "- Rot" in result:        
           result = result.replace("- Rot", "") 

       if " - Sport" in result:
           set_trace()
           result = result.replace(" - Sport", "")
       
        
       result = result.strip()
       
       return result
    
    
    def create_connection(self, db_file):        

        try:
            conn = sqlite3.connect(db_file + ".db")        
            obj_cursor = conn.cursor()        
            
            self.database_process(conn, obj_cursor)
          
            conn.commit()        
            obj_cursor.close()   
            
        except:
            
            work = True
            number = 1
            while work:
                try:
                    conn = sqlite3.connect(db_file + "_" + str(number) + ".db")        
                    obj_cursor = conn.cursor()        
                    
                    self.database_process(conn, obj_cursor)
                    
                    conn.commit()        
                    obj_cursor.close()
                    
                    work = False
                except:
                    obj_cursor.close()   
                    number +=1
        

    def database_process(self, conn, obj_cursor):       
        
        self.create_db_tables(obj_cursor)        
        
        self.insert_data_in_df_table(conn, obj_cursor, self.__df_Football_team, "Football_team", "Football_team_id, Team_name")        
        
        self.insert_data_in_df_table(conn, obj_cursor, self.__df_Saisons, "Saison", "Saaison_id, Saison_Description, Begin_Year, End_Year")
                
        self.insert_data_in_df_table(conn, obj_cursor, self.__df_Fotball_games, "Football_game", "Football_game_id, Team_1_name, Team_2_name, Score_Team_1, Score_Team_2, Date_game, id_Saison""")
    
    
    def create_db_tables(self, obj_cursor):
        
        obj_cursor.execute('''CREATE TABLE Saison
                             ([Saaison_id] INTEGER PRIMARY KEY,
                              [Saison_Description] text, 
                              [Begin_Year] date,
                              [End_Year] date)''')
        
                
        obj_cursor.execute('''CREATE TABLE Football_game
                             ([Football_game_id] INTEGER PRIMARY KEY,
                              [Team_1_name] text, 
                              [Team_2_name] text, 
                              [Date_game] date,
                              [Score_Team_1] integer,
                              [Score_Team_2] integer,
                              [id_Saison] integer)''')
        
        obj_cursor.execute('''CREATE TABLE Football_team
                             ([Football_team_id] INTEGER PRIMARY KEY,
                              [Team_name] text)''')
        
    
    
    def insert_data_in_df_table(self, conn, obj_cursor, df, str_table_name, columns):
                        
        for i, row in df.iterrows():            
            str_values = "'" + str(i) + "'"  + "".join(", '" + str(value) + "'" for value in row.values)
            
            sql = '''INSERT INTO {} ({}) VALUES ({});'''.format(str_table_name, columns, str_values)
            
            obj_cursor.execute(sql)
                      
                      
#            self.__df_Saisons.to_sql("Saison", conn, if_exists='replace', index = True)
        
#        
#        obj_cursor.execute('''INSERT INTO Saison (Saaison_id,Saison_Description, Saison_Description, Final_table_id, Begin_Year, [End_Year)
#                              SELECT DISTINCT sa.str_Saison_Description, sa.int_Begin_Year, sa.int_End_Year
#                              FROM Saison sa
#                              LEFT JOIN COUNTRY ctr ON clt.Country_ID = ctr.Country_ID''')
        # LEFT JOIN COUNTRY ctr ON clt.Country_ID = ctr.Country_ID

    def export_database(self):
        
        self.create_connection(self.__df_data_scources.loc["DataBase_name", "Value"])
        
    def convert_obj_in_DataFrame(self):
        
        # Create DataFrame for the Football Saisons
        df_Saison = DataFrame(index=list(range(len(self.__dict_Saisons.keys()))),                              
                              columns=["str_Saison_Description",                                       
                                       "int_Begin_Year",
                                       "int_End_Year"])
        
        self.fill_df(df_Saison, self.__dict_Saisons, ["get_str_Saison_description", "get_begin_year", "get_end_year"])
        self.__df_Saisons = df_Saison

        
        # Create DataFrame for the Football Games
        df_Fotball_games = DataFrame(index=list(range(len(self.__dict_foot_ball_games.keys()))),                              
                                    columns=["str_Team1",                                       
                                             "str_Team2",
                                             "int_Scour_Team1",
                                             "int_Scour_Team2",
                                             "Date_of_Game",
                                             "id_Saison"])
        
        self.fill_df(df_Fotball_games, self.__dict_foot_ball_games, ["get_team1", "get_team2", "get_scour_team1", "get_scour_team2", "get_date", "get_id_saison"])
        self.__df_Fotball_games = df_Fotball_games
        
        
        # Create DataFrame for the Football Teams
        df_Football_Teams = DataFrame(index=list(range(len(self.__dict_teams.keys()))),                              
                                      columns=["str_Team"])
        
        self.fill_df(df_Football_Teams, self.__dict_teams, ["get_football_team"])
        self.__df_Football_team = df_Football_Teams
    
    def fill_df(self, df, dict_obj, list_properties):
        
        for id_dict, (obj_id, obj) in enumerate(dict_obj.items()):
            for id_col,col in enumerate(df.columns):
                
                df.at[id_dict, col] = getattr(obj, list_properties[id_col])
            
    
    
    @property
    def get_df_Saisons(self):
        return self.__df_Saisons
    
    @property
    def get_df_Football_games(self):
        return self.__df_Fotball_games
    
    @property
    def get_df_Football_teams(self):
        return self.__df_Football_team
                
    @property          
    def get_dict_saisons(self):
        return self.__dict_Saisons
                               
       
class Championship():
    def __init__(self):
        self.__str_Saison_description = ""        
        self.__title_final_table = ""
        
        self.__url_base_source = ""
        
        self.__str_final_table = ""
        self.__url_final_table = ""
        
        self.__year_begin = np.NaN
        self.__year_end = np.NaN
        
        self.__str_result_table = ""
        self.__url_result_table = ""
        
        self.__master = ""
        
        self.__dict_obj_games = dict()
        self.__dict_obj_teams = dict()
    
    @property
    def get_df_final_table(self):
        return self.__df_final_table
    
    @property
    def get_str_Saison_description(self):
        return self.__str_Saison_description
    
    @property
    def get_str_final_table(self):
        return self.__str_final_table
    
    @property
    def get_url_final_table(self):
        return self.__url_final_table
    
    @property
    def get_str_result_table(self):
        return self.__str_result_table
    
    @property
    def get_url_result_table(self):
        return self.__url_result_table
       
    @property
    def get_dict_games(self):
        return self.__dict_obj_games
    
    @property
    def get_begin_year(self):
        return self.__year_begin
    
    @property
    def get_end_year(self):
        return self.__year_end
    
    @property
    def get_list_keys(self):
        return ["str_Saison_Description", 
                "Final_table_id",
                "int_Begin_Year",
                "int_End_Year"]
        
    def set_description(self, description):
        self.__str_Saison_description = description
        
    def set_final_table(self, str_final_table, url_final_table):
        self.__title_final_table = str_final_table
        
    def set_result_table(self, str_results_table, url_results_table):
        self.__str_Ergebnisse = str_results_table
        self.__url_result_table = url_results_table
        
    def set_master(self, master):
        self.__master = master
        
    def set_url_base_source(self, url_source):
        self.__url_base_source = url_source
        
    def set_year(self, year_begin, year_end):
        self.__year_begin = year_begin
        self.__year_end = year_end
        
    def set_dict_games(self, dict_games):
        self.__dict_obj_games = dict_games
        

class football_game():
    def __init__(self):
        self.__team_1 = ""
        self.__team_2 = ""
        
        self.__scoure_team_1 = np.NaN
        self.__scoure_team_2 = np.NaN
        
        self.__url_statistic = ""
        
        self.__id_saison = np.NaN
        self.__obj_saison = np.NaN
        
        self.__date_game = date(1,1,1)
    
    
    @property
    def get_obj_saison(self):
        return self.__obj_saison
    
    @property
    def get_id_saison(self):
        return self.__id_saison
    
    @property
    def get_date(self):
        return self.__date_game
    
    @property
    def get_scour_team1(self):
        return self.__scoure_team_1
    
    @property
    def get_scour_team2(self):
        return self.__scoure_team_2
        
    @property
    def get_team1(self):
        return self.__team_1
    
    @property
    def get_team2(self):
        return self.__team_2
    
    
    def clean_names(self, str_column):
        
       str_chars = string.ascii_letters + string.digits + "ÄäÜüÖöß" + "-." + " "
       
       result = str_column
       
       list_chars = [string for string in result if string not in str_chars]
       
       
       while len(list_chars) > 0:         
           
           if "Ã¼" in result:    
    #           set_trace()
               result = result.replace("Ã¼", "ü")
           
           if "Ã¶" in result:    
    #           set_trace()
               result = result.replace("Ã¶", "ö")   
                
            
           if "Ã" in result:
    #           set_trace()
               result = result.replace("Ã", "")
                
            
           if "ÃŸ" in result:            
    #           set_trace()
               result = result.replace("ÃŸ", "ß")
               
           if "Ÿ" in result:
               result = result.replace("Ÿ", "ß")
                
            
           if "Â\xa0" in result:               
    #           set_trace()
               result = result.replace("Â\xa0", " ")
               
           list_chars = [string for string in result if string not in str_chars]


           
       if "- Blau" in result:        
           result = result.replace("- Blau", "")
           
       if "- Rot" in result:        
           result = result.replace("- Rot", "") 

       if " - Sport" in result:           
           result = result.replace(" - Sport", "")
           
       if "Bor." in result:
           result = result.replace("Bor.", "Borussia")
           
       if "FC" in result:
           result = result.replace("FC", "")
           
           
        
       result = result.strip()
       
       return result
        
    
    
    def set_teams(self, str_teams):
        try:
            if str_teams.count("-") == 1:
                int_pos = [i for i, ii in enumerate(str_teams) if ii == "-"][0]
            elif str_teams.count("-") == 2:
                int_pos = [i for i, ii in enumerate(str_teams) if ii == "-"][1]
            elif str_teams.count("-") == 3:
                int_pos = [i for i, ii in enumerate(str_teams) if ii == "-"][1]
                
        except:
            set_trace()

        team1 = self.clean_names(str_teams[:int_pos])
        team2 = self.clean_names(str_teams[int_pos+1:])
        
        self.__team_1, self.__team_2 = team1, team2
        
    def set_scoure(self, str_scoure):
#        [value if not np.isnan(value) else "Fehler" for value in arr ]
        
        try:
            self.__scoure_team_1, self.__scoure_team_2 = [int(scour) if not np.isnan(int(scour)) else 0 for scour in str_scoure.split(":")]
        except:            
            self.__scoure_team_1, self.__scoure_team_2 = 0, 0
            
                
    def set_date(self, str_date):
        self.__date_game = datetime.strptime(str_date[:10], "%d.%m.%Y")
        
    def set_url_statistic(self, str_url):        
        self.__str_url_statistic = str_url        
        
    def set_saison(self, id_saison, obj_saison):
        self.__id_saison = id_saison
        self.__obj_saison = obj_saison   
        
        
    
class football_team():
    def __init__(self, name):
        self.__name = name
    
    @property
    def get_football_team(self):
        return self.__name