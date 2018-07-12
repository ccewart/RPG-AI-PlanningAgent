#NorthMapping = [(y, x) for x in range(-2, 3, 1) for y in range(2, -3, -1)]
#print(NorthMapping)
#EastMapping = [(y, x) for x in range(2, -3, -1) for y in range(2, -3, -1)]
#print(EastMapping)
#SouthMapping = [(y, x) for x in range(-2, 3, 1) for y in range(2, -3, -1)]
#print(SouthMapping)
#WestMapping = [(y, x) for x in range(2, -3, -1) for y in range(2, -3, -1)]
#print(WestMapping)
view = [['~' for i in range(5)] for j in range(5)]
for i in range(1, 5):
    for j in range(5):
        view[i][j] = ' '

for e in view:
    print(e)

direction = 'W'

def rotate_view(view):
    if direction == 'N':
        return view
    elif direction == 'E':
        view = [list(reversed(x)) for x in zip(*view)]
    elif direction == 'S':
        for _ in range(2):
            view = [list(reversed(x)) for x in zip(*view)]
    elif direction == 'W':
        for _ in range(3):
            view = [list(reversed(x)) for x in zip(*view)]
    return view

view = rotate_view(view)

print()
for e in view:
    print(e)

