import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_results(csv_file_path="benchmark_results_final.csv", visualisation_path: str = None):
    """
    Plots the benchmark results from the CSV file.

    Args:
        csv_file_path: Path to the CSV file containing benchmark results.
        visualisation_path: Directory to save the plots.
    """
    if visualisation_path is None:
        visualisation_path = "visualisation"
    try:
        df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        print(f"Error: File '{csv_file_path}' not found.")
        return

    # Filter for successful runs
    df = df[df["success"] == True]
    if df.empty:
        print("Warning: No data available.")
        return

    # Filter for optimization level 3 for the main plots
    df_opt = df[df["opt_level"] == 3]

    sns.set_theme(style="whitegrid")

    metrics = {
        "compile_time": "Compilation Time (s)",
        "gate_count": "Total Gate Count",
        "depth": "Circuit Depth",
        "2q_gates": "Number of 2-Qubit Gates (CX/CZ)",
        "swap_gates": "Number of SWAP Gates"
    }

    hardware_types = df_opt["hardware"].unique()
    algorithms = df_opt["algorithm"].unique()

    for hw in hardware_types:
        print(f"Creating plots for hardware: {hw}")
        df_hw = df_opt[df_opt["hardware"] == hw]

        for metric, label in metrics.items():
            if metric not in df.columns:
                continue

            # Directory structure: visualisation/plots/{Hardware}/{Metric}/
            overview_dir = os.path.join(visualisation_path, "plots", hw, metric)
            plot_dir = os.path.join(overview_dir, "algo")
            if not os.path.exists(plot_dir):
                os.makedirs(plot_dir)

            # 1. Overview Plot (All algorithms in one graph)
            plt.figure(figsize=(12, 7))
            sns.lineplot(
                data=df_hw,
                x="qubits",
                y=metric,
                hue="compiler",
                style="algorithm",
                markers=True,
                dashes=True,
                linewidth=2,
                markersize=8,
                errorbar=('ci', 95)
            )
            if metric == "compile_time":
                plt.yscale("log")

            plt.title(f"Overview: {label} - {hw}")
            plt.xlabel("Number of Qubits")
            plt.ylabel(label)
            plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0, title="Legend")
            plt.tight_layout()

            filename = os.path.join(overview_dir, "overview.png")
            plt.savefig(filename)
            plt.close()
            print(f"  Created: {filename}")

            # 2. Detail Plots (One graph per algorithm)
            for algo in algorithms:
                df_algo = df_hw[df_hw["algorithm"] == algo]
                if df_algo.empty:
                    continue

                plt.figure(figsize=(10, 6))
                sns.lineplot(
                    data=df_algo,
                    x="qubits",
                    y=metric,
                    hue="compiler",
                    style="compiler",  # Map style to compiler for better distinction
                    markers=True,
                    dashes=False,
                    linewidth=2.5,
                    markersize=9,
                    errorbar=('ci', 95)
                )
                if metric == "compile_time":
                    plt.yscale("log")

                plt.title(f"{label} - {algo.upper()} ({hw})")
                plt.xlabel("Number of Qubits")
                plt.ylabel(label)
                plt.legend(title="Compiler")
                plt.tight_layout()

                filename = os.path.join(plot_dir, f"{algo}.png")
                plt.savefig(filename)
                plt.close()
                print(f"    Detail: {filename}")


if __name__ == "__main__":
    plot_results()
