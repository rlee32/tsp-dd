#!/usr/bin/env python3

# Outputs a the difference between two tours as a list of disjoint k-moves (JSON formatted).

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

def edge(i, j, set_id):
    return (min(i, j), max(i, j))

def edge_set(tour, set_id):
    edges = set()
    j = tour[-1]
    for i in tour:
        edges.add(edge(i, j, set_id))
        j = i
    return edges

def distance(instance, i, j):
    dx = instance[i][0] - instance[j][0]
    dy = instance[i][1] - instance[j][1]
    return round((dx ** 2 + dy ** 2) ** 0.5)
def edge_cost(instance, edge):
    return distance(instance, edge[0], edge[1])
def edge_cost_sum(instance, edges):
    total = 0
    for e in edges:
        total += edge_cost(intance, e)
    return total

def map_edges(m, edges):
    for e in edges:
        for i in e:
            if i not in m:
                m[i] = set()
            m[i].add(e)

def extract_island(m):
    """Extracts a disjoint set of edges from the provided edge map."""
    if len(m) == 0:
        return
    edges = set()
    for i in m:
        visit_set = set()
        for e in m[i]:
            edges.add(e)
            visit_set.add(e[0])
            visit_set.add(e[1])
        del m[i]
        visit_set.remove(i)
        while visit_set:
            for j in list(visit_set):
                if j in m:
                    for e in m[j]:
                        edges.add(e)
                        visit_set.add(e[0])
                        visit_set.add(e[1])
                    del m[j]
                visit_set.remove(j)
        break
    return edges

def split_difference(first_exclusive, second_exclusive):
    """splits the edges that are the difference between two tours into disjoint k-moves."""
    edge_map = {}
    map_edges(edge_map, first_exclusive)
    map_edges(edge_map, second_exclusive)
    edge_sum = 0
    for j in edge_map:
        edge_sum += len(edge_map[j])
    print(f'total difference is a {len(first_exclusive)}-opt move.')
    assert(edge_sum == 4 * len(first_exclusive))

    edges = extract_island(edge_map)
    islands = []
    edge_count = 0
    while edges:
        kmove = [[], []]
        for e in edges:
            if e in first_exclusive:
                kmove[0].append(e)
            else:
                assert(e in second_exclusive)
                kmove[1].append(e)
            edge_count += 1
        assert(len(kmove[0]) == len(kmove[1]))
        islands.append(kmove)
        edges = extract_island(edge_map)
    assert(edge_count == len(first_exclusive) + len(second_exclusive))
    return islands


import sys
import json

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("arguments: first_tour_path second_tour_path optional_output_path")
    first_tour_path = sys.argv[1]
    second_tour_path = sys.argv[2]
    first_tour = read_tour(first_tour_path)
    second_tour = read_tour(second_tour_path)

    first_edges = edge_set(first_tour, 0)
    second_edges = edge_set(second_tour, 1)

    first_exclusive = set()
    for e in first_edges:
        if e not in second_edges:
            first_exclusive.add(e)

    second_exclusive = set()
    for e in second_edges:
        if e not in first_edges:
            second_exclusive.add(e)

    islands = split_difference(first_exclusive, second_exclusive)
    print(f'split the total k-move into {len(islands)} disjoint k-moves.')
    print(f'k-opt for each island: {[len(x[0]) for x in islands]}')

    if len(sys.argv) > 3:
        json.dump(islands, open(sys.argv[3], 'w'))
    else:
        print(islands)
