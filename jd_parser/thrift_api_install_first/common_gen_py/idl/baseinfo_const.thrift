namespace java com.ipin.rpc.common
namespace py ipin.rpc.common.types.baseinfo_const


enum MarriageType {
	/** 单身 */
	MARRIAGE_SINGLE = 1,
	/** 已婚 */
	MARRIAGE_MARRIED = 2,
	/** 离异 */
	MARRIAGE_DIVORCED = 3,
	/** 保密 */
	MARRIAGE_SECRECY = 4,
}

enum GenderType {
	GENDER_FEMALE = 0,
	GENDER_MALE = 1,
}

enum PoliticsType {
	/** 群众 */
	POLI_QUNZHONG = 1,
	/** 无党派人士 */
	POLI_WUDANGPAI = 2,
	/** 团员 */
	POLI_TUANYUAN = 3,
	/** 党员 */
	POLI_DANGYUAN = 4,
	/** 民主党派 */
	POLI_MINZHUPAI = 5,
}
