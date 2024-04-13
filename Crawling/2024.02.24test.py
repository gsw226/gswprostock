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
import matplotlib.pyplot as plt
import statsmodels.api as sm
 
from sklearn.linear_model import LinearRegression


warnings.simplefilter(action='ignore', category=FutureWarning)
headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'}

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
    #print(df)
    # date_format = "%Y.%m.%d"
    # df['날짜'] = pd.to_datetime(df['날짜'], format=date_format)

    # df['날짜_정수'] = df['날짜'].dt.strftime('%Y%m%d').astype(int)
    # x = df['날짜_정수']

    time.sleep(0.3)
print(df)
df = df.dropna()

df = df.iloc[0:100] #크롤링을해서 긁어낸 데이터를 저장한 "배열"
print(df)
df = df.sort_values(by='날짜')


y = df.종가
print(y[0])

#print(x)
#print(type(x))
print(y)
x = sm.add_constant(x)
print(x)
model = sm.OLS(y,x).fit()
#print(model.summary())

plt.figure(figsize=(15, 5))
plt.title('Celltrion (close)')
plt.xticks(rotation=45) 
plt.plot(df['날짜'], df['종가'], 'co-')
plt.grid(color='gray', linestyle='--')