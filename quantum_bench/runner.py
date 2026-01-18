import os
from typing import List, Optional

import pandas as pd

from quantum_bench.compilers.cirq_adapter import CirqAdapter
from quantum_bench.compilers.pytket_adapter import PytketAdapter
from quantum_bench.compilers.qiskit_adapter import QiskitAdapter
import quantum_bench.data.mqt_provider as mqt
from quantum_bench.hardware.model import get_hardware
from quantum_bench.plotter import plot_results


def run_benchmark(hardware_names: List[str], algo_names: List[str], qubit_ranges: List[int], benchmark_levels: List[str],
                  opt_levels: List[int], num_runs: int = 1,
                  run_verification: bool = False, run_visualisation: bool = False, run_plotter: bool = False,
                  output_file: str = "benchmark_results_final.csv", visualisation_path: str = None, full_compilation: bool = None, seed: int = None,
                  active_phases: Optional[List[str]] = None):
    """
    Executes the benchmark suite.

    Args:
        hardware_names: List of hardware names to benchmark against.
        algo_names: List of algorithm names to benchmark.
        qubit_ranges: Range of qubit counts to test.
        benchmark_levels: List of benchmark levels (e.g., 'ALG', 'INDEP').
        opt_levels: List of optimization levels to test.
        num_runs: Number of runs per configuration.
        run_verification: Whether to verify the compiled circuits.
        run_visualisation: Whether to visualize the circuits.
        run_plotter: Whether to plot the results after benchmarking.
        output_file: Path to the output CSV file.
        visualisation_path: Path for visualisation output.
        seed: Random seed.
        active_phases: List of active compiler phases.
    """
    print(f"Starting Benchmarking Suite ({num_runs} runs per config)...")

    if os.path.exists(output_file):
        os.remove(output_file)

    results = []

    for hardware_name in hardware_names:
        hardware = mqt.get_hardware_model(hardware_name)

        if not hardware:
            hardware = get_hardware(hardware_name)
            if not hardware:
                print(f"Skipping unknown hardware: {hardware_name}")
                continue

        print(f"\n=== Hardware: {hardware_name} ===")

        compilers = [
            CirqAdapter(hardware),
            PytketAdapter(hardware),
            QiskitAdapter(hardware)
        ]
        for benchmark_level in benchmark_levels:
            for n_qubits in qubit_ranges:
                for algo_name in algo_names:
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
                                    "benchmark_level": benchmark_level,
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
                                            "gate_count": '-',
                                            "depth": '-',
                                            "compile_time": '-',
                                            "2q_gates": '-',
                                            "swap_gates": '-',
                                            "initial": '-'
                                        })
                                        row["success"] = False

                                    if run_visualisation and compiled_qasm_path and n_qubits == min(qubit_ranges) and run_i == 0:
                                        mqt.visualize_circuit(compiled_qasm_path, hardware.name, visualisation_path)

                                    if run_verification:
                                        if compiled_qasm_path and n_qubits == min(qubit_ranges) and run_i == 0:
                                            equivalence = mqt.verify_circuit(qasm_path, compiled_qasm_path)
                                            row["Equivalence"] = equivalence
                                        else:
                                            row["Equivalence"] = "Skipped"
                                except Exception as e:
                                    row["success"] = False
                                    print(f"Error during compilation: {e}")

                                print(row)
                                results.append(row)

                                df_row = pd.DataFrame([row])
                                write_header = not os.path.exists(output_file)
                                df_row.to_csv(output_file, mode='a', header=write_header, index=False)

    if os.path.exists(output_file):
        print(f"Benchmark finished. Results saved to {output_file}.")
        if run_plotter:
            plot_results(output_file, visualisation_path, full_compilation)
    else:
        print("Benchmark failed.")
