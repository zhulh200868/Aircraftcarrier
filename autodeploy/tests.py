#!/usr/bin/env python
# -*- coding=utf8 -*-


from django.test import TestCase

# Create your tests here.

import time
import json
import urllib2
import urllib
import sys
import random
import string
import re
from threading import Thread

cmd= \
'''
{
    "paras": [
        {
            "cmd": "%s",
            "arg": "%s",
            "ip_list": "%s",
            "no": "1"
        }
    ],
    "mid": "%d"
}
'''

cmd_noarg= \
'''
{
    "paras": [
        {
            "cmd": "%s",
            "arg": "",
            "ip_list": "%s",
            "no": "1"
        }
    ],
    "mid": "%d"
}
'''

##调用
def command(data,url):
    data=json.dumps(data)
    data=json.loads(data)
    try:
        request = urllib2.Request(
            url     = url+'/autodeploy/ReceiveTask/',
            # headers = headers,
            data    =  json.JSONEncoder().encode(data)
            )
        res = urllib2.urlopen(request)
    except Exception, e:
        print "调用接口失败:"+str(e)
        sys.exit(255)
    else:
        print "调用接口成功..."
        return res.read()
    finally:
        pass


##检查结果
def checkResult(data,url,check_time=5,check_cnt=10):
    data=json.dumps(data)
    data=json.loads(data)
    print(data)
    for i in range(0,check_cnt):
        print "第 %d 次 检测任务状态..." %(i+1)
        try:
            request = urllib2.Request(
                url     = url+'/autodeploy/QueryJob/',
                # data    = urllib.urlencode({'task_id':str(data['task_id']),'no':str(data['paras'][0]['no']),'step_num':str(data['paras'][0]['step_num'])}))
                data    = json.JSONEncoder().encode(data)
            )
            res = urllib2.urlopen(request)
        except Exception, e:
            print '获取任务信息失败\n 明细:%s\n过%s秒重试' %(str(e),check_time)
            pass
        else:
            print "获取任务信息成功..."
            rs = analyzeResult(res.read(),len(data['paras']))
            if rs==0:
                print "任务执行完毕..."
                sys.exit(0)
            elif rs==1:
                print "任务正在执行，等待 %s 秒后重新检查..." %check_time
            else:
                sys.exit(255)
        finally:
            pass
        time.sleep(check_time)
    print '任务还未全部执行完成,超过限定时间,此次任务失败...准备退出任务程序...'
    sys.exit(255)

##解析结果
def analyzeResult(res,total_cnt):
    ##0:任务完成,1:执行中,2:执行错误
    result=json.loads(res)
    print("res",result)
    if len(result) > 0:
        total_cnt=now_step=int(result['step_num'])
        need_cnt =len(result['iplist'].split(','))
        success_cnt=len(result['success_Result'].split(',')) if 'success_Result' in result.keys() else 0
        failed_cnt=len(result['failed_Result'].split('JD_ERROR')) if 'failed_Result' in result.keys() else 0
        unknown_cnt=need_cnt-(success_cnt+failed_cnt)
        print '开始解析...'
        print '总计需要 %d 步,目前已经进行到第 %s 步...' % (total_cnt,now_step)
        print '第 %s 步 共有 %s 台机器需要执行,目前成功的为 %s 台,失败的为 %s,没有返回的为 %s 台'  %(now_step,need_cnt,success_cnt,failed_cnt,unknown_cnt)
        if need_cnt==success_cnt and total_cnt == now_step and failed_cnt==0 :
            print '所有任务执行完毕...退出调度程序'
            return 0
        elif unknown_cnt > 0:
            print '以下服务器还未返回结果...'
            reip = re.compile(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])')
            fail_list = reip.findall(result['failed_Result'])
            temp1=set(result['iplist'].split(',')).difference( set(result['success_Result'].split(',')) if 'success_Result' in result.keys() else [] )
            temp2=set(temp1).difference(set(fail_list))
            unknown_ip_list=[]
            for ip in temp2:
                if ip in result['iplist'].split(','):
                    unknown_ip_list.append(ip)
            print '\t',unknown_ip_list
            return 1
        elif total_cnt > now_step and failed_cnt ==0:
            return 1
        elif failed_cnt>0:
            print '检测到任务失败,准备退出任务程序...'
            print '以下为错误明细：'
            for error in result['failed_Result'].split('JD_ERROR'):
                print '\t %s' %error
            return 2
    else:
        print '目前没有任务返回结果...'
        return 1
'''
# def getConfig(args,params):
#     if len(args)<4:
#         print "usage: python callsalt.py salt-master-url cmd args ip-list [times] "
#         exit(1)
#     ## 处理参数
#     params["url"] =args[0]
#     _cmd =args[1]
#     _arg =args[2]
#     _ips =args[3]
#     if _arg!="no_args":
#         params["data"]=cmd%(_cmd,_arg,_ips,random.randint(40000, 45000))
#     else:
#         params["data"]=cmd_noarg%(_cmd,_ips,random.randint(40000, 45000))
#     params["times"]=60
#     try:
#         if len(args)>=5:
#             params["_times"]=string.atoi(args[4])
#     except:
#         print "input times wrong! set default value 30"
#         params["_times"]=60
'''
def main():
    #处理参数
    # data = '{"mid":"201702161129_3","paras":[{"arg":"zhulh","cmd":"os_util.useradd","cmd_parent":"os_util","ip_category_list":"102,67","ip_list":"172.19.152.40,172.16.167.106","no":"2"}]}'
    # data = {"task_id":"2017030201","paras":[{"arg":"zhulh","cmd":"os_util.userdel","cmd_parent":"os_util","ip_category_list":"102,67","ip_list":"172.19.152.19","no":"1","step_num":"1"}]}
    data = {"task_id":"2017030201","step_num":"1","no":"1","ip_list":"172.19.152.19,172.19.152.21,172.19.152.88","cmd":"os_util.useradd","arg":"zhulh"}
    url='http://127.0.0.1:9009'
    ##调用接口    command(data,url)
    # command(data,url)
    # if command(data,url) == "True":
    #     print '等待10秒检查返回结果'
    #     time.sleep(10)
    data = {"task_id":"2017030201","paras":[{"arg":"zhulh","cmd":"os_util.useradd","cmd_parent":"os_util","ip_category_list":"102,67","ip_list":"172.19.152.19,172.19.152.21,172.19.152.88","no":"1","step_num":"1"}]}
    checkResult(data,url)

if __name__ == '__main__':
    main()
