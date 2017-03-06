#!/usr/bin/env python
# -*- coding=utf8 -*-

import time
import datetime
import json
import urllib2
import urllib
import sys
import random
import string

# url='http://172.22.91.79:9000'
#
# json串例子
# {
#     "paras": [
#         {
#             "cmd": "docker_util.download_image",
#             "arg": "cd /software/servers/jd-murder-0.1.2/dist;python download_image.py --max_upload_rate 10240 --max_download_rate 10240 --delay_slice 100 --delay_time 0.2 --extra_client max_uploads:10:http_timeout:60 -i druid_jypt_science:latest -s http://172.19.186.28:9999 -p /data3/download_image --mode docker --all true",
#             "ip_list": "172.19.152.15,172.19.152.16",
#             "no": "1"
#         }
#     ],
#     "mid": "43210"
# }

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
  data=json.loads(data)
  try:
    request = urllib2.Request(
        url     = url+'/AutoDeploy/receiveTask.do',
        # headers = headers,
        data    =  json.JSONEncoder().encode(data)
        )
    res = urllib2.urlopen(request)
  except Exception, e:
    print "调用接口失败:"+str(e)
    sys.exit(255)
  else:
    print "调用接口成功..."
    return res
  finally:
    pass


##检查结果
def checkResult(data,url,check_time=3,check_cnt=10):
  paras=json.loads(data)
  print(data)
  for i in range(0,check_cnt):
    print "第 %d 次 检测任务状态..." %(i+1)
    try:
      request = urllib2.Request(
          url     = url+'/AutoDeploy/QueryJob.do',
          data    = urllib.urlencode({'taskid':paras['mid']}))
      res = urllib2.urlopen(request)
    except Exception, e:
      print '获取任务信息失败\n 明细:%s\n过%s秒重试' %(str(e),check_time)
      pass
    else:
      print "获取任务信息成功..."
      # print(res.read())
      print('len(paras["paras"])',len(paras['paras']))
      rs = analyzeResult(res.read(),len(paras['paras']))
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
  print(result)
  if len(result)>0:
    now_no=int(result['no'])
    need_cnt =len(result['iplist'].split(','))
    success_cnt=len(result['success_Result'].split(',')) if 'success_Result' in result.keys() else 0
    failed_cnt=len(result['failed_Result'].split('JD_ERROR')) if 'failed_Result' in result.keys() else 0
    unknown_cnt=need_cnt-(success_cnt+failed_cnt)
    print '开始解析...'
    print '总计需要 %d 步,目前已经进行到第 %s 步...' % (total_cnt,now_no)
    print '第 %s 步 共有 %s 台机器需要执行,目前成功的为 %s 台,失败的为 %s,没有返回的为 %s 台'  %(now_no,need_cnt,success_cnt,failed_cnt,unknown_cnt)
    if need_cnt==success_cnt and total_cnt == now_no and failed_cnt==0 :
      print '所有任务执行完毕...退出调度程序'
      return 0
    elif unknown_cnt > 0:
      print '以下服务器还未返回结果...'
      print '\t',set(result['iplist'].split(',')).difference( set(result['success_Result'].split(',')) if 'success_Result' in result.keys() else [] )
      return 1
    elif total_cnt > now_no and failed_cnt ==0:
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

def getConfig(args,params):
  if len(args)<4:
    print "usage: python callsalt.py salt-master-url cmd args ip-list [times] "
    exit(1)
  ## 处理参数
  params["url"] =args[0]
  _cmd =args[1]
  _arg =args[2]
  _ips =args[3]
  if _arg!="no_args":
    params["data"]=cmd%(_cmd,_arg,_ips,random.randint(40000, 45000))
  else:
    params["data"]=cmd_noarg%(_cmd,_ips,random.randint(40000, 45000))
  params["times"]=60
  try:
    if len(args)>=5:
      params["_times"]=string.atoi(args[4])
  except:
    print "input times wrong! set default value 30"
    params["_times"]=60
  ## 打印
  #print "url: " ,params["url"]
  #print "_cmd: " ,_cmd
  #print "_arg: " ,_arg
  #print "_ips: " ,_ips
  #print "data: ",params["data"]
  #print "times:",params["times"]

def main():
    #处理参数
	# params = {}
	# getConfig(args,params)
    data = '{"mid":"201702161129_5","paras":[{"arg":"zhulh","cmd":"os_util.userdel","cmd_parent":"os_util","ip_category_list":"102,67","ip_list":"172.19.152.19,172.19.152.21","no":"1"}]}'
    url='http://127.0.0.1:9000'
    ##调用接口
	# command(params["data"],params["url"])
    command(data,url)
    print '等待5秒检查返回结果'
    time.sleep(5)

    ##返回结果
	# checkResult(params["data"],params["url"],20,params["times"])
    checkResult(data,url)

if __name__ == '__main__':
    # main(sys.argv[1:])
    main()

# 例子
# python callsalt.py http://172.19.152.40:9000 docker_util.download_image "cd /software/servers/jd-murder-0.1.2/dist;python download_image.py --max_upload_rate 10240 --max_download_rate 10240 --delay_slice 100 --delay_time 0.2 --extra_client max_uploads:10:http_timeout:60 -i druid_jypt_science:latest -s http://172.19.186.28:9999 -p /data3/download_image --mode docker --all true" 172.19.152.15,172.19.152.16
# args[0] -- 调用的salt master的地址
# args[1] -- 命令
# args[2] -- 命令参数，使用""包含所有参数
# args[3] -- salt节点的ip列表，即具体的执行主机的ip列表。以逗号分隔。
# args[4] -- 最大异步检查salt的执行循环的次数，每20s检查一次，直到所有执行完成。默认为30次，即最大10min等待完成，否则认为操作。