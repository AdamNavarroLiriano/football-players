
import pandas as pd
import numpy as np
import udf
import requests
from bs4 import BeautifulSoup
from time import sleep

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

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


# Transfers per team per season
teams_df = leagues_data_all_seasons[['club_name', 'name', 'squad_code', 'squad_name_in_url']].drop_duplicates().reset_index(drop=True)

# Create DataFrames that will contain all data
arrivals_df = pd.DataFrame()
departures_df = pd.DataFrame()

for idx, row in teams_df.iterrows():
    for year in years:
        # Print message
        print('Getting data from {}. Season {}'.format(row.squad_name_in_url, year))

        # Get team season data
        team_season_arrivals, team_season_departures = udf.get_teams_seasons_transfers(row.squad_name_in_url,
                                                                                       row.squad_code,
                                                                                       year)
        # Append to DataFrames
        arrivals_df = pd.concat([arrivals_df, team_season_arrivals], ignore_index=True)
        departures_df = pd.concat([departures_df, team_season_departures], ignore_index=True)
        sleep(np.random.randint(0, 5, 1))
