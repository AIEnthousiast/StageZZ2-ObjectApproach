from Instances import Node, Edge
from dataclasses import dataclass,field
from collections import defaultdict
import functools
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from abc import ABC

import heapq




@dataclass
class SNOPSolutionBase(ABC):

   
    _edges : set[Edge]
    _adjancy_in : dict[Node:set[Node]] = field(default_factory= lambda : defaultdict(lambda : set()) , init=False)
    _adjancy_out : dict[Node:set[Node]] = field(default_factory= lambda : defaultdict(lambda : set()), init=False)
    _nodes : set[Node] = field(default_factory= lambda : set(),init=False)
    __nodes_pos : dict[str:tuple[int,int]] = field(default_factory= lambda : defaultdict(lambda : None), init=False)
    __G : nx.Graph = field(init=False)
    


    def __post_init__(self):
        for edge in self._edges:
            self._adjancy_out[edge.endpoint_1].add(edge.endpoint_2)
            self._adjancy_in[edge.endpoint_2].add(edge.endpoint_1)
            self._nodes.add(edge.endpoint_1)
            self._nodes.add(edge.endpoint_2)
        self._edges = set(self._edges)
        self.__G = None
        

    def get_nodes(self) -> set[Node]:
        return sorted(self._nodes,key= lambda x: x.label)
    
    def get_edges(self) -> set[Edge]:
        return sorted(self._edges.copy(),key=lambda x : x.endpoint_1.label+x.endpoint_2.label)

    @functools.cached_property
    def number_of_nodes(self):
        return len(self._nodes)

    @property
    def _map_nodes_to_edge(self) -> dict[tuple[Node,Node]:int]:
        return {(edge.endpoint_1,edge.endpoint_2):edge for edge in self._edges}
    

    def get_trial_value(self) -> int:
        ...
   
    
    @functools.cached_property
    def value(self) -> int:
        ...
    
    def __dfs(self, visited : set[Node],starting_node : Node) -> Node:
        if starting_node not in visited:
            visited.add(starting_node)
            for neighbour in self._adjancy_out[starting_node]:
                self.__dfs(visited, neighbour)


    @functools.cached_property
    def feasibility(self) -> bool:
        node = list(self._nodes)[0]
        visited = set()
        self.__dfs(visited,node)
        if len(visited) == self.number_of_nodes:
            self._adjancy_in,self._adjancy_out = self._adjancy_out,self._adjancy_in
            visited = set()
            self.__dfs(visited,node)
        self._adjancy_in,self._adjancy_out = self._adjancy_out,self._adjancy_in
        return len(visited) == self.number_of_nodes
    

   
    def show(self) -> None:
        if self.__G is None:
            self.__G = nx.MultiDiGraph()
            for edge in self._edges:
                self.__G.add_edge(edge.endpoint_1.label,edge.endpoint_2.label,color=edge.color)
            self.__nodes_pos = {node.label :  node.position for node in self._nodes}

        colors = [self.__G[u][v][0]['color'] for u,v in self.__G.edges()]
        nx.draw(self.__G,with_labels=True,pos=self.__nodes_pos,edge_color=colors)
        plt.show()

    
    
    def cycles(self) -> set[tuple[Edge]]:
        def to_string_cycle(cycle):
            s = cycle[0].endpoint_1.label
            for edge in cycle:
                s += edge.endpoint_2.label
            return s
        cycles = set()

        visited = defaultdict(lambda: False)
        dummy_node = Node("",(0,0))
        for node in self._nodes:
            self.__dfs_cycle( node, node, visited, [Edge(dummy_node,node)], cycles)


        return sorted(cycles,key= lambda c: to_string_cycle(c))
        
    """@functools.cached_property
    def value(self):
        return np.sum((self.dijkstra(i,j) for i in self.__nodes for j in self.__nodes if i != j))
"""

    def get_minimum_paths(self):
        paths = {}

        for start in self._nodes:
            paths.update(self.dijkstra(start))
        return paths

    def dijkstra(self, start):
        # Initialize distances and priority queue
        distances = {node: float('infinity') for node in self._nodes}
        distances[start] = 0
        priority_queue = [(0, start)]
        predecessors = defaultdict(lambda : None)
        paths = {start:(0,[])}
        
        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)
            
            
            if current_distance > distances[current_node]:
                continue
            
            for neighbor in self._adjancy_out[current_node]:
                distance = current_distance + self._map_nodes_to_edge[(current_node,neighbor)].cost
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    predecessors[neighbor] = current_node
                    paths[neighbor] = (distance,paths[current_node][1] + [self._map_nodes_to_edge[(current_node,neighbor)]])
                    heapq.heappush(priority_queue, (distance, neighbor))
        

        return {(start,u):v for (u,v) in paths.items()} 

    def __dfs_cycle(self, start: Node, current : Node, visited : dict[Node:bool], path: list[Edge], cycles: set[tuple[Edge]]):
        visited[current] = True
    
        if current != start:
            path.append(self._map_nodes_to_edge[(path[-1].endpoint_2,current)])

        for neighbor in self._adjancy_out[current]:
            if neighbor == start:
                tpath = path.copy()
                tpath.append(self._map_nodes_to_edge[(current,start)])
                tpath.pop(0)
                tpath = tuple(tpath)
                cycles.add(tpath)
            elif not visited[neighbor]:
                self.__dfs_cycle(start, neighbor, visited, path, cycles)

        path.pop()
        visited[current] = False
        
    def _get_involved_edges(self,s):
        return [e for e in self._edges if e.endpoint_1 == s or e.endpoint_2 == s]
    

    def accept_solution(self):
        ...

    def deny_solution(self) :
        ...


    def get_one_edge_reversal_neighbour(self,edge : Edge):
       ...
    

    def get_prox_node_edges_reversals_neighbour(self, s : Node):
        ...

    def get_path_reversal_neighbour(self, path : tuple[Edge]):
        ...



        
