from mqt.bench.benchmarks import get_available_benchmark_names
from mqt.bench.targets import get_available_device_names, get_device

from quantum_bench.runner import run_benchmark

if __name__ == "__main__":
    benchmarks = get_available_benchmark_names()
    hardware = get_available_device_names()
    # Startet die Benchmarking-Suite mit den definierten Parametern
    run_benchmark(
        hardware_names=[], 
        algo_names=[],
        qubit_ranges=[],
        benchmark_levels=[], #"ALG", "INDEP", "NATIVEGATES", "MAPPED"
        opt_levels=[],
        num_runs=,
        output_file=,
        run_visualisation=,
        run_verification=,
        run_plotter=,
        #active_phases=[], # "REBASE", "MAPPING", "OPTIMIZATION"
    )
