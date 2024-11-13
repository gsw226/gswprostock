# ax + by = c
# dx + ey = f

a = int(input())
b = int(input())
c = int(input())
d = int(input())
e = int(input())
f = int(input())


for i in range(-1000,1000):
    for j in range(-1000,1000):
        for k in range(-1000,1000):
            for l in range(-1000,1000):
                if a*i == d*k or b*j==e*l:
                    