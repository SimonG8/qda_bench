from mqt.bench.benchmarks import get_available_benchmark_names
from mqt.bench.targets import get_available_device_names, get_device
from quantum_bench.runner import run_benchmark, run_mapping_benchmark, run_compilation_benchmark

if __name__ == "__main__":
    run_benchmark(
        hardware_names=["ibm_falcon_27"],
        algo_names=["grover"],
        qubit_ranges=[5],
        benchmark_levels=["ALG"], #, "INDEP", "NATIVEGATES", "MAPPED"],
        opt_levels=[3],
        num_runs=1,
        output_file="benchmark_results.csv",
        run_visualisation=False,
        run_verification=False,
        run_plotter=True,
    )
