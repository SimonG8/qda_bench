import pytest
from quantum_bench.compilers.qiskit_adapter import QiskitAdapter
from quantum_bench.compilers.cirq_adapter import CirqAdapter
from quantum_bench.compilers.pytket_adapter import PytketAdapter

# Parametrisierung: Führe Tests für alle Compiler und Hardware-Typen aus
@pytest.mark.parametrize("AdapterClass", [QiskitAdapter, CirqAdapter, PytketAdapter])
@pytest.mark.parametrize("hardware_fixture", ["falcon_hardware", "grid_hardware"])
def test_compile_basic(AdapterClass, hardware_fixture, request, dummy_qasm_file):
    # Fixture dynamisch laden
    hardware = request.getfixturevalue(hardware_fixture)
    
    adapter = AdapterClass(hardware)
    
    # Teste Opt-Level 0
    metrics = adapter.compile(dummy_qasm_file, opt_level=0, seed=42)
    
    assert metrics is not None
    assert "gate_count" in metrics
    assert "depth" in metrics
    assert "compile_time" in metrics
    assert "2q_gates" in metrics
    assert "swap_gates" in metrics
    assert "mapped_circuit" in metrics
    
    assert metrics["gate_count"] > 0
    assert metrics["compile_time"] >= 0

@pytest.mark.parametrize("AdapterClass", [QiskitAdapter, CirqAdapter, PytketAdapter])
def test_compile_opt_levels(AdapterClass, falcon_hardware, dummy_qasm_file):
    adapter = AdapterClass(falcon_hardware)
    
    # Teste, ob Level 3 läuft (könnte länger dauern, aber bei 2 Qubits schnell)
    metrics_l3 = adapter.compile(dummy_qasm_file, opt_level=3, seed=42)
    assert metrics_l3 is not None

def test_qiskit_seed_reproducibility(falcon_hardware, dummy_qasm_file):
    """Prüft, ob Qiskit mit festem Seed deterministisch ist."""
    adapter = QiskitAdapter(falcon_hardware)
    
    # Zwei Läufe mit gleichem Seed
    m1 = adapter.compile(dummy_qasm_file, opt_level=3, seed=12345)
    m2 = adapter.compile(dummy_qasm_file, opt_level=3, seed=12345)
    
    # Sollten identisch sein (Tiefe und Gate Count)
    assert m1["gate_count"] == m2["gate_count"]
    assert m1["depth"] == m2["depth"]
    # 2q gates sollten auch gleich sein
    assert m1["2q_gates"] == m2["2q_gates"]
