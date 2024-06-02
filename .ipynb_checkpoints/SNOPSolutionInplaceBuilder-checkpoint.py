from Instances import Edge
from SNOPSolutionBase import SNOPSolutionBase
from SNOPSolutionBuilder import SNOPSolutionBuilder
from SNOPSolutionInplace import SNOPSolutionInplace


class SNOPSolutionInplaceBuilder(SNOPSolutionBuilder):
    def build(self,edges: set[Edge]) -> SNOPSolutionBase:
        return SNOPSolutionInplace(edges)