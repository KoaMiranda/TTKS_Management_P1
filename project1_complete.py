import os
import fileinput as fi #unnecessary? loadtext?
import numpy as np
import matplotlib.pyplot as plt
import random as rand
import math #ceil function

def file_grabber(txt_file):
    # txt_file = input("Enter the name of file: ")
    locs = np.loadtxt(txt_file, dtype=np.double)
    return locs

def eucl_dist(inp: np.ndarray):
  ignore = 0
  rows = inp.shape[0]
  cols = inp.shape[1]
  gNNmatrix = np.zeros((rows,rows))

  for i in range(rows):
      temp = list(range(cols)) #for the x,y coords
      for j in range(rows):
          if j < ignore: continue #ex. when j == 3, should skip 0,1,2
          if i == j: continue #skip the diagonal

          for k in range(cols):
            temp[k] = inp[i,k] - inp[j,k] #ex. row 2, inp([2][0]) - inp([3+0][0])
          temp[0] = temp[0]**2 #x-coord
          temp[1] = temp[1]**2 #y-coord
          total = temp[0] + temp[1]
          ed = np.sqrt(total) #euclidean distance
          gNNmatrix[i][j] = ed # assign it to the global NxN matrix
      ignore += 1 #only top triangle of matrix
  return gNNmatrix

def get_distance(pair):
   return pair[1] # get the second value in the pair, should be distance

def eamonn_nn(originalPoints, euclideanPoints): # will be using original coordinates and distance matrix from euclidean function
   
   allPoints = len(originalPoints)
   unvisitedNodes = set(range(1,allPoints)) # load all the nodes besides the first one
   routeTaken = [0] # start at node 0

   while unvisitedNodes:
      currentNode = routeTaken[-1] # goes to the last added node, or current node
      distanceFromCurrent = [] # store distances from unvisited nodes to current here

      for i in unvisitedNodes:
         j = euclideanPoints[currentNode][i] # lookup distance from current node using the given euclidean matrix
         distanceFromCurrent.append((i,j)) # putting a point and relational distance in our array
         #print(distanceFromCurrent) i think it worked?
         #if len(distanceFromCurrent) < 5:
            #print("right after append: ", distanceFromCurrent[:3]) 
         # i need to sort the distanceFromCurrent list by distance
      distanceFromCurrent.sort(key=get_distance) # should put shortest distances first
      #if len(distanceFromCurrent) < 5:
        #print("right after sort: ", distanceFromCurrent[:5]) 
      neighborNodes = [pair[0] for pair in distanceFromCurrent] # first element in the pair is our index, just as we took the pair[1] in get_distance
    # neighborNodes>1 shows theres more than 1 node left
      if len(neighborNodes) > 1 and rand.random() < 0.1: # random generates something between 0.0 and 1.0, so this sets the 1/10th probability
         nextNode = neighborNodes[1] # choose longer distance 
      else:
         nextNode = neighborNodes[0] # will be shorter most of the time

      routeTaken.append(nextNode) # add to our route 
      unvisitedNodes.remove(nextNode) # remove it from our nodes to visit

   routeTaken.append(0) # creates a loop, goes back to the first point
   return routeTaken
         
   # this was for testing  
   # i think while loop was issue, need to remove nodes from array
      #removalNode = distanceFromCurrent[0][0]
      #unvisitedNodes.remove(removalNode) seems to be working

def route_distance(routeTaken, euclideanPoints, localMin): # will be calculating how much distance route took
   
   totalDistance = 0.0
   
   for i in range(len(routeTaken) - 1): # looping through pairs, we need to add distances up
      totalDistance += euclideanPoints[routeTaken[i]][routeTaken[i+1]] # node we are on as well as node we will go to
                                                                       # dont think this includes last node back to start, do it below
                                                                       # ^Fixed. appended the start node to the routeTaken so it creates a loop
      if totalDistance > localMin: 
         break
   totalDistance += euclideanPoints[routeTaken[-1]][routeTaken[0]]
   return totalDistance

# NNAnswer = eamonn_nn(arr, euclideanAnswer)
# print(NNAnswer)
# print(route_distance(NNAnswer, euclideanAnswer))

def route_visualization(arr, NNAnswer, fileName, distance): #added 
   points = arr[NNAnswer] # ordering the points to the best path
   x = points[:,0] # extracting the points from the columns
   y = points[:,1]

   xMin = x.min() - 10 # adding a 10 pixel buffer for each edge of the graph
   xMax = x.max() + 10
   yMin = y.min() - 10
   yMax = y.max() + 10
   xWidth = xMax - xMin # calculation for the height and width of the graph
   yHeight = yMax - yMin

   if xWidth < yHeight: # smaller of the x and y dimension is set to 1920
      width = 1920 / 100 # pixel conversion
      height = width * (yHeight / xWidth) # scaling the side no adjusted to 1920 pixels
   else:
      height = 1920 / 100
      width = height * (xWidth / yHeight)

   plt.figure(figsize=(width,height), dpi = 100)
   plt.scatter(x, y, color = 'b', s = 40, marker = 'o') # creating a dot for each point
   plt.plot(x, y, '-', color = 'b', linewidth = 2) # drawing the lines connecting the points 
   plt.scatter(x[0], y[0], color = 'r', s = 40, marker = 'o') # creating a dot for the first point / landing pad in a different color

   plt.xlim(xMin, xMax)
   plt.ylim(yMin, yMax)
   plt.axis('equal') # making the x and y axis equal units so it is not stretched

   plt.title("Best Route Found")
   plt.xlabel("X axis")
   plt.ylabel("Y axis")
   plt.grid()

   plt.savefig(f'{fileName}_SOLUTION_{distance}.jpg', format='jpg')
#    plt.show()

# route_visualization(arr, NNAnswer)

def main(): 
    print("ComputeDronePath Program:\n")

    #Testing for proper file name
    try: 
        txt_file = input("Enter the name of file: ")
        arr = file_grabber(txt_file)
    except FileNotFoundError:
        print("Invalid file name. Please check if the proper file name is given or if the file is in the same directory as program.")
    else:
        nodes = len(arr)
        if nodes > 256: 
           print("File exceeds maximum number of locations.")
           quit()
        
        euclideanAnswer = eucl_dist(arr)
        print(f"There are {nodes} nodes, computing route... (Type Control+C to stop program)") #beginning of the anytime algorithm:
        print("\tShortest Route Discovered So Far")
        localMin = float('inf')
        routeBSF = list()

        try:
            while True: #im too stupid, im just going to use control+c...
                NNAnswer = eamonn_nn(arr, euclideanAnswer) #route 
                calcDist = math.ceil(route_distance(NNAnswer, euclideanAnswer, localMin)) #total distance of route
               #when finding localMinimum, need to do early-abandonment to see if the path is necessary to traverse
                if calcDist < localMin: 
                    print(f"\t\t{calcDist}") #new BSF 
                    localMin = calcDist
                    routeBSF = NNAnswer

        except KeyboardInterrupt:
           if localMin > 6000: 
              print(f"Warning: Solution is {localMin}, greater than the 6000-meter constraint.")

           fileName = txt_file[:-4]
           fileFormatName = f"{fileName}_SOLUTION_{localMin}.txt"
           #Write the minimum route into a .txt file
           with open(fileFormatName, 'x', encoding="utf-8") as f: 
              for i in range(len(routeBSF)):
                 f.write(f"{str(routeBSF[i])}")
                 if i < nodes:
                    f.write("\n")
           print(f"Route written to disk as {fileFormatName}")
           route_visualization(arr, routeBSF, fileName, localMin)

if __name__ == "__main__":
    main()