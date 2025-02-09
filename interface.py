# IMPORT MODULES ==============================================================
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import Canvas

import numpy as np
from fractions import Fraction

# IMPORT CLASSES FOR COMPUTATIONS =============================================
from dfs import dfs
from network_to_matrix import network


# TUPLES FOR FONT AND SIZE OF TEXT ON PAGE ====================================
title = ("Verdana", 20)
text = ("Verdana", 15)
subscript = ("Verdana", 10)

# =============================================================================
class Mastermind(tk.Tk): 
    def __init__(self): 
         tk.Tk.__init__(self)
         container = tk.Frame(self) 
         container.pack(side = "top", fill = "both", expand = True) 
         
         # INFO NEEDED FOR EACH FRAME
         self.rows = 20
         self.cols = 40
         self.cell_size = np.floor(min(
             self.winfo_screenwidth()/self.cols,
             self.winfo_screenheight()/self.rows))
         
         self.bind("<Configure>", self.resize_window)
 
         self.noise_position = (3,1) # location of node which represents noise
         self.node_positions = {self.noise_position: 'noise'} # dictionary of the node positions
         self.node_connections = [] # list of tuples (x1,y1,x2,y2) to describe the connection between two nodes
         
         self.Q = [] # system matrix
         self.V_0 = [] # couplings to noise
         self.W_df = [] # decoherence free subspace

         self.frames = {} # empty array to store the pages 
         self.frames["input_network"] = input_network(container, self)
         self.frames["describe_system"] = describe_system(container, self)
         self.frames["results"] = results(container, self)
         for frame in self.frames.values():
             frame.grid(row=0, column=0)
         self.show_frame("input_network") # starts on start page
         
    def show_frame(self, choice):
        """
        Raises specified frame to user view.
        """
        frame = self.frames[choice] 
        frame.tkraise()
         
    def resize_window(self,event):
        """
        Allows user to resize window, so frame resizes accordingly.
        """
        self.cell_size = np.floor(min(
            event.width/self.cols,
            event.height/self.rows))
        for frame in self.frames.values():
            frame.resize_frame()

class ResizableFrame(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self,parent)
    def resize_frame(self):
        pass

class input_network(ResizableFrame):  
    def __init__(self, parent, controller):
        ResizableFrame.__init__(self, parent)
        
        self.controller = controller
        self.cell_size = controller.cell_size
        self.rows = controller.rows
        self.cols = controller.cols
        
        self.first_coord = None
        self.second_coord = None
        
        self.canvas = Canvas(self, width= self.cols * self.cell_size, height=self.rows * self.cell_size) 
        self.canvas.pack()
        self.draw_grid()
        self.add_text()
        self.canvas.bind("<Button-1>", self.line) # binds mouseclick event to add_node
        
        self.btn = ttk.Button(self, text = 'Next', command = lambda: self.ask_yes_no())
        self.btn.pack(expand = True)
        self.btn.place(x= (self.cell_size*self.cols) - 100 , y= (self.cell_size*self.rows) - 100)
          
    def add_text(self):
        """
        Adds text to user interface, to explain how to draw network.
        """
        heading = "CLICK ON THE GRID TO DRAW THE OSCILLATOR NETWORK."
        instructions = "Click once to set the first node and then click again to set the node its coupled to."
        noise = "Blue node represents noise/coupling to the environment."
        self.canvas.create_text((self.cols*self.cell_size/2),20, font = title,text = heading)
        self.canvas.create_text((self.cols*self.cell_size/2),70, font = text, text = instructions)
        self.canvas.create_text(420,150, font = text, text = noise)
        (y,x) = self.controller.noise_position
        self.canvas.create_oval(
            (x+0.25)*self.cell_size,
            (y+0.25)*self.cell_size,
            (x+0.75)*self.cell_size,
            (y+0.75)*self.cell_size,
            fill= "blue") 
        
    def draw_grid(self): 
        """
        Loops over each row and column, draws the grid for the interface.
        """
        for i in range(self.rows):
            for j in range(self.cols):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="purple") # draws the grid
                
    def coords(self, x,y): 
        """
        Takes pixel coordinates of click and converts to grid coordinates.
        """
        col = x // self.cell_size
        row = y // self.cell_size
        return (row,col)
    
    def position(self, x,y): 
        """
        From grid coordinates, returns pixel coordinates of the plotted node.
        """
        row, col = self.coords(x, y)
        x_pos = int(col*self.cell_size + self.cell_size // 2)
        y_pos = int(row*self.cell_size + self.cell_size // 2)
        return (x_pos, y_pos)
    
    def add_node(self, x,y): 
        """
        Adds new nodes to the dictionary of nodes and their labels. Plots node.
        """
        row, col = self.coords(x,y)
        if (row, col) not in self.controller.node_positions and (row,col) != self.controller.noise_position: 
            index = (len(self.controller.node_positions)-1)
            self.controller.node_positions[(row,col)] = index # adds to the dictionary with unique index
            # the key is the coordinates and the value is the index 
            self.draw_node(row, col, "purple") # visual representation
            
    def line(self, event):
        """
        Tracks lines added to network; keeps a list of these and draw them.
        """
        if self.first_coord is None:
            self.first_coord = (event.x, event.y)            
            self.add_node(self.first_coord[0],self.first_coord[1])
        else:
            self.second_coord = (event.x, event.y)
            self.add_node(self.second_coord[0],self.second_coord[1])
            
            x1, y1 = self.position(self.first_coord[0],self.first_coord[1])
            x2, y2 = self.position(self.second_coord[0],self.second_coord[1])
            
            r1, c1 = self.coords(x1,y1)
            r2, c2 = self.coords(x2,y2)
            self.controller.node_connections.append((r1,c1,r2,c2))
            self.canvas.create_line(x1, y1, x2, y2)
            
            self.first_coord = None 
            
    def draw_node(self, row, col, colour):
        """
        Plots nodes on interface, as circles with specified colour.
        """
        if (row,col) != (3,1): 
            x = col*self.cell_size + self.cell_size // 2
            y = row*self.cell_size + self.cell_size // 2
            radius = 8
            self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill= colour)
            
    def ask_yes_no(self):
        """
        When user clicks next button, checks network has been completed.
        """
        result = messagebox.askyesno("Proceed", "Have you completed the network?")
        if result == True:
            self.controller.show_frame("describe_system")
            
    def resize_frame(self):
        """
        Allows frame to be resized if user changed size of window
        """
        self.cell_size = self.controller.cell_size
        self.canvas.delete("all")
        self.draw_grid()
        self.add_text()
        for (row,col) in self.controller.node_positions:
            self.draw_node(row,col,"purple")
        for (r1,c1,r2,c2) in self.controller.node_connections:
            x1,y1=self.position(c1*self.cell_size,r1*self.cell_size)
            x2,y2=self.position(c2*self.cell_size,r2*self.cell_size)
            self.canvas.create_line(x1, y1, x2, y2)
    
class describe_system(ResizableFrame):
    def __init__(self, parent, controller):
        ResizableFrame.__init__(self, parent)
        
        self.controller = controller
        self.cell_size = controller.cell_size
        self.rows = controller.rows
        self.cols = controller.cols

        self.canvas = Canvas(self, width= self.cols * self.cell_size, height=self.rows * self.cell_size)  
        self.canvas.pack() 
        self.draw_grid()    
        
    def draw_grid(self): 
        """
        Loops over each row and column, draws the grid for the interface.
        """
        for i in range(self.rows):
            for j in range(self.cols):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="purple") # draws the grid 
        self.canvas.create_text((self.cols*self.cell_size/2, 20), font = title,text = "MATRIX REPRESENTATION OF THE NETWORK.")
        btn = ttk.Button(self, text='Next', command = lambda: self.controller.show_frame("results")) 
        btn.pack()
        btn.place(x= (self.cell_size*self.cols) - 80 , y= (self.cell_size*self.rows) - 80)
        
    def tkraise(self):
        """
        Action upon user pressing 'next' button. Calls network class to obtain
        matrix Q and noise_vectors V_0.
        """
        N = len(self.controller.node_positions)
        convert = network(self.controller.node_positions,self.controller.node_connections)
        Q, V_0 = convert.output_matrix()
    
        print("Q = np.array(",Q,")")
        print("V_0 = np.array(",V_0,")")
        # SAVE RESULTS TO CONTROLLER CLASS
        self.controller.Q = Q
        self.controller.V_0 = V_0
        
        # SHOW RESULTS ON INTERFACE
        self.draw_matrix(Q, N)
        self.draw_noise_vectors(V_0, N)
        super().tkraise()
    
    def draw_matrix(self, Q, N):
        """
        Adds Q matrix to user interface.
        """
        self.canvas.create_text(40,(int(N/2) + 1.5)*self.cell_size, font = title, text = "Q =")
        for i in range(0, N-1):
            for j in range(0, N -1):
                x = 110 + i*self.cell_size
                y = 110 + j*self.cell_size
                if i == j:
                    self.canvas.create_text(x, y, font = title, text = "w" )
                elif int(Q[i][j]) == 1:
                    self.canvas.create_text(x, y, font = title, text = "d" )
                else:    
                    self.canvas.create_text(x, y, font = title, text = str(int(Q[i][j])) )         
    
    def draw_noise_vectors(self, V_0, N):
        """
        Adds noise vectors V_0 to user interface.
        """
        self.canvas.create_text(int(N*1.2 + 3)*self.cell_size, (int(N/2) + 1.5)*self.cell_size, font = title, text = "V =")
        self.canvas.create_text(int(N*1.2 + 3)*self.cell_size, (int(N/2) + 1.8)*self.cell_size, font = subscript, text = "0")
        for i in range(0,N-1): # component of the vectors
            for j in range(0,len(V_0)): # each vector
                   y = 110 + i*self.cell_size
                   x = (N + 5.5 + j)*self.cell_size
                   self.canvas.create_text(x, y, font = title, text = str(int(V_0[j][i])))
        for i in range(0,len(V_0)-1):
            vert = (int(N*3/2) + 3.5)*self.cell_size
            horiz = (3.5 + i*2)*self.cell_size
            self.canvas.create_text(horiz,vert, font = title, text = ";")               

class results(ResizableFrame):
    def __init__(self, parent, controller):
      ResizableFrame.__init__(self, parent)
      self.controller = controller
      self.cell_size = controller.cell_size
      self.rows = controller.rows
      self.cols = controller.cols
      self.Q = controller.Q
      self.V_0 = controller.V_0
      self.W_df = controller.W_df

      self.canvas = Canvas(self, width= self.cols * self.cell_size, height=self.rows * self.cell_size)  
      self.canvas.pack() 
      self.draw_grid()
      
    def draw_grid(self): 
        """
        Loops over each row and column, draws the grid for the interface.
        """
        for i in range(self.rows):
             for j in range(self.cols):
                 x1 = j * self.cell_size
                 y1 = i * self.cell_size                  
                 x2 = x1 + self.cell_size
                 y2 = y1 + self.cell_size
                 self.canvas.create_rectangle(x1, y1, x2, y2, outline="purple") # draws the grid 
        header = "CONCLUSIONS: IS THERE A DECOHERENCE FREE SUBSPACE?"
        self.canvas.create_text((self.cols*self.cell_size/2, 20), font = title,text = header)
        disclaimer = "If vector elements overlap or are illegible, these subspaces may be found in the Python console."
        self.canvas.create_text((self.cols*self.cell_size/2, 60), font = text, text = disclaimer)
        btn = ttk.Button(self, text='Next', command = self.destroy)
        btn.pack()
        btn.place(x= (self.cell_size*self.cols) - 80 , y= (self.cell_size*self.rows) - 80)
    
            
    def draw_subspaces(self, Wdf_dim, dfs, subspaces):
        """
        Adds the subspaces and W_df to the interface.
        """
        N = len(self.controller.Q)
        
        heading = "These are the subspaces affected by decoherence:"
        self.canvas.create_text(8*self.cell_size,int(4.5*self.cell_size), font = text, text = heading)
        
        subspaces = np.vectorize(lambda x: Fraction(x).limit_denominator())(subspaces)
        rows, cols = subspaces.shape
        for i in range(rows): # component of the vectors
            for j in range(cols): # each vector
                   y =(5.5 + j)*self.cell_size
                   x = (2.5 + (i*2))*self.cell_size
                   self.canvas.create_text(x, y, font = title, text = str(subspaces[i][j]))
        for i in range(0,len(subspaces)-1):
            vert = (5+N/2)*self.cell_size
            horiz = (3.5 + i*2)*self.cell_size
            self.canvas.create_text(horiz,vert, font = title, text = ";")   
        if Wdf_dim !=0:
            heading_2 = "And this is the decoherence free subspace:"
            self.canvas.create_text(24*self.cell_size,int(4.5*self.cell_size), font = text, text = heading_2, fill = "purple")
            
            dfs = np.vectorize(lambda x: Fraction(x).limit_denominator())(dfs)
            rows, cols = dfs.shape
            for i in range(rows): # component of the vectors
                for j in range(cols): # each vector
                       y =(5.5 + j)*self.cell_size
                       x = (20.5 + (i*2))*self.cell_size
                       self.canvas.create_text(x, y, font = title, text = str(dfs[i][j]), fill = "purple")
            for i in range(0,len(dfs)-1):
                vert = (5+N/2)*self.cell_size
                horiz = (21.5 + i*2)*self.cell_size
                self.canvas.create_text(horiz,vert, font = title, text = ";")
                 
    def tkraise(self):
        """
        Action upon user pressing 'next' button. Calls dfs class to find the 
        subspaces formed by decoherence and W_df, if it exists.
        """
        DFS = dfs(self.controller.Q, self.controller.V_0)
        Wdf_dim, W_df, Subspaces = DFS.propagation()
        if Wdf_dim == 0:
            heading = "No, there is no Decoherence Free Subspace."
            self.canvas.create_text((9.5*self.cell_size, 110), font = text, text = heading)
        elif Wdf_dim > 0:
            heading = ("Yes, there is a Decoherence Free Subspace of dimension %d"%(Wdf_dim))
            self.canvas.create_text((9.5*self.cell_size, 110), font = text, text = heading)
        self.draw_subspaces(Wdf_dim, W_df, Subspaces)
        super().tkraise()
  
app = Mastermind()
app.attributes("-zoomed", True)
app.mainloop()
