from Instances import Instance, Edge, Node
from SNOPSolution import SNOPSolution
from MetaData import MetaData
from Metaheuristic import Metaheuristic
from timeit import default_timer as timer
from typing import Callable,Generator
from functools import partial
from RVND import RVND
from LocalSearch import LocalSearch
import random



class GVNS(Metaheuristic):
    def __init__(self):
        self.neighbourhoods : list[Callable[[SNOPSolution],Generator[tuple[SNOPSolution,bool],None,None]]] = []
        self.local_search : LocalSearch = RVND()

    def get_feasible_solution(self, neighbourhood_gen : Generator[tuple[SNOPSolution,bool],None,None]) -> SNOPSolution:
        neighbour,feasibility = next(neighbourhood_gen)
        while not feasibility:
            try:
                neighbour,feasibility = next(neighbourhood_gen)
            except StopIteration:
                return None
        return neighbour
        
    def construct_model(self, instance: Instance | SNOPSolution) -> None:
        super().construct_model(instance)
        self.neighbourhoods = [one_edge_reversal_neighbour,partial(prox_node_edges_reversals_neighbour,nodes=self.starting_solution.get_nodes()),
                               traverse_cycle_reversal_neighbour]
        
        
    def solve(self, time_limit: int = float('inf'), show: bool = False) -> MetaData:
        it = 0
        itmax = 10
        current_solution = self.starting_solution
        
        start = timer()
        while it < itmax and timer() - start < time_limit:
            k = 0
            neighborhood_generators = [neighbourhood(current_solution) for neighbourhood in self.neighbourhoods]
            while k < len(self.neighbourhoods) and timer() - start < time_limit:
                random_neighbour = self.get_feasible_solution(neighborhood_generators[k])
                if random_neighbour is None:
                    k += 1
                    continue
                self.local_search.construct_model(random_neighbour)
                improved_neighbour : SNOPSolution = self.local_search.solve(return_first_improvement=False).misc["solution"]
                if improved_neighbour.value < current_solution.value:
                    current_solution = improved_neighbour
                    neighborhood_generators = [neighbourhood(current_solution) for neighbourhood in self.neighbourhoods]
                    k = 1
                else:
                    k += 1
                it += 1
                if it == itmax:
                    k = len(self.neighbourhoods)
            
        meta = MetaData(timer() - start,current_solution.value)
        meta.misc["solution"] = current_solution

        return meta



def one_edge_reversal_neighbour(solution : SNOPSolution )  -> Generator[tuple[SNOPSolution,bool],None,None]:
    current_solution = solution
    shuffled_edges = list(current_solution.get_edges())
    random.shuffle(shuffled_edges)

    for edge in shuffled_edges:
        trial_solution = current_solution.get_one_edge_reversal_neighbour(edge)
        yield trial_solution,trial_solution.feasibility
    
        
def prox_node_edges_reversals_neighbour(solution : SNOPSolution , nodes : set[Node] = None) -> Generator[tuple[SNOPSolution,bool],None,None]:
    current_solution = solution
    nodes = nodes if nodes else solution.get_nodes()
    for node in nodes:
        trial_solution = current_solution.get_prox_node_edges_reversals_neighbour(node)
        yield trial_solution,trial_solution.feasibility
    
    
def traverse_cycle_reversal_neighbour(solution : SNOPSolution ) -> Generator[tuple[SNOPSolution,bool],None,None]:
    current_solution = solution
    shuffled_cycles = list(current_solution.cycles)
    random.shuffle(shuffled_cycles)

    for cycle in shuffled_cycles:
        trial_solution = current_solution.get_path_reversal_neighbour(cycle)
        yield trial_solution,True