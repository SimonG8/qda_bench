import os
import concurrent.futures
from typing import List, Optional

import pandas as pd

from quantum_bench.compilers.cirq_adapter import CirqAdapter
from quantum_bench.compilers.pytket_adapter import PytketAdapter
from quantum_bench.compilers.qiskit_adapter import QiskitAdapter
import quantum_bench.data.mqt_provider as mqt
from quantum_bench.hardware.model import get_hardware
from quantum_bench.plotter import plot_results, plot_compilation_benchmark, plot_mapping_benchmark


def process_task(hardware_name, benchmark_level, algo_name, n_qubits, compiler_cls, opt_level, run_i, qasm_path, active_phases, seed, do_visualize, run_verification, is_verification_run, visualisation_path):

    # Re-fetch hardware inside the worker process
    hardware = mqt.get_hardware_model(hardware_name)
    if not hardware:
        hardware = get_hardware(hardware_name)

    compiler = compiler_cls(hardware)
    
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

        if do_visualize and compiled_qasm_path:
             mqt.visualize_circuit(compiled_qasm_path, hardware.name, visualisation_path)

        if run_verification:
            if is_verification_run and compiled_qasm_path:
                equivalence = mqt.verify_circuit(qasm_path, compiled_qasm_path)
                row["Equivalence"] = equivalence
            else:
                row["Equivalence"] = "Skipped"

    except Exception as e:
        row["success"] = False
        print(f"Error during compilation in worker: {e}")

    return row


def run_benchmark(hardware_names: List[str], algo_names: List[str], qubit_ranges: List[int], benchmark_levels: List[str],
                  opt_levels: List[int], num_runs: int = 1,
                  run_verification: bool = False, run_visualisation: bool = False, run_plotter: bool = False,
                  output_file: str = "benchmark_results_final.csv", visualisation_path: str = None, seed: int = None,
                  active_phases: Optional[List[str]] = None, max_workers: Optional[int] = None, max_queued_tasks: int = 20):
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
        max_workers: Maximum number of parallel workers.
        max_queued_tasks: Maximum number of tasks to schedule ahead of execution.
    """
    
    if max_workers is None:
        max_workers = os.cpu_count() or 1
    
    # Ensure we don't block workers by having a too small queue
    if max_queued_tasks < max_workers:
        max_queued_tasks = max_workers
        
    print(f"Starting Benchmarking Suite ({num_runs} runs per config)...")
    print(f"Parallelism: max_workers={max_workers}, max_queued_tasks={max_queued_tasks}")

    results = []
    interrupted = False
    
    def handle_result(future):
        try:
            row = future.result()
            results.append(row)
            print(row)

            df_row = pd.DataFrame([row])
            write_header = not os.path.exists(output_file)
            df_row.to_csv(output_file, mode='a', header=write_header, index=False)
        except Exception as e:
            print(f"Task failed with error: {e}")

    # Use ProcessPoolExecutor for parallelism
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = set()

        try:
            for hardware_name in hardware_names:
                hardware = mqt.get_hardware_model(hardware_name)

                if not hardware:
                    hardware = get_hardware(hardware_name)
                    if not hardware:
                        print(f"Skipping unknown hardware: {hardware_name}")
                        continue

                print(f"\n=== Scheduling Hardware: {hardware_name} ===")

                # List of compiler classes to instantiate in workers
                compiler_classes = [
                    CirqAdapter,
                    PytketAdapter,
                    QiskitAdapter
                ]
                
                for benchmark_level in benchmark_levels:
                    for n_qubits in qubit_ranges:
                        if n_qubits > hardware.num_qubits:
                            continue
                        for algo_name in algo_names:


                            qasm_path = mqt.get_circuit(hardware_name, algo_name, n_qubits, benchmark_level)
                            if not qasm_path:
                                continue

                            if run_visualisation and n_qubits == min(qubit_ranges):
                                mqt.visualize_circuit(qasm_path, hardware.name, visualisation_path)

                            # Removed the immediate print here to avoid flooding the console
                            # print(f"--- {benchmark_level}-Benchmark: {algo_name} ({n_qubits} Qubits) ---")

                            for compiler_cls in compiler_classes:
                                for opt_level in opt_levels:
                                    for run_i in range(num_runs):
                                        
                                        # Limit backlog
                                        while len(futures) >= max_queued_tasks:
                                            done, _ = concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)
                                            for f in done:
                                                futures.remove(f)
                                                handle_result(f)

                                        do_visualize = (run_visualisation and n_qubits == min(qubit_ranges) and run_i == 0)
                                        is_verification_run = (n_qubits == min(qubit_ranges) and run_i == 0)
                                        
                                        future = executor.submit(
                                            process_task,
                                            hardware_name,
                                            benchmark_level,
                                            algo_name,
                                            n_qubits,
                                            compiler_cls,
                                            opt_level,
                                            run_i,
                                            qasm_path,
                                            active_phases,
                                            seed,
                                            do_visualize,
                                            run_verification,
                                            is_verification_run,
                                            visualisation_path
                                        )
                                        futures.add(future)

            print(f"Scheduled all tasks. Waiting for remaining {len(futures)} results...")

            # Collect remaining results
            for future in concurrent.futures.as_completed(futures):
                handle_result(future)
                
        except KeyboardInterrupt:
            print("\nBenchmark interrupted. Cancelling pending tasks...")
            for f in futures:
                f.cancel()
            interrupted = True

    if os.path.exists(output_file):
        if interrupted:
            print(f"Benchmark interrupted. Partial results saved to {output_file}.")
        else:
            print(f"Benchmark finished. Results saved to {output_file}.")

        if run_plotter:
            plot_results(output_file, visualisation_path)
    else:
        print("Benchmark failed or no results generated.")


def run_mapping_benchmark(hardware_names: List[str], algo_names: List[str], qubit_ranges: List[int],
                          output_file: str = "mapping_results.csv", plot_path: str = None, run_plotter: bool = False,
                          max_workers: Optional[int] = None, max_queued_tasks: int = 20):
    run_benchmark(
        hardware_names=hardware_names,
        algo_names=algo_names,
        qubit_ranges=qubit_ranges,
        benchmark_levels=["ALG", "INDEP", "NATIVEGATES", "MAPPED"],
        opt_levels=[3],
        num_runs=1,
        output_file=output_file,
        run_visualisation=False,
        run_verification=False,
        run_plotter=False,
        active_phases=["rebase", "mapping"],
        max_workers=max_workers,
        max_queued_tasks=max_queued_tasks
    )
    if run_plotter:
        plot_mapping_benchmark(output_file, plot_path)

def run_compilation_benchmark(hardware_names: List[str], algo_names: List[str], qubit_ranges: List[int],
                              output_file: str = "compilation_results.csv", plot_path: str = None, run_plotter: bool = False,
                              max_workers: Optional[int] = None, max_queued_tasks: int = 20):
    run_benchmark(
        hardware_names=hardware_names,
        algo_names=algo_names,
        qubit_ranges=qubit_ranges,
        benchmark_levels=["ALG"],
        opt_levels=[3],
        num_runs=1,
        output_file=output_file,
        run_visualisation=False,
        run_verification=False,
        run_plotter=False,
        max_workers=max_workers,
        max_queued_tasks=max_queued_tasks
    )
    if run_plotter:
        plot_compilation_benchmark(output_file, plot_path)