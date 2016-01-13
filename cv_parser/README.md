## 一、 针对html文本的CV解析 
1. 作用：对输入的半结构化cv文本解析解析为结构化的文本。  
2. 原理：html解析器，纯规则＋相关词库匹配生成。  
3. *演示地址: http://192.168.1.91:8087/cvparser*  
4. 输入与输出  
    - 输入：2个参数  
    --1. HtmlContent : 58tongcheng,51job和智联的招聘html文本转换为unicode后的内容  
    --2. cvFrom : 58tongcheng,51job,zhilian 中的一个  

    [cv_type 字段的 具体定义](http://192.168.1.22/rpc_idl/etl_thrift_idl/blob/simple/cv/cv_type.thrift)

    -- 输出thrift　定义类型, cvRaw  
    ```python
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
    ```

5. 具体抽取字段和准确率（有待测试）  

6. 代码: 所有代码文件在91号机子 */home/weihong/cv_parser/* 下   
    - [thrift客户端调用文件thrift_client_cv.py](./cv_parser/thrift_client_cv.py)   
    - [thrift服务器端调用文件thrift_server_cv.py](./cv_parser/thrift_server_cv.py)  
    
    ```python
    
	 def getClient(addr='192.168.1.91',port=9097):
	    transport = TSocket.TSocket(addr,port)
	    transport = TTransport.TBufferedTransport(transport)
	    protocol = TBinaryProtocol.TBinaryProtocol(transport)
	    client = cvService.Client(protocol)
	    return transport,client


	if __name__=="__main__":
	    try:
            transport,client = getClient()
            transport.open()
            fname = './cv_parser/data/cv_58/10.html'
            cv_html = codecs.open(fname,'rb','utf-8').read()
            print 'parsing...'
            
            result = client.parseHtml(htmlContent=cv_html,cvFrom=58tongcheng)
            
            transport.close()
        except Thrift.TException,e:
            print '%s'%(e.message)

    ```   


7. 本地使用  

    - http调用接口
    
    ```python

    # 输入url地址,htmlContent(utf-8格式)文本内容及cvFrom两个参数即可。
    #  
    url = 'http://192.168.1.91:8087/string'  
    content = codecs.open("./cv_parser/data/cv_zhilian/JM002219486R90250000000.html","rb","utf-8").read()
    res = requests.post(url,data={"htmlContent":content,"cvFrom":"zhilian")}
    result = res.content
    
    ```


    - 下载源码后安装使用   　  

    *sudo python setup.py install*  

    ```python
    
    from cv_parser.api_cv_parser import CvParser
    test  = CvParser()
    test.parser(htmlContent="input your HtmlContent herer",fname=None,url=None,cvFrom="51job")

    ```

    - 同上，引用 * api_cv_parser.py * 文件即可  



8. 实例：  

http://192.168.1.91:8087/cvparser  


  

*****


>> by-　miaoweihong@ipin.com  

>> time- @2016-01
