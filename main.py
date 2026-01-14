from mqt.bench.benchmarks import get_available_benchmark_names

from quantum_bench.plotter import plot_results
from quantum_bench.runner import run_benchmark

if __name__ == "__main__":
    benchmarks = get_available_benchmark_names()
    benchmarks.remove('grover')
    benchmarks.remove('qwalk')
    # Startet die Benchmarking-Suite mit den definierten Parametern
    run_benchmark(
        hardware=["Falcon27"],
        algorithms=benchmarks,
        qubit_ranges=[4,5,6,7,8,9,10,11,12,13,14,15,16],
        opt_levels=[3],
        num_runs=1,
        output_file="test_result.csv",
        run_visualisation=False,
        run_verification=False,
        run_plotter=True
    )
    #plot_results("test_result.csv");