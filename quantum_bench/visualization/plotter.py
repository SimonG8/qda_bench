import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_results(csv_file="benchmark_results_final.csv"):
    # Pfad-Logik (wie zuvor)
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
                 csv_file = r"C:\Users\admin\PycharmProjects\Entwurfsautomatisierung_Quantencomputing\benchmark_results_final.csv"

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

    # Nur Opt-Level 3 betrachten für den Vergleich der besten Ergebnisse
    df_opt = df[df["opt_level"] == 3]

    sns.set_theme(style="whitegrid")
    
    # Metriken, die wir plotten wollen
    metrics = {
        "compile_time": "Kompilierungszeit (s)",
        "gate_count": "Gesamt-Gatteranzahl",
        "depth": "Schaltkreistiefe",
        "2q_gates": "Anzahl 2-Qubit Gatter (CX/CZ)",
        "swap_gates": "Anzahl SWAP Gatter"
    }

    # Algorithmen, die wir plotten wollen
    algorithms = df_opt["algorithm"].unique()

    for algo in algorithms:
        algo_subset = df_opt[df_opt["algorithm"] == algo]

        for metric, label in metrics.items():
            # Prüfen, ob die Metrik überhaupt im DF existiert (z.B. swap_gates neu)
            if metric not in df.columns:
                continue

            plt.figure(figsize=(10, 6))

            # Lineplot eignet sich gut für Skalierung über Qubits
            # Wir nutzen Marker, um die Datenpunkte deutlich zu machen
            sns.lineplot(
                data=algo_subset,
                x="qubits",
                y=metric,
                hue="compiler",
                style="compiler",
                markers=True,
                dashes=False,
                linewidth=2.5,
                markersize=8
            )

            # Log-Skala für Zeit oft sinnvoll, für Gatter linear besser lesbar (außer bei exp. Wachstum)
            if metric == "compile_time":
                plt.yscale("log")

            plt.title(f"{label} vs. Qubit-Anzahl ({algo.upper()})")
            plt.xlabel("Anzahl Qubits")
            plt.ylabel(label)
            plt.legend(title="Compiler")
            
            # Dateiname generieren
            filename = f"plot_{algo}_{metric}.png"
            plt.savefig(filename)
            plt.close() # Speicher freigeben
            print(f"Erstellt: {filename}")

if __name__ == "__main__":
    plot_results()
