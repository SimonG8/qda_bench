import os
import time
from typing import Optional, Tuple, Dict, Any

from pytket import OpType
from pytket.architecture import Architecture
from pytket.mapping import MappingManager, LexiLabellingMethod, LexiRouteRoutingMethod
from pytket.passes import (
    SynthesiseTket, FullPeepholeOptimise,
    DecomposeSwapsToCXs, RemoveRedundancies,
    DecomposeBoxes
)
from pytket.qasm import circuit_from_qasm, circuit_to_qasm

from quantum_bench.hardware.config import HardwareModel
from .base import CompilerAdapter


class PytketAdapter(CompilerAdapter):
    def __init__(self, hardware: HardwareModel, export_dir: str = None):
        super().__init__("Pytket", hardware, export_dir)
        self.architecture = Architecture(hardware.coupling_map)
        self.mapping_manager = MappingManager(self.architecture)

    def compile(self, qasm_file: str, opt_level: int, seed: Optional[int] = None) -> Tuple[Dict[str, Any], str]:
        try:
            circuit = circuit_from_qasm(qasm_file)
        except Exception as e:
            print(f"Pytket QASM Import Error: {e}")
            return None, None

        start_time = time.time()

        DecomposeBoxes().apply(circuit)

        if opt_level >= 1:
            SynthesiseTket().apply(circuit)
        if opt_level >= 2:
            FullPeepholeOptimise().apply(circuit)

        lookahead = 10 if opt_level < 3 else 50
        route_method = LexiRouteRoutingMethod(lookahead=lookahead)
        label_method = LexiLabellingMethod()

        self.mapping_manager.route_circuit(circuit, [label_method, route_method])

        swap_count = circuit.n_gates_of_type(OpType.SWAP)

        DecomposeSwapsToCXs(self.architecture).apply(circuit)

        if opt_level >= 2:
            RemoveRedundancies().apply(circuit)

        duration = time.time() - start_time

        metrics = {
            "gate_count": circuit.n_gates,
            "depth": circuit.depth(),
            "compile_time": duration,
            "2q_gates": circuit.n_gates_of_type(OpType.CX),
            "swap_gates": swap_count,
        }

        try:
            _, file = os.path.split(qasm_file.removesuffix(".qasm"))
            filename = os.path.join(self.export_dir, f"{file}_pytket_opt{opt_level}.qasm")
            circuit_to_qasm(circuit, filename)
        except Exception as e:
            print(f"Pytket QASM Export Error: {e}")
            return metrics, None

        return metrics, filename
