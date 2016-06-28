from random import randint

d = {}

for i in range(0, 5):
    print('i: {}'.format(i))
    d['{}'.format(randint(0,50))] = i
    if len(d) < 3:
        i -= 1

print(d)
