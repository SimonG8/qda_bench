import time
from typing import Optional
from pytket.qasm import circuit_from_qasm
from pytket.architecture import Architecture
from pytket.passes import (
    SynthesiseTket, FullPeepholeOptimise,
    DecomposeSwapsToCXs, RemoveRedundancies,
    DecomposeBoxes
)
from pytket.mapping import MappingManager, LexiLabellingMethod, LexiRouteRoutingMethod
from pytket import OpType
from .base import CompilerAdapter
from quantum_bench.hardware.config import HardwareModel

class PytketAdapter(CompilerAdapter):
    def __init__(self, hardware: HardwareModel):
        super().__init__("pytket", hardware)
        self.architecture = Architecture(hardware.coupling_map)
        self.mapping_manager = MappingManager(self.architecture)

    def compile(self, qasm_file: str, opt_level: int, seed: Optional[int] = None) -> dict:
        try:
            circuit = circuit_from_qasm(qasm_file)
        except Exception:
            return None

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
        
        return {
            "gate_count": circuit.n_gates,
            "depth": circuit.depth(),
            "compile_time": duration,
            "2q_gates": circuit.n_gates_of_type(OpType.CX),
            "swap_gates": swap_count,
            "mapped_circuit": circuit
        }
