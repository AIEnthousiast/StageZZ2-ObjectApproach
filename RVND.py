# -*- coding: utf-8 -*-

from Instances import Instance, Edge, Node
from SNOPSolution import SNOPSolution
from MetaData import MetaData
from LocalSearch import LocalSearch
from timeit import default_timer as timer
import random

class RVND(LocalSearch):
    def solve(self, time_limit: int = float("inf"), return_first_improvement: bool = False,show: bool = False) -> MetaData:
        if self.starting_solution:

            improvement = True
            start = timer()
            current_solution = self.starting_solution
            
            while improvement and timer() - start < time_limit:
                improvement = False
                random.shuffle(self.neighbourhood_exploring_functions)

                # traverse first neighborhood -> edge reversal
                for fun in self.neighbourhood_exploring_functions:
                    current_solution,improvement = fun(current_solution)
                    if improvement:
                        break
                if improvement and return_first_improvement:
                    break
                


            meta = MetaData(timer() - start,current_solution.value)
            meta.misc["solution"] = current_solution

            if show:
                current_solution.show()
            return meta
        

                    