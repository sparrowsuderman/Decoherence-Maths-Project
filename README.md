# Decoherence-Maths-Project
Code produced as part of my third year maths project. Allows a user to draw a network (using a series of clicks) and then returns whether the system has Decoherence Free Subspaces.
<br> `interface.py` produces the interface for which allows the user to interact to input information and receive results.
<br> `network_to_matrix.py` converts the network which is input by the user into an 'adjacency' matrix and some vectors which represent the connections to the environment.
<br> `dfs.py` computes the propagation of decoherence through the network in order to determine whether there is a subspace which is protected from decoherence.
