import time
from qiskit import QuantumCircuit, transpile, qasm2
from qiskit.transpiler import Target, InstructionProperties
from qiskit.circuit.library import XGate, SXGate, RZGate, CXGate, Measure
from .base import CompilerAdapter
from ..config import HardwareConfig

class QiskitAdapter(CompilerAdapter):
    def __init__(self):
        super().__init__("Qiskit")
        self.target = self._build_target()

    def _build_target(self) -> Target:
        """Erstellt ein Qiskit Target-Objekt aus der Falcon-Konfiguration."""
        coupling_map = HardwareConfig.get_coupling_map()
        # Qiskit Target erlaubt feingranulare Definition 
        target = Target(num_qubits=27)
        
        # Hinzufügen der Basisgatter (Idealisiert, ohne Fehlerwerte für diesen Benchmark)
        target.add_instruction(XGate(), properties={(i,): None for i in range(27)})
        target.add_instruction(SXGate(), properties={(i,): None for i in range(27)})
        target.add_instruction(RZGate(0.0), properties={(i,): None for i in range(27)})
        
        # WICHTIG: Measure-Instruktion hinzufügen, sonst schlägt Synthese fehl
        target.add_instruction(Measure(), properties={(i,): None for i in range(27)})
        
        # CX Gatter nur auf den definierten Kanten
        cx_props = {tuple(edge): None for edge in coupling_map}
        target.add_instruction(CXGate(), properties=cx_props)
        
        return target

    def compile(self, qasm_file: str, opt_level: int) -> dict:
        # Import: Nutzung des performanteren qasm2 Moduls
        try:
            qc = qasm2.load(qasm_file)
        except Exception as e:
             # Fallback für QASM 3 Import falls nötig
             from qiskit import qasm3
             with open(qasm_file, 'r') as f:
                 qc = qasm3.loads(f.read())

        start_time = time.time()
        # Transpilation
        # seed_transpiler=42 sorgt für Determinismus bei SABRE (Level 3)
        transpiled_qc = transpile(
            qc,
            target=self.target,
            optimization_level=opt_level,
            seed_transpiler=42
        )
        duration = time.time() - start_time
        
        # Metriken extrahieren
        # count_ops() gibt ein Dict zurück
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
