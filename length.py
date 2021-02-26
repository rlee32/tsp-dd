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

def read_tour(path):
    """Reads a TSPLIB-formatted TSP tour file. """
    tour = []
    with open(path, "r") as f:
        for line in f:
            if "TOUR_SECTION" in line:
                break
        for line in f:
            line = line.strip()
            if "-1" in line or "EOF" in line or not line:
                break
            fields = line.strip().split()
            tour.append((int(fields[0])))
    return tour

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
def tour_cost(instance, tour):
    prev = tour[-1]
    cost = 0
    for i in tour:
        cost += edge_cost(instance, (prev, i))
        prev = i
    return cost

import sys

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("arguments: tsp_instance_file tour_file")
        sys.exit()
    instance_path = sys.argv[1]
    instance = read_instance(instance_path)
    tour_file = sys.argv[2]
    tour = read_tour(tour_file)

    cost = tour_cost(tour)
    print(f'cost: {cost}')
