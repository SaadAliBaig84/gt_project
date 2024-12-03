import tkinter as tk
from tkinter import simpledialog
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Ford Fulkerson Algorithm to compute Maximum Flow
def ford_fulkerson(graph, source, sink):
    flow = 0
    residual_graph = graph.copy()
    max_flow = {}
    step = 0  # Step counter for path colors

    while True:
        # Step 1: Perform BFS to find an augmenting path
        parent = bfs(residual_graph, source, sink)
        
        if not parent:  # No augmenting path found
            break
        
        # Step 2: Find the minimum capacity in the augmenting path
        path_flow = float('Inf')
        s = sink
        while s != source:
            path_flow = min(path_flow, residual_graph[parent[s]][s]['capacity'])
            s = parent[s]
        
        # Step 3: Update residual graph
        v = sink
        path_edges = []  # List to store the edges in the augmenting path
        while v != source:
            u = parent[v]
            residual_graph[u][v]['capacity'] -= path_flow
            if residual_graph.has_edge(v, u):
                residual_graph[v][u]['capacity'] += path_flow
            else:
                residual_graph.add_edge(v, u, capacity=path_flow)
            path_edges.append((u, v))  # Add edge to the augmenting path
            v = parent[v]
        
        flow += path_flow
        step += 1
        plot_graph(residual_graph, path_edges, step)  # Visualize residual graph after each update

    return flow, residual_graph

# BFS to find the augmenting path
def bfs(graph, source, sink):
    visited = set()
    parent = {source: None}
    queue = [source]
    
    while queue:
        u = queue.pop(0)
        
        if u == sink:
            return parent
        
        for v in graph[u]:
            if v not in visited and graph[u][v]['capacity'] > 0:
                queue.append(v)
                visited.add(v)
                parent[v] = u
    return None

# Visualize the graph using NetworkX and Matplotlib
def plot_graph(graph, path_edges=None, step=0):
    pos = nx.spring_layout(graph)
    plt.figure(figsize=(8, 6))

    # Draw nodes and edges with capacities
    nx.draw(graph, pos, with_labels=True, node_size=3000, node_color='lightblue', font_size=12, font_weight='bold')
    edge_labels = nx.get_edge_attributes(graph, 'capacity')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)

    # Highlight the path followed in each step with different colors
    if path_edges:
        path_color = plt.cm.viridis(step / 10)  # Use a color scale based on the step
        nx.draw_networkx_edges(graph, pos, edgelist=path_edges, width=3, edge_color=[path_color], alpha=0.7)

    plt.title(f"Flow Network - Step {step}")
    plt.show(block=False)  # Show the plot without blocking the rest of the code

# GUI to get inputs and visualize the algorithm
def visualize_ford_fulkerson():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Ask the user for input graph in the form of an adjacency matrix
    nodes = simpledialog.askstring("Input", "Enter the nodes (comma separated, e.g., A,B,C,D):").split(',')
    edges_input = simpledialog.askstring("Input", "Enter the edges with capacities (e.g., A-B-10, B-C-5, C-D-10):")

    # Create an empty directed graph
    graph = nx.DiGraph()

    # Add nodes
    for node in nodes:
        graph.add_node(node.strip())
    
    # Add edges with capacities
    edges = edges_input.split(',')
    for edge in edges:
        u, v, cap = edge.split('-')
        graph.add_edge(u.strip(), v.strip(), capacity=int(cap))

    # Ask for source and sink
    source = simpledialog.askstring("Input", "Enter the source node:")
    sink = simpledialog.askstring("Input", "Enter the sink node:")

    # Visualize the initial graph
    plot_graph(graph)

    # Run Ford-Fulkerson Algorithm
    max_flow, residual_graph = ford_fulkerson(graph, source, sink)
    
    # Display the result in a new window with Tkinter
    result_window = tk.Toplevel(root)
    result_window.title("Maximum Flow Result")
    
    result_label = tk.Label(result_window, text=f"Maximum Flow: {max_flow}", font=("Helvetica", 14))
    result_label.pack(pady=20)

    # Visualize the final residual graph
    plot_graph(residual_graph)

    root.mainloop()


if __name__ == "__main__":
    visualize_ford_fulkerson()
