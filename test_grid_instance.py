from Instances import GridInstance,Edge,Node


def test_grid_instance_init() -> None:
    grid = GridInstance(3,0)

    assert grid.get_number_blockages() == 0

    n1 = Node('1',(0,0))
    n2 = Node('2',(0,1))
    n3 = Node('3',(0,2))
    n4 = Node('4',(1,0))
    n5 = Node('5',(1,1))
    n6 = Node('6',(1,2))
    n7 = Node('7',(2,0))
    n8 = Node('8',(2,1))
    n9 = Node('9',(2,2))
    assert grid.get_nodes() == set([n1,n2,n3,n4,n5,n6,n7,n8,n9]) 

    e1 = Edge(n1,n2,1)
    e2 = Edge(n1,n4,1)
    assert e1 in grid.get_edges() and e2 in grid.get_edges()