# Comparative Analysis of Design Automation Methods for Quantum Computers

This repository contains the source code and benchmark suite for the Master's thesis in the "Information Engineering" program. The goal of the project is a sound, comparative analysis of different software frameworks for the design automation of quantum circuits.

## Project Goal

The thesis investigates how efficiently current compiler frameworks (Qiskit, Cirq, pytket) map quantum algorithms to realistic hardware topologies. The focus is on the following aspects:
- **Routing & Mapping:** How are logical qubits distributed to physical qubits considering limited connectivity?
- **Gate Optimization:** How well can the tools reduce the number of gates and circuit depth?
- **Comparison Metrics:** Compiler runtime, resulting gate count (esp. 2-qubit gates), circuit depth, and number of inserted SWAP gates.

**MQT Bench**, a standardized benchmark suite for quantum computing, serves as the basis for the evaluation.

## Research Questions

The project addresses the following key questions:
1. **Efficiency and Accuracy:** How do current design automation methods differ in terms of efficiency and accuracy?
2. **Hardware and Circuit Behavior:** How do compilers and algorithms behave on different hardware with different circuits? Can conclusions be drawn for specific application areas?

## Project Structure and Functionality

The code is modular to allow flexible testing of different compilers and hardware architectures.

### Main Components

*   **`main.py`**
    The entry point of the application. Here, the benchmark configuration is defined (which hardware, which algorithms, qubit count, optimization level) and the `run_benchmark` process is initiated. It supports different modes, such as focusing on mapping/routing or full compilation.

*   **`quantum_bench/runner.py`**
    The central control unit.
    - Iterates over all configured combinations of hardware, algorithms, and compilers.
    - Calls the respective compiler adapters.
    - Collects metrics (Gate Count, Depth, Compile Time, etc.) and saves them in a CSV file.
    - Can optionally trigger verification (equivalence checking) and visualization.

*   **`quantum_bench/data/mqt_provider.py`**
    Interface to MQT Bench.
    - `get_circuit`: Loads benchmark circuits (e.g., DJ, GHZ, QFT) in the desired qubit size and exports them as OpenQASM 2.0 files.
    - `verify_circuit`: Uses MQT QCEC to ensure that the compiled circuit is equivalent to the original.
    - `visualize_circuit`: Creates graphics of the circuits.
    - `get_hardware_model`: Loads hardware definitions from MQT Bench.

*   **`quantum_bench/hardware/model.py`**
    Defines the hardware models.
    - Represents the hardware topology (coupling map) and basis gates.
    - Provides a unified interface for the compiler adapters.

*   **`quantum_bench/plotter.py`**
    Analyzes the generated CSV file.
    - Creates detailed plots using `seaborn` and `matplotlib`.
    - Generates overview graphs (comparison of all compilers over qubit count) and detail plots per algorithm.
    - Visualizes metrics such as compilation time, depth, SWAP count, etc.

### Compiler Adapters (`quantum_bench/compilers/`)

To ensure a fair and unified interface, the Adapter Pattern is used. All adapters inherit from `base.py`.

*   **`base.py`**: Defines the abstract interface `CompilerAdapter`.
*   **`qiskit_adapter.py`**:
    - Uses the IBM Qiskit `transpile` workflow.
    - Creates a `Target` object based on the hardware definition.
    - Maps metrics from the transpiled circuit.
*   **`cirq_adapter.py`**:
    - Implements compilation for Google Cirq.
    - Converts the hardware topology into a `cirq.Device`.
    - Uses routers like `cirq.RouteCQC` and optimizers like `cirq.optimize_for_target_gateset`.
*   **`pytket_adapter.py`**:
    - Uses the `pytket` compiler stack.
    - Uses `MappingManager` and `LexiRouteRoutingMethod` for routing.
    - Executes optimization passes like `FullPeepholeOptimise` and `SynthesiseTket`.

## Usage

1.  **Install Dependencies:**
    Ensure that all required libraries are installed (see imports in the files: `qiskit`, `cirq`, `pytket`, `mqt.bench`, `mqt.qcec`, `pandas`, `seaborn`, `networkx`).

2.  **Configure Benchmark:**
    Adjust the parameters in `main.py`. The project supports running benchmarks on various hardware architectures (e.g., IBM Eagle, Rigetti Ankaa, IonQ Forte) and algorithms (e.g., QFT, Grover, VQE, QAOA).

    Example configuration from `main.py`:
    ```python
    # Example: Running a mapping-focused benchmark
    run_benchmark(
        hardware_names=["ibm_eagle_127", "rigetti_ankaa_84", "ionq_forte_36"],
        algo_names=["qft", "grover", "vqe", "qaoa", "randomcircuit", "ghz"],
        qubit_ranges=[4, 5, 8, 10, 15, 16, 20, 25, 32, 36, 40, 50, 64, 75, 84, 100, 127],
        benchmark_levels=["ALG", "INDEP", "NATIVEGATES", "MAPPED"],
        opt_levels=[3],
        num_runs=1,
        output_file="MAPPING_Result.csv",
        full_compilation=False,
        active_phases=["rebase", "mapping"]
    )
    ```

3.  **Execute:**
    Start the script via:
    ```bash
    python main.py
    ```

4.  **Results:**
    - The raw data can be found in the specified CSV file (e.g., `MAPPING_Result.csv`).
    - Plots are saved (if enabled) in the `visualisation/plots/` folder.
    - Compiled QASM files land in the cache folder `benchmarks_cache/`.

## Sources & References

The work relies on current research literature and documentation of the tools used:
- **MQT Bench:** [https://www.cda.cit.tum.de/mqtbench/](https://www.cda.cit.tum.de/mqtbench/)
- **Qiskit:** [https://qiskit.org/](https://qiskit.org/)
- **Cirq:** [https://quantumai.google/cirq](https://quantumai.google/cirq)
- **pytket:** [https://cqcl.github.io/tket/pytket/api/](https://cqcl.github.io/tket/pytket/api/)
