import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import numpy as np
import warnings
import matplotlib.pyplot as plt
import mplfinance as mpf
from pykrx import stock

def stock_name_to_code(stock_name):
    ticker_list = stock.get_market_ticker_list()
    
    for code in ticker_list:
        name = stock.get_market_ticker_name(code)
        if name == stock_name:
            return code
    else:
        return 0
def right(upper,lower,sma5,sma100):
    boll = int(input('볼린저가 수렴했나요?(수렴했으면1 안햇으면0)'))
    if boll == 1:
        buy(upper,lower,sma5,sma100)
    else:
        sell(upper,lower,sma5,sma100)
def op(upper,lower,sma5,sma100):
    if sma5 >

def sell(upper,lower,sma5,sma100):
    for a,i in enumerate(sma5):
        for b,j in enumerate(sma100):
            
# def buy:  
def right_or_op(upper,lower,sma 5,sma100):
    for a,i in enumerate(sma5):
        for b,j in enumerate(sma100):
            if i > j:
                right(upper,lower,sma5,sma100)
            elif i < j:
                op(upper,lower,sma5,sma100)


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.options.display.float_format = '{:,.0f}'.format
warnings.simplefilter(action='ignore', category=FutureWarning)

while 1:
    stock_name = input('종목 입력:')
    stock_code = stock_name_to_code(stock_name)
    if stock_code != 0:
        print(f"{stock_name}의 종목 코드는 {stock_code}입니다.")
        break
    else:
        print('종목 코드를 찾을 수 없습니다')

headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'}
df = pd.DataFrame()
excel_df = pd.DataFrame()
sise_url = f'https://finance.naver.com/item/sise_day.nhn?code={stock_code}'
for page in range(1,51):
    page_url = '{}&page={}'.format(sise_url, page)
    response = requests.get(page_url, headers=headers)
    html = bs(response.text, 'html.parser')
    html_table = html.select("table")
    table = pd.read_html(str(html_table))
    df = pd.concat([df, table[0].dropna()])

df = df.reset_index(drop=True)
df.drop(columns=['전일비'], inplace=True)
df = df.rename(columns={"날짜":"date","시가":"open","고가":"high","저가":"low","종가":"close","거래량":"volume"})

# ================================================================
sort_df = df.sort_index(ascending=False)
date_format = "%Y.%m.%d"
sort_df['date'] = pd.to_datetime(sort_df['date'], format=date_format)
sort_df.set_index('date',inplace=True)

df['date'] = pd.to_datetime(df['date'], format=date_format)
df.set_index('date',inplace=True)

sort_df['sma5'] = sort_df['close'].rolling(window=5).mean()
sort_df['sma20'] = sort_df['close'].rolling(window=20).mean()
sort_df['sma100'] = sort_df['close'].rolling(window=100).mean()

df['stddev'] = sort_df['close'].rolling(window=20).std()
sort_df['upper'] = sort_df['sma20'] + (df['stddev']*2)
sort_df['lower'] = sort_df['sma20'] - (df['stddev']*2)

sma5_list = sort_df['sma5'].tolist()
sma100_list = sort_df['sma100'].tolist()
upper_list = sort_df['upper'].tolist()
lower_list = sort_df['lower'].tolist()

right_or_op(upper_list,lower_list,sma5_list,sma100_list)

sma5 = mpf.make_addplot(sort_df['sma5'],type='line',color = 'r', width=1, alpha=0.5)
sma20 = mpf.make_addplot(sort_df['sma20'],type='line',color = 'b', width=1, alpha=0.5)
sma100 = mpf.make_addplot(sort_df['sma100'],type='line',color = 'g', width=1, alpha=0.5)

upper = mpf.make_addplot(sort_df['upper'],type='line',color = 'y', width=0.7, alpha=1)
lower = mpf.make_addplot(sort_df['lower'],type='line',color = 'y', width=0.7, alpha=1)

mpf.plot(sort_df, type='candle', addplot=[sma5,sma20,sma100,upper,lower],style='charles',show_nontrading=True,figratio=(15, 6))