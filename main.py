from ftplib import print_line

from mqt.bench.benchmarks import get_available_benchmark_names
from mqt.bench.targets import get_available_device_names, get_device
from qiskit import generate_preset_pass_manager

from quantum_bench.runner import run_benchmark

if __name__ == "__main__":
    benchmarks = get_available_benchmark_names()
    benchmarks.remove('grover')
    benchmarks.remove('qwalk')
    hardware = get_available_device_names()
    # Startet die Benchmarking-Suite mit den definierten Parametern
    run_benchmark(
        hardware_names=["ibm_falcon_27"], #"ionq_forte_36", "ionq_aria_25"
        algo_names=["grover"],
        qubit_ranges=[5,5],
        benchmark_levels=["ALG"], #"alg", "indep", "nativegates", "mapped"
        opt_levels=[3],
        num_runs=1,
        output_file="testing.csv",
        run_visualisation=False,
        run_verification=False,
        run_plotter=False,
        #active_phases=["rebase", "mapping", "optimization"]
    )
    # pm = generate_preset_pass_manager(3,target=get_device("ibm_falcon_27"))
    # passes = pm.to_flow_controller().passes
    # for task in passes:
    #     print(task)
    # print('')
    # last = len(passes)-1
    # print(passes[last].condition)
