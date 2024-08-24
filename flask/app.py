import json
import ssl
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, session, redirect, jsonify
from flask_migrate import Migrate
db = SQLAlchemy()
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import warnings
import matplotlib
matplotlib.use('Agg')
import mplfinance as mpf
from io import BytesIO
from numpy.polynomial.polynomial import Polynomial
import base64
import schedule
import time
from datetime import datetime
import re
import ssl
from passlib.hash import pbkdf2_sha256
from controller import crawling
from controller import stock_name_to_code
from controller import calculate_expected
from controller import sum
from controller import make_plt
from controller import hash_password
from controller import check_password


app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), nullable=False)
    stock_name = db.Column(db.String(80), nullable=False, unique=True)

class own(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), nullable=False)
    date_time = db.Column(db.Integer, nullable=False)
    stock_name = db.Column(db.String(80), nullable=False)
    buy_sell = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    # percent = db.Column(db.Real, nullable=False)
    # method = db.Column(db.String(120), nullable=False)
with app.app_context():
    db.create_all()

@app.route('/chart/<int:num>')
def num(num):
    num = str(num)
    if len(num) < 6:
        num = num.zfill(6)
    file_path = '/Users/gangsang-u/Documents/GitHub/gsw226-s_file/flask/stock.csv'
    df = pd.read_csv(file_path)
    
    print('---------',df)

    df = crawling(num)
    sort_df = sum(df)

    img_stream = make_plt(sort_df, 0, 0, 0, 0, 0)
    
    if isinstance(img_stream, BytesIO):
        img_bytes = img_stream.getvalue()
    else:
        raise TypeError("Expected a BytesIO object")

    if img_bytes:
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    else:
        img_base64 = ''
    return render_template('chart.html', img=img_base64,stock_name=row)

@app.route('/ma')
def ma(stock_name,sma5_,sma20_,sma100_,upper_,lower_,sort_df):
    if stock_name != '' and stock_name != 0:
        a = make_plt(sort_df,sma5_,sma20_,sma100_,upper_,lower_)
        a.seek(0)
        # print('aaaaa')
        # print(a.read)
        return a.read()
    return "<div>Not found File</div>"

@app.route('/buy', methods=['POST'])
def buy():
     if request.method == 'POST':
        #세션에서 내이름 뽑기
        #내 이름으로 보유금액 가져오기
        #보유금액에서 구매가격 만큼 차감 가져온걸 그대로 저장
        #내 돈에서 주식현재가격 빼고, 저장
        #차감되었으면, 구매해서 own테이블에 담기
        #own도 저  장
        return redirect('/')
@app.route('/', methods=['POST', 'GET'])
def a():
    uid = session.get('uid','')
    #여기서 세션에 사용자 정보 없으면, 로그인 페이지 리디렉션
    if uid == None:
        redirect("/sign")
    # schedule.every().day.at("00:00").do(xa)
    sma_expect = []
    sma_expect_profit = []
    expect = ''
    stock_name = 0
    sma5_ = 0
    sma20_ = 0
    sma100_ = 0
    upper_ = 0
    lower_ = 0
    sort_df = pd.DataFrame
    print('aaaaaaa')
    print(uid)
    if uid != '':
        # results = favorite.query.filter_by(email=uid).order_by(favorite.id.asc()).limit(3).all()
        results = favorite.query.filter_by(email=uid)
        stock_lst = [result.stock_name for result in results]
        if stock_lst == None:
            stock_lst = ['0','0','0']
        if request.method == 'POST':
            # stock_name[len(stock_lst)] = ''
            # if len(stock_lst) > 0:
            #     stock_name = stock_lst[len(stock_lst)-1]
            # else:
            stock_name = request.form.get('stock_name')
            sma5_ = request.form.get('sma5')
            sma20_ = request.form.get('sma20')
            sma100_ = request.form.get('sma100')
            upper_ = request.form.get('upper')
            lower_ = request.form.get('lower') 
            favor = request.form.get('favor')
            buy = request.form.get('buy') 
            sell = request.form.get('sell') 

            if stock_name != '':
                if favor != None:
                    new = favorite(email=uid,stock_name=stock_name)
                    db.session.add(new)
                    db.session.commit()
                stock_code = stock_name_to_code(stock_name)
                stock_code = str(stock_code)
                df = crawling(stock_code)
                print(sort_df)
                sort_df = sum(df)   
                sma5_expect = calculate_expected(sort_df['sma5'],5, degree=2)
                sma20_expect= calculate_expected(sort_df['sma20'],20, degree=3)
                sma100_expect= calculate_expected(sort_df['sma100'],100, degree=5)
                
                sma5_expect_profit = sma5_expect - df['close'].iloc[0]
                sma20_expect_profit = sma20_expect - df['close'].iloc[0]
                sma100_expect_profit = sma100_expect - df['close'].iloc[0]

                sma5_expect_profit = round(sma5_expect_profit, 2)
                sma20_expect_profit = round(sma20_expect_profit, 2)
                sma100_expect_profit = round(sma100_expect_profit, 2)

                sma5_expect = round(sma5_expect, 2)
                sma20_expect= round(sma20_expect, 2)
                sma100_expect= round(sma100_expect, 2)

                sma_expect.append(sma5_expect)
                sma_expect.append(sma20_expect)
                sma_expect.append(sma100_expect)
            
                sma_expect_profit.append(sma5_expect_profit)
                sma_expect_profit.append(sma20_expect_profit)
                sma_expect_profit.append(sma100_expect_profit)
                if not(sma_expect[0] =='' and sma_expect[1]=='' and sma_expect[2]==''):
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
            late_close = sort_df['close'].iloc[-1]
            late_date = sort_df.index[-1]
            print('9999999999',late_date)
            
            img = ma(stock_name,sma5_,sma20_,sma100_,upper_,lower_,sort_df)

            if type(img) != bytes:
                img = img.encode('utf-8')
            if img != '':
                img = base64.b64encode(img).decode('utf-8')
                return render_template('a_2.html',imgdata = img ,lst1 = sma_expect,lst2 = sma_expect_profit, expect = expect, stock_name = stock_name, stock_lst = stock_lst)
            else: 
                return render_template('a_2.html',imgdata = img ,lst1 = sma_expect,lst2 = sma_expect_profit, expect = expect, stock_name = stock_name)
        else:
            return render_template('a_2.html')
    else:
        return redirect('/sign')
    
@app.route('/sign', methods=['POST', 'GET'])  # 이메일, 비밀번호 db로 전송
def sign():
    password_pattern = r'^(?=.*[!@#$%^&*(),.?":{}|<>])(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).+$'
    
    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        
        if email == '' or password == '':
            return redirect('/sign')
        
        if re.match(password_pattern, password):
            hashed_password = hash_password(password)
            new_user = User(email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return render_template('login.html')
        else:
            return redirect('/sign')
    else:
        return render_template('sign.html')


@app.route('/login', methods=['POST','GET']) # 이메일, 비밀번호, 잔고 db로 전송
def login():
    if request.method == 'POST':
        
        login_email = request.form['login_email']
        login_password = request.form['login_password']
        user = User.query.filter_by(email=login_email).first()
        if user.email == login_email:
            if check_password(login_password,user.password):
                session['uid'] = login_email
                
                return redirect('/') 
            else:
                return render_template('login.html')
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')
        

@app.route('/list', methods=['POST', 'GET'])
def list_stock():
    try:
        uid = session.get('uid','')
        print(uid)
        # results = favorite.query.filter_by(email=uid).all()
        results = favorite.query.with_entities(favorite.stock_name).filter_by(email=uid).all()
        result_strings = [item[0] for item in results]
        print(result_strings)
        file_path = '/Users/gangsang-u/Documents/GitHub/gsw226-s_file/flask/stock_data.csv'
        lst = pd.read_csv(file_path)
        lst.drop(lst.columns[3], axis=1, inplace=True)
        print(lst)
        test = []
        for i in result_strings:
            a = lst[lst['한글 종목약명'] == i]
            print('------',a.values)
            test.extend(a.values)
            # test.append(a.values)

        print(test[0])
        result_df = pd.DataFrame(test)
        result_df.columns = ['단축코드','한글 종목명','한글 종목약명','어제종가']
        # print(result_df)
        lst_table = lst.to_html(classes='table table-striped')
        result_table = result_df.to_html(classes='table table-striped')
        return render_template('list.html', table=lst_table, favor_lst = result_table)
    except FileNotFoundError:
        return "Stock data file not found.", 404
    except Exception as e:
        return f"An error occurred: {e}", 500 

@app.route('/my', methods=['POST', 'GET'])
def my_page():
    if request.method == 'POST':
        auto = request.form.get('auto')
        if auto:
            offensive = request.form.get('offensive')
            balance = request.form.get('balance')
            defend = request.form.get('defend')
            if offensive:
                print('off')
            elif balance:
                print('bal')
            else:
                print('def')
    return render_template('my.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="443", ssl_context="adhoc")