import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime 
from matplotlib import dates as mdates
from bs4 import BeautifulSoup as bs
import time
import warnings
import numpy as np
import seaborn as sns
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
import os



warnings.simplefilter(action='ignore', category=FutureWarning)
headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'}
lst = []
df = pd.DataFrame()
sise_url = 'https://finance.naver.com/item/sise_day.nhn?code=068270'
x = []
for page in range(1, 11):
    page_url = '{}&page={}'.format(sise_url, page)
    

    response = requests.get(page_url, headers=headers)
    html = bs(response.text, 'html.parser')
    html_table = html.select("table")
    table = pd.read_html(str(html_table))
    df = pd.concat([df, table[0].dropna()])
      
    
    date_format = "%Y.%m.%d"
    df['날짜'] = pd.to_datetime(df['날짜'], format=date_format)


    df['날짜_정수'] = df['날짜'].dt.strftime('%Y%m%d').astype(int)
    x = df['날짜_정수']
    lst.append(df)
    print(df)

    time.sleep(0.3)
df.to_excel('abc.xlsx')

df = pd.read_excel('DATA.xlsx')
print(df)

df = df.iloc[0:100] #크롤링을해서 긁어낸 데이터를 저장한 "배열"

df = df.sort_values(by='날짜')

plt.figure(figsize=(15, 5))
plt.title('Celltrion (close)')
plt.xticks(rotation=45) 
plt.plot(df['날짜'], df['종가'], 'co-')
plt.grid(color='gray', linestyle='--')
plt.show()