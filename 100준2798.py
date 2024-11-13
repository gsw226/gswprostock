n = int(input())
m = int(input())
cards = []

for i in range(n):
    num = int(input())
    cards.append(num)

for a in range(n):
    cards[a]

result = 0

for j in range(n):
    for l in range(j+1,n):
        for k in range(l+1,n):
            sum = cards[j]+cards[l]+cards[k]
            if result < sum and sum <= m:
                result = sum
print(result)