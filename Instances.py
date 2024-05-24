from dataclasses import dataclass,field
from collections import defaultdict
import networkx as nx
import sys
import random
import copy
import functools
import matplotlib.pyplot as plt


FREE_COLOR = 'b'
BLOCKED_COLOR = 'r'


class NoBlocksAvailableError(Exception):
    pass

class InvalidInstanceError(Exception):
    pass

@dataclass(frozen=True,slots=True,order=True)
class Node:
    label : str
    position: tuple[int,int] = field(hash=False,compare=False)
    color : str =  field(default="b", hash=False,compare=False)



@dataclass(frozen=True)
class Edge:
    endpoint_1 : Node 
    endpoint_2 : Node 
    cost : int = field(default=1)
    blocked : bool = field(default=False,hash=False,compare=False)


   

    @functools.cached_property
    def color(self) -> str:
        return BLOCKED_COLOR if self.blocked else FREE_COLOR
    
    @functools.cached_property
    def inverse(self):
        return Edge(self.endpoint_2,self.endpoint_1,self.cost,self.blocked)

class Instance:
    def __init__(self, edges : list[Edge]):
        self.__adjancy : dict[Node:list[Node]] = defaultdict(lambda: [])
        self.__nodes : set[Node] = set()
        for edge in edges:
            if not edge.blocked:
                self.__adjancy[edge.endpoint_1].append(edge.endpoint_2)
                self.__adjancy[edge.endpoint_2].append(edge.endpoint_1)
            self.__nodes.add(edge.endpoint_1)
            self.__nodes.add(edge.endpoint_2)

        self.__edges : list[Edge] = edges
        self.__G : nx.Graph = None
        self.__nodes_pos : dict[str:tuple(int,int)] = {node.label:node.position for node in self.__nodes}
        self.__n_blocks : int = 0
        for edge in self.__edges:
            if edge.blocked:
                self.__n_blocks += 1

    
    def get_nodes(self) -> set[Node]:
        return self.__nodes
    

    def get_edges(self) -> list[Edge]:
        return self.__edges
    
    def get_number_blockages(self) -> int:
        return self.__n_blocks

    @functools.cached_property
    def costs(self) -> dict[Edge:int]:
        return {(e.endpoint_1,e.endpoint_2):e.cost for e in self.__edges}
    
    def __reset_graph(self) -> None:
        self.__G = None

    def get_neighbours(self, n: Node) -> list[Node]:
        try:
            assert n in self.__nodes
        except AssertionError:
            print("Unrecognized node label", file=sys.stderr)

        if n in self.__nodes:
            return self.__adjancy[n].copy()
      

    def add_one_block(self) -> None:
        blokable_edge = get_one_safely_blockable_edge(self.__edges)
    
        try: 
            assert blokable_edge is not None
        except AssertionError:
            raise NoBlocksAvailableError
        else:
            new_edge = Edge(blokable_edge.endpoint_1,blokable_edge.endpoint_2,blokable_edge.cost,blocked=True)
            self.__edges.remove(blokable_edge)
            self.__edges.append(new_edge)

            self.__adjancy[blokable_edge.endpoint_1].remove(blokable_edge.endpoint_2)
            self.__adjancy[blokable_edge.endpoint_2].remove(blokable_edge.endpoint_1)
            self.__n_blocks += 1
            self.__reset_graph()

    def show(self) -> None:
        if self.__G is None:
            self.__G = nx.Graph()
            for edge in self.__edges:
                self.__G.add_edge(edge.endpoint_1.label,edge.endpoint_2.label,color=edge.color)

        colors = [self.__G[u][v]['color'] for u,v in self.__G.edges()]
        nx.draw(self.__G,with_labels=True,pos=self.__nodes_pos,edge_color=colors)
        plt.show()

    def __dfs(self,visited : set[Node],node: Node) -> None:  #function for dfs 
        if node not in visited:
            visited.add(node)
            for neighbour in self.get_neighbours(node):
                self.__dfs(visited, neighbour)

    def is_strongly_connected(self) -> bool:
        visited = set()
        s = random.choice(list(self.__nodes))
        self.__dfs(visited,s)
        return len(visited) == len(self.__nodes)
    
    @functools.cached_property
    def feasibility(self) -> bool:
        return self.is_strongly_connected() and len(find_bridges(self.__edges)) == 0

    def get_random_strong_orientation(self) -> set[Edge]:
            
        #1 -> white 
        #0 -> black
        #-1 -> gray
        
        
        def DFS_visit(i,parent):
            color[i] = -1
            
            for j in sorted(self.__adjancy[i],key=lambda x : w[x]):
                if color[j] == 1:
                    try:
                        A.add(Edge(i,j,self.costs[(i,j)]))
                    except:
                        A.add(Edge(i,j,self.costs[(j,i)]))
                    DFS_visit(j,i)
                elif j != parent and color[j] != 0:
                    try:
                        A.add(Edge(i,j,self.costs[(i,j)]))
                    except:
                        A.add(Edge(i,j,self.costs[(j,i)]))
            color[i] = 0
            
        
        color = defaultdict(lambda : 1)
        A = set()
        weights = list(range(0,len(self.__nodes)))
        random.shuffle(weights)

        w = {}
        for n,weight in zip(self.__nodes,weights):
            w[n] = weight
    
        
        r = random.choice(list(self.__nodes))
        
        DFS_visit(r,-1)
        
        return A


    def save_dat_format(self):
        filename = f"v_{len(self.__nodes)}_a{len(self.__edges)}_r0_b{self.__n_blocks}.dat"
                                    
        blocks : list[Edge] = []
        with open(filename,'w') as f:
            f.write(f"INSTANCE_NAME v_{len(self.__nodes)}_a{len(self.__edges)}_r0_b{self.__n_blocks}\n")
            f.write(f"NB_VERTICES {len(self.__nodes)}\n")
            f.write(f"NB_ARCS {len(self.__edges)}\n")
            f.write(f"NB_BLOCKAGES {self.__n_blocks}\n\n\n")

            f.write("VERTICES\n")
            
            for node in self.__nodes:
                f.write(f"{node.label} {node.position[0]} {node.position[1]}\n")
            
            f.write("\n\nARCS\n")
            for edge in self.__edges:
                f.write(f"{edge.endpoint_1.label} {edge.endpoint_2.label} {edge.cost}\n")
                if edge.blocked:
                    blocks.append(edge) 

            f.write("\n\n")
            f.write("REQUESTS\n\n")
            f.write("BLOCKAGES\n\n")
            for edge in blocks:
                f.write(f"{edge.endpoint_1} {edge.endpoint_2}\n")
                
            f.write("\nEND\n")

class GridInstance(Instance):
    def __init__(self, n : int, n_blockages: int = 0):
        super().__init__(self.__create_grid_edges(n))
        for _ in range(n_blockages):
            try:
                self.add_one_block()
            except NoBlocksAvailableError:
                break
        
            
    def __create_grid_edges(self,n):
        """
        Generate edges for a nxn grid instance
        """
        edges = []
        nodes = [[Node(f"{i*n+j+1}",(i,j)) for j in range(n)] for i in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i < n-1:
                   edges.append(Edge(nodes[i][j],nodes[i+1][j],1))
                if j < n-1:
                    edges.append(Edge(nodes[i][j],nodes[i][j+1],1))
                    
        return edges
                    







def get_one_safely_blockable_edge(edges : list[Edge]) -> Edge:
        
    try:
        assert len(find_bridges(edges)) == 0
    except:
        raise InvalidInstanceError
    
    shuffled_edges = edges.copy()
    edges_copy = edges.copy()
    random.shuffle(shuffled_edges)
    blockable = None
    
    
    for e in shuffled_edges:
        if not e.blocked:
            edges_copy.remove(e)
            bridges = find_bridges(edges_copy)
            if len(bridges) == 0:
                blockable = e
                break
            edges_copy.append(e)

        
        
    return blockable







def find_bridges(edges: list[Edge]) -> list[Edge]:
    def dfs(u, parent, visited, disc, low, bridges):
        nonlocal time
        visited[u] = True
        disc[u] = time
        low[u] = time
        time += 1
           
        for v in adjancy[u]:
            if not visited[v]:
                dfs(v, u, visited, disc, low, bridges)
                low[u] = min(low[u], low[v])
                if low[v] > disc[u]:
                    try:
                        bridges.append(edge_mapping[(u,v)])
                    except:
                        bridges.append(edge_mapping[(v,u)])
            elif v != parent:
                low[u] = min(low[u], disc[v])
                

    visited = defaultdict(lambda: False)
    disc = defaultdict(lambda : float('inf'))
    low = defaultdict(lambda : float('inf'))
    bridges = []
    time = 0

    adjancy = defaultdict(lambda : [])
    nodes = set()
    for edge in edges:
        if not edge.blocked:
            adjancy[edge.endpoint_1].append(edge.endpoint_2)
            adjancy[edge.endpoint_2].append(edge.endpoint_1)
        nodes.add(edge.endpoint_1)
        nodes.add(edge.endpoint_2)


    edge_mapping = {(edge.endpoint_1,edge.endpoint_2): edge for edge in edges}

    for n in nodes:
        if not visited[n]:
            dfs(n, None, visited, disc, low, bridges)

    return bridges


           
def read_instance(filepath):

    arcs = {}
    vertices_mapp = {}
    requests  = []

    lecture = 0

    with open(filepath,"r") as f:
        for line in f:
            line = line.strip()
            if line != '':
                line = line.split(" ")
                if  lecture == 0:
                    if line[0].strip() == "VERTICES":
                        lecture = 1
                elif lecture == 1:
                    if line[0] != "ARCS":
                        vertices_mapp[line[0]] = Node(line[0],(int(line[1]),int(line[2])))
                    else:
                        lecture = 2
                elif lecture==2:
                    if line[0] != "REQUESTS":
                        arcs[(line[0],line[1])] = [int(line[2]),False]
                    else:
                        lecture = 3
                elif lecture == 3:
                    if line[0] != "BLOCKAGES":
                        requests.append(line)
                    else:
                        lecture = 4
                elif lecture == 4:
                    if line[0] != "END":
                        arcs[(line[0],line[1])][1] = True

    edges = [Edge(vertices_mapp[a[0][0]],vertices_mapp[a[0][1]],a[1][0],a[1][1]) for a in arcs.items()]


    return edges
