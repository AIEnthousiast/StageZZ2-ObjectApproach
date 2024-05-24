from Instances import Node,FREE_COLOR


def test_node_default() -> None:
    n = Node("1",(3,4))
    assert n.label == "1" and n.position[0] == 3 and n.position[1] == 4 and n.color == FREE_COLOR
