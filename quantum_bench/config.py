from typing import List, Tuple
import networkx as nx

class HardwareConfig:
    """
    Zentrale Konfiguration für die Zielhardware.
    Definiert die Topologie des IBM Falcon 27-Qubit Prozessors.
    """
    
    # Adjazenzliste basierend auf der Heavy-Hex-Struktur (vereinfacht für 27 Qubits)
    # Quellenangabe: Basierend auf IBM Quantum Dokumentation und Qiskit FakeProvider Daten.
    FALCON_27_EDGES = [
        (0, 1), (1, 0), (1, 2), (1, 4), (2, 1), (2, 3), (3, 2), (3, 5),
        (4, 1), (4, 7), (5, 3), (5, 8), (6, 7), (7, 4), (7, 6), (7, 10),
        (8, 5), (8, 9), (8, 11), (9, 8), (10, 7), (10, 12), (11, 8), (11, 14),
        (12, 10), (12, 13), (12, 15), (13, 12), (13, 14), (14, 11), (14, 13), (14, 16),
        (15, 12), (15, 18), (16, 14), (16, 19), (17, 18), (18, 15), (18, 17), (18, 21),
        (19, 16), (19, 20), (19, 22), (20, 19), (21, 18), (21, 23), (22, 19), (22, 25),
        (23, 21), (23, 24), (24, 23), (24, 25), (25, 22), (25, 24), (25, 26), (26, 25)
    ]
    
    # Native Gatter-Basis für supraleitende Qubits
    BASIS_GATES = ['cx', 'id', 'rz', 'sx', 'x']

    @staticmethod
    def get_coupling_map() -> List[List[int]]:
        """Gibt die Coupling Map als Liste von Listen zurück (für Qiskit)."""
        return [[src, dst] for src, dst in HardwareConfig.FALCON_27_EDGES]

    @staticmethod
    def get_nx_graph() -> nx.Graph:
        """Gibt die Topologie als NetworkX Graph zurück (für Cirq/Analyse)."""
        G = nx.Graph()
        G.add_edges_from(HardwareConfig.FALCON_27_EDGES)
        return G
