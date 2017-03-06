autodeploy  有三个接口

首先autodeploy需要完成功能有如下几个：
1、salt-minion执行命令完毕以后回调callback_util.py的回调模块，将执行结果入库    ----  这个功能最好实现
2、通过http接口调用salt-api
3、查询任务执行结果
备注：
2、3功能前需要有一个login的装饰器来判断请求的IP是否在安全的列表中。即login函数
2、3功能的请求串信息如下：
data = {"task_id":"2017030201","paras":[{"arg":"zhulh","cmd":"os_util.useradd","cmd_parent":"os_util","ip_category_list":"102,67","ip_list":"172.19.152.19,172.19.152.21","no":"1","step_num":"1"}]}

其中：
task_id ： 为执行的任务号
paras ： 为参数字典
arg ：为函数所传的参数，多个参数使用四个"####"隔开
cmd ：自定义模块名和函数
cmd_parent ： 自定义模块名
ip_category_list ： 暂无
ip_list ： 执行的IP，多个IP通过","隔开
no ： 执行的次数
step_num ： 一个任务内的步数

----以上是老的参数：
使用新的参数：20170305
data = {"task_id":"2017030201","step_num":"1","no":"1","ip_list":"172.19.152.19,172.19.152.21","cmd":"os_util.useradd","arg":"zhulh"}



执行任务有如下情况：
1、一个任务下需要进行多步；
2、一个任务多次执行；
3、传过来的次数大于1，且之前没有执行过；
4、传过来的步数大于1，且之前的步数没有执行过；
6、传多个IP的；
7、多个IP的有失败的，有成功的；
8、多个IP全部成功的；
9、多个IP全部失败的；
10、多个IP有没有返回的；
11、同一个任务，调整IP或者步数或者执行命令；

查询任务结果的情况如下：




#这个接口是salt-minion callback_util模块使用，将执行接口返回回来
http://172.22.91.79:9000/AutoDeploy/SaveLog.do

#这个是执行任务的接口
http://172.22.91.79:9000/AutoDeploy/receiveTask.do

#这个是查询任务结果的接口
http://172.22.91.79:9000/AutoDeploy/QueryJob.do







#一个命令数据库的变化情况：
SELECT * FROM t_exec_jid_detail WHERE jid = "20170214190641711929"
id	jid	ip	result	detail	donetime
46251	20170214190641711929	172.19.152.40	true		2017-02-14 19:06:44

SELECT * FROM t_exec_log WHERE task_id = "201702131129_3"
id	task_id
6573	201702131129_3

SELECT * FROM t_exec_mapping WHERE jid = "20170214190641711929"
jid	ip_list	command	no	task_id
20170214190641711929	172.19.152.40	os_util.userdel	1	201702131129_3




[2017-02-14 19:06:41,649] ["http-bio-9000"-exec-1] [com.jd.autodeploy.util.IPLimitUtil.getIPAddressLimit(IPLimitUtil.java:38)] - 获取到的IP地址为：172.22.91.80
[2017-02-14 19:06:41,650] ["http-bio-9000"-exec-1] [com.jd.autodeploy.util.IPLimitUtil.getIPAddressLimit(IPLimitUtil.java:45)] - 访问IP[172.22.91.80]在安全IP列表[127.0.0.1,172.19.152.40,172.16.199.39,172.19.186.28,172.22.91.80]中
[2017-02-14 19:06:41,650] ["http-bio-9000"-exec-1] [com.jd.autodeploy.action.AutoDeployAction.handleRequest(AutoDeployAction.java:48)] - {"paras": [{"ip_list": "172.19.152.40", "no": "1", "cmd": "os_util.userdel", "arg": "zhulh", "ip_category_list": "102,67", "cmd_parent": "os_util"}], "mid": "201702131129_3"}
[2017-02-14 19:06:41,656] [Thread-14] [com.jd.autodeploy.service.impl.AutoDeployServiceImpl.doTask(AutoDeployServiceImpl.java:52)] - mid == 201702131129_3
[2017-02-14 19:06:41,742] [Thread-14] [com.jd.autodeploy.service.impl.AutoDeployServiceImpl.exeSaltApi(AutoDeployServiceImpl.java:338)] - 调用 Salt-API 返回信息:{"_links": {"jobs": [{"href": "/jobs/20170214190641711929"}]}, "return": [{"jid": "20170214190641711929", "minions": ["172.19.152.40"]}]}
[2017-02-14 19:06:43,506] ["http-bio-9000"-exec-2] [com.jd.autodeploy.action.SaveLog.handleRequest(SaveLog.java:40)] - 接收到的报文是{"fun_args": ["zhulh"], "jid": "20170214190641711929", "return": {"result": true, "details": ""}, "retcode": 0, "success": true, "fun": "os_util.userdel", "id": "172.19.152.40"}
[2017-02-14 19:06:43,507] ["http-bio-9000"-exec-2] [com.jd.autodeploy.action.SaveLog.handleRequest(SaveLog.java:44)] - 接收到的参数是jid[20170214190641711929]id[172.19.152.40]
[2017-02-14 19:06:44,752] [Thread-14] [com.jd.autodeploy.service.impl.AutoDeployServiceImpl.doTask(AutoDeployServiceImpl.java:165)] - 任务[201702131129_3]执行成功
[2017-02-14 19:06:44,752] [Thread-14] [com.jd.autodeploy.thread.DoTaskThread.run(DoTaskThread.java:22)] - true

[2017-02-14 19:06:46,684] ["http-bio-9000"-exec-3] [com.jd.autodeploy.action.QueryJobAction.handleRequest(QueryJobAction.java:35)] - 接收到的taskid为:201702131129_3


正常执行命令
1、首先查询请求的IP是否在安全的列表中
2、打印出请求通过json串
3、拿到mid(即任务ID)，查t_exec_mapping表查询是否有执行
4、调用salt-api来执行命令
5、打印salt-api的返回信息
6、打印salt-minion返回的信息，并输入至t_exec_jid_detail表中
7、判断命令是否执行成功
8、最后输出true or false

查询
1、打印接收到的taskid
2、将结果返回



已经执行的任务且是成功的，再次执行的日志：
[2017-02-15 22:46:29,573] ["http-bio-9000"-exec-4] [com.jd.autodeploy.util.IPLimitUtil.getIPAddressLimit(IPLimitUtil.java:38)] - 获取到的IP地址为：172.22.91.80
[2017-02-15 22:46:29,574] ["http-bio-9000"-exec-4] [com.jd.autodeploy.util.IPLimitUtil.getIPAddressLimit(IPLimitUtil.java:45)] - 访问IP[172.22.91.80]在安全IP列表[127.0.0.1,172.19.152.40,172.16.199.39,172.19.186.28,172.22.91.80]中
[2017-02-15 22:46:29,574] ["http-bio-9000"-exec-4] [com.jd.autodeploy.action.AutoDeployAction.handleRequest(AutoDeployAction.java:48)] - {"paras": [{"ip_list": "172.19.152.40", "no": "1", "cmd": "os_util.userdel", "arg": "zhulh", "ip_category_list": "102,67", "cmd_parent": "os_util"}], "mid": "201702131129_3"}
[2017-02-15 22:46:29,581] [Thread-27] [com.jd.autodeploy.service.impl.AutoDeployServiceImpl.doTask(AutoDeployServiceImpl.java:52)] - mid == 201702131129_3
[2017-02-15 22:46:29,605] [Thread-27] [com.jd.autodeploy.service.impl.AutoDeployServiceImpl.doTask(AutoDeployServiceImpl.java:124)] - 当前任务[201702131129_3]已成功执行完成，请不要重复尝试
[2017-02-15 22:46:29,605] [Thread-27] [com.jd.autodeploy.thread.DoTaskThread.run(DoTaskThread.java:22)] - true
[2017-02-15 22:46:34,638] ["http-bio-9000"-exec-5] [com.jd.autodeploy.action.QueryJobAction.handleRequest(QueryJobAction.java:35)] - 接收到的taskid为:201702131129_3

已经执行的任务且是成功的，修改了no字段，再次执行的日志：
[2017-02-15 23:00:34,463] ["http-bio-9000"-exec-6] [com.jd.autodeploy.util.IPLimitUtil.getIPAddressLimit(IPLimitUtil.java:38)] - 获取到的IP地址为：172.22.91.80
[2017-02-15 23:00:34,464] ["http-bio-9000"-exec-6] [com.jd.autodeploy.util.IPLimitUtil.getIPAddressLimit(IPLimitUtil.java:45)] - 访问IP[172.22.91.80]在安全IP列表[127.0.0.1,172.19.152.40,172.16.199.39,172.19.186.28,172.22.91.80]中
[2017-02-15 23:00:34,464] ["http-bio-9000"-exec-6] [com.jd.autodeploy.action.AutoDeployAction.handleRequest(AutoDeployAction.java:48)] - {"paras": [{"ip_list": "172.19.152.40", "no": "2", "cmd": "os_util.userdel", "arg": "zhulh", "ip_category_list": "102,67", "cmd_parent": "os_util"}], "mid": "201702131129_3"}
[2017-02-15 23:00:34,466] [Thread-28] [com.jd.autodeploy.service.impl.AutoDeployServiceImpl.doTask(AutoDeployServiceImpl.java:52)] - mid == 201702131129_3
[2017-02-15 23:00:34,487] [Thread-28] [com.jd.autodeploy.service.impl.AutoDeployServiceImpl.doTask(AutoDeployServiceImpl.java:168)] - 执行任务[201702131129_3]时异常
java.lang.NullPointerException
        at com.jd.autodeploy.service.impl.AutoDeployServiceImpl.doTask(AutoDeployServiceImpl.java:101)
        at com.jd.autodeploy.thread.DoTaskThread.run(DoTaskThread.java:22)
        at java.lang.Thread.run(Thread.java:745)
[2017-02-15 23:00:34,491] [Thread-28] [com.jd.autodeploy.thread.DoTaskThread.run(DoTaskThread.java:22)] - false
[2017-02-15 23:00:39,525] ["http-bio-9000"-exec-7] [com.jd.autodeploy.action.QueryJobAction.handleRequest(QueryJobAction.java:35)] - 接收到的taskid为:201702131129_3


#在40的机器上有例子
SELECT * FROM t_exec_mapping WHERE task_id = "201702161128_2" ORDER BY jid DESC;

通过task_id来看jid的取最新一个



判断no是否为1

[2017-02-16 21:21:13,069] ["http-bio-9000"-exec-24] [com.jd.autodeploy.action.QueryJobAction.handleRequest(QueryJobAction.java:35)] - 接收到的taskid为:201702131129_4
[2017-02-16 21:21:16,927] ["http-bio-9000"-exec-46] [com.jd.autodeploy.util.IPLimitUtil.getIPAddressLimit(IPLimitUtil.java:38)] - 获取到的IP地址为：172.22.91.80
[2017-02-16 21:21:16,927] ["http-bio-9000"-exec-46] [com.jd.autodeploy.util.IPLimitUtil.getIPAddressLimit(IPLimitUtil.java:45)] - 访问IP[172.22.91.80]在安全IP列表[127.0.0.1,172.19.152.40,172.16.199.39,172.19.186.28,172.22.91.80]中
[2017-02-16 21:21:16,927] ["http-bio-9000"-exec-46] [com.jd.autodeploy.action.AutoDeployAction.handleRequest(AutoDeployAction.java:48)] - {"paras": [{"ip_list": "172.19.152.40", "no": "2", "cmd": "os_util.userdel", "arg": "zhulh", "ip_category_list": "102,67", "cmd_parent": "os_util"}], "mid": "201702131128_1"}
[2017-02-16 21:21:16,929] [Thread-186] [com.jd.autodeploy.service.impl.AutoDeployServiceImpl.doTask(AutoDeployServiceImpl.java:52)] - mid == 201702131128_1
[2017-02-16 21:21:16,937] [Thread-186] [com.jd.autodeploy.service.impl.AutoDeployServiceImpl.doTask(AutoDeployServiceImpl.java:74)] - 当前任务[201702131128_1]执行步骤[1]时异常，请查证无误后再执行
[2017-02-16 21:21:16,937] [Thread-186] [com.jd.autodeploy.thread.DoTaskThread.run(DoTaskThread.java:22)] - false
[2017-02-16 21:21:21,947] ["http-bio-9000"-exec-66] [com.jd.autodeploy.action.QueryJobAction.handleRequest(QueryJobAction.java:35)] - 接收到的taskid为:201702131128_1
[2017-02-16 21:21:25,000] ["http-bio-9000"-exec-60] [com.jd.autodeploy.action.QueryJobAction.handleRequest(QueryJobAction.java:35)] - 接收到的taskid为:201702131128_1
[2017-02-16 21:21:28,038] ["http-bio-9000"-exec-65] [com.jd.autodeploy.action.QueryJobAction.handleRequest(QueryJobAction.java:35)] - 接收到的taskid为:201702131128_1
[2017-02-16 21:21:31,069] ["http-bio-9000"-exec-62] [com.jd.autodeploy.action.QueryJobAction.handleRequest(QueryJobAction.java:35)] - 接收到的taskid为:201702131128_1
[2017-02-16 21:21:34,099] ["http-bio-9000"-exec-34] [com.jd.autodeploy.action.QueryJobAction.handleRequest(QueryJobAction.java:35)] - 接收到的taskid为:201702131128_1
[2017-02-16 21:21:37,127] ["http-bio-9000"-exec-70] [com.jd.autodeploy.action.QueryJobAction.handleRequest(QueryJobAction.java:35)] - 接收到的taskid为:201702131128_1
[2017-02-16 21:21:40,157] ["http-bio-9000"-exec-63] [com.jd.autodeploy.action.QueryJobAction.handleRequest(QueryJobAction.java:35)] - 接收到的taskid为:201702131128_1
[2017-02-16 21:21:43,201] ["http-bio-9000"-exec-64] [com.jd.autodeploy.action.QueryJobAction.handleRequest(QueryJobAction.java:35)] - 接收到的taskid为:201702131128_1
[2017-02-16 21:21:46,232] ["http-bio-9000"-exec-24] [com.jd.autodeploy.action.QueryJobAction.handleRequest(QueryJobAction.java:35)] - 接收到的taskid为:201702131128_1
[2017-02-16 21:21:49,264] ["http-bio-9000"-exec-46] [com.jd.autodeploy.action.QueryJobAction.handleRequest(QueryJobAction.java:35)] - 接收到的taskid为:201702131128_1











[2017-02-17 20:12:57,691] ["http-bio-9000"-exec-34] [com.jd.autodeploy.util.IPLimitUtil.getIPAddressLimit(IPLimitUtil.java:38)] - 获取到的IP地址为：172.19.152.40
[2017-02-17 20:12:57,694] ["http-bio-9000"-exec-34] [com.jd.autodeploy.util.IPLimitUtil.getIPAddressLimit(IPLimitUtil.java:45)] - 访问IP[172.19.152.40]在安全IP列表[127.0.0.1,172.19.152.40,172.16.199.39,172.19.186.28,172.22.91.80]中
[2017-02-17 20:12:57,694] ["http-bio-9000"-exec-34] [com.jd.autodeploy.action.AutoDeployAction.handleRequest(AutoDeployAction.java:48)] - {"mid":"14873335173797563_1_0","paras":[{"arg":"jd_test20170217####2001","cmd":"os_util.useradd","cmd_parent":"os_util","ip_list":"172.16.167.134,172.16.167.133","no":"1"}]}
[2017-02-17 20:12:57,698] ["http-bio-9000"-exec-70] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:41)] - 开始查询任务[14873335173797563_1_0]的执行详情...
[2017-02-17 20:12:57,701] [Thread-195] [com.jd.autodeploy.service.impl.AutoDeployServiceImpl.doTask(AutoDeployServiceImpl.java:52)] - mid == 14873335173797563_1_0
[2017-02-17 20:12:57,715] ["http-bio-9000"-exec-70] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:126)] - 查询任务[14873335173797563_1_0]返回报文为:{"message":"根据任务ID[14873335173797563_1_0]未查询到任务信息","result":"no_record"}
[2017-02-17 20:12:57,805] [Thread-195] [com.jd.autodeploy.service.impl.AutoDeployServiceImpl.exeSaltApi(AutoDeployServiceImpl.java:338)] - 调用 Salt-API 返回信息:{"_links": {"jobs": [{"href": "/jobs/20170217201257774296"}]}, "return": [{"jid": "20170217201257774296", "minions": ["172.16.167.134", "172.16.167.133"]}]}
[2017-02-17 20:12:58,105] ["http-bio-9000"-exec-63] [com.jd.autodeploy.action.SaveLog.handleRequest(SaveLog.java:40)] - 接收到的报文是{"fun_args": ["jd_test20170217", "2001"], "jid": "20170217201257774296", "return": {"result": true, "details": "Group 'mail' not found. Creating the user mailbox file with 0600 mode."}, "retcode": 0, "success": true, "fun": "os_util.useradd", "id": "172.16.167.133"}
[2017-02-17 20:12:58,105] ["http-bio-9000"-exec-63] [com.jd.autodeploy.action.SaveLog.handleRequest(SaveLog.java:44)] - 接收到的参数是jid[20170217201257774296]id[172.16.167.133]
[2017-02-17 20:12:59,437] ["http-bio-9000"-exec-64] [com.jd.autodeploy.action.SaveLog.handleRequest(SaveLog.java:40)] - 接收到的报文是{"fun_args": ["jd_test20170217", "2001"], "jid": "20170217201257774296", "return": {"result": false, "details": "useradd: user 'jd_test20170217' already exists"}, "retcode": 0, "success": true, "fun": "os_util.useradd", "id": "172.16.167.134"}
[2017-02-17 20:12:59,437] ["http-bio-9000"-exec-64] [com.jd.autodeploy.action.SaveLog.handleRequest(SaveLog.java:44)] - 接收到的参数是jid[20170217201257774296]id[172.16.167.134]
[2017-02-17 20:13:27,721] ["http-bio-9000"-exec-24] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:41)] - 开始查询任务[14873335173797563_1_0]的执行详情...
[2017-02-17 20:13:27,728] ["http-bio-9000"-exec-24] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:100)] - 任务[14873335173797563_1_0]有执行失败的主机
[2017-02-17 20:13:27,729] ["http-bio-9000"-exec-24] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:126)] - 查询任务[14873335173797563_1_0]返回报文为:{"all_detail":"172.16.167.134,172.16.167.133","all_num":2,"fail_detail":"172.16.167.134:useradd: user 'jd_test20170217' already exists","fail_num":1,"message":"任务[14873335173797563_1_0]有执行失败的主机","result":"fail","running_detail":"","running_num":0,"success_detail":"172.16.167.133","success_num":1}
[2017-02-17 20:14:58,041] [Thread-195] [com.jd.autodeploy.service.impl.AutoDeployServiceImpl.doTask(AutoDeployServiceImpl.java:74)] - 当前任务[14873335173797563_1_0]执行步骤[1]时异常，请查证无误后再执行
[2017-02-17 20:14:58,043] [Thread-195] [com.jd.autodeploy.thread.DoTaskThread.run(DoTaskThread.java:22)] - false
[2017-02-17 20:15:12,115] ["http-bio-9000"-exec-46] [com.jd.autodeploy.util.IPLimitUtil.getIPAddressLimit(IPLimitUtil.java:38)] - 获取到的IP地址为：172.19.152.40
[2017-02-17 20:15:12,115] ["http-bio-9000"-exec-46] [com.jd.autodeploy.util.IPLimitUtil.getIPAddressLimit(IPLimitUtil.java:45)] - 访问IP[172.19.152.40]在安全IP列表[127.0.0.1,172.19.152.40,172.16.199.39,172.19.186.28,172.22.91.80]中
[2017-02-17 20:15:12,116] ["http-bio-9000"-exec-46] [com.jd.autodeploy.action.AutoDeployAction.handleRequest(AutoDeployAction.java:48)] - {"mid":"14873335173797563_1_0","paras":[{"arg":"jd_test20170217####2001","cmd":"os_util.useradd","cmd_parent":"os_util","ip_list":"172.16.167.134,172.16.167.133","no":"1"}]}
[2017-02-17 20:15:12,117] [Thread-196] [com.jd.autodeploy.service.impl.AutoDeployServiceImpl.doTask(AutoDeployServiceImpl.java:52)] - mid == 14873335173797563_1_0
[2017-02-17 20:15:12,117] ["http-bio-9000"-exec-66] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:41)] - 开始查询任务[14873335173797563_1_0]的执行详情...
[2017-02-17 20:15:12,126] ["http-bio-9000"-exec-66] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:100)] - 任务[14873335173797563_1_0]有执行失败的主机
[2017-02-17 20:15:12,126] ["http-bio-9000"-exec-66] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:126)] - 查询任务[14873335173797563_1_0]返回报文为:{"all_detail":"172.16.167.134,172.16.167.133","all_num":2,"fail_detail":"172.16.167.134:useradd: user 'jd_test20170217' already exists","fail_num":1,"message":"任务[14873335173797563_1_0]有执行失败的主机","result":"fail","running_detail":"","running_num":0,"success_detail":"172.16.167.133","success_num":1}
[2017-02-17 20:15:12,129] [Thread-196] [com.jd.autodeploy.service.impl.AutoDeployServiceImpl.executeTaskByStepNum(AutoDeployServiceImpl.java:297)] - 任务[14873335173797563_1_0]执行步骤[1]操作，需要执行的IP是[172.16.167.134]
[2017-02-17 20:15:12,211] [Thread-196] [com.jd.autodeploy.service.impl.AutoDeployServiceImpl.exeSaltApi(AutoDeployServiceImpl.java:338)] - 调用 Salt-API 返回信息:{"_links": {"jobs": [{"href": "/jobs/20170217201512180115"}]}, "return": [{"jid": "20170217201512180115", "minions": ["172.16.167.134"]}]}
[2017-02-17 20:15:12,474] ["http-bio-9000"-exec-60] [com.jd.autodeploy.action.SaveLog.handleRequest(SaveLog.java:40)] - 接收到的报文是{"fun_args": ["jd_test20170217", "2001"], "jid": "20170217201512180115", "return": {"result": true, "details": "Group 'mail' not found. Creating the user mailbox file with 0600 mode."}, "retcode": 0, "success": true, "fun": "os_util.useradd", "id": "172.16.167.134"}
[2017-02-17 20:15:12,474] ["http-bio-9000"-exec-60] [com.jd.autodeploy.action.SaveLog.handleRequest(SaveLog.java:44)] - 接收到的参数是jid[20170217201512180115]id[172.16.167.134]
[2017-02-17 20:15:15,218] [Thread-196] [com.jd.autodeploy.service.impl.AutoDeployServiceImpl.doTask(AutoDeployServiceImpl.java:165)] - 任务[14873335173797563_1_0]执行成功
[2017-02-17 20:15:15,218] [Thread-196] [com.jd.autodeploy.thread.DoTaskThread.run(DoTaskThread.java:22)] - true



重复执行：
[2017-02-17 21:49:09,110] ["http-bio-9000"-exec-34] [com.jd.autodeploy.util.IPLimitUtil.getIPAddressLimit(IPLimitUtil.java:38)] - 获取到的IP地址为：172.19.152.40
[2017-02-17 21:49:09,110] ["http-bio-9000"-exec-34] [com.jd.autodeploy.util.IPLimitUtil.getIPAddressLimit(IPLimitUtil.java:45)] - 访问IP[172.19.152.40]在安全IP列表[127.0.0.1,172.19.152.40,172.16.199.39,172.19.186.28,172.22.91.80]中
[2017-02-17 21:49:09,110] ["http-bio-9000"-exec-34] [com.jd.autodeploy.action.AutoDeployAction.handleRequest(AutoDeployAction.java:48)] - {"mid":"14873335173797563_1_1","paras":[{"arg":"jd_test20170217####2001","cmd":"os_util.useradd","cmd_parent":"os_util","ip_list":"172.16.167.134,172.16.167.133","no":"1"}]}
[2017-02-17 21:49:09,111] [Thread-213] [com.jd.autodeploy.service.impl.AutoDeployServiceImpl.doTask(AutoDeployServiceImpl.java:52)] - mid == 14873335173797563_1_1
[2017-02-17 21:49:09,113] ["http-bio-9000"-exec-70] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:41)] - 开始查询任务[14873335173797563_1_1]的执行详情...
[2017-02-17 21:49:09,119] ["http-bio-9000"-exec-70] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:126)] - 查询任务[14873335173797563_1_1]返回报文为:{"message":"根据任务ID[14873335173797563_1_1]未查询到任务信息","result":"no_record"}
[2017-02-17 21:49:09,201] [Thread-213] [com.jd.autodeploy.service.impl.AutoDeployServiceImpl.exeSaltApi(AutoDeployServiceImpl.java:338)] - 调用 Salt-API 返回信息:{"_links": {"jobs": [{"href": "/jobs/20170217214909170192"}]}, "return": [{"jid": "20170217214909170192", "minions": ["172.16.167.134", "172.16.167.133"]}]}
[2017-02-17 21:49:09,314] ["http-bio-9000"-exec-63] [com.jd.autodeploy.action.SaveLog.handleRequest(SaveLog.java:40)] - 接收到的报文是{"fun_args": ["jd_test20170217", "2001"], "jid": "20170217214909170192", "return": {"result": false, "details": "useradd: user 'jd_test20170217' already exists"}, "retcode": 0, "success": true, "fun": "os_util.useradd", "id": "172.16.167.133"}
[2017-02-17 21:49:09,314] ["http-bio-9000"-exec-63] [com.jd.autodeploy.action.SaveLog.handleRequest(SaveLog.java:44)] - 接收到的参数是jid[20170217214909170192]id[172.16.167.133]
[2017-02-17 21:49:09,317] ["http-bio-9000"-exec-64] [com.jd.autodeploy.action.SaveLog.handleRequest(SaveLog.java:40)] - 接收到的报文是{"fun_args": ["jd_test20170217", "2001"], "jid": "20170217214909170192", "return": {"result": false, "details": "useradd: user 'jd_test20170217' already exists"}, "retcode": 0, "success": true, "fun": "os_util.useradd", "id": "172.16.167.134"}
[2017-02-17 21:49:09,317] ["http-bio-9000"-exec-64] [com.jd.autodeploy.action.SaveLog.handleRequest(SaveLog.java:44)] - 接收到的参数是jid[20170217214909170192]id[172.16.167.134]
[2017-02-17 21:49:39,122] ["http-bio-9000"-exec-24] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:41)] - 开始查询任务[14873335173797563_1_1]的执行详情...
[2017-02-17 21:49:39,129] ["http-bio-9000"-exec-24] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:100)] - 任务[14873335173797563_1_1]有执行失败的主机
[2017-02-17 21:49:39,130] ["http-bio-9000"-exec-24] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:126)] - 查询任务[14873335173797563_1_1]返回报文为:{"all_detail":"172.16.167.134,172.16.167.133","all_num":2,"fail_detail":"172.16.167.133:useradd: user 'jd_test20170217' already existsJD_ERROR172.16.167.134:useradd: user 'jd_test20170217' already exists","fail_num":2,"message":"任务[14873335173797563_1_1]有执行失败的主机","result":"fail","running_detail":"","running_num":0,"success_detail":"","success_num":0}
[2017-02-17 21:51:09,427] [Thread-213] [com.jd.autodeploy.service.impl.AutoDeployServiceImpl.doTask(AutoDeployServiceImpl.java:74)] - 当前任务[14873335173797563_1_1]执行步骤[1]时异常，请查证无误后再执行
[2017-02-17 21:51:09,429] [Thread-213] [com.jd.autodeploy.thread.DoTaskThread.run(DoTaskThread.java:22)] - false



14873335173797563_1_0
task_id总1是模板中的序号，0是执行的次数，14873335173797563是task_id最初的id


[2017-02-17 10:31:54,997] ["http-bio-9000"-exec-6] [com.jd.autodeploy.util.IPLimitUtil.getIPAddressLimit(IPLimitUtil.java:34)] - 获取到的IP地址为：172.22.91.79
[2017-02-17 10:31:54,998] ["http-bio-9000"-exec-6] [com.jd.autodeploy.util.IPLimitUtil.getIPAddressLimit(IPLimitUtil.java:41)] - 访问IP[172.22.91.79]在安全IP列表[127.0.0.1,172.22.91.79,172.19.186.28]中
[2017-02-17 10:31:54,998] ["http-bio-9000"-exec-6] [com.jd.autodeploy.action.AutoDeployAction.handleRequest(AutoDeployAction.java:48)] - {"mid":"198562_1_0","paras":[{"cmd":"software_util.getfile","cmd_parent":"software_util","filelist":[{"gitpath":"/bdp_client2.0_huidu/software/servers/bdp_tools/mergefiles-1.7.jar","path":"mergefiles-1.7.jar"}],"filename":"mergefiles-1.7.jar","ip_list":"172.16.170.36,172.16.170.41,172.22.156.111,172.22.81.14,172.22.81.15,172.22.81.16,172.22.81.17,172.22.81.18,172.22.81.19,172.22.90.129,172.22.91.11,172.22.91.12,172.22.96.100,172.22.96.101,172.22.96.102,172.22.96.103","no":"1","weburl":"http://172.17.55.82/wuxiaochun3/201702/16/1487238303970/mergefiles-1.7.jar?Expires=1487324705&AccessKey=PBhRGY9ohSc0mxls&Signature=2p9XyIfkYjybzoGlhkSkawic3es%3D"}]}
[2017-02-17 10:31:54,999] [Thread-7] [com.jd.autodeploy.service.impl.AutoDeployServiceImpl.doTask(AutoDeployServiceImpl.java:59)] - mid == 198562_1_0
[2017-02-17 10:31:55,001] ["http-bio-9000"-exec-7] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:41)] - 开始查询任务[198562_1_0]的执行详情...
[2017-02-17 10:31:55,011] ["http-bio-9000"-exec-7] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:126)] - 查询任务[198562_1_0]返回报文为:{"message":"根据任务ID[198562_1_0]未查询到任务信息","result":"no_record"}
[2017-02-17 10:31:55,156] [Thread-7] [com.jd.autodeploy.service.impl.AutoDeployServiceImpl.exeSaltApi(AutoDeployServiceImpl.java:345)] - 调用 Salt-API 返回信息:{"_links": {"jobs": [{"href": "/jobs/20170217103155128316"}]}, "return": [{"jid": "20170217103155128316", "minions": []}]}
[2017-02-17 10:32:25,014] ["http-bio-9000"-exec-8] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:41)] - 开始查询任务[198562_1_0]的执行详情...
[2017-02-17 10:32:25,016] ["http-bio-9000"-exec-8] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:126)] - 查询任务[198562_1_0]返回报文为:{"message":"根据任务ID[198562_1_0]未查询到任务信息","result":"no_record"}
[2017-02-17 10:32:55,019] ["http-bio-9000"-exec-9] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:41)] - 开始查询任务[198562_1_0]的执行详情...
[2017-02-17 10:32:55,021] ["http-bio-9000"-exec-9] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:126)] - 查询任务[198562_1_0]返回报文为:{"message":"根据任务ID[198562_1_0]未查询到任务信息","result":"no_record"}
[2017-02-17 10:33:25,023] ["http-bio-9000"-exec-10] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:41)] - 开始查询任务[198562_1_0]的执行详情...
[2017-02-17 10:33:25,025] ["http-bio-9000"-exec-10] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:126)] - 查询任务[198562_1_0]返回报文为:{"message":"根据任务ID[198562_1_0]未查询到任务信息","result":"no_record"}
[2017-02-17 10:33:27,456] ["http-bio-9000"-exec-1] [com.jd.autodeploy.action.SaveLog.handleRequest(SaveLog.java:40)] - 接收到的报文是{"fun_args": ["bdp_client2.0_huidu"], "jid": "20170217103155128316", "return": {"result": true, "details": "Already up-to-date."}, "retcode": 0, "success": true, "fun": "git.pull", "id": "172.22.91.79"}
[2017-02-17 10:33:27,456] ["http-bio-9000"-exec-1] [com.jd.autodeploy.action.SaveLog.handleRequest(SaveLog.java:44)] - 接收到的参数是jid[20170217103155128316]id[172.22.91.79]
[2017-02-17 10:33:28,239] [Thread-7] [com.jd.autodeploy.util.HttpClientUtil.doPostRequest(HttpClientUtil.java:93)] - http post url[http://172.22.91.79:9002/webapi/downfile/] param[{"filelist":[{"salt_path":"/bdp_client2.0_huidu/software/servers/bdp_tools/mergefiles-1.7.jar"}]}]
[2017-02-17 10:33:28,290] [Thread-7] [org.apache.commons.httpclient.HttpMethodBase.getResponseBody(HttpMethodBase.java:682)] - Going to buffer response body of large or unknown size. Using getResponseBodyAsStream instead is recommended.
[2017-02-17 10:33:28,291] [Thread-7] [com.jd.autodeploy.util.HttpClientUtil.doPostRequest(HttpClientUtil.java:111)] - {"filelist": [{"result": "true", "target_path": "/software/servers/bdp_tools/", "update_time": "20170217", "service": "bdp_client2.0_huidu", "salt_path": "/bdp_client2.0_huidu/software/servers/bdp_tools/mergefiles-1.7.jar", "install_path": "/software/", "auth": "755", "cluster_name": "bdp_client2.0_huidu", "user": "bdp_client", "user_group": "bdp_client", "service_info_id": 117, "id": 3347, "md5": "12"}]}
[2017-02-17 10:33:28,345] [Thread-7] [com.jd.autodeploy.service.impl.AutoDeployServiceImpl.exeSaltApi(AutoDeployServiceImpl.java:345)] - 调用 Salt-API 返回信息:{"_links": {"jobs": [{"href": "/jobs/20170217103328317032"}]}, "return": [{"jid": "20170217103328317032", "minions": []}]}
[2017-02-17 10:33:55,028] ["http-bio-9000"-exec-2] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:41)] - 开始查询任务[198562_1_0]的执行详情...
[2017-02-17 10:33:55,031] ["http-bio-9000"-exec-2] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:84)] - 任务[198562_1_0]还有未返回的主机...开始处理未返回主机IP
[2017-02-17 10:33:55,031] ["http-bio-9000"-exec-2] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:104)] - 任务[198562_1_0]还有未返回执行信息的主机,暂时没有返回执行失败的主机
[2017-02-17 10:33:55,033] ["http-bio-9000"-exec-2] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:126)] - 查询任务[198562_1_0]返回报文为:{"all_detail":"172.16.170.36,172.16.170.41,172.22.156.111,172.22.81.14,172.22.81.15,172.22.81.16,172.22.81.17,172.22.81.18,172.22.81.19,172.22.90.129,172.22.91.11,172.22.91.12,172.22.96.100,172.22.96.101,172.22.96.102,172.22.96.103","all_num":16,"fail_detail":"","fail_num":0,"message":"任务[198562_1_0]还有未返回执行信息的主机,暂时没有返回执行失败的主机","result":"running","running_detail":"172.16.170.36,172.16.170.41,172.22.156.111,172.22.81.14,172.22.81.15,172.22.81.16,172.22.81.17,172.22.81.18,172.22.81.19,172.22.90.129,172.22.91.11,172.22.91.12,172.22.96.100,172.22.96.101,172.22.96.102,172.22.96.103","running_num":16,"success_detail":"","success_num":0}
[2017-02-17 10:34:25,107] ["http-bio-9000"-exec-3] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:41)] - 开始查询任务[198562_1_0]的执行详情...
[2017-02-17 10:34:25,110] ["http-bio-9000"-exec-3] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:84)] - 任务[198562_1_0]还有未返回的主机...开始处理未返回主机IP
[2017-02-17 10:34:25,110] ["http-bio-9000"-exec-3] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:104)] - 任务[198562_1_0]还有未返回执行信息的主机,暂时没有返回执行失败的主机
[2017-02-17 10:34:25,111] ["http-bio-9000"-exec-3] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:126)] - 查询任务[198562_1_0]返回报文为:{"all_detail":"172.16.170.36,172.16.170.41,172.22.156.111,172.22.81.14,172.22.81.15,172.22.81.16,172.22.81.17,172.22.81.18,172.22.81.19,172.22.90.129,172.22.91.11,172.22.91.12,172.22.96.100,172.22.96.101,172.22.96.102,172.22.96.103","all_num":16,"fail_detail":"","fail_num":0,"message":"任务[198562_1_0]还有未返回执行信息的主机,暂时没有返回执行失败的主机","result":"running","running_detail":"172.16.170.36,172.16.170.41,172.22.156.111,172.22.81.14,172.22.81.15,172.22.81.16,172.22.81.17,172.22.81.18,172.22.81.19,172.22.90.129,172.22.91.11,172.22.91.12,172.22.96.100,172.22.96.101,172.22.96.102,172.22.96.103","running_num":16,"success_detail":"","success_num":0}
[2017-02-17 10:34:55,178] ["http-bio-9000"-exec-4] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:41)] - 开始查询任务[198562_1_0]的执行详情...
[2017-02-17 10:34:55,181] ["http-bio-9000"-exec-4] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:84)] - 任务[198562_1_0]还有未返回的主机...开始处理未返回主机IP
[2017-02-17 10:34:55,181] ["http-bio-9000"-exec-4] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:104)] - 任务[198562_1_0]还有未返回执行信息的主机,暂时没有返回执行失败的主机
[2017-02-17 10:34:55,181] ["http-bio-9000"-exec-4] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:126)] - 查询任务[198562_1_0]返回报文为:{"all_detail":"172.16.170.36,172.16.170.41,172.22.156.111,172.22.81.14,172.22.81.15,172.22.81.16,172.22.81.17,172.22.81.18,172.22.81.19,172.22.90.129,172.22.91.11,172.22.91.12,172.22.96.100,172.22.96.101,172.22.96.102,172.22.96.103","all_num":16,"fail_detail":"","fail_num":0,"message":"任务[198562_1_0]还有未返回执行信息的主机,暂时没有返回执行失败的主机","result":"running","running_detail":"172.16.170.36,172.16.170.41,172.22.156.111,172.22.81.14,172.22.81.15,172.22.81.16,172.22.81.17,172.22.81.18,172.22.81.19,172.22.90.129,172.22.91.11,172.22.91.12,172.22.96.100,172.22.96.101,172.22.96.102,172.22.96.103","running_num":16,"success_detail":"","success_num":0}
[2017-02-17 10:35:25,260] ["http-bio-9000"-exec-5] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:41)] - 开始查询任务[198562_1_0]的执行详情...
[2017-02-17 10:35:25,263] ["http-bio-9000"-exec-5] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:84)] - 任务[198562_1_0]还有未返回的主机...开始处理未返回主机IP
[2017-02-17 10:35:25,263] ["http-bio-9000"-exec-5] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:104)] - 任务[198562_1_0]还有未返回执行信息的主机,暂时没有返回执行失败的主机
[2017-02-17 10:35:25,263] ["http-bio-9000"-exec-5] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:126)] - 查询任务[198562_1_0]返回报文为:{"all_detail":"172.16.170.36,172.16.170.41,172.22.156.111,172.22.81.14,172.22.81.15,172.22.81.16,172.22.81.17,172.22.81.18,172.22.81.19,172.22.90.129,172.22.91.11,172.22.91.12,172.22.96.100,172.22.96.101,172.22.96.102,172.22.96.103","all_num":16,"fail_detail":"","fail_num":0,"message":"任务[198562_1_0]还有未返回执行信息的主机,暂时没有返回执行失败的主机","result":"running","running_detail":"172.16.170.36,172.16.170.41,172.22.156.111,172.22.81.14,172.22.81.15,172.22.81.16,172.22.81.17,172.22.81.18,172.22.81.19,172.22.90.129,172.22.91.11,172.22.91.12,172.22.96.100,172.22.96.101,172.22.96.102,172.22.96.103","running_num":16,"success_detail":"","success_num":0}
[2017-02-17 10:35:28,462] [Thread-7] [com.jd.autodeploy.service.impl.AutoDeployServiceImpl.doTask(AutoDeployServiceImpl.java:117)] - 当前任务[198562_1_0]执行步骤[1]时异常，请查证无误后再执行
[2017-02-17 10:35:28,463] [Thread-7] [com.jd.autodeploy.thread.DoTaskThread.run(DoTaskThread.java:22)] - false
[2017-02-17 10:35:55,343] ["http-bio-9000"-exec-6] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:41)] - 开始查询任务[198562_1_0]的执行详情...
[2017-02-17 10:35:55,346] ["http-bio-9000"-exec-6] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:84)] - 任务[198562_1_0]还有未返回的主机...开始处理未返回主机IP
[2017-02-17 10:35:55,346] ["http-bio-9000"-exec-6] [com.jd.autodeploy.action.QueryTaskDetailAction.handleRequest(QueryTaskDetailAction.java:104)] - 任务[198562_1_0]还有未返回执行信息的主机,暂时没有返回执行失败的主机




等待5秒检查返回结果
{"mid":"201702161129_3","paras":[{"arg":"zhulh","cmd":"os_util.useradd","cmd_parent":"os_util","ip_category_list":"102,67","ip_list":"172.19.152.40,172.16.167.106","no":"2"}]}
第 1 次 检测任务状态...
获取任务信息成功...
{u'failed_Result': u"172.19.152.40:useradd: user 'zhulh' already exists", u'iplist': u'172.19.152.40,172.16.167.106', u'success_Result': u'172.16.167.106', u'no': u'1'}
开始解析...
总计需要 1 步,目前已经进行到第 1 步...
第 1 步 共有 2 台机器需要执行,目前成功的为 1 台,失败的为 1,没有返回的为 0 台
检测到任务失败,准备退出任务程序...
以下为错误明细：
	 172.19.152.40:useradd: user 'zhulh' already exists






