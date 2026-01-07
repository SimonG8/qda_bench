import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_results(csv_file="benchmark_results_final.csv"):
    # Ermittle den absoluten Pfad zur CSV-Datei relativ zum Projekt-Root
    # Annahme: Das Skript wird entweder aus dem Root oder dem visualization-Ordner ausgeführt.
    # Wir suchen die Datei im Projekt-Root (zwei Ebenen über diesem Skript, wenn installiert, 
    # oder im aktuellen Arbeitsverzeichnis).
    
    if not os.path.exists(csv_file):
        # Versuche, die Datei im Projekt-Root zu finden
        # Pfad: .../quantum_bench/visualization/plotter.py -> .../benchmark_results_final.csv
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        potential_path = os.path.join(project_root, csv_file)
        
        # Alternative: Wenn wir im Projekt-Root sind, aber der Pfad nicht stimmt
        if os.path.exists(potential_path):
            csv_file = potential_path
        else:
            # Fallback: Suche im aktuellen Arbeitsverzeichnis (CWD)
            cwd_path = os.path.join(os.getcwd(), csv_file)
            if os.path.exists(cwd_path):
                csv_file = cwd_path
            else:
                 # Hardcoded Fallback für die IDE-Umgebung des Users
                 csv_file = r"C:\Users\admin\PycharmProjects\Entwurfsautomatisierung_Quantencomputing\benchmark_results_final.csv"

    print(f"Lese Ergebnisse aus: {csv_file}")
    
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Fehler: Datei '{csv_file}' nicht gefunden. Bitte führen Sie zuerst main.py aus.")
        return

    df = df[df["success"] == True]
    
    if df.empty:
        print("Warnung: Keine erfolgreichen Benchmarks in der CSV-Datei gefunden.")
        return

    # Globales Styling
    sns.set_theme(style="whitegrid")
    
    # 1. Plot: Compilation Time vs Qubits (für Opt Level 3)
    plt.figure(figsize=(10, 6))
    subset = df[df["opt_level"] == 3]
    if not subset.empty:
        sns.lineplot(data=subset, x="qubits", y="compile_time", hue="compiler", style="algorithm", markers=True)
        plt.yscale("log") # Logarithmisch, da Laufzeiten stark variieren
        plt.title("Kompilierungszeit (Level 3) vs. Qubit-Anzahl")
        plt.ylabel("Zeit (s)")
        plt.savefig("plot_compile_time.png")
        print("Plot gespeichert: plot_compile_time.png")
    
    # 2. Plot: Gate Count Overhead
    # Hier wäre Normalisierung sinnvoll, wir plotten absolute Werte beispielhaft für QFT
    plt.figure(figsize=(10, 6))
    qft_subset = df[(df["algorithm"] == "qft") & (df["opt_level"] == 3)]
    if not qft_subset.empty:
        sns.barplot(data=qft_subset, x="qubits", y="gate_count", hue="compiler")
        plt.title("Gatter-Anzahl nach Kompilierung (QFT, Level 3)")
        plt.ylabel("Anzahl Gatter")
        plt.savefig("plot_gate_count_qft.png")
        print("Plot gespeichert: plot_gate_count_qft.png")
    
    # 3. Plot: Tiefe (Depth) Vergleich
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x="compiler", y="depth", hue="opt_level")
    plt.title("Verteilung der Schaltkreistiefe über alle Algorithmen")
    plt.savefig("plot_depth_distribution.png")
    print("Plot gespeichert: plot_depth_distribution.png")

if __name__ == "__main__":
    plot_results()
