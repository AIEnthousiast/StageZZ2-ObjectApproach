from Instances import Instance,Edge,Node



def test_instance_nodes() -> None:
    edges = []
    n1 = Node("1",(0,0))
    n2 = Node("2",(0,1))
    n3 = Node("3",(0,2))
    

    edges.append(Edge(n1,n2,1))
    edges.append(Edge(n1,n3,1))
    edges.append(Edge(n2,n3,1))

    instance = Instance(edges)

    assert  instance.get_nodes() == set([n1,n2,n3])


def test_instance_edges_copy() -> None:
    edges = []
    n1 = Node("1",(0,0))
    n2 = Node("2",(0,1))
    n3 = Node("3",(0,2))
    

    edges.append(Edge(n1,n2,1))
    edges.append(Edge(n1,n3,1))
    edges.append(Edge(n2,n3,1))

    instance = Instance(edges)

    assert set(instance.get_edges()) == set(edges)


def test_instance_neighbours() -> None:
    edges = []
    n1 = Node("1",(0,0))
    n2 = Node("2",(0,1))
    n3 = Node("3",(0,2))
    

    edges.append(Edge(n1,n2,1))
    edges.append(Edge(n1,n3,1))
    edges.append(Edge(n2,n3,1))

    instance = Instance(edges)

    assert set(instance.get_neighbours(n1)) == set([n2,n3])




def test_instance_nodes_one_block() -> None:
    edges = []
    n1 = Node("1",(0,0))
    n2 = Node("2",(0,1))
    n3 = Node("3",(0,2))
    
    edges.append(Edge(n1,n2,1,True))
    edges.append(Edge(n1,n3,1))
    edges.append(Edge(n2,n3,1))

    instance = Instance(edges)

    assert set(instance.get_neighbours(n1)) == set([n3]) and instance.get_number_blockages() == 1




def test_add_one_block() -> None:
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

    edges = [e1,e2,e3,e4,e5,e6]

    instance = Instance(edges)

    assert instance.get_number_blockages() == 0

    instance.add_one_block()

    assert instance.get_number_blockages() == 1