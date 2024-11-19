import networkx as nx
import pickle

class Graph:
    def __init__(self, canvas_width=800, canvas_height=600):
        """Initializes the graph with the canvas dimensions for node placement"""
        self.nodes = {}
        self.edges = []
        self.graph = nx.Graph()
        self.canvas_width = canvas_width  # Default canvas width
        self.canvas_height = canvas_height  # Default canvas height

    def add_node(self, name):
        """Adds a node at the center of the canvas with unique coordinates"""
        # Calculate the center of the canvas
        x = self.canvas_width // 2  # X center coordinate
        y = self.canvas_height // 2  # Y center coordinate
        self.nodes[name] = (x, y)
        self.graph.add_node(name)

    def add_edge(self, node1, node2):
        """Adds an edge between two nodes"""
        if node1 not in self.graph or node2 not in self.graph:
            raise ValueError("One or both nodes do not exist in the graph.")
        self.edges.append((node1, node2))
        self.graph.add_edge(node1, node2)

    def is_connected(self):
        """Checks if the graph is connected"""
        return nx.is_connected(self.graph)

    def radius_and_diameter(self):
        """Returns the radius and diameter of a connected graph"""
        if nx.is_connected(self.graph):
            radius = nx.radius(self.graph)
            diameter = nx.diameter(self.graph)
            return radius, diameter
        return None, None

    def remove_node(self, node_name):
        """Removes a node and all its associated edges from the graph"""
        if node_name in self.graph:
            # Remove all edges connected to this node
            self.graph.remove_node(node_name)
            # Remove the node from the nodes dictionary
            del self.nodes[node_name]
            # Remove all edges from the edges list that involve this node
            self.edges = [edge for edge in self.edges if node_name not in edge]
        else:
            raise ValueError(f"Node {node_name} does not exist.")

    def remove_edge(self, node1, node2):
        """Removes an edge between two nodes"""
        if (node1, node2) in self.edges:
            self.edges.remove((node1, node2))
            self.graph.remove_edge(node1, node2)
        elif (node2, node1) in self.edges:
            self.edges.remove((node2, node1))
            self.graph.remove_edge(node2, node1)
        else:
            raise ValueError(f"Edge between {node1} and {node2} does not exist.")

    def adjacency_matrix(self):
        """Returns the adjacency matrix of the graph"""
        # Using networkx's adjacency_matrix function to get the matrix as a sparse matrix
        adj_matrix = nx.adjacency_matrix(self.graph)
        # Convert the sparse matrix to a dense one and return as a list of lists
        return adj_matrix.toarray().tolist()

    def save(self, filename: str):
        """Saves the graph object to a file using pickle"""
        if not filename:
            print("Error: Invalid filename provided.")
            return

        try:
            with open(filename, "wb") as file:
                pickle.dump(self, file)  # Serialize the entire graph object
                print(f"Graph successfully saved to {filename}")
        except PermissionError:
            print(f"Error: Permission denied when saving to {filename}")
        except Exception as e:
            print(f"Error saving graph: {e}")

    @staticmethod
    def load(filename: str):
        """Loads the graph from a pickle file"""
        try:
            with open(filename, "rb") as file:
                graph_data = pickle.load(file)  # Deserialize the graph
                print(f"Graph loaded from {filename}")
                return graph_data  # Return the deserialized graph object
        except Exception as e:
            print(f"Error loading graph: {e}")
            raise
