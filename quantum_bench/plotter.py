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
            "swap_gates": "Number of SWAP Gates"
        }

    def load_data(self):
        if not os.path.exists(self.csv_file_path):
            print(f"Error: File '{self.csv_file_path}' not found.")
            return False
        self.df = pd.read_csv(self.csv_file_path)
        # Filter for successful runs
        if "success" in self.df.columns:
            self.df = self.df[self.df["success"] == True]
        return not self.df.empty

    def _generate_plot(self, data, x_col, y_col, hue_col, title, output_path):
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
                style=hue_col,
                markers=True,
                dashes=False,
                linewidth=2,
                markersize=8,
                errorbar=('ci', 95) # 95% confidence interval for statistical dispersion
            )
            
            if y_col == "compile_time":
                plt.yscale("log")

            plt.title(title)
            plt.xlabel("Number of Qubits")
            plt.ylabel(self.metric_labels.get(y_col, y_col))
            plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
            plt.tight_layout()
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            plt.savefig(output_path)
            plt.close()
            print(f"Generated: {output_path}")
        except Exception as e:
            print(f"Failed to generate plot {output_path}: {e}")
            plt.close()

    def run_plot_config(self, category_name, sub_category_name, group_cols, hue_col, x_col="qubits"):
        """
        Abstract function to generate plots based on configuration.
        
        Args:
            category_name: Top level folder (e.g., "Mapping_Only")
            sub_category_name: Sub folder (e.g., "Hardware_Compiler_vs_BenchmarkLevel")
            group_cols: List of columns to group by (creates separate plot files)
            hue_col: Column to use for different lines in the graph
            x_col: Column for x-axis
        """
        print(f"--- Processing {category_name} / {sub_category_name} ---")
        
        # Ensure all columns exist
        required_cols = group_cols + [hue_col, x_col]
        for col in required_cols:
            if col not in self.df.columns:
                print(f"Warning: Column '{col}' not found in data. Skipping config.")
                return

        # Iterate over each metric
        for metric in self.metrics:
            if metric not in self.df.columns:
                continue

            # Group by the specified columns to create separate plots
            # We use groupby on the dataframe to iterate over unique combinations
            grouped = self.df.groupby(group_cols)
            
            for name, group_data in grouped:
                # name is a tuple of values corresponding to group_cols
                if not isinstance(name, tuple):
                    name = (name,)
                
                # Construct filename from group values
                group_desc = "_".join([f"{col}-{val}" for col, val in zip(group_cols, name)])
                
                # Clean filename
                group_desc = group_desc.replace(" ", "_").replace("/", "-")
                
                # Output path: {root}/{Category}/{SubCategory}/{Metric}/{group_desc}.png
                output_path = os.path.join(
                    self.output_dir,
                    category_name,
                    sub_category_name,
                    metric,
                    f"{group_desc}.png"
                )
                
                title = f"{sub_category_name}\n{group_desc} - {self.metric_labels.get(metric, metric)}"
                
                self._generate_plot(
                    data=group_data,
                    x_col=x_col,
                    y_col=metric,
                    hue_col=hue_col,
                    title=title,
                    output_path=output_path
                )

    def plot_mapping_benchmarks(self):
        """
        Category 1: Mapping Only
        """
        category = "Mapping_Only"
        
        # Group by: Hardware, Compiler, Opt_Level (as requested to have separate graphs per opt_level)
        # Hue: benchmark_level
        # Average: algos
        self.run_plot_config(
            category_name=category,
            sub_category_name="Hardware_Compiler_vs_BenchmarkLevel",
            group_cols=["hardware", "compiler", "opt_level"],
            hue_col="benchmark_level"
        )

        # Group by: Benchmark_Level, Compiler, Opt_Level
        # Hue: hardware
        self.run_plot_config(
            category_name=category,
            sub_category_name="BenchmarkLevel_Compiler_vs_Hardware",
            group_cols=["benchmark_level", "compiler", "opt_level"],
            hue_col="hardware"
        )

        # Group by: Benchmark_Level, Hardware, Opt_Level
        # Hue: compiler
        self.run_plot_config(
            category_name=category,
            sub_category_name="BenchmarkLevel_Hardware_vs_Compiler",
            group_cols=["benchmark_level", "hardware", "opt_level"],
            hue_col="compiler"
        )

    def plot_compilation_benchmarks(self):
        """
        Category 2: Full Compilation
        """
        category = "Full_Compilation"

        # Group by: opt_level, algorithm, benchmark_level
        # Hue: compiler
        # Average: hardware
        self.run_plot_config(
            category_name=category,
            sub_category_name="OptLevel_Algorithm_vs_Compiler",
            group_cols=["opt_level", "algorithm", "benchmark_level"],
            hue_col="compiler"
        )

        # Group by: opt_level, hardware, benchmark_level
        # Hue: compiler
        # Average: algos
        self.run_plot_config(
            category_name=category,
            sub_category_name="OptLevel_Hardware_vs_Compiler",
            group_cols=["opt_level", "hardware", "benchmark_level"],
            hue_col="compiler"
        )

        # Group by: algorithm, hardware, benchmark_level
        # Hue: compiler
        # Average: opt_level
        self.run_plot_config(
            category_name=category,
            sub_category_name="Algorithm_Hardware_vs_Compiler",
            group_cols=["algorithm", "hardware", "benchmark_level"],
            hue_col="compiler"
        )

def plot_results(csv_file_path="benchmark_results_final.csv", visualisation_path="visualisation", full_compilation=False):
    plotter = BenchmarkPlotter(csv_file_path, visualisation_path)
    if plotter.load_data():
        if full_compilation:
            plotter.plot_compilation_benchmarks()
        else:
            plotter.plot_mapping_benchmarks()
    else:
        print("Could not load data or data is empty.")

if __name__ == "__main__":
    plot_results()
