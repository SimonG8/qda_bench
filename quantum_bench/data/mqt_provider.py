import os
from mqt.bench import get_benchmark, BenchmarkLevel
from qiskit import QuantumCircuit, qasm2

class BenchmarkProvider:
    """
    Verwaltet den Zugriff auf MQT Bench Schaltkreise.
    """
    
    def __init__(self, export_dir: str = "benchmarks_cache"):
        self.export_dir = export_dir
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)

    def get_circuit(self, algo_name: str, num_qubits: int) -> str:
        """
        Lädt einen Benchmark-Schaltkreis und gibt den OpenQASM 2 String zurück.
        Wir nutzen QASM 2 als neutrales Austauschformat, da Qiskit's from_qasm_file
        standardmäßig QASM 2 erwartet und Cirq/pytket damit besser klarkommen.
        
        Args:
            algo_name: Name des Algorithmus (z.B. 'dj', 'ghz', 'qft').
            num_qubits: Anzahl der Qubits.
        
        Returns:
            Pfad zur generierten QASM-Datei oder der QASM-String.
        """
        try:
            # Abruf des Schaltkreises auf Algorithmischer Ebene 
            qc = get_benchmark(
                benchmark=algo_name,
                level=BenchmarkLevel.ALG,
                circuit_size=num_qubits
            )
            
            # Export zu OpenQASM 2 für maximale Kompatibilität
            filename = os.path.join(self.export_dir, f"{algo_name}_{num_qubits}.qasm")
            
            # Wir nutzen hier Qiskit's qasm2 exporter
            with open(filename, 'w') as f:
                f.write(qasm2.dumps(qc))
                
            return filename
            
        except Exception as e:
            print(f" Benchmark {algo_name} mit {num_qubits} Qubits fehlgeschlagen: {e}")
            return None
