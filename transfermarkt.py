
import pandas as pd
import numpy as np
import udf
import requests
from bs4 import BeautifulSoup

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

# Test function on premier leaguue year 2009.
example = udf.transfermarkt_teams_year(leagues_url_list[0][1], '2009')
example = example.drop(columns='Club')
example.columns = ['club_name', 'name', 'squad_size', 'avg_age', 'foreigners_quantity',
                   'total_market_value', 'avg_market_value', 'total_mv', 'avg_mv', 'squad_code', 'url_scraped']

example.iloc[0]

