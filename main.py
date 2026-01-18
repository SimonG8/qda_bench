from mqt.bench.benchmarks import get_available_benchmark_names
from mqt.bench.targets import get_available_device_names, get_device
from qiskit import generate_preset_pass_manager
from quantum_bench.data.mqt_provider import visualize_circuit, get_circuit
from quantum_bench.plotter import plot_results
from quantum_bench.runner import run_benchmark

if __name__ == "__main__":
    benchmarks = ["qft", "vqe", "qaoa", "randomcircuit", "ghz"]
    hardware = ["ibm_eagle_127", "rigetti_ankaa_84", "ionq_forte_36"]
    qubits = [4, 5, 8, 10, 15, 16, 20, 25, 32, 36, 40, 50, 64, 75, 84, 100, 127]
    # Startet die Benchmarking-Suite mit den definierten Parametern
    run_benchmark(
        hardware_names=["ibm_falcon_27"], #"ionq_forte_36", "ionq_aria_25"
        algo_names=benchmarks,
        qubit_ranges=qubits,
        benchmark_levels=["ALG", "INDEP", "NATIVEGATES", "MAPPED"],
        opt_levels=[3],
        num_runs=1,
        output_file="MAPPING_Result.csv",
        run_visualisation=False,
        run_verification=False,
        run_plotter=False,
        full_compilation=False,
        active_phases=["rebase","mapping"]
    )
    run_benchmark(
        hardware_names=hardware,
        algo_names=benchmarks,
        qubit_ranges=qubits,
        benchmark_levels=["ALG"], #"INDEP", "NATIVEGATES", "MAPPED"],
        opt_levels=[0, 3],
        num_runs=1,
        output_file="FULL_COMPILATION_Result.csv",
        run_visualisation=False,
        run_verification=False,
        run_plotter=False,
        full_compilation=True
    )
    run_benchmark(
        hardware_names=hardware,  # "ionq_forte_36", "ionq_aria_25"
        algo_names=["grover"],
        qubit_ranges=qubits,
        benchmark_levels=["ALG", "INDEP", "NATIVEGATES", "MAPPED"],
        opt_levels=[3],
        num_runs=1,
        output_file="MAPPING_Result_grover.csv",
        run_visualisation=False,
        run_verification=False,
        run_plotter=False,
        full_compilation=False,
        active_phases=["rebase", "mapping"]
    )
    run_benchmark(
        hardware_names=hardware,  # "ionq_forte_36", "ionq_aria_25"
        algo_names=["grover"],
        qubit_ranges=qubits,
        benchmark_levels=["ALG"],  # "INDEP", "NATIVEGATES", "MAPPED"],
        opt_levels=[0, 3],
        num_runs=1,
        output_file="FULL_COMPILATION_Result_grover.csv",
        run_visualisation=False,
        run_verification=False,
        run_plotter=False,
        full_compilation=True
    )
    # plot_results("all_bench_levels_falcon27_rebase_mapping.csv",True)


    # pm = generate_preset_pass_manager(3,target=get_device("ibm_falcon_27"))
    # passes = pm.to_flow_controller().passes
    # for task in passes:
    #     print(task)
    # print('')
    # last = len(passes)-1
    # print(passes[last].condition)

    # hw = "ibm_falcon_27"
    # for benchmark in benchmarks:
    #     qasm = get_circuit(hw,benchmark,4,"ALG")
    #     visualize_circuit(qasm,hw)