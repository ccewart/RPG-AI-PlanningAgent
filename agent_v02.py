#!/usr/bin/python3
# ^^ note the python directive on the first line
# COMP 9414 agent initiation file 
# requires the host is running before the agent
# designed for python 3.6
# typical initiation would be (file in working directory, port = 31415)
#        python3 agent.py -p 31415

from agent_classes import Coords, Compass, Character
from queue import Queue
from greedyBFS import *
import sys
import socket



# declaring visible grid to agent
view = [['' for _ in range(5)] for _ in range(5)]

# declaring a known map of the world to agent
worldMap = [['?' for _ in range(160)] for _ in range(160)]

# declaring navigation tools
currentX = 80
currentY = 80
cardinalPoints = ['N', 'E', 'S', 'W']
orientation = 0
stepsTaken = 0
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

# declaring inventory
hasTreasure = False
hasAxe = False
hasKey = False
hasRaft = False
nbOfSteppingStones = 0

def initialiseWorldMap(view):
    if stepsTaken==0:
        for i in range(5):
            for j in range(5):
                if(i==2 and j==2):
                    worldMap[80][80] = 'S'
                else:
                    worldMap[78+i][78+j] = view[i][j]

def updateWorldMap(view):
    if cardinalPoints[orientation] == 'N':
        for i in range(5):
            worldMap[currentY-2][currentX-2+i] = view[0][i]
    elif cardinalPoints[orientation] == 'E':
        for i in range(5):
            worldMap[currentY-2+i][currentX+2] = view[0][i]
    elif cardinalPoints[orientation] == 'S':
        for i in range(5):
            worldMap[currentY+2][currentX+2-i] = view[0][i]
    elif cardinalPoints[orientation] == 'W':
        for i in range(5):
            worldMap[currentY+2-i][currentX - 2] = view[0][i]

def printWorldMap():
    for i in range(72, 88):
        for q in range(72, 100):
            print(worldMap[i][q][0], end = '')
        print()

def moveForward():
    global currentY
    global currentX
    global stepsTaken
    if cardinalPoints[orientation] == 'N':
        currentY = currentY-1
    elif cardinalPoints[orientation] == 'E':
        currentX = currentX+1
    elif cardinalPoints[orientation] == 'S':
        currentY = currentY+1
    elif cardinalPoints[orientation] == 'W':
        currentX = currentX-1
    stepsTaken += 1

def rotate(direction):
    global orientation
    global stepsTaken
    if direction == 'l':
        orientation = (orientation - 1) % 4
    elif direction == 'r':
        orientation = (orientation + 1) % 4
    stepsTaken += 1

def adjacentSquaresHeuristic():
    cardinals = [['N', 0],['E', 0], ['S', 0], ['W', 0]]
    for i in range(4):
        for j in range(-2, 3):
            if i == 0 and worldMap[currentY-3][currentX+j] == '?':
                cardinals[0][1] += 1
            if i == 1 and worldMap[currentY+j][currentX+3] == '?':
                cardinals[1][1] += 1
            if i == 2 and worldMap[currentY+3][currentX+j] == '?':
                cardinals[2][1] += 1
            if i == 3 and worldMap[currentY+j][currentX-3] == '?':
                cardinals[3][1] += 1   
    L = [1,2,3,2]
    if cardinalPoints[orientation] == 'N':
        for i in range(4):
            if view[L[i]][L[::-1][i]] in ['~', 'T', '*', '-', '.']:
                cardinals[i][1] -= 5
    if cardinalPoints[orientation] == 'E':
        for i in range(4):
            if view[L[i]][L[::-1][i]] in ['~', 'T', '*', '-', '.']:
                cardinals[(i+1)%4][1] -= 5
    if cardinalPoints[orientation] == 'S':
        for i in range(4):
            if view[L[i]][L[::-1][i]] in ['~', 'T', '*', '-', '.']:
                cardinals[(i+2)%4][1] -= 5
    if cardinalPoints[orientation] == 'W':
        for i in range(4):
            if view[L[i]][L[::-1][i]] in ['~', 'T', '*', '-', '.']:
                cardinals[(i+3)%4][1] -= 5
    return cardinals      

def pathToActions(path):
    for e in path:
        if e[0] == 2 and e[1] ==             2:
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
    localY, localX = currentY, currentX
    localOrientation = cardinalPoints[orientation]
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
            if cardinalPoints[orientation] == 'N':
                if view[i][j] == item:
                    itemLocations.append((currentY-2+i, currentX-2+j))
            elif cardinalPoints[orientation] == 'E':
                if view[i][j] == item:
                    itemLocations.append((currentY-2+j, currentX+2-i))
            elif cardinalPoints[orientation] == 'S':
                if view[i][j] == item:
                    itemLocations.append((currentY+2-i, currentX+2-j))
            elif cardinalPoints[orientation] == 'W':
                if view[i][j] == item:
                    itemLocations.append((currentY+2-j, currentX-2+i))
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
    global hasTreasure
    global hasKey
    global hasAxe
    if ((y, x)) in thingCoords['$']:
        hasTreasure = True
        thingCoords['$'] = []
    if ((y, x)) in thingCoords['a']:
        hasAxe = True
        thingCoords['a'].remove((y, x))
    if ((y, x)) in thingCoords['k']:
        hasKey = True
        thingCoords['k'].remove((y, x))
    if ((y, x)) in thingCoords['o']:
        nbOfSteppingStones += 1
        thingCoords['o'].remove((y, x))

def which_action():
    act = actionQueue.dequeue()
    if act == 'f':
        moveForward()
    if act == 'l':
        rotate('l')
    if act == 'r':
        rotate('r')  
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
    if (cardinalPoints[orientation] in maxHSquares) and (view[1][2] not in ['~', '*', '.']):
        moveForward()
        return 'f'
    else:
        if  (((cardinalPoints[orientation] == 'N') and ('E' in maxHSquares) and ('W' not in maxHSquares)) or
            ((cardinalPoints[orientation] == 'E') and ('S' in maxHSquares) and ('N' not in maxHSquares)) or
            ((cardinalPoints[orientation] == 'S') and ('W' in maxHSquares) and ('E' not in maxHSquares)) or
            ((cardinalPoints[orientation] == 'W') and ('N' in maxHSquares) and ('S' not in maxHSquares))
            ):
                rotate('r')
                return 'r'
        elif(((cardinalPoints[orientation] == 'N') and ('W' in maxHSquares) and ('E' not in maxHSquares)) or
            ((cardinalPoints[orientation] == 'E') and ('N' in maxHSquares) and ('S' not in maxHSquares)) or
            ((cardinalPoints[orientation] == 'S') and ('E' in maxHSquares) and ('W' not in maxHSquares)) or
            ((cardinalPoints[orientation] == 'W') and ('S' in maxHSquares) and ('N' not in maxHSquares))
            ):
                rotate('l')
                return 'l'
    return None

def chopTree():
    for i in range(4):
        actionQueue.enqueue('c')
        actionQueue.enqueue('r')
        rotate('r')

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
    global hasTreasure
    global hasRaft
    global stepsTaken
    global onLand
    global waterTiles
    global exploredWaterTiles
    if stepsTaken > 500:
        sys.exit(1)
    if worldMap[currentY][currentX] == '~' and (currentY, currentX) not in exploredWaterTiles:
        exploredWaterTiles.append((currentY, currentX))
    if view[1][2] == '$':                           # if treasure right in front of us, cancel previous plans
        while actionQueue.isEmpty() == False:
            actionQueue.dequeue()
        hasTreasure = True
        thingCoords['T'] = []
        moveForward()
        return 'f'
    checkForThings(view)
    pickUpStuff(currentY, currentX)
    if actionQueue.isEmpty() == False:              # if stack has something in it
        act = which_action()
        return act
    for e in thingCoords:                           # can we get to treasure, axe, key or stones
        if e in ['$', 'a', 'k', 'o'] and onLand == True:
            if thingCoords[e]:
                path = greedySearch((currentY, currentX), worldMap,(thingCoords[e][0][0], thingCoords[e][0][1]))
                if len(path) > 1:
                    pathToActions_worldMap(path)     
    if actionQueue.isEmpty() == False:              # if stack has something in it
        act = which_action()
        return act
    if hasTreasure == True:                         # have treasure, and there's a path back
        pathBack = greedySearch((currentY, currentX), worldMap,(80, 80))
        if len(pathBack) > 1:
            pathToActions_worldMap(pathBack)
            act = which_action()
            return act
    if onLand == True:
        a = adjacentSquaresHeuristic()                  # go to square near unexplored areas
        nonAdjacentUnexploredTilePath = nonAdjacentTileToExplore(a, currentY, currentX)
        if nonAdjacentUnexploredTilePath:
            if len(nonAdjacentUnexploredTilePath) > 1:
                pathToActions_worldMap(nonAdjacentUnexploredTilePath)
                act = which_action()
                return act
        act = AdjacentTileToExplore(a)                  # go to adjacent square near most unexplored areas
        if act:
            return act
        if hasAxe == True and hasRaft == False and thingCoords['T']:         # if we can chop down a tree, do that
            for e in thingCoords['T']:
                path = greedySearch((currentY, currentX), worldMap,(thingCoords['T'][0][0], thingCoords['T'][0][1]))
                if len(path) > 1:
                    thingCoords['T'].remove(path[-1])
                    pathToActions_worldMap(path)
                    chopTree()
                    hasRaft = True
                    act = which_action()
                    return act
    if hasRaft == True and onLand == True:                         # go explore water   
        waterTiles = [(i,j) for j in range(160) for i in range(160) if worldMap[i][j] == '~']
        if waterTiles:
            for e in waterTiles:
                path = greedySearch((currentY, currentX), worldMap,(waterTiles[0][0], waterTiles[0][1]), ['*', 'T', '?', '-', '.'])
                if len(path) > 1:
                    waterTiles.pop(0)
                    pathToActions_worldMap(path)
                    onLand = False
                    hasRaft = False
                    act = which_action()
                    return act
    if onLand == False:
        waterPath = waterTileToExplore()
        if waterPath:
            Coords = localToWorldCoords(view[i][j])
            if view[i][j] == '~' and (Coords[0] not in waterTiles):
                waterTiles.append(Coords[0])
        if waterTiles:
            waterTilesPath = greedySearch((currentY, currentX), worldMap,(waterTiles[0][0], waterTiles[0][1]), [' ', '*', 'T', '?', '-', '.'])
            if len(waterTilesPath) > 1:
                waterTiles.pop(0)
                pathToActions_worldMap(waterTilesPath)
                act = which_action()
                return act
    rotate('l')
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
            initialiseWorldMap(view)
            updateWorldMap(view)
            printWorldMap()
            print_grid(view) # COMMENT THIS OUT ON SUBMISSION
            action = get_action(view) # gets new actions
            sock.send(action.encode('utf-8'))
    sock.close()

