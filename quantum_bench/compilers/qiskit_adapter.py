import os
import time
from typing import Optional, Tuple, Dict, Any, List

from cirq_ionq import GPIGate, GPI2Gate, ZZGate
from mqt.bench.targets.gatesets.rigetti import RXPIGate, RXPI2Gate, RXPI2DgGate
from qiskit import QuantumCircuit, transpile
from qiskit import qasm2
from qiskit.circuit import Delay
from qiskit.circuit.library import *
from qiskit.circuit.equivalence_library import SessionEquivalenceLibrary
from qiskit.transpiler import Target, PassManager
from qiskit.transpiler.passes import (
    Optimize1qGatesDecomposition, CommutativeCancellation,
    RemoveResetInZeroState,
    Collect2qBlocks, ConsolidateBlocks, UnitarySynthesis,
    SabreSwap,
    SabreLayout, Unroll3qOrMore,
    VF2Layout, ApplyLayout, BasisTranslator,
    RemoveDiagonalGatesBeforeMeasure, RemoveFinalReset,
    InverseCancellation
)

from quantum_bench.hardware.model import HardwareModel
from .base import CompilerAdapter


class QiskitAdapter(CompilerAdapter):
    def __init__(self, hardware: HardwareModel, export_dir: str = None):
        super().__init__("Qiskit", hardware, export_dir)
        self.target = self._build_target()

    def _build_target(self) -> Target:
        """Creates a Qiskit Target object from the hardware configuration."""
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
            "swap": SwapGate(),
            "ecr": ECRGate(),
            "delay": Delay(0),
            "rxpi": RXPIGate(),
            "rxpi2": RXPI2Gate(),
            "rxpi2dg": RXPI2DgGate(),
            "iswap": iSwapGate(),
            "gpi": GPIGate(phi=0),
            "gpi2": GPI2Gate(phi=0),
            "zz": ZZGate(theta=0),
        }

        # Add basis gates
        for gate_name in basis_gates:
            gate_obj = gate_map.get(gate_name.lower())
            if gate_obj:
                if gate_name.lower() in ["cx", "cz", "ecr"]:
                    # 2-Qubit gates on defined edges
                    props = {edge: None for edge in coupling_map}
                    target.add_instruction(gate_obj, properties=props)
                else:
                    # 1-Qubit gates on all qubits
                    target.add_instruction(gate_obj, properties={(i,): None for i in range(num_qubits)})

        return target

    def compile(self, qasm_file: str, optimization_level: int = 1, active_phases: Optional[List[str]] = None,
                seed: Optional[int] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        try:
            circuit = QuantumCircuit.from_qasm_file(qasm_file)
        except Exception as e:
            print(f"Qiskit QASM Import Error: {e}")
            return None, None

        operations = circuit.count_ops()
        gate_count = circuit.size() - operations.get('barrier', 0)
        depth = circuit.depth()
        two_q_count = circuit.num_nonlocal_gates()
        swap_count = operations.get('swap', 0)
        initial_metrics = {
            "gate_count": gate_count,
            "depth": depth,
            "compile_time": '-',
            "2q_gates": two_q_count,
            "swap_gates": swap_count,
        }

        start_time = time.time()

        # If no phases are specified, use standard transpile
        if active_phases is None:
            transpiled_circuit = transpile(
                circuit,
                target=self.target,
                optimization_level=optimization_level,
                seed_transpiler=seed,
            )
        else:
            pm = PassManager()

            # 0. Unrolling
            if "rebase" in active_phases:
                pm.append(Unroll3qOrMore(self.target))

            # 1. Mapping / Layout
            if "mapping" in active_phases:
                pm.append(SabreLayout(self.target, seed=seed))
                pm.append(SabreSwap(self.target.build_coupling_map(), seed=seed))

            transpiled_circuit = pm.run(circuit)
            swap_count = transpiled_circuit.count_ops().get('swap', 0)

            # 2. Optimization
            if "optimization" in active_phases:
                pm = PassManager()

                # Ensure SWAPs and other gates are decomposed to basis
                pm.append(BasisTranslator(SessionEquivalenceLibrary, target=self.target))

                pm.append([
                    Optimize1qGatesDecomposition(target=self.target),
                    RemoveResetInZeroState()
                ])

                # Inverse cancellation for CNOTs (self-inverse)
                pm.append(InverseCancellation([(CXGate(), CXGate())]))

                pm.append(CommutativeCancellation())

                # More aggressive optimization for higher levels
                if optimization_level >= 2:
                    pm.append([
                        Collect2qBlocks(),
                        ConsolidateBlocks(target=self.target),
                        UnitarySynthesis(target=self.target)
                    ])

                # Cleanup
                pm.append([
                    RemoveDiagonalGatesBeforeMeasure(),
                    RemoveFinalReset()
                ])

                transpiled_circuit = pm.run(circuit)

        duration = time.time() - start_time
        operations = transpiled_circuit.count_ops()
        gate_count = transpiled_circuit.size() - operations.get('barrier', 0)
        depth = transpiled_circuit.depth()
        two_q_count = transpiled_circuit.num_nonlocal_gates()
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
            filename = os.path.join(self.export_dir, f"{file}_qiskit_opt{optimization_level}.qasm")
            qasm2.dump(transpiled_circuit, filename)
        except Exception as e:
            print(f"Qiskit QASM Export Error: {e}")
            return metrics, None

        return metrics, filename
