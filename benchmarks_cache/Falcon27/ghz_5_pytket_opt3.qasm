OPENQASM 2.0;
include "qelib1.inc";

qreg node[6];
creg meas[5];
u3(0.5*pi,0.0*pi,1.0*pi) node[0];
cx node[0],node[1];
cx node[1],node[2];
cx node[2],node[3];
cx node[3],node[5];
barrier node[5],node[3],node[2],node[1],node[0];
measure node[5] -> meas[0];
measure node[3] -> meas[1];
measure node[2] -> meas[2];
measure node[1] -> meas[3];
measure node[0] -> meas[4];
