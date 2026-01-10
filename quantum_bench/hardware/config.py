from typing import List, Tuple
import networkx as nx

class HardwareModel:
    """
    Basisklasse für Hardware-Modelle.
    """
    def __init__(self, name: str, num_qubits: int, edges: List[Tuple[int, int]], basis_gates: List[str]):
        self.name = name
        self.num_qubits = num_qubits
        self.edges = edges
        self.basis_gates = basis_gates

    @property
    def coupling_map(self) -> List[List[int]]:
        """Gibt die Coupling Map als Liste von Listen zurück (für Qiskit/pytket)."""
        return [[src, dst] for src, dst in self.edges]

    @property
    def nx_graph(self) -> nx.Graph:
        """Gibt die Topologie als NetworkX Graph zurück (für Cirq/Analyse)."""
        G = nx.Graph()
        G.add_edges_from(self.edges)
        return G

class Falcon27(HardwareModel):
    """
    IBM Falcon r5.11 Prozessor (27 Qubits, Heavy-Hex Lattice).
    """
    def __init__(self):
        # Adjazenzliste basierend auf der Heavy-Hex-Struktur
        edges = [
            (0, 1), (1, 0), (1, 2), (1, 4), (2, 1), (2, 3), (3, 2), (3, 5),
            (4, 1), (4, 7), (5, 3), (5, 8), (6, 7), (7, 4), (7, 6), (7, 10),
            (8, 5), (8, 9), (8, 11), (9, 8), (10, 7), (10, 12), (11, 8), (11, 14),
            (12, 10), (12, 13), (12, 15), (13, 12), (13, 14), (14, 11), (14, 13), (14, 16),
            (15, 12), (15, 18), (16, 14), (16, 19), (17, 18), (18, 15), (18, 17), (18, 21),
            (19, 16), (19, 20), (19, 22), (20, 19), (21, 18), (21, 23), (22, 19), (22, 25),
            (23, 21), (23, 24), (24, 23), (24, 25), (25, 22), (25, 24), (25, 26), (26, 25)
        ]
        super().__init__("Falcon27", 27, edges, ['cx', 'id', 'rz', 'sx', 'x'])

class Grid25(HardwareModel):
    """
    Generische 5x5 Gitter-Topologie (25 Qubits).
    Höhere Konnektivität (Grad 4 im Zentrum) als Heavy-Hex.
    """
    def __init__(self):
        edges = []
        rows = 5
        cols = 5
        # Gitter-Kanten generieren
        for r in range(rows):
            for c in range(cols):
                idx = r * cols + c
                
                # Kante nach rechts
                if c < cols - 1:
                    right_idx = r * cols + (c + 1)
                    edges.append((idx, right_idx))
                    edges.append((right_idx, idx))
                
                # Kante nach unten
                if r < rows - 1:
                    down_idx = (r + 1) * cols + c
                    edges.append((idx, down_idx))
                    edges.append((down_idx, idx))
                    
        super().__init__("Grid25", 25, edges, ['cx', 'id', 'rz', 'sx', 'x'])
