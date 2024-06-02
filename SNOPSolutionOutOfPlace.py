from Instances import Node, Edge, InvalidInstanceError
from SNOPSolutionBase import SNOPSolutionBase
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

import heapq



@dataclass
class CarriableModel:
    
    __model : gp.Model
    _nodes : set[Node]
    _edges : set[Edge]
    _adjancy_in : dict[Node:list[Node]] = field(default_factory= lambda : defaultdict(lambda : []))
    _adjancy_out : dict[Node:list[Node]] = field(default_factory= lambda : defaultdict(lambda : []))
    __f : gp.tupledict = field(default_factory=lambda : {},init=False)


    def construct(self):
        f = {}
        for s in self._nodes:
            for edge in self._edges:
                i,j = edge.endpoint_1, edge.endpoint_2
                f[s.label,i.label,j.label] = self.__model.addVar(0,self.number_of_nodes-1,name="f^%s_%s%s"%(s.label,i.label,j.label),vtype=GRB.CONTINUOUS)

        self.__model.update()

        objective = gp.quicksum(edge.cost*f[s.label,edge.endpoint_1.label,edge.endpoint_2.label] for edge in self._edges for s in self._nodes)
        self.__model.setObjective(objective,sense=GRB.MINIMIZE)
        
        for s in self._nodes:
            self.__model.addConstr(gp.quicksum(f[s.label,s.label,i.label] for i in self._adjancy_out[s]) == self.number_of_nodes - 1,name="Outflow_%s"%(s.label))
            for i in self._nodes:
                if i != s:
                    self.__model.addConstr(gp.quicksum(f[s.label,j.label,i.label] for j in self._adjancy_in[i]) - gp.quicksum(f[s.label,i.label,j.label] for j in self._adjancy_out[i]) == 1,
                                                        name="InFlow_%s_%s"%(s.label,i.label))

        self.__f = f
    
    
    def invert_edge_in_model(self, edge : Edge):
        number_of_nodes = len(self._nodes)

        self._adjancy_in[edge.endpoint_1].add(edge.endpoint_2)
        self._adjancy_in[edge.endpoint_2].remove(edge.endpoint_1)

        self._adjancy_out[edge.endpoint_1].remove(edge.endpoint_2)
        self._adjancy_out[edge.endpoint_2].add(edge.endpoint_1)


        #remove outflows
        self.__model.remove(self.__model.getConstrByName("Outflow_%s"%(edge.endpoint_1.label)))
        self.__model.remove(self.__model.getConstrByName("Outflow_%s"%(edge.endpoint_2.label)))


        #remove inflows 
        for s in self._nodes:
            if s != edge.endpoint_1:
                self.__model.remove(self.__model.getConstrByName("Inflow_%s_%s"%(s.label,edge.endpoint_1)))
            if s != edge.endpoint_2:
                self.__model.remove(self.__model.getConstrByName("Inflow_%s_%s"%(s.label,edge.endpoint_2)))

            #remove variables
            self.__model.remove(self.__model.getVarByName("f^%s_%s%s"%(s.label,edge.endpoint_1,edge.endpoint_2)))
            
            del  self.__f[s.label,edge.endpoint_1,edge.endpoint_2]

            #add new variable
            self.__f[s.label,edge.endpoint_2,edge.endpoint_1] = self.__model.addVar(0,number_of_nodes-1,name="f^%s_%s%s"%(s.label,edge.endpoint_2,edge.endpoint_1),vtype=GRB.CONTINUOUS)
        
        self.__model.update()
        #add Outflows        
        self.__model.addConstr(gp.quicksum(self.f[edge.endpoint_1.label,edge.endpoint_1.label,i.label] for i in self._adjancy_out[edge.endpoint_1]) == number_of_nodes - 1,name="Outflow_%s"%(edge.endpoint_1.label))
        self.__model.addConstr(gp.quicksum(self.f[edge.endpoint_2.label,edge.endpoint_2.label,i.label] for i in self._adjancy_out[edge.endpoint_2]) == number_of_nodes - 1,name="Outflow_%s"%(edge.endpoint_2.label))

        #add inflows
        for s in self._nodes:
            if s != edge.endpoint_1:
                self.__model.addConstr(gp.quicksum(self.__f[s.label,j.label,edge.endpoint_1.label] for j in self._adjancy_in[edge.endpoint_1]) - gp.quicksum(self.__f[s.label,edge.endpoint_1.label,j.label] for j in self._adjancy_out[edge.endpoint_1]) == 1,
                                                        name="InFlow_%s_%s"%(s.label,edge.endpoint_1.label))
            if s != edge.endpoint_2:
                self.__model.addConstr(gp.quicksum(self.__f[s.label,j.label,edge.endpoint_2.label] for j in self._adjancy_in[edge.endpoint_2]) - gp.quicksum(self.__f[s.label,edge.endpoint_2.label,j.label] for j in self._adjancy_out[edge.endpoint_2]) == 1,
                                                        name="InFlow_%s_%s"%(s.label,edge.endpoint_2.label))
        

    def optimize(self):
        self.__model.optimize()


    @property
    def ObjBound(self):
        return self.__model.ObjBound
        

@dataclass
class SNOPSOlutionOutOfPlace(SNOPSolutionBase):
    
    __last_solution : SNOPSolutionBase = field(default=None,init=False)


  

    @functools.cached_property
    def number_of_nodes(self):
        return len(self._nodes)

  

    def __construct_value_model(self,model: gp.Model) -> None:
        
        
        f = {}
        for s in self._nodes:
            for edge in self._edges:
                i,j = edge.endpoint_1, edge.endpoint_2
                f[s.label,i.label,j.label] = model.addVar(0,self.number_of_nodes-1,name="f^%s_%s%s"%(s.label,i.label,j.label),vtype=GRB.CONTINUOUS)

        model.update()

        objective = gp.quicksum(edge.cost*f[s.label,edge.endpoint_1.label,edge.endpoint_2.label] for edge in self._edges for s in self._nodes)
        model.setObjective(objective,sense=GRB.MINIMIZE)
        for s in self._nodes:
            model.addConstr(gp.quicksum(f[s.label,s.label,i.label] for i in self._adjancy_out[s]) == self.number_of_nodes - 1,name="Outflow_%s"%(s.label))
            for i in self._nodes:
                if i != s:
                    model.addConstr(gp.quicksum(f[s.label,j.label,i.label] for j in self._adjancy_in[i]) - gp.quicksum(f[s.label,i.label,j.label] for j in self._adjancy_out[i]) == 1,
                                                        name="InFlow_%s_%s"%(s.label,i.label)) 

        return model
        
    def accept_solution(self) -> SNOPSolutionBase:
        return self.__last_solution
    
    def deny_solution(self) -> SNOPSolutionBase:
        self.__last_solution = None
        return self
    
    @property
    def value(self) -> int:
      
        
        with gp.Env(empty=True) as env:
            env.setParam('OutputFlag', 0)
            env.start()
            with gp.Model(env=env) as model:
                
                model = self.__construct_value_model(model)
                model.optimize()
                
                return model.ObjBound
    

    
    def get_trial_value(self) -> int:
        return self.value
    
    def get_one_edge_reversal_neighbour(self,edge : Edge):
        neigbhour_edges = self._edges.copy()
        new_edge = Edge(edge.endpoint_2,edge.endpoint_1,edge.cost)
        neigbhour_edges.remove(edge)
        neigbhour_edges.add(new_edge)

        
        self.__last_solution = SNOPSOlutionOutOfPlace(neigbhour_edges)
        if  not self.__last_solution.feasibility:
            self.__last_solution = None

        return self.__last_solution
    

    def get_prox_node_edges_reversals_neighbour(self, s : Node):
        neigbhour_edges = self._edges.copy()
        for edge in self._get_involved_edges(s):
            neigbhour_edges.remove(edge)
            neigbhour_edges.add(Edge(edge.endpoint_2,edge.endpoint_1,edge.cost))
        
        self.__last_solution = SNOPSOlutionOutOfPlace(neigbhour_edges)
        if  not self.__last_solution.feasibility:
            self.__last_solution = None

        return self.__last_solution

    def get_path_reversal_neighbour(self, path : tuple[Edge],check : bool=False):
        neigbhour_edges = self._edges.copy()
        for edge in path:
            neigbhour_edges.remove(edge)
            neigbhour_edges.add(Edge(edge.endpoint_2,edge.endpoint_1,edge.cost))
        self.__last_solution = SNOPSOlutionOutOfPlace(neigbhour_edges)
        if check and not self.__last_solution.feasibility:
            self.__last_solution = None
        return self.__last_solution
    
    



        
