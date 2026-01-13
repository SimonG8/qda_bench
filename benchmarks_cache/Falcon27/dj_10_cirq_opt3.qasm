// Generated from Cirq v1.6.1

OPENQASM 2.0;
include "qelib1.inc";


// Qubits: [q(4), q(6), q(7), q(10), q(11), q(12), q(13), q(14), q(15), q(18)]
qreg q[10];
creg m_c_0[1];
creg m_c_1[1];
creg m_c_2[1];
creg m_c_3[1];
creg m_c_4[1];
creg m_c_5[1];
creg m_c_6[1];
creg m_c_7[1];
creg m_c_8[1];


u3(pi*1.5,0,0) q[3];
u3(pi*0.5,0,0) q[6];
u3(pi*1.5,0,0) q[8];
u3(pi*1.5,0,0) q[2];
u3(pi*0.5,0,0) q[7];
u3(pi*0.5,0,0) q[9];
u3(pi*0.5,0,0) q[0];
u3(pi*1.5,0,0) q[1];
u3(pi*0.5,0,0) q[4];
cz q[3],q[5];
u3(pi*0.5,pi*1.0,pi*1.0) q[3];
u3(0,pi*1.0,pi*1.0) q[5];
measure q[3] -> m_c_0[0];
cz q[6],q[5];
u3(pi*0.5,pi*2.0,0) q[6];
cz q[8],q[5];
swap q[2],q[3];
measure q[6] -> m_c_1[0];
u3(pi*0.5,pi*1.0,pi*1.0) q[8];
cz q[3],q[5];
measure q[8] -> m_c_2[0];
u3(pi*0.5,pi*1.0,pi*1.0) q[3];
swap q[7],q[6];
measure q[3] -> m_c_3[0];
cz q[6],q[5];
swap q[9],q[8];
swap q[4],q[7];
u3(pi*0.5,pi*2.0,0) q[6];
cz q[8],q[5];
measure q[6] -> m_c_4[0];
u3(pi*0.5,pi*2.0,0) q[8];
swap q[5],q[3];
measure q[8] -> m_c_5[0];
swap q[3],q[2];
swap q[7],q[6];
cz q[0],q[2];
swap q[6],q[5];
u3(pi*0.5,pi*2.0,0) q[0];
cz q[1],q[2];
swap q[5],q[3];
measure q[0] -> m_c_6[0];
u3(pi*0.5,pi*1.0,pi*1.0) q[1];
cz q[3],q[2];
measure q[1] -> m_c_7[0];
u3(pi*0.5,pi*2.0,0) q[3];
u3(pi*0.5,pi*1.0,0) q[2];
measure q[3] -> m_c_8[0];
