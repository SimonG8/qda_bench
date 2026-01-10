from quantum_bench.runner import run_benchmark
from quantum_bench.hardware.config import Falcon27
from quantum_bench.plotter import plot_results

if __name__ == "__main__":
    # Konfiguration des Benchmarks
    HARDWARE_CONFIGS = [Falcon27()]
    ALGORITHMS = ['ghz', 'dj', 'qft', 'grover']
    QUBIT_RANGES = [5, 10]
    NUM_RUNS = 1

    # Startet die Benchmarking-Suite mit den definierten Parametern
    run_benchmark(HARDWARE_CONFIGS, ALGORITHMS, QUBIT_RANGES, NUM_RUNS)
    plot_results()