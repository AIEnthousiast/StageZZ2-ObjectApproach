from Instances import Edge,Node,find_bridges


def test_find_bridges_None() -> None:
    edges = []
    n1 = Node("1",(0,0))
    n2 = Node("2",(0,1))
    n3 = Node("3",(0,2))
    
    edges.append(Edge(n1,n2,1))
    edges.append(Edge(n1,n3,1))
    edges.append(Edge(n2,n3,1))

    assert len(find_bridges(edges)) == 0


def test_find_bridges() -> None:
    edges = []
    n1 = Node("1",(0,0))
    n2 = Node("2",(0,1))
    n3 = Node("3",(0,2))
    
    edges.append(Edge(n1,n2,1))
    edges.append(Edge(n1,n3,1))
    edges.append(Edge(n2,n3,1,True))

    assert len(find_bridges(edges)) == 2

