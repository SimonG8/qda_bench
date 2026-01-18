import os
import time
from typing import Optional, Tuple, Dict, Any, List

from cirq.ops.matrix_gates import two_qubit_to_cz
from qiskit import QuantumCircuit, transpile
from qiskit import qasm2
from qiskit.circuit.library import XGate, SXGate, RZGate, CXGate, CZGate, IGate, Measure, SwapGate, HGate, RYGate, \
    RXGate, ZGate, YGate
from qiskit.transpiler import Target, PassManager
from qiskit.transpiler.passes import (
    Optimize1qGatesDecomposition, CommutativeCancellation,
    OptimizeSwapBeforeMeasure, RemoveResetInZeroState,
    Collect2qBlocks, ConsolidateBlocks, UnitarySynthesis,
    BasicSwap, LookaheadSwap, SabreSwap,
    TrivialLayout, DenseLayout, SabreLayout, Unroll3qOrMore
)

from quantum_bench.hardware.model import HardwareModel
from .base import CompilerAdapter


class QiskitAdapter(CompilerAdapter):
    def __init__(self, hardware: HardwareModel, export_dir: str = None):
        super().__init__("Qiskit", hardware, export_dir)
        self.target = self._build_target()

    def _build_target(self) -> Target:
        """Erstellt ein Qiskit Target-Objekt aus der Hardware-Konfiguration."""
        num_qubits = self.hardware.num_qubits
        coupling_map = self.hardware.coupling_map
        basis_gates = self.hardware.basis_gates

        target = Target(num_qubits=num_qubits)

        gate_map = {
            "x": XGate(),
            "y": YGate(),
            "z": ZGate(),
            "sx": SXGate(),
            "rz": RZGate(0.0),
            "rx": RXGate(0.0),
            "ry": RYGate(0.0),
            "h": HGate(),
            "cx": CXGate(),
            "cz": CZGate(),
            "id": IGate(),
            "measure": Measure(),
            "swap": SwapGate()
        }

        # Basisgatter hinzufügen
        for gate_name in basis_gates:
            gate_obj = gate_map.get(gate_name.lower())
            if gate_obj:
                if gate_name.lower() in ["cx", "cz"]:
                    # 2-Qubit Gatter auf den definierten Kanten
                    props = {edge: None for edge in coupling_map}
                    target.add_instruction(gate_obj, properties=props)
                else:
                    # 1-Qubit Gatter auf allen Qubits
                    target.add_instruction(gate_obj, properties={(i,): None for i in range(num_qubits)})

        return target

    def compile(self, qasm_file: str, optimization_level: int = 1, active_phases: Optional[List[str]] = None, seed: Optional[int] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        try:
            circuit = QuantumCircuit.from_qasm_file(qasm_file)
        except Exception as e:
            print(f"Qiskit QASM Import Error: {e}")
            return None, None

        start_time = time.time()

        # Wenn keine Phasen spezifiziert sind, nutze Standard-Transpile
        if active_phases is None:
            transpiled_circuit = transpile(
                circuit,
                target=self.target,
                optimization_level=optimization_level,
                seed_transpiler=seed,
            )
        else:
            # Benutzerdefinierte Pipeline
            pm = PassManager()

            if "rebase" in active_phases:
                pm.append(Unroll3qOrMore(self.target))

            # 1. Mapping / Layout
            if "mapping" in active_phases:
                pm.append(SabreLayout(self.target, seed=seed))
                pm.append(SabreSwap(self.target.build_coupling_map(), "decay",seed=seed))

            # 3. Optimierung
            if "optimization" in active_phases:
                pm.append([
                    Optimize1qGatesDecomposition(target=self.target),
                    RemoveResetInZeroState()
                ])
                pm.append(CommutativeCancellation())
                pm.append([
                    Collect2qBlocks(),
                    ConsolidateBlocks(target=self.target),
                    UnitarySynthesis(target=self.target)
                ])
            transpiled_circuit = pm.run(circuit)

        duration = time.time() - start_time
        operations = transpiled_circuit.count_ops()
        gate_count = transpiled_circuit.size()-operations.get('barrier', 0)
        depth = transpiled_circuit.depth()
        two_q_count = transpiled_circuit.num_nonlocal_gates()
        swap_count = operations.get('swap', 0)
        metrics = {
            "gate_count": gate_count,
            "depth": depth,
            "compile_time": duration,
            "2q_gates": two_q_count,
            "swap_gates": swap_count,
        }

        try:
            _, file = os.path.split(qasm_file.removesuffix(".qasm"))
            filename = os.path.join(self.export_dir, f"{file}_qiskit_opt{optimization_level}.qasm")
            qasm2.dump(transpiled_circuit, filename)
        except Exception as e:
            print(f"Qiskit QASM Export Error: {e}")
            return metrics, None

        return metrics, filename
