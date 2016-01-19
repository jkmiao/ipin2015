## 一、自动生成JD
1. 作用：输入职位名称，自动生成相关职位要求和职责
2. 原理：先根据各个职位抓取比较重要的职位要求句子，作为某个职位的数据库。用户输入职位名和句子数时，在数据库中先用simhash寻找最接近用户输入职位名的文件名作为职位名，通过snowNLP库，pageRank等算法
读取文件生成摘要返回作为JD。

3. 运行
    - **演示地址：**http://192.168.1.91:8086/genjd

>input

> $:python mypreprocess.py python工程师 4　6  3


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

> 技能要求：
> 1. python
> 2. 算法编程
> 3. mysql

![image]("https://github.com/jkmiao/ipin2015/blob/master/auto_gen_jd/auto_genjd.png")

>> by-　miaoweihong@ipin.com
