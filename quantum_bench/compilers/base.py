import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple

from quantum_bench.hardware.config import HardwareModel


class CompilerAdapter(ABC):
    """
    Abstraktes Interface für alle Quanten-Compiler.
    """

    def __init__(self, name: str, hardware: HardwareModel, export_dir: str):
        self.name = name
        self.hardware = hardware
        if export_dir is None:
            export_dir = os.path.join("benchmarks_cache", hardware.name)
        self.export_dir = export_dir
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)

    @abstractmethod
    def compile(self, qasm_file: str, opt_level: int, seed: Optional[int] = None) -> Tuple[Dict[str, Any], str]:
        """
        Kompiliert den gegebenen QASM-Schaltkreis.
        Gibt ein Dictionary mit Metriken und das kompilierte Schaltkreis-Objekt zurück.
        """
        pass
