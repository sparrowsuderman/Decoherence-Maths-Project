"""
      Network Class to convert the list of nodes and connections 
      into the Q matrix and V_0 the oscillators coupled to noise.
"""

# IMPORT MODULES ==============================================================
import numpy as np

#==============================================================================

class network:
    def __init__(self, node_positions, node_connections):
        self.node_positions = node_positions # dictionary of nodes
        self.node_connections = node_connections # list of node couplings
        self.N = len(self.node_positions) # number of nodes in network

    def adjacency(self): 
        """
        Lists through node_connections (in coordinates) to return a list of 
        corresponding node connections in terms of their labels.
        """
        adjacent_pts = np.zeros((len(self.node_connections),2))
        noise = []
        for i in range(0,len(self.node_connections)): 
            (x1, y1) = (self.node_connections[i][0], self.node_connections[i][1])
            (x2, y2) = (self.node_connections[i][2], self.node_connections[i][3])
            node1 = (self.node_positions[(x1,y1)])# finds label corresponding to
            node2 = (self.node_positions[(x2,y2)])# the coordinates
            if node1 == "noise": 
                noise.append(int(node2)) # list of nodes coupled to noise
            elif node2 == "noise":
                noise.append(int(node1))
            elif (x1,y1) != (x2,y2): 
                (adjacent_pts[i][0], adjacent_pts[i][1]) = (int(node1),int(node2))
        return adjacent_pts, noise               

    def build_matrix(self, adjacent_pts): 
        """
        From list of node adjacencies, system matrix Q is returned.
        """
        Q = np.zeros((self.N-1,self.N-1))
        for i in range(0, len(adjacent_pts)):
            (x,y) = (int(adjacent_pts[i][0]),int(adjacent_pts[i][1]))
            if (x,y) != (0,0):
                Q[x][y] = 1
                Q[y][x] = 1
        return Q    

    def noise_vector(self, noise):
        """
        Returns couplings to noise in vector form, ie: first subspace V_0.
        """
        V_0 = np.zeros((len(noise),self.N-1))
        for i in range(0,len(noise)): 
            V_0[i][int(noise[i])] = 1 
        return V_0

    def output_matrix(self):
        """
        Completes all the steps required to convert list and disctionary which 
        are input to return the Q matrix and noise vectors.
        """
        adjacent_pts, noise = self.adjacency()
        Q = self.build_matrix(adjacent_pts)
        V_0 = self.noise_vector(noise)
        return Q, V_0
        