from mqt.bench.benchmarks import get_available_benchmark_names
from mqt.bench.targets import get_available_device_names, get_device
from quantum_bench.runner import run_benchmark, run_mapping_benchmark, run_compilation_benchmark

if __name__ == "__main__":
    run_benchmark(
        hardware_names=["ionq_forte_36"],
        algo_names=["ghz"],
        qubit_ranges=[5],
        benchmark_levels=["INDEP"], #, "INDEP", "NATIVEGATES", "MAPPED"],
        opt_levels=[3],
        num_runs=1,
        output_file="benchmark_results.csv",
        run_visualisation=True,
        run_verification=False,
        run_plotter=False,
        active_phases=["rebase", "mapping", "optimization"]
    )


