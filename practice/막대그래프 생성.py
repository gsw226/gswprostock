import pandas as pd
from pandas import Series
import matplotlib.pyplot as plt

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'

# 데이터와 인덱스 생성
myindex = ['ㄱㄱㅊ', 'ㅎㄱㄷ', 'ㅇㅅㅅ', 'ㅊㅇ']
members = Series(data=[20, 60, 81, 40], index=myindex)

# Series 출력
print(members)

# values 속성을 이용하여 요소들의 값을 확인할 수 있다
print('# values 속성을 이용하여 요소들의 값을 확인할 수 있다')
print(members.values)

# index 속성을 이용하여 색인 객체를 구별할 수 있다
print('# index 속성을 이용하여 색인 객체를 구별할 수 있다')
print(members.index)

# 막대 그래프 생성
members.plot(kind='bar', rot=0, ylim=[0, members.max()+20], use_index=True, grid=False, color=['r', 'g', 'b', 'y'])

# x, y 축 레이블 및 그래프 제목 설정
plt.xlabel('학생이름')
plt.ylabel('점수')
plt.title('학생별 시험 점수')

# 비율 계산 및 출력
ratio = 100 * members / members.sum()
print(ratio)
print('-'*40)

# 그래프에 값과 비율 표시
for idx in range(members.size):
    value = str(members[idx]) + '건'
    ratioval = '%.1f%%' % (ratio[idx])
    plt.text(x=idx, y=members[idx]+1, s=value, horizontalalignment='center')
    plt.text(x=idx, y=members[idx]/2+1, s=ratioval, horizontalalignment='center')

# 평균 값 계산 및 출력
meanval = members.mean()
print(meanval)

# 그래프에 평균선 및 텍스트 추가
average = '평균 : %d건' % meanval
plt.axhline(y=meanval, color='r', linewidth=1, linestyle='dashed')
plt.text(x=0, y=meanval+1, s=average, horizontalalignment='center')

# 그래프 저장 및 출력
filename = 'graph01.png'
plt.savefig(filename, dpi=400, bbox_inches='tight')
print(filename + " 파일이 저장되었습니다.")
plt.show()