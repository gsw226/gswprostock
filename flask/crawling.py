import pandas as pd
from bs4 import BeautifulSoup
import requests

# 주식 이름에서 코드를 추출하는 함수
def stock_name_to_code(stock_str):
    if len(stock_str) < 6:
        return stock_str.zfill(6)
    else:
        return stock_str

# 네이버 금융에서 전날 종가를 가져오는 함수
def get_yesterday_close(tickers):
    close_prices = []
    headers = {"User-Agent": "Mozilla/5.0"}
    
    for ticker in tickers:
        if len(ticker) < 6:
            ticker = ticker.zfill(6)
        url = f"https://finance.naver.com/item/sise_day.nhn?code={ticker}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 모든 거래일의 데이터를 포함하는 <tr> 태그 찾기
        rows = soup.find_all('tr', {'onmouseover': True})
        
        if rows:
            # 가장 최근의 거래일(어제)의 데이터를 가져옴
            last_row = rows[0]
            cols = last_row.find_all('td')
            
            if len(cols) > 1:
                close_price_text = cols[1].text.strip().replace(',', '')
                
                # 종가 텍스트가 비어 있는지 확인
                if close_price_text:
                    try:
                        close_prices.append(float(close_price_text))  # 실수로 변환하여 추가
                    except ValueError:
                        close_prices.append(None)  # 변환 실패 시 None 추가
                else:
                    close_prices.append(None)
            else:
                close_prices.append(None)
        else:
            close_prices.append(None)
    
    return close_prices

# CSV 파일에서 데이터 읽기
csv_df = pd.read_csv('./stock.csv')

# 단축코드 열을 수정 (inplace=True로 설정)
csv_df['단축코드'] = csv_df['단축코드'].apply(stock_name_to_code)

# 종가 데이터 추출
result = get_yesterday_close(csv_df['단축코드'].tolist())

# 결과를 데이터프레임에 저장
csv_df['어제종가'] = result
print(csv_df['어제종가'])

# 수정된 데이터프레임을 CSV 파일로 저장
csv_df.to_csv('stock_data.csv', index=False, encoding='utf-8-sig')
