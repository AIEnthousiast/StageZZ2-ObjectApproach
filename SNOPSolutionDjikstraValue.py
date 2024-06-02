from Instances import Node, Edge
from SNOPSolutionBase import SNOPSolutionBase
from dataclasses import dataclass,field
from collections import defaultdict

import functools
import numpy as np
from multiprocessing import Pool
import heapq



@dataclass
class SNOPSOlutionDjikstraValue(SNOPSolutionBase):
    
    __last_solution : SNOPSolutionBase = field(default=None,init=False)
    _nodes_list : list[Node] = field(init=False)
    _node_to_number : dict[Node:int] = field(init=False)


    def __post_init__(self):
        super().__post_init__()
        self._nodes_list = list(self._nodes)
        self._node_to_number = {n:i for i,n in enumerate(self._nodes_list)}



    @functools.cached_property
    def number_of_nodes(self):
        return len(self._nodes)


        
    def accept_solution(self) -> SNOPSolutionBase:
        return self.__last_solution
    
    def deny_solution(self) -> SNOPSolutionBase:
        self.__last_solution = None
        return self
    
    @property
    def value(self):
        return np.sum([self.minimum_distances_from(i) for i in range(self.number_of_nodes)])
        """adj_out = defaultdict(lambda:[])
        costs = {}
        for edge in self._edges:            
            adj_out[self._node_to_number[edge.endpoint_1]].append(self._node_to_number[edge.endpoint_2])
            costs[(self._node_to_number[edge.endpoint_1],self._node_to_number[edge.endpoint_2])] = edge.cost

        adj_out = dict(adj_out)
        n = self.number_of_nodes
        args = [(n,adj_out,costs,i) for i in range(self.number_of_nodes)]
        with Pool(processes=4) as pool:

            #vf = functools.partial(minimum_distances_from,N=self.number_of_nodes,adjancy_out=adj_out,costs=costs)
            results = pool.imap_unordered(minimum_distances_from,args,chunksize=self.number_of_nodes//4)
            for result in results:
                value += result
        return value
"""
    def minimum_distances_from(self,start_index):
        # Initialize distances and priority queue
        start = self._nodes_list[start_index]
        distances = {node: float('infinity') for node in self._nodes}
        distances[start] = 0
        priority_queue = [(0, start)]
        
        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)
            
            
            if current_distance > distances[current_node]:
                continue
            
            for neighbor in self._adjancy_out[current_node]:
                distance = current_distance + self._map_nodes_to_edge[(current_node,neighbor)].cost
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    heapq.heappush(priority_queue, (distance, neighbor))
        

        return np.sum(np.array(list(distances.values())))

        """

    def dijkstra(self, start, end):
        # Initialize distances and priority queue
        distances = {node: float('infinity') for node in self._nodes}
        distances[start] = 0
        priority_queue = [(0, start)]
        
        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)
            
            # Early exit if we reach the end node
            if current_node == end:
                return current_distance
            
            if current_distance > distances[current_node]:
                continue
            
            for neighbor in self._adjancy_out[current_node]:
                distance = current_distance + self._map_nodes_to_edge[(current_node,neighbor)].cost
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    heapq.heappush(priority_queue, (distance, neighbor))
        
        return float('infinity')  # If there's no path to the end node"""


    
    def get_trial_value(self) -> int:
        return self.value
    
    def get_one_edge_reversal_neighbour(self,edge : Edge):
        neigbhour_edges = self._edges.copy()
        new_edge = Edge(edge.endpoint_2,edge.endpoint_1,edge.cost)
        neigbhour_edges.remove(edge)
        neigbhour_edges.add(new_edge)

        
        self.__last_solution = SNOPSOlutionDjikstraValue(neigbhour_edges)
        if  not self.__last_solution.feasibility:
            self.__last_solution = None

        return self.__last_solution
    

    def get_prox_node_edges_reversals_neighbour(self, s : Node):
        neigbhour_edges = self._edges.copy()
        for edge in self._get_involved_edges(s):
            neigbhour_edges.remove(edge)
            neigbhour_edges.add(Edge(edge.endpoint_2,edge.endpoint_1,edge.cost))
        
        self.__last_solution = SNOPSOlutionDjikstraValue(neigbhour_edges)
        if  not self.__last_solution.feasibility:
            self.__last_solution = None

        return self.__last_solution

    def get_path_reversal_neighbour(self, path : tuple[Edge],check : bool=False):
        neigbhour_edges = self._edges.copy()
        for edge in path:
            neigbhour_edges.remove(edge)
            neigbhour_edges.add(Edge(edge.endpoint_2,edge.endpoint_1,edge.cost))
        self.__last_solution = SNOPSOlutionDjikstraValue(neigbhour_edges)
        if check and not self.__last_solution.feasibility:
            self.__last_solution = None
        return self.__last_solution
    
    




def minimum_distances_from_wrapper(N,adjancy_out,costs):

    def minimum_distances_from(start):
        distances = {i: float('infinity') for i in range(N)}
        distances[start] = 0
        priority_queue = [(0, start)]
        predecessors = defaultdict(lambda : None)
        
        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)
            
            
            if current_distance > distances[current_node]:
                continue
            
            for neighbor in adjancy_out[current_node]:
                distance = current_distance + costs[(current_node,neighbor)]
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    predecessors[neighbor] = current_node
                    heapq.heappush(priority_queue, (distance, neighbor))
        

        return np.sum(np.array(list(distances.values())))

    return minimum_distances_from


        
def minimum_distances_from(tup):
    N,adjancy_out,costs,start = tup
    distances = {i: float('infinity') for i in range(N)}
    distances[start] = 0
    priority_queue = [(0, start)]
    predecessors = defaultdict(lambda : None)
    
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        
        
        if current_distance > distances[current_node]:
            continue
        
        for neighbor in adjancy_out[current_node]:
            distance = current_distance + costs[(current_node,neighbor)]
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))
    

    return np.sum(np.array(list(distances.values())))
