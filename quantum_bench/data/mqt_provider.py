import os

from mqt.bench import get_benchmark, BenchmarkLevel
from mqt.qcec import verify_compilation
from qiskit import QuantumCircuit, qasm2


def get_circuit(algo_name: str, num_qubits: int, export_dir: str = "benchmarks_cache") -> str:
    """
    Lädt einen Benchmark-Schaltkreis und gibt den OpenQASM 2 String zurück.
    Wir nutzen QASM 2 als neutrales Austauschformat, da Qiskit's from_qasm_file
    standardmäßig QASM 2 erwartet und Cirq/pytket damit besser klarkommen.

    Args:
        algo_name: Name des Algorithmus (z.B. 'dj', 'ghz', 'qft').
        num_qubits: Anzahl der Qubits.
        export_dir: Exportordner (path)

    Returns:
        Pfad zur generierten QASM-Datei oder der QASM-String.
    """
    try:
        # Abruf des Schaltkreises auf Algorithmischer Ebene
        qc = get_benchmark(
            benchmark=algo_name,
            level=BenchmarkLevel.ALG,
            circuit_size=num_qubits
        )

        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

        filename = os.path.join(export_dir, f"{algo_name}_{num_qubits}.qasm")
        qasm2.dump(qc, filename)

        return filename

    except Exception as e:
        print(f" Benchmark {algo_name} mit {num_qubits} Qubits fehlgeschlagen: {e}")
        return None


def verify_circuit(qasm_file: str, compiled_qasm_file: str) -> str:
    """
    Verifiziert die Äquivalenz zwischen Original und Kompilat mittels MQT QCEC.
    """
    try:
        result = verify_compilation(qasm_file, compiled_qasm_file, check_partial_equivalence=True,
                                    transform_dynamic_circuit=True)
        return result.equivalence.name

    except Exception as e:
        print(f"Verifikation von {compiled_qasm_file} fehlgeschlagen: {e}")
        return "Error"


def visualize_circuit(qasm_file: str, hardware: str, visualisation_path: str = None):
    if visualisation_path is None:
        visualisation_path = "visualisation"
    try:
        circuit_dir = os.path.join(visualisation_path, "circuits", hardware)
        if not os.path.exists(circuit_dir):
            os.makedirs(circuit_dir)
        _, file = os.path.split(qasm_file.removesuffix(".qasm"))
        filename = os.path.join(circuit_dir, f"{file}.png")
        QuantumCircuit.from_qasm_file(qasm_file).draw(output="mpl", filename=filename)
    except Exception as e:
        print(f"Visualisierung von {qasm_file} fehlgeschlagen: {e}")
