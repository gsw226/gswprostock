from flask import Flask, render_template, send_file, request, session
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import warnings
import matplotlib
matplotlib.use('Agg')
import mplfinance as mpf
from io import BytesIO
from pykrx import stock
from numpy.polynomial.polynomial import Polynomial
import investpy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key'

# def stock_name_to_code(stock_name):
#     stock_list = investpy.stocks.get_stocks(country='south korea')
    
#     stock_list.reset_index(drop=True, inplace=True)
    
#     stock_row = stock_list[stock_list['name'] == stock_name]
#     if not stock_row.empty:
#         return stock_row.iloc[0]['symbol']
    
#     return None
# ===========================
#     ticker_list = stock.get_market_ticker_list()
        
#         for code in ticker_list:
#             name = stock.get_market_ticker_name(code)
#             if name == stock_name:
#                 return code
#         else:
#             return 0

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
   
    last_point = sense - 1
    gradient = p_derivative(last_point) / ((max(df) - min(df)) / sense)
    intercept = p(last_point) - gradient * last_point

    return gradient,intercept

def calculate_expected(df, sense, degree=5):
    df = df[-sense:-1]
    if len(df) < 2:
        raise ValueError("DataFrame must contain at least two points.")
    p = approximation(df, degree)
    
    return p(sense)


def crawling():
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.options.display.float_format = '{:,.0f}'.format
    warnings.simplefilter(action='ignore', category=FutureWarning)
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'}
    df = pd.DataFrame()
    # sise_url = f'https://finance.naver.com/item/sise_day.nhn?code={stock_code}'    
    sise_url = f'https://finance.naver.com/item/sise_day.nhn?code=005930'    
    for page in range(1,31):
        page_url = '{}&page={}'.format(sise_url, page)
        response = requests.get(page_url, headers=headers)
        if response.status_code != 200:
            print(f'Failed to retrieve data from page {page}')
            continue
        html = bs(response.text, 'html.parser')
        html_table = html.select("table")
        table = pd.read_html(str(html_table))
        df = pd.concat([df, table[0].dropna()])
        print(df)
    df = df.reset_index(drop=True)
    print("REINDEX\n",df)
    df.drop(columns=['전일비'], inplace=True)
    df = df.rename(columns={"날짜": "date", "시가": "open", "고가": "high", "저가": "low", "종가": "close", "거래량": "volume"}) 
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

def make_plt(sort_df):
    addplt = []
    a = BytesIO()
    
    sma5_ = session.get('sma5', '')
    sma20_ = session.get('sma20', '')
    sma100_ = session.get('sma100', '')
    upper_ = session.get('upper', '')
    lower_ = session.get('lower', '')
    
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
    stock_name = session['stock_name']
    print("STOCKNAME:",stock_name)
    # stock_code = stock_name_to_code(stock_name)
    df = crawling()
    #print(df)
    sort_df = sum(df)

    sma5_expect = calculate_expected(sort_df['sma5'],5, degree=2)
    sma20_expect= calculate_expected(sort_df['sma20'],20, degree=3)
    sma100_expect= calculate_expected(sort_df['sma100'],100, degree=5)
    print(sma5_expect,sma20_expect,sma100_expect)
    
    sma5_expect_profit = sma5_expect - df['close'].iloc[0]
    sma20_expect_profit = sma20_expect - df['close'].iloc[0]
    sma100_expect_profit = sma100_expect - df['close'].iloc[0]
    print(sma5_expect_profit,sma20_expect_profit,sma100_expect_profit)

    session['sma5_expect'] = sma5_expect
    session['sma20_expect'] = sma20_expect
    session['sma100_expect'] = sma100_expect

    session['sma5_expect_profit'] = sma5_expect_profit
    session['sma20_expect_profit'] = sma20_expect_profit
    session['sma100_expect_profit'] = sma100_expect_profit

    a = make_plt(sort_df)
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
        print(stock_name)
        session['stock_name'] = stock_name
        session['sma5'] = sma5_
        session['sma20'] = sma20_
        session['sma100'] = sma100_
        session['upper'] = upper_
        session['lower'] = lower_

    sma_expect = []
    sma_expect_profit = []
    sma5_expect = session.get('sma5_expect', '')
    sma_expect.append(sma5_expect)
    sma20_expect = session.get('sma20_expect', '')
    sma_expect.append(sma20_expect)
    sma100_expect = session.get('sma100_expect', '')
    sma_expect.append(sma100_expect)

    sma5_expect_profit = session.get('sma5_expect_profit', '')
    sma_expect_profit.append(sma5_expect_profit)
    sma20_expect_profit = session.get('sma20_expect_profit', '')
    sma_expect_profit.append(sma20_expect_profit)
    sma100_expect_profit = session.get('sma100_expect_profit', '')
    sma_expect_profit.append(sma100_expect_profit)

    expect = ''
    if int(max(sma_expect)) > 0:
        expect = '매매'
        if int(max(sma_expect)) == int(sma5_expect):
            expect += ' 단타'
        elif int(max(sma_expect)) == int(sma20_expect):
            expect += ' 스윙'
        else:
            expect += ' 장타'
    else:
        expect = '매도'
    
    return render_template('a_2.html',lst1 = sma_expect,lst2 = sma_expect_profit, expect = expect)
    # return render_template('a_2.html')



@app.route('/')
def home():
    return render_template('a.html')



if __name__ == '__main__':
    app.run(debug=True)