from abc import ABC, abstractmethod
from typing import Dict, Any

class CompilerAdapter(ABC):
    """
    Abstraktes Interface für alle Quanten-Compiler.
    """
    
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def compile(self, qasm_file: str, opt_level: int) -> Dict[str, Any]:
        """
        Kompiliert den gegebenen QASM-Schaltkreis.
        
        Args:
            qasm_file: Pfad zur QASM-Datei.
            opt_level: Optimierungsstufe (0, 1, 2, 3).
            
        Returns:
            Ein Dictionary mit Metriken:
            - 'gate_count': Gesamtanzahl Gatter
            - 'depth': Tiefe des Schaltkreises
            - 'compile_time': Benötigte Zeit in Sekunden
            - 'mapped_circuit': Das kompilierte Objekt (optional)
        """
        pass
