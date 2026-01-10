from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from quantum_bench.hardware.config import HardwareModel

class CompilerAdapter(ABC):
    """
    Abstraktes Interface für alle Quanten-Compiler.
    """
    
    def __init__(self, name: str, hardware: HardwareModel):
        self.name = name
        self.hardware = hardware

    @abstractmethod
    def compile(self, qasm_file: str, opt_level: int, seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Kompiliert den gegebenen QASM-Schaltkreis.
        """
        pass
