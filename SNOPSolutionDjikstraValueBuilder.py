from Instances import Edge
from SNOPSolutionBase import SNOPSolutionBase
from SNOPSolutionBuilder import SNOPSolutionBuilder
from SNOPSolutionDjikstraValue import SNOPSOlutionDjikstraValue


class SNOPSolutionDjikstraValueBuilder(SNOPSolutionBuilder):
    def build(self,edges: set[Edge]) -> SNOPSolutionBase:
        return SNOPSOlutionDjikstraValue(edges)