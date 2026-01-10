import networkx as nx
from quantum_bench.hardware.config import Falcon27, Grid25

def test_falcon27_structure():
    hw = Falcon27()
    assert hw.num_qubits == 27
    assert len(hw.edges) > 0
    
    # Prüfen, ob Coupling Map und Graph konsistent sind
    assert len(hw.coupling_map) == len(hw.edges)
    
    G = hw.nx_graph
    assert isinstance(G, nx.Graph)
    assert G.number_of_nodes() == 27 # Sollte alle Knoten enthalten, auch isolierte (falls vorhanden)
    # Falcon 27 hat typischerweise weniger Kanten als ein volles Gitter
    # Wir prüfen nur grob, ob Kanten da sind
    assert G.number_of_edges() > 20

def test_grid25_structure():
    hw = Grid25()
    assert hw.num_qubits == 25
    
    G = hw.nx_graph
    # Ein 5x5 Gitter hat:
    # 5 Zeilen * 4 Kanten horizontal = 20
    # 5 Spalten * 4 Kanten vertikal = 20
    # Total = 40 Kanten (undirekt)
    # Unsere Implementierung speichert (u,v) und (v,u), also 80 in der Liste, aber 40 im nx.Graph
    assert G.number_of_edges() == 40
    assert G.number_of_nodes() == 25
