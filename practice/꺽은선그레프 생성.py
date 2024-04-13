import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from pandas import Series
plt.rcParams['font.family'] = 'Malgun Gothic'

matplotlib.rcParams['axes.unicode_minus'] = False

mylist = [30,20,40,30,60,50]
myindex = ['ㄱㄱㅊ','ㄱㅇㅅ','ㅇㅅㅅ','ㅇㅇㅌ','ㅇㄷㅈ','ㅎㄱㄷ']


print(myindex)
print(mylist)

myseries = Series(data=mylist,index=myindex)
myylim=[0,myseries.max()+10]
myseries.plot(title='시험점수',kind='line',ylim=myylim,grid=True,rot=10,use_index=True)

filename = 'seriesGraph01.png'
plt.savefig(filename, dpi=400, bbox_inches = 'tight')
print(filename +'파일이 저장되었음니다.')
plt.show()