import time
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
from ..config import HardwareConfig

class PytketAdapter(CompilerAdapter):
    def __init__(self):
        super().__init__("pytket")
        # Pytket Architecture erwartet Liste von Tupeln
        self.architecture = Architecture(HardwareConfig.FALCON_27_EDGES)
        self.mapping_manager = MappingManager(self.architecture)

    def compile(self, qasm_file: str, opt_level: int) -> dict:
        # Import
        try:
            circuit = circuit_from_qasm(qasm_file)
        except Exception:
            return None

        start_time = time.time()
        
        # WICHTIG: Custom Gates (wie sie durch QASM Import entstehen können) müssen zerlegt werden
        DecomposeBoxes().apply(circuit)

        # Phase 1: Vor-Optimierung (Hardware-unabhängig)
        if opt_level >= 1:
            SynthesiseTket().apply(circuit)
        if opt_level >= 2:
            FullPeepholeOptimise().apply(circuit)

        # Phase 2: Mapping und Routing 
        # LexiRoute ist ein starker Algorithmus für Routing
        lookahead = 10 if opt_level < 3 else 50
        route_method = LexiRouteRoutingMethod(lookahead=lookahead)
        label_method = LexiLabellingMethod()
        
        # Mapping durchführen
        self.mapping_manager.route_circuit(circuit, [label_method, route_method])
        
        # Phase 3: Post-Optimierung und Rebase
        # Wir müssen SWAPs in native CX zerlegen
        DecomposeSwapsToCXs(self.architecture).apply(circuit)
        
        # Optional: Weitere Redundanzen entfernen nach dem Routing
        if opt_level >= 2:
            RemoveRedundancies().apply(circuit)

        duration = time.time() - start_time
        
        return {
            "gate_count": circuit.n_gates,
            "depth": circuit.depth(),
            "compile_time": duration,
            "2q_gates": circuit.n_gates_of_type(OpType.CX)
        }
