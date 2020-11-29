
import pandas as pd
import numpy as np
import udf
import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

league_url = 'https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1/plus/?saison_id=2019'

requests_url = requests.get(league_url, headers=headers)
request_html = BeautifulSoup(requests_url.content)
requests_url.close()


tabla = request_html.find_all(class_='items')[0]
tabla = udf.parse_table(tabla)
tabla_df = pd.DataFrame(tabla[1:], columns=tabla[0])
tabla_df = tabla_df.iloc[1:].reset_index(drop=True)

links = request_html.find_all(class_ = 'hauptlink no-border-links show-for-small show-for-pad')
tabla_df['squad_code'] = [link.findChild()['id'] for link in links]

