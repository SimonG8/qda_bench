import pandas as pd
import traceback
from tqdm import tqdm
from quantum_bench.data.mqt_provider import BenchmarkProvider
from quantum_bench.compilers.qiskit_adapter import QiskitAdapter
from quantum_bench.compilers.cirq_adapter import CirqAdapter
from quantum_bench.compilers.pytket_adapter import PytketAdapter

def run_benchmark():
    # Setup
    provider = BenchmarkProvider()
    compilers = [QiskitAdapter(), CirqAdapter(), PytketAdapter()]
    
    # Test-Matrix definieren
    # MQT Bench Algorithmen [15]
    algorithms = ['ghz', 'dj', 'qft', 'grover']
    # Qubit-Anzahlen: Müssen <= 27 (Falcon) sein.
    qubit_ranges = [5, 10, 15, 20, 25]
    
    results = []

    print("Starte Benchmarking-Suite auf IBM Falcon 27 Topologie...")
    
    # Iteration über alle Kombinationen
    for algo in algorithms:
        for n_qubits in qubit_ranges:
            print(f"--- Benchmark: {algo} ({n_qubits} Qubits) ---")

            #Skip grover >15
            if algo == 'grover' and n_qubits >= 15:
                continue

            # 1. Schaltkreis abrufen
            qasm_path = provider.get_circuit(algo, n_qubits)
            if not qasm_path:
                continue
                
            for compiler in compilers:
                # Wir testen nur Opt-Level 0 (Baseline) und 3 (Max) für die These
                # um die Laufzeit in Grenzen zu halten.
                for opt_level in [3]:
                    row = {
                        "algorithm": algo,
                        "qubits": n_qubits,
                        "compiler": compiler.name,
                        "opt_level": opt_level
                    }
                    
                    try:
                        # Kompilierung ausführen
                        metrics = compiler.compile(qasm_path, opt_level)
                        
                        if metrics:
                            row.update(metrics)
                            row["success"] = True
                        else:
                            row["success"] = False
                            
                    except Exception as e:
                        print(f"Fehler bei {compiler.name} {algo}-{n_qubits}: {e}")
                        # traceback.print_exc()
                        row["success"] = False
                        row["error"] = str(e)
                    print(row)
                    results.append(row)

    # Speichern der Rohdaten
    df = pd.DataFrame(results)
    df.to_csv("benchmark_results_final.csv", index=False)
    print("Benchmark abgeschlossen. Ergebnisse gespeichert.")

if __name__ == "__main__":
    run_benchmark()
