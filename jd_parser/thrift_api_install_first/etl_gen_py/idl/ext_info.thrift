namespace py ipin.rpc.etl.ext_info
namespace java com.ipin.rpc.etl.ext_info
namespace go ext_info

include "common/base_datatype.thrift"
include "common/common_error.thrift"
include "cv/cv_type.thrift"
include "jd/jd_type.thrift"
include "common_type.thrift"

service ExtInfoService{

   /**处理CV附加信息**/
    void processCvExtra(1:cv_type.CvMeasure cvMeasure, 2:i32 uid) throws (1:common_error.NamedError namedError);
   /**处理JD附加信息**/
    void processJdExtra(1:jd_type.JdMeasure jdMeasure, 2:i32 uid) throws (1:common_error.NamedError namedError);
    void processJdExtraById(1:string jdId, 2:i32 uid) throws (1:common_error.NamedError namedError);

   /**设置CvVector数据 */
    list<cv_type.CvVector> genCvVector(1:cv_type.CvMeasure cvMeasure, 2:i32 uid) throws (1:common_error.NamedError namedError);
   /**设置JdVector数据**/
    jd_type.JdVector genJdVector(1:jd_type.JdMergedInfo info, 2:i32 uid) throws (1:common_error.NamedError namedError);

    /* 设置CV与JD匹配信息 */
    void genCvJdMatchInfo(1:i32 uid)throws (1:common_error.NamedError namedError);
    /** 通过Jd找Cv */
    list<cv_type.CvJdMatchInfo> listCvJdMatchInfoByJdId(1:string jdId)throws (1:common_error.NamedError namedError);
    /** 通过帐号ID找所有匹配信息**/
    list<cv_type.CvJdMatchInfo> listCvJdMatchInfoByUid(1:string uid)throws (1:common_error.NamedError namedError);

    /** 设置合并信息 */
    // jd_type.JdMergedInfo mergeJd(1:jd_type.JdMeasure jdMeasure, 2:i32 uid) throws(1:common_error.NamedError namedError);
    /** 获取JD合并后信息 */
    jd_type.JdMergedInfo getJdMergedInfo(1:string jdMergedId) throws(1:common_error.NamedError namedError);
    /** 根据uid获取JD合并后信息 */
    list<jd_type.JdMergedInfo> listJdMergedInfoByUid(1:i32 uid) throws(1:common_error.NamedError namedError);
    /** 隐藏合并后的JD */
    void hideJdAndCvByAccountId(1:string accountId) throws(1:common_error.NamedError namedError);

    /**设置ＪＤ状态 */
    void setJdStatus(1:common_type.JdStatus jdStatus) throws  (1:common_error.NamedError namedError);
   /** 设置统计信息 **/
    void setStatistics(1:common_type.Statistics s) throws (1:common_error.NamedError namedError);
    /** 获取统记总记录数 **/
    i32 getStatisticsCount(1:list<string> owners, 2:common_type.StreamStatus status) throws (1:common_error.NamedError namedError);
    /** 更新统计表 */
    void updateStatistics(1:string accountId, 2:string recordId, 3:common_type.StreamStatus status) throws (1:common_error.NamedError namedError);
   /** 更新Ｊｄ状态 */
   void updateJdStreamStatus(1:string type, 2:string indexUrl, 3:i64 status) throws (1:common_error.NamedError namedError);

}
