## 一、 JD解析 

1. 作用：对输入的半结构化ＪＤ文本解析解析为结构化的文本。  
2. 原理：使用句子分类器＋规则＋相关词库匹配生成。  
3. *演示地址: http://192.168.1.91:8088/jdparser*  
4. 输入与输出  
    - 输入：2个参数  
    --1. htmlContent : lagou,liepin,51job和智联的招聘html转换为unicode编码后的内容  
    --2. jdFrom : lagou,51job,zhilian,liepin 中的一个  

    [jd_type 字段的 具体定义](http://192.168.1.22/rpc_gen/etl_gen_py/blob/simple/idl/jd/jd_type.thrift)

    -- 输出thrift　定义类型, jdRaw  
    ```python
    struct JdRaw {
        1:string jdId,
        2:string jdFrom,
        3:string jdUrl,
        4:JdIncRaw jdInc,
        5:JdJobRaw jdJob,
        6:string pubTime,
        7:string endTime,
    }
    ```

5. 具体抽取字段和准确率（有待测试）  

6. 代码: 所有代码文件在91号机子 */home/weihong/jd_parser/* 下  
    - thrift 调用接口   
    --1. [thrift服务器端调用文件 thrift_server_jd.py](thrift_server_jd.py)    
    --2. [thrift客户端调用文件 thrift_client_jd.py](thrift_client_jd.py)  
    - http调用接口:   


    ```python
    url = "http://192.168.1.91:8088/string"
    input_url = "http://www.lagou.com/jobs/1270757.html"

    htmlContent = codecs.open("./jd_parser/test_jds/lagou/lagou_100.html").read()
    jdFrom = "lagou" #修改
    res = requests.post(url,data={"htmlContent":htmlContent,"jdFrom":jdFrom})
    result = json.loads(res.content)
    ```  



## 二. 接口部署本地安装及使用   


1. 下载源码到本地 git clone 
2. cd ./thrift_api_install_first/common_gen_py/  `sudo python setup.py install`
3. cd ./thrift_api_install_first/etl_gen_py/    ` sudo python setup.py install`
4. 安装api_jd_parser接口 python setup.py install --user
5. 使用: 
    
    ```python
    from jd_parser_html.api_jd_parser import JdParser
    test = jdparser()
    htmlContent = codecs.open("./jd_parser/test_jds/lagou/lagou_100.html").read()
    result = test.parser(htmlContent=htmlContent,jdFrom="lagou")
    print result
    
    ```


## 三. 演示demo： 


http://192.168.1.91:8088/jdparser  

---

>> by-　miaoweihong@ipin.com
>> @2016.01
