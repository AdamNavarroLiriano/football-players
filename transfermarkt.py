import pandas as pd
import numpy as np
import udf
import requests
import re
from bs4 import BeautifulSoup
from time import sleep

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

# <editor-fold desc="TEAM DATA">
# Get the url format of top 5 european leagues
leagues_url_list = \
    [('premier league', 'https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1/plus/?saison_id={}'),
     ('bundesliga', 'https://www.transfermarkt.com/bundesliga/startseite/wettbewerb/L1/plus/?saison_id={}'),
     ('laliga', 'https://www.transfermarkt.com/primera-division/startseite/wettbewerb/ES1/plus/?saison_id={}'),
     ('serieA', 'https://www.transfermarkt.com/serie-a/startseite/wettbewerb/IT1/plus/?saison_id={}'),
     ('ligue1', 'https://www.transfermarkt.com/ligue-1/startseite/wettbewerb/FR1/plus/?saison_id={}')]

# Create DataFrame of URLs
leagues_url_df = pd.DataFrame(leagues_url_list, columns=['league', 'url'])

# Seasons to get data from
years = list(range(2009, 2020))
years = [str(year) for year in years]

# Iterate over leagues and years and compile on DataFrame
leagues_data_all_seasons = pd.DataFrame()

for league in leagues_url_list:
    for year in years:
        print('Year {}. League {}'.format(year, league[0]))

        # Get request and some data cleaning
        league_year_df = udf.transfermarkt_teams_year(league[1], year)
        league_year_df = league_year_df.drop(columns='Club')
        league_year_df.columns = ['club_name', 'name', 'squad_size', 'avg_age', 'foreigners_quantity',
                                  'total_market_value', 'avg_market_value', 'total_mv', 'avg_mv', 'squad_code', 'squad_url', 'url_scraped']

        # Append to compilation
        leagues_data_all_seasons = pd.concat([leagues_data_all_seasons, league_year_df], ignore_index=True)

leagues_data_all_seasons['squad_name_in_url'] = leagues_data_all_seasons['squad_url'].str.extract('^/(.*)/startseite')
leagues_data_all_seasons.to_csv('Data/transfermarkt_league_data.csv', index=False)
# </editor-fold>

#leagues_data_all_seasons = pd.read_csv('Data/transfermarkt_league_data.csv')

# <editor-fold desc="TRANSFERS PER TEAM PER SEASON">
# Transfers per team per season----------------------------------
teams_df = leagues_data_all_seasons[['club_name', 'name', 'squad_code', 'squad_name_in_url']].drop_duplicates().reset_index(drop=True)

# Create DataFrames that will contain all data
arrivals_df = pd.DataFrame()
departures_df = pd.DataFrame()
missing_data = []

for idx, row in teams_df.iterrows():
    for year in years:
        for window in ['s','w']:
            # Print message
            print('Getting data from {}. Season {}. Window {}. Team {}/{}'.format(row.squad_name_in_url, year, window, idx+1, teams_df.shape[0]))

            # 3 tries to get the data, if not pass
            flag = 0
            for i in range(3):
                if flag == 0:
                    try:
                        # Get team season data
                        team_season_arrivals, team_season_departures = udf.get_teams_seasons_transfers(row.squad_name_in_url,
                                                                                                       row.squad_code,
                                                                                                       year,
                                                                                                       window)
                        # Append to DataFrames
                        arrivals_df = pd.concat([arrivals_df, team_season_arrivals], ignore_index=True)
                        departures_df = pd.concat([departures_df, team_season_departures], ignore_index=True)
                        sleep(1)


                        # Break out of tries
                        flag = 1

                    except:
                        print('Not possible to get data')
                        missing_data.append(row)
                else:
                    break

arrivals_df.to_csv('Data/arrivals_df.csv', index=False)
departures_df.to_csv('Data/departures_df.csv', index=False)
# </editor-fold>---------------------------

# Reading data
arrivals_df = pd.read_csv('Data/arrivals_df.csv')
departures_df = pd.read_csv('Data/departures_df.csv')

# <editor-fold desc="CLEANING PURCHASES">
# Players worth, avoiding end of loans and unknown transfers------------------------------
purchases_df = arrivals_df.loc[(arrivals_df.fee.notna()) & (arrivals_df.fee.notnull())].reset_index(drop=True)
purchases_df = purchases_df.loc[~purchases_df.fee.str.match('.*(loan)')].reset_index(drop=True)
purchases_df = purchases_df.loc[purchases_df.fee != '?'].reset_index(drop=True)
purchases_df.loc[purchases_df.fee == '-', 'fee'] = 0


# Clean players prices by creating loans flag and transform column to numeric
purchases_df['loan'] = np.where((purchases_df.fee.str.lower().str.contains('.*(fee)',na=True)) &
                                (purchases_df.fee != 0), 1, 0)

# Create a copy and go over cases
purchases_df['purchase_price'] = purchases_df['fee']
purchases_df['purchase_price'] = np.where(purchases_df.purchase_price == 'free transfer', '0', purchases_df.purchase_price)
purchases_df = udf.clean_transfermarkt_monetary(purchases_df, 'purchase_price')
# </editor-fold>


# PLAYER DATABASE------------------
players_ids = purchases_df[['arrival_link']].arrival_link.str.extract('/(.*?)/profil.*spieler/(.*)').drop_duplicates().reset_index(drop=True)
players_ids.columns = ['name', 'player_id']

# Get data for each player
dict_players = {}
for idx, row in players_ids.iterrows():
    print(row.name)
    player_summary = udf.get_player_summary(player_name=row['name'], player_code=row.player_id)
    dict_players[row['name']] = player_summary