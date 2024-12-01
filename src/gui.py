import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, colorchooser
from src.graph_logic import Graph
import random

class GraphEditorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Graph Editor")
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.graph = Graph()

        # Menu
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        # File Menu
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Load Graph", command=self.load_graph)
        file_menu.add_command(label="Save Graph", command=self.save_graph)
        menu.add_cascade(label="File", menu=file_menu)

        # Operations Menu
        operations_menu = tk.Menu(menu, tearoff=0)
        operations_menu.add_command(label="Add Node", command=self.add_node)
        operations_menu.add_command(label="Remove Node", command=self.remove_node)
        operations_menu.add_command(label="Add Edge", command=self.add_edge)
        operations_menu.add_command(label="Remove Edge", command=self.remove_edge)
        operations_menu.add_command(label="Color Node", command=self.color_node)
        operations_menu.add_command(label="Rename Node", command=self.rename_node)
        menu.add_cascade(label="Base Operations", menu=operations_menu)

        # Toolbar
        toolbar = tk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        tk.Button(toolbar, text="Adjacency Matrix", command=self.show_adjacency_matrix).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Radius and Diameter", command=self.compute_radius_and_diameter).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Make Connected Graph", command=self.make_graph_connected).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Find Hamiltonian Cycles", command=self.find_hamiltonian_cycles).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Compute Graph Center", command=self.compute_center).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Tensor Product", command=self.compute_tensor_product).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Cartesian Product", command=self.compute_cartesian_product).pack(side=tk.LEFT)

        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)

        # State to track dragging node
        self.dragging_node = None
        self.initial_coordinates = None

    def run(self):
        self.root.mainloop()

    def load_graph(self):
        """Load a graph from a file."""
        file_path = filedialog.askopenfilename(defaultextension=".bin",
                                               filetypes=[("Graph Files", "*.bin"), ("Text Files", "*.txt")])
        if file_path:
            try:
                # Load the graph using the load method from the Graph class
                self.graph = Graph.load(file_path)  # Use the static load method and update self.graph
                self.draw_graph()  # Redraw the graph after loading
                print(f"Graph loaded from {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error loading graph: {str(e)}")

    def save_graph(self):
        """Save the current graph to a file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".bin",
                                                 filetypes=[("Graph Files", "*.bin"), ("Text Files", "*.txt")])
        if file_path:
            try:
                # Save the graph using the save method from the Graph class
                self.graph.save(file_path)  # Save the graph as a .bin file
                print(f"Graph successfully saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving graph: {str(e)}")

    def draw_graph(self):
        """Redraw the graph on the canvas."""
        self.canvas.delete("all")  # Clear the canvas before redrawing

        # Ensure all nodes have 'pos', 'color', and 'shape'
        nodes = self.graph.get_nodes()
        for node, attributes in nodes.items():
            attributes.setdefault('pos', [random.random() * 500, random.random() * 500])
            attributes.setdefault('color', 'blue')  # Default color
            attributes.setdefault('shape', 'circle')  # Default shape

        # Draw edges (directed or undirected) with color if specified
        for node1, node2 in self.graph.get_edges():
            pos1, pos2 = self.graph.get_nodes()[node1]['pos'], self.graph.get_nodes()[node2]['pos']

            # Retrieve edge attributes
            edge_data = self.graph.get_edge_data(node1, node2)
            edge_color = edge_data.get('color', 'black')  # Default color
            directed = edge_data.get('directed', False)  # Default directed as False

            if directed:
                # Draw the arrow from node1 to node2 for directed edges
                self.canvas.create_line(pos1[0], pos1[1], pos2[0], pos2[1],
                                        fill=edge_color, arrow=tk.LAST, width=5,
                                        arrowshape=(10, 20, 10))
            else:
                # Draw undirected edge as a line
                self.canvas.create_line(pos1[0], pos1[1], pos2[0], pos2[1],
                                        fill=edge_color, width=3)


        # Draw nodes with their respective colors, shapes, and labels
        for node in self.graph.get_nodes():
            pos = self.graph.get_nodes()[node]['pos']
            color = self.graph.get_nodes()[node]['color']
            shape = self.graph.get_nodes()[node]['shape']
            radius = 10  # Default size for circle and square

            # Draw node shape (circle or square)
            if shape == 'circle':
                self.canvas.create_oval(pos[0] - radius, pos[1] - radius,
                                        pos[0] + radius, pos[1] + radius, fill=color)
            elif shape == 'square':
                self.canvas.create_rectangle(pos[0] - radius, pos[1] - radius,
                                             pos[0] + radius, pos[1] + radius, fill=color)

            # Draw the node label slightly above the node, with black text
            self.canvas.create_text(pos[0], pos[1] - radius - 10, text=str(node), fill="black")

    def on_mouse_press(self, event):
        """Handle mouse press events."""
        for node, attributes in self.graph.get_nodes().items():
            if 'pos' in attributes:
                node_x, node_y = attributes['pos']  # Extract x and y coordinates from the 'pos' attribute

                # Check if the mouse click is within the node bounds
                if self.is_within_bounds(event.x, event.y, node_x, node_y):
                    print(f"Node {node} clicked at ({node_x}, {node_y})")
                    self.dragging_node = node  # Set the node to be dragged
                    self.initial_coordinates = (node_x, node_y)  # Store initial coordinates

    def on_mouse_drag(self, event):
        """Moves the node with the mouse while dragging"""
        if self.dragging_node:
            new_x, new_y = event.x, event.y
            self.graph.get_nodes()[self.dragging_node]['pos'] = [new_x, new_y]  # Update position
            self.draw_graph()  # Redraw the graph to reflect the new position

    def on_mouse_release(self, _):
        """Finalize the new position of the node when mouse button is released"""
        if self.dragging_node:
            self.dragging_node = None  # Reset the dragging state
            self.initial_coordinates = None  # Clear initial coordinates

    def is_within_bounds(self, click_x, click_y, node_x, node_y, threshold=15):
        """Check if the mouse click is within a given distance (threshold) from the node."""
        distance = ((click_x - node_x) ** 2 + (click_y - node_y) ** 2) ** 0.5
        return distance <= threshold

    def show_adjacency_matrix(self):
        if not self.graph.get_nodes():
            messagebox.showerror("Error", "Graph is empty. Cannot show adjacency matrix.")
            return
        matrix = self.graph.adjacency_matrix()
        messagebox.showinfo("Adjacency Matrix", str(matrix))

    def rename_node(self):
        """Renames a node by asking the user for the current and new names."""
        # Ask the user for the current node name
        old_name = simpledialog.askstring("Rename Node", "Enter the current node name:", parent=self.root)

        if old_name:
            # Ask the user for the new node name
            new_name = simpledialog.askstring("Rename Node", f"Enter a new name for node '{old_name}':",
                                              parent=self.root)

            if new_name:
                # Call the graph operation to rename the node
                success, message = self.graph.rename_node(old_name, new_name)

                # Show result to the user
                if success:
                    messagebox.showinfo("Node Renamed", message)
                    self.draw_graph()
                else:
                    messagebox.showwarning("Error", message)

    def compute_radius_and_diameter(self):
        if not self.graph.get_nodes():
            messagebox.showerror("Error", "Graph is empty. Cannot compute radius and diameter.")
            return
        radius, diameter = self.graph.radius_and_diameter()
        messagebox.showinfo("Radius and Diameter", f"Radius: {radius}, Diameter: {diameter}")

    def add_node(self):
        """Prompts the user for node name and shape, then adds the node."""
        node_name = self._get_input("Enter node name:")
        if node_name:
            # Ask the user to choose a shape for the new node (circle or square)
            shape = simpledialog.askstring("Node Shape", "Enter the shape of the node (circle or square):",
                                           parent=self.root)

            if shape not in ['circle', 'square']:
                messagebox.showwarning("Invalid Shape", "Please enter 'circle' or 'square'.")
                return

            # Add the node with the selected shape
            self.graph.add_node(node_name, shape=shape)
            self.draw_graph()

    def remove_node(self):
        if not self.graph.get_nodes():
            messagebox.showerror("Error", "Graph is empty. Cannot remove node.")
            return
        node_name = self._get_input("Enter node name to remove:")
        if node_name:
            try:
                self.graph.remove_node(node_name)
                self.draw_graph()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def add_edge(self):
        """Adds an edge between two nodes with the option to make it directed or undirected."""
        if not self.graph.get_nodes():
            messagebox.showerror("Error", "Graph is empty. Cannot add edge.")
            return

        # Get user input for the two nodes
        node1 = self._get_input("Enter first node for edge:")
        node2 = self._get_input("Enter second node for edge:")

        if not node1 or not node2:
            messagebox.showerror("Error", "Invalid input. Both nodes are required.")
            return

        # Debugging the node input
        print(f"Adding edge between {node1} and {node2}")

        # Ask the user if the edge should be directed or not
        directed_input = simpledialog.askstring("Edge Type", "Is the edge directed? (yes/no):")
        if not directed_input:
            messagebox.showerror("Error", "No input provided for edge type.")
            return

        directed_input = directed_input.strip().lower()

        # Validate the edge direction input
        directed = directed_input == "yes"  # True if "yes", False otherwise
        if directed_input not in ("yes", "no"):
            messagebox.showwarning("Invalid Input", "Invalid input for edge type. Defaulting to undirected.")

        try:
            # Check if nodes exist
            if node1 not in self.graph.get_nodes() or node2 not in self.graph.get_nodes():
                raise ValueError(f"Nodes {node1} and/or {node2} do not exist in the graph.")

            # Add the edge with direction information
            self.graph.add_edge_to_graph(node1, node2, directed)

            # Redraw the graph
            self.draw_graph()
            print(f"Edge between {node1} and {node2} added successfully")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def remove_edge(self):
        if not self.graph.get_nodes():
            messagebox.showerror("Error", "Graph is empty. Cannot remove edge.")
            return
        node1 = self._get_input("Enter first node for edge to remove:")
        node2 = self._get_input("Enter second node for edge to remove:")
        if node1 and node2:
            try:
                self.graph.remove_edge(node1, node2)
                self.draw_graph()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def make_graph_connected(self):
        """Convert the graph to a connected graph"""
        if not self.graph.get_nodes():
            messagebox.showerror("Error", "Graph is empty. Cannot make it connected.")
            return
        self.graph.make_connected()
        self.draw_graph()
        messagebox.showinfo("Info", "The graph has been converted to a connected graph.")

    def find_hamiltonian_cycles(self):
        """Find Hamiltonian cycles in the graph"""
        if not self.graph.get_nodes():
            messagebox.showerror("Error", "Graph is empty. Cannot find Hamiltonian cycles.")
            return
        cycles = self.graph.find_hamiltonian_cycles()
        if cycles:
            messagebox.showinfo("Hamiltonian Cycles", f"Found Hamiltonian cycles:\n{cycles}")
        else:
            messagebox.showinfo("Hamiltonian Cycles", "No Hamiltonian cycles found.")

    def compute_center(self):
        """Compute the center of the graph"""
        if not self.graph.get_nodes():
            messagebox.showerror("Error", "Graph is empty. Cannot compute the center.")
            return
        center = self.graph.center()
        messagebox.showinfo("Graph Center", f"Center: {center}")

    def compute_tensor_product(self):
        """Compute the tensor product of two graphs"""
        if not self.graph.get_nodes():
            messagebox.showerror("Error", "Graph is empty. Cannot compute tensor product.")
            return
        second_graph_file = filedialog.askopenfilename(defaultextension=".bin",
                                                      filetypes=[("Graph Files", "*.bin")])
        if second_graph_file:
            second_graph = Graph.load(second_graph_file)
            result_graph = self.graph.tensor_product(second_graph)
            self.graph = result_graph
            self.draw_graph()
            messagebox.showinfo("Tensor Product", "Tensor product computed successfully.")

    def compute_cartesian_product(self):
        """Compute the cartesian product of two graphs"""
        if not self.graph.get_nodes():
            messagebox.showerror("Error", "Graph is empty. Cannot compute cartesian product.")
            return
        second_graph_file = filedialog.askopenfilename(defaultextension=".bin",
                                                      filetypes=[("Graph Files", "*.bin")])
        if second_graph_file:
            second_graph = Graph.load(second_graph_file)
            result_graph = self.graph.cartesian_product(second_graph)
            self.graph = result_graph
            self.draw_graph()
            messagebox.showinfo("Cartesian Product", "Cartesian product computed successfully.")

    def color_node(self):
        """Select a node and apply color to it."""
        if not self.graph.get_nodes():
            messagebox.showerror("Error", "Graph is empty. Cannot color a node.")
            return
        node_name = self._get_input("Enter the node name to color:")
        if node_name and node_name in self.graph.get_nodes():
            # Open color chooser dialog
            color_code = colorchooser.askcolor(title="Choose Node Color")[1]
            if color_code:
                # Update the node's color in the graph
                self.graph.get_nodes()[node_name]['color'] = color_code
                self.draw_graph()  # Redraw graph to apply the color
            else:
                messagebox.showinfo("Info", "No color selected.")
        else:
            messagebox.showerror("Error", f"Node '{node_name}' not found.")

    def _get_input(self, prompt):
        """Helper function to get user input via dialog."""
        return simpledialog.askstring("Input", prompt)