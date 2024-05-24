# -*- coding: utf-8 -*-

from Instances import Instance, Edge, Node
from MetaData import MetaData
from LocalSearch import LocalSearch
from timeit import default_timer as timer
import random

class VND(LocalSearch):
    def solve(self, time_limit: int = float("inf"), return_first_improvement: bool = False, show: bool = False) -> MetaData:
        if self.starting_solution:

            improvement = True
            start = timer()
            nodes = self.starting_solution.get_nodes()
            current_solution = self.starting_solution

            while improvement and timer() - start < time_limit:
                improvement = False
                # traverse first neighborhood -> edge reversal
                edges = current_solution.get_edges()
                for edge in edges:
                    instance = current_solution.get_one_edge_reversal_neighbour(edge)
                    
                    if instance:
                        if instance.get_model_value() < current_solution.value:
                            current_solution.accept_solution()
                            improvement = True
                            break
                        else:
                            current_solution.deny_solution()

                    

                if not improvement:
                    # traverse second neighborhood -> prox. node reversals
                    for node in nodes:
                        
                        instance = current_solution.get_prox_node_edges_reversals_neighbour(node)
                        if instance:
                            if instance.get_model_value() < current_solution.value:
                                current_solution.accept_solution()
                                improvement = True
                                break
                            else:
                                current_solution.deny_solution()

                    if not improvement:
                        
                        cycles = current_solution.cycles()
                        for cycle in cycles:
                            instance = current_solution.get_path_reversal_neighbour(cycle,False)
                            if instance:
                                if instance.get_model_value() < current_solution.value:
                                    current_solution.accept_solution()
                                    improvement = True
                                    break
                                else:
                                    current_solution.deny_solution()

            
                if improvement and return_first_improvement:
                    break

            meta = MetaData(timer() - start,current_solution.value)
            meta.misc["solution"] = current_solution
            
            if show:
                current_solution.show()
            return meta
        

                    