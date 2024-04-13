import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from datetime import datetime
from matplotlib import dates as mdates
from bs4 import BeautifulSoup as bs
import requests


headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'}

df = pd.DataFrame()
sise_url = 'https://finance.naver.com/item/sise_day.nhn?code=068270'

for page in range(1, 10):
    page_url = '{}&page={}'.format(sise_url, page)
    response = requests.get(page_url, headers=headers)
    html = bs(response.text, 'html.parser')
    html_table = html.select("table")
    table = pd.read_html(str(html_table))
    df = pd.concat([df, table[0].dropna()])

df = df.dropna()
df = df.iloc[0:30]
df = df.sort_values(by='날짜')

df['날짜'] = pd.to_datetime(df['날짜'], format='%Y.%m.%d')
df['날짜'] = mdates.date2num(df['날짜'])


X = df[['날짜']]
y = df['종가']

print(X)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


model = LinearRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)


mse = mean_squared_error(y_test, y_pred)
print(f'Mean Squared Error: {mse}')


plt.figure(figsize=(15, 5))
plt.title('Celltrion (close) - Linear Regression Prediction')
plt.xticks(rotation=45)
plt.plot(df['날짜'], df['종가'], 'co-', label='Actual')
plt.plot(X_test, y_pred, 'ro-', label='Predicted')
plt.legend()
plt.grid(color='gray', linestyle='--')
plt.show()