import sys
import re
import argparse
from typing import List, Dict, Tuple

class NodeError(Exception):
    pass

class EdgeException(Exception):
    pass

class Edge:
    def __init__(self, start_node: str, end_node: str, weight: float):
        self.start_node = start_node
        self.end_node = end_node
        self.weight = weight

    def to_graphviz_string(self) -> str:
        return f'{self.start_node} -> {self.end_node} [ label="{round(self.weight, 2)}" ];'

    def __str__(self) -> str:
        return f'{self.start_node} -> {self.end_node}: {round(self.weight, 2)}'

    def normalize(self):
        if self.weight < 0:
            self.weight *= -1
            self.start_node, self.end_node = self.end_node, self.start_node

def print_edges(edges: List[Edge], graphviz: bool):
    if graphviz:
        print("digraph G {")
    for edge in edges:
        edge.normalize()
        print(edge.to_graphviz_string() if graphviz else str(edge))
    if graphviz:
        print("}")

def add_weight(weights: Dict[str, float], node_name: str, weight_delta: float):
    weights[node_name] = weights.get(node_name, 0) + weight_delta

def sort_weights(weights: Dict[str, float]) -> List[Tuple[float, str]]:
    return sorted([(value, key) for key, value in weights.items()])

def get_node_weights(edges: List[Edge]) -> Dict[str, float]:
    weights = {}
    for edge in edges:
        add_weight(weights, edge.end_node, edge.weight)
        add_weight(weights, edge.start_node, -edge.weight)
    return weights

def find_greater_weight(weight_comp: float, weights: Dict[str, float]) -> str:
    for node, weight in weights.items():
        if weight >= weight_comp:
            return node
    return None

def weights_to_edges(sorted_weights: List[Tuple[float, str]], weights: Dict[str, float]) -> List[Edge]:
    edges = []
    for i in range(len(sorted_weights) - 1):
        current_node = sorted_weights[i][1]
        current_weight = weights[current_node]
        if current_weight == 0:
            continue
        
        transact = abs(current_weight)
        target = find_greater_weight(transact, weights)
        if target is None:
            target = sorted_weights[i + 1][1]
        edges.append(Edge(current_node, target, transact))
        weights[target] += current_weight
    return edges

def remove_zero_weights(weights: List[Tuple[float, str]]):
    return [w for w in weights if w[0] != 0]

def split_star_nodes(edges: List[Edge], empty_nodes: List[str], verbose: bool) -> List[Edge]:
    nodes = list(set(empty_nodes + [edge.start_node for edge in edges if edge.start_node != "*"]
                                  + [edge.end_node for edge in edges if edge.end_node != "*"]))
    if verbose:
        print(f"Found these {len(nodes)} unique nodes: {nodes}")

    new_edges = []
    for edge in edges:
        if edge.start_node == "*":
            new_edges.extend(
                Edge(node, edge.end_node, edge.weight / len(nodes)) 
                for node in nodes if node != edge.end_node
            )
        elif edge.end_node == "*":
            new_edges.extend(
                Edge(edge.start_node, node, edge.weight / len(nodes)) 
                for node in nodes if node != edge.start_node
            )
        else:
            new_edges.append(edge)
    return new_edges

SEARCH_COMMENT = re.compile("^(#| *$)")
SEARCH_EDGE = re.compile("(\w+|\*) *-> *(\w+|\*): *([0-9]+(\.[0-9]+)?)")
SEARCH_NODE = re.compile("^(\w+)$")

def parse_edge(line: str) -> Edge:
    m = SEARCH_EDGE.match(line)
    if m:
        start_node, end_node, weight = m.groups()[:3]
        return Edge(start_node, end_node, float(weight))
    raise EdgeException("Invalid input line")

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-g", "--graphviz", action='store_true')
    argparser.add_argument("-v", "--verbose", action='store_true')
    argparser.add_argument("filename", nargs='?')
    args = argparser.parse_args()

    edges = []
    empty_nodes = []

    with open(args.filename) if args.filename else sys.stdin as input_file:
        for i, line in enumerate(input_file, 1):
            try:
                edges.append(parse_edge(line))
            except EdgeException:
                if SEARCH_NODE.match(line):
                    empty_nodes.append(line.strip())
                elif not SEARCH_COMMENT.match(line):
                    print(f"Invalid input on line {i}: {line.strip()}", file=sys.stderr)
                    sys.exit(1)

    edges = split_star_nodes(edges, empty_nodes, args.verbose)
    weights = get_node_weights(edges)
    sorted_weights = sort_weights(weights)
    sorted_weights = remove_zero_weights(sorted_weights)

    # Optionally perform a consistency check if verbose
    if args.verbose and sorted_weights:
        assert round(sum(weight for weight, _ in sorted_weights), 10) == 0.0
        print("Node weights: ", sorted_weights)

    edges = weights_to_edges(sorted_weights, weights)

    if args.verbose and edges:
        total_money_transacted = sum(edge.weight for edge in edges)
        print(f"Total money transacted: {total_money_transacted}")
    
    print_edges(edges, args.graphviz)