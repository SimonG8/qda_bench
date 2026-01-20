import os
from typing import Optional

from mqt.bench import get_benchmark, BenchmarkLevel
from mqt.bench.targets import get_device
from mqt.qcec import verify
from qiskit import QuantumCircuit, qasm2

from quantum_bench.hardware.model import HardwareModel


def get_circuit(hardware_name: str, algo_name: str, num_qubits: int, benchmark_level: str, export_dir: str = "benchmarks_cache") -> Optional[str]:
    """
    Loads a benchmark circuit and returns the path to the OpenQASM 2 file.

    Args:
        hardware_name: Name of the target hardware.
        algo_name: Name of the algorithm (e.g., 'dj', 'ghz', 'qft').
        num_qubits: Number of qubits.
        benchmark_level: Level of the benchmark ('ALG', 'INDEP', 'NATIVEGATES', 'MAPPED').
        export_dir: Directory to save the generated QASM file.

    Returns:
        Path to the generated QASM file or None if generation fails.
    """
    try:
        level_map = {
            "ALG": BenchmarkLevel.ALG,
            "INDEP": BenchmarkLevel.INDEP,
            "NATIVEGATES": BenchmarkLevel.NATIVEGATES,
            "MAPPED": BenchmarkLevel.MAPPED
        }
        
        if benchmark_level not in level_map:
            raise ValueError(f"Unknown benchmark level: {benchmark_level}")

        kwargs = {"benchmark": algo_name, "level": level_map[benchmark_level], "circuit_size": num_qubits}
        if benchmark_level in ["NATIVEGATES", "MAPPED"]:
            kwargs["target"] = get_device(hardware_name)

        qc = get_benchmark(**kwargs)

        os.makedirs(export_dir, exist_ok=True)
        filename = os.path.join(export_dir, f"{benchmark_level}_{algo_name}_{num_qubits}.qasm")
        qasm2.dump(qc, filename)

        return filename

    except Exception as e:
        print(f"Failed to load {benchmark_level} benchmark {algo_name} with {num_qubits} qubits: {e}")
        return None


def verify_circuit(qasm_file: str, compiled_qasm_file: str) -> str:
    """
    Verifies the equivalence between the original and compiled circuit using MQT QCEC.

    Args:
        qasm_file: Path to the original QASM file.
        compiled_qasm_file: Path to the compiled QASM file.

    Returns:
        Result of the equivalence check (e.g., "equivalent", "not_equivalent", "error").
    """
    try:
        result = verify(qasm_file, compiled_qasm_file, check_partial_equivalence=True, transform_dynamic_circuit=True)
        return result.equivalence.name
    except Exception as e:
        print(f"Verification of {compiled_qasm_file} failed: {e}")
        return "Error"


def visualize_circuit(qasm_file: str, hardware: str, visualisation_path: str = "visualisation"):
    """
    Visualizes the quantum circuit and saves it as an image.

    Args:
        qasm_file: Path to the QASM file.
        hardware: Name of the hardware (used for directory structure).
        visualisation_path: Base path for visualization output.
    """
    try:
        circuit_dir = os.path.join(visualisation_path, "circuits", hardware)
        os.makedirs(circuit_dir, exist_ok=True)
        
        _, file = os.path.split(qasm_file.removesuffix(".qasm"))
        filename = os.path.join(circuit_dir, f"{file}.png")
        
        QuantumCircuit.from_qasm_file(qasm_file).draw(output="mpl", filename=filename, idle_wires=False)
    except Exception as e:
        print(f"Visualization of {qasm_file} failed: {e}")


def get_hardware_model(device_name: str) -> Optional[HardwareModel]:
    """
    Loads a hardware model from MQT Bench.

    Args:
        device_name: Name of the device to load.

    Returns:
        HardwareModel instance or None if loading fails.
    """
    try:
        device = get_device(device_name)
        return HardwareModel(
            name=device_name,
            num_qubits=device.num_qubits,
            edges=list(device.build_coupling_map()),
            basis_gates=list(device.operation_names)
        )
    except Exception as e:
        print(f"Could not load hardware {device_name}: {e}")
        return None
