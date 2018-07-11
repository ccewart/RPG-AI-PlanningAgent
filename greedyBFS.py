class Queue:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0,item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)

class Node:
    def __init__(self, data):
        self.data = data

    def coords(self):
        return self.data

def heuristicKey(item):
    return item[1]

def manhattanDistance(node, goal):
    A = node.coords()
    B = goal.coords()
    return ((abs(A[1] - B[1])) + (abs(A[0] - B[0])))

def greedySearch(worldCoords, view, goal, obstacles = ['*', 'T', '~', '?', '-', '.']):
    priorityQueue = Queue()
    visited = {}
    finalPath = []
    if len(view) == 5:
        start = Node((2, 2))
    else:
        start = Node((worldCoords[0],worldCoords[1]))
    a, b = goal[0], goal[1]
    goal = Node((a, b))
    priorityQueue.enqueue(start)
    goalFound = 0
    greedySearchRec(start, goal, priorityQueue, visited, finalPath, goalFound, view, obstacles)
    return finalPath
 
def greedySearchRec(node, goal, pq, visited, finalPath, goalFound, view, obstacles):
    if goalFound == 1:
        return 1
    currentNode = pq.dequeue()
    finalPath.append(currentNode.coords())
    heuristic = manhattanDistance(currentNode, goal)
    children = [[None, 0], [None, 0], [None, 0], [None, 0]]
    if heuristic == 0:
        return 1
    else:
        currentCoords = currentNode.coords()
        visited[currentCoords] = True
        for i in range(4):
            if currentCoords[0] != 0:
                children[0][0] = Node((currentCoords[0] - 1, currentCoords[1]))
                children[0][1] = manhattanDistance(children[0][0], goal)
            if currentCoords[1] != 4:
                children[1][0] = Node((currentCoords[0], currentCoords[1] + 1))
                children[1][1] = manhattanDistance(children[1][0], goal)
            if currentCoords[0] != 4:
                children[2][0] = Node((currentCoords[0] + 1, currentCoords[1]))
                children[2][1] = manhattanDistance(children[2][0], goal)
            if currentCoords[1] != 0:
                children[3][0] = Node((currentCoords[0], currentCoords[1] - 1))
                children[3][1] = manhattanDistance(children[3][0], goal)
    children.sort(key = heuristicKey)
    for i in range(4):
        if children[i][0] and goal != 1:
            if children[i][0].coords() not in visited:
                a, b = children[i][0].coords()
                if view[a][b] not in obstacles:
                    pq.enqueue(children[i][0])
                    goalFound = greedySearchRec(children[i][0], goal, pq, visited, finalPath, goalFound, view, obstacles)
                    if goalFound != 1:
                        finalPath.remove(children[i][0].coords())
    return goalFound


