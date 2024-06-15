import requests

headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'}
url = 'https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo?serviceKey=%2FUB%2BN6oc%2BLqwC%2FRfoNOJxaDVQeKk5CGHioiR%2BnmtE3J5sWI%2BEXRW5jeqsqsgds%2Bdcg6d2dN8i5ovHa%2B%2FStLC1g%3D%3D&numOfRows=100&pageNo=1&resultType=json'
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    print(data)