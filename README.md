# Vergleichende Analyse von Methoden zur Entwurfsautomatisierung für Quantencomputer

Dieses Repository beinhaltet den Quellcode und die Benchmark-Suite für die Masterarbeit im Studiengang "Information Engineering". Ziel des Projekts ist eine fundierte, vergleichende Analyse verschiedener Software-Frameworks zur Entwurfsautomatisierung (Design Automation) von Quantenschaltkreisen.

## Projektziel

Die Arbeit untersucht, wie effizient aktuelle Compiler-Frameworks (Qiskit, Cirq, pytket) Quantenalgorithmen auf realistische Hardware-Topologien abbilden. Dabei stehen folgende Aspekte im Fokus:
- **Routing & Mapping:** Wie werden logische Qubits auf physikalische Qubits unter Berücksichtigung eingeschränkter Konnektivität verteilt?
- **Gate-Optimierung:** Wie gut können die Tools die Anzahl der Gatter und die Schaltkreistiefe reduzieren?
- **Vergleichsmetriken:** Laufzeit des Compilers, resultierende Gatteranzahl (insb. 2-Qubit-Gatter), Schaltkreistiefe und Anzahl eingefügter SWAP-Gatter.

Als Basis für die Evaluation dient **MQT Bench**, eine standardisierte Benchmark-Suite für Quantencomputing.

## Forschungsfragen

Das Projekt adressiert unter anderem folgende Fragestellungen:
1. Wie unterscheiden sich aktuelle Entwurfs- und Optimierungsmethoden in ihrer Effizienz und Genauigkeit?
2. In welchen Anwendungsbereichen (z.B. bestimmte Algorithmusklassen wie QFT, Graph-State) zeigen bestimmte Strategien Stärken oder Schwächen?
3. Lassen sich allgemeine Empfehlungen für den Einsatz bestimmter Compiler-Strategien in Abhängigkeit von Hardware und Algorithmus ableiten?

## Projektstruktur und Funktionsweise

Der Code ist modular aufgebaut, um verschiedene Compiler und Hardware-Architekturen flexibel testen zu können.

### Hauptkomponenten

*   **`main.py`**
    Der Einstiegspunkt der Anwendung. Hier wird die Benchmark-Konfiguration definiert (welche Hardware, welche Algorithmen, Qubit-Anzahl, Optimierungslevel) und der `run_benchmark` Prozess angestoßen.

*   **`quantum_bench/runner.py`**
    Die zentrale Steuereinheit.
    - Iteriert über alle konfigurierten Kombinationen aus Hardware, Algorithmen und Compilern.
    - Ruft die jeweiligen Compiler-Adapter auf.
    - Sammelt Metriken (Gate Count, Depth, Compile Time, etc.) und speichert diese in einer CSV-Datei (`benchmark_results_final.csv`).
    - Kann optional Verifikation (Äquivalenzprüfung) und Visualisierung anstoßen.

*   **`quantum_bench/data/mqt_provider.py`**
    Schnittstelle zu MQT Bench.
    - `get_circuit`: Lädt Benchmark-Schaltkreise (z.B. DJ, GHZ, QFT) in der gewünschten Qubit-Größe und exportiert sie als OpenQASM 2.0 Datei.
    - `verify_circuit`: Nutzt MQT QCEC, um sicherzustellen, dass der kompilierte Schaltkreis äquivalent zum Original ist.
    - `visualize_circuit`: Erstellt Grafiken der Schaltkreise.

*   **`quantum_bench/hardware/config.py`**
    Definiert die Hardware-Modelle.
    - Enthält Klassen wie `Falcon27` (IBM Falcon r5.11 Topologie) oder `Grid25` (generisches Gitter).
    - Stellt die Coupling-Maps (für Qiskit/pytket) und NetworkX-Graphen (für Cirq) bereit.

*   **`quantum_bench/plotter.py`**
    Analysiert die generierte CSV-Datei.
    - Erstellt mittels `seaborn` und `matplotlib` detaillierte Plots.
    - Generiert Übersichts-Graphen (Vergleich aller Compiler über Qubit-Anzahl) und Detail-Plots pro Algorithmus.
    - Visualisiert Metriken wie Kompilierungszeit, Tiefe, SWAP-Anzahl etc.

### Compiler-Adapter (`quantum_bench/compilers/`)

Um eine faire und einheitliche Schnittstelle zu gewährleisten, wird das Adapter-Pattern verwendet. Alle Adapter erben von `base.py`.

*   **`base.py`**: Definiert das abstrakte Interface `CompilerAdapter`.
*   **`qiskit_adapter.py`**:
    - Nutzt den IBM Qiskit `transpile` Workflow.
    - Erstellt ein `Target`-Objekt basierend auf der Hardware-Definition.
    - Mappt Metriken aus dem transpilierten Circuit.
*   **`cirq_adapter.py`**:
    - Implementiert die Kompilierung für Google Cirq.
    - Wandelt die Hardware-Topologie in ein `cirq.Device` um.
    - Nutzt Router wie `cirq.RouteCQC` und Optimierer wie `cirq.optimize_for_target_gateset`.
*   **`pytket_adapter.py`**:
    - Nutzt den `pytket` Compiler Stack.
    - Verwendet `MappingManager` und `LexiRouteRoutingMethod` für das Routing.
    - Führt Optimierungspasses wie `FullPeepholeOptimise` und `SynthesiseTket` aus.

## Nutzung

1.  **Abhängigkeiten installieren:**
    Stellen Sie sicher, dass alle benötigten Bibliotheken installiert sind (siehe Imports in den Dateien: `qiskit`, `cirq`, `pytket`, `mqt.bench`, `mqt.qcec`, `pandas`, `seaborn`, `networkx`).

2.  **Benchmark konfigurieren:**
    Passen Sie in `main.py` die Parameter an:
    ```python
    run_benchmark(
        hardware=["Falcon27"],          # Zu testende Hardware
        algorithms=["dj", "ghz"],       # Algorithmen aus MQT Bench
        qubit_ranges=[5, 10, 15],       # Qubit-Anzahlen
        opt_levels=[3],                 # Optimierungslevel
        num_runs=5                      # Wiederholungen pro Konfiguration
    )
    ```

3.  **Ausführen:**
    Starten Sie das Skript über:
    ```bash
    python main.py
    ```

4.  **Ergebnisse:**
    - Die Rohdaten finden sich in `benchmark_results_final.csv`.
    - Plots werden (sofern aktiviert) im Ordner `visualisation/plots/` gespeichert.
    - Kompilierte QASM-Dateien landen im Cache-Ordner `benchmarks_cache/`.

## Quellen & Referenzen

Die Arbeit stützt sich auf aktuelle Forschungsliteratur und Dokumentationen der verwendeten Tools:
- **MQT Bench:** [https://www.cda.cit.tum.de/mqtbench/](https://www.cda.cit.tum.de/mqtbench/)
- **Qiskit:** [https://qiskit.org/](https://qiskit.org/)
- **Cirq:** [https://quantumai.google/cirq](https://quantumai.google/cirq)
- **pytket:** [https://cqcl.github.io/tket/pytket/api/](https://cqcl.github.io/tket/pytket/api/)
