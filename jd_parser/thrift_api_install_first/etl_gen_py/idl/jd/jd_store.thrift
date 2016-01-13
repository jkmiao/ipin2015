namespace py ipin.rpc.etl.jd.store
namespace java com.ipin.rpc.etl.jd

include "jd_type.thrift"
include "../common/common_error.thrift"


service JdStoreService {
	/**
	* 查询jdId
	*/
	string queryJdId(1:string indexUrl,4:string contentSign) throws (1:common_error.NamedError namedError);
	/**
	* 获取jdRaw
	*/
	jd_type.JdRaw getJdRaw(1:string jdId) throws (1:common_error.NamedError namedError); 
	/**
	* 更新jdRaw
	*/
	void setJdRaw(1:jd_type.JdRaw jdRaw) throws (1:common_error.NamedError namedError);
      	/**
	* 更新jdRaw 批量
	*/
	void setJdRawBulk(1:list<jd_type.JdRaw> jdRaws) throws (1:common_error.NamedError namedError);
    
	/**
	* 获取jdMeasure
	*/
	jd_type.JdMeasure getJdMeasure(1:string jdId) throws (1:common_error.NamedError namedError);
	/**
	* 更新jdMeasure
	*/
	void setJdMeasure(1:jd_type.JdMeasure jdMeasure) throws (1:common_error.NamedError namedError);
	void setJdMeasureBulk(1:list<jd_type.JdMeasure> jdMeasures) throws (1:common_error.NamedError namedError);
	
    string getJdIdByIndexUrl(1:string indexUrl) throws(1:common_error.NamedError namedError);
}
