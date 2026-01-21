import os
import time
from typing import Optional, Tuple, Dict, Any, List

import cirq
import networkx as nx
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
        self.basis_gates = hardware.basis_gates
        self.gateset = self._create_cirq_gateset()

    @property
    def metadata(self):
        return self._metadata

    def _create_cirq_gateset(self):
        gate_map = {
            "cx": cirq.CNOT,
            "cz": cirq.CZ,
            "x": cirq.X,
            "y": cirq.Y,
            "z": cirq.Z,
            "h": cirq.H,
            "s": cirq.S,
            "t": cirq.T,
            "swap": cirq.SWAP,
            "iswap": cirq.ISWAP,
            "rx": cirq.Rx,
            "ry": cirq.Ry,
            "rz": cirq.Rz,
            "sx": cirq.S ** 0.5,
        }

        families = []
        for gate_name in self.basis_gates:
            g_lower = gate_name.lower()
            if g_lower in gate_map:
                families.append(cirq.GateFamily(gate_map[g_lower]))

        return cirq.ops.Gateset(*families)

    def validate_operation(self, operation):
        if len(operation.qubits) == 2:
            u, v = operation.qubits
            if not self.coupling_map.has_edge(u, v):
                raise ValueError(f"Qubits {u} and {v} are not connected.")

        if operation.gate not in self.gateset:
            raise ValueError(f"Gate {operation.gate} is not supported.")
        pass


class CirqAdapter(CompilerAdapter):
    def __init__(self, hardware: HardwareModel, export_dir: str = None):
        super().__init__("Cirq", hardware, export_dir)
        self.device = GenericDevice(hardware)
        self.device_graph = self.device.metadata.nx_graph
        self.target_gateset = self.device.gateset

    def compile(self, qasm_file: str, optimization_level: int = 1, active_phases: Optional[List[str]] = None,
                seed: Optional[int] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        with open(qasm_file, 'r') as f:
            qasm_str = f.read()

        # Remove barriers
        qasm_str = "\n".join(line for line in qasm_str.splitlines() if not line.strip().startswith("barrier"))

        try:
            optimized_circuit = circuit_from_qasm(qasm_str)
        except Exception as e:
            print(f"Cirq QASM Import Error: {e}")
            return None, None

        operations = list(optimized_circuit.all_operations())
        gate_count = len(operations)
        depth = len(optimized_circuit)
        two_q_count = sum(1 for op in operations if len(op.qubits) == 2)
        swap_count = sum(1 for op in operations if isinstance(op.gate, cirq.SwapPowGate))

        initial_metrics = {
            "gate_count": gate_count,
            "depth": depth,
            "compile_time": None,
            "2q_gates": two_q_count,
            "swap_gates": swap_count,
        }

        start_time = time.time()

        # If no phases are specified, run all
        if active_phases is None:
            active_phases = ["rebase", "mapping", "optimization"]

        # 0. Translation / Rebase
        if "rebase" in active_phases:
            try:
                optimized_circuit = cirq.optimize_for_target_gateset(
                    optimized_circuit,
                    gateset=cirq.CZTargetGateset())
            except Exception as e:
                print(f"Cirq Rebase Error: {e}")

        # 1. Optimization (Pre-Mapping)
        if "optimization" in active_phases:
            optimized_circuit = cirq.merge_single_qubit_gates_to_phxz(optimized_circuit)
            optimized_circuit = cirq.eject_phased_paulis(optimized_circuit)
            optimized_circuit = cirq.eject_z(optimized_circuit)
            optimized_circuit = cirq.align_left(optimized_circuit)
            optimized_circuit = cirq.drop_negligible_operations(optimized_circuit)
            optimized_circuit = cirq.drop_empty_moments(optimized_circuit)
            optimized_circuit = cirq.synchronize_terminal_measurements(optimized_circuit)

        # 2. Mapping & Routing
        if "mapping" in active_phases:
            lookahead = 0
            if optimization_level == 1: lookahead = 1
            if optimization_level >= 2: lookahead = 2

            try:
                router = cirq.RouteCQC(self.device_graph)
                optimized_circuit = router(optimized_circuit, lookahead_radius=lookahead)
            except Exception as e:
                print(f"Cirq Routing Error: {e}")

        # 3. Optimization (Post-Mapping)
        if "optimization" in active_phases:
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
            "initial": initial_metrics
        }

        try:
            _, file = os.path.split(qasm_file.removesuffix(".qasm"))
            filename = os.path.join(self.export_dir, f"{file}_cirq_opt{optimization_level}.qasm")
            optimized_circuit.save_qasm(filename)
        except Exception as e:
            print(f"Cirq QASM Export Error: {e}")
            return metrics, None

        return metrics, filename
