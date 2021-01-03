import pandas as pd
import numpy as np
import re
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
from time import sleep
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from secrets_variables import selenium_directory

def parse_table(table):
    """ Get data from table """
    return [
        [cell.get_text().strip() for cell in row.find_all(['th', 'td'])]
           for row in table.find_all('tr')
    ]


def unique_columns(table):
    '''

    :param table: (pd.DataFrame)
    :return: list with indices of unique columns of table
    '''

    unique_columns = list(set(table.columns))
    idx_columns = [table.columns.tolist().index(col) for col in unique_columns]
    idx_columns.sort()

    return idx_columns


def get_team_data(id, season, team):
    '''
    Gets all tables related to all competitions a team played during a season

    :param id: (string) team id
    :param season: (string) formatted by yyyy-yyyy
    :param team: (string) name of the team
    :return: dict
    '''


    # Open headless browser
    team_url_root = f'https://fbref.com/en/squads/{id}/{season}/all_comps/{team}-Stats-All-Competitions'
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(selenium_directory,
                              chrome_options=chrome_options)

    driver.get(team_url_root)
    team_html = BeautifulSoup(driver.page_source, 'html.parser')
    driver.close()

    sleep(1.5)

    players_df_list = []
    gk_df_list = []

    try:
        combined_stats = parse_table(team_html.find(id='stats_standard_ks_combined'))
        combined_stats_df = pd.DataFrame(combined_stats[2:], columns=combined_stats[1])
        combined_stats_df = combined_stats_df.loc[
            (combined_stats_df.Player != 'Player') & (combined_stats_df.Player != '')].reset_index(drop=True)
        players_df_list.append(combined_stats_df)
    except:
        pass


    try:
        goalkeeping_stats = parse_table(team_html.find(id='stats_keeper_ks_combined'))
        goalkeeping_stats_df = pd.DataFrame(goalkeeping_stats[2:], columns=goalkeeping_stats[1])
        goalkeeping_stats_df = goalkeeping_stats_df.loc[
            (goalkeeping_stats_df.Player != 'Player') & (goalkeeping_stats_df.Player != '')].reset_index(drop=True)
        gk_df_list.append(goalkeeping_stats_df)
    except:
        pass


    try:
        advanced_goalkeeping_stats = parse_table(team_html.find(id='stats_keeper_adv_ks_combined'))
        advanced_goalkeeping_stats_df = pd.DataFrame(advanced_goalkeeping_stats[2:], columns=advanced_goalkeeping_stats[1])
        advanced_goalkeeping_stats_df = advanced_goalkeeping_stats_df.loc[
            (advanced_goalkeeping_stats_df.Player != 'Player') & (advanced_goalkeeping_stats_df.Player != '')].reset_index(
            drop=True)
        gk_df_list.append(advanced_goalkeeping_stats_df)
    except:
        pass


    try:
        shooting_stats = parse_table(team_html.find(id='stats_shooting_ks_combined'))
        shooting_stats_df = pd.DataFrame(shooting_stats[2:], columns=shooting_stats[1])
        shooting_stats_df = shooting_stats_df.loc[
            (shooting_stats_df.Player != 'Player') & (shooting_stats_df.Player != '')].reset_index(drop=True)
        players_df_list.append(shooting_stats_df)
    except:
        pass


    try:
        passing_stats = parse_table(team_html.find(id='stats_passing_ks_combined'))
        passing_stats_df = pd.DataFrame(passing_stats[2:], columns=passing_stats[1])
        passing_stats_df = passing_stats_df.loc[
            (passing_stats_df.Player != 'Player') & (passing_stats_df.Player != '')].reset_index(drop=True)
        players_df_list.append(passing_stats_df)
    except:
        pass


    try:
        passing_types_stats = parse_table(team_html.find(id='stats_passing_types_ks_combined'))
        passing_types_stats_df = pd.DataFrame(passing_types_stats[2:], columns=passing_types_stats[1])
        passing_types_stats_df = passing_types_stats_df.loc[
            (passing_types_stats_df.Player != 'Player') & (passing_types_stats_df.Player != '')].reset_index(drop=True)
        players_df_list.append(passing_types_stats_df)
    except:
        pass


    try:
        gca_stats = parse_table(team_html.find(id='stats_gca_ks_combined'))
        gca_stats_df = pd.DataFrame(gca_stats[2:], columns=gca_stats[1])
        gca_stats_df = gca_stats_df.loc[(gca_stats_df.Player != 'Player') & (gca_stats_df.Player != '')].reset_index(
            drop=True)
        players_df_list.append(gca_stats_df)
    except:
        pass


    try:
        defense_stats = parse_table(team_html.find(id='stats_defense_ks_combined'))
        defense_stats_df = pd.DataFrame(defense_stats[2:], columns=defense_stats[1])
        defense_stats_df = defense_stats_df.loc[
            (defense_stats_df.Player != 'Player') & (defense_stats_df.Player != '')].reset_index(drop=True)
        players_df_list.append(defense_stats_df)
    except:
        pass


    try:
        possession_stats = parse_table(team_html.find(id='stats_possession_ks_combined'))
        possession_stats_df = pd.DataFrame(possession_stats[2:], columns=possession_stats[1])
        possession_stats_df = possession_stats_df.loc[
            (possession_stats_df.Player != 'Player') & (possession_stats_df.Player != '')].reset_index(drop=True)
        players_df_list.append(possession_stats_df)
    except:
        pass


    try:
        playing_time_stats = parse_table(team_html.find(id='stats_playing_time_ks_combined'))
        playing_time_stats_df = pd.DataFrame(playing_time_stats[2:], columns=playing_time_stats[1])
        playing_time_stats_df = playing_time_stats_df.loc[
            (playing_time_stats_df.Player != 'Player') & (playing_time_stats_df.Player != '')].reset_index(drop=True)
        players_df_list.append(playing_time_stats_df)
    except:
        pass

    try:
        misc_stats = parse_table(team_html.find(id='stats_misc_ks_combined'))
        misc_stats_df = pd.DataFrame(misc_stats[2:], columns=misc_stats[1])
        misc_stats_df = misc_stats_df.loc[(misc_stats_df.Player != 'Player') & (misc_stats_df.Player != '')].reset_index(
            drop=True)
        players_df_list.append(misc_stats_df)
    except:
        pass


    # Gather all player data into one DataFrame. Create another one for goalkeepers too
    player_df = players_df_list[0]

    if len(players_df_list) > 1:
        for i in range(1, len(players_df_list)):
            temp_df = players_df_list[i]
            player_df = player_df.merge(temp_df, how='left',
                                        left_on=['Player', 'Nation', 'Pos', 'Age'],
                                        right_on=['Player', 'Nation', 'Pos', 'Age'])

    player_df['season'] = season
    player_df['team'] = id


    # For goalkeepers now
    gk_df = gk_df_list[0]

    if len(gk_df_list) > 1:
        for i in range(1, len(gk_df_list)):
            temp_df = gk_df_list[i]
            gk_df = gk_df.merge(temp_df, how='left',
                                        left_on=['Player', 'Nation', 'Pos', 'Age'],
                                        right_on=['Player', 'Nation', 'Pos', 'Age'])

    gk_df['season'] = season
    gk_df['team'] = id


    # Avoid duplicated columns and return
    player_df.columns = [col.lower() for col in player_df.columns]
    cols_players = unique_columns(player_df)
    player_df = player_df.iloc[:, cols_players]

    gk_df.columns = [col.lower() for col in gk_df.columns]
    cols_gk = unique_columns(gk_df)
    gk_df = gk_df.iloc[:, cols_gk]


    return (player_df, gk_df)


def get_top5_seasons_standings(season):
    '''

    :param season: (str) string of the type 'yyyy-yyyy'
    :return:
    '''


    fbref_stats_url = f'https://fbref.com/en/comps/Big5/{season}/{season}-Big-5-European-Leagues-Stats'
    fbref_stats_get = requests.get(fbref_stats_url)
    fbref_stats_html = BeautifulSoup(fbref_stats_get.content, 'html.parser')
    fbref_stats_get.close()

    # Get all relevant teams from Europe Big 5
    table_scores = fbref_stats_html.find_all(id='big5_table')[0]
    table_parsed = parse_table(table_scores)
    table_parsed_df = pd.DataFrame(table_parsed[1:], columns=table_parsed[0])

    # Get all the URLS for these teams
    teams_links = table_scores.find_all('a')
    teams_links = [link['href'] for link in teams_links if 'squad' in link['href']]
    table_parsed_df['url_team'] = teams_links

    # Parse the URL to generate a unique identifier for each team
    table_parsed_df['team_id'] = table_parsed_df.url_team.apply(lambda x: re.search('(?<=squads/).*?/', x).group())
    table_parsed_df['team_id'] = table_parsed_df['team_id'].str.replace('/', '')

    return table_parsed_df


def get_leagues_links():
    '''

    :return: DataFrame with all leagues in the WhoScored page
    '''

    url = 'https://www.whoscored.com/Statistics'
    driver = webdriver.Chrome(selenium_directory)

    # Open Browser and get top 5 leagues URLs
    driver.get(url)
    sleep(1)
    html = driver.page_source
    html_parsed = BeautifulSoup(html, parser='html_parser')
    driver.close()


    # Use BeautifulSoup in order to get the links
    leagues_urls = html_parsed.find_all(class_='pt iconize iconize-icon-left')
    leagues_links = [(league.text, league['href']) for league in leagues_urls]
    leagues_links_df = pd.DataFrame(leagues_links, columns=['league_name', 'url'])

    return leagues_links_df


def get_seasons_standings(url, season):
    '''

    :param url (str): url of the league to explore, as obtained by the function get_league_links
    :param season (str): string of the type yyyy/yyyy
    :return: DataFrame with standings and links for each of the teams in a season
    '''

    # Create the URL to get the info from
    url_league = 'https://www.whoscored.com' + url


    # Open browser, select season and get page HTML
    driver = webdriver.Chrome(selenium_directory)
    driver.get(url_league)
    sleep(1.5)

    season_select = Select(driver.find_element_by_id('seasons'))
    season_select.select_by_visible_text(season)
    sleep(1.5)
    league_html = BeautifulSoup(driver.page_source, parser='html_parser')


    # Parse standings table
    league_standings_df = pd.DataFrame(parse_table(league_html.find(class_='standings')))
    league_standings_df.columns = ['team', 'games', 'wins', 'draws', 'losses',
                                   'goals_scored', 'goals_received', 'goals_difference', 'points',
                                   'last_5_games']

    league_standings_df['position'] = league_standings_df.team.apply(lambda x: re.search('[0-9]+', x).group())
    league_standings_df['team'] = league_standings_df.team.str.replace(r'[0-9]+', '')
    league_standings_df['team_url'] = [team['href'] for team in
                                       league_html.find(class_='standings').find_all(class_='team-link')]
    league_standings_df['season'] = league_html.find(id='seasons').find('option', selected=True).text

    driver.close()

    # Return table
    return league_standings_df


def get_futbin_league_pages(league_key, fifa_year):
    '''
    Get the number of pages you need to request for each league

    :param league_key: (int) number representing the league in futbin
    :param fifa_year: (int) year of fifa edition
    :return: (int). number of pages
    '''

    # URL to request
    url = f'https://www.futbin.com/{fifa_year}/players?page=1&version=all_nif&league={league_key}'
    r = requests.get(url)
    sleep(2)

    # Parse HTML and close connection
    html = BeautifulSoup(r.content, 'html.parser')
    r.close()


    return int(html.find(class_='pagination pg-blue justify-content-end').find_all(class_='page-item')[-2].text.strip())


def get_fut_players_per_page(league_key, fifa_year, page):
    '''

    :param league_key:
    :param fifa_year:
    :param page:
    :return:
    '''

    url_futbin = f'https://www.futbin.com/{fifa_year}/players?page={page}&version=all_nif&league={league_key}'
    r = requests.get(url_futbin)
    sleep(2)


    # Parse HTML and close connection
    html = BeautifulSoup(r.content, 'html.parser')
    r.close()


    # Headers and data
    league_list = parse_table(html.find(id='repTb'))
    table_headers = html.find(class_='players_table_header').find_all('th')
    headers = [el.text for el in table_headers]


    league_page_df = pd.DataFrame(league_list, columns=headers)
    league_page_df['league'] = league_key
    league_page_df['fifa'] = fifa_year
    league_page_df['page'] = page


    # Players URLS
    table = html.find(id='repTb')
    players_urls = [row.find('a')['href'] for row in table.find_all('tr')]
    league_page_df['player_url'] = players_urls


    # Teams and Country
    players_club_nation = html.find_all(class_='players_club_nation')
    club = [player.find_all('a')[0]['data-original-title'] for player in players_club_nation]
    nation = [player.find_all('a')[1]['data-original-title'] for player in players_club_nation]
    league_page_df['club'] = club
    league_page_df['nation'] = nation


    return league_page_df


def drop_duplicates_cols(df, suffixes=['_x', '_y', '_z']):
    '''
    Drops duplicated columns that result after merging DataFrames


    :param df: (pd.DataFrame)
    :param suffixes:  suffixes to eliminate
    :return:
    '''

    cols_drop = [col for col in df.columns for suff in suffixes if suff in col]
    df_dropped = df.drop(columns=cols_drop)

    return df_dropped


def transfermarkt_teams_year(league_url, year):
    '''
    Function that returns DataFrame for each league and year

    :param league_url (str): string of transfermarkt for each league
    :param year (str): string of type 'yyyy' signaling year id
    :return league_df (DataFrame):
    '''

    # Headers to make request and not get 404 status code
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

    # Format the leagues URL with the year of the season to get data from
    league_url = league_url.format(year)

    # Get request and parsing
    requests_url = requests.get(league_url, headers=headers)
    request_html = BeautifulSoup(requests_url.content)
    requests_url.close()

    # Parse table from HTML
    table = request_html.find_all(class_='items')[0]
    table = parse_table(table)
    league_df = pd.DataFrame(table[2:], columns=table[0])

    # Paste the team ID for URL purposes
    links = request_html.find_all(class_='hauptlink no-border-links show-for-small show-for-pad')
    league_df['squad_code'] = [link.findChild()['id'] for link in links]
    league_df['squad_url'] = [link.findChild()['href'] for link in links]

    # Paste league url to be able to trace back.
    league_df['url_scraped'] = league_url

    return league_df

def get_teams_seasons_transfers(team_name_url, squad_code, year, window):
    '''

    :param team_name_url (str): string acceptable by transfermarkt for each team. example fc-chelsea
    :param squad_code (str): numeric code transfermarkt uses to identify each team
    :param year (str): string of type yyyy for the window
    :return:
    '''


    # Format URL, check transfermarkt webpage to make sure it works
    transfer_url = f'https://www.transfermarkt.com/{team_name_url}/transfers/verein/{squad_code}/plus/0?saison_id={year}&pos=&detailpos=&w_s={window}'

    # Headers to make request and not get 404 status code
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

    # Make request and get the two tables corresponding to arrivals and departures
    url_request = requests.get(transfer_url, headers=headers)
    html_content = BeautifulSoup(url_request.content)
    tables_transfers = html_content.find_all(class_='responsive-table')
    url_request.close()

    # Arrivals
    arrivals_list = parse_table(tables_transfers[0])
    arrivals_list_players = [element for element in arrivals_list if len(element) >= 5]
    arrivals_df = pd.DataFrame(arrivals_list_players[1:])
    arrivals_df = arrivals_df.iloc[:, [3, 4, 5, 9, 10, 11]]
    arrivals_df.columns = ['player_name', 'position', 'age', 'origin_squad', 'origin_league', 'fee']
    arrivals_df['destination_squad'] = team_name_url
    arrivals_df['year'] = year
    arrivals_df['window'] = window

    # Departures
    departures_list = parse_table(tables_transfers[1])
    departures_list_players = [element for element in departures_list if len(element) >= 5]
    departures_df = pd.DataFrame(departures_list_players[1:])
    departures_df = departures_df.iloc[:, [3, 4, 5, 9, 10, 11]]
    departures_df.columns = ['player_name', 'position', 'age', 'destination_squad', 'destination_league', 'fee']
    departures_df['origin_squad'] = team_name_url
    departures_df['year'] = year
    departures_df['window'] = window

    # Players URL from transfers lists
    arrivals_links = tables_transfers[0].find_all(class_='spielprofil_tooltip')
    arrivals_df['arrival_link'] = [link['href'] for link in arrivals_links]

    departures_links = tables_transfers[1].find_all(class_='spielprofil_tooltip')
    departures_df['departure_link'] = [link['href'] for link in departures_links]


    # Return tuple with both tables
    return (arrivals_df, departures_df)


def clean_transfermarkt_monetary(df, monetary_col):

    # Create a copy and go over cases
    df_copy = df.copy()
    df_copy['monetary_aux'] = df_copy[monetary_col]
    df_copy['monetary_aux'] = np.where(df_copy.monetary_aux == '-', '0', df_copy.monetary_aux)
    df_copy['monetary_aux'] = df_copy['monetary_aux'].astype(str).str.lstrip('€')

    # Calculate  purchases magnitudes a transform to numeric finally
    df_copy['magnitude'] = df_copy.monetary_aux.str.extract('([A-Za-z]+.?$)')
    df_copy['monetary_value'] = df_copy.monetary_aux.astype(str).str.lower().str.replace('([A-Za-z :€])',
                                                                                         '').str.strip()
    df_copy['monetary_value'] = np.where(df_copy['monetary_value'] == '', '0', df_copy['monetary_value'])

    df_copy['monetary_aux'] = np.where(df_copy.magnitude == 'm',
                                       df_copy.monetary_value.astype(float) * 1e6,
                                       np.where(df_copy.magnitude == 'Th.',
                                                df_copy.monetary_value.astype(float) * 1e3,
                                                df_copy.monetary_value))

    # Convert to float and return dataframe
    df_copy['monetary_aux'] = df_copy.monetary_aux.astype(float)
    df_copy[monetary_col] = df_copy.monetary_aux
    df_copy = df_copy.drop(columns=['monetary_aux', 'monetary_value', 'magnitude'])

    return df_copy


def get_player_summary(player_name, player_code):
    player_url = f'https://www.transfermarkt.com/{player_name}/profil/spieler/{player_code}'
    injury_url = f'https://www.transfermarkt.com/{player_name}/verletzungen/spieler/{player_code}'
    detailed_stats_url = f'https://www.transfermarkt.com/{player_name}/leistungsdatendetails/spieler/{player_code}/saison//verein/0/liga/0/wettbewerb//pos/0/trainer_id/0/plus/1'

    # Headers to make request and not get 404 status code
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

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
    teams_links = player_html.find_all(class_='hauptlink no-border-links vereinsname')
    teams_left = [team.text for team in teams_links[0::2]]
    teams_joined = [team.text for team in teams_links[1::2]]

    player_transfer_df = player_transfer_df.loc[
        ~(player_transfer_df.season.str.lower().str.strip().isin(['upcoming transfer',
                                                                  'transfer history']))].reset_index(drop=True)
    player_transfer_df['teams_left_link'] = teams_left
    player_transfer_df['teams_joined_link'] = teams_joined

    # Clean monetary values
    player_transfer_df = player_transfer_df.loc[player_transfer_df.fee != 'End of loan'].reset_index(drop=True)
    player_transfer_df['loan'] = np.where((player_transfer_df.fee.str.lower().str.contains('.*(loan|fee)', na=True)) &
                                          (player_transfer_df.fee != 0), 1, 0)
    player_transfer_df['known_fee'] = np.where(player_transfer_df.fee == '?', 0, 1)
    player_transfer_df['fee'] = np.where(player_transfer_df.fee == '?', '0', player_transfer_df.fee)
    player_transfer_df = clean_transfermarkt_monetary(player_transfer_df, 'mv')
    player_transfer_df = clean_transfermarkt_monetary(player_transfer_df, 'fee')

    # Misc info like position, height, dominant foot-------------
    try:
        main_position = player_html.find(class_='hauptposition-left').text.strip().replace('  ', '').replace(
            'Main position:', '').lower()
    except:
        try:
            main_position = player_html.find(class_='hauptposition-center').text.strip().replace('  ', '').replace('Main position:', '').lower()
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

    return player_dict


