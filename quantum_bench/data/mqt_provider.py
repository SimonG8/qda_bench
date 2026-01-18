import os
from typing import Optional

from mqt.bench import get_benchmark, BenchmarkLevel
from mqt.bench.targets import get_device
from mqt.qcec import verify_compilation, verify
from numpy.f2py.auxfuncs import throw_error
from qiskit import QuantumCircuit, qasm2

from quantum_bench.hardware.model import HardwareModel


def get_circuit(hardware_name, algo_name: str, num_qubits: int, benchmark_level: str, export_dir: str = "benchmarks_cache") -> Optional[str]:
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
        match benchmark_level:
            case "ALG":
                qc = get_benchmark(
                    benchmark=algo_name,
                    level=BenchmarkLevel.ALG,
                    circuit_size=num_qubits
                )
            case "INDEP":
                qc = get_benchmark(
                    benchmark=algo_name,
                    level=BenchmarkLevel.INDEP,
                    circuit_size=num_qubits
                )
            case "NATIVEGATES":
                qc = get_benchmark(
                    target=get_device(hardware_name),
                    benchmark=algo_name,
                    level=BenchmarkLevel.NATIVEGATES,
                    circuit_size=num_qubits
                )
            case "MAPPED":
                qc = get_benchmark(
                    target=get_device(hardware_name),
                    benchmark=algo_name,
                    level=BenchmarkLevel.MAPPED,
                    circuit_size=num_qubits
                )
            case _: throw_error(f"Unbekannter Benchmark-Level: {benchmark_level}")

        # Abruf des Schaltkreises auf Algorithmischer Ebene

        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

        filename = os.path.join(export_dir, f"{algo_name}_{num_qubits}.qasm")
        qasm2.dump(qc, filename)

        return filename

    except Exception as e:
        print(f" Laden von {benchmark_level}-Benchmark {algo_name} mit {num_qubits} Qubits fehlgeschlagen: {e}")
        return None


def verify_circuit(qasm_file: str, compiled_qasm_file: str) -> str:
    """
    Verifiziert die Äquivalenz zwischen Original und Kompilat mittels MQT QCEC.
    """
    try:
        result = verify(qasm_file, compiled_qasm_file, check_partial_equivalence=True,
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
        QuantumCircuit.from_qasm_file(qasm_file).draw(output="mpl", filename=filename,idle_wires=False)
    except Exception as e:
        print(f"Visualisierung von {qasm_file} fehlgeschlagen: {e}")


def get_hardware(device_name: str) -> Optional[HardwareModel]:
    """
    Lädt ein Hardware-Modell aus MQT Bench.
    """
    try:
        device = get_device(device_name)
        basis_gates = list(device.operation_names)
        coupling_map = list(device.build_coupling_map())
        num_qubits = device.num_qubits

        return HardwareModel(device_name, num_qubits, coupling_map, basis_gates)

    except Exception as e:
        print(f"Konnte Hardware {device_name} nicht laden: {e}")
        return None
