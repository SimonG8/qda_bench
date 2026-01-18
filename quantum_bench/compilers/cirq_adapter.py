import os
import time
from typing import Optional, Tuple, Dict, Any, List

import cirq
import networkx as nx
from cirq import CZTargetGateset
from cirq.contrib.qasm_import import circuit_from_qasm

from quantum_bench.hardware.model import HardwareModel
from .base import CompilerAdapter


class GenericDevice(cirq.Device):
    """
    Generic Cirq Device class dynamically created from a HardwareModel.
    """

    def __init__(self, hardware: HardwareModel):
        self.coupling_map = nx.Graph(hardware.coupling_map)
        self.graph = nx.relabel_nodes(self.coupling_map, lambda x: cirq.NamedQubit(str(x)))
        self.qubits = list(self.graph.nodes)
        self._metadata = cirq.DeviceMetadata(self.qubits, nx_graph=self.graph)
        self.basis_gates = self._define_gateset(hardware.basis_gates)

    @property
    def metadata(self):
        return self._metadata

    def _define_gateset(self, basis_gates):
        # Map string names to Cirq Gate Types
        gate_map = {
            "x": cirq.X,
            "y": cirq.Y,
            "z": cirq.Z,
            "sx": cirq.S,
            "rz": cirq.Rz,
            "rx": cirq.Rx,
            "ry": cirq.Ry,
            "h": cirq.H,
            "cx": cirq.CNOT,
            "cz": cirq.CZ,
            "id": cirq.I,
            "measure": cirq.measure,
            "swap": cirq.SWAP
        }

        allowed_gates = set()
        for g in basis_gates:
            if g.lower() in gate_map:
                allowed_gates.add(gate_map[g.lower()])
        return allowed_gates

    def validate_operation(self, operation):
        if len(operation.qubits) == 2:
            u, v = operation.qubits
            if not self.coupling_map.has_edge(u, v):
                raise ValueError(f"Qubits {u} and {v} are not connected.")

        if operation.gate not in self.basis_gates:
            # This is a simplified check; real validation might be more complex
            pass


class CirqAdapter(CompilerAdapter):
    def __init__(self, hardware: HardwareModel, export_dir: str = None):
        super().__init__("Cirq", hardware, export_dir)
        self.device = GenericDevice(hardware)
        self.device_graph = self.device.metadata.nx_graph
        self.target_gateset = self.device.basis_gates

    def compile(self, qasm_file: str, optimization_level: int = 1, active_phases: Optional[List[str]] = None, seed: Optional[int] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        with open(qasm_file, 'r') as f:
            qasm_str = f.read()

        # Remove barriers as they might cause issues in some importers
        qasm_str = "\n".join(line for line in qasm_str.splitlines() if not line.strip().startswith("barrier"))

        try:
            optimized_circuit = circuit_from_qasm(qasm_str)
        except Exception as e:
            print(f"Cirq QASM Import Error: {e}")
            return None, None

        start_time = time.time()

        # 0. Translation
        if active_phases is None or "rebase" in active_phases:
            optimized_circuit = cirq.optimize_for_target_gateset(
                optimized_circuit, gateset=CZTargetGateset()
            )

        # 1. Optimization (Pre-Mapping)
        if active_phases is None or "optimization" in active_phases:
            optimized_circuit = cirq.merge_single_qubit_gates_to_phxz(optimized_circuit)
            optimized_circuit = cirq.drop_negligible_operations(optimized_circuit)
            optimized_circuit = cirq.eject_phased_paulis(optimized_circuit)
            optimized_circuit = cirq.eject_z(optimized_circuit)

        # 2. Mapping & Routing
        if active_phases is None or "mapping" in active_phases:
            # Lookahead based on Opt-Level
            lookahead = 0
            if optimization_level == 1: lookahead = 1
            if optimization_level >= 2: lookahead = 2

            router = cirq.RouteCQC(self.device_graph)
            optimized_circuit = router(optimized_circuit, lookahead_radius=lookahead)

        # 3. Optimization (Post-Mapping)
        if active_phases is None or "optimization" in active_phases:
            optimized_circuit = cirq.drop_empty_moments(optimized_circuit)

        duration = time.time() - start_time
        operations = list(optimized_circuit.all_operations())
        gate_count = len(operations)
        depth = len(optimized_circuit)
        two_q_count = sum(1 for op in operations if len(op.qubits) == 2)
        swap_count = sum(1 for op in operations if isinstance(op.gate, cirq.SwapPowGate))

        metrics = {
            "gate_count": gate_count,
            "depth": depth,
            "compile_time": duration,
            "2q_gates": two_q_count,
            "swap_gates": swap_count,
        }

        try:
            _, file = os.path.split(qasm_file.removesuffix(".qasm"))
            filename = os.path.join(self.export_dir, f"{file}_cirq_opt{optimization_level}.qasm")
            optimized_circuit.save_qasm(filename)
        except Exception as e:
            print(f"Cirq QASM Export Error: {e}")
            return metrics, None

        return metrics, filename
