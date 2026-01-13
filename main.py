import os

import pytket.extensions.cirq as pytket_cirq
import pytket.extensions.qiskit as pytket_qiskit
from mqt import qcec
from mqt.bench import get_benchmark, BenchmarkLevel
from mqt.bench.targets import get_device
from mqt.core import QuantumComputation
from mqt.qcec import verify_compilation, verify
from pytket.qasm import circuit_from_qasm_str
from cirq.contrib.qasm_import import circuit_from_qasm
from qiskit import qasm2, QuantumCircuit

from quantum_bench.compilers.cirq_adapter import CirqAdapter
from quantum_bench.compilers.pytket_adapter import PytketAdapter
from quantum_bench.compilers.qiskit_adapter import QiskitAdapter
from quantum_bench.runner import run_benchmark
from quantum_bench.hardware.config import Falcon27, Grid25
from quantum_bench.plotter import plot_results

if __name__ == "__main__":
    # Startet die Benchmarking-Suite mit den definierten Parametern
    run_benchmark(
        hardware_configs=[Falcon27()],
        algorithms=["dj","ghz","qft"],
        qubit_ranges=[5, 10, 15, 20],
        num_runs=1,
        opt_levels=[3],
        output_file="test_result.csv",
        run_visualisation=True,
        run_verification=True,
        run_plotter=True,
    )

