from mqt.bench.benchmarks import get_available_benchmark_names
from mqt.bench.targets import get_available_device_names, get_device
from qiskit import generate_preset_pass_manager
from quantum_bench.data.mqt_provider import visualize_circuit, get_circuit
from quantum_bench.plotter import plot_results
from quantum_bench.runner import run_benchmark, run_mapping_benchmark, run_compilation_benchmark

if __name__ == "__main__":
    benchmarks = ["qft", "vqe_real_amp", "qaoa", "randomcircuit", "ghz"]
    hardware = ["ibm_eagle_127", "rigetti_ankaa_84", "ionq_forte_36"]
    qubits = [4, 5, 8, 10, 15, 16, 20, 25, 32, 36, 40, 50, 64, 75, 84, 100, 127]
    run_mapping_benchmark(benchmarks, hardware, qubits, max_workers=4, max_queued_tasks=8)
    run_compilation_benchmark(benchmarks, hardware, qubits, max_workers=4, max_queued_tasks=8)
    # plot_results("all_bench_levels_falcon27_rebase_mapping.csv",True)


    # pm = generate_preset_pass_manager(3,target=get_device("ibm_falcon_27"))
    # passes = pm.to_flow_controller().passes
    # for task in passes:
    #     print(task)
    # print('')
    # last = len(passes)-1
    # print(passes[last].condition)

    # hw = "ibm_falcon_27"
    # for benchmark in benchmarks:
    #     qasm = get_circuit(hw,benchmark,4,"ALG")
    #     visualize_circuit(qasm,hw)





    # FEHLENDE BENCHMARKS:

    # Mapping Only:
    # ibm_eagle_127,ALG,qft,84,Pytket,3
    # ibm_eagle_127,ALG,qaoa,100,Pytket,3
    # ibm_eagle_127,INDEP,qaoa,100,Pytket,3

    # Full Compilation:
    # ibm_eagle_127,ALG,qaoa,100,Pytket,3
