import os
import time
from typing import Optional, Tuple, Dict, Any, List

from pytket import OpType
from pytket._tket.passes import AutoRebase, RebaseTket
from pytket.architecture import Architecture
from pytket.mapping import MappingManager, LexiLabellingMethod, LexiRouteRoutingMethod
from pytket.passes import (
    FullPeepholeOptimise,
    RemoveRedundancies,
    DecomposeBoxes, KAKDecomposition, CliffordSimp,
    ContextSimp, PeepholeOptimise2Q, PauliSimp, DecomposeSwapsToCXs
)
from pytket.qasm import circuit_from_qasm, circuit_to_qasm

from quantum_bench.hardware.model import HardwareModel
from .base import CompilerAdapter


class PytketAdapter(CompilerAdapter):
    """Adapter for the Pytket compiler."""

    def __init__(self, hardware: HardwareModel, export_dir: str = None):
        super().__init__("Pytket", hardware, export_dir)
        self.architecture = Architecture(hardware.coupling_map)
        self.mapping_manager = MappingManager(self.architecture)
        self.basis_gates = self._define_gateset()

    def _define_gateset(self):
        gate_map = {
            "x": OpType.X,
            "y": OpType.Y,
            "z": OpType.Z,
            "sx": OpType.SX,
            "rz": OpType.Rz,
            "rx": OpType.Rx,
            "ry": OpType.Ry,
            "h": OpType.H,
            "cx": OpType.CX,
            "cz": OpType.CZ,
            "id": OpType.noop,
            "measure": OpType.Measure,
            "swap": OpType.SWAP
        }
        return {gate_map[g.lower()] for g in self.hardware.basis_gates if g.lower() in gate_map}

    def compile(self, qasm_file: str, optimization_level: int = 1, active_phases: Optional[List[str]] = None, seed: Optional[int] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        try:
            circuit = circuit_from_qasm(qasm_file, maxwidth=128)
        except Exception as e:
            print(f"Pytket QASM Import Error: {e}")
            return None, None

        initial_metrics = self._calculate_metrics(circuit)
        initial_metrics["compile_time"] = '-'

        start_time = time.time()

        if active_phases is None:
            active_phases = ["rebase", "mapping", "optimization"]

        if "rebase" in active_phases:
            try:
                DecomposeBoxes().apply(circuit)
                AutoRebase(self.basis_gates).apply(circuit)
            except Exception:
                RebaseTket().apply(circuit)

        if "optimization" in active_phases:
            FullPeepholeOptimise().apply(circuit)
            CliffordSimp().apply(circuit)
            ContextSimp().apply(circuit)

        if "mapping" in active_phases:
            # Lookahead based on Opt-Level
            lookahead = 0
            if optimization_level == 1: lookahead = 2
            if optimization_level >= 2: lookahead = 5

            lexi_label = LexiLabellingMethod()
            lexi_route = LexiRouteRoutingMethod(lookahead)
            self.mapping_manager.route_circuit(circuit, [lexi_label, lexi_route])

        if "optimization" in active_phases:
            PeepholeOptimise2Q().apply(circuit)
            KAKDecomposition().apply(circuit)
            RemoveRedundancies().apply(circuit)

        duration = time.time() - start_time
        metrics = self._calculate_metrics(circuit)
        metrics["compile_time"] = duration
        metrics["initial"] = initial_metrics

        circuit.remove_blank_wires()
        filename = self._save_circuit(circuit, qasm_file, optimization_level)
        
        return (metrics, filename) if filename else (metrics, None)

    def _calculate_metrics(self, circuit) -> Dict[str, Any]:
        return {
            "gate_count": circuit.n_gates - circuit.n_gates_of_type(OpType.Barrier),
            "depth": circuit.depth(),
            "2q_gates": circuit.n_2qb_gates(),
            "swap_gates": circuit.n_gates_of_type(OpType.SWAP),
        }

    def _save_circuit(self, circuit, original_file: str, opt_level: int) -> Optional[str]:
        try:
            _, file = os.path.split(original_file.removesuffix(".qasm"))
            filename = os.path.join(self.export_dir, f"{file}_pytket_opt{opt_level}.qasm")
            circuit_to_qasm(circuit, filename, maxwidth=128)
            return filename
        except Exception as e:
            print(f"Pytket QASM Export Error: {e}")
            return None
