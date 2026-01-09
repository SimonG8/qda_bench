import pandas as pd
import traceback
import os
from tqdm import tqdm
from quantum_bench.data.mqt_provider import BenchmarkProvider
from quantum_bench.compilers.qiskit_adapter import QiskitAdapter
from quantum_bench.compilers.cirq_adapter import CirqAdapter
from quantum_bench.compilers.pytket_adapter import PytketAdapter

# Für Visualisierung
import matplotlib.pyplot as plt
from qiskit.visualization import circuit_drawer as qiskit_drawer
import cirq.contrib.svg
from pytket.circuit.display import render_circuit_jupyter # Nur für Jupyter, wir nutzen Text/PDF Export

def save_circuit_visualization(circuit, compiler_name, algo_name, n_qubits, opt_level):
    """
    Speichert eine Visualisierung des Schaltkreises.
    """
    vis_dir = "visualizations"
    if not os.path.exists(vis_dir):
        os.makedirs(vis_dir)
        
    filename_base = f"{vis_dir}/{algo_name}_{n_qubits}_{compiler_name}_opt{opt_level}"
    
    try:
        if compiler_name == "Qiskit" or compiler_name == "Original":
            # Qiskit: Matplotlib Drawer
            # Original wird auch als Qiskit Circuit übergeben
            fig = circuit.draw(output='mpl', style='iqp')
            fig.savefig(f"{filename_base}.png")
            plt.close(fig)
            
        elif compiler_name == "Cirq":
            # Cirq: Text Diagramm (SVG ist komplexer ohne Browser)
            # Encoding auf utf-8 setzen, um Unicode-Fehler zu vermeiden
            with open(f"{filename_base}.txt", "w", encoding="utf-8") as f:
                f.write(str(circuit))
            # Optional: SVG speichern
            with open(f"{filename_base}.svg", "w", encoding="utf-8") as f:
                f.write(cirq.contrib.svg.circuit_to_svg(circuit))

        elif compiler_name == "pytket":
            # pytket: Konvertierung zu Qiskit für Visualisierung ist oft am einfachsten
            from pytket.extensions.qiskit import tk_to_qiskit
            try:
                # replace_implicit_swaps=True verhindert die Warnung und macht den Circuit kompatibel
                qc = tk_to_qiskit(circuit, replace_implicit_swaps=True)
                fig = qc.draw(output='mpl', style='iqp')
                fig.savefig(f"{filename_base}.png")
                plt.close(fig)
            except Exception as e:
                print(f"Pytket Vis Error: {e}")

    except Exception as e:
        print(f"Konnte Visualisierung nicht speichern für {filename_base}: {e}")

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
            
            # 1. Schaltkreis abrufen
            qasm_path = provider.get_circuit(algo, n_qubits)
            if not qasm_path:
                continue
            
            # Original-Schaltkreis visualisieren (nur bei 5 Qubits)
            if n_qubits == 5:
                try:
                    from qiskit import QuantumCircuit
                    qc_orig = QuantumCircuit.from_qasm_file(qasm_path)
                    save_circuit_visualization(qc_orig, "Original", algo, n_qubits, 0)
                except Exception as e:
                    print(f"Fehler bei Original-Visualisierung: {e}")

            for compiler in compilers:
                # Wir testen nur Opt-Level 0 (Baseline) und 3 (Max) für die These
                # um die Laufzeit in Grenzen zu halten.
                for opt_level in [0, 3]:
                    row = {
                        "algorithm": algo,
                        "qubits": n_qubits,
                        "compiler": compiler.name,
                        "opt_level": opt_level
                    }

                    if algo == 'grover' and n_qubits > 10:
                        continue

                    try:
                        # Kompilierung ausführen
                        metrics = compiler.compile(qasm_path, opt_level)
                        
                        if metrics:
                            # Visualisierung speichern (nur für 5 Qubits und Opt-Level 3)
                            if n_qubits == 5 and opt_level == 3 and "mapped_circuit" in metrics:
                                save_circuit_visualization(
                                    metrics["mapped_circuit"], 
                                    compiler.name, 
                                    algo, 
                                    n_qubits, 
                                    opt_level
                                )
                            
                            # mapped_circuit aus metrics entfernen, da nicht CSV-serialisierbar
                            if "mapped_circuit" in metrics:
                                del metrics["mapped_circuit"]
                                
                            row.update(metrics)
                            row["success"] = True
                        else:
                            row["success"] = False
                            
                    except Exception as e:
                        print(f"Fehler bei {compiler.name} {algo}-{n_qubits}: {e}")
                        # traceback.print_exc()
                        row["success"] = False
                        row["error"] = str(e)

                    results.append(row)
                    print(row)

    # Speichern der Rohdaten
    df = pd.DataFrame(results)
    df.to_csv("benchmark_results_final.csv", index=False)
    print("Benchmark abgeschlossen. Ergebnisse gespeichert.")

if __name__ == "__main__":
    run_benchmark()
