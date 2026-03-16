import heapq
import random
import tkinter as tk
from tkinter import ttk

graph = {
    "A": {"B": 4, "C": 2},
    "B": {"A": 4, "D": 5, "G": 7},
    "C": {"A": 2, "D": 6, "E": 10},
    "D": {"B": 5, "C": 6, "F": 6},
    "E": {"C": 10, "F": 5, "H": 1},
    "F": {"D": 6, "E": 5, "I": 1},
    "G": {"B": 7, "H": 6},
    "H": {"G": 6, "E": 1, "I": 1},
    "I": {"H": 1, "F": 1}
}

positions = {
    "A": (80, 250), "B": (200, 120), "C": (200, 380),
    "D": (350, 200), "E": (350, 420), "F": (500, 300),
    "G": (350, 50), "H": (500, 150), "I": (620, 250)
}

def dijkstra(start, goal):
    queue = [(0, start, [])]
    visited = set()

    while queue:
        cost, node, path = heapq.heappop(queue)
        if node in visited:
            continue
        visited.add(node)
        path = path + [node]

        if node == goal:
            return cost, path

        for n, w in graph[node].items():
            heapq.heappush(queue, (cost + w, n, path))

    return float("inf"), []

def calculate_utility(base_time):
    normal = base_time
    heavy = base_time * random.uniform(1.2, 1.6)
    expected = 0.6 * normal + 0.4 * heavy
    utility = -(0.7 * expected + 0.3 * heavy)
    return utility, expected

root = tk.Tk()
root.title("GPS Navigation Agent")
root.geometry("850x650")

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Start:").grid(row=0, column=0)
start_var = tk.StringVar()
ttk.Combobox(frame, textvariable=start_var,
            values=list(graph.keys()),
            state="readonly").grid(row=0, column=1)

tk.Label(frame, text="Destination:").grid(row=0, column=2)
goal_var = tk.StringVar()
ttk.Combobox(frame, textvariable=goal_var,
            values=list(graph.keys()),
            state="readonly").grid(row=0, column=3)

canvas = tk.Canvas(root, width=800, height=500, bg="white")
canvas.pack(pady=20)

result_label = tk.Label(root, text="", font=("Arial", 11))
result_label.pack()


def draw_graph(path=None):
    canvas.delete("all")
    drawn = set()

    for node in graph:
        for neighbor, weight in graph[node].items():
            if (neighbor, node) in drawn:
                continue
            drawn.add((node, neighbor))

            x1, y1 = positions[node]
            x2, y2 = positions[neighbor]

            color, width = "black", 2
            if path and any(
                {path[i], path[i+1]} == {node, neighbor}
                for i in range(len(path)-1)
            ):
                color, width = "red", 4

            canvas.create_line(x1, y1, x2, y2,
                            fill=color, width=width)

            canvas.create_text((x1+x2)/2, (y1+y2)/2 - 10,
                            text=str(weight),
                            fill="blue",
                            font=("Arial", 9, "bold"))
            
    for node, (x, y) in positions.items():
        canvas.create_oval(x-20, y-20, x+20, y+20,
                        fill="lightgreen")
        canvas.create_text(x, y,
                        text=node,
                        font=("Arial", 12, "bold"))

def run():
    start, goal = start_var.get(), goal_var.get()

    if not start or not goal or start == goal:
        result_label.config(text="Select valid start and destination.")
        return

    cost, path = dijkstra(start, goal)
    if not path:
        result_label.config(text="No route found.")
        return

    utility, expected = calculate_utility(cost)
    draw_graph(path)

    result_label.config(
        text=f"Path: {' -> '.join(path)} | "
            f"Cost: {cost} | "
            f"Expected: {round(expected,2)} | "
            f"Utility: {round(utility,2)}"
    )
    
ttk.Button(frame, text="Find Route", command=run)\
    .grid(row=0, column=4, padx=10)

draw_graph()
root.mainloop()