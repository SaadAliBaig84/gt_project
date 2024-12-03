import tkinter as tk
from tkinter import simpledialog, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

snapshots = []  # Store graphs for each step
current_step = 0  # Track the current step being displayed
layout_pos = None  # Global variable for layout positions


def ford_fulkerson(graph, source, sink):
    flow = 0
    residual_graph = graph.copy()
    step = 0
    flows = {edge: 0 for edge in graph.edges}  # Initialize flow for each edge

    while True:
        parent = dfs(residual_graph, source, sink)
        if not parent:
            break

        # Find the bottleneck (minimum capacity along the path)
        path_flow = float('Inf')
        s = sink
        path_edges = []
        while s != source:
            path_flow = min(path_flow, residual_graph[parent[s]][s]['capacity'] - flows[(parent[s], s)])
            path_edges.append((parent[s], s))
            s = parent[s]

        # Update flow along the path and reverse flow in the residual graph
        for u, v in path_edges:
            flows[(u, v)] += path_flow
            if (v, u) not in flows:
                flows[(v, u)] = 0
            flows[(v, u)] -= path_flow

        flow += path_flow
        step += 1
        snapshots.append((residual_graph.copy(), flows.copy(), path_edges, step))

    return flow, residual_graph


def dfs(graph, source, sink):
    visited = set()
    parent = {source: None}
    stack = [source]  # Use a stack for DFS

    while stack:
        u = stack.pop()
        for v in graph[u]:
            if v not in visited and graph[u][v]['capacity'] > 0:
                visited.add(v)
                stack.append(v)
                parent[v] = u
                if v == sink:
                    return parent
    return None


def plot_graph(graph, flows, path_edges=None, step=0):
    plt.clf()
    global layout_pos  # Use the same layout for all steps

    # Draw nodes and labels
    nx.draw(graph, layout_pos, with_labels=True, node_size=3000, node_color='lightblue', font_size=12, font_weight='bold')

    # Display flow/capacity on each edge
    edge_labels = {edge: f"{flows.get(edge, 0)}/{graph.edges[edge]['capacity']}" for edge in graph.edges}
    nx.draw_networkx_edge_labels(graph, layout_pos, edge_labels=edge_labels, font_size=10)

    # Highlight the current augmenting path (if any)
    if path_edges:
        nx.draw_networkx_edges(graph, layout_pos, edgelist=path_edges, width=3, edge_color='red', alpha=0.7)

    plt.title(f"Flow Network - Step {step}")


def next_graph(canvas, figure, result_label):
    global current_step
    if current_step < len(snapshots):
        graph, flows, path_edges, step = snapshots[current_step]
        plot_graph(graph, flows, path_edges, step)
        canvas.draw()
        current_step += 1
    else:
        result_label.config(text=f"Maximum Flow: {max_flow}")


def visualize_ford_fulkerson():
    global max_flow, current_step, source, layout_pos
    current_step = 0

    root = tk.Tk()
    root.withdraw()

    try:
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

        layout_pos = nx.spring_layout(graph)  # Precompute the layout and store it

        max_flow, _ = ford_fulkerson(graph, source, sink)

        # Create a new window for visualization
        result_window = tk.Toplevel()
        result_window.title("Ford-Fulkerson Visualization")

        figure = plt.figure(figsize=(8, 6))
        canvas = FigureCanvasTkAgg(figure, result_window)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        result_label = tk.Label(result_window, text="", font=("Helvetica", 14))
        result_label.pack(pady=10)

        next_button = tk.Button(result_window, text="Next", command=lambda: next_graph(canvas, figure, result_label))
        next_button.pack(pady=10)

        plot_graph(*snapshots[current_step][:3])
        canvas.draw()
        current_step += 1

        result_window.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        root.destroy()


if __name__ == "__main__":
    visualize_ford_fulkerson()
