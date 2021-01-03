import pandas as pd
import numpy as np
import udf
import requests
import re
from bs4 import BeautifulSoup
from time import sleep


import importlib
importlib.reload(udf)


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

udf.get_player_summary(player_name=row['name'], player_code=row.player_id)

player_name=row['name']; player_code=row.player_id

player_url = f'https://www.transfermarkt.com/{player_name}/profil/spieler/{player_code}'
injury_url = f'https://www.transfermarkt.com/{player_name}/verletzungen/spieler/{player_code}'
detailed_stats_url = f'https://www.transfermarkt.com/{player_name}/leistungsdatendetails/spieler/{player_code}/saison//verein/0/liga/0/wettbewerb//pos/0/trainer_id/0/plus/1'

# Headers to make request and not get 404 status code
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

player_request = requests.get(player_url, headers=headers)
player_html = BeautifulSoup(player_request.content)
player_request.close()

player_transfers_table = player_html.find(class_='responsive-table')
player_transfers_table = parse_table(player_transfers_table)

player_transfer_df = pd.DataFrame(player_transfers_table[1:-1])
player_transfer_df = player_transfer_df.iloc[:, [0, 1, 4, 7, 8, 9]]
player_transfer_df.columns = player_transfers_table[0][0:-1]
player_transfer_df.columns = [col.lower() for col in player_transfer_df.columns]

# Retrieving links for future joins etc
player_transfer_df = player_transfer_df.loc[~(player_transfer_df.season.str.lower().str.strip().isin(['upcoming transfer',
                                                                                                      'transfer history']))].reset_index(drop=True)
teams_links = player_html.find_all(class_='hauptlink no-border-links vereinsname')
teams_left = [team.text for team in teams_links[0::2]]
teams_joined = [team.text for team in teams_links[1::2]]

player_transfer_df['teams_left_link'] = teams_left
player_transfer_df['teams_joined_link'] = teams_joined

player_transfer_df = player_transfer_df.loc[player_transfer_df.fee != 'End of loan'].reset_index(drop=True)
player_transfer_df['loan'] = np.where((player_transfer_df.fee.str.lower().str.contains('.*(loan|fee)',na=True)) &
                                (player_transfer_df.fee != 0), 1, 0)

# Clean monetary values
player_transfer_df['known_fee'] = np.where(player_transfer_df.fee == '?', 0, 1)
player_transfer_df['fee'] = np.where(player_transfer_df.fee == '?', '0', player_transfer_df.fee)
player_transfer_df = clean_transfermarkt_monetary(player_transfer_df, 'mv')
player_transfer_df = clean_transfermarkt_monetary(player_transfer_df, 'fee')



player_transfer_df.iloc[-6]


# Misc info like position, height, dominant foot-------------
try:
    main_position = player_html.find(class_='hauptposition-left').text.strip().replace('  ', '').replace(
        'Main position:', '').lower()
except:
    try:
        main_position = player_html.find(class_='hauptposition-center').text.strip().replace('  ', '').replace(
            'Main position:', '').lower()
    except:
        main_position = 'None'

try:
    secondary_positions = player_html.find(class_='nebenpositionen').text.strip().replace(r'  ', ' '). \
        replace('Other position:\n', '')
    secondary_positions = [position for position in secondary_positions.split('  ') if position != '']
except:
    secondary_positions = ['No']

misc_data = parse_table(player_html.find_all(class_='auflistung')[2])
misc_data = [misc for misc in misc_data if misc[0].lower() in ['citizenship:', 'foot:', 'height:']]

foot = misc_data[2][1]
height = misc_data[0][1].replace('\xa0', '')
citizenship = misc_data[1][1].lower()

# Market value dataframe----------------
html_str = str(player_html)
pattern = re.compile(r"'data':(.*)}\],")
mv_string = pattern.findall(html_str)[0]
mv_string = mv_string.encode().decode('unicode_escape')

mv_df = pd.DataFrame(zip(re.findall("'verein':(.*?),'age'", mv_string),
                         re.findall("'mw':(.*?),'datum_mw'", mv_string),
                         re.findall("'datum_mw':(.*?),'x'", mv_string),
                         re.findall("'age':(.*?),'mw'", mv_string)),
                     columns=['team', 'market_value', 'date', 'age'])

mv_df = mv_df.apply(lambda x: x.str.replace("'", ''))
mv_df = clean_transfermarkt_monetary(mv_df, 'market_value')
mv_df['date'] = pd.to_datetime(mv_df['date'])

# Historical performance-------------------------
stats_request = requests.get(detailed_stats_url, headers=headers)
stats_html = BeautifulSoup(stats_request.content)
stats_request.close()

stats_table = parse_table(stats_html.find(class_='items'))

if main_position != 'goalkeeper':
    cols_names = ['season', 'competition', 'squad_capped', 'games_played', 'points_per_game',
                  'goals', 'assists', 'own_goals', 'subbed_in', 'subbed_out',
                  'yellow_cards', 'double_yellow', 'red_card', 'penalty_goals', 'mins_per_goal', 'mins_played']

    stats_table_df = pd.DataFrame(stats_table[2:]).drop(labels=[1, 3], axis=1)
    stats_table_df.columns = cols_names
else:
    cols_names = ['season', 'competition', 'squad_capped', 'games_played', 'points_per_game',
                  'goals', 'own_goals', 'subbed_in', 'subbed_out',
                  'yellow_cards', 'double_yellow', 'red_card', 'goals_conceded', 'clean_sheets', 'mins_played']

    stats_table_df = pd.DataFrame(stats_table[2:]).drop(labels=[1, 3], axis=1)
    stats_table_df.columns = cols_names

teams_seasons = stats_html.find_all(class_='hauptlink no-border-rechts zentriert')
teams_seasons = [team_season.findChild()['href'] for team_season in teams_seasons]
teams_seasons = [re.search('/(.*?)/', team_season).group().replace('/', '') for team_season in teams_seasons]
stats_table_df['squad'] = teams_seasons

cols_cleaning_stats = [col for col in stats_table_df.columns if col not in ['season', 'competition', 'squad']]
stats_table_df[cols_cleaning_stats] = stats_table_df[cols_cleaning_stats].apply(
    lambda x: x.str.replace('-', '0').str.replace("[,']", '').astype(float))

# Injuries--------------------
injury_request = requests.get(injury_url, headers=headers)
injury_html = BeautifulSoup(injury_request.content)
injury_request.close()

if injury_html.find(class_='items') is not None:
    injury_table = parse_table(injury_html.find(class_='items'))
    injury_table_df = pd.DataFrame(injury_table[1:], columns=injury_table[0])
    injury_table_df.columns = [col.lower().replace(' ', '_') for col in injury_table_df.columns]

    # Cleaning
    injury_table_df['days'] = injury_table_df['days'].str.replace(' days', '').astype(float)
    injury_table_df['games_missed'] = injury_table_df['games_missed'].str.replace('-', '0').astype(float)
    injury_table_df[['from', 'until']] = injury_table_df[['from', 'until']].apply(lambda x: pd.to_datetime(x))

else:
    injury_table_df = pd.DataFrame()

# Final dictionary----------
player_dict = {'foot': foot,
               'citizenship': citizenship,
               'main_position': main_position,
               'secondary_position': secondary_positions,
               'height': height,
               'transfer_history': player_transfer_df,
               'performance_stats': stats_table_df,
               'injury_history': injury_table_df}

get_player_summary(row['name'], row.player_id)