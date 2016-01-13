namespace py ipin.rpc.etl.cv.cv_type
namespace java com.ipin.rpc.etl.cv

include "../common_type.thrift"

struct CvPrivateInfoRaw {
	/** cvId */
    1:string cvId,
    /** 简历渠道 */
    2:string cvFrom,
	/** cv关键词 */
    3:list<string> keywords = [],
    /** 用户名 */
    4:string userName,
    /** 手机号 */
    5:string phoneNumber,
    /** 邮箱地址 */
    6:string email,
	/** qq */
	9:string qq,
    /** 身份证 */
    10:string idNumber,
}

struct CvBaseInfoRaw {
	/** cvId */
	1:string cvId,
	/** cv更新时间 */
	2:string updateTime,
	/** 婚姻状况 */
	4:string marriage,
	/** 年龄 */
	6:string age,
	/** 出生日期 */
	7:string dob,
	/** 身高 */
	8:string height,
	/** 工作经验时间 */
	9:string nowWorkAge,
	/** 最高学历 */
	10:string nowDiploma,
	/** 当前籍贯 */
	11:string nowLocation,
	/** 当前政治属性 */
	12:string nowPolistatus,
	/** 当前联系地址 */
	13:string nowAddress,
	/** 当前所在地邮编 */
	14:string nowZipCode,
	/** 当前户口所在地 */
	15:string nowHukou,
    /** 性别 */
    25:string gender,
    /** 现在的公司 */
    26:string nowInc,
	/** 个人简介 */
	30:string intro,
	/** 当前所在行业 */
	31:string nowIndustry,
	/** 当前职位 */
	32:string nowPosition,
	/** 最高学历学校 */
	33:string recentSchName,
	/** 最高学历专业 */
	34:string recentMajorName,
	/** 是否有海外经历 */
	40:string overSea,
    /** 最近工作一份工作的时间 */
    42:string recentJobDuration,
    /** 目前薪资 */
    43:string nowSalary,
    
    50:string cvFrom,
}

struct CvJobExpRaw {
	/** cvId */
	1:string cvId,
	/** 期望工作地点 */
	2:string expLocations,
	/** 期望薪水 */
	3:string expSalary,
	/** 期望工作类型 */
	4:string expJobTypes,
	/** 期望职位 */
	5:string expPositions,
	/** 期望行业 */
	6:string expIndustrys,
    /** 勿推荐企业 */
    7:string ignoreIncs,
    /** 工作状态 */
    8:string workStatus,
    /** 到职时间 */
    9:string dutyTime,
    /** 期望职能 */
    10:string expJobCates,
}

struct CvEduItemRaw {
	/** 教育经历id*/
	1:string itemId,
	/** cvId */
	2:string cvId,
	/** 教育开始时间 */
	3:string eduStart,
	/** 教育结束时间 */
	4:string eduEnd,
	/** 学校名称 */
	5:string schName,
	/** 专业名称 */
	6:string majorName,
	/** 教育经历描述 */
	7:string eduDesc,
	/** 学历 */
	8:string eduDiploma,
}

struct CvJobItemRaw {
	/** 工作经历id */
	1:string itemId,
	/** cvId */
	2:string cvId,
	/** 公司名称 */
	3:string incName,
	/** 公司描述 */
	4:string incDesc,
	/** 公司规模 */
	5:string incEmployee,
	/** 公司所在行业 */
	6:string incIndustrys,
	/** 公司类型 */
	7:string incType,
	/** 公司所在地 */
	8:string incLocation,
	/** 工作开始时间 */
	9:string jobStart,
	/** 工作结束时间 */
	10:string jobEnd,
	/** 工作时间 */
	11:string jobDuration,
	/** 薪酬 */
	12:string jobSalary,
	/** 所在部门 */
	13:string jobDepartment,
	/** 职位 */
	14:string jobPosition,
	/** 工作描述 */
	15:string jobDesc,
}

struct CvProItemRaw {
    1:string cvId,
    2:string itemId,
    3:string proStart,
    4:string proEnd,
    5:string proName,
    6:string proDuty,
    7:string proDesc,
    8:string softwareEnv,
    9:string hardwareEnv,
    10:string devTool,
}

struct CvCertItemRaw {
    1:string cvId,
    2:string itemId,
    3:string certTime,
    4:string certName,
    5:string certLevel,
}

struct CvTrainItemRaw {
    1:string cvId,
    2:string itemId,
    3:string trainStart,
    4:string trainEnd,
    5:string trainAgency,
    6:string trainTitle,
    7:string trainContent,
    8:string trainDesc,
    9:string trainLoc,
}

struct CvLanguageItemRaw {
    1:string cvId,
    2:string itemId,
    3:string languageName,
    4:string languageLevel,
}

struct CvSkillItemRaw {
    1:string cvId,
    2:string itemId,
    3:string skillName,
    4:string skillLevel,
    5:string skillDuration,
}

struct CvRaw {
	/** cvId */
	1:string cvId,
	/** cv来源 */
	2:string cvFrom,
	/** 基本信息 */
	3:CvBaseInfoRaw baseInfo,
	/** 求职意向 */
	4:CvJobExpRaw jobExp,
	/** 教育经历 */
	5:list<CvEduItemRaw> eduList = [],
	/** 工作经历 */
	6:list<CvJobItemRaw> jobList = [],

    /** 项目经验 */
    7:list<CvProItemRaw> proList = [],
	/** 培训经历 */
    8:list<CvTrainItemRaw> trainList = [],
	/** 语言技能 */
    9:list<CvLanguageItemRaw> languageList = [],
	/** 证书 */
    10:list<CvCertItemRaw> certList = [],
    /** 技能 */
    11:list<CvSkillItemRaw> skillList = [],
    /** 隐私信息 */
    12:CvPrivateInfoRaw privateInfo,

}

//=================================== 量化部分 ===============================================
struct CvPrivateInfoMeasure {
    /** cvId */
    1:string cvId,
    /** 简历渠道 */
    2:string cvFrom,
    /** cv关键词 */
    3:list<string> keywords,
    /** 用户名 */
    4:string userName,
    /** 手机号 */
    5:string phoneNumber,
    /** 邮箱地址 */
    6:string email,
    /** msn */
    7:string msn,
    /** 博客 */
    8:string blog,
    9:string Qq,
    10:string idNumber,
}

struct CvBaseInfoMeasure {
    /** cvId */
    1:string cvId,
    /** 更新时间 */
    2:i64 updateTime,
    /** 婚姻状态 baseinfo_const.MarriageType */
    4:byte marriage,
    /** 年龄 */
    6:byte age,
    /** 生日 */
    7:i64 dob,
    /** 身高 */
    8:i16 height,
    /** 工作经验(单位ms) */
    9:i64 nowWorkAge,
    /** 学历 edu_const.DiplomaType */
    10:byte nowDiploma,
    /** 当前所在地Id */
    11:string nowLocationId,
    /** 政治面貌 baseinfo_const.PoliticsType */
    12:byte nowPolistatus,
    13:string nowPosition,
    /** 户口所在地Id */
    15:string nowHukouLocId,
    /** 性别 **/
    25:byte gender,
    /** 现在的公司 **/
    26:string nowIncId,
    /** 当前行业Id */
    31:byte nowIndustryId,
    /** 当前学校Id */
    33:string recentSchId,
    /** 当前专业Id */
    34:string recentMajorId,
    /** 是否有海外经历 */
    40:bool nowOverSea,

    42:string recentJobDuration,
    43:string nowSalary,
    44:string selfEvaluation,
    45:string intro,
    46:string nowAddress,
    50:string cvFrom,
}

struct CvJobExpMeasure {
    /** cvId */
    1:string cvId,
    /** 期望工作地点列表 */
    2:list<string> expLocationIdList = [],
    /** 期望工作类型列表 job_const.JobType */
    4:list<byte> expJobTypeList = [],
    /** 期望职位列表 */
    5:list<string> expPositionList = [],
    /** 期望行业列表 */
    6:list<byte> expIndustryIdList = [],
    /** 最低薪酬 */
    7:i32 expSalaryMin,
    /** 最高薪酬 */
    8:i32 expSalaryMax,
        /** 勿推荐企业 */
    9:string ignoreIncs,
    /** 工作状态 */
    10:byte workStatus,
    /** 到职时间 */
    11:string dutyTime,
    /** 期望职能 */
    12:string expJobCates,
}

struct CvEduItemMeasure {
    /** itemId */
    1:string itemId,
    /** cvId */
    2:string cvId,
    /** 教育开始时间 */
    3:i64 eduStart,
    /** 教育结束时间 */
    4:i64 eduEnd,
    /** 学校Id */
    5:string schId,
    /** 专业Id */
    6:string majorId,
    /** 学历 edu_const.DiplomaType*/
    8:byte eduDiploma,
    /** 是否统招 */
    9:bool tongzhao,
    /** 全日制 非全日制 */
    10:byte eduType,
    /** 描述 */
    20:string eduDesc,
}

struct CvJobItemMeasure {
    /** itemId */
    1:string itemId,
    /** cvId */
    2:string cvId,
    /** 公司片段Id */
    3:string incSegmentId,
    /** 公司规模区间最小人数 */
    4:i32 incEmployeeMin,
    /** 公司规模区间最大人数 */
    5:i32 incEmployeeMax,
    /** 公司所在行业 */
    6:list<byte> incIndustryIdList = [],
    /** 公司类型 job_const.IncType */
    7:byte incType,
    /** 公司所在地Id */
    8:string incLocationId,
    /** 工作开始时间 */
    9:i64 jobStart,
    /** 工作结束时间 */
    10:i64 jobEnd,
    /** 工作时长(单位ms) */
    11:i64 jobDuration,

    /** 工作职位 */
    12:string jobPosition,
    /** 工作描述 */
    13:string jobDesc,
    /** 公司描述 */
    14:string incDesc,
    /** 下属团队人数 */
    18:i16 jobSubTeamSize,
    /** 薪酬区间最小值 */
    30:i32 jobSalaryMin,
    /** 薪酬区间最大值 */
    31:i32 jobSalaryMax,
}

struct CvProItemMeasure {
    1:string cvId,
    2:string itemId,
    3:i64 proStart,
    4:i64 proEnd,
    5:string proName,
    6:string proDuty,
    7:string proDesc,
}

struct CvCertItemMeasure {
    1:string cvId,
    2:string itemId,
    3:i64 certTime,
    4:string certName,
    5:string certLevel,
}

struct CvTrainItemMeasure {
    1:string cvId,
    2:string itemId,
    3:i64 trainStart,
    4:i64 trainEnd,
    5:string trainAgency,
    6:string trainTitle,
    7:string trainContent,
    8:string trainDesc,
    9:string trainLoc,
}

struct CvLanguageItemMeasure {
    1:string cvId,
    2:string itemId,
    3:string languageName,
    4:string languageLevel,
}

struct CvSkillItemMeasure {
    1:string cvId,
    2:string itemId,
    3:string skillName,
    4:string skillLevel,
    5:i64 skillDuration,
}

struct CvMeasure {
    /** cvId */
    1:string cvId,
    /** 基本信息 */
    2:CvBaseInfoMeasure baseInfo,
    /** 求职意向 */
    3:CvJobExpMeasure jobExp,
    /** 教育经历 */
    4:list<CvEduItemMeasure> eduList =  [],
    /** 工作经历 */
    5:list<CvJobItemMeasure> jobList = [],
        /** 项目经验 */
    7:list<CvProItemMeasure> proList = [],
    /** 培训经历 */
    8:list<CvTrainItemMeasure> trainList = [],
    /** 语言技能 */
    9:list<CvLanguageItemMeasure> languageList = [],
    /** 证书 */
    10:list<CvCertItemMeasure> certList = [],
    /** 技能 */
    11:list<CvSkillItemMeasure> skillList = [],
    /** 隐私信息 */
    12:CvPrivateInfoMeasure privateInfo,
}

struct CvJdRelation {
    1:string accountId,
    2:i32 uid,
    3:string cvId,
    4:string jdId,
    5:string jdMergedId,
    6:string acceptTime,
    7:i64 acceptTimeStamp,
}

struct CvJdMatchInfo {
    1:string cvId,
    2:string itemId,
    3:i32 uid,
    4:common_type.BIND_STATUS cvStatus,
    5:string jdMergedId,
    6:double matchRatio,
    7:i64 createTimestamp,
}

struct JobJdMatchInfo {
    1:string itemId,
    2:string cvId,
    5:string jdMergedId,
    6:double matchRatio,
}

struct CvVector{
    1:string itemId,
    2:string cvId,
    3:list<double> posVector,
    4:list<double> descVector,
    5:double excellentRatio,
    6:i64 jobStart,
    7:i64 jobEnd,
    8:i32 uid,
    9:common_type.BIND_STATUS status,
}
