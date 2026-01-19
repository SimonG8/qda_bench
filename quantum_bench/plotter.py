import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

class BenchmarkPlotter:
    def __init__(self, csv_file_path, output_dir="visualisation"):
        self.csv_file_path = csv_file_path
        self.output_dir = output_dir
        self.df = None
        self.metrics = [
            "compile_time",
            "gate_count",
            "depth",
            "2q_gates",
            "swap_gates"
        ]
        # Map metrics to readable names if needed, otherwise use column names
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

    def load_data(self):
        if not os.path.exists(self.csv_file_path):
            print(f"Error: File '{self.csv_file_path}' not found.")
            return False
        self.df = pd.read_csv(self.csv_file_path)
        # Filter for successful runs
        if "success" in self.df.columns:
            self.df = self.df[self.df["success"] == True]
        
        self.df.rename(columns=self.metric_labels, inplace=True)
        return not self.df.empty

    def _generate_plot(self, data, x_col, y_col, hue_col, style_col, title, output_path):
        plt.figure(figsize=(12, 7))
        sns.set_theme(style="whitegrid")
        
        # Check if data is sufficient
        if data.empty:
            return

        try:
            sns.lineplot(
                data=data,
                x=x_col,
                y=y_col,
                hue=hue_col,
                style=style_col,
                markers=True,
                dashes=False,
                linewidth=2,
                markersize=8,
                errorbar=('ci', 95) # 95% confidence interval for statistical dispersion
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
            plt.close()
            print(f"Generated: {output_path}")
        except Exception as e:
            print(f"Failed to generate plot {output_path}: {e}")
            plt.close()

    def run_plot_config(self, category_name, group_cols, line_cols, x_col="qubits"):
        """
        Abstract function to generate plots based on configuration.
        
        Args:
            category_name: Sub folder (e.g., "Hardware_Compiler_vs_BenchmarkLevel")
            group_cols: List of columns to group by (creates separate plot files)
            line_col: Column to use for different lines in the graph. First value is used for hue, second for style.
            x_col: Column for x-axis
        """
        print(f"--- Processing {category_name} ---")
        
        real_group_cols = [self.metric_labels.get(c, c) for c in group_cols]
        real_line_cols = [self.metric_labels.get(c, c) for c in line_cols]
        real_x_col = self.metric_labels.get(x_col, x_col)

        # Ensure all columns exist
        required_cols = real_group_cols + real_line_cols + [real_x_col]
        for col in required_cols:
            if col not in self.df.columns:
                print(f"Warning: Column '{col}' not found in data. Skipping config.")
                return

        if len(real_line_cols) == 1:
            real_line_cols = [real_line_cols[0], real_line_cols[0]]

        # Iterate over each metric
        for metric in self.metrics:
            real_metric = self.metric_labels.get(metric, metric)
            if real_metric not in self.df.columns:
                continue

            # Group by the specified columns to create separate plots
            # We use groupby on the dataframe to iterate over unique combinations
            grouped = self.df.groupby(real_group_cols)
            
            for name, group_data in grouped:
                # name is a tuple of values corresponding to group_cols
                if not isinstance(name, tuple):
                    name = (name,)

                # Construct description from group values
                group_desc = " ".join([f"{col}: {val}" for col, val in zip(real_group_cols, name)])

                #Create title from category and description
                title = f"{category_name}\n{group_desc}\n{real_metric}"

                # Clean desc for filename
                filename = group_desc.replace(": ", "-").replace(" ", "_")

                # Clean category for directory
                directory = category_name.replace(": ", "-").replace(" ", "_")
                
                # Output path: {root}/{Category}/{SubCategory}/{Metric}/{group_desc}.png
                output_path = os.path.join(
                    self.output_dir,
                    directory,
                    metric,
                    f"{filename}.png"
                )
                self._generate_plot(
                    data=group_data,
                    x_col=real_x_col,
                    y_col=real_metric,
                    hue_col=real_line_cols[0],
                    style_col=real_line_cols[1],
                    title=title,
                    output_path=output_path
                )

def plot_results(csv_file_path="benchmark_results.csv", visualisation_path="visualisation"):
    if visualisation_path is None:
        visualisation_path = "visualisation"
    plotter = BenchmarkPlotter(csv_file_path=csv_file_path, output_dir=visualisation_path)
    if plotter.load_data():
        plotter.run_plot_config(
            category_name="Compiler Benchmark",
            group_cols=["algorithm", "hardware", "benchmark_level"],
            line_cols=["compiler","opt_level"]
        )
    else:
        print("Could not load data or data is empty.")

def plot_mapping_benchmark(csv_file_path="mapping_results.csv", visualisation_path="visualisation"):
    """
    Category 1: Mapping Only
    """
    plotter = BenchmarkPlotter(csv_file_path, visualisation_path)
    if plotter.load_data():
        # Group by: Hardware, Compiler, Opt_Level (as requested to have separate graphs per opt_level)
        # Hue: benchmark_level
        # Average: algos
        plotter.run_plot_config(
            category_name="Mapping Only",
            group_cols=["hardware", "compiler", "opt_level"],
            line_cols=["benchmark_level"]
        )

        # Group by: Benchmark_Level, Compiler, Opt_Level
        # Hue: hardware
        plotter.run_plot_config(
            category_name="Mapping Only",
            group_cols=["benchmark_level", "compiler", "opt_level"],
            line_cols=["hardware"]
        )

        # Group by: Benchmark_Level, Hardware, Opt_Level
        # Hue: compiler
        plotter.run_plot_config(
            
            category_name="Mapping Only",
            group_cols=["benchmark_level", "hardware", "opt_level"],
            line_cols=["compiler"]
        )
    else:
        print("Could not load data or data is empty.")

def plot_compilation_benchmark(csv_file_path="compilation_results.csv", visualisation_path="visualisation"):
    """
    Category 2: Full Compilation
    """
    plotter = BenchmarkPlotter(csv_file_path, visualisation_path)
    if plotter.load_data():
        # Group by: opt_level, algorithm, benchmark_level
        # Hue: compiler
        # Average: hardware
        plotter.run_plot_config(
            
            category_name="Full Compilation",
            group_cols=["opt_level", "algorithm", "benchmark_level"],
            line_cols=["compiler"]
        )

        # Group by: opt_level, hardware, benchmark_level
        # Hue: compiler
        # Average: algos
        plotter.run_plot_config(
            
            category_name="Full Compilation",
            group_cols=["opt_level", "hardware", "benchmark_level"],
            line_cols=["compiler"]
        )

        # Group by: algorithm, hardware, benchmark_level
        # Hue: compiler
        # Average: opt_level
        plotter.run_plot_config(
            
            category_name="Full Compilation",
            group_cols=["algorithm", "hardware", "benchmark_level"],
            line_cols=["compiler"]
        )
    else:
        print("Could not load data or data is empty.")

if __name__ == "__main__":
    plot_results()
