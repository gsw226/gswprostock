import matplotlib
matplotlib.use('Agg')  # Use Agg backend for matplotlib

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, session, redirect
from flask_migrate import Migrate
import pandas as pd
import base64
import re

from controller import crawling
from controller import name_to_code
from controller import calculate_expected
from controller import sum
from controller import make_plt
from controller import hash_password
from controller import unhash_password
from controller import decide
from controller import code_to_name
from sqlalchemy.exc import IntegrityError

import subprocess
import schedule
import time
import threading

import time
from datetime import datetime


db = SQLAlchemy()
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
    account = db.Column(db.Integer)

class favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), nullable=False)
    stock_name = db.Column(db.String(80), nullable=False)  # UNIQUE 제약 조건 추가

class own(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), nullable=False)
    stock_name = db.Column(db.String(80), nullable=False)
    date_time = db.Column(db.Integer, nullable=False)
    buy_sell = db.Column(db.Integer, nullable=False)
    many = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    # percent = db.Column(db.Real, nullable=False)
    # method = db.Column(db.String(120), nullable=False)
with app.app_context():
    db.create_all()

# Define the function to be executed via subprocess and log output in real-time
def my_scheduled_function():
    print("Executing crawling.py at 15:00")
    
    # Use subprocess to run crawling.py and log output in real-time
    command = ['python', 'crawling.py']
    try:
        # Use Popen to allow real-time logging
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Continuously read stdout and stderr in real-time
        for line in process.stdout:
            print(line, end="")  # Print each line to the console in real-time
        
        # Read and print any errors
        for error_line in process.stderr:
            print("Error:", error_line, end="")

        # Wait for the process to finish
        process.wait()
        print("crawling.py completed with return code", process.returncode)

    except Exception as e:
        print(f"Failed to run crawling.py: {e}")

def check_time():
    while True:
        current_time = datetime.now().time()
        target_time = datetime.strptime("15:40:00", "%H:%M:%S").time()
        print(current_time)
        print(target_time)
        if current_time.hour == target_time.hour and current_time.minute == target_time.minute:
            my_scheduled_function()
            time.sleep(60)
        time.sleep(10)  

def start_background_task():
    thread = threading.Thread(target=check_time)
    thread.daemon = True 
    thread.start()  



@app.route('/' ,methods=['POST','GET'])
def index():
    uid = session.get('uid','')
    #즐겨찾는 종목처리를 일로넘김
    if uid == None:
        redirect("/sign")
    results = favorite.query.filter_by(email=uid).all()
    print('result')
    print(results)
    stock_lst = [result.stock_name for result in results]
    stock_lst = stock_lst[-3:]  # 가장 밑에 있는 3개
    stock_lst = stock_lst + [0] * (3 - len(stock_lst))  # 기본값으로 0을 추가
    print('result')
    stock_number = "005930"
    url = "/chart/"+stock_number
    if request.method == 'POST':
        stock_name = request.form.get('stock_name')
        num = name_to_code(stock_name=stock_name)
        stock_number = str(num)
        # sma5_ = request.form.get('sma5') or ''
        # sma20_ = request.form.get('sma20') or ''
        # sma100_ = request.form.get('sma100') or ''
        # upper_ = request.form.get('upper') or ''
        # lower_ = request.form.get('lower') or ''
        favor = request.form.get('favor') or ''
        # print(sma5_,sma20_,sma100_,upper_,lower_,favor)
        options = ','.join(val for val in [favor] if val)
        url = f"/chart/{stock_number}?name={stock_name}"
    return redirect(url)


@app.route('/ma')
def ma(stock_name, sma5_, sma20_, sma100_, upper_, lower_, sort_df=None):

    a = make_plt(sort_df,sma5_,sma20_,sma100_,upper_,lower_)
    a.seek(0)
    return a.read()
    # return "<div>Not found File</div>"


@app.route('/buy/<num>', methods=['POST', 'GET'])  # POST와 GET 메서드 모두 허용
def buy(num):
    buy = request.form.get('stock_name')
    number = request.form.get('number')
    uid = session.get('uid', '')
    stock_name = code_to_name(num)
    print(stock_name)
    
    if request.method == 'POST':
        # print('1111')
        if uid != '':
            print('222')
            close_df = pd.read_csv('stock_data.csv')
            close_df.drop(close_df.columns[3], axis=1, inplace=True)
            
            # 수정된 부분: or 대신 | 사용
            filtered_df = close_df[(close_df['한글 종목약명'] == stock_name) | (close_df['한글 종목명'] == stock_name)]
            print(filtered_df['어제종가'].iloc[0])
            price= filtered_df['어제종가'].iloc[0]
            # filtered_df가 비어있지 않은지 확인
            if not filtered_df.empty:
                if buy == 'buy':
                    user_account = User.query.filter_by(email=uid).first().account
                    new_own = own(email=uid, stock_name=stock_name, date_time=20240226, buy_sell='buy',many=number,price=price)
                    db.session.add(new_own)
                    db.session.commit()

                    # print(user_account)
            else:
                print("해당 주식이 없습니다.")  # 주식이 없는 경우 처리
            
        return redirect('/')
    
    print('33')
    # GET 요청 처리
    return render_template('buy.html', stock_name=stock_name, num=num)  # GET 요청 시 buy.html 템플릿을 렌더링
     

@app.route('/chart/<num>', methods=['POST', 'GET'])
def a(num):
    uid = session.get('uid','')
    if uid == None:
        redirect("/sign")
    sma_expect = []
    sma_expect_profit = []
    expect = ''
    # stock_name = request.args.get('name') or 0
    stock_name = code_to_name(num)
    print(stock_name)
    # sma5_ = 0
    # sma20_ = 0
    # sma100_ = 0
    # upper_ = 0
    # lower_ = 0
    sort_df = pd.DataFrame
    if uid != '':
        if request.method == 'GET':
            df = crawling(num)
            sort_df = sum(df)
            favor = None
            
            options = request.args.get('options', '').split(',')
            print(options)
            if 'sma5' in options:
                sma5_ = 'sma5'
            if 'sma20' in options:
                sma20_ = 'sma20'
            if 'sma100' in options:
                sma100_ = 'sma100'
            if 'upper' in options:
                upper_ = 'upper'
            if 'lower' in options:
                lower_ = 'lower'
            if 'favor' in options:
                favor = 'favor'
            if favor == 'favor':
                # Check if the stock_name already exists for the user
                existing_favorite = favorite.query.filter_by(email=uid, stock_name=stock_name).first()
                if not existing_favorite:
                    print("INSERT")
                    new_favorite = favorite(email=uid, stock_name=stock_name)
                    db.session.add(new_favorite)
                    db.session.commit()
                else:
                    print('종복')
            close_df = pd.read_csv("./stock_data.csv")
            close_df.drop(close_df.columns[3], axis=1, inplace=True)
            print(close_df.head(10).to_string())

            favorite_stocks = favorite.query.filter_by(email=uid).all()
            print(favorite_stocks)
            favorite_stock_names = [fav.stock_name for fav in favorite_stocks]
            print(favorite_stock_names)
            # filtered_close_df = close_df[close_df['단축코드'].isin(favorite_stock_names)]
            
            # print(filtered_close_df.head(10).to_string())
            
            if num != 0:
                df = crawling(num)
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
                expect = decide(sma_expect=sma_expect,sma_expect_profit=sma_expect_profit,sma5_expect_profit=sma5_expect_profit,sma20_expect_profit=sma20_expect_profit)
            
            results = favorite.query.filter_by(email=uid).all()
            print('result')
            print(results)
            stock_lst = [result.stock_name for result in results]
            stock_lst = stock_lst[-3:]  # 가장 밑에 있는 3개
            stock_lst = stock_lst + [0] * (3 - len(stock_lst))
            img = ma(stock_name,sma5_,sma20_,sma100_,upper_,lower_,sort_df)

            if type(img) != bytes:
                img = img.encode('utf-8')
            if img != '':
                img = base64.b64encode(img).decode('utf-8')
                candlestick_data = [
                    {
                        'x': index,
                        'y': [row['open'], row['high'], row['low'], row['close']]
                    }
                    for index, row in sort_df.iterrows()
                ]
                sma5_data = [
                    {
                        'x': index,
                        'y': 0 if pd.isna(row['sma5']) else row['sma5']
                    }
                    for index, row in sort_df.iterrows()
                ]
                # 추가된 데이터
                sma20_data = [
                    {
                        'x': index,
                        'y': 0 if pd.isna(row['sma20']) else row['sma20']
                    }
                    for index, row in sort_df.iterrows()
                ]
                sma100_data = [
                    {
                        'x': index,
                        'y': 0 if pd.isna(row['sma100']) else row['sma100']
                    }
                    for index, row in sort_df.iterrows()
                ]
                upper_data = [
                    {
                        'x': index,
                        'y': 0 if pd.isna(row['upper']) else row['upper']
                    }
                    for index, row in sort_df.iterrows()
                ]
                lower_data = [
                    {
                        'x': index,
                        'y': 0 if pd.isna(row['lower']) else row['lower']
                    }
                    for index, row in sort_df.iterrows()
                ]
                # 그래프에 추가할 데이터 리스트
                all_data = {
                    'candlestick': candlestick_data,
                    'sma5': sma5_data,
                    'sma20': sma20_data,
                    'sma100': sma100_data,
                    'upper': upper_data,
                    'lower': lower_data
                }
                # 데이터가 없을 경우 빈 리스트로 초기화
                sma5_data = sma5_data if sma5_data is not None else []
                sma20_data = sma20_data if sma20_data is not None else []
                sma100_data = sma100_data if sma100_data is not None else []
                upper_data = upper_data if upper_data is not None else []
                lower_data = lower_data if lower_data is not None else []

                return render_template('a_2.html', 
                                       imgdata=img,
                                       lst1=sma_expect,
                                       lst2=sma_expect_profit,
                                       expect=expect,
                                       stock_name=stock_name,
                                       stock_lst=stock_lst,
                                       uid=uid,
                                       candlestick_data=all_data,
                                       sma5_data=sma5_data,  # 추가
                                       sma20_data=sma20_data,  # 추가
                                       sma100_data=sma100_data,  # 추가
                                       upper_data=upper_data,  # 추가
                                       lower_data=lower_data,  # 추가
                                       num=num)
            else: 
                return render_template('a_2.html',imgdata = img ,lst1 = sma_expect,lst2 = sma_expect_profit, expect = expect, stock_name = stock_name,uid=uid,candlestick_data=sort_df,num=num)
    else:
        return redirect('/sign')
    


@app.route('/sign', methods=['POST', 'GET'])  # 이메일, 비밀번호 db로 전송
def sign():
    password_pattern = r'^(?=.*[!@#$%^&*(),.?":{}|<>])(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).+$'
    
    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        password_2 = request.form.get('password_2', '')
        
        if email == '' or password == '':
            return render_template('/sign.html' , msg = "아이디 또는 비밀번호를 입력하세요.")
        
        if re.match(password_pattern, password):
            if password == password_2:
                hashed_password = hash_password(password)
                user = User.query.filter_by(email=email).first()
                if user != email:
                    new_user = User(email=email, password=hashed_password, account=10000000)
                    db.session.add(new_user)
                    db.session.commit()
                    return render_template('login.html', msg = "성공적으로 회원가입 완료")
                else:
                    return render_template('/sign.html', msg = "이메일이 중복 됩니다.")
            else: 
                return render_template('/sign.html', msg = "비밀번호가 일치하지 않습니다.")
        else:
            return render_template('/sign.html', msg = "비밀번호 규칙을 확인하세요.")
    else:
        return render_template('sign.html')



@app.route('/login', methods=['POST','GET']) # 이메일, 비밀번호, 잔고 db로 전송
def login():
    if request.method == 'POST':
        
        login_email = request.form['login_email']
        login_password = request.form['login_password']
        user = User.query.filter_by(email=login_email).first()
        if user.email == login_email:
            if unhash_password(login_password,user.password):
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
        print('1_1_1',result_strings)
        file_path = './stock_data.csv'
        lst = pd.read_csv(file_path)
        lst.drop(lst.columns[3], axis=1, inplace=True)
        print('2_2_2',lst)
        test = []
        if result_strings is not None:
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


@app.route('/my/check', methods=['POST', 'GET'])
def my_page_check():
    uid = session.get('uid','')
    results = User.query.filter_by(email=uid).first()
    if request.method == 'POST':
        check_email = request.form.get('check_email')
        check_password = request.form.get('check_password')
        if check_email == results.email:
            password=unhash_password(results.password)
            if check_password == password:
                return render_template('real_my/')
        
    return render_template('my_check.html')

@app.route("/remove", methods=['POST'])
def remove_account():
    #print()
    return "success", 200

if __name__ == '__main__':
    print(datetime.now())
    start_background_task()
    app.run(host="0.0.0.0", port="443", debug=True,ssl_context="adhoc")