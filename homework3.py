from math import fabs

class Point:

    def __init__(self, x, y, z, movements):
        'Initializer for a point'

        self.coordinates = (x, y, z)
        self.movements = movements
        self.visited = False

    def goto(self, movement):
        'Function that returns the next set of coordinates and the cost after a movement takes place from the current point'

        x, y, z = self.coordinates
        cost = 10 if movement in range(1,7) else 14

        #X
        if movement in [1, 7, 8, 11, 12]:
            x = self.coordinates[0] + 1
        elif movement in [2, 9, 10, 13, 14]:
            x = self.coordinates[0] - 1

        #Y
        if movement in [3, 7, 9, 15, 16]:
            y = self.coordinates[1] + 1
        elif movement in [4, 8, 10, 17, 18]:
            y = self.coordinates[1] - 1

        #Z
        if movement in [5, 11, 13, 15, 17]:
            z = self.coordinates[2] + 1
        elif movement in [6, 12, 14, 16, 18]:
            z = self.coordinates[2] - 1

        return (x, y, z), cost

class Node:

    def __init__(self, point, path, totalCost, heuristicCost, stepCost):
        self.point = point
        self.path = path
        self.totalCost = totalCost
        self.heuristicCost = heuristicCost
        self.stepCost = stepCost
        self.next = None

class Frontier:

    def __init__(self, algo):

        self.front = None
        self.rear = None
        self.length = 0
        self.algo = algo

    def dequeue(self):

        f = self.front
        if f == self.rear:
            self.rear = None
        self.front = f.next
        self.length -= 1
        return f.point, f.path, f.totalCost, f.heuristicCost, f.stepCost

    def enqueue(self, point, path, totalCost, heuristicCost, stepCost):

        node = Node(point, path, totalCost, heuristicCost, stepCost)

        if self.length == 0:
            self.front = node
            self.rear = node

        elif self.algo == 'BFS':
            r = self.rear
            r.next = node
            self.rear = node

        else:
            flag = False
            check_node = self.front
            prev_node = None
            while check_node is not None:
                if (self.algo == 'A*' and check_node.heuristicCost > heuristicCost) or (self.algo == 'UCS' and check_node.totalCost > totalCost):
                    flag = True
                    break
                prev_node = check_node
                check_node = check_node.next

            if flag:
                if prev_node is None:
                    self.front = node
                else:
                    prev_node.next = node
                node.next = check_node
            else:
                r = self.rear
                r.next = node
                self.rear = node

        self.length += 1

class Tunnel:

    def parseInput(self, fname):
        'Function to parse the input file'

        f = open(fname)
        self.algo = f.readline().strip()
        self.max_x, self.max_y, self.max_z = [int(i) for i in f.readline().split()]
        self.init = tuple(int(i) for i in f.readline().split())
        self.goal = tuple(int(i) for i in f.readline().split())
        self.states = int(f.readline())
        self.points = {}

        for _ in range(self.states):
            temp = [int(i) for i in f.readline().strip().split()]
            p = Point(temp[0], temp[1], temp[2], temp[3:])
            self.points[p.coordinates] = p

    def valid(self, coordinates):
        'Function to check if a coordinate is valid point in the tunnel'
        
        x, y, z = coordinates
        if (x >= self.max_x or x < 0) or (y >= self.max_y or y < 0) or (z >= self.max_z or z < 0):
            return False
        return True

    def getNextPoint(self, current, movement):
        'Function to get the next point adjacent to the current one after performing a certain movement'

        new_coordinates, cost = current.goto(movement)
        if self.valid(new_coordinates):
            new_point = self.points[new_coordinates]
            return new_point, cost
        else:
            return None, cost

    def checkGoal(self, point):
        'Function to check whether the current point is the exit of the tunnel'

        if point.coordinates == self.goal:
            return True
        return False

    def heuristic(self, point):
        'Function that returns the heuristic value of a point'

        x, y, z = point.coordinates
        goal_x, goal_y, goal_z = self.goal
        difference = fabs(goal_x - x) + fabs(goal_y - y) + fabs(goal_z - z)
        return difference * 14
    
    def search(self):
        'Function to search for given ending point'

        frontier = Frontier(self.algo)
        frontier.enqueue(self.points[self.init], [], 0, 0, [0])
        found = False
        totalCost = 0

        while frontier.length != 0:
            point, path, totalCost, _, stepCost = frontier.dequeue()
            point.visited = True
            if self.checkGoal(point):
                found = True
                break

            for movement in point.movements:
                x, cost = self.getNextPoint(point, movement)
                if x is not None and x.visited is False:
                    frontier.enqueue(
                                        x, 
                                        path + [point.coordinates], 
                                        totalCost + 1 if self.algo == 'BFS' else totalCost + cost,
                                        totalCost + cost + self.heuristic(x) if self.algo == 'A*' else 0,
                                        stepCost + [1] if self.algo == 'BFS' else stepCost + [cost]
                                    )

        
        self.found = found
        if found:
            self.totalCost = totalCost
            self.path_length = len(path) + 1
            self.final_path = path + [point.coordinates]
            self.stepCost = stepCost

    def saveOutput(self, output):
        'Function to save results to output.txt'

        with open(output, 'w') as f:
            if not self.found:
                f.write('FAIL')
            else:
                f.write(str(self.totalCost) + '\n')
                f.write(str(self.path_length))

                for point in range(len(self.final_path)):
                    f.write('\n' + str(self.final_path[point][0]) + ' ' + str(self.final_path[point][1]) + ' ' + str(self.final_path[point][2]) + ' ' + str(self.stepCost[point]))

def main(input_file='input.txt', output_file='output.txt'):
    t = Tunnel()
    t.parseInput(input_file)
    t.search()
    t.saveOutput(output_file)

main()