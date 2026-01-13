from quantum_bench.hardware.config import Falcon27
from quantum_bench.runner import run_benchmark

if __name__ == "__main__":
    # Startet die Benchmarking-Suite mit den definierten Parametern
    run_benchmark(
        hardware_configs=[Falcon27()],
        algorithms=["dj", "ghz", "qft"],
        qubit_ranges=[5, 10, 15, 20],
        num_runs=1,
        opt_levels=[3],
        output_file="test_result.csv",
        run_visualisation=True,
        run_verification=True,
        run_plotter=True
    )
