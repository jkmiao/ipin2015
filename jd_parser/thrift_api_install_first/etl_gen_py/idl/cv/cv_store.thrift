namespace py ipin.rpc.etl.cv.store
namespace java com.ipin.rpc.etl.cv

include "../common/base_datatype.thrift"
include "../common/common_error.thrift"
include "cv_type.thrift"

service CvStoreService {
	/** 设置简历Raw */
	void setCvRaw(1:cv_type.CvRaw cvRaw) throws (1:common_error.NamedError namedError);
	/** 获取简历Raw */
	cv_type.CvRaw getCvRaw(1:string cvId) throws (1:common_error.NamedError namedError);
	
	void setCvMeasure(1:cv_type.CvMeasure cvMeasure) throws (1:common_error.NamedError namedError);
	/** 获取量化简历 */
	cv_type.CvMeasure getCvMeasure(1:string cvId) throws (1:common_error.NamedError namedError);
	list<cv_type.CvMeasure> listCvMeasure(1:list<string> cvIdList) throws (1:common_error.NamedError namedError);

    /** 根据ItemId 获取所有量化信息 */
     cv_type.CvMeasure getCvMeasureByItemId(1:string itemId) throws (1:common_error.NamedError namedError);
    /** 根据ItemIdList 获取所有量化信息 */
     list<cv_type.CvMeasure> listCvMeasureByItemId(1:list<string> itemIdList) throws (1:common_error.NamedError namedError);

    /** 根据ItemId 获取所有工作量化信息 */
     list<cv_type.CvJobItemMeasure> getCvJobMeasureByItemId(1:string itemId) throws (1:common_error.NamedError namedError);
    /** 根据ItemIdList 获取所有工作量化信息 */
     map<string, list<cv_type.CvJobItemMeasure>> listCvJobMeasureByItemId(1:list<string> itemIdList) throws (1:common_error.NamedError namedError);

}
