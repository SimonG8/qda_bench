import os

import pandas as pd

from quantum_bench.compilers.cirq_adapter import CirqAdapter
from quantum_bench.compilers.pytket_adapter import PytketAdapter
from quantum_bench.compilers.qiskit_adapter import QiskitAdapter
from quantum_bench.data.mqt_provider import get_circuit, verify_circuit, visualize_circuit
from quantum_bench.plotter import plot_results


def run_benchmark(hardware_configs, algorithms, qubit_ranges, opt_levels, num_runs=10,
                  run_verification=False, run_visualisation=False, run_plotter=False,
                  output_file="benchmark_results_final.csv", visualisation_path=None, seed=None):
    """
    Führt den Benchmark durch.
    """
    results = []

    print(f"Starte Benchmarking-Suite ({num_runs} Runs pro Config)...")

    if os.path.exists(output_file):
        os.remove(output_file)

    for hardware in hardware_configs:
        print(f"\n=== Hardware: {hardware.name} ===")

        compilers = [
            CirqAdapter(hardware),
            PytketAdapter(hardware),
            QiskitAdapter(hardware)
        ]

        for algo in algorithms:
            for n_qubits in qubit_ranges:
                if n_qubits > hardware.num_qubits:
                    continue

                print(f"--- Benchmark: {algo} ({n_qubits} Qubits) ---")

                qasm_path = get_circuit(algo, n_qubits)
                if not qasm_path:
                    continue

                for compiler in compilers:
                    for opt_level in opt_levels:
                        for run_i in range(num_runs):
                            row = {
                                "hardware": hardware.name,
                                "algorithm": algo,
                                "qubits": n_qubits,
                                "compiler": compiler.name,
                                "opt_level": opt_level,
                                "run": run_i,
                            }

                            try:
                                metrics, compiled_qasm_path = compiler.compile(qasm_path, opt_level, seed)

                                if metrics:
                                    row.update(metrics)
                                    row["success"] = True
                                else:
                                    row["success"] = False

                                if compiled_qasm_path and n_qubits == 5 and opt_level == 3 and run_i == 0:
                                    if run_visualisation:
                                        visualize_circuit(compiled_qasm_path, hardware.name, visualisation_path)

                                    if run_verification:
                                        equivalence = verify_circuit(qasm_path, compiled_qasm_path)
                                        row["Eqivalenz"] = equivalence
                                    else:
                                        row["Eqivalenz"] = "Skipped"
                                else:
                                    row["Eqivalenz"] = "Skipped"
                            except Exception as e:
                                row["success"] = False
                                row["error"] = str(e)

                            print(row)
                            results.append(row)

                            df_row = pd.DataFrame([row])
                            write_header = not os.path.exists(output_file)
                            df_row.to_csv(output_file, mode='a', header=write_header, index=False)

    print(f"Benchmark abgeschlossen. Ergebnisse in {output_file} gespeichert.")
    if run_plotter:
        plot_results(output_file, visualisation_path)
