import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime 
from matplotlib import dates as mdates
from bs4 import BeautifulSoup as bs
import time

headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'}

df = pd.DataFrame()
sise_url = 'https://finance.naver.com/item/sise_day.nhn?code=068270'  
for page in range(1, 10):
    page_url = '{}&page={}'.format(sise_url, page)
    

    response = requests.get(page_url, headers=headers)
    html = bs(response.text, 'html.parser')
    html_table = html.select("table")
    table = pd.read_html(str(html_table))

    df = pd.concat([df, table[0].dropna()])
    #time.sleep(1)

print("-----------------------------------")
print(df)

df = df.dropna()
df = df.iloc[0:30]
df = df.sort_values(by='날짜')
print(df)


plt.figure(figsize=(15, 5))
plt.title('Celltrion (close)')
plt.xticks(rotation=45) 
plt.plot(df['날짜'], df['종가'], 'co-')
plt.grid(color='gray', linestyle='--')
plt.show()