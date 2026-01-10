import pandas as pd
import os
import random
import logging
from quantum_bench.data.mqt_provider import BenchmarkProvider
from quantum_bench.compilers.qiskit_adapter import QiskitAdapter
from quantum_bench.compilers.cirq_adapter import CirqAdapter
from quantum_bench.compilers.pytket_adapter import PytketAdapter

# MQT QCEC für Verifikation
from mqt import qcec

# Für Visualisierung
import matplotlib.pyplot as plt
import cirq.contrib.svg
from qiskit import QuantumCircuit

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

def verify_circuit(original_qasm, compiled_circuit, compiler_name):
    """
    Verifiziert die Äquivalenz zwischen Original und Kompilat mittels MQT QCEC.
    """
    if qcec is None:
        return "QCEC not installed"
        
    try:
        # QCEC benötigt zwei QuantumCircuit Objekte oder Pfade
        # 1. Original laden
        qc1 = QuantumCircuit.from_qasm_file(original_qasm)
        
        # 2. Kompilat vorbereiten
        qc2 = None
        if compiler_name == "Qiskit":
            qc2 = compiled_circuit
        elif compiler_name == "pytket":
            from pytket.extensions.qiskit import tk_to_qiskit
            qc2 = tk_to_qiskit(compiled_circuit, replace_implicit_swaps=True)
        elif compiler_name == "Cirq":
            # Cirq ist tricky, wir exportieren zu QASM und importieren in Qiskit
            # Das ist nicht performant, aber robust
            from cirq import qasm
            qasm_str = qasm(compiled_circuit)
            qc2 = QuantumCircuit.from_qasm_str(qasm_str)
            
        if qc2 is None:
            return "Conversion failed"

        # 3. Verifikation durchführen
        result = qcec.verify(qc1, qc2)
        return str(result.equivalence) # "equivalent", "not_equivalent", etc.
        
    except Exception as e:
        return f"Error: {str(e)}"

def run_benchmark(hardware_configs, algorithms, qubit_ranges, num_runs=10, output_file="benchmark_results_final.csv"):
    """
    Führt den Benchmark durch.
    """
    provider = BenchmarkProvider()

    results = []

    logging.info(f"Starte Benchmarking-Suite ({num_runs} Runs pro Config)...")
    
    if os.path.exists(output_file):
        os.remove(output_file)
    
    for hardware in hardware_configs:
        logging.info(f"\n=== Hardware: {hardware.name} ===")
        
        compilers = [
            QiskitAdapter(hardware), 
            CirqAdapter(hardware), 
            PytketAdapter(hardware)
        ]
        
        for algo in algorithms:
            for n_qubits in qubit_ranges:
                if n_qubits > hardware.num_qubits:
                    continue
                    
                logging.info(f"--- Benchmark: {algo} ({n_qubits} Qubits) ---")
                
                qasm_path = provider.get_circuit(algo, n_qubits)
                if not qasm_path:
                    continue
                
                if n_qubits == 5:
                    try:
                        qc_orig = QuantumCircuit.from_qasm_file(qasm_path)
                        save_circuit_visualization(qc_orig, "Original", algo, n_qubits, 0, hardware.name)
                    except Exception as e:
                        logging.error(f"Fehler bei Original-Visualisierung: {e}")

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
                                    mapped_circuit = metrics.get("mapped_circuit")
                                    
                                    # Visualisierung (nur 5 Qubits, Opt 3, Run 0)
                                    if n_qubits == 5 and opt_level == 3 and run_i == 0 and mapped_circuit:
                                        save_circuit_visualization(
                                            mapped_circuit, 
                                            compiler.name, 
                                            algo, 
                                            n_qubits, 
                                            opt_level,
                                            hardware.name
                                        )
                                    
                                    # --- VERIFIKATION ---
                                    # Wir verifizieren nur den ersten Run jedes Sets, um Zeit zu sparen
                                    # und nur bis zu einer gewissen Qubit-Größe (QCEC skaliert gut, aber sicher ist sicher)
                                    if run_i == 0 and n_qubits <= 20 and mapped_circuit:
                                        verification_result = verify_circuit(qasm_path, mapped_circuit, compiler.name)
                                        row["verified"] = verification_result
                                    else:
                                        row["verified"] = "Skipped"

                                    if "mapped_circuit" in metrics:
                                        del metrics["mapped_circuit"]
                                        
                                    row.update(metrics)
                                    row["success"] = True
                                else:
                                    row["success"] = False
                                    
                            except Exception as e:
                                row["success"] = False
                                row["error"] = str(e)
                            
                            logging.info(f"Result: {compiler.name} L{opt_level} Run {run_i}: {row.get('gate_count', 'N/A')} Gatter ({row.get('compile_time','N/A')}s)")
                            results.append(row)
                            
                            df_row = pd.DataFrame([row])
                            write_header = not os.path.exists(output_file)
                            df_row.to_csv(output_file, mode='a', header=write_header, index=False)

    logging.info(f"Benchmark abgeschlossen. Ergebnisse in {output_file} gespeichert.")
