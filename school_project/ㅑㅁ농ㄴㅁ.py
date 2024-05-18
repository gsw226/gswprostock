def 함수이름(a):
    if a%2 == 0:
        return '짝수'
    elif a%2 == 1:
        return '홀수'
    
a = int(input())
result = 함수이름(a)
print(result)