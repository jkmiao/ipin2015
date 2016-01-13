namespace py ipin.rpc.etl.cv.simple_parse
namespace java com.ipin.rpc.etl.cv

include "../common/base_datatype.thrift"
include "../common/common_error.thrift"
include "cv_type.thrift"

service CvSimpleParseService {
	cv_type.CvRaw parseHtml(2:string htmlContent) throws (1:common_error.NamedError namedError, 2:common_error.IllegalArgumentException ex2);
}
