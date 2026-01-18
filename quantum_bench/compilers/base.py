import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple, List

from quantum_bench.hardware.model import HardwareModel


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
    def compile(self, qasm_file: str, optimization_level: int = 1, active_phases: Optional[List[str]] = None, seed: Optional[int] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Kompiliert den gegebenen QASM-Schaltkreis.

        Args:
            qasm_file: Pfad zur QASM-Datei.
            optimization_level: Allgemeines Optimierungslevel (0-3).
            active_phases: Liste der aktiven Phasen (z.B. ["mapping", "routing", "optimization"]). None = alle.
            optimization_passes: Liste der spezifischen Optimierungen (z.B. ["peephole", "kak"]).
            seed: Random Seed.

        Returns:
            Dictionary mit Metriken und Pfad zur kompilierten Datei.
        """
        pass
