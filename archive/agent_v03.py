#!/usr/bin/python3
# Charles Ewart
# Agent initiation file 
# requires the host is running before the agent
# designed for python 3.6
# typical initiation would be (file in working directory, port = 31415)
#        python3 agent.py -p 31415
# socket code created by Leo Hoare
# with slight modifications by Alan Blair

from agent import Coords, Compass, Character
from environment import *
from queue import Queue
from greedyBFS import *
import sys
import socket

# declaring visible grid to agent
view = [['' for _ in range(5)] for _ in range(5)]

# declaring a known map of the world to agent
worldMap = [['?' for _ in range(160)] for _ in range(160)]

# Initialise character at position (80,80)
Char = Character(80, 80)
RPG_Env = RPG_Environment()

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
    Updated_view = rotate_view(view)
    for i in range(5):
        for j in range(5):
            worldMap[Char.Y_pos + 2 - i][Char.X_pos - 2 + j] = Updated_view[i][j]

def printWorldMap():
    for row in range(100, 75, -1):
        for column in range(72, 86):
            print(worldMap[row][column][0], end = '')
        print()

def which_action():
    act = actionQueue.dequeue()
    if act == 'f':
        Char.move_forward()
    if act == 'l':
        Char.rotate('l')
    if act == 'r':
        Char.rotate('r') 
    return act

# function to take get action from AI or user
def get_action(view):
    if Char.steps_taken > 50:
        sys.exit(1)
    if actionQueue.isEmpty() == False:              # if stack has something in it
        return which_action()
    if Char.hasTreasure == True:                         # have treasure, and there's a path back
        pathBack = greedySearch((Char.Y_pos, Char.X_pos), worldMap,(80, 80))
        if len(pathBack) > 1:   
            pathToActions_worldMap(pathBack)
            return which_action()

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
            worldMap[80][80] = 'S'
            updateWorldMap(view)
            printWorldMap()
            print_grid(view) # COMMENT THIS OUT ON SUBMISSION
            action = get_action(view) # gets new actions
            sock.send(action.encode('utf-8'))
    sock.close()

