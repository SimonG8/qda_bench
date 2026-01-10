import pandas as pd
import os
import random
from quantum_bench.data.mqt_provider import BenchmarkProvider
from quantum_bench.compilers.qiskit_adapter import QiskitAdapter
from quantum_bench.compilers.cirq_adapter import CirqAdapter
from quantum_bench.compilers.pytket_adapter import PytketAdapter

# Für Visualisierung
import matplotlib.pyplot as plt
import cirq.contrib.svg

def save_circuit_visualization(circuit, compiler_name, algo_name, n_qubits, opt_level, hardware_name):
    """
    Speichert eine Visualisierung des Schaltkreises in visualizations/circuits/{hardware_name}.
    """
    base_vis_dir = "visualizations"
    circuit_dir = os.path.join(base_vis_dir, "circuits", hardware_name)
    
    if not os.path.exists(circuit_dir):
        os.makedirs(circuit_dir)
        
    filename_base = os.path.join(circuit_dir, f"{algo_name}_{n_qubits}_{compiler_name}_opt{opt_level}")
    
    try:
        if compiler_name == "Qiskit" or compiler_name == "Original":
            fig = circuit.draw(output='mpl', style='iqp')
            fig.savefig(f"{filename_base}.png")
            plt.close(fig)
            
        elif compiler_name == "Cirq":
            with open(f"{filename_base}.txt", "w", encoding="utf-8") as f:
                f.write(str(circuit))
            with open(f"{filename_base}.svg", "w", encoding="utf-8") as f:
                f.write(cirq.contrib.svg.circuit_to_svg(circuit))

        elif compiler_name == "pytket":
            from pytket.extensions.qiskit import tk_to_qiskit
            try:
                qc = tk_to_qiskit(circuit, replace_implicit_swaps=True)
                fig = qc.draw(output='mpl', style='iqp')
                fig.savefig(f"{filename_base}.png")
                plt.close(fig)
            except Exception as e:
                print(f"Pytket Vis Error: {e}")

    except Exception as e:
        print(f"Konnte Visualisierung nicht speichern für {filename_base}: {e}")

def run_benchmark(hardware_configs, algorithms, qubit_ranges, num_runs=1):
    """
    Führt den Benchmark durch.
    
    Args:
        hardware_configs: Liste der Hardware-Konfigurationen (z.B. [Falcon27(), Grid25()])
        algorithms: Liste der Algorithmen-Namen (z.B. ['ghz', 'qft'])
        qubit_ranges: Liste der Qubit-Anzahlen (z.B. [5, 10, 15])
        num_runs: Anzahl der Wiederholungen pro Konfiguration für Statistik
    """
    provider = BenchmarkProvider()
    
    results = []

    print(f"Starte Benchmarking-Suite ({num_runs} Runs pro Config)...")
    
    for hardware in hardware_configs:
        print(f"\n=== Hardware: {hardware.name} ===")
        
        compilers = [
            QiskitAdapter(hardware), 
            CirqAdapter(hardware), 
            PytketAdapter(hardware)
        ]
        
        for algo in algorithms:
            for n_qubits in qubit_ranges:
                if n_qubits > hardware.num_qubits:
                    continue
                    
                print(f"--- Benchmark: {algo} ({n_qubits} Qubits) ---")
                
                qasm_path = provider.get_circuit(algo, n_qubits)
                if not qasm_path:
                    continue
                
                # Original-Schaltkreis visualisieren (nur bei 5 Qubits)
                if n_qubits == 5:
                    try:
                        from qiskit import QuantumCircuit
                        qc_orig = QuantumCircuit.from_qasm_file(qasm_path)
                        save_circuit_visualization(qc_orig, "Original", algo, n_qubits, 0, hardware.name)
                    except Exception as e:
                        print(f"Fehler bei Original-Visualisierung: {e}")

                for compiler in compilers:
                    for opt_level in [0, 3]:
                        for run_i in range(num_runs):
                            seed = random.randint(0, 100000)
                            
                            row = {
                                "hardware": hardware.name,
                                "algorithm": algo,
                                "qubits": n_qubits,
                                "compiler": compiler.name,
                                "opt_level": opt_level,
                                "run": run_i,
                                "seed": seed
                            }
                            
                            try:
                                metrics = compiler.compile(qasm_path, opt_level, seed=seed)
                                
                                if metrics:
                                    # Visualisierung speichern (nur 5 Qubits, Opt 3, Run 0)
                                    if n_qubits == 5 and opt_level == 3 and run_i == 0 and "mapped_circuit" in metrics:
                                        save_circuit_visualization(
                                            metrics["mapped_circuit"], 
                                            compiler.name, 
                                            algo, 
                                            n_qubits, 
                                            opt_level,
                                            hardware.name
                                        )
                                    
                                    if "mapped_circuit" in metrics:
                                        del metrics["mapped_circuit"]
                                        
                                    row.update(metrics)
                                    row["success"] = True
                                else:
                                    row["success"] = False
                                    
                            except Exception as e:
                                row["success"] = False
                                row["error"] = str(e)
                            
                            print(row)
                            results.append(row)

    df = pd.DataFrame(results)
    df.to_csv("benchmark_results_final.csv", index=False)
    print("Benchmark abgeschlossen. Ergebnisse gespeichert.")
