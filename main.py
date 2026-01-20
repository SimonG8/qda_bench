from mqt.bench.benchmarks import get_available_benchmark_names
from mqt.bench.targets import get_available_device_names, get_device
from qiskit import generate_preset_pass_manager
from quantum_bench.data.mqt_provider import visualize_circuit, get_circuit, get_hardware_model
from quantum_bench.plotter import plot_results
from quantum_bench.runner import run_benchmark, run_mapping_benchmark, run_compilation_benchmark
import qiskit.transpiler.passes.layout.sabre_layout

if __name__ == "__main__":
    benchmarks = ["qft", "vqe_real_amp", "qaoa", "randomcircuit", "ghz"]
    hardware = ["ionq_forte_36"] #["ibm_eagle_127", "rigetti_ankaa_84", "ionq_forte_36"]
    qubits = [4, 5, 8, 10, 15, 16, 20, 25, 32, 36, 40, 50, 64, 75, 84, 100, 127]
    run_mapping_benchmark(hardware, benchmarks, qubits, output_file="mapping_result_ionq.csv", max_workers=5, max_queued_tasks=10)
    #run_compilation_benchmark(hardware, benchmarks, qubits, max_workers=4, max_queued_tasks=8)

    #run_mapping_benchmark(["grover"], hardware, qubits, plot_path="mapping_resuls_grover.csv", max_workers=4, max_queued_tasks=8)
    #run_compilation_benchmark(["grover"], hardware, qubits, plot_path="compilation_resuls_grover.csv", max_workers=4, max_queued_tasks=8)

    # FEHLENDE BENCHMARKS:

    # Mapping Only:
    # ibm_eagle_127,ALG,qft,84,Pytket,3
    # ibm_eagle_127,ALG,qaoa,100,Pytket,3
    # ibm_eagle_127,INDEP,qaoa,100,Pytket,3
    # ibm_eagle_127,MAPPED,randomcircuit,127,Pytket,3
    # ibm_eagle_127,MAPPED,randomcircuit,127,Cirq,3

    # Full Compilation:
    # ibm_eagle_127,ALG,qaoa,100,Pytket,3
