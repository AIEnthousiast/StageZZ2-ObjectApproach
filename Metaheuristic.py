# -*- coding: utf-8 -*-

from Instances import Instance,InvalidInstanceError
from MetaData import MetaData
from ResolutionProtocol import ResolutionProtocol
from SNOPSolutionBase import SNOPSolutionBase
from SNOPSolutionBuilder import SNOPSolutionBuilder
from SNOPSolutionInplaceBuilder import SNOPSolutionInplaceBuilder
from abc import abstractmethod


class Metaheuristic(ResolutionProtocol):
    def __init__(self):
        self.starting_solution : SNOPSolutionBase = None

    def construct_model(self, instance: Instance | SNOPSolutionBase, builder : SNOPSolutionBuilder = SNOPSolutionInplaceBuilder()) -> None:
        try:
            assert instance.feasibility
        except AssertionError:
            raise InvalidInstanceError
        else:
            if isinstance(instance,Instance):
                print(builder)
                self.starting_solution = builder.build(instance.get_random_strong_orientation(True))
            else:
                self.starting_solution = instance
            
    @abstractmethod
    def solve(self, time_limit: int = float("inf"), show: bool = False) -> MetaData:
        ...

