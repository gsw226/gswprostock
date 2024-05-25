from flask import Flask, render_template, send_file, request, session
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
from pykrx import stock
from numpy.polynomial.polynomial import Polynomial
from datetime import datetime, timedelta



app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key'

def stock_name_to_code(stock_name):
    ticker_list = stock.get_market_ticker_list()
    for code in ticker_list:
        name = stock.get_market_ticker_name(code)
        if name == stock_name:
            print('=========')
            print(code)
            return code
    else:
        return 0

def approximation(df, degree=5):
    x = list(range(len(df)))
    y = df.values

    p = Polynomial.fit(x, y, degree)
    # y = ax^2 + bx^2 + c
    return p

def calculate_gradient_at_last_point(df, sense, degree=5):
    df = df[-sense:-1]
    if len(df) < 2:
        raise ValueError("DataFrame must contain at least two points.")
    p = approximation(df, degree)
    
    p_derivative = p.deriv()
   
    last_point = sense - 1#(df.index[-1] - df.index[0]).days
    gradient = p_derivative(last_point) / ((max(df) - min(df)) / sense)
    intercept = p(last_point) - gradient * last_point

    return gradient,intercept

from datetime import datetime, timedelta

def get_tomorrow_date():
    today = datetime.today()
    tomorrow = today + timedelta(days=1)
    return tomorrow.strftime('%Y-%m-%d')


def crawling(stock_code):
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.options.display.float_format = '{:,.0f}'.format
    warnings.simplefilter(action='ignore', category=FutureWarning)
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'}
    df = pd.DataFrame()
    sort_df = pd.DataFrame()
    sise_url = f'https://finance.naver.com/item/sise_day.nhn?code={stock_code}'    
    # sise_url = 'https://finance.naver.com/item/sise_day.nhn?code=072870'    
    for page in range(1,31):
        page_url = '{}&page={}'.format(sise_url, page)
        response = requests.get(page_url, headers=headers)
        html = bs(response.text, 'html.parser')
        html_table = html.select("table")
        table = pd.read_html(str(html_table))
        df = pd.concat([df, table[0].dropna()])
    return df
def sum(df):
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

def make_plt(df,sort_df,sma5_,sma20_,sma100_,upper_,lower_):
    addplt = []
    a = BytesIO()
    
    if sma5_== 'sma5':
        sma5 = mpf.make_addplot(sort_df['sma5'],type='line',color = 'r', width=1, alpha=0.5)
        addplt.append(sma5)
    if sma20_== 'sma20':
        sma20 = mpf.make_addplot(sort_df['sma20'],type='line',color = 'b', width=1, alpha=0.5)
        addplt.append(sma20)
    if sma100_== 'sma100':
        sma100 = mpf.make_addplot(sort_df['sma100'],type='line',color = 'g', width=1, alpha=0.5)
        addplt.append(sma100)
    if upper_== 'upper':
        upper = mpf.make_addplot(sort_df['upper'],type='line',color = 'y', width=0.7, alpha=1)
        addplt.append(upper)
    if lower_== 'lower':
        lower = mpf.make_addplot(sort_df['lower'],type='line',color = 'y', width=0.7, alpha=1)
        addplt.append(lower)
    mpf.plot(sort_df, type='candle', addplot=addplt,style='charles',show_nontrading=True,figratio=(15,6),savefig = a)
    
    return a


@app.route('/ma')
def ma():
    stock_name = session.get('stock_name', '')
    
    stock_code = stock_name_to_code(stock_name)
    df = crawling(stock_code)
    df = df.reset_index(drop=True)
    df.drop(columns=['전일비'], inplace=True)
    df = df.rename(columns={"날짜": "date", "시가": "open", "고가": "high", "저가": "low", "종가": "close", "거래량": "volume"})
    print(df)
    sort_df = sum(df)
    

    sma5_gradient = calculate_gradient_at_last_point(sort_df['sma5'],5, degree=2)
    sma20_gradient= calculate_gradient_at_last_point(sort_df['sma20'],10, degree=2)
    sma100_gradient= calculate_gradient_at_last_point(sort_df['sma100'],20, degree=2)
    print(sma5_gradient,sma20_gradient,sma100_gradient)

    sma5_graph = sma5_gradient[0]*3000 + sma5_gradient[1]
    sma20_graph = sma20_gradient[0]*20000 + sma20_gradient[1]
    sma100_graph = sma100_gradient[0]*100000 + sma100_gradient[1]

    c = 0
    if sma5_graph > df['close'].iloc[0]:
        print('sma5: 매매')
        c += 1
    else:
        print('sma5: 매도')
        c -= 1

    if sma20_graph > df['close'].iloc[0]:
        print('sma20: 매매')
        c += 1
    else:
        print('sma20: 매도')
        c -= 1

    if sma100_graph > df['close'].iloc[0]:
        print('sma100: 매매')
        c += 1
    else:
        print('sma100: 매도')
        c -= 1

    if c > 0:
        print('최종: 매매')
    else:
        print('최종: 매도')         
    sum_graph = (sma5_graph+sma20_graph+sma100_graph)/3
    expected_profit = sum_graph - df['close'].iloc[0]
    print('예상 종가:',sum_graph)
    print('예상 순수익:',expected_profit)
    sma5_ = session.get('sma5', '')
    sma20_ = session.get('sma20', '')
    sma100_ = session.get('sma100', '')
    upper_ = session.get('upper', '')
    lower_ = session.get('lower', '')

    a = make_plt(df, sort_df, sma5_, sma20_, sma100_, upper_, lower_)
    a.seek(0)

    return send_file(a, mimetype='image/png')

@app.route('/1', methods=['POST', 'GET'])
def a():
    if request.method == 'POST':
        stock_name = request.form.get('stock_name')
        sma5_ = request.form.get('sma5')
        sma20_ = request.form.get('sma20')
        sma100_ = request.form.get('sma100')
        upper_ = request.form.get('upper')
        lower_ = request.form.get('lower')
        
        session['stock_name'] = stock_name
        session['sma5'] = sma5_
        session['sma20'] = sma20_
        session['sma100'] = sma100_
        session['upper'] = upper_
        session['lower'] = lower_
    return render_template('a_2.html')



@app.route('/')
def home():
    return render_template('a.html')



if __name__ == '__main__':
    app.run(debug=True)