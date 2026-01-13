// Generated from Cirq v1.6.1

OPENQASM 2.0;
include "qelib1.inc";


// Qubits: [q(7), q(10), q(12), q(13), q(15)]
qreg q[5];
creg m_c_0[1];
creg m_c_1[1];
creg m_c_2[1];
creg m_c_3[1];


u3(pi*1.5,0,0) q[1];
u3(pi*0.5,0,0) q[3];
u3(pi*1.5,0,0) q[4];
u3(pi*1.5,0,0) q[0];
cz q[1],q[2];
u3(pi*0.5,pi*1.0,pi*1.0) q[1];
u3(0,pi*1.0,pi*1.0) q[2];
measure q[1] -> m_c_0[0];
cz q[3],q[2];
u3(pi*0.5,pi*2.0,0) q[3];
cz q[4],q[2];
swap q[0],q[1];
measure q[3] -> m_c_1[0];
u3(pi*0.5,pi*1.0,pi*1.0) q[4];
cz q[1],q[2];
measure q[4] -> m_c_2[0];
u3(pi*0.5,pi*1.0,pi*1.0) q[1];
u3(pi*0.5,pi*1.0,0) q[2];
measure q[1] -> m_c_3[0];
