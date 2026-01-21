import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


class BenchmarkPlotter:
    """Class to handle plotting of benchmark results."""

    def __init__(self, csv_file_path: str, output_dir: str = "visualisation"):
        self.csv_file_path = csv_file_path
        self.output_dir = output_dir
        self.df = None
        self.metrics = ["compile_time", "gate_count", "depth", "2q_gates", "swap_gates"]
        self.metric_labels = {
            "compile_time": "Compilation Time (s)",
            "gate_count": "Total Gate Count",
            "depth": "Circuit Depth",
            "2q_gates": "Number of 2-Qubit Gates",
            "swap_gates": "Number of SWAP Gates",
            "qubits": "Number of Qubits",
            "algorithm": "Algorithm",
            "hardware": "Hardware Architecture",
            "benchmark_level": "Benchmark Level",
            "compiler": "Compiler",
            "opt_level": "Optimization Level"
        }

    def load_data(self) -> bool:
        """Loads data from the CSV file."""
        if not os.path.exists(self.csv_file_path):
            print(f"Error: File '{self.csv_file_path}' not found.")
            return False

        self.df = pd.read_csv(self.csv_file_path)
        if "success" in self.df.columns:
            self.df = self.df[self.df["success"] == True]

        self.df.rename(columns=self.metric_labels, inplace=True)
        return not self.df.empty

    def _generate_plot(self, data, x_col, y_col, hue_col, style_col, title, output_path):
        plt.figure(figsize=(12, 7))
        sns.set_theme(style="whitegrid")

        if data.empty:
            return

        try:
            sns.lineplot(
                data=data, x=x_col, y=y_col, hue=hue_col, style=style_col,
                markers=True, dashes=False, linewidth=2, markersize=8, errorbar=('ci', 95), sort=True
            )

            if y_col == self.metric_labels.get("compile_time", "compile_time"):
                plt.yscale("log")

            plt.title(title)
            plt.xlabel(x_col)
            plt.ylabel(y_col)
            plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
            plt.tight_layout()

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            plt.savefig(output_path)
            print(f"Generated: {output_path}")
        except Exception as e:
            print(f"Failed to generate plot {output_path}: {e}")
        finally:
            plt.close()

    def run_plot_config(self, category_name, group_cols, line_cols, x_col="qubits",metrics=None):
        """
        Generates plots based on configuration.

        Args:
            category_name: Sub folder name.
            group_cols: List of columns to group by.
            line_cols: Column to use for different lines (hue, style).
            x_col: Column for x-axis.
            metrics: List of metrics to plot.
        """
        print(f"--- Processing {category_name} ---")

        real_group_cols = [self.metric_labels.get(c, c) for c in group_cols]
        real_line_cols = [self.metric_labels.get(c, c) for c in line_cols]
        real_x_col = self.metric_labels.get(x_col, x_col)
        if metrics is None:
            metrics = self.metrics
        if len(real_line_cols) == 1:
            real_line_cols = [real_line_cols[0], real_line_cols[0]]

        for metric in metrics:
            real_metric = self.metric_labels.get(metric, metric)
            if real_metric not in self.df.columns:
                continue

            for name, group_data in self.df.groupby(real_group_cols):
                if not isinstance(name, tuple):
                    name = (name,)

                group_desc = " ".join([f"{col}: {val}" for col, val in zip(real_group_cols, name)])
                title = f"{category_name}\n{group_desc}\n{real_metric}"
                filename = group_desc.replace(": ", "-").replace(" ", "_")
                directory = category_name.replace(": ", "-").replace(" ", "_")

                output_path = os.path.join(self.output_dir, directory, metric, f"{filename}.png")
                self._generate_plot(
                    data=group_data, x_col=real_x_col, y_col=real_metric,
                    hue_col=real_line_cols[0], style_col=real_line_cols[1],
                    title=title, output_path=output_path
                )


def plot_results(csv_file_path="benchmark_results.csv", visualisation_path="visualisation",
                 category_name="Compiler Benchmark", group_cols=None, line_cols=None, metrics=None):
    if line_cols is None:
        line_cols = ["compiler", "opt_level"]
    if group_cols is None:
        group_cols = ["algorithm", "hardware", "benchmark_level"]
    plotter = BenchmarkPlotter(csv_file_path, visualisation_path)
    if plotter.load_data():
        plotter.run_plot_config(
            category_name=category_name,
            group_cols=group_cols,
            line_cols=line_cols,
            metrics=metrics
        )
    else:
        print("Could not load data or data is empty.")


def plot_mapping_benchmark(csv_file_path="mapping_results.csv", visualisation_path="visualisation"):
    plotter = BenchmarkPlotter(csv_file_path, visualisation_path)
    if plotter.load_data():
        plotter.run_plot_config("Mapping Only", ["hardware", "compiler", "opt_level"], ["benchmark_level"])
        plotter.run_plot_config("Mapping Only", ["benchmark_level", "compiler", "opt_level"], ["hardware"])
        plotter.run_plot_config("Mapping Only", ["benchmark_level", "hardware", "opt_level"], ["compiler"])
    else:
        print("Could not load data or data is empty.")


def plot_compilation_benchmark(csv_file_path="compilation_results.csv", visualisation_path="visualisation"):
    plotter = BenchmarkPlotter(csv_file_path, visualisation_path)
    if plotter.load_data():
        plotter.run_plot_config("Full Compilation", ["opt_level", "algorithm", "benchmark_level"], ["compiler"])
        plotter.run_plot_config("Full Compilation", ["opt_level", "hardware", "benchmark_level"], ["compiler"])
        plotter.run_plot_config("Full Compilation", ["algorithm", "hardware", "benchmark_level"], ["compiler"])
    else:
        print("Could not load data or data is empty.")


if __name__ == "__main__":
    plot_results()
