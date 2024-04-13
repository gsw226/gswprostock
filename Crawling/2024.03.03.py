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

from tensorflow.keras.models import Sequential      
from tensorflow.keras.layers import Dense
from tensorflow.keras import optimizers




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
df = df.iloc[0:100] #크롤링을해서 긁어낸 데이터를 저장한 "배열"

df = df.sort_values(by='날짜')

print(df)
x = df["날짜"]
y = df["종가"]

model = Sequential()
# 출력 y의 차원은 1. 입력 x의 차원(input_dim)은 1
# 선형 회귀이므로 activation은 'linear'
model.add(Dense(1, input_dim=1, activation='linear'))

# sgd는 경사 하강법을 의미. 학습률(learning rate, lr)은 0.01.
sgd = optimizers.SGD(lr=0.01)

# 손실 함수(Loss function)은 평균제곱오차 mse를 사용합니다.
model.compile(optimizer=sgd, loss='mse', metrics=['mse'])

# 주어진 x와 y데이터에 대해서 오차를 최소화하는 작업을 300번 시도합니다.
model.fit(x, y, epochs=300)


plt.plot(x, model.predict(x), 'b', x, y, 'k.')



#model = LinearRegression()
#model.fit(df[['날짜']], df['종가'])

# plt.figure(figsize=(15, 5))
# plt.title('Celltrion (close)')
# plt.xticks(rotation=45) 
# plt.plot(df['날짜'], df['종가'], 'co-')
# plt.grid(color='gray', linestyle='--')
# plt.show()

#df['날짜'] = pd.to_datetime(df['날짜'], format='%Y.%m.%d')


# 선형 회귀 모델 피팅


# 모델을 사용하여 예측
#predictions = model.predict(df[['날짜']])

#plt.figure(figsize=(15, 5))
#plt.title('종가에 대한 선형 회귀 그래프')
#plt.xticks(rotation=45)
#plt.plot(df['날짜'], df['종가'], 'co-', label='원래 데이터')
#plt.plot(df['날짜'], predictions, 'r-', label='선형 회귀선')
#plt.legend()
#plt.grid(color='gray', linestyle='--')
#plt.show()