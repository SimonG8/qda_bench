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

    def _generate_plot(self, data, x_col, y_col, hue_col, style_col, title, output_path, ratio=False):
        plt.figure(figsize=(12, 7))
        sns.set_theme(style="whitegrid")

        if data.empty:
            return

        try:
            sns.lineplot(
                data=data, x=x_col, y=y_col, hue=hue_col, style=style_col,
                markers=True, dashes=False, linewidth=3, markersize=10, errorbar=('ci', 95),
                hue_order=sorted(data[hue_col].unique()), style_order=sorted(data[style_col].unique())
            )

            if y_col == self.metric_labels.get("compile_time", "compile_time") and not ratio:
                plt.yscale("log")
            plt.tick_params(axis='both', which='major', labelsize=25)
            plt.title(title, fontsize=30)
            plt.xlabel(x_col, fontsize=30)
            if ratio:
                plt.ylabel("Compression Ratio", fontsize=30)
            else:
                plt.ylabel(y_col, fontsize=30)
            plt.legend(loc='upper left', borderaxespad=0, fontsize=27)
            plt.tight_layout()

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            plt.savefig(output_path)
            print(f"Generated: {output_path}")
        except Exception as e:
            print(f"Failed to generate plot {output_path}: {e}")
        finally:
            plt.close()

    def run_plot_config(self, category_name, group_cols, line_cols, x_col="qubits", title_cols=None, metrics=None, ratio=False, filter=None):
        """
        Generates plots based on configuration.

        Args:
            category_name: Sub folder name.
            group_cols: List of columns to group by.
            line_cols: Column to use for different lines (hue, style).
            x_col: Column for x-axis.
            metrics: List of metrics to plot.
            filter: Dictionary of filters to apply {column: value}.
        """
        print(f"--- Processing {category_name} ---")
        real_title_cols = [self.metric_labels.get(c, c) for c in title_cols]
        real_group_cols = [self.metric_labels.get(c, c) for c in group_cols]
        real_line_cols = [self.metric_labels.get(c, c) for c in line_cols]
        real_x_col = self.metric_labels.get(x_col, x_col)
        if metrics is None:
            metrics = self.metrics
        if len(real_line_cols) == 1:
            real_line_cols = [real_line_cols[0], real_line_cols[0]]

        df_to_plot = self.df.copy()
        if filter:
            for col, val in filter.items():
                real_col = self.metric_labels.get(col, col)
                if real_col in df_to_plot.columns:
                    df_to_plot = df_to_plot[df_to_plot[real_col] == val]
                else:
                    print(f"Warning: Filter column '{col}' not found in data.")

        if df_to_plot.empty:
            print("Warning: No data left after filtering.")
            return

        for metric in metrics:
            real_metric = self.metric_labels.get(metric, metric)
            if real_metric not in df_to_plot.columns:
                continue

            for name, group_data in df_to_plot.groupby(real_group_cols):
                if not isinstance(name, tuple):
                    name = (name,)
                
                title = ", ".join([f"{col}: {val}" for col, val in zip(real_title_cols, name)])
                if ratio:
                    title = title+f"\nCompression Ratio ({real_metric})"

                group_desc = "_".join([f"{col}-{val}" for col, val in zip(group_cols, name)])
                filename = group_desc+"_"+metric
                directory = category_name.replace(": ", "-").replace(",", "").replace(" ","_")

                output_path = os.path.join(self.output_dir, directory, metric, f"{filename}.png")
                self._generate_plot(
                    data=group_data, x_col=real_x_col, y_col=real_metric,
                    hue_col=real_line_cols[0], style_col=real_line_cols[1],
                    title=title, output_path=output_path, ratio=ratio
                )


def plot_results(csv_file_path="benchmark_results.csv", visualisation_path="visualisation",
                 category_name="Compiler Benchmark", group_cols=None, line_cols=None,title_cols=None, metrics=None,
                 filter=None):
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
            title_cols=title_cols,
            metrics=metrics,
            filter=filter
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


def plot_compression_ratio_comparison(csv_file_numerator, csv_file_denominator, visualisation_path="visualisation",
                                      category_name="Compression Ratio", group_cols=None, line_cols=None, metrics=None):
    if group_cols is None:
        group_cols = ["algorithm", "hardware", "benchmark_level"]
    if line_cols is None:
        line_cols = ["compiler", "opt_level"]

    plotter_num = BenchmarkPlotter(csv_file_numerator, visualisation_path)
    if not plotter_num.load_data():
        print(f"Could not load {csv_file_numerator}")
        return

    plotter_denom = BenchmarkPlotter(csv_file_denominator, visualisation_path)
    if not plotter_denom.load_data():
        print(f"Could not load {csv_file_denominator}")
        return

    # Identify metric columns (display names)
    metric_display_names = [plotter_num.metric_labels.get(m, m) for m in plotter_num.metrics]

    # Identify merge keys
    df_num = plotter_num.df
    df_denom = plotter_denom.df

    common_cols = [c for c in df_num.columns if c in df_denom.columns]
    merge_keys = [c for c in common_cols if c not in metric_display_names and c != "success"]

    merged = pd.merge(df_num, df_denom, on=merge_keys, suffixes=('_num', '_denom'))

    if merged.empty:
        print("Error: No matching data found for ratio calculation.")
        return

    df_ratio = merged[merge_keys].copy()

    available_metrics = []
    for m in plotter_num.metrics:
        disp_name = plotter_num.metric_labels.get(m, m)
        col_num = f"{disp_name}_num"
        col_denom = f"{disp_name}_denom"

        if col_num in merged.columns and col_denom in merged.columns:
            df_ratio[disp_name] = merged[col_num] / merged[col_denom]
            available_metrics.append(m)

    plotter_ratio = BenchmarkPlotter(csv_file_numerator, visualisation_path)
    plotter_ratio.df = df_ratio

    if metrics is None:
        metrics = available_metrics

    plotter_ratio.run_plot_config(category_name, group_cols, line_cols, metrics=metrics, ratio=True)


if __name__ == "__main__":
    plot_results()
