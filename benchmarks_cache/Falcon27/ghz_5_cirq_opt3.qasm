// Generated from Cirq v1.6.1

OPENQASM 2.0;
include "qelib1.inc";


// Qubits: [q(4), q(7), q(10), q(12), q(13)]
qreg q[5];
creg m_meas_4[1];
creg m_meas_3[1];
creg m_meas_2[1];
creg m_meas_0[1];
creg m_meas_1[1];


u3(pi*1.5,0,0) q[3];
u3(pi*1.5,0,0) q[4];
u3(pi*0.5,0,0) q[2];
u3(pi*0.5,0,0) q[1];
u3(pi*0.5,0,0) q[0];
cz q[3],q[4];
u3(pi*0.5,0,0) q[3];
u3(0,pi*1.5,pi*0.5) q[4];
measure q[4] -> m_meas_4[0];
cz q[2],q[3];
u3(pi*0.5,pi*1.0,pi*1.0) q[2];
u3(0,pi*1.5,pi*0.5) q[3];
measure q[3] -> m_meas_3[0];
cz q[1],q[2];
u3(pi*0.5,pi*1.0,pi*1.0) q[1];
u3(0,pi*1.5,pi*0.5) q[2];
measure q[2] -> m_meas_2[0];
cz q[0],q[1];
u3(pi*0.5,pi*1.0,pi*1.0) q[0];
u3(0,pi*1.5,pi*0.5) q[1];
measure q[0] -> m_meas_0[0];
measure q[1] -> m_meas_1[0];
