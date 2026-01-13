import os
import time
from typing import Optional, Tuple, Dict, Any
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import Target
from qiskit import qasm2
from qiskit.circuit.library import XGate, SXGate, RZGate, CXGate, Measure
from .base import CompilerAdapter
from quantum_bench.hardware.config import HardwareModel

class QiskitAdapter(CompilerAdapter):
    def __init__(self, hardware: HardwareModel,export_dir: str = None):
        super().__init__("Qiskit", hardware,export_dir)
        self.target = self._build_target()

    def _build_target(self) -> Target:
        """Erstellt ein Qiskit Target-Objekt aus der Hardware-Konfiguration."""
        coupling_map = self.hardware.coupling_map
        num_qubits = self.hardware.num_qubits
        
        target = Target(num_qubits=num_qubits)
        
        # Basisgatter hinzufügen
        target.add_instruction(XGate(), properties={(i,): None for i in range(num_qubits)})
        target.add_instruction(SXGate(), properties={(i,): None for i in range(num_qubits)})
        target.add_instruction(RZGate(0.0), properties={(i,): None for i in range(num_qubits)})
        target.add_instruction(Measure(), properties={(i,): None for i in range(num_qubits)})
        
        # CX Gatter auf den definierten Kanten
        cx_props = {tuple(edge): None for edge in coupling_map}
        target.add_instruction(CXGate(), properties=cx_props)
        
        return target

    def compile(self, qasm_file: str, opt_level: int, seed: Optional[int] = None) -> Tuple[Dict[str, Any], str]:
        try:
            circuit = QuantumCircuit.from_qasm_file(qasm_file)
        except Exception as e:
            print(f"Qiskit QASM Import Error: {e}")
            return None, None

        start_time = time.time()
        
        transpiled_circuit = transpile(
            circuit,
            target=self.target,
            optimization_level=opt_level,
            seed_transpiler=seed,

        )
        duration = time.time() - start_time

        ops = transpiled_circuit.count_ops()
        gate_count = sum(ops.values())
        depth = transpiled_circuit.depth()
        
        metrics = {
            "gate_count": gate_count,
            "depth": depth,
            "compile_time": duration,
            "2q_gates": ops.get('cx', 0),
            "swap_gates": ops.get('swap', 0),
        }

        try:
            _, file = os.path.split(qasm_file.removesuffix(".qasm"))
            filename = os.path.join(self.export_dir, f"{file}_qiskit_opt{opt_level}.qasm")
            qasm2.dump(transpiled_circuit, filename)
        except Exception as e:
            print(f"Qiskit QASM Export Error: {e}")
            return metrics, None

        return metrics, filename
