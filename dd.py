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

def map_edges(m, edges):
    for e in edges:
        for i in e:
            if i not in m:
                m[i] = set()
            m[i].add(e)
            assert(len(m[i]) in (1, 2, 3, 4))

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

def test_junction(m, junction):
    """Tests junction to see if associated edges are disjoint, trivially disjoint, or indeterminate (adjacent to other junctions).
    If disjoint or trivially disjoint, then disjoint edges are returned.
    If indeterminate, None is returned.
    """
    disjoint_set = None
    assert(len(m[junction]) == 4)
    for e in m[junction]:
        assert(junction in e)
        # walk edges.
        visited_edges = set() # this set should be a 1D walk.
        visited_edges.add(e)
        i = e[0] if e[1] == junction else e[1]
        if len(m[i]) == 4:
            # skip the case of adjacent junctions for now.
            continue
        assert(len(m[i]) == 2)
        while True:
            mm = list(m[i])
            next_edge = mm[0] if mm[1] in visited_edges else mm[1]
            visited_edges.add(next_edge)
            i = next_edge[0] if next_edge[1] == i else next_edge[1]
            if i == junction:
                disjoint_set = visited_edges
            if len(m[i]) == 4:
                # just stop at junctions.
                break
        if disjoint_set is not None:
            break
    return disjoint_set

def split_island(move):
    """Attempts to split a touching set of edges into disjoint sets at 'junctions'."""
    if len(move[0]) < 4:
        # cannot split an island that is less than 4-opt.
        return [move]
    m = {}
    map_edges(m, move[0])
    map_edges(m, move[1])
    splits = []
    for i in m:
        if len(m[i]) == 4:
            split = test_junction(m, i)
            if split is None:
                continue
            if len(split) % 2 == 0:
                splits.append(split)
    if not splits:
        return [move]
    move[0] = set(move[0])
    move[1] = set(move[1])
    moves = []
    for split in splits:
        new_move = [[], []]
        for e in split:
            if e in move[0]:
                new_move[0].append(e)
                move[0].remove(e)
            else:
                assert(e in move[1])
                new_move[1].append(e)
                move[1].remove(e)
        moves.append(new_move)
    move[0] = list(move[0])
    move[1] = list(move[1])
    moves.append(move)
    return moves

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

    presplit_islands = split_difference(first_exclusive, second_exclusive)
    islands = []
    for island in presplit_islands:
        islands += split_island(island)

    print(f'split the total k-move into {len(islands)} disjoint k-moves.')
    print(f'k-opt for each island: {[len(x[0]) for x in islands]}')

    if len(sys.argv) > 3:
        json.dump(islands, open(sys.argv[3], 'w'))
    else:
        print(islands)
