import argparse
import logging

from quantum_bench.runner import run_benchmark
from quantum_bench.hardware.config import Falcon27, Grid25
from quantum_bench.plotter import plot_results

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    HARDWARE_CONFIGS = [Falcon27(), Grid25()]
    ALGORITHMS = ["dj", "ghz", "qft", "grover"]
    QUBIT_RANGES = [5, 10, 15, 20]
    NUM_RUNS = 10

    # Startet die Benchmarking-Suite mit den definierten Parametern
    run_benchmark(HARDWARE_CONFIGS, ALGORITHMS, QUBIT_RANGES, NUM_RUNS)
    plot_results()