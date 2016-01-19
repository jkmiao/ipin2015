## 一、 JD解析 
1. 作用：对输入的半结构化ＪＤ文本解析解析为结构化的文本。
2. 原理：使用句子分类器＋规则＋相关词库匹配生成。
3. *演示地址: http://192.168.1.91:8086/jdparser*
4. 输入与输出
    - 输入：jd文本
    - 输出：`<string,string>` 的字典
        + 字典key有19个,大部分为字符串如 **公司名、职位名等不存在输出为“”，具体请看http://192.168.1.91:8086/jdparser）**
        + 年龄:一个元组（minage,maxage）,无要求（0,100）
        + 经验:一个元组(minyear,maxyear),无要求(0,100)
        + 证书:一个数组【证书１，证书２，。。。】
        + 薪酬:一个元组(minpay,maxpay),如底薪2500，则结果为(2500,0)(因为一般没有最高上限),或者 (u"面议",0)
        + 专业:具体专业字符串或者“专业不限”
        + 学历:学历字符串,有“以上”等关键字出现时，结果为列表
        + 技能: 列表，默认６个技能关键词
        + 其他: 大部分为字符串或列表，具体可直接看源码jd_parser.py

5. 具体抽取字段和准确率（200份JD下）
    - inc_name ( 公司名称 ) : 0.77
    - inc_tag ( 有关公司的行业性质、员工规模等公司概述信息标签 ) : 0.79
    - pub_time ( 发布时间 ) : 0.92
    - end_time ( 截止时间 ) : 0.98
    - job_name ( 职业名称 ) : 0.77
    - job_tag ( 有关招聘多少人等、需具备的经验等工作概述信息标签 ) : 0.79
    - sex ( 性别要求 ) :0.97
    - age ( 年龄要求 ) : 0.97
    - major ( 专业要求 ) :0.90
    - degree ( 学历要求 ) :0.93
    - exp ( 经验年限要求 ) :0.95
    - skill ( 技能要求 ) : 0.57(这个比较难以定义，后面输出改变，测试集未来得及标注好，所以较低)
    - workplace ( 工作地点 ) : 0.91
    - pay ( 薪酬待遇 ) : 0.95
    - cert ( 证书要求(如:英语四六级等级证书) ) : 0.96
    - demand ( 工作要求 ) : 0.89
    - duty ( 工作内容 ) : 0.83
    - benefits ( 福利制度 ) : 0.88
    - other ( 其它未处理的句子(如公司简介) ) :0.1（这个也比较杂乱，难以定义，具体看在线演示就明白）

6. 代码: 所有代码文件在91号机子`/data/weihong/auto_gen_jd` 下
    - thrift客户端调用文件: `auto_gen_jd/api_jd_parser/Client_jd.py`

    ```python
    def getClient(addr='192.168.1.91',port=9096):  
        transport = TSocket.TSocket(addr,port)  
        transport = TTransport.TBufferedTransport(transport)  
        protocol = TBinaryProtocol.TBinaryProtocol(transport)  
        client = jdService.Client(protocol)  
        return transport,client  

    if __name__=="__main__":  
        try:  
            transport,client = getClient()  
            transport.open()  
            jdstr = open('../data/jd_text.txt').read()   
            result = client.parser(jdstr)  
            print result  
            transport.close()  
        except Thrift.TException,e:  
            print '%s'%(e.message)
    ```
    - http调用接口

    ```python
    url = 'http://192.168.1.91:8086/string'  
    res = requests.post(url,data={"source":jdstr})  
    result = json.loads(res.content)
    ```

7. 实例：

>输入：

> 15k-25k 深圳 经验5-10年 大专及以上 全职
> 职位诱惑 : 大平台 新技术
> 发布时间：09:48发布
> 职位描述
> 
> 岗位要求：
> 
> 1、6年以上J2EE web架构设计开发经验，4年SOA化话经验。  
> 2、精通 struts，EJB，SSH，Ibatis等J2EE开发技术。   
> 3、有大型企业工作流平台的实施经验，能够主导工作流平台的设计及实施工作；   
> 4、沟通良好，工作态度好，主动性强   
> 5、有供应链领域经验   
> 6、有分布式部署、不停机部署经验  

>输出：
> inc_name ( 公司名称 ) :
>  
> inc_tag ( 有关公司的行业性质、员工规模等公司概述信息标签 ) :
>  
> pub_time ( 发布时间 ) :
>  2015-12-07  09:48
> end_time ( 截止时间 ) :
>  
> job_name ( 职业名称 ) :
>  架构设计
> job_tag ( 有关招聘多少人等、需具备的经验等工作概述信息标签 ) :
>  全职 
>  经验5-10年
> sex ( 性别要求 ) :
>  0
> age ( 年龄要求 ) :
>  (0, 100)
> major ( 专业要求 ) :
>  专业不限
> degree ( 学历要求 ) :
>  大专 / 本科 / 硕士 / 博士 / 博士后
> exp ( 经验年限要求 ) :
>  (5, 10)
> skill ( 技能要求 ) :
>  开发技术 / 架构设计
> workplace ( 工作地点 ) :
>  深圳
> pay ( 薪酬待遇 ) :
>  (15000, 25000)
> cert ( 证书要求(如:英语四六级等级证书) ) :
>  
> demand ( 工作要求 ) :
> 1、6年以上J2EE web架构设计开发经验，4年SOA化话经验。
> 2、精通 struts，EJB，SSH，Ibatis等J2EE开发技术。
> 3、有大型企业工作流平台的实施经验，能够主导工作流平台的设计及实施工作；
> 4、沟通良好，工作态度好，主动性强
> 5、有供应链领域经验
> 6、有分布式部署、不停机部署经验 
> duty ( 工作内容 ) :
>  
> benefits ( 福利制度 ) :
>  
> other ( 其它未处理的句子(如公司简介) ) :
>  15k-25k 深圳 经验5-10年 大专及以上 全职
> 职位诱惑 : 大平台 新技术
>   
---

## 二、自动生成JD
1. 作用：输入职位名称，自动生成相关职位要求和职责
2. 原理：先根据各个职位抓取比较重要的职位要求句子，作为某个职位的数据库。用户输入职位名和句子数时，在数据库中先用simhash寻找最接近用户输入职位名的文件名作为职位名，通过snowNLP库，读取文件生成摘要返回作为JD。

3. 运行
    - **演示地址：**http://192.168.1.91:8086/genjd

>input

> $:python mypreprocess.py python工程师 4　6


>output

> job name:  python工程师  
> 工作职责:  
> 
> 1. 负责桌面控制集成程序开发
> 2. 负责更改完善后台数据存储结构，不断支持app端的新功能上线
> 3. 解决封账号、封IP采集难点攻克
> 4. 完成领导交办的其他任务  
> 
> 岗位要求:  
> 
> 1. 可接受长期实习或者应届毕业生
> 2. 能阅读英文文档，熟悉翻墙原理
> 3. 熟悉Mysql数据库和SQL语句
> 4. 掌握版本管理工具的使用方法，如git
> 5. mongodb一年以上开发经验，掌握mongodb的基本操作
> 6. 至少一种熟悉关系数据库的和一种非关系数据库，熟悉SQL语句，熟悉缓存技术  

>> by-　miaoweihong@ipin.com
