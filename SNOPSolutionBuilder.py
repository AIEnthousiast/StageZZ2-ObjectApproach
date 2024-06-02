from abc import ABC
from Instances import Edge
from SNOPSolutionBase import SNOPSolutionBase

class SNOPSolutionBuilder(ABC):

    def build(self,edges : set[Edge]) -> SNOPSolutionBase:
        ...