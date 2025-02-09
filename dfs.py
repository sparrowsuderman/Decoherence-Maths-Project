"""
   Algorithm to deduce whether a network has a Decoherence Free Subspace
                          and find what it is.
"""
# IMPORT MODULES ==============================================================
import numpy as np
from fractions import Fraction
import sympy as sp

# =============================================================================
class dfs:
    def __init__(self, Q, V_0):
        self.Q = Q
        self.V_0 = V_0
     
        
    def propagation(self):
       subspaces = self.V_0
       W_ks = self.V_0

       while np.all(W_ks == 0) == False: 
           for i in range(len(W_ks)):  
               W_k = W_ks[i]
               W_new = self.multiply(self.Q, W_k)
               W_new = self.Gram_Schmidt(W_new, subspaces)
               W_simp = np.vectorize(lambda x: Fraction(x).limit_denominator())(W_new) 
               if np.all(W_simp == 0) == False: 
                   subspaces = np.vstack([subspaces, W_simp])
               W_ks[i] = W_simp
       self.print_subspaces(subspaces, False)
       dim_space, dim_vec = subspaces.shape # num of subspaces affected by noise, num of nodes
       Wdf_dim = int(dim_vec - dim_space) #dimension of W_df
       if Wdf_dim == 0: 
            print("There is no decoherence free subspace.")
            dfs = None
       elif Wdf_dim != 0:          
            print("There is a decoherence free subspace of dimension %d."%(Wdf_dim))
            dfs = self.W_df(subspaces, Wdf_dim) # determine decoherence free subspaces
            self.decouple_system(subspaces, dfs, dim_vec)
       return Wdf_dim, dfs, subspaces

    def dot(self, vector_1, vector_2):
        """
        DOT PRODUCT
        """
        sum_ = np.dot(vector_1, vector_2)
        return sum_
                            
    def multiply(self, matrix,vector):
        """
        MATRIX MULTIPLIED WITH VECTOR
        """
        # Multiply matrix and vector and return result
        result = np.matmul(matrix,vector)
        return result

    def Gram_Schmidt(self, vector, subspaces):
        """
        Gram-schmidt process to orthogonalise a vector given a set.
        """
        v1 = vector
        for i in range(0,len(subspaces)): 
            v2 = subspaces[i]
            dot1 = self.dot(v1,v2)
            dot2 = self.dot(v2,v2)
            scale = -1*dot1/dot2
            v2 = scale*v2
            vnew = v1 + v2
            v1 = vnew
        return v1
    
    def unit(self,vector):
        """
        returns unit vectors
        """
        mag_sqrd = self.dot(vector,vector)
        mag = sp.sqrt(mag_sqrd)
        print(mag)
        vector = vector/mag
        return vector

    def W_df(self, subspaces, Wdf_dim):
        """
        Takes subspaces formed and returns the Decoherence Free Subspace, 
        using Gaussian elimination, then Gram-Schmidt.
        """
        subspace_cols = sp.Matrix((subspaces))
        subspaces_dim, system_dim = subspaces.shape
        
        RREF, nodes = sp.Matrix(subspace_cols).rref()
        W_df = np.zeros((Wdf_dim, system_dim),float)
        df_nodes = []
        for i in range(system_dim):
            if float(i) not in nodes:
                df_nodes.append(i)
        
        for i in range(Wdf_dim):
            j = df_nodes[i]
            W_df[i][j] = 1.0
            vector = np.array(W_df[i])
            W_df[i] = self.Gram_Schmidt(vector, subspaces)
            subspaces = np.vstack([subspaces,W_df[i]])
        self.print_subspaces(W_df, True)
        return W_df # returns DFS

    
        #NEED TO WORK ON THIS SO THAT IT WOKRS BETTER SO WILL LEAVE IT FOR NOW
    def decouple_system(self, subspaces, W_df, N):
        all_subspaces_frac = np.vstack([subspaces,W_df])
        all_subspaces = all_subspaces_frac.astype(float)
        A_t = np.zeros((N,N)) # rows are subspaces
        for i in range(N):  
            A_t[i] = self.unit(all_subspaces[i])
        A = np.transpose(A_t) # columns are subspaces
        Q_transformed = self.multiply(A_t,(self.multiply(self.Q, A)))
        self.print_subspaces(Q_transformed, True)
        Roots = Q_transformed **2
        print("Terms are all squared because can't do surds")
        self.print_subspaces(Roots, True)
        
    def print_subspaces(self, Matrix, Dec_Free): # needs to be changed / or not? adjust or new function to print to canvas, later
       """
       Takes the matrix containing subspaces, converts all the decimals to fractions
       and prints the matrix in a viewer friendly way such that the columns are the subspaces. 
       """
       Printable = np.vectorize(lambda x: Fraction(x).limit_denominator())(Matrix)
       matrix = np.transpose(Printable)
       if Dec_Free == True:
           print("This is the Decoherence Free Subspace:")
       else: 
           print("These are the subspaces affected by decoherence:")
      
        # Determine the width of each column
       column_widths = [max(len(str(item)) for item in matrix[:, col]) for col in range(matrix.shape[1])]
       for row in matrix:
           formatted_row = " | ".join(f"{str(item):<{column_widths[i]}}" for i, item in enumerate(row))
           print(formatted_row)






