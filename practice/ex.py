import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf

# 데이터프레임 생성 예시
data = {
    '날짜': ['2022-01-01', '2022-01-02', '2022-01-03', '2022-01-04', '2022-01-05'],
    '시가': [100, 110, 105, 115, 120],
    '고가': [120, 130, 125, 135, 130],
    '저가': [90, 100, 95, 105, 110],
    '종가': [110, 120, 115, 125, 125]
}
df = pd.DataFrame(data)

# '날짜' 열을 datetime으로 변환
df['날짜'] = pd.to_datetime(df['날짜'])

# 캔들차트 그리기
mpf.plot(df, type='candle', style='charles', show_nontrading=True)

plt.show()
