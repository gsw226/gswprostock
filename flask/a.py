from flask import Flask, render_template, send_file
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import numpy as np
import warnings
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import mplfinance as mpf
from io import BytesIO

app = Flask(__name__)
def crawling():
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.options.display.float_format = '{:,.0f}'.format
    warnings.simplefilter(action='ignore', category=FutureWarning)
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'}
    df = pd.DataFrame()
    sort_df = pd.DataFrame()
    sise_url = f'https://finance.naver.com/item/sise_day.nhn?code=068270'
    for page in range(1,51):
        page_url = '{}&page={}'.format(sise_url, page)
        response = requests.get(page_url, headers=headers)
        html = bs(response.text, 'html.parser')
        html_table = html.select("table")
        table = pd.read_html(str(html_table))
        df = pd.concat([df, table[0].dropna()])
    return df
def sum(df):
    df = df.reset_index(drop=True)
    df.drop(columns=['전일비'], inplace=True)
    df = df.rename(columns={"날짜":"date","시가":"open","고가":"high","저가":"low","종가":"close","거래량":"volume"})

    sort_df = df.sort_index(ascending=False)
    date_format = "%Y.%m.%d"
    sort_df['date'] = pd.to_datetime(sort_df['date'], format=date_format)
    sort_df.set_index('date',inplace=True)

    df['date'] = pd.to_datetime(df['date'], format=date_format)
    df.set_index('date',inplace=True)
    # df['날짜_정수'] = df['date'].dt.strftime('%Y%m%d').astype(int)

    sort_df['sma5'] = sort_df['close'].rolling(window=5).mean()
    sort_df['sma20'] = sort_df['close'].rolling(window=20).mean()
    sort_df['sma100'] = sort_df['close'].rolling(window=100).mean()

    sort_df['stddev'] = sort_df['close'].rolling(window=20).std()
    sort_df['upper'] = sort_df['sma20'] + (sort_df['stddev']*2)
    sort_df['lower'] = sort_df['sma20'] - (sort_df['stddev']*2)
    return sort_df
def make_plt(df,sort_df):
    sma5 = mpf.make_addplot(sort_df['sma5'],type='line',color = 'r', width=1, alpha=0.5)
    sma20 = mpf.make_addplot(sort_df['sma20'],type='line',color = 'b', width=1, alpha=0.5)
    sma100 = mpf.make_addplot(sort_df['sma100'],type='line',color = 'g', width=1, alpha=0.5)

    upper = mpf.make_addplot(sort_df['upper'],type='line',color = 'y', width=0.7, alpha=1)
    lower = mpf.make_addplot(sort_df['lower'],type='line',color = 'y', width=0.7, alpha=1)
    
    a = BytesIO()

    mpf.plot(sort_df, type='candle', addplot=[sma5,sma20,sma100,upper,lower],style='charles',show_nontrading=True,figratio=(15,6),savefig = a)
    return a

@app.route('/1')
def a():
    return render_template('a.html')


@app.route('/2')
def ab():
    a = 3
    return render_template('b.html', parameter = a)


@app.route('/abc')
def abc():
    df = crawling()
    sort_df = sum(df)
    a = make_plt(df,sort_df)
    a.seek(0)
    return send_file(a, mimetype='image/png')

if __name__ == '__main__':
    app.run()   