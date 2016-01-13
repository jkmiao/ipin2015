namespace py ipin.rpc.etl.jd.jd_type
namespace java com.ipin.rpc.etl.jd

include "../common/base_datatype.thrift"
include "../common_type.thrift"
include "jd_remedy.thrift"

struct JdIncRaw {
	/** 公司名称 */
	1:base_datatype.DtString incName = {},
	/** 行业 */
	2:base_datatype.DtString incIndustry = {},
	/** 公司类型 */
	3:base_datatype.DtString incType = {},
	/** 公司规模 */
	4:base_datatype.DtString incScale = {},
	/** 公司介绍 */
	5:base_datatype.DtString incIntro = {},
	/** 公司ｕｒｌ*/
	6:base_datatype.DtString incUrl = {},
}

struct JdIncMeasure {
	/** 公司片段id */
	1:base_datatype.DtString incSegmentId = {},
	/** 公司行业 */
	2:base_datatype.DtByte incIndustryId = {},
	/** 公司类型 */
	3:base_datatype.DtByte incType = {},
	/** 公司规模最小值 */
	4:base_datatype.DtInt incScaleMin = {},
	/** 公司规模最大值 */
	5:base_datatype.DtInt incScaleMax = {},
}

struct JdJobRaw {
	/** 职位名称 */
	1:base_datatype.DtString jobPosition = {},
	/** 薪水 */
	2:base_datatype.DtString jobSalary = {},
	/** 工作地区 */
	3:base_datatype.DtString jobWorkLoc = {},
	/** 学历要求 */
	4:base_datatype.DtString jobDiploma = {},
	/** 工作经验 */
	5:base_datatype.DtString jobWorkAge = {},
	/** 工作描述 */
	6:base_datatype.DtString jobDescription = {},
	/** 职能 */
	7:base_datatype.DtString jobCate = {},
	/** 工作类型 */
	8:base_datatype.DtString jobType = {},

	/** 工作福利 */
	9:base_datatype.DtString jobWelfare = {},
}

struct JdJobMeasure {
	/** 薪水最小值 */
	1:base_datatype.DtInt jobSalaryMin = {},
	/** 薪水最大值 */
	2:base_datatype.DtInt jobSalaryMax = {},
	/** 工作地区 */
	3:base_datatype.DtString jobWorkLocId = {},
	/** 学历 */
	4:base_datatype.DtByte jobDiplomaId = {},
	/** 工作经历最小值 */
	5:base_datatype.DtLong jobWorkAgeMin = {},
	/** 工作经历最大值 */
	6:base_datatype.DtLong jobWorkAgeMax = {},
	/** 职位名称 */
	8:base_datatype.DtString jobPosition = {},
	/** 工作描述 */
	9:base_datatype.DtString jobDescription = {},
	
	/** 职位职能 */
	10:base_datatype.DtString jobCate = {},
	/** 工作类型　*/
	11:base_datatype.DtString jobType = {},
	/** 工作福利　*/
	12:base_datatype.DtString jobWelfare = {},
	/**专业　*/
	13: base_datatype.DtString jobMajor = {},
}

struct JdRaw {
	1:string jdId,
	2:string jdFrom,
	3:string jdUrl,
	4:JdIncRaw jdInc = {},
	5:JdJobRaw jdJob = {},
    6:jd_remedy.JdRemedyRaw remedyInfo = {},
	8:base_datatype.DtString pubDate = {},
}

struct JdMeasure {
	1:string jdId,
	2:string jdFrom,
	3:string jdUrl,
	4:JdIncMeasure jdInc,
	5:JdJobMeasure jdJob,
    6:jd_remedy.JdRemedyMeasure remedyInfo = {},
	8:base_datatype.DtDateTime pubDate = {},
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
    52:list<string> skills,
    53:string workDemand,
    54:string workDuty,
    55:list<string> jobTags,
    100:common_type.BIND_STATUS status,
}

struct JdVector {
    1:string jdMergedId,
    2:list<double> posVector,
    3:list<double> descVector,
    4:i32 uid,
    10:common_type.BIND_STATUS status,
}
