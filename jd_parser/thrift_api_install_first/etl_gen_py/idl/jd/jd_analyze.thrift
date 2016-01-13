namespace py ipin.rpc.etl.jd.analyze
namespace java com.ipin.rpc.etl.jd

include "../common/common_error.thrift"
include "jd_type.thrift"

service JdAnalyzeService {
    /**
    * JD 语义解析
    *
    */
    jd_type.JdRaw analyzeHtml(1:string htmlContent, 2:string jdFrom) throws (1:common_error.NamedError namedError, 2:common_error.IllegalArgumentException ex2);
}
