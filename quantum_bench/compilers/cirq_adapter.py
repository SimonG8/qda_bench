import time
import cirq
import networkx as nx
from cirq.contrib.qasm_import import circuit_from_qasm
from .base import CompilerAdapter
from ..config import HardwareConfig

class FalconDevice(cirq.Device):
    """
    Benutzerdefinierte Cirq-Device Klasse für Falcon 27.
    """
    def __init__(self):
        # Convert int graph to LineQubit graph
        int_graph = HardwareConfig.get_nx_graph()
        # Relabel nodes from int to LineQubit
        self.graph = nx.relabel_nodes(int_graph, lambda x: cirq.LineQubit(x))
        self.qubits = list(self.graph.nodes)
        self._metadata = cirq.DeviceMetadata(self.qubits, nx_graph=self.graph)

    @property
    def metadata(self):
        return self._metadata

    def validate_operation(self, operation):
        if not super().validate_operation(operation):
            return False
        # Prüfen auf Konnektivität für 2-Qubit Gatter
        if len(operation.qubits) == 2:
            u, v = operation.qubits
            # Da wir nun LineQubits im Graphen haben, können wir direkt prüfen
            if not self.graph.has_edge(u, v):
                raise ValueError(f"Qubits {u} und {v} nicht verbunden.")

class CirqAdapter(CompilerAdapter):
    def __init__(self):
        super().__init__("Cirq")
        self.device = FalconDevice()
        self.device_graph = self.device.metadata.nx_graph

    def compile(self, qasm_file: str, opt_level: int) -> dict:
        # Einlesen des QASM Strings
        with open(qasm_file, 'r') as f:
            qasm_str = f.read()
        
        # Entfernen von "barrier" Befehlen
        qasm_str = "\n".join([line for line in qasm_str.splitlines() if not line.strip().startswith("barrier")])

        try:
            circuit = circuit_from_qasm(qasm_str)
        except Exception as e:
            print(f"Cirq QASM Import Error: {e}")
            return None

        # WICHTIG: Mapping der importierten Qubits (NamedQubit) auf LineQubits des Devices
        # Wir sortieren die Qubits numerisch, um eine deterministische Zuordnung zu haben
        def qubit_index(q):
            s = str(q)
            try:
                # Extrahiere Index aus "q[10]" oder "q_10" oder "10"
                if '[' in s:
                    return int(s.split('[')[1].split(']')[0])
                if '_' in s:
                    return int(s.split('_')[-1])
                return int(s)
            except ValueError:
                # Fallback: Hash des Strings, um zumindest eine deterministische Sortierung zu haben
                return hash(s)

        sorted_qubits = sorted(circuit.all_qubits(), key=qubit_index)
        qubit_map = {q: cirq.LineQubit(i) for i, q in enumerate(sorted_qubits)}
        circuit = circuit.transform_qubits(qubit_map)

        start_time = time.time()
        
        # 1. Dekomposition in Target Gateset
        circuit = cirq.optimize_for_target_gateset(
            circuit, gateset=cirq.CZTargetGateset()
        )
        
        # 2. Routing 
        lookahead = 4
        if opt_level >= 2: lookahead = 8
        if opt_level >= 3: lookahead = 15
            
        # RouteCQC erwartet einen Graphen mit Qubit-Objekten (hier LineQubit)
        router = cirq.RouteCQC(self.device_graph)
        try:
            routed_circuit = router(circuit, lookahead_radius=lookahead)
        except ValueError as e:
            print(f"Cirq Routing failed: {e}")
            return None

        # 3. Optimierung (Post-Routing)
        if opt_level >= 1:
            routed_circuit = cirq.drop_negligible_operations(routed_circuit)
        if opt_level >= 2:
            routed_circuit = cirq.eject_z(routed_circuit)
        if opt_level >= 3:
            routed_circuit = cirq.align_left(routed_circuit)

        duration = time.time() - start_time
        
        # Metriken
        gate_count = len(list(routed_circuit.all_operations()))
        depth = len(routed_circuit) 

        two_q_count = sum(1 for op in routed_circuit.all_operations() if len(op.qubits) == 2)
        
        # SWAP Gatter zählen
        swap_count = 0
        for op in routed_circuit.all_operations():
            if isinstance(op.gate, cirq.SwapPowGate) and op.gate.exponent == 1.0:
                swap_count += 1

        return {
            "gate_count": gate_count,
            "depth": depth,
            "compile_time": duration,
            "2q_gates": two_q_count,
            "swap_gates": swap_count,
            "mapped_circuit": routed_circuit
        }
