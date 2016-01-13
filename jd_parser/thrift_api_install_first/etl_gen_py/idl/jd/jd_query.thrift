namespace py ipin.rpc.etl.jd.query
namespace java com.ipin.rpc.etl.jd

include "../common/common_error.thrift"

struct JdForQuery {
	1:string jdId,
	2:list<double> jdPositionVec,
	//3:string jdPositionLsh
	301:list<string> jdPositionLshList,
	4:list<double> jdDescVec,
	//5:string jdDescLsh
	501:list<string> jdDescLshList,
	6:i64 pubDate,
	10:i32 salary,
	11:string workLocId,
    12:double incRank,
	13:i16 workAge,
	14:i16 indId,
	15:string jobCate,
}

enum JD_QUERY_ORDER_BY {
	BY_JD_SALARY = 1,
	BY_INC_SALARY_RANK = 2,
	BY_INC_RANK = 3,
	BY_RELATE = 4,
}

enum JD_QUERY_ORDER {
	ORDER_ASC = 1,
	ORDER_DESC = 2,
}

struct JdQueryFilter {
	10:bool filterBySalary,
	11:i32 minSalary,
	12:i32 maxSalary,
	
	20:bool filterBySalaryRank,
	21:double minSalaryRank,
	22:double maxSalaryRank,

	30:bool filterByIncRank,
	31:double minIncRank,
	32:double maxIncRank,

	40:bool filterByWorkLocId,
	41:string workLocId,
	
	50:bool filterByIndId,
	51:i16 indId

	60:bool filterByWorkAge,
	61:i16 minWorkAge,
	62:i16 maxWorkAge,

	70:bool filterByPubDate,
	71:i64 minPubDate,

	80:bool filterByJobCate,
	81:string jobCate,
}

struct JdQueryRequest {
	1:list<double> jdPositionVec,
	2:list<string> jdPositionLshList,
	3:double jdPositionWeight,

	5:list<double> jdDescVec,
	6:list<string> jdDescLshList,
	7:double jdDescWeight,

	10:i32 maxCount,
	11:double minSim,
	12:JdQueryFilter filter,
	13:JD_QUERY_ORDER_BY orderBy,
	14:JD_QUERY_ORDER order,
	
	//15:string jobCate,
	16:i16 lshSkipBit,
	17:i16 lshGroupCount=100,
}

struct JdQueryResultItem {
	1:string jdId,
	2:double relate,
}

struct JdQueryResult {
	1:list<JdQueryResultItem> resultList,
	/* 根据position lsh 产生的备选列表  */
	2:i32 jdPositionLshSelCount,
	/* 根据desc lsh 产生的备选列表 */
	3:i32 jdDescLshSelCount,
}


service JdQueryService {
	/**
     *更新数据
     */
	void setJdForQuery(1:string versionName,10:JdForQuery jdForQuery,11:bool skipPersistence,12:string contentSign) throws (1:common_error.NamedError namedError);
	/**
	 *获取内容签名
	 */
	string getJdForQuerySign(1:string versionName,10:string jdId) throws (1:common_error.NamedError namedError);
	/**
	 * 查询
	 */
	list<JdQueryResultItem> query(1:string versionName,10:JdQueryRequest query) throws (1:common_error.NamedError namedError);

	/**
	 * 查询 返回更多信息
	 */
	JdQueryResult queryWithDetail(1:string versionName,10:JdQueryRequest query) throws (1:common_error.NamedError namedError);

	/**
	 * 删除JdForQuery记录
	 */
	void deleteJdForQuery(1:string versionName,10:string jdId) throws (1:common_error.NamedError namedError);
}
