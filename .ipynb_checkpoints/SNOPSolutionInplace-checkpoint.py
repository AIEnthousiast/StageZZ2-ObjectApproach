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
import threading
from SNOPSolutionBase import SNOPSolutionBase



@dataclass
class CarriableModel:
    
    __model : gp.Model
    _nodes : set[Node]
    _edges : set[Edge]
    _adjancy_in : dict[Node:set[Node]] = field(default_factory= lambda : defaultdict(lambda : set()))
    _adjancy_out : dict[Node:set[Node]] = field(default_factory= lambda : defaultdict(lambda : set()))
    __f : gp.tupledict = field(default_factory= lambda: set())
    __inverse_transformations : list[Edge] = field(default_factory= lambda : [],init=False)
    __last_value : int = field(default=0, init=False)
   
        

    @property
    def last_value(self):
        return self.__last_value

    
    
    def set_adjancy_in(self,adj_in):
        self._adjancy_in = adj_in

    def set_adjancy_out(self,adj_out):
        self._adjancy_out = adj_out

    def get_adjancy_in(self) -> dict[Node:list[Node]] :
        return copy.deepcopy(self._adjancy_in)
    
    def get_adjancy_out(self) -> dict[Node:list[Node]] :
        return copy.deepcopy(self._adjancy_out)
    

    def reset_transformations(self):
        self.__inverse_transformations = []

    def construct(self):
        f = {}
        number_of_nodes = len(self._nodes)
        for s in self._nodes:
            for edge in self._edges:
                i,j = edge.endpoint_1, edge.endpoint_2
                f[s.label,i.label,j.label] = self.__model.addVar(0,number_of_nodes-1,name="f^%s_%s%s"%(s.label,i.label,j.label),vtype=GRB.CONTINUOUS)
        self.__model.update()

        objective = gp.quicksum(edge.cost*f[s.label,edge.endpoint_1.label,edge.endpoint_2.label] for edge in self._edges for s in self._nodes)
        self.__model.setObjective(objective,sense=GRB.MINIMIZE)
        
        for s in self._nodes:
            
            self.__model.addConstr(gp.quicksum(f[s.label,s.label,i.label] for i in self._adjancy_out[s]) == number_of_nodes - 1,name="OutFlow_%s"%(s.label))
            for i in self._nodes:
                if i != s:
                    self.__model.addConstr(gp.quicksum(f[s.label,j.label,i.label] for j in self._adjancy_in[i]) - gp.quicksum(f[s.label,i.label,j.label] for j in self._adjancy_out[i]) == 1,
                                                        name="InFlow_%s_%s"%(s.label,i.label))

        self.__model.update()
        self.__f = f
    
    

    def get_edges(self):
        return self._edges.copy()
    
   
    def alter_edges(self,edges: list[Edge]):
        for edge in edges:
            self._edges.remove(edge)
            self._edges.add(edge.inverse)
        

    def alter_adjancy_lists(self,edges : list[Edge]):
        for edge in edges:
            self._adjancy_in[edge.endpoint_1].add(edge.endpoint_2)
            self._adjancy_in[edge.endpoint_2].remove(edge.endpoint_1)
            self._adjancy_out[edge.endpoint_1].remove(edge.endpoint_2)
            self._adjancy_out[edge.endpoint_2].add(edge.endpoint_1)

            self._edges.remove(edge)
            self._edges.add(edge.inverse)

        #self.alter_edges(edges)

    def construct_variables_from(self,start,finish,edges,number_of_nodes):
        for i in range(start,finish):
            edge = edges[i]
            for s in self._nodes:
                self.__model.remove(self.__model.getVarByName("f^%s_%s%s"%(s.label,edge.endpoint_1.label,edge.endpoint_2.label)))
                
                del  self.__f[s.label,edge.endpoint_1.label,edge.endpoint_2.label]
                self.__f[s.label,edge.endpoint_2.label,edge.endpoint_1.label] = self.__model.addVar(0,number_of_nodes-1,name="f^%s_%s%s"%(s.label,edge.endpoint_2.label,edge.endpoint_1.label),vtype=GRB.CONTINUOUS)
    def construct_constrs_from(self,start,finish,involved_nodes,number_of_nodes):
        for i in range(start,finish):     
            node = involved_nodes[i]
            self.__model.remove(self.__model.getConstrByName("OutFlow_%s"%(node.label)))
            self.__model.addConstr(gp.quicksum(self.__f[node.label,node.label,i.label] for i in self._adjancy_out[node]) == number_of_nodes - 1,name="OutFlow_%s"%(node.label))

            for s in self._nodes:
                if s != node:
                    self.__model.remove(self.__model.getConstrByName("InFlow_%s_%s"%(s.label,node.label)))
                    self.__model.addConstr(gp.quicksum(self.__f[s.label,j.label,node.label] for j in self._adjancy_in[node]) - gp.quicksum(self.__f[s.label,node.label,j.label] for j in self._adjancy_out[node]) == 1,
                                                            name="InFlow_%s_%s"%(s.label,node.label))
            
    

    def invert_edge_in_model(self, edges : list[Edge], number_of_threads: int = 5):
        
        
        
        n = len(edges)
    
        edges = list(edges)
        number_of_nodes = len(self._nodes)

        involved_nodes = set()
        for edge in edges:
            involved_nodes.add(edge.endpoint_1)
            involved_nodes.add(edge.endpoint_2)
        involved_nodes = list(involved_nodes)
        
        self.__inverse_transformations = list(map(lambda e : e.inverse,edges))
    

        variable_threads = []
        constr_threads = []
        if n < number_of_threads:
            for i in range(n):
                thread = threading.Thread(target=self.construct_variables_from, args=(i, i+1,edges,number_of_nodes))
                variable_threads.append(thread)
                thread.start()
        else:
            chunk_size = n // number_of_threads
            for i in range(number_of_threads):
                start_var = i * chunk_size
                end_var = (i + 1) * chunk_size if i < number_of_threads - 1 else n
                thread = threading.Thread(target=self.construct_variables_from, args=(start_var, end_var,edges,number_of_nodes))
                variable_threads.append(thread)
                thread.start()
        for thread in variable_threads:
            thread.join()
        


        p = len(involved_nodes)
        if  p < number_of_threads:
            for i in range(p):
                thread = threading.Thread(target=self.construct_constrs_from, args=(i, i+1,involved_nodes,number_of_nodes))
                constr_threads.append(thread)
                thread.start()
        else:
            chunk_size = p // number_of_threads
            for i in range(number_of_threads):
                start_var = i * chunk_size
                end_var = (i + 1) * chunk_size if i < number_of_threads - 1 else p
                thread = threading.Thread(target=self.construct_constrs_from, args=(start_var, end_var,involved_nodes,number_of_nodes))
                constr_threads.append(thread)
                thread.start()
            
        for thread in constr_threads:
            thread.join()

        self.__model.update()

        objective = gp.quicksum(edge.cost*self.__f[s.label,edge.endpoint_1.label,edge.endpoint_2.label] for edge in self._edges for s in self._nodes)
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
        return [e for e in self._edges if e.endpoint_1 == s or e.endpoint_2 == s]
        

    @property
    def ObjBound(self):
        return self.__model.ObjBound
        

    def __dfs(self, visited : set[Node],starting_node : Node) -> Node:
        if starting_node not in visited:
            visited.add(starting_node)
            for neighbour in self._adjancy_out[starting_node]:
                self.__dfs(visited, neighbour)

    @property 
    def feasibility(self):
        node = list(self._nodes)[0]
        number_of_nodes = len(self._nodes)
        visited = set()
        self.__dfs(visited,node)
        if len(visited) == number_of_nodes:
            self._adjancy_in,self._adjancy_out = self._adjancy_out,self._adjancy_in
            visited = set()
            self.__dfs(visited,node)
            self._adjancy_in,self._adjancy_out = self._adjancy_out,self._adjancy_in
        return len(visited) == number_of_nodes


@dataclass
class SNOPSolutionInplace(SNOPSolutionBase):

   
    __model : CarriableModel = field(default=None)
    

    def __post_init__(self):

        super().__post_init__()
        
        if self.__model == None:
            env = gp.Env(empty=True)
            env.setParam('OutputFlag', 0)
            env.start()
            model = gp.Model(env=env)
        
            self.__model = CarriableModel(model,self._nodes,self._edges.copy(),copy.deepcopy(self._adjancy_in),copy.deepcopy(self._adjancy_out))
            self.__model.construct()
            self.__value = self.get_trial_value()
        

    def get_nodes(self) -> set[Node]:
        return self._nodes
    
    def get_edges(self) -> set[Edge]:
        return self._edges.copy()

    @functools.cached_property
    def number_of_nodes(self):
        return len(self._nodes)


    def get_trial_value(self) -> int:
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
        self._edges = self.__model.get_edges()
        self._adjancy_in = self.__model.get_adjancy_in()
        self._adjancy_out = self.__model.get_adjancy_out()
        self.__model.reset_transformations()
        self.__value = self.__model.last_value
        return self

    def deny_solution(self):
        self.__model.revert()
        return self


    @property
    def model_feasibility(self) -> bool:
        return self.__model.feasibility

    
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
            

    def get_path_reversal_neighbour(self, path : tuple[Edge],check=False):
        
        
        self.__model.alter_adjancy_lists(path)
        
        if not check or self.__model.feasibility:
            self.__model.invert_edge_in_model(path)
            return self
        else:
            self.__model.alter_adjancy_lists(list(map(lambda e : e.inverse,path)))
            
        return None
    
    



        
