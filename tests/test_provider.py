import os
import pytest
from quantum_bench.data.mqt_provider import BenchmarkProvider

def test_provider_download(tmp_path):
    # Wir nutzen tmp_path als Cache-Dir, damit wir nichts zumüllen
    provider = BenchmarkProvider(export_dir=str(tmp_path))
    
    # Kleiner Schaltkreis (GHZ 2 Qubits)
    qasm_path = provider.get_circuit("ghz", 2)
    
    assert qasm_path is not None
    assert os.path.exists(qasm_path)
    assert qasm_path.endswith(".qasm")
    
    # Inhalt prüfen
    with open(qasm_path, 'r') as f:
        content = f.read()
        assert "OPENQASM" in content
        assert "qreg" in content

def test_provider_invalid_algo(tmp_path):
    provider = BenchmarkProvider(export_dir=str(tmp_path))
    # Ungültiger Algo-Name
    res = provider.get_circuit("nicht_existent", 2)
    assert res is None
