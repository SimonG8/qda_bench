from typing import List, Tuple, Optional

from traci.connection import switch


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
    def coupling_map(self) -> List[Tuple[int,int]]:
        """Gibt die Coupling Map als Liste von Tuples zurück (für Qiskit/pytket)."""
        return self.edges

def get_hardware(hardware_name: str) -> Optional[HardwareModel]:
    match hardware_name:
        case _: return None