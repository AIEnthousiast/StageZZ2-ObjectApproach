# -*- coding: utf-8 -*-

from Instances import Instance,Node
from MetaData import MetaData
from SNOPSolutionBase import SNOPSolutionBase
from SNOPSolutionBase import SNOPSolutionBase
from SNOPSolutionBuilder import SNOPSolutionBuilder
from SNOPSolutionInplaceBuilder import SNOPSolutionInplaceBuilder
from abc import abstractmethod
import functools
from Metaheuristic import Metaheuristic

class LocalSearch(Metaheuristic):
    def __init__(self):
        self.neighbourhood_exploring_functions = None
    def construct_model(self, instance: Instance | SNOPSolutionBase,builder: SNOPSolutionBuilder = SNOPSolutionInplaceBuilder() ) -> None:
        super().construct_model(instance,builder)
        self.neighbourhood_exploring_functions = [traverse_cycle_reversal_neighbour,traverse_one_edge_reversal_neighbour,
                                                      functools.partial(traverse_prox_node_edges_reversals_neighbour,nodes=self.starting_solution.get_nodes())]

    @abstractmethod 
    def solve(self, time_limit: int = float("inf"), return_first_improvement: bool = False, show: bool = False) -> MetaData:
        ...

    


def traverse_one_edge_reversal_neighbour(solution : SNOPSolutionBase )  -> tuple[SNOPSolutionBase,bool]:
    current_solution = solution
    improvement = False
    for edge in current_solution.get_edges():
        trial_solution = current_solution.get_one_edge_reversal_neighbour(edge)
        if trial_solution:
            if trial_solution.get_trial_value() < current_solution.value:
                current_solution = current_solution.accept_solution()
                improvement = True
                break
            else:
                current_solution = current_solution.deny_solution()
    return current_solution,improvement
    
def traverse_prox_node_edges_reversals_neighbour(solution : SNOPSolutionBase , nodes : set[Node] = None) -> tuple[SNOPSolutionBase,bool]:
    current_solution = solution
    improvement = False
    nodes = nodes if nodes else solution.get_nodes()
    for node in nodes:
        trial_solution = current_solution.get_prox_node_edges_reversals_neighbour(node)
        if trial_solution:
            if trial_solution.get_trial_value() < current_solution.value:
                current_solution = current_solution.accept_solution()
                improvement = True
                break
            else:
                current_solution = current_solution.deny_solution()
    return current_solution,improvement
    
def traverse_cycle_reversal_neighbour(solution : SNOPSolutionBase ) -> tuple[SNOPSolutionBase,bool]:
    current_solution = solution
    improvement = False
    for cycle in current_solution.cycles():
        trial_solution = current_solution.get_path_reversal_neighbour(cycle)
        if trial_solution:
            if trial_solution.get_trial_value() < current_solution.value:
                current_solution = current_solution.accept_solution()
                improvement = True
                break
            else:
                current_solution = current_solution.deny_solution()
    return current_solution,improvement
