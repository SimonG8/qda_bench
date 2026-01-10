import time
from typing import Optional
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import Target
from qiskit.circuit.library import XGate, SXGate, RZGate, CXGate, Measure
from .base import CompilerAdapter
from quantum_bench.hardware.config import HardwareModel

class QiskitAdapter(CompilerAdapter):
    def __init__(self, hardware: HardwareModel):
        super().__init__("Qiskit", hardware)
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

    def compile(self, qasm_file: str, opt_level: int, seed: Optional[int] = None) -> dict:
        try:
            qc = QuantumCircuit.from_qasm_file(qasm_file)
        except Exception as e:
             from qiskit import qasm3
             with open(qasm_file, 'r') as f:
                 qc = qasm3.loads(f.read())

        start_time = time.time()
        
        transpiled_qc = transpile(
            qc,
            target=self.target,
            optimization_level=opt_level,
            seed_transpiler=seed
        )
        duration = time.time() - start_time
        
        ops = transpiled_qc.count_ops()
        gate_count = sum(ops.values())
        depth = transpiled_qc.depth()
        
        return {
            "gate_count": gate_count,
            "depth": depth,
            "compile_time": duration,
            "2q_gates": ops.get('cx', 0),
            "swap_gates": ops.get('swap', 0),
            "mapped_circuit": transpiled_qc
        }
