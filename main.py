from quantum_bench.runner import run_benchmark

if __name__ == "__main__":

    # Startet die Benchmarking-Suite mit den definierten Parametern
    run_benchmark(
        hardware=["Falcon27"],
        algorithms=["dj", "ghz", "qft"],
        qubit_ranges=[5, 10, 15, 20],
        opt_levels=[3],
        num_runs=1,
        output_file="test_results.csv",
        run_visualisation=False,
        run_verification=False,
        run_plotter=False
    )
