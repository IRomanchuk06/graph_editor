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
        operations_menu.add_command(label="Color Node", command=self.color_node)  # Changed to 'Color Node'
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
        """Draw the graph with updated colors and node labels."""
        self.canvas.delete("all")  # Clear the canvas before redrawing

        # Ensure that all nodes have 'pos' and optionally 'color'
        for node in self.graph.nodes:
            if isinstance(self.graph.nodes[node], tuple):
                self.graph.nodes[node] = {'pos': list(self.graph.nodes[node])}
            if 'pos' not in self.graph.nodes[node]:
                self.graph.nodes[node]['pos'] = [random.random() * 500, random.random() * 500]
            elif isinstance(self.graph.nodes[node]['pos'], tuple):
                self.graph.nodes[node]['pos'] = list(self.graph.nodes[node]['pos'])
            if 'color' not in self.graph.nodes[node]:
                self.graph.nodes[node]['color'] = "blue"  # Default color

        # Draw edges with color if specified
        for edge in self.graph.edges:
            node1, node2 = edge
            pos1 = self.graph.nodes[node1]['pos']
            pos2 = self.graph.nodes[node2]['pos']

            # Use get_edge_data to access edge attributes safely
            edge_data = self.graph.get_edge_data(node1, node2)
            edge_color = edge_data.get('color', "black") if edge_data else "black"  # Default color

            self.canvas.create_line(pos1[0], pos1[1], pos2[0], pos2[1], fill=edge_color)

        # Draw nodes with their respective colors and labels
        for node in self.graph.nodes:
            pos = self.graph.nodes[node]['pos']
            color = self.graph.nodes[node]['color']
            radius = 10

            # Draw the node as a circle
            self.canvas.create_oval(pos[0] - radius, pos[1] - radius,
                                    pos[0] + radius, pos[1] + radius, fill=color)

            # Draw the node label slightly above the node, with black text
            self.canvas.create_text(pos[0], pos[1] - radius - 10, text=str(node), fill="black")

    def on_mouse_press(self, event):
        """Handle mouse press events."""
        for node, attributes in self.graph.nodes.items():
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
            self.graph.nodes[self.dragging_node]['pos'] = [new_x, new_y]  # Update position
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
        if not self.graph.nodes:
            messagebox.showerror("Error", "Graph is empty. Cannot show adjacency matrix.")
            return
        matrix = self.graph.adjacency_matrix()
        messagebox.showinfo("Adjacency Matrix", str(matrix))

    def compute_radius_and_diameter(self):
        if not self.graph.nodes:
            messagebox.showerror("Error", "Graph is empty. Cannot compute radius and diameter.")
            return
        radius, diameter = self.graph.radius_and_diameter()
        messagebox.showinfo("Radius and Diameter", f"Radius: {radius}, Diameter: {diameter}")

    def add_node(self):
        node_name = self._get_input("Enter node name:")
        if node_name:
            self.graph.add_node(node_name)
            self.draw_graph()

    def remove_node(self):
        if not self.graph.nodes:
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
        if not self.graph.nodes:
            messagebox.showerror("Error", "Graph is empty. Cannot add edge.")
            return
        node1 = self._get_input("Enter first node for edge:")
        node2 = self._get_input("Enter second node for edge:")
        if node1 and node2:
            try:
                self.graph.add_edge(node1, node2)
                self.draw_graph()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def remove_edge(self):
        if not self.graph.nodes:
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
        if not self.graph.nodes:
            messagebox.showerror("Error", "Graph is empty. Cannot make it connected.")
            return
        self.graph.make_connected()
        self.draw_graph()
        messagebox.showinfo("Info", "The graph has been converted to a connected graph.")

    def find_hamiltonian_cycles(self):
        """Find Hamiltonian cycles in the graph"""
        if not self.graph.nodes:
            messagebox.showerror("Error", "Graph is empty. Cannot find Hamiltonian cycles.")
            return
        cycles = self.graph.find_hamiltonian_cycles()
        if cycles:
            messagebox.showinfo("Hamiltonian Cycles", f"Found Hamiltonian cycles:\n{cycles}")
        else:
            messagebox.showinfo("Hamiltonian Cycles", "No Hamiltonian cycles found.")

    def compute_center(self):
        """Compute the center of the graph"""
        if not self.graph.nodes:
            messagebox.showerror("Error", "Graph is empty. Cannot compute the center.")
            return
        center = self.graph.center()
        messagebox.showinfo("Graph Center", f"Center: {center}")

    def compute_tensor_product(self):
        """Compute the tensor product of two graphs"""
        if not self.graph.nodes:
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
        if not self.graph.nodes:
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
        if not self.graph.nodes:
            messagebox.showerror("Error", "Graph is empty. Cannot color a node.")
            return
        node_name = self._get_input("Enter the node name to color:")
        if node_name and node_name in self.graph.nodes:
            # Open color chooser dialog
            color_code = colorchooser.askcolor(title="Choose Node Color")[1]
            if color_code:
                # Update the node's color in the graph
                self.graph.nodes[node_name]['color'] = color_code
                self.draw_graph()  # Redraw graph to apply the color
            else:
                messagebox.showinfo("Info", "No color selected.")
        else:
            messagebox.showerror("Error", f"Node '{node_name}' not found.")

    def _get_input(self, prompt):
        """Helper function to get user input via dialog."""
        return simpledialog.askstring("Input", prompt)