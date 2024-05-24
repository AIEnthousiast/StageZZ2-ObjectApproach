from Instances import Edge,Node,get_one_safely_blockable_edge,find_bridges,InvalidInstanceError
import pytest

def test_get_one_safely_blockable_edge_None() -> None:
    edges = []
    n1 = Node("1",(0,0))
    n2 = Node("2",(0,1))
    n3 = Node("3",(0,2))
    
    edges.append(Edge(n1,n2,1))
    edges.append(Edge(n1,n3,1))
    edges.append(Edge(n2,n3,1))

    blockable = get_one_safely_blockable_edge(edges)


    assert blockable is None


def test_get_one_safely_blockable_edge_invalid_instance() -> None:
    edges = []
    n1 = Node("1",(0,0))
    n2 = Node("2",(0,1))
    n3 = Node("3",(0,2))
    n4 = Node("4",(0,3))
    
    edges.append(Edge(n1,n2,1))
    edges.append(Edge(n1,n3,1))
    edges.append(Edge(n2,n3,1))
    edges.append(Edge(n1,n4,1))

    with pytest.raises(InvalidInstanceError):
        blockable = get_one_safely_blockable_edge(edges)

def test_get_one_safely_blockable_edge() -> None:
    edges = []
    n1 = Node("1",(0,0))
    n2 = Node("2",(0,1))
    n3 = Node("3",(0,2))
    n4 = Node('4',(0,3))
    

    e1 = Edge(n1,n2,1)
    e2 = Edge(n1,n3,1)
    e3 = Edge(n1,n4,1)
    e4 = Edge(n2,n4,1)
    e5 = Edge(n2,n3,1)
    e6 = Edge(n3,n4,1)
    edges.append(e1)
    edges.append(e2)
    edges.append(e3)
    edges.append(e4)
    edges.append(e5)
    edges.append(e6)
    
    
    blockable = get_one_safely_blockable_edge(edges)

    assert blockable is not None
    
