from Instances import Edge,Node,FREE_COLOR,BLOCKED_COLOR


def test_edge_default() -> None:

    e1 = Node("1",(1,2))
    e2 = Node("2",(3,4))
        
    edge = Edge(e1,e2,1)
    assert edge.endpoint_1 == e1 and edge.endpoint_2 == e2  and edge.color == FREE_COLOR and edge.cost == 1


def test_edge_blocked() -> None:

    e1 = Node("1",(1,2))
    e2 = Node("2",(3,4))
        
    edge = Edge(e1,e2,1,True)
    assert edge.endpoint_1 == e1 and edge.endpoint_2 == e2  and edge.color == BLOCKED_COLOR and edge.cost == 1


