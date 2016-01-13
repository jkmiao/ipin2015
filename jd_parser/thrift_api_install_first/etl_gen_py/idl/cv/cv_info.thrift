namespace py ipin.rpc.cv.info
namespace java com.ipin.rpc.cv

include "../common/base_datatype.thrift"
include "../common/common_error.thrift"
include "cv_type.thrift"

struct CvScore {
    1:string cvId,
    2:double score,
}

service CvInfoService{
   
   /**设置CvScore数据**/
    void setCvScore(3:CvScore cvScore) throws (1:common_error.NamedError namedError);
    
   /**获取CvScore数据**/
   CvScore getCvScore(3:string cv_id) throws (1:common_error.NamedError namedError);
   
   /**批量获取CvScore数据**/
   list<CvScore> getCvScores(3:list<string> cv_ids) throws (1:common_error.NamedError namedError);
    
}
