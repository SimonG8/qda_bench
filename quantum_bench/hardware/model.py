from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class HardwareModel:
    """
    Represents a quantum hardware model including its topology and basis gates.
    """
    name: str
    num_qubits: int
    edges: List[Tuple[int, int]]
    basis_gates: List[str]

    @property
    def coupling_map(self) -> List[Tuple[int, int]]:
        """Returns the coupling map as a list of tuples."""
        return self.edges


def get_hardware(hardware_name: str) -> Optional[HardwareModel]:
    """
    Factory function to retrieve a hardware model by name.
    
    Args:
        hardware_name: Name of the hardware to retrieve.
        
    Returns:
        HardwareModel instance or None if not found.
    """
    return None
