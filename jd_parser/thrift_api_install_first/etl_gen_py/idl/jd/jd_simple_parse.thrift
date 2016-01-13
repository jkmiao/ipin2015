namespace py ipin.rpc.etl.jd.simple_parse
namespace java com.ipin.rpc.etl.jd

include "../common/common_error.thrift"
include "jd_type.thrift"

service JdParseService {
	/**
     * 解析jd详细页
     */
	jd_type.JdRaw parseHtml(2:string htmlContent) throws (1:common_error.NamedError namedError, 2:common_error.IllegalArgumentException ex2);

}
