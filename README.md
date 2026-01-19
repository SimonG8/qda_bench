# Vergleichende Analyse von Entwurfsautomatisierungsmethoden für Quantencomputer

Dieses Repository enthält den Quellcode und die Benchmark-Suite für die Masterarbeit im Studiengang "Information Engineering". Ziel des Projekts ist eine fundierte, vergleichende Analyse verschiedener Software-Frameworks für die Entwurfsautomatisierung von Quantenschaltkreisen.

## Projektziel

Die Arbeit untersucht, wie effizient aktuelle Compiler-Frameworks (Qiskit, Cirq, pytket) Quantenalgorithmen auf realistische Hardware-Topologien abbilden. Der Fokus liegt auf folgenden Aspekten:
- **Routing & Mapping:** Wie werden logische Qubits unter Berücksichtigung begrenzter Konnektivität auf physische Qubits verteilt?
- **Gatter-Optimierung:** Wie gut können die Tools die Anzahl der Gatter und die Schaltkreistiefe reduzieren?
- **Vergleichsmetriken:** Compiler-Laufzeit, resultierende Gatter-Anzahl (insb. 2-Qubit-Gatter), Schaltkreistiefe und Anzahl eingefügter SWAP-Gatter.

Als Basis für die Evaluation dient **MQT Bench**, eine standardisierte Benchmark-Suite für Quantencomputing.

## Forschungsfragen

Das Projekt adressiert folgende Kernfragen:
1. **Effizienz und Genauigkeit:** Wie unterscheiden sich aktuelle Entwurfsautomatisierungsmethoden hinsichtlich Effizienz und Genauigkeit?
2. **Hardware- und Schaltkreisverhalten:** Wie verhalten sich Compiler und Algorithmen auf unterschiedlicher Hardware mit verschiedenen Schaltkreisen? Lassen sich Rückschlüsse für spezifische Anwendungsbereiche ziehen?

## Benchmark-Kategorien

Das Framework bietet spezialisierte Benchmark-Modi, um verschiedene Aspekte der Kompilierung isoliert zu betrachten (siehe `quantum_bench/runner.py` und `quantum_bench/plotter.py`):

### 1. Nur Mapping (Mapping Only)
Dieser Modus vergleicht, wie sich verschiedene Hardware-Architekturen auf die Mapping-Algorithmen der Compiler auswirken.
- **Fokus:** Isoliertes Betrachten der Mapping- und Routing-Phasen (z.B. durch Beschränkung auf `rebase` und `mapping`).
- **Analyse:** Untersucht wird das Verhalten über verschiedene Abstraktionsebenen hinweg (ALG, INDEP, NATIVEGATES, MAPPED).
- **Ziel:** Identifikation von Stärken und Schwächen der Router bei unterschiedlichen Topologien.

### 2. Vollständige Kompilierung (Full Compiling)
Dieser Modus vergleicht, wie sich verschiedene Schaltkreise auf die gesamte Kompilierungskette auswirken.
- **Fokus:** Vollständiger Kompilierungsdurchlauf mit allen Optimierungen.
- **Analyse:** Konzentration auf die algorithmische Ebene (ALG).
- **Ziel:** Bewertung der Gesamtperformance der Compiler für verschiedene Quantenalgorithmen.

## Parallelisierung

Für das Ausführen großer Benchmarks steht der separate Git-Branch **`Paralelisierung`** zur Verfügung. Dieser Branch erweitert das Framework um Multiprocessing-Fähigkeiten, wodurch Benchmarks auf mehreren Kernen gleichzeitig ausgeführt werden können. Dies reduziert die Wartezeit bei umfangreichen Experimenten erheblich.

## Projektstruktur und Funktionalität

Der Code ist modular aufgebaut, um flexible Tests verschiedener Compiler und Hardware-Architekturen zu ermöglichen.

### Hauptkomponenten

*   **`main.py`**
    Der Einstiegspunkt der Anwendung. Hier wird die Benchmark-Konfiguration definiert (welche Hardware, welche Algorithmen, Qubit-Anzahl, Optimierungslevel) und der `run_benchmark` Prozess angestoßen.
    
*   **`quantum_bench/runner.py`**
    Die zentrale Steuereinheit.
    - Iteriert über alle konfigurierten Kombinationen aus Hardware, Algorithmen und Compilern.
    - Ruft die entsprechenden Compiler-Adapter auf.
    - Sammelt Metriken (Gate Count, Depth, Compile Time, etc.) und speichert sie in einer CSV-Datei.
    - Implementiert die Logik für `run_mapping_benchmark` und `run_compilation_benchmark`.

*   **`quantum_bench/data/mqt_provider.py`**
    Schnittstelle zu MQT Bench.
    - Lädt Benchmark-Schaltkreise und Hardware-Definitionen.
    - Verifiziert und visualisiert Schaltkreise.

*   **`quantum_bench/hardware/model.py`**
    Definiert die Hardware-Modelle (Topologie, Basis-Gatter).

*   **`quantum_bench/plotter.py`**
    Analysiert die generierten CSV-Dateien.
    - Erstellt detaillierte Plots mittels `seaborn` und `matplotlib`.
    - Bietet spezialisierte Plot-Funktionen für die "Mapping Only" und "Full Compiling" Szenarien.

### Compiler-Adapter (`quantum_bench/compilers/`)

Um eine faire und einheitliche Schnittstelle zu gewährleisten, wird das Adapter-Pattern verwendet (Qiskit, Cirq, pytket).

## Nutzung

1.  **Abhängigkeiten installieren:**
    Stellen Sie sicher, dass alle benötigten Bibliotheken installiert sind (`qiskit`, `cirq`, `pytket`, `mqt.bench`, `mqt.qcec`, `pandas`, `seaborn`, `networkx`).

2.  **Benchmark konfigurieren:**
    Passen Sie die Parameter in `main.py` an. Wählen Sie zwischen `run_mapping_benchmark` oder `run_compilation_benchmark` je nach Untersuchungsziel.

    Beispielkonfiguration:
    ```python
    # Beispiel: Ausführen eines Mapping-Benchmarks
    run_mapping_benchmark(
        hardware_names=["ibm_eagle_127", "rigetti_ankaa_84"],
        algo_names=["qft", "grover"],
        qubit_ranges=[4, 10, 20],
        output_file="MAPPING_Result.csv"
    )
    ```

3.  **Ausführen:**
    Starten Sie das Skript über:
    ```bash
    python main.py
    ```

## Quellen & Referenzen

Die Arbeit stützt sich auf aktuelle Forschungsliteratur und Dokumentationen der verwendeten Tools:
- **MQT Bench:** [https://www.cda.cit.tum.de/mqtbench/](https://www.cda.cit.tum.de/mqtbench/)
- **Qiskit:** [https://qiskit.org/](https://qiskit.org/)
- **Cirq:** [https://quantumai.google/cirq](https://quantumai.google/cirq)
- **pytket:** [https://cqcl.github.io/tket/pytket/api/](https://cqcl.github.io/tket/pytket/api/)
