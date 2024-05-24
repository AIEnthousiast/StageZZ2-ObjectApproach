# -*- coding: utf-8 -*-

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
import copy
import heapq



@dataclass
class CarriableModel:
    
    __model : gp.Model
    __nodes : set[Node]
    __edges : set[Edge]
    __adjancy_in : dict[Node:set[Node]] = field(default_factory= lambda : defaultdict(lambda : set()))
    __adjancy_out : dict[Node:set[Node]] = field(default_factory= lambda : defaultdict(lambda : set()))
    __f : gp.tupledict = field(default_factory= lambda: set())
    __inverse_transformations : list[Edge] = field(default_factory= lambda : [],init=False)
    __last_value : int = field(default=0, init=False)
   
        

    @property
    def last_value(self):
        return self.__last_value

    
    
    def set_adjancy_in(self,adj_in):
        self.__adjancy_in = adj_in

    def set_adjancy_out(self,adj_out):
        self.__adjancy_out = adj_out

    def get_adjancy_in(self) -> dict[Node:list[Node]] :
        return copy.deepcopy(self.__adjancy_in)
    
    def get_adjancy_out(self) -> dict[Node:list[Node]] :
        return copy.deepcopy(self.__adjancy_out)
    

    def reset_transformations(self):
        self.__inverse_transformations = []

    def construct(self):
        f = {}
        number_of_nodes = len(self.__nodes)
        for s in self.__nodes:
            for edge in self.__edges:
                i,j = edge.endpoint_1, edge.endpoint_2
                f[s.label,i.label,j.label] = self.__model.addVar(0,number_of_nodes-1,name="f^%s_%s%s"%(s.label,i.label,j.label),vtype=GRB.CONTINUOUS)
        self.__model.update()

        objective = gp.quicksum(edge.cost*f[s.label,edge.endpoint_1.label,edge.endpoint_2.label] for edge in self.__edges for s in self.__nodes)
        self.__model.setObjective(objective,sense=GRB.MINIMIZE)
        
        for s in self.__nodes:
            
            self.__model.addConstr(gp.quicksum(f[s.label,s.label,i.label] for i in self.__adjancy_out[s]) == number_of_nodes - 1,name="OutFlow_%s"%(s.label))
            for i in self.__nodes:
                if i != s:
                    self.__model.addConstr(gp.quicksum(f[s.label,j.label,i.label] for j in self.__adjancy_in[i]) - gp.quicksum(f[s.label,i.label,j.label] for j in self.__adjancy_out[i]) == 1,
                                                        name="InFlow_%s_%s"%(s.label,i.label))

        self.__model.update()
        self.__f = f
    
    

    def get_edges(self):
        return self.__edges.copy()
    
   
    def alter_edges(self,edges: list[Edge]):
        for edge in edges:
            self.__edges.remove(edge)
            self.__edges.add(edge.inverse)
        

    def alter_adjancy_lists(self,edges : list[Edge]):
        for edge in edges:
            self.__adjancy_in[edge.endpoint_1].add(edge.endpoint_2)
            self.__adjancy_in[edge.endpoint_2].remove(edge.endpoint_1)
            self.__adjancy_out[edge.endpoint_1].remove(edge.endpoint_2)
            self.__adjancy_out[edge.endpoint_2].add(edge.endpoint_1)

            self.__edges.remove(edge)
            self.__edges.add(edge.inverse)

        #self.alter_edges(edges)


   
        

    def invert_edge_in_model(self, edges : list[Edge]):
        number_of_nodes = len(self.__nodes)
        

        involved_nodes = set()
        for edge in edges:
            involved_nodes.add(edge.endpoint_1)
            involved_nodes.add(edge.endpoint_2)

        
        self.__inverse_transformations = list(map(lambda e : e.inverse,edges))

        for edge in edges:
            #remove inflows 
            
            for s in self.__nodes:
                self.__model.remove(self.__model.getVarByName("f^%s_%s%s"%(s.label,edge.endpoint_1.label,edge.endpoint_2.label)))
                
                del  self.__f[s.label,edge.endpoint_1.label,edge.endpoint_2.label]
                self.__f[s.label,edge.endpoint_2.label,edge.endpoint_1.label] = self.__model.addVar(0,number_of_nodes-1,name="f^%s_%s%s"%(s.label,edge.endpoint_2.label,edge.endpoint_1.label),vtype=GRB.CONTINUOUS)
              


        for node in involved_nodes:     
            self.__model.remove(self.__model.getConstrByName("OutFlow_%s"%(node.label)))
            self.__model.addConstr(gp.quicksum(self.__f[node.label,node.label,i.label] for i in self.__adjancy_out[node]) == number_of_nodes - 1,name="OutFlow_%s"%(node.label))

            for s in self.__nodes:
                if s != node:
                    self.__model.remove(self.__model.getConstrByName("InFlow_%s_%s"%(s.label,node.label)))
                    self.__model.addConstr(gp.quicksum(self.__f[s.label,j.label,node.label] for j in self.__adjancy_in[node]) - gp.quicksum(self.__f[s.label,node.label,j.label] for j in self.__adjancy_out[node]) == 1,
                                                            name="InFlow_%s_%s"%(s.label,node.label))
            
            
        self.__model.update()

        objective = gp.quicksum(edge.cost*self.__f[s.label,edge.endpoint_1.label,edge.endpoint_2.label] for edge in self.__edges for s in self.__nodes)
        self.__model.setObjective(objective,sense=GRB.MINIMIZE)

    def optimize(self):
        self.__model.optimize()
        self.__last_value = self.__model.ObjBound


    def revert(self):
        inverse_transf = self.__inverse_transformations[::-1]
        self.alter_adjancy_lists(inverse_transf)
        self.invert_edge_in_model(list(inverse_transf))

        
        self.__inverse_transformations = []

    def get_involved_edges(self,s):
        return [e for e in self.__edges if e.endpoint_1 == s or e.endpoint_2 == s]
        

    @property
    def ObjBound(self):
        return self.__model.ObjBound
        

    def __dfs(self, visited : set[Node],starting_node : Node) -> Node:
        if starting_node not in visited:
            visited.add(starting_node)
            for neighbour in self.__adjancy_out[starting_node]:
                self.__dfs(visited, neighbour)

    @property 
    def feasibility(self):
        node = list(self.__nodes)[0]
        number_of_nodes = len(self.__nodes)
        visited = set()
        self.__dfs(visited,node)
        if len(visited) == number_of_nodes:
            self.__adjancy_in,self.__adjancy_out = self.__adjancy_out,self.__adjancy_in
            visited = set()
            self.__dfs(visited,node)
            self.__adjancy_in,self.__adjancy_out = self.__adjancy_out,self.__adjancy_in
        return len(visited) == number_of_nodes


@dataclass
class SNOPSolution:

   
    __edges : set[Edge]
    __model : CarriableModel = field(default=None)
    __value : int = field(default=None,init=False)
    __adjancy_in : dict[Node:set[Node]] = field(default_factory= lambda : defaultdict(lambda : set()) , init=False)
    __adjancy_out : dict[Node:set[Node]] = field(default_factory= lambda : defaultdict(lambda : set()), init=False)
    __nodes : set[Node] = field(default_factory= lambda : set(),init=False)
    __nodes_pos : dict[str:tuple[int,int]] = field(default_factory= lambda : defaultdict(lambda : None), init=False)
    __G : nx.Graph = field(init=False)
    


    def __post_init__(self):

        self.__edges = set(self.__edges)
        for edge in self.__edges:
            self.__adjancy_out[edge.endpoint_1].add(edge.endpoint_2)
            self.__adjancy_in[edge.endpoint_2].add(edge.endpoint_1)
            self.__nodes.add(edge.endpoint_1)
            self.__nodes.add(edge.endpoint_2)
        
        if self.__model == None:
            env = gp.Env(empty=True)
            env.setParam('OutputFlag', 0)
            env.start()
            model = gp.Model(env=env)
        
            self.__model = CarriableModel(model,self.__nodes,self.__edges.copy(),copy.deepcopy(self.__adjancy_in),copy.deepcopy(self.__adjancy_out))
            self.__model.construct()
            self.__value = self.get_model_value()
        self.__G = None
        

    def get_nodes(self) -> set[Node]:
        return self.__nodes
    
    def get_edges(self) -> set[Edge]:
        return self.__edges.copy()

    @functools.cached_property
    def number_of_nodes(self):
        return len(self.__nodes)

    @property
    def __map_nodes_to_edge(self) -> dict[tuple[Node,Node]:int]:
        return {(edge.endpoint_1,edge.endpoint_2):edge for edge in self.__edges}
    
    
    def get_model_value(self) -> int:
        """try:
            assert self.model_feasibility
        except AssertionError:
            raise InvalidInstanceError
        """
        self.__model.optimize()
        return self.__model.ObjBound

    
    @property
    def value(self) -> int:
        return self.__value



    def accept_solution(self):
        self.__edges = self.__model.get_edges()
        self.__adjancy_in = self.__model.get_adjancy_in()
        self.__adjancy_out = self.__model.get_adjancy_out()
        self.__model.reset_transformations()
        self.__value = self.__model.last_value


    def deny_solution(self):
        self.__model.revert()


    

    def __dfs(self, visited : set[Node],starting_node : Node) -> Node:
        if starting_node not in visited:
            visited.add(starting_node)
            for neighbour in self.__adjancy_out[starting_node]:
                self.__dfs(visited, neighbour)


    @functools.cached_property
    def feasibility(self) -> bool:
        node = list(self.__nodes)[0]
        visited = set()
        self.__dfs(visited,node)
        if len(visited) == self.number_of_nodes:
            self.__adjancy_in,self.__adjancy_out = self.__adjancy_out,self.__adjancy_in
            visited = set()
            self.__dfs(visited,node)
            self.__adjancy_in,self.__adjancy_out = self.__adjancy_out,self.__adjancy_in
        return len(visited) == self.number_of_nodes
    
    @property
    def model_feasibility(self) -> bool:
        return self.__model.feasibility

   
    def show(self) -> None:
        if self.__G is None:
            self.__G = nx.MultiDiGraph()
            for edge in self.__edges:
                self.__G.add_edge(edge.endpoint_1.label,edge.endpoint_2.label,color=edge.color)
            self.__nodes_pos = {node.label :  node.position for node in self.__nodes}

        colors = [self.__G[u][v][0]['color'] for u,v in self.__G.edges()]
        nx.draw(self.__G,with_labels=True,pos=self.__nodes_pos,edge_color=colors)
        plt.show()

    

    def cycles(self) -> set[tuple[Edge]]:
        cycles = set()

        visited = defaultdict(lambda: False)
        dummy_node = Node("",(0,0))
        for node in self.__nodes:
            self.__dfs_cycle( node, node, visited, [Edge(dummy_node,node)], cycles)

        return cycles
        
    def __dfs_cycle(self, start: Node, current : Node, visited : dict[Node:bool], path: list[Edge], cycles: set[tuple[Edge]]):
        visited[current] = True
    
        if current != start:

            path.append(self.__map_nodes_to_edge[(path[-1].endpoint_2,current)])

        for neighbor in self.__adjancy_out[current]:
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
        
    
    def get_one_edge_reversal_neighbour(self,edge : Edge):

        self.__model.alter_adjancy_lists([edge])
    

        if self.__model.feasibility:
            self.__model.invert_edge_in_model({edge})
            return self
        else:
            self.__model.alter_adjancy_lists([edge.inverse])
           
        return None

    def get_prox_node_edges_reversals_neighbour(self, s : Node):
        
        involved_initially = self.__model.get_involved_edges(s)
        self.__model.alter_adjancy_lists(involved_initially)
        
            
        if self.__model.feasibility:
            self.__model.invert_edge_in_model(involved_initially)
            return self
        else:
            self.__model.alter_adjancy_lists(list(map(lambda e : e.inverse,involved_initially)))
        return None
            

    def get_path_reversal_neighbour(self, path : tuple[Edge],check=True):
        
        
        self.__model.alter_adjancy_lists(path)
        
        if not check or self.__model.feasibility:
            self.__model.invert_edge_in_model(path)
            return self
        else:
            self.__model.alter_adjancy_lists(list(map(lambda e : e.inverse,path)))
            
        return None
    
    



        