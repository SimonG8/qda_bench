import os
import time
from typing import Optional, Tuple, Dict, Any, List

from cirq_ionq import GPIGate, GPI2Gate, ZZGate
from mqt.bench.targets.gatesets.rigetti import RXPIGate, RXPI2Gate, RXPI2DgGate
from qiskit import QuantumCircuit, transpile, qasm2
from qiskit.circuit import Delay
from qiskit.circuit.library import (
    XGate, YGate, ZGate, SXGate, RZGate, RXGate, RYGate, HGate,
    CXGate, CZGate, IGate, Measure, Reset, SwapGate, ECRGate, iSwapGate
)
from qiskit.circuit.equivalence_library import SessionEquivalenceLibrary
from qiskit.transpiler import Target, PassManager
from qiskit.transpiler.passes import (
    Optimize1qGatesDecomposition, CommutativeCancellation,
    RemoveResetInZeroState, Collect2qBlocks, ConsolidateBlocks,
    UnitarySynthesis, SabreSwap, SabreLayout, Unroll3qOrMore,
    BasisTranslator, RemoveDiagonalGatesBeforeMeasure,
    RemoveFinalReset, InverseCancellation
)

from quantum_bench.hardware.model import HardwareModel
from .base import CompilerAdapter


class QiskitAdapter(CompilerAdapter):
    """Adapter for the Qiskit compiler."""

    def __init__(self, hardware: HardwareModel, export_dir: str = None):
        super().__init__("Qiskit", hardware, export_dir)
        self.target = self._build_target()

    def _build_target(self) -> Target:
        """Creates a Qiskit Target object from the hardware configuration."""
        target = Target(num_qubits=self.hardware.num_qubits)
        
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
            "reset": Reset(),
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

        for gate_name in self.hardware.basis_gates:
            gate_obj = gate_map.get(gate_name.lower())
            if not gate_obj:
                continue
                
            if gate_obj.num_qubits == 2:
                props = {edge: None for edge in self.hardware.coupling_map}
                target.add_instruction(gate_obj, properties=props)
            else:
                props = {(i,): None for i in range(self.hardware.num_qubits)}
                target.add_instruction(gate_obj, name=gate_name, properties=props)

        return target

    def compile(self, qasm_file: str, optimization_level: int = 1, active_phases: Optional[List[str]] = None, seed: Optional[int] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        try:
            circuit = QuantumCircuit.from_qasm_file(qasm_file)
        except Exception as e:
            print(f"Qiskit QASM Import Error: {e}")
            return None, None

        initial_metrics = self._calculate_metrics(circuit)
        initial_metrics["compile_time"] = '-'

        start_time = time.time()

        if active_phases is None:
            transpiled_circuit = transpile(
                circuit,
                target=self.target,
                optimization_level=optimization_level,
                seed_transpiler=seed,
            )
        else:
            transpiled_circuit = self._run_custom_pass_manager(circuit, active_phases, optimization_level, seed)

        duration = time.time() - start_time
        metrics = self._calculate_metrics(transpiled_circuit)
        metrics["compile_time"] = duration
        metrics["initial"] = initial_metrics

        filename = self._save_circuit(transpiled_circuit, qasm_file, optimization_level)
        return (metrics, filename) if filename else (metrics, None)

    def _run_custom_pass_manager(self, circuit, active_phases, optimization_level, seed):
        pm = PassManager()

        if "rebase" in active_phases:
            pm.append(Unroll3qOrMore(self.target))

        if "mapping" in active_phases:
            pm.append(SabreLayout(self.target, seed=seed))
            pm.append(SabreSwap(self.target.build_coupling_map(), seed=seed))

        if "optimization" in active_phases:
            pm.append(BasisTranslator(SessionEquivalenceLibrary, target=self.target))
            pm.append([Optimize1qGatesDecomposition(target=self.target), RemoveResetInZeroState()])
            pm.append(InverseCancellation([(CXGate(), CXGate())]))
            pm.append(CommutativeCancellation())

            if optimization_level >= 2:
                pm.append([
                    Collect2qBlocks(),
                    ConsolidateBlocks(target=self.target),
                    UnitarySynthesis(target=self.target)
                ])

            pm.append([RemoveDiagonalGatesBeforeMeasure(), RemoveFinalReset()])

        return pm.run(circuit)

    def _calculate_metrics(self, circuit: QuantumCircuit) -> Dict[str, Any]:
        operations = circuit.count_ops()
        return {
            "gate_count": circuit.size() - operations.get('barrier', 0),
            "depth": circuit.depth(),
            "2q_gates": circuit.num_nonlocal_gates(),
            "swap_gates": operations.get('swap', 0),
        }

    def _save_circuit(self, circuit: QuantumCircuit, original_file: str, opt_level: int) -> Optional[str]:
        try:
            _, file = os.path.split(original_file.removesuffix(".qasm"))
            filename = os.path.join(self.export_dir, f"{file}_qiskit_opt{opt_level}.qasm")
            qasm2.dump(circuit, filename)
            return filename
        except Exception as e:
            print(f"Qiskit QASM Export Error: {e}")
            return None
