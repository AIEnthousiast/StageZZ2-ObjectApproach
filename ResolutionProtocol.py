from typing import Protocol
from Instances import Instance
from MetaData import MetaData

class ResolutionProtocol(Protocol):
    def construct_model(self, instance : Instance) -> None:
        """Should tune the model in order to solve the instance given"""

    def solve(self, time_limit : int, show : bool) -> MetaData:
        """Should solve the model with the specified time limit """