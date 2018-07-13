#!/usr/bin/python3
# Charles Ewart
# Agent initiation file 
# requires the host is running before the agent
# designed for python 3.6
# typical initiation would be (file in working directory, port = 31415)
#        python3 agent.py -p 31415
# created by Leo Hoare
# with slight modifications by Alan Blair

from agent_classes import Coords, Compass, Character
from environment import *
from queue import Queue
from greedyBFS import *
import sys
import socket

# Initialise character at position (80,80)
Char = Character(80, 80)

# declaring visible grid to agent
view = [['' for _ in range(5)] for _ in range(5)]

# declaring a known map of the world to agent
worldMap = [['?' for _ in range(160)] for _ in range(160)]

# declaring navigation tools
waterTiles = []
exploredWaterTiles = []
thingCoords = {
                '$': [],
                'k': [],
                'a': [],
                'o': [],
                'T': [],
                '-': []
                }
avoid = ['*', 'T', '~', '?', '-', '.']
onLand = True

# declaring action tools
actionQueue = Queue()

def rotate_view(view):
    if Char.get_orientation == 'N':
        return view
    elif Char.get_orientation == 'E':
        view = [list(reversed(x)) for x in zip(*view)]
    elif Char.get_orientation == 'S':
        for _ in range(2):
            view = [list(reversed(x)) for x in zip(*view)]
    elif Char.get_orientation == 'W':
        for _ in range(3):
            view = [list(reversed(x)) for x in zip(*view)]
    return view

def updateWorldMap(view):
    view = rotate_view(view)
    for i in range(5):
        for j in range(5):
            worldMap[Char.Y_pos + 2 - i][Char.X_pos - 2 + j] = view[i][j]

def printWorldMap():
    for row in range(100, 75, -1):
        for column in range(72, 86):
            print(worldMap[row][column][0], end = '')
        print()

def adjacentSquaresHeuristic():
    cardinals = [['N', 0],['E', 0], ['S', 0], ['W', 0]]
    for i in range(4):
        for j in range(-2, 3):
            if i == 0 and worldMap[Char.Y_pos-3][Char.X_pos+j] == '?':
                cardinals[0][1] += 1
            if i == 1 and worldMap[Char.Y_pos+j][Char.X_pos+3] == '?':
                cardinals[1][1] += 1
            if i == 2 and worldMap[Char.Y_pos+3][Char.X_pos+j] == '?':
                cardinals[2][1] += 1
            if i == 3 and worldMap[Char.Y_pos+j][Char.X_pos-3] == '?':
                cardinals[3][1] += 1   
    L = [1,2,3,2]
    if Char.get_orientation == 'N':
        for i in range(4):
            if view[L[i]][L[::-1][i]] in ['~', 'T', '*', '-', '.']:
                cardinals[i][1] -= 5
    if Char.get_orientation == 'E':
        for i in range(4):
            if view[L[i]][L[::-1][i]] in ['~', 'T', '*', '-', '.']:
                cardinals[(i+1)%4][1] -= 5
    if Char.get_orientation == 'S':
        for i in range(4):
            if view[L[i]][L[::-1][i]] in ['~', 'T', '*', '-', '.']:
                cardinals[(i+2)%4][1] -= 5
    if Char.get_orientation == 'W':
        for i in range(4):
            if view[L[i]][L[::-1][i]] in ['~', 'T', '*', '-', '.']:
                cardinals[(i+3)%4][1] -= 5
    return cardinals      

def pathToActions(path):
    for e in path:
        if e[0] == 2 and e[1] == 2:
            pass
        elif e[1] < 2:
            actionQueue.enqueue('l')
            actionQueue.enqueue('f')
        elif e[0] < 2:
            actionQueue.enqueue('f')
        elif e[1] > 2:
            actionQueue.enqueue('r')
            actionQueue.enqueue('f')

def pathToActions_worldMap(path):
    localY, localX = Char.Y_pos, Char.X_pos
    localOrientation = Char.get_orientation
    for tile in path:
        if tile[0] == localX and tile[1] == localY:
            pass
        elif tile[0] < localY:
            if localOrientation == 'N':
                actionQueue.enqueue('f')
            elif localOrientation == 'E':
                actionQueue.enqueue('l')
                actionQueue.enqueue('f')
            elif localOrientation == 'S':
                actionQueue.enqueue('r')
                actionQueue.enqueue('r')
                actionQueue.enqueue('f')
            elif localOrientation == 'W':
                actionQueue.enqueue('r')
                actionQueue.enqueue('f')
            localY -= 1
            localOrientation = 'N'
        elif tile[1] > localX:
            if localOrientation == 'N':
                actionQueue.enqueue('r')
                actionQueue.enqueue('f')
            elif localOrientation == 'E':
                actionQueue.enqueue('f')
            elif localOrientation == 'S':
                actionQueue.enqueue('l')
                actionQueue.enqueue('f')
            elif localOrientation == 'W':
                actionQueue.enqueue('r')
                actionQueue.enqueue('r')
                actionQueue.enqueue('f')
            localX += 1
            localOrientation = 'E'
        elif tile[0] > localY:
            if localOrientation == 'N':
                actionQueue.enqueue('r')
                actionQueue.enqueue('r')
                actionQueue.enqueue('f')
            elif localOrientation == 'E':
                actionQueue.enqueue('r')
                actionQueue.enqueue('f')
            elif localOrientation == 'S':
                actionQueue.enqueue('f')
            elif localOrientation == 'W':
                actionQueue.enqueue('l')
                actionQueue.enqueue('f')
            localY += 1
            localOrientation = 'S'
        elif tile[1] < localX:
            if localOrientation == 'N':
                actionQueue.enqueue('l')
                actionQueue.enqueue('f')
            elif localOrientation == 'E':
                actionQueue.enqueue('l')
                actionQueue.enqueue('l')
                actionQueue.enqueue('f')
            elif localOrientation == 'S':
                actionQueue.enqueue('r')
                actionQueue.enqueue('f')
            elif localOrientation == 'W':
                actionQueue.enqueue('f')
            localX -= 1
            localOrientation = 'W'      

def localToWorldCoords(item):
    itemLocations = []
    for i in range(5):
        for j in range(5):
            if Char.get_orientation == 'N':
                if view[i][j] == item:
                    itemLocations.append((Char.Y_pos-2+i, Char.X_pos-2+j))
            elif Char.get_orientation == 'E':
                if view[i][j] == item:
                    itemLocations.append((Char.Y_pos-2+j, Char.X_pos+2-i))
            elif Char.get_orientation == 'S':
                if view[i][j] == item:
                    itemLocations.append((Char.Y_pos+2-i, Char.X_pos+2-j))
            elif Char.get_orientation == 'W':
                if view[i][j] == item:
                    itemLocations.append((Char.Y_pos+2-j, Char.X_pos-2+i))
    if itemLocations:
        return itemLocations
    else:
        return None

def checkForThings(view):
    for i in range(5):                           
        for j in range(5):
            if view[i][j] in ['$', 'k', 'a', 'o', '-']:
                Coords = localToWorldCoords(view[i][j])
                if Coords[0] not in thingCoords[view[i][j]]:
                    thingCoords[view[i][j]].append(Coords[0])
            elif view[i][j] == 'T':
                Coords = localToWorldCoords('T')
                if (Coords[0][0]-1,Coords[0][1]) not in thingCoords[view[i][j]]:
                    thingCoords['T'].append((Coords[0][0]-1,Coords[0][1]))
                if (Coords[0][0]+1,Coords[0][1]) not in thingCoords[view[i][j]]:
                    thingCoords['T'].append((Coords[0][0],Coords[0][1]+1))
                if (Coords[0][0]+1,Coords[0][1]) not in thingCoords[view[i][j]]:
                    thingCoords['T'].append((Coords[0][0]+1,Coords[0][1]))
                if (Coords[0][0],Coords[0][1]-1) not in thingCoords[view[i][j]]:
                    thingCoords['T'].append((Coords[0][0],Coords[0][1]-1))
    return None

def pickUpStuff(y, x):
    if ((y, x)) in thingCoords['$']:
        Char.hasTreasure = True
        thingCoords['$'] = []
    if ((y, x)) in thingCoords['a']:
        Char.hasAxe = True
        thingCoords['a'].remove((y, x))
    if ((y, x)) in thingCoords['k']:
        Char.hasKey = True
        thingCoords['k'].remove((y, x))
    if ((y, x)) in thingCoords['o']:
        Char.nbOfSteppingStones += 1
        thingCoords['o'].remove((y, x))

def which_action():
    act = actionQueue.dequeue()
    if act == 'f':
        Char.move_forward()
    if act == 'l':
        Char.rotate('l')
    if act == 'r':
        Char.rotate('r') 
    return act

def nonAdjacentTileToExplore(a, y, x):
    if all([a[0][1]<=0, a[1][1]<=0, a[2][1]<=0, a[3][1]<=0]):
        potentialPlaces = []
        for i in range(160):
            for j in range(160):
                if worldMap[i][j] not in ['~', 'T', '*', '?', '.', '-'] and \
                    (worldMap[i-1][j] == '?' or \
                    worldMap[i+1][j] == '?' or \
                    worldMap[i][j-1] == '?' or \
                    worldMap[i-1][j+1] == '?'):
                    potentialPlaces.append((i,j))
        if potentialPlaces:
            for i in range(len(potentialPlaces)):
                path = greedySearch((y, x), worldMap,(potentialPlaces[0][0], potentialPlaces[0][1]))
                if len(path) > 1:
                    return path
                else:
                    potentialPlaces.pop(0)
    return None

def AdjacentTileToExplore(a):
    maxHSquares = []
    for i in range(4):
        if a[i][1] == max(a[0][1], a[1][1], a[2][1], a[3][1]):
            maxHSquares.append(a[i][0])
    if (Char.get_orientation in maxHSquares) and (view[1][2] not in ['~', '*', '.']):
        Char.move_forward()
        return 'f'
    else:
        if  (((Char.get_orientation == 'N') and ('E' in maxHSquares) and ('W' not in maxHSquares)) or
            ((Char.get_orientation == 'E') and ('S' in maxHSquares) and ('N' not in maxHSquares)) or
            ((Char.get_orientation == 'S') and ('W' in maxHSquares) and ('E' not in maxHSquares)) or
            ((Char.get_orientation == 'W') and ('N' in maxHSquares) and ('S' not in maxHSquares))
            ):
                Char.rotate('r')
                return 'r'
        elif(((Char.get_orientation == 'N') and ('W' in maxHSquares) and ('E' not in maxHSquares)) or
            ((Char.get_orientation == 'E') and ('N' in maxHSquares) and ('S' not in maxHSquares)) or
            ((Char.get_orientation == 'S') and ('E' in maxHSquares) and ('W' not in maxHSquares)) or
            ((Char.get_orientation == 'W') and ('S' in maxHSquares) and ('N' not in maxHSquares))
            ):
                Char.rotate('l')
                return 'l'
    return None

def chopTree():
    for i in range(4):
        actionQueue.enqueue('c')
        actionQueue.enqueue('r')
        Char.rotate('r')

def waterTilesToExplore(y, x):
    potentialPlaces = []
    for i in range(160):
        for j in range(160):
            if worldMap[i][j] not in [' ', 'T', '*', '?', '.', '-'] and \
                (worldMap[i-1][j] == '?' or \
                worldMap[i+1][j] == '?' or \
                worldMap[i][j-1] == '?' or \
                worldMap[i-1][j+1] == '?'):
                potentialPlaces.append((i,j))
    if potentialPlaces:
        for i in range(len(potentialPlaces)):
            path = greedySearch((y, x), worldMap,(potentialPlaces[0][0], potentialPlaces[0][1]))
            if len(path) > 1:
                return path
            else:
                potentialPlaces.pop(0)
    return None

def nonAdjacentWaterTileToExplore(a, y, x):
    potentialPlaces = []
    for i in range(160):
        for j in range(160):
            if worldMap[i][j] not in [' ', 'T', '*', '?', '.', '-'] and \
                (worldMap[i-1][j] == '?' or \
                worldMap[i+1][j] == '?' or \
                worldMap[i][j-1] == '?' or \
                worldMap[i-1][j+1] == '?'):
                potentialPlaces.append((i,j))
    if potentialPlaces:
        for i in range(len(potentialPlaces)):
            path = greedySearch((y, x), worldMap,(potentialPlaces[0][0], potentialPlaces[0][1]))
            if len(path) > 1:
                return path
            else:
                potentialPlaces.pop(0)
    return None

# function to take get action from AI or user
def get_action(view):
    global onLand
    global waterTiles
    global exploredWaterTiles
    if Char.steps_taken > 50:
        sys.exit(1)
    print(Char.get_orientation)
    if worldMap[Char.Y_pos][Char.X_pos] == '~' and (Char.Y_pos, Char.X_pos) not in exploredWaterTiles:
        exploredWaterTiles.append((Char.Y_pos, Char.X_pos))
    if view[1][2] == '$':                           # if treasure right in front of us, cancel previous plans
        while actionQueue.isEmpty() == False:
            actionQueue.dequeue()
        Char.Char.hasTreasure = True
        thingCoords['T'] = []
        Char.move_forward()
        return 'f'
    checkForThings(view)
    pickUpStuff(Char.Y_pos, Char.X_pos)
    if actionQueue.isEmpty() == False:              # if stack has something in it
        act = which_action()
        return act
    for e in thingCoords:                           # can we get to treasure, axe, key or stones
        if e in ['$', 'a', 'k', 'o'] and onLand == True:
            if thingCoords[e]:
                path = greedySearch((Char.Y_pos, Char.X_pos), worldMap,(thingCoords[e][0][0], thingCoords[e][0][1]))
                if len(path) > 1:
                    pathToActions_worldMap(path)     
    if actionQueue.isEmpty() == False:              # if stack has something in it
        act = which_action()
        return act
    if Char.hasTreasure == True:                         # have treasure, and there's a path back
        pathBack = greedySearch((Char.Y_pos, Char.X_pos), worldMap,(80, 80))
        if len(pathBack) > 1:
            pathToActions_worldMap(pathBack)
            act = which_action()
            return act
    if onLand == True:
        a = adjacentSquaresHeuristic()                  # go to square near unexplored areas
        nonAdjacentUnexploredTilePath = nonAdjacentTileToExplore(a, Char.Y_pos, Char.X_pos)
        if nonAdjacentUnexploredTilePath:
            if len(nonAdjacentUnexploredTilePath) > 1:
                pathToActions_worldMap(nonAdjacentUnexploredTilePath)
                act = which_action()
                return act
        act = AdjacentTileToExplore(a)                  # go to adjacent square near most unexplored areas
        if act:
            return act
        if Char.hasAxe == True and Char.hasRaft == False and thingCoords['T']:         # if we can chop down a tree, do that
            for e in thingCoords['T']:
                path = greedySearch((Char.Y_pos, Char.X_pos), worldMap,(thingCoords['T'][0][0], thingCoords['T'][0][1]))
                if len(path) > 1:
                    thingCoords['T'].remove(path[-1])
                    pathToActions_worldMap(path)
                    chopTree()
                    Char.hasRaft = True
                    act = which_action()
                    return act
    if Char.hasRaft == True and onLand == True:                         # go explore water   
        waterTiles = [(i,j) for j in range(160) for i in range(160) if worldMap[i][j] == '~']
        if waterTiles:
            for e in waterTiles:
                path = greedySearch((Char.Y_pos, Char.X_pos), worldMap,(waterTiles[0][0], waterTiles[0][1]), ['*', 'T', '?', '-', '.'])
                if len(path) > 1:
                    waterTiles.pop(0)
                    pathToActions_worldMap(path)
                    onLand = False
                    Char.hasRaft = False
                    act = which_action()
                    return act
    if onLand == False:
        waterPath = waterTileToExplore()
        if waterPath:
            Coords = localToWorldCoords(view[i][j])
            if view[i][j] == '~' and (Coords[0] not in waterTiles):
                waterTiles.append(Coords[0])
        if waterTiles:
            waterTilesPath = greedySearch((Char.Y_pos, Char.X_pos), worldMap,(waterTiles[0][0], waterTiles[0][1]), [' ', '*', 'T', '?', '-', '.'])
            if len(waterTilesPath) > 1:
                waterTiles.pop(0)
                pathToActions_worldMap(waterTilesPath)
                act = which_action()
                return act
    Char.rotate('l')
    return 'l' 

# helper function to print the grid
def print_grid(view):
    print('+-----+')
    for ln in view:
        print('|'+str(ln[0])+str(ln[1])+str(ln[2])+str(ln[3])+str(ln[4])+'|')
    print('+-----+')

if __name__ == '__main__':

    # checks for correct amount of arguments 
    if len(sys.argv) != 3:
        print('Usage Python3 '+sys.argv[0]+' -p port \n')
        sys.exit(1)

    port = int(sys.argv[2])

    # checking for valid port number
    if not 1025 <= port <= 65535:
        print('Incorrect port number')
        sys.exit()

    # creates TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
         # tries to connect to host
         # requires host is running before agent
         sock.connect(('localhost',port))
    except (ConnectionRefusedError):
         print('Connection refused, check host is running')
         sys.exit()

    # navigates through grid with input stream of data
    i=0
    j=0
    while 1:
        data=sock.recv(100)
        if not data:
            exit()
        for ch in data:
            if (i==2 and j==2):
                view[i][j] = '^'
                view[i][j+1] = chr(ch)
                j+=1 
            else:
                view[i][j] = chr(ch)
            j+=1
            if j>4:
                j=0
                i=(i+1)%5
        if j==0 and i==0:
            #initialiseWorldMap(view)
            worldMap[80][80] = 'S'
            updateWorldMap(view)
            printWorldMap()
            print_grid(view) # COMMENT THIS OUT ON SUBMISSION
            action = get_action(view) # gets new actions
            sock.send(action.encode('utf-8'))
    sock.close()

