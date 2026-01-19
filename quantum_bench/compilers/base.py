import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple, List

from quantum_bench.hardware.model import HardwareModel


class CompilerAdapter(ABC):
    """
    Abstract base class for all quantum compiler adapters.
    """

    def __init__(self, name: str, hardware: HardwareModel, export_dir: Optional[str] = None):
        """
        Initializes the compiler adapter.

        Args:
            name: Name of the compiler.
            hardware: The target hardware model.
            export_dir: Directory to export compiled circuits to. Defaults to 'benchmarks_cache/<hardware_name>'.
        """
        self.name = name
        self.hardware = hardware
        if export_dir is None:
            export_dir = os.path.join("benchmarks_cache", hardware.name)
        self.export_dir = export_dir
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)

    @abstractmethod
    def compile(self, qasm_file: str, optimization_level: int = 1, active_phases: Optional[List[str]] = None,
                seed: Optional[int] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Compiles the given QASM circuit.

        Args:
            qasm_file: Path to the QASM file.
            optimization_level: General optimization level (0-3).
            active_phases: List of active phases (e.g., ["rebase", "mapping", "optimization"]).
                           If None, all phases are executed. If empty list, no phases are executed.
            seed: Random seed for reproducibility.

        Returns:
            A tuple containing a dictionary with metrics and the path to the compiled QASM file.
            Returns (None, None) if compilation fails.
        """
        pass
