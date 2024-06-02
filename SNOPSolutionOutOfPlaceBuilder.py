from Instances import Edge
from SNOPSolutionBase import SNOPSolutionBase
from SNOPSolutionBuilder import SNOPSolutionBuilder
from SNOPSolutionOutOfPlace import SNOPSOlutionOutOfPlace


class SNOPSOlutionOutOfPlaceBuilder(SNOPSolutionBuilder):
    def build(self,edges: set[Edge]) -> SNOPSolutionBase:
        return SNOPSOlutionOutOfPlace(edges)