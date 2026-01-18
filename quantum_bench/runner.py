import os
from typing import List, Optional

import pandas as pd

from quantum_bench.compilers.cirq_adapter import CirqAdapter
from quantum_bench.compilers.pytket_adapter import PytketAdapter
from quantum_bench.compilers.qiskit_adapter import QiskitAdapter
import quantum_bench.data.mqt_provider as mqt
from quantum_bench.hardware.model import get_hardware
from quantum_bench.plotter import plot_results


def run_benchmark(hardware_names, algo_names, qubit_ranges, benchmark_levels, opt_levels, num_runs=10,
                  run_verification=False, run_visualisation=False, run_plotter=False,
                  output_file="benchmark_results_final.csv", visualisation_path=None, seed=None,
                  active_phases: Optional[List[str]] = None):
    """
    Führt den Benchmark durch.
    """
    print(f"Starte Benchmarking-Suite ({num_runs} Runs pro Config)...")

    if os.path.exists(output_file):
        os.remove(output_file)

    results = []

    for hardware_name in hardware_names:
        hardware = mqt.get_hardware(hardware_name)

        if not hardware:
            hardware = get_hardware(hardware_name)
            if not hardware:
                continue

        print(f"\n=== Hardware: {hardware_name} ===")

        compilers = [
            CirqAdapter(hardware),
            PytketAdapter(hardware),
            QiskitAdapter(hardware)
        ]
        for benchmark_level in benchmark_levels:
            for algo_name in algo_names:
                for n_qubits in qubit_ranges:
                    if n_qubits > hardware.num_qubits:
                        continue

                    qasm_path = mqt.get_circuit(hardware_name, algo_name, n_qubits, benchmark_level)
                    if not qasm_path:
                        continue

                    if run_visualisation and n_qubits == min(qubit_ranges):
                        mqt.visualize_circuit(qasm_path, hardware.name, visualisation_path)

                    print(f"--- {benchmark_level}-Benchmark: {algo_name} ({n_qubits} Qubits) ---")

                    for compiler in compilers:
                        for opt_level in opt_levels:
                            for run_i in range(num_runs):
                                row = {
                                    "hardware": hardware.name,
                                    "algorithm": algo_name,
                                    "qubits": n_qubits,
                                    "compiler": compiler.name,
                                    "opt_level": opt_level,
                                    "run": run_i,
                                }

                                try:
                                    metrics, compiled_qasm_path = compiler.compile(
                                        qasm_file=qasm_path,
                                        optimization_level=opt_level,
                                        active_phases=active_phases,
                                        seed=seed
                                    )

                                    if metrics:
                                        row.update(metrics)
                                        row["success"] = True
                                    else:
                                        row.update({
                                            "gate_count": None,
                                            "depth": None,
                                            "compile_time": None,
                                            "2q_gates": None,
                                            "swap_gates": None,
                                        })
                                        row["success"] = False

                                    if run_visualisation and compiled_qasm_path and n_qubits == min(qubit_ranges) and run_i == 0:
                                        mqt.visualize_circuit(compiled_qasm_path, hardware.name, visualisation_path)

                                    if run_verification:
                                        if compiled_qasm_path and n_qubits == min(qubit_ranges) and run_i == 0:
                                            equivalence = mqt.verify_circuit(qasm_path, compiled_qasm_path)
                                            row["Eqivalenz"] = equivalence
                                        else:
                                            row["Eqivalenz"] = "Skipped"
                                except Exception as e:
                                    row["success"] = False
                                    print(f"Fehler während des Kompilierens: {e}")

                                print(row)
                                results.append(row)

                                df_row = pd.DataFrame([row])
                                write_header = not os.path.exists(output_file)
                                df_row.to_csv(output_file, mode='a', header=write_header, index=False)

    if os.path.exists(output_file):
        print(f"Benchmark abgeschlossen. Ergebnisse in {output_file} gespeichert.")
        if run_plotter:
            plot_results(output_file, visualisation_path)
    else:
        print("Benchmark fehlgeschlagen.")
