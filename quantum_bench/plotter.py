import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_results(csv_file="benchmark_results_final.csv"):
    # Pfad-Logik
    if not os.path.exists(csv_file):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        potential_path = os.path.join(project_root, csv_file)
        
        if os.path.exists(potential_path):
            csv_file = potential_path
        else:
            cwd_path = os.path.join(os.getcwd(), csv_file)
            if os.path.exists(cwd_path):
                csv_file = cwd_path
            else:
                 csv_file = r"/benchmark_results_final.csv"

    print(f"Lese Ergebnisse aus: {csv_file}")
    
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Fehler: Datei '{csv_file}' nicht gefunden.")
        return

    df = df[df["success"] == True]
    if df.empty:
        print("Warnung: Keine Daten.")
        return

    df_opt = df[df["opt_level"] == 3]

    sns.set_theme(style="whitegrid")
    
    metrics = {
        "compile_time": "Kompilierungszeit (s)",
        "gate_count": "Gesamt-Gatteranzahl",
        "depth": "Schaltkreistiefe",
        "2q_gates": "Anzahl 2-Qubit Gatter (CX/CZ)",
        "swap_gates": "Anzahl SWAP Gatter"
    }

    hardware_types = df_opt["hardware"].unique()
    algorithms = df_opt["algorithm"].unique()
    
    for hw in hardware_types:
        print(f"Erstelle Plots für Hardware: {hw}")
        df_hw = df_opt[df_opt["hardware"] == hw]

        for metric, label in metrics.items():
            if metric not in df.columns:
                continue
            
            # Ordnerstruktur: visualizations/plots/{Hardware}/{Metrik}/
            plot_dir = os.path.join("visualizations", "plots", hw, metric)
            if not os.path.exists(plot_dir):
                os.makedirs(plot_dir)

            # 1. Übersichtsplot (Alle Algorithmen in einem Graph)
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
            
            plt.title(f"Übersicht: {label} - {hw}")
            plt.xlabel("Anzahl Qubits")
            plt.ylabel(label)
            plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0, title="Legende")
            plt.tight_layout()
            
            filename = os.path.join(plot_dir, "overview.png")
            plt.savefig(filename)
            plt.close()
            print(f"  Erstellt: {filename}")
            
            # 2. Detailplots (Pro Algorithmus ein Graph)
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
                    style="compiler", # Style auch auf Compiler mappen für bessere Unterscheidung
                    markers=True, 
                    dashes=False,
                    linewidth=2.5,
                    markersize=9,
                    errorbar=('ci', 95)
                )
                if metric == "compile_time":
                    plt.yscale("log")
                
                plt.title(f"{label} - {algo.upper()} ({hw})")
                plt.xlabel("Anzahl Qubits")
                plt.ylabel(label)
                plt.legend(title="Compiler")
                plt.tight_layout()
                
                filename = os.path.join(plot_dir, f"algo_{algo}.png")
                plt.savefig(filename)
                plt.close()
                print(f"    Detail: {filename}")

if __name__ == "__main__":
    plot_results()
