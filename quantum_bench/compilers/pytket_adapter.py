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
    def __init__(self, hardware: HardwareModel, export_dir: str = None):
        super().__init__("Pytket", hardware, export_dir)
        self.architecture = Architecture(hardware.coupling_map)
        self.mapping_manager = MappingManager(self.architecture)
        self.basis_gates = self._define_gateset()

    def _define_gateset(self):
        # Map string names to Pytket OpTypes
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

        allowed_optypes = set()
        for g in self.hardware.basis_gates:
            if g.lower() in gate_map:
                allowed_optypes.add(gate_map[g.lower()])
        return allowed_optypes

    def compile(self, qasm_file: str, optimization_level: int = 1, active_phases: Optional[List[str]] = None, seed: Optional[int] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        try:
            circuit = circuit_from_qasm(qasm_file,maxwidth=128)
        except Exception as e:
            print(f"Pytket QASM Import Error: {e}")
            return None, None

        gate_count = circuit.n_gates - circuit.n_gates_of_type(OpType.Barrier)
        depth = circuit.depth()
        two_q_count = circuit.n_2qb_gates()
        swap_count = circuit.n_gates_of_type(OpType.SWAP)

        initial_metrics = {
            "gate_count": gate_count,
            "depth": depth,
            "compile_time": '-',
            "2q_gates": two_q_count,
            "swap_gates": swap_count,
        }

        start_time = time.time()

        # If no phases are specified, run all
        if active_phases is None:
            active_phases = ["rebase", "mapping", "optimization"]

        # 0. Rebasing
        if "rebase" in active_phases:
            # Rebase to basis gates
            try:
                DecomposeBoxes().apply(circuit)
                rebase = AutoRebase(self.basis_gates)
            except Exception as e:
                # Fallback if AutoRebase fails
                rebase = RebaseTket()
            rebase.apply(circuit)

        # 1. Optimization before Mapping (Pre-Optimization)
        if "optimization" in active_phases:
            FullPeepholeOptimise().apply(circuit)
            CliffordSimp().apply(circuit)
            ContextSimp().apply(circuit)

        # 2. Mapping & Routing
        if "mapping" in active_phases:
            # Lookahead based on Opt-Level
            lookahead = 0
            if optimization_level == 1: lookahead = 2
            if optimization_level >= 2: lookahead = 5

            lexi_label = LexiLabellingMethod()
            lexi_route = LexiRouteRoutingMethod(lookahead)
            self.mapping_manager.route_circuit(circuit, [lexi_label, lexi_route])

        # 3. Optimization after Mapping (Post-Optimization)
        if "optimization" in active_phases:
            PeepholeOptimise2Q().apply(circuit)
            KAKDecomposition().apply(circuit)
            RemoveRedundancies().apply(circuit)

        duration = time.time() - start_time
        gate_count = circuit.n_gates - circuit.n_gates_of_type(OpType.Barrier)
        depth = circuit.depth()
        two_q_count = circuit.n_2qb_gates()
        swap_count = circuit.n_gates_of_type(OpType.SWAP)

        metrics = {
            "gate_count": gate_count,
            "depth": depth,
            "compile_time": duration,
            "2q_gates": two_q_count,
            "swap_gates": swap_count,
            "initial": initial_metrics
        }

        circuit.remove_blank_wires()

        try:
            _, file = os.path.split(qasm_file.removesuffix(".qasm"))
            filename = os.path.join(self.export_dir, f"{file}_pytket_opt{optimization_level}.qasm")
            circuit_to_qasm(circuit, filename,maxwidth=128)
        except Exception as e:
            print(f"Pytket QASM Export Error: {e}")
            return metrics, None

        return metrics, filename

