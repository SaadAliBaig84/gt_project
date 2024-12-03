import tkinter as tk
from tkinter import simpledialog
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

snapshots = []  # Store graphs for each step
current_step = 0  # Track the current step being displayed

def ford_fulkerson(graph, source, sink):
    flow = 0
    residual_graph = graph.copy()
    step = 0

    while True:
        parent = dfs(residual_graph, source, sink)
        if not parent:
            break

        path_flow = float('Inf')
        s = sink
        while s != source:
            path_flow = min(path_flow, residual_graph[parent[s]][s]['capacity'])
            s = parent[s]

        v = sink
        path_edges = []
        while v != source:
            u = parent[v]
            residual_graph[u][v]['capacity'] -= path_flow
            if residual_graph.has_edge(v, u):
                residual_graph[v][u]['capacity'] += path_flow
            else:
                residual_graph.add_edge(v, u, capacity=path_flow)
            path_edges.append((u, v))
            v = parent[v]

        flow += path_flow
        step += 1
        snapshots.append((residual_graph.copy(), path_edges, step))  # Save snapshot

    return flow, residual_graph

def dfs(graph, source, sink):
    visited = set()
    parent = {source: None}
    stack = [source]  # Use a stack for DFS
    
    while stack:
        u = stack.pop()
        if u == sink:
            return parent
        for v in graph[u]:
            if v not in visited and graph[u][v]['capacity'] > 0:
                stack.append(v)
                visited.add(v)
                parent[v] = u
    return None


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

def plot_graph(graph, path_edges=None, step=0):
    plt.clf()
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, node_size=3000, node_color='lightblue', font_size=12, font_weight='bold')
    edge_labels = nx.get_edge_attributes(graph, 'capacity')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)

    if path_edges:
        path_color = plt.cm.viridis(step / 10)
        nx.draw_networkx_edges(graph, pos, edgelist=path_edges, width=3, edge_color=[path_color], alpha=0.7)

    plt.title(f"Flow Network - Step {step}")

def next_graph(canvas, figure, result_label):
    global current_step
    if current_step < len(snapshots):
        graph, path_edges, step = snapshots[current_step]
        plot_graph(graph, path_edges, step)
        canvas.draw()
        current_step += 1
    else:
        result_label.config(text=f"Maximum Flow: {max_flow}")

def visualize_ford_fulkerson():
    global max_flow, current_step  # Declare current_step as global
    current_step = 0  # Initialize current_step
    
    root = tk.Tk()
    root.withdraw()

    nodes = simpledialog.askstring("Input", "Enter the nodes (comma separated, e.g., A,B,C,D):").split(',')
    edges_input = simpledialog.askstring("Input", "Enter the edges with capacities (e.g., A-B-10, B-C-5, C-D-10):")

    graph = nx.DiGraph()
    for node in nodes:
        graph.add_node(node.strip())
    
    edges = edges_input.split(',')
    for edge in edges:
        u, v, cap = edge.split('-')
        graph.add_edge(u.strip(), v.strip(), capacity=int(cap))

    source = simpledialog.askstring("Input", "Enter the source node:")
    sink = simpledialog.askstring("Input", "Enter the sink node:")

    max_flow, _ = ford_fulkerson(graph, source, sink)

    result_window = tk.Toplevel(root)
    result_window.title("Ford-Fulkerson Visualization")

    figure = plt.figure(figsize=(8, 6))
    canvas = FigureCanvasTkAgg(figure, result_window)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    result_label = tk.Label(result_window, text="", font=("Helvetica", 14))
    result_label.pack(pady=10)

    next_button = tk.Button(result_window, text="Next", command=lambda: next_graph(canvas, figure, result_label))
    next_button.pack(pady=10)

    plot_graph(*snapshots[current_step])  # Show the initial graph
    canvas.draw()
    current_step += 1

    root.mainloop()


if __name__ == "__main__":
    visualize_ford_fulkerson()
