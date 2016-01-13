#!/bin/bash

rm -rf src/ipin*
./tool/gen_py.py --common_pkg ipin.rpc.common idl/base_datatype.thrift  idl/common_error.thrift  idl/jd_source.thrift  idl/vector_type.thrift idl/baseinfo_const.thrift idl/edu_const.thrift idl/job_const.thrift
