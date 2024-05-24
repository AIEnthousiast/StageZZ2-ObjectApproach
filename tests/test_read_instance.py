from Instances import read_instance, GridInstance

def test_read_instance() -> None:
    edges = read_instance("v_9_a12_r0_b0.dat")

    grid = GridInstance(n=3)

    assert grid.get_edges() == edges