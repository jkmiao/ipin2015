namespace py ipin.rpc.etl.cv.measure
namespace java com.ipin.rpc.etl.cv

include "../common/base_datatype.thrift"
include "../common/common_error.thrift"
include "cv_type.thrift"

service CvMeasureService {
	/** 量化基本信息 */
	cv_type.CvBaseInfoMeasure measureBaseInfo(3:cv_type.CvBaseInfoRaw baseInfoRaw) throws (1:common_error.NamedError namedError);
	/** 量化工作期望 */
	cv_type.CvJobExpMeasure measureJobExp(1:cv_type.CvJobExpRaw jobExpRaw) throws (1:common_error.NamedError namedError);
	/** 量化教育经历 */
	cv_type.CvEduItemMeasure measureEduItem(1:cv_type.CvEduItemRaw eduItemRaw) throws (1:common_error.NamedError namedError);
	/** 量化工作经历 */
	cv_type.CvJobItemMeasure measureJobItem(1:cv_type.CvJobItemRaw jobItemRaw) throws (1:common_error.NamedError namedError);
	/** 量化整个cv */
	cv_type.CvMeasure measureCv(1:cv_type.CvRaw cvRaw) throws (1:common_error.NamedError namedError);
}
