from Instances import Node, Edge, InvalidInstanceError
from dataclasses import dataclass,field
from collections import defaultdict
import gurobipy as gp
from gurobipy import GRB
import functools
import networkx as nx
import matplotlib.pyplot as plt
import random 
import numpy as np
from timeit import default_timer as timer
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
        return self._nodes
    
    def get_edges(self) -> set[Edge]:
        return self._edges.copy()

    @functools.cached_property
    def number_of_nodes(self):
        return len(self._nodes)

    @property
    def __map_nodes_to_edge(self) -> dict[tuple[Node,Node]:int]:
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
        cycles = set()

        visited = defaultdict(lambda: False)
        dummy_node = Node("",(0,0))
        for node in self._nodes:
            self.__dfs_cycle( node, node, visited, [Edge(dummy_node,node)], cycles)

        return cycles
        


    def __dfs_cycle(self, start: Node, current : Node, visited : dict[Node:bool], path: list[Edge], cycles: set[tuple[Edge]]):
        visited[current] = True
    
        if current != start:
            path.append(self.__map_nodes_to_edge[(path[-1].endpoint_2,current)])

        for neighbor in self._adjancy_out[current]:
            if neighbor == start:
                tpath = path.copy()
                tpath.append(self.__map_nodes_to_edge[(current,start)])
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



        
