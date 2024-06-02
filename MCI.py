from ResolutionProtocol import ResolutionProtocol
from Instances import Instance
from MetaData import MetaData
from SNOPCompactModel import SNOPCompactModel
import gurobipy as gp
from timeit import default_timer as timer


class MCI(ResolutionProtocol):
    def __init__(self, N = 1):
        self.__model = None
        self.__paths = None
        self.__N = N

    def construct_model(self, instance: Instance) -> None:
        env = gp.Env()
        env.setParam('OutputFlag', 0)
        env.start()
        self.__model = SNOPCompactModel(env=env)
        self.__model.construct_model(instance)

        self.__paths = list(map(lambda x : x[1], sorted(instance.get_minimum_paths().values(),key=lambda x : x[0],reverse=True)))

    def solve(self, time_limit: int) -> MetaData:
        i = 0
        start = timer()
        best_sol = None
        best_value = float('inf')
        limit =  min(self.__N,len(self.__paths))
        while timer() - start < time_limit and i < limit:
            self.__model.fix_path(self.__paths[i])
            meta = self.__model.solve()
            if meta.objective_value == float("inf"):
                self.__model.revert_last_fix()
                i += 1
                continue
            if meta.objective_value < best_value:
                best_sol = meta
                best_value = meta.objective_value
            i += 1
        meta = MetaData(timer() - start,best_value)
        meta.misc["solution"] = best_sol.misc["solution"]
        return best_sol
