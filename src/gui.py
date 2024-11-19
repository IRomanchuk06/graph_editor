import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from src.graph_logic import Graph

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
        menu.add_cascade(label="Operations", menu=operations_menu)

        # Toolbar
        toolbar = tk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        tk.Button(toolbar, text="Adjacency Matrix", command=self.show_adjacency_matrix).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Radius and Diameter", command=self.compute_radius_and_diameter).pack(side=tk.LEFT)

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
        self.canvas.delete("all")
        for edge in self.graph.edges:
            x1, y1 = self.graph.nodes[edge[0]]
            x2, y2 = self.graph.nodes[edge[1]]
            self.canvas.create_line(x1, y1, x2, y2, fill="black")
        for node, (x, y) in self.graph.nodes.items():
            self.canvas.create_oval(x - 15, y - 15, x + 15, y + 15, fill="lightblue", tags=node)
            self.canvas.create_text(x, y, text=node, tags=node)

    def on_mouse_press(self, event):
        """Detects the node under the mouse click"""
        for node, (x, y) in self.graph.nodes.items():
            if abs(event.x - x) <= 15 and abs(event.y - y) <= 15:
                self.dragging_node = node
                self.initial_coordinates = (x, y)
                break

    def on_mouse_drag(self, event):
        """Moves the node with the mouse while dragging"""
        if self.dragging_node:
            # Update node position
            new_x, new_y = event.x, event.y
            self.graph.nodes[self.dragging_node] = (new_x, new_y)
            self.draw_graph()

    def on_mouse_release(self, _):
        """Finalize the new position of the node when mouse button is released"""
        if self.dragging_node:
            self.dragging_node = None
            self.initial_coordinates = None

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

    @staticmethod
    def _get_input(prompt: str) -> str | None:
        """Gets user input from a dialog."""
        return simpledialog.askstring("Input", prompt)
