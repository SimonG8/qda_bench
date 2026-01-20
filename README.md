# Entwurfsautomatisierung für Quantencomputer

Dieses Repository enthält den Quellcode für die Masterarbeit im Studiengang "Information Engineering" mit dem Titel **"Vergleichende Analyse von Methoden zur Entwurfsautomatisierung für Quantencomputer"**.

## Projektbeschreibung

Ziel der Arbeit ist es, verschiedene Ansätze der Entwurfsautomatisierung – insbesondere Routing/Mapping und Gate-Optimierung – zu vergleichen. Dabei werden Metriken wie Laufzeit, Gatteranzahl und die Anzahl der eingefügten SWAP-Gatter analysiert.

Es werden etablierte Compiler-Frameworks verwendet, um unterschiedliche Strategien zur Anpassung und Optimierung von Quanten-Schaltkreisen zu bewerten:
*   **Qiskit**
*   **Cirq**
*   **pytket**

Als Basis für die Bewertung dient die standardisierte Benchmark-Suite **MQT Bench** (https://www.cda.cit.tum.de/mqtbench/).

## Benchmark-Kategorien

Das Framework stellt zwei vorimplementierte Hauptkategorien für Benchmarks bereit, die in `quantum_bench/runner.py` definiert sind:

### 1. Full Compilation
Dieser Modus führt den vollständigen Kompilierungsprozess durch. Er dient dazu, die Gesamtleistung der Compiler von der algorithmischen Beschreibung bis zum hardware-konformen Schaltkreis zu bewerten.
*   **Funktion:** `run_compilation_benchmark`
*   **Fokus:** Gesamte Toolchain inklusive High-Level-Optimierungen, Mapping und Routing.

### 2. Mapped Only
Dieser Modus isoliert das Mapping- und Routing-Problem. Es werden spezifisch nur die Phasen für das Rebasing (Anpassung an das Gate-Set) und das Mapping (Platzierung und Routing) aktiviert.
*   **Funktion:** `run_mapping_benchmark`
*   **Fokus:** Bewertung der Effizienz von Mapping-Algorithmen und der Anzahl der benötigten SWAP-Gatter, ohne Einfluss weiterer Optimierungsschritte.

## Performance & Parallelisierung

Für die Ausführung von größeren Benchmarks oder umfangreichen Testreihen wird auf den Branch **`Parallelisierung`** verwiesen. Dieser Branch erweitert das Framework um Möglichkeiten zur parallelen Ausführung der Kompilierungsvorgänge, was die Gesamtlaufzeit der Benchmarks signifikant reduziert.

## Installation

Stellen Sie sicher, dass alle Abhängigkeiten installiert sind:

```bash
pip install -r requirements.txt
```

Die Konfiguration und Ausführung der Benchmarks erfolgt über die `main.py`.
