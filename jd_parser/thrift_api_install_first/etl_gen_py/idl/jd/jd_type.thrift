namespace py ipin.rpc.etl.jd.jd_type
namespace java com.ipin.rpc.etl.jd

include "../common_type.thrift"

struct JdIncRaw {
	/** 公司名称 */
	1:string incName,
	/** 行业 */
	2:string incIndustry,
	/** 公司类型 */
	3:string incType,
	/** 公司规模 */
	4:string incScale,
	/** 公司介绍 */
	5:string incIntro,
	/** 公司ｕｒｌ*/
	6:string incUrl,
    /** 公司地址 */
    7:string incLocation,
}

struct JdJobRaw {
	/** 职位名称 */
	1:string jobPosition,
	/** 薪水 */
	2:string jobSalaryMin,
	/** 薪水 */
    3: string jobSalaryMax,
	/** 工作地区 */
	4:string jobWorkLoc,
	/** 学历要求 */
	5:string jobDiploma,
	/** 工作描述 */
	7:string jobDescription,
	/** 职能 */
	8:string jobCate,
	/** 工作类型 */
	9:string jobType,

	/** 工作福利 */
	10:string jobWelfare,
    /** 性别要求 */
    11:string gender,
    /** 年龄要求  */
    12:string minAge,
    /** 年龄要求  */
    13: string maxAge,
    /** 证书要求(如:英语四六级等级证书) */
    14:list<string> certList,
    /** 专业要求*/
    15: list<string> jobMajorList,
    /** 技能要求*/
    16: list<string> skillList,
    /** 工作要求 */
    17: string workDemand,
    /** 工作职责 */
    18: string workDuty,
	/** 工作经验 */
	20:string jobWorkAgeMin,
	/** 工作经验 */
	21:string jobWorkAgeMax,
    /** 其他信息*/
    100: string other,
}

struct JdRaw {
	1:string jdId,
	2:string jdFrom,
	3:string jdUrl,
	4:JdIncRaw jdInc,
	5:JdJobRaw jdJob,
	8:string pubTime,
    9:string endTime,
}
struct JdIncMeasure {
	/** 公司片段id */
	1:string incSegmentId,
	/** 公司行业 */
	2:byte incIndustryId,
	/** 公司类型 */
	3:byte incType,
	/** 公司规模最小值 */
	4:i32 incScaleMin,
	/** 公司规模最大值 */
	5:i32 incScaleMax,
}

struct JdJobMeasure {
	/** 薪水最小值 */
	1:i32 jobSalaryMin,
	/** 薪水最大值 */
	2:i32 jobSalaryMax,
	/** 工作地区 */
	3:string jobWorkLocId,
	/** 学历 */
	4:byte jobDiplomaId,
	/** 工作经历最小值 */
	5:i64 jobWorkAgeMin,
	/** 工作经历最大值 */
	6:i64 jobWorkAgeMax,
	/** 职位名称 */
	8:string jobPosition,
	/** 工作描述 */
	9:string jobDescription,
	
	/** 职位职能 */
	10:string jobCate,
	/** 工作类型　*/
	11:string jobType,
	/** 工作福利　*/
	12:string jobWelfare,
	/**专业　*/
	13: list<string> jobMajorList,
}


struct JdMeasure {
	1:string jdId,
	2:string jdFrom,
	3:string jdUrl,
	4:JdIncMeasure jdInc,
	5:JdJobMeasure jdJob,
	8:i64 pubDate,
}

struct JdMergedInfo {
    1:string jdMergedId,
    2:i32 uid,
    3:i64 pubDateStamp,
    4:list<string> rawJdList,
    5:string incSegmentId
    6:byte incIndustryId,
    7:byte incType,
    8:i32 incScaleMin,
    9:i32 incScaleMax,
    10:i32 jobSalaryMin,
    11:i32 jobSalaryMax,
    12:string jobWorkLocId,
    13:byte jobDiplomaId,
    14:i64 jobWorkAgeMin,
    15:i64 jobWorkAgeMax,
    16:string jobPosition,
    17:string jobDescription,
    18:string jobCate,
    19:string jobType,

    50:string jobWelfare,
    51:string jobMajor,
    52:list<string> skillList,
    53:string workDemand,
    54:string workDuty,
    55:list<string> jobTagList,
    100:common_type.BIND_STATUS status,
}

struct JdVector {
    1:string jdMergedId,
    2:list<double> posVector,
    3:list<double> descVector,
    4:i32 uid,
    10:common_type.BIND_STATUS status,
}
