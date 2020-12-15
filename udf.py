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

def get_teams_seasons_transfers(team_name_url, squad_code, year):
    '''

    :param team_name_url (str): string acceptable by transfermarkt for each team. example fc-chelsea
    :param squad_code (str): numeric code transfermarkt uses to identify each team
    :param year (str): string of type yyyy for the window
    :return:
    '''


    # Format URL, check transfermarkt webpage to make sure it works
    transfer_url = f'https://www.transfermarkt.com/{team_name_url}/transfers/verein/{squad_code}/plus/0?saison_id={year}&pos=&detailpos=&w_s='

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

    # Departures
    departures_list = parse_table(tables_transfers[1])
    departures_list_players = [element for element in departures_list if len(element) >= 5]
    departures_df = pd.DataFrame(departures_list_players[1:])
    departures_df = departures_df.iloc[:, [3, 4, 5, 9, 10, 11]]
    departures_df.columns = ['player_name', 'position', 'age', 'destination_squad', 'destination_league', 'fee']
    departures_df['origin_squad'] = team_name_url
    departures_df['year'] = year


    # Players URL from transfers lists
    arrivals_links = tables_transfers[0].find_all(class_='spielprofil_tooltip')
    arrivals_df['arrival_link'] = [link['href'] for link in arrivals_links]

    departures_links = tables_transfers[1].find_all(class_='spielprofil_tooltip')
    departures_df['departure_link'] = [link['href'] for link in departures_links]


    # Return tuple with both tables
    return (arrivals_df, departures_df)