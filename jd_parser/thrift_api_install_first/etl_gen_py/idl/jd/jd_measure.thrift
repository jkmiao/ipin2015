namespace py ipin.rpc.etl.jd.measure
namespace java com.ipin.rpc.etl.jd

include "../common/common_error.thrift"
include "jd_type.thrift"

service JdMeasureService {
	jd_type.JdMeasure measureJd(1:jd_type.JdRaw jdRaw) throws (1:common_error.NamedError namedError); 
}
