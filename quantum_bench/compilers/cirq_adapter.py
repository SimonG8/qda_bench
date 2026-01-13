import os
import re
import time
from typing import Optional, Tuple, Dict, Any

import cirq
import networkx as nx
from cirq.contrib.qasm_import import circuit_from_qasm

from quantum_bench.hardware.config import HardwareModel
from .base import CompilerAdapter


class GenericDevice(cirq.Device):
    """
    Generische Cirq-Device Klasse, die dynamisch aus einem HardwareModel erzeugt wird.
    """

    def __init__(self, hardware: HardwareModel):
        # Convert int graph to LineQubit graph
        int_graph = hardware.nx_graph
        # Relabel nodes from int to LineQubit
        self.graph = nx.relabel_nodes(int_graph, lambda x: cirq.LineQubit(x))
        self.qubits = list(self.graph.nodes)
        self._metadata = cirq.DeviceMetadata(self.qubits, nx_graph=self.graph)

    @property
    def metadata(self):
        return self._metadata

    def validate_operation(self, operation):
        if not super().validate_operation(operation):
            return False
        if len(operation.qubits) == 2:
            u, v = operation.qubits
            if not self.graph.has_edge(u, v):
                raise ValueError(f"Qubits {u} und {v} nicht verbunden.")


class CirqAdapter(CompilerAdapter):
    def __init__(self, hardware: HardwareModel, export_dir: str = None):
        super().__init__("Cirq", hardware, export_dir)
        self.device = GenericDevice(hardware)
        self.device_graph = self.device.metadata.nx_graph

    def compile(self, qasm_file: str, opt_level: int, seed: Optional[int] = None) -> Tuple[Dict[str, Any], str]:
        with open(qasm_file, 'r') as f:
            qasm_str = f.read()

        qasm_str = "\n".join(line for line in qasm_str.splitlines() if not line.strip().startswith("barrier"))

        try:
            circuit = circuit_from_qasm(qasm_str)
        except Exception as e:
            print(f"Cirq QASM Import Error: {e}")
            return None, None

        def qubit_index(q):
            s = str(q)
            # Sucht nach der ersten zusammenhängenden Zahl im String
            match = re.search(r'\d+', s)
            if match:
                return int(match.group())
            # Fallback: Hash des Namens, um zumindest deterministisch zu sein
            return hash(s)

        sorted_qubits = sorted(circuit.all_qubits(), key=qubit_index)
        qubit_map = {q: cirq.LineQubit(i) for i, q in enumerate(sorted_qubits)}
        circuit = circuit.transform_qubits(qubit_map)

        start_time = time.time()

        circuit = cirq.optimize_for_target_gateset(
            circuit, gateset=cirq.CZTargetGateset()
        )

        lookahead = 4
        if opt_level >= 2: lookahead = 8
        if opt_level >= 3: lookahead = 15

        router = cirq.RouteCQC(self.device_graph)

        routed_circuit = router(circuit, lookahead_radius=lookahead)

        if opt_level >= 1:
            routed_circuit = cirq.drop_negligible_operations(routed_circuit)
        if opt_level >= 2:
            routed_circuit = cirq.eject_z(routed_circuit)
        if opt_level >= 3:
            routed_circuit = cirq.align_left(routed_circuit)

        duration = time.time() - start_time

        gate_count = len(list(routed_circuit.all_operations()))
        depth = len(routed_circuit)

        two_q_count = sum(1 for op in routed_circuit.all_operations() if len(op.qubits) == 2)

        swap_count = 0
        for op in routed_circuit.all_operations():
            if isinstance(op.gate, cirq.SwapPowGate) and op.gate.exponent == 1.0:
                swap_count += 1

        metrics = {
            "gate_count": gate_count,
            "depth": depth,
            "compile_time": duration,
            "2q_gates": two_q_count,
            "swap_gates": swap_count,
        }

        try:
            _, file = os.path.split(qasm_file.removesuffix(".qasm"))
            filename = os.path.join(self.export_dir, f"{file}_cirq_opt{opt_level}.qasm")
            with open(filename, 'w') as f:
                f.write(routed_circuit.to_qasm())
        except Exception as e:
            print(f"Cirq QASM Export Error: {e}")
            return metrics, None

        return metrics, filename
