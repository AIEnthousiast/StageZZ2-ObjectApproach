import Instances
import gurobipy as gp
from gurobipy import GRB
from MetaData import MetaData
import networkx as nx
from ResolutionProtocol import ResolutionProtocol

class SNOPCompactModel(ResolutionProtocol):
    def __init__(self,env : gp.Env = gp.Env()):
        self.env = env

        self.__model = gp.Model(name='CompactModel',env=self.env)
        self.__pos = {}
        self.x, self.f = {}, {}

    def construct_model(self,instance: Instances.Instance) -> None:
        #Construct all possible directed edges
       
        self.__model = gp.Model(name='CompactModel',env=self.env)
        edges : list[Instances.Edge] =  instance.get_edges()
        
        unblocked_edges = [edge for edge in edges if not edge.blocked]


        nodes : set[Instances.Node] = instance.get_nodes()

        self.__pos = {n.label:(n.position[0],n.position[1]) for n in nodes}
        # Construct variables
        for edge in unblocked_edges:
            
            n1 = edge.endpoint_1.label
            n2 = edge.endpoint_2.label
            self.x[n1,n2] = self.__model.addVar(name="x_%s_%s"%(n1,n2),vtype=GRB.BINARY)
            self.x[n2,n1] = self.__model.addVar(name="x_%s_%s"%(n2,n1),vtype=GRB.BINARY)
                    
            for s in nodes:
                self.f[s.label,n1,n2] = self.__model.addVar(0,GRB.INFINITY,name="f^%s_%s_%s"%(s,n1,n2),vtype=GRB.CONTINUOUS)
                self.f[s.label,n2,n1] = self.__model.addVar(0,GRB.INFINITY,name="f^%s_%s_%s"%(s,n2,n1),vtype=GRB.CONTINUOUS)
                
        
        self.__model.update()


        objective = gp.quicksum(e.cost*(self.f[s.label,e.endpoint_1.label,e.endpoint_2.label] + self.f[s.label,e.endpoint_2.label,e.endpoint_1.label]) for e in unblocked_edges for s in nodes)
        self.__model.setObjective(objective,sense=GRB.MINIMIZE)
        
        
        #Construct constraints
        
        for e in unblocked_edges:
            i,j = e.endpoint_1.label,e.endpoint_2.label
            self.__model.addConstr(self.x[i,j] + self.x[j,i] == 1)

        for s in nodes:
            self.__model.addConstr(sum(self.f[s.label,s.label,i.label] for i in instance.get_neighbours(s)) == len(nodes) - 1)

            for i in nodes:
                if i != s :
                    neighbours = instance.get_neighbours(i)
                    self.__model.addConstr(sum(self.f[s.label,j.label,i.label] for j in neighbours) - sum(self.f[s.label,i.label,j.label] for j in neighbours) == 1)       
            for e in unblocked_edges:
                (i,j) = e.endpoint_1,e.endpoint_2
                self.__model.addConstr(-self.f[s.label,i.label,j.label]+(len(nodes)-1)*self.x[i.label,j.label] >= 0)
                self.__model.addConstr(-self.f[s.label,j.label,i.label]+(len(nodes)-1)*self.x[j.label,i.label] >= 0)
    


    def solve(self,time_limit=float("inf"),show=False) -> MetaData:
       
        
        self.__model.Params.timeLimit = time_limit


        self.__model.optimize()
        
        diedges = []
        for v in self.__model.getVars():
            if v.varname[0] == "x" and v.x > 0.5:
                splits = v.varname.split("_")
                diedges.append((splits[1],splits[2]))

        if show:
            Gp = nx.MultiDiGraph()
            Gp.add_edges_from(diedges)

            colors = ["b"]*len(diedges)
         
            nx.draw(Gp,self.__pos,with_labels=True,edge_color=colors)
            
        meta = MetaData(self.__model.Runtime,self.__model.ObjBound)
        meta.misc["Gap"] = self.__model.MIPGap
        meta.misc["solution"] = self.__model.getVars()

        return meta
    

    