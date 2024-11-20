import networkx as nx
import pickle
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox, colorchooser
import random
import itertools

class Graph:
    def __init__(self, canvas_width=800, canvas_height=600):
        """Initializes the graph with the canvas dimensions for node placement"""
        self.nodes = {}
        self.edges = []
        self.graph = nx.Graph()
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.node_colors = {}
        plt.ion()  # Enable interactive mode

    def add_node(self, name):
        """Adds a node at the center of the canvas with unique coordinates"""
        if name in self.graph:
            raise ValueError(f"Node {name} already exists.")
        x = self.canvas_width // 2  # X center coordinate
        y = self.canvas_height // 2  # Y center coordinate
        self.nodes[name] = (x, y)  # Save node position
        self.graph.add_node(name)  # Add node to the graph

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

    def center(self):
        """Returns the center of the graph"""
        if nx.is_connected(self.graph):
            return nx.center(self.graph)
        return None

    def remove_node(self, node_name):
        """Removes a node and all its associated edges from the graph"""
        if node_name in self.graph:
            self.graph.remove_node(node_name)
            del self.nodes[node_name]
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

    def get_edge_data(self, node1, node2):
        """Returns edge data between two nodes, if the edge exists."""
        if self.graph.has_edge(node1, node2):
            return self.graph[node1][node2]  # Returns a dictionary with edge data (if any)
        else:
            raise ValueError(f"No edge exists between {node1} and {node2}")

    def adjacency_matrix(self):
        """Returns the adjacency matrix of the graph"""
        adj_matrix = nx.adjacency_matrix(self.graph)
        return adj_matrix.toarray().tolist()

    def save(self, filename: str):
        """Saves the graph object to a file using pickle"""
        if not filename:
            print("Error: Invalid filename provided.")
            return
        try:
            with open(filename, "wb") as file:
                pickle.dump(self, file)
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
                graph_data = pickle.load(file)
                print(f"Graph loaded from {filename}")
                return graph_data
        except Exception as e:
            print(f"Error loading graph: {e}")
            raise

    def make_connected(self):
        """Makes the graph connected by adding edges"""
        if not nx.is_connected(self.graph):
            connected_components = list(nx.connected_components(self.graph))
            for i in range(len(connected_components) - 1):
                node1 = list(connected_components[i])[0]
                node2 = list(connected_components[i + 1])[0]
                self.add_edge(node1, node2)
            print("Graph has been made connected.")

    def _find_hamiltonian_cycle_util(self, path, pos):
        # If all vertices are included in the path
        if pos == len(self.graph.nodes):
            # Check if the last node is connected to the first node to form a cycle
            if self.graph.has_edge(path[pos - 1], path[0]):
                return True
            return False

        for node in self.graph.nodes:
            if node not in path:  # Ensure node has not been visited
                # Check if there is an edge between the last node and the current node
                if self.graph.has_edge(path[pos - 1], node):
                    path[pos] = node
                    if self._find_hamiltonian_cycle_util(path, pos + 1):
                        return True
                    path[pos] = -1  # Backtrack
        return False

    def find_hamiltonian_cycles(self):
        # Start from the first node
        path = [-1] * len(self.graph.nodes)
        path[0] = list(self.graph.nodes)[0]

        # Try to find a Hamiltonian cycle using backtracking
        if self._find_hamiltonian_cycle_util(path, 1):
            # If a cycle is found, return the cycle (start to end and back to start)
            return [path + [path[0]]]
        return []  # No Hamiltonian cycle found

    def tensor_product(self, second_graph):
        """Compute the tensor product of two graphs."""
        result_graph = nx.Graph()  # Create an empty graph for the result

        # Iterate over all pairs of nodes from both graphs
        for (v1, v2) in itertools.product(self.graph.nodes, second_graph.nodes):
            # Add the combined node to the result graph
            result_graph.add_node((v1, v2))

        # Iterate over all pairs of edges to determine tensor product edges
        for (v1, u1) in self.graph.edges:
            for (v2, u2) in second_graph.edges:
                # Add an edge in the result graph if conditions are met
                result_graph.add_edge((v1, v2), (u1, u2))

        return result_graph

    def cartesian_product(self, other_graph):
        """Returns the Cartesian product of the current graph with another graph"""
        return nx.cartesian_product(self.graph, other_graph.graph)

    def draw(self):
        """Draws the graph using matplotlib and applies the node colors"""
        plt.clf()  # Clear the current figure
        pos = {node: coords for node, coords in self.nodes.items()}  # Node positions
        node_color_list = [self.node_colors.get(node, 'lightblue') for node in self.graph.nodes]
        nx.draw(self.graph, pos, with_labels=True, node_color=node_color_list,
                node_size=500, font_size=10, font_color='black', font_weight='bold')
        plt.draw()  # Update the current figure
        plt.pause(0.1)  # Small pause to ensure the figure updates

    def set_node_color(self, node, color):
        """Set color for a specific node."""
        if node in self.nodes:
            self.node_colors[node] = color
        else:
            raise ValueError("Node does not exist")

    def get_node_color(self, node):
        """Return the color of a specific node."""
        return self.node_colors.get(node, "lightblue")  # Default to lightblue if no color is set

    def gui_color_node(self):
        """GUI for selecting node and color"""
        def on_color_change():
            node_name = node_name_entry.get()
            color = color_entry.get()
            try:
                self.color_node(node_name, color)
            except ValueError as e:
                error_label.config(text=str(e))

        # Create a simple Tkinter window for color selection
        gui_window = tk.Tk()
        gui_window.title("Color Node")

        # Entry for node name
        tk.Label(gui_window, text="Enter Node Name:").pack()
        node_name_entry = tk.Entry(gui_window)
        node_name_entry.pack()

        # Entry for color
        tk.Label(gui_window, text="Enter Color:").pack()
        color_entry = tk.Entry(gui_window)
        color_entry.pack()

        # Button to change color
        color_button = tk.Button(gui_window, text="Change Color", command=on_color_change)
        color_button.pack()

        # Label for error messages
        error_label = tk.Label(gui_window, text="", fg="red")
        error_label.pack()

        gui_window.mainloop()

    def color_node_from_gui(self):
        """Select a node and apply color to it"""
        if not self.graph.nodes:
            messagebox.showerror("Error", "Graph is empty. Cannot color a node.")
            return
        node_name = self._get_input("Enter the node name to color:")
        if node_name in self.graph.nodes:
            color = colorchooser.askcolor()[1]
            if color:
                self.set_node_color(node_name, color)
                self.draw()
        else:
            messagebox.showerror("Error", "Node not found.")
