// Generated from Cirq v1.6.1

OPENQASM 2.0;
include "qelib1.inc";


// Qubits: [q(1), q(2), q(3), q(4), q(5), q(7), q(8), q(10), q(12), q(13)]
qreg q[10];
creg m_meas_9[1];
creg m_meas_8[1];
creg m_meas_7[1];
creg m_meas_6[1];
creg m_meas_5[1];
creg m_meas_4[1];
creg m_meas_3[1];
creg m_meas_2[1];
creg m_meas_0[1];
creg m_meas_1[1];


u3(pi*1.5,0,0) q[8];
u3(pi*1.5,0,0) q[9];
u3(pi*0.5,0,0) q[7];
u3(pi*0.5,0,0) q[5];
u3(pi*0.5,0,0) q[3];
u3(pi*0.5,0,0) q[0];
u3(pi*0.5,0,0) q[1];
u3(pi*0.5,0,0) q[2];
u3(pi*0.5,0,0) q[4];
u3(pi*0.5,0,0) q[6];
cz q[8],q[9];
u3(pi*0.5,0,0) q[8];
u3(0,pi*1.5,pi*0.5) q[9];
measure q[9] -> m_meas_9[0];
cz q[7],q[8];
u3(0,pi*1.5,pi*0.5) q[8];
u3(pi*0.5,pi*1.0,pi*1.0) q[7];
measure q[8] -> m_meas_8[0];
cz q[5],q[7];
u3(pi*0.5,pi*1.0,pi*1.0) q[5];
u3(0,pi*1.5,pi*0.5) q[7];
measure q[7] -> m_meas_7[0];
cz q[3],q[5];
u3(pi*0.5,pi*1.0,pi*1.0) q[3];
u3(0,pi*1.5,pi*0.5) q[5];
measure q[5] -> m_meas_6[0];
cz q[0],q[3];
u3(pi*0.5,pi*1.0,pi*1.0) q[0];
u3(0,pi*1.5,pi*0.5) q[3];
measure q[3] -> m_meas_5[0];
cz q[1],q[0];
u3(pi*0.5,pi*1.0,pi*1.0) q[1];
u3(0,pi*1.5,pi*0.5) q[0];
measure q[0] -> m_meas_4[0];
cz q[2],q[1];
u3(pi*0.5,pi*1.0,pi*1.0) q[2];
u3(0,pi*1.5,pi*0.5) q[1];
measure q[1] -> m_meas_3[0];
cz q[4],q[2];
u3(pi*0.5,pi*1.0,pi*1.0) q[4];
u3(0,pi*1.5,pi*0.5) q[2];
measure q[2] -> m_meas_2[0];
cz q[6],q[4];
u3(pi*0.5,pi*1.0,pi*1.0) q[6];
u3(0,pi*1.5,pi*0.5) q[4];
measure q[6] -> m_meas_0[0];
measure q[4] -> m_meas_1[0];
