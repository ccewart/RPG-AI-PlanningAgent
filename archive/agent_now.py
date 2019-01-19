#!/usr/bin/python3
# z3331148 Charles Ewart Assignment3 Question1
# The main pieces of the program are the World Map array, the Greedy Best First Search algorithm
# and a queue in which we store the next action.
# Every time the agent moves, the new explored tiles are stored in the World Map array.
# Then using, the new information, determines whether to set a path to a new subgoal, such
# as an item, or to continue exploring.
# At each square, there is a heuristic for which direction will yield the most amount of new
# information about the world, so we prioritise that direction. If they are all blocked or give
# us no new information we use Greedy Search to find a path to a tile that is adjacent to an 
# unexplored area. If we have the treasure, refresh the queue, and devise a plan to the start.
# I went with Greedy Best First Search over A* for the speed advantage. Having an optimal path and
# reducing the number of steps wasn't worth the speed tradeoff.
#
#


# ^^ note the python directive on the first line
# COMP 9414 agent initiation file 
# requires the host is running before the agent
# designed for python 3.6
# typical initiation would be (file in working directory, port = 31415)
#        python3 agent.py -p 31415
# created by Leo Hoare
# with slight modifications by Alan Blair

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
axeLocations = []
keyLocations = []
thingCoords = {
                '$': [],
                'k': [],
                'a': [],
                'o': [],
                'T': [],
                '-': []
                }
avoid = ['*', 'T', '~', '?', '-', '.']

# declaring action tools
actionQueue = Queue()

# declaring inventory
hasTreasure = False
hasAxe = False
hasKey = False
hasRaft = False
nbOfSteppingStones = 0

# for updating world map before any steps have been done
def initialiseWorldMap(view):
    if stepsTaken==0:
        for i in range(5):
            for j in range(5):
                if(i==2 and j==2):
                    worldMap[80][80] = 'S'
                else:
                    worldMap[78+i][78+j] = view[i][j]

# use the first row of view to update any new information about the world
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
    for i in range(73, 87):
        for q in range(73, 95):
            print(worldMap[i][q][0], end = '')
        print()

# update world space coordinates when we move forward
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

# update global direction when we move rotate
def rotate(direction):
    global orientation
    global stepsTaken
    if direction == 'l':
        orientation = (orientation - 1) % 4
    elif direction == 'r':
        orientation = (orientation + 1) % 4
    stepsTaken += 1

# returns which directions have the most '?' on their border.
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
            if view[L[i]][L[::-1][i]] in ['~', 'T', '*', '-']:
                cardinals[i][1] -= 5
    if cardinalPoints[orientation] == 'E':
        for i in range(4):
            if view[L[i]][L[::-1][i]] in ['~', 'T', '*', '-']:
                cardinals[(i+1)%4][1] -= 5
    if cardinalPoints[orientation] == 'S':
        for i in range(4):
            if view[L[i]][L[::-1][i]] in ['~', 'T', '*', '-']:
                cardinals[(i+2)%4][1] -= 5
    if cardinalPoints[orientation] == 'W':
        for i in range(4):
            if view[L[i]][L[::-1][i]] in ['~', 'T', '*', '-']:
                cardinals[(i+3)%4][1] -= 5
    return cardinals      

# translates a local space (input view) path to a sequence of actions which are then enqueued.
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

# translates a world space path to a sequence of actions which are then enqueued.
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

# translating what is seen in input 'view' to WorldMap coordinates.
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
                    itemLocations.append((currentY+2-i, currentX-2+j))
            elif cardinalPoints[orientation] == 'W':
                if view[i][j] == item:
                    itemLocations.append((currentY+2-j, currentX-2+i))
    if itemLocations:
        return itemLocations
    else:
        return None

# updating agents knowledge of coordinates of different items and features
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

# update globals if we are on top of an item
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

# searches through the World Map for a tile that is next to a '?', then uses
# Greedy Search to return a path.
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

# if one direction yields more new information, go that direction.
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

# function to take get action from AI or user
def get_action(view):
    global hasTreasure
    global stepsTaken
    if stepsTaken > 10000:
        sys.exit(1)
    if view[1][2] == '$':                           # if treasure right in front of us, cancel previous plans
        while actionQueue.isEmpty() == False:
            actionQueue.dequeue()
        hasTreasure = True
        moveForward()
        return 'f'
    checkForThings(view)                            # update knowledge of any items or features
    pickUpStuff(currentY, currentX)                 # update inventory if we are on top of an item
    if actionQueue.isEmpty() == False:              # if we already have an action in queue, return that action
        act = which_action()
        return act
    for e in thingCoords:                           # can we get to treasure, axe, key or stones
        if e in ['$', 'a', 'k', 'o']:
            if thingCoords[e]:
                path = greedySearch((currentY, currentX), worldMap,(thingCoords[e][0][0], thingCoords[e][0][1]))
                if len(path) > 1:
                    pathToActions_worldMap(path)     
    if actionQueue.isEmpty() == False:              # check queue again after finding path above
        act = which_action()
        return act
    if hasTreasure == True:                         # if agent has treasure, and there's a valid path back, enqueue path
        pathBack = greedySearch((currentY, currentX), worldMap,(80, 80))
        if len(pathBack) > 1:
            pathToActions_worldMap(pathBack)
            act = which_action()
            return act
    a = adjacentSquaresHeuristic()                  # if adjacent tiles don't provide new information explore unexplored areas
    nonAdjacentUnexploredTilePath = nonAdjacentTileToExplore(a, currentY, currentX)
    if nonAdjacentUnexploredTilePath:
        if len(nonAdjacentUnexploredTilePath) > 1:
            pathToActions_worldMap(nonAdjacentUnexploredTilePath)
            act = which_action()
            return act
    act = AdjacentTileToExplore(a)                  # go to adjacent square near most unexplored areas
    if act:
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
            #printWorldMap()
            print_grid(view) # COMMENT THIS OUT ON SUBMISSION
            action = get_action(view) # gets new actions
            sock.send(action.encode('utf-8'))

    sock.close()

