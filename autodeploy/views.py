#!/usr/bin/env python
# -*- coding=utf-8 -*-

from django.shortcuts import render,HttpResponse,render_to_response
from django.views.decorators.csrf import csrf_exempt
from salt_api import saltAPI
import models
import time,sys,os
base_dir = '/'.join(os.path.abspath(os.path.dirname(__file__)).split("/"))
sys.path.append(base_dir)
from logger import logger
from django import forms
# Create your views here.
from django.conf import settings
import json
reload(sys)
sys.setdefaultencoding('utf-8')
from functools import wraps
import datetime

# http://hustxiaoxian.lofter.com/post/1cc7b162_3a6d738

# 从这块开始是按照autodeploy来写的

def login(func):
    @wraps(func)
    def login_wrapper(request):
        try:
            #获取请求的IP地址
            if request.META.has_key('HTTP_X_FORWARDED_FOR'):
                ip =  request.META['HTTP_X_FORWARDED_FOR']
            else:
                ip = request.META['REMOTE_ADDR']
            logger.info(" - 获取到的IP地址为：%s"%ip)
            #判断请求的IP地址是否存在安全的列表中
            if ip not in settings.CLIENT_SAFE_IF:
                logger.warning(" - 您访问的IP[%s]不在安全IP列表[%s]中！"%(ip,settings.CLIENT_SAFE_IF))
                return HttpResponse("False")
            logger.info(" - 访问IP[%s]在安全IP列表[%s]中！"%(ip,settings.CLIENT_SAFE_IF))
            return func(request)
        except Exception,e:
            logger.warning(" - The exception is %s"%str(e))
            return HttpResponse("False")
    return login_wrapper

@csrf_exempt
def SaveLog(request):
    """
    salt-minion callback_util模块使用，将执行结果存入数据库中
    :param request:
    :return:
    """
    if request.method == "POST":
        jid = request.POST.get("jid").encode()
        ip = request.POST.get("id").encode()
        result=eval(request.POST.get("return").encode())['result']
        detail=eval(request.POST.get("return").encode())['details']
        t_detail = models.t_exec_jid_detail(jid=jid, ip=ip,result=result,detail=detail)
        t_detail.save()
        logger.info(" - 接收到的报文是: %s"%json.dumps(request.POST))
        logger.info(" - 接收到的参数是jid[%s]id[%s]"%(jid,ip))
    else:
        logger.warning(" - The salt-minion's request is not post !")
    return HttpResponse("OK")

@login
@csrf_exempt
def ReceiveTask(request):
    """
    执行salt 命令接口
    :param request:
    :return:
    """
    print("request.POST-->",request.POST)
    # 判断请求是否为POST
    if request.method == "POST":
        try:
            # task_id = str(json.loads(request.POST.keys()[0])['task_id'])
            # fun = str(json.loads(request.POST.keys()[0])['paras'][0]["cmd"])
            # tgt = str(json.loads(request.POST.keys()[0])['paras'][0]["ip_list"])
            # no = str(json.loads(request.POST.keys()[0])['paras'][0]["no"])
            # step_num = str(json.loads(request.POST.keys()[0])['paras'][0]["step_num"])
            task_id = str(json.loads(request.POST.keys()[0])['task_id'])
            fun = str(json.loads(request.POST.keys()[0])["cmd"])
            tgt = str(json.loads(request.POST.keys()[0])["ip_list"])
            no = str(json.loads(request.POST.keys()[0])["no"])
            step_num = str(json.loads(request.POST.keys()[0])["step_num"])
            #回调函数
            ret = "callback_util"
            #列表模式
            expr_form = "list"
            #调用salt是异步模式
            client = "local_async"
            params = {
                    "client":client,
                    "fun":fun,
                    "expr_form":expr_form,
                    "tgt":tgt,
                    "ret":ret,
                        }
            #如果有arg参数传过来就得将参数通过####分割出来
            if json.loads(request.POST.keys()[0]).has_key("arg"):
                arg = str(json.loads(request.POST.keys()[0])["arg"])
                for num,args in enumerate(arg.split("####")):
                    params['arg%s'%str(int(num)+1)] = args
            logger.info(" - 接收到命令串为: %s"%params)
            logger.info(" - task_id == %s"%str(task_id))
            #这块会出现The Exception is 'ascii' codec can't decode byte 0xe6 in position 3: ordinal not in range(128)错误
            #需要添加
            # reload(sys)
            # sys.setdefaultencoding('utf-8')
            # if str(no) == "1" :
            # ip_num = len(tgt.split(","))
            # 在这里需要判断这个任务号是否存在，如果存在需要判断是否执行成功，成功则打印成功日志，失败将失败的机器再次执行；
            if models.t_exec_mapping.objects.all().filter(task_id=task_id,no=str(no),step_num=step_num).count():
                    #查找task_id对应的jid
                    jid = models.t_exec_mapping.objects.all().filter(task_id=task_id,no=str(no),step_num=step_num).values("jid")
                    #临时的执行完返回true结果的ip列表
                    true_ip_list = []
                    for i in jid:
                        #通过jid将所有返回值为True的查询出来
                        true_ret = models.t_exec_jid_detail.objects.all().values('ip').filter(jid=i["jid"],result='True')
                        if len(true_ret) > 0:
                            for j in true_ret:
                                true_ip_list.append(str(j["ip"]))
                    #通过task_id，no和step_num查找并且jid是排序最小的ip_list的值，这个就是第一次执行任务的时候IP列表
                    ip_all = models.t_exec_mapping.objects.all().values('ip_list').filter(task_id=task_id,no=str(no),step_num=step_num).order_by('jid').first()
                    ip_all_list = str(ip_all['ip_list']).split(",")
                    #判断ip_all中的值和temp_true_ip_list中的值是否一样，如果是一样的说明本次任务执行成功，如果不一样说明本次任务有失败的节点
                    if set(ip_all_list) == set(true_ip_list):
                    # if set(tgt.split(",")) == set(temp_true_ip_list):
                        logger.info(" - 当前任务[%s]已成功执行完成，请不要重复尝试"%str(task_id))
                        logger.info(" - true")
                        return HttpResponse('True')
                    else:
                        # 将第一次执行的command查询出来，跟本次任务的fun进行对比，如果一样的就执行失败的节点，不一样的话就退出返回False
                        command = models.t_exec_mapping.objects.all().values('command').filter(task_id=task_id,no=str(no),step_num=step_num).order_by('jid').first()['command']
                        if fun != command:
                            logger.warning(" - 检查Command时发现不一致，最开始的是[%s],现在的是[%s]"%(command,fun))
                            return HttpResponse('False')
                        logger.info(" - 开始查询任务[%s]的执行详情..."%task_id)
                        logger.info(" - 任务[%s]有执行失败的主机"%task_id)
                        #将tgt为空，通过ip_all_list和true_ip_list来得差集，就是需要执行的ip列表
                        tgt = ""
                        # logger.info(" - The list is %s,the temp_ip_list is %s,the temp_true_ip_list is %s"%((list(set(ip_all_list).difference(set(true_ip_list)))),temp_ip_list,temp_true_ip_list))
                        if len(list(set(ip_all_list).difference(set(true_ip_list)))) == 1:
                            for line in list(set(ip_all_list).difference(set(true_ip_list))):
                                tgt = line
                        else:
                            for line in list(set(ip_all_list).difference(set(true_ip_list))):
                                tgt = line + "," + tgt
                        #可能有","结尾的情况
                        tgt = tgt.strip(",")
                        # 这块还需要确认成功和失败入库的情况
                        logger.info(" - The tgt is %s"%tgt)
                        params["tgt"] = tgt
            else:
                # 当查询发现数据库中没有task_id和no的数据，就得需要判断在no之前的有没有数据，如果有就执行，没有的话就退出。
                if int(no) > 1:
                    format_no = str(int(no) - 1)
                    # 判断no - 1的情况数据存不存在，如果为0的说明不能执行，如果不为0就可以执行。
                    if int(models.t_exec_mapping.objects.all().filter(task_id=task_id,no=format_no,step_num=step_num).count()) == 0 :
                        logger.info(" - 当前任务[%s]执行步骤[1]时异常，可能是任务的执行次数不正确，还没有执行第一次！"%(task_id))
                        logger.info(" - false")
                        return HttpResponse("False")
                else:
                    #当传进来的参数step_num大于1的时候，需要进行判断是否执行的的步数有没有执行。
                    if int(step_num) > 1:
                        format_step = str(int(step_num) - 1 )
                        if int(models.t_exec_mapping.objects.all().filter(task_id=task_id,no=no,step_num=format_step).count()) == 0:
                            logger.info(" - 当前任务[%s]执行步骤[1]时异常，可能是任务的步数不正确，还没有执行之前的步数！"%(task_id))
                            logger.info(" - false")
                            return HttpResponse("False")
            #salt-api实例化,并开始调用salt-api
            sapi = saltAPI()
            logger.info(" - The params is %s"%params)
            result = sapi.saltCmd(params)
            logger.info(" - 调用 Salt-API 返回信息: %s"%result)
            jid = result[0]['jid']
            createtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            t_mapping = models.t_exec_mapping(jid=jid,ip_list=tgt,command=fun,no=no,task_id=task_id,step_num=step_num,createtime=createtime)
            t_mapping.save()
            return HttpResponse("True")
        except Exception,e:
            logger.critical(" - The Exception is %s"%str(e))
    else:
        logger.warning(" - 必须是post的请求才能执行！")
    return HttpResponse('False')

@login
@csrf_exempt
def QueryJob(request):
    """
    查询任务结果的接口
    :param request:
    :return:
    """
    result = {
        "failed_Result":"",
        "iplist":"",
        "success_Result":"",
        "no":"",
        "step_num":""
    }
    try:
        task_id = str(json.loads(request.POST.keys()[0])['task_id'])
        no = str(json.loads(request.POST.keys()[0])['paras'][0]['no'])
        tgt = str(json.loads(request.POST.keys()[0])['paras'][0]['ip_list'])
        step_num = str(json.loads(request.POST.keys()[0])['paras'][0]["step_num"])
        logger.info(" - 接收到的taskid为:%s"%task_id)
        if models.t_exec_mapping.objects.all().filter(task_id=task_id,no=str(no),step_num=step_num).count():
            #查找task_id对应的jid
            logger.info(" - 开始查询任务[%s]的执行详情..."%task_id)
            #通过task_id，no和step_num查找并且jid是排序最小的ip_list的值，这个就是第一次执行任务的时候IP列表
            ip_all = models.t_exec_mapping.objects.all().values('ip_list').filter(task_id=task_id,no=str(no),step_num=step_num).order_by('jid').first()
            ip_all_list = str(ip_all['ip_list']).split(",")
            jid = models.t_exec_mapping.objects.all().filter(task_id=task_id,no=str(no),step_num=str(step_num)).values("jid")
            true_ip_list = []
            false_ip_list = []
            fail_detail_list = []
            for i in jid:
                #通过jid将所有返回值为True的查询出来
                true_ret = models.t_exec_jid_detail.objects.all().values('ip').filter(jid=i["jid"],result='True')
                false_ret = models.t_exec_jid_detail.objects.all().values('ip','detail').filter(jid=i["jid"],result='False')
                if len(true_ret) > 0:
                    for j in true_ret:
                        true_ip_list.append(str(j["ip"]))
                if len(false_ret) > 0:
                    for j in false_ret:
                        false_ip_list.append(str(j["ip"]))
                        fail_detail_list.append((str(j["ip"]) +":"+str(j['detail'])))
            unknown_list = set(ip_all_list).difference(set(false_ip_list + true_ip_list))
            #判断tgt中的值和temp_true_ip_list中的值是否一样
            result["iplist"] = tgt
            result["no"] = no
            result["step_num"] = step_num
            #此处判断是否有返回值，都为0，说明任务还没有返回值
            if len(true_ip_list) == 0 and len(false_ip_list) == 0:
                logger.info(' - 查询任务[%s]返回报文为:{"message":"根据任务ID[%s]未查询到任务信息","result":"no_record"}'%(task_id,task_id))
                result = {}
            #这里是判断是否执行成功
            if set(tgt.split(",")) == set(true_ip_list):
                logger.info(" - 任务[%s]执行成功"%task_id)
                logger.info(" - true")
                if result.has_key("failed_Result"):
                    result.pop("failed_Result")
                #如果有失败的IP，则说明本次任务失败
            elif len(false_ip_list) > 0:
                logger.info(" - 任务[%s]执行失败的主机"%task_id)
                temp_list=[]
                for k in false_ret:
                    temp_list.append(k["ip"] + ":" + k["detail"])
                now_date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                old_date = models.t_exec_mapping.objects.all().values('createtime').filter(task_id=task_id,no=str(no),step_num=step_num).order_by('jid').last()
                if int(Caltime(now_date,str(old_date['createtime'])))/60 > 5:
                    logger.info(''' - 查询任务[%s]返回报文为:{"all_detail":"%s","all_num":%s,"fail_detail":"%s","fail_num":%s,"message":"任务[%s]有执行失败的主机","result":"fail","success_detail":"%s","success_num":%s}'''
                            %(task_id,str(ip_all['ip_list']),len(ip_all_list),(",".join(set(fail_detail_list))+","+",".join(unknown_list)),(len(set(fail_detail_list))+len(unknown_list)),task_id,",".join(true_ip_list),len(true_ip_list)))
                    for ip in unknown_list:
                        temp_list.append(ip + ":it can't return")
                    logger.info(" - false")
                else:
                    logger.info(''' - 查询任务[%s]返回报文为:{"all_detail":"%s","all_num":%s,"fail_detail":"%s","fail_num":%s,"message":"任务[%s]有执行失败的主机","result":"running","running_detail":"%s","running_num":%s,"success_detail":"%s","success_num":%s}'''
                            %(task_id,str(ip_all['ip_list']),len(ip_all_list),",".join(set(fail_detail_list)),len(set(fail_detail_list)),task_id,",".join(unknown_list),len(unknown_list),",".join(true_ip_list),len(true_ip_list)))
                result["failed_Result"] = "JD_ERROR".join(temp_list)
            #如果没有成功执行的IP，则将result中success_Result的item删除掉
            if len(true_ip_list) == 0:
                if result.has_key("failed_Result"):
                    result.pop("success_Result")
            else:
                result["success_Result"] = ",".join(true_ip_list)
            # data.append(result)
        #这块是没有task_id
        else:
            logger.debug(" - 任务[%s]不存在！"%task_id)
            result={}
    except Exception,e:
        logger.critical(" - The Exception is %s"%str(e))
    res = json.dumps(result)
    return HttpResponse(res,content_type="application/json")

#计算两个时间差，以秒为单位
def Caltime(date1,date2):
    date1=time.strptime(date1,"%Y-%m-%d %H:%M:%S")
    date2=time.strptime(date2,"%Y-%m-%d %H:%M:%S")
    date1=datetime.datetime(date1[0],date1[1],date1[2],date1[3],date1[4],date1[5])
    date2=datetime.datetime(date2[0],date2[1],date2[2],date2[3],date2[4],date2[5])
    return (date1-date2).seconds

