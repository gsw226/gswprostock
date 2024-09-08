import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import warnings
from io import BytesIO
import mplfinance as mpf
from numpy.polynomial.polynomial import Polynomial
from passlib.hash import pbkdf2_sha256



def crawling(stock_code):
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.options.display.float_format = '{:,.0f}'.format
    warnings.simplefilter(action='ignore', category=FutureWarning)
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'}
    df = pd.DataFrame()
    sise_url = f'https://finance.naver.com/item/sise_day.nhn?code={stock_code}'
    # sise_url = f'https://finance.naver.com/item/sise_day.nhn?code=005930'
    for page in range(1,31):
        page_url = '{}&page={}'.format(sise_url, page)
        response = requests.get(page_url, headers=headers)
        if response.status_code != 200:
            print(f'Failed to retrieve data from page {page}')
        html = bs(response.text, 'html.parser')
        html_table = html.select("table")
        table = pd.read_html(str(html_table))
        # print(table)
        df = pd.concat([df, table[0].dropna()])
    df = df.reset_index(drop=True)
    df.drop(columns=['전일비'], inplace=True)
    df = df.rename(columns={"날짜": "date", "시가": "open", "고가": "high", "저가": "low", "종가": "close", "거래량": "volume"})
    return df

def name_to_code(stock_name):
    ticker_list = pd.read_csv('./stock.csv')
    c=0
    ticker_list = ticker_list.rename(columns={'단축코드':'code','한글 종목명':'name','한글 종목약명':'short_name'})
    for code in ticker_list['short_name']:
        if stock_name == code:
            # print("C: ", c)
            # print(ticker_list.iloc[c, 0])
            stock_code = ticker_list.iloc[c, 0]
            stock_str = str(stock_code)
            if len(stock_str) < 6:
                stock_str = stock_str.zfill(6)
            return stock_str
        else:
            c += 1
    return 0

def code_to_name(stock_code):
    #stock_code = str(stock_code).zfill(6)  # 6자리 형식으로 문자열로 변환

    ticker_list = pd.read_csv('/Users/gangsang-u/Documents/GitHub/gsw226-s_file/flask/stock_data.csv')
    ticker_list = ticker_list.rename(columns={'단축코드': 'code', '한글 종목명': 'name', '한글 종목약명': 'short_name'})

    matching_row = ticker_list[ticker_list['code'] == stock_code]
    print('01010',matching_row)

    if not matching_row.empty:
        stock_name = matching_row.iloc[0]['short_name']
        return stock_name
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

# sma 5 20 100 구하기
def sum(df):
    sort_df = df.sort_index(ascending=False)
    date_format = "%Y.%m.%d"
    sort_df['date'] = pd.to_datetime(sort_df['date'], format=date_format)
    sort_df.set_index('date',inplace=True)

    df['date'] = pd.to_datetime(df['date'], format=date_format)
    df.set_index('date',inplace=True)
    # sort_df['int_date'] = df['date'].dt.strftime('%Y%m%d').astype(int)

    sort_df['sma5'] = sort_df['close'].rolling(window=5).mean()
    sort_df['sma20'] = sort_df['close'].rolling(window=20).mean()
    sort_df['sma100'] = sort_df['close'].rolling(window=100).mean()
    
    sort_df['stddev'] = sort_df['close'].rolling(window=20).std()
    sort_df['upper'] = sort_df['sma20'] + (sort_df['stddev']*2)
    sort_df['lower'] = sort_df['sma20'] - (sort_df['stddev']*2)
    # print(sort_df)
    return sort_df

# 그레프 만들기
def make_plt(sort_df,sma5_,sma20_,sma100_,upper_,lower_):
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
    mpf.plot(sort_df, type='candle', addplot=addplt,style='charles',show_nontrading=True,figratio=(13,6),savefig = a)
    # a.read()
    return a

def decide(sma_expect,sma_expect_profit,sma5_expect_profit,sma20_expect_profit):
    if not(sma_expect[0] =='' and sma_expect[1]=='' and sma_expect[2]==''): #얘네 걍 싹다 함수로
                    if int(max(sma_expect_profit)) > 0:
                        expect = '매매'
                        if int(max(sma_expect_profit)) == int(sma5_expect_profit):
                            expect += ' 단타'
                        elif int(max(sma_expect_profit)) == int(sma20_expect_profit):
                            expect += ' 스윙'
                        else:
                            expect += ' 장타'
                    else:
                        expect = '매도'
    return expect

# 암호화
def hash_password(original_password):
    salt = 'gsw226'
    password = original_password + salt
    hashed_password = pbkdf2_sha256.hash(password)
    return hashed_password
# 복호화
def unhash_password(original_password, hashed_password):
    salt = 'gsw226'
    password = original_password + salt
    return pbkdf2_sha256.verify(password, hashed_password)
