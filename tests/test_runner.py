import os
import pandas as pd

from quantum_bench.runner import run_benchmark

def test_runner_integration(tmp_path, falcon_hardware, grid_hardware):
    """
    Testet den kompletten Benchmark-Durchlauf mit minimalen Parametern.
    """
    # Minimale Konfiguration für schnellen Test
    hardware_configs = [falcon_hardware, grid_hardware]
    algorithms = ['ghz']
    qubit_ranges = [5]
    num_runs = 1
    
    # Temporäre Output-Datei
    output_csv = tmp_path / "test_results.csv"
    
    # Benchmark starten
    # Wir nutzen die Standard-Hardware-Configs (Falcon27, Grid25), 
    # da diese im Runner hardcodiert instanziiert werden (könnte man auch injecten, aber für Systemtest ok)
    run_benchmark(hardware_configs, algorithms, qubit_ranges, num_runs, output_file=str(output_csv))
    
    # Prüfen, ob Datei erstellt wurde
    assert output_csv.exists()
    
    # Inhalt prüfen
    df = pd.read_csv(output_csv)
    assert not df.empty
    assert "algorithm" in df.columns
    assert "compiler" in df.columns
    assert "gate_count" in df.columns
    
    # Prüfen, ob wir Ergebnisse für beide Hardware-Typen haben
    assert "Falcon27" in df["hardware"].values
    assert "Grid25" in df["hardware"].values
    
    # Prüfen, ob wir Ergebnisse für alle Compiler haben
    assert "Qiskit" in df["compiler"].values
    assert "Cirq" in df["compiler"].values
    assert "pytket" in df["compiler"].values
