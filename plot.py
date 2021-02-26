#!/usr/bin/env python3

import json
from matplotlib import pyplot as plt

def read_instance(path):
    """Reads a TSPLIB-formatted TSP instance (not tour) file. """
    coordinates = []
    with open(path, "r") as f:
        for line in f:
            if "NODE_COORD_SECTION" in line:
                break
        for line in f:
            line = line.strip()
            if "EOF" in line or not line:
                break
            fields = line.strip().split()
            coordinates.append((float(fields[1]), float(fields[2])))
    return coordinates

def read_moves(path):
    """Reads a JSON file containing a list of two sets of edges, each representing disjoint k-moves. """
    return json.load(open(path, 'r'))

def plot_edges(instance, edges, linestyle):
    """instance is a list of coordinates read from TSPLIB-formatted file.
    edges is a list of 2-tuples representing edges. """
    for e in edges:
        c0 = instance[e[0] - 1]
        c1 = instance[e[1] - 1]
        plt.plot([c0[0], c1[0]], [c0[1], c1[1]], 'x' + linestyle)

def distance(instance, i, j):
    # i and j are index + 1.
    i -= 1
    j -= 1
    assert(i >= 0 and j >= 0)
    dx = instance[i][0] - instance[j][0]
    dy = instance[i][1] - instance[j][1]
    return round((dx ** 2 + dy ** 2) ** 0.5)
def edge_cost(instance, edge):
    return distance(instance, edge[0], edge[1])
def edge_cost_sum(instance, edges):
    total = 0
    for e in edges:
        total += edge_cost(instance, e)
    return total

class ColorSwatch:
    def __init__(self):
        self.wheel = 'rgbmk'
        self.index = 0
    def next(self):
        c = self.wheel[self.index]
        self.index += 1
        if self.index == len(self.wheel):
            self.index = 0
        return c

import sys

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("arguments: tsp_instance_file edge_file")
        sys.exit()
    instance_path = sys.argv[1]
    instance = read_instance(instance_path)
    edge_path = sys.argv[2]
    moves = read_moves(edge_path)

    colors = ColorSwatch()
    total_cost = 0
    total_k = 0
    costs = []
    for edges in moves:
        c = colors.next()
        plot_edges(instance, edges[0], f'{c}-')
        plot_edges(instance, edges[1], f'{c}:')
        cost = edge_cost_sum(instance, edges[0]) - edge_cost_sum(instance, edges[1])
        k = len(edges[0])
        costs.append((cost, k))
        total_cost += cost
        total_k += k
    costs.sort()
    for c in costs:
        print(f'cost, k-count: {c}')
    print(f'\ntotal k, cost: {total_k}, {total_cost}')
    plt.show()
