# demonstrating the use of itemgetter

from operator import itemgetter

data:list[int] = [1, 12,  23, 34, 45, 56, 67, 78, 89, 90] 

first_last:itemgetter = itemgetter(0, -1, 8)

print(first_last(data))

items:dict[str, int] = {"vol": 3, "pace": 23, "d": 10}

vol_n_pace:itemgetter = itemgetter('vol', 'pace')

print(vol_n_pace(items))