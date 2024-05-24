# -*- coding: utf-8 -*-

from Instances import Instance,InvalidInstanceError,Node
from MetaData import MetaData
from ResolutionProtocol import ResolutionProtocol
from SNOPSolution import SNOPSolution
from abc import abstractmethod
import functools


class Metaheuristic(ResolutionProtocol):
    def __init__(self):
        self.starting_solution : SNOPSolution = None

    def construct_model(self, instance: Instance | SNOPSolution) -> None:
        try:
            assert instance.feasibility
        except AssertionError:
            raise InvalidInstanceError
        else:
            if isinstance(instance,Instance):
                self.starting_solution = SNOPSolution(instance.get_random_strong_orientation())
            else:
                self.starting_solution = instance
            
    @abstractmethod
    def solve(self, time_limit: int = float("inf"), show: bool = False) -> MetaData:
        ...

