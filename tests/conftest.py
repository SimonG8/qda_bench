import pytest
import os
from quantum_bench.hardware.config import Falcon27, Grid25

@pytest.fixture
def dummy_qasm_file(tmp_path):
    """
    Erstellt eine temporäre QASM-Datei für Tests (Bell-State).
    """
    qasm_content = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0],q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
"""
    p = tmp_path / "test.qasm"
    p.write_text(qasm_content)
    return str(p)

@pytest.fixture
def falcon_hardware():
    return Falcon27()

@pytest.fixture
def grid_hardware():
    return Grid25()
