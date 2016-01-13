#!/bin/bash

rm -rf src/ipin*
./tool/gen_py.py --common_pkg ipin.rpc.etl idl/ext_info.thrift idl/common_type.thrift
./tool/gen_py.py --common_pkg ipin.rpc.etl.cv idl/cv/cv_type.thrift  idl/cv/cv_simple_parse.thrift idl/cv/cv_measure.thrift idl/cv/cv_store.thrift
./tool/gen_py.py --common_pkg ipin.rpc.etl.jd idl/jd/jd_type.thrift idl/jd/jd_measure.thrift idl/jd/jd_query.thrift idl/jd/jd_simple_parse.thrift idl/jd/jd_store.thrift idl/jd/jd_analyze.thrift

