#!/usr/bin/env python
# -*- coding=utf8 -*-

import os,sys
#在这里将django的settings配置给引进来
base_dir = '/'.join(os.path.abspath(os.path.dirname(__file__)).split("/")[:-1])
# print base_dir
sys.path.append(base_dir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'Aircraftcarrier.settings'

# from django.core.management import setup_environ
# import settings
# setup_environ(settings)
from autoreport.models import Assets,Server_info,Static
import salt.utils.event
from logger import logger
from thread_pool import ThreadPool
import threading
from multiprocessing import Process
import multiprocessing
import time,datetime
import salt.client

saltpki_dir = "/etc/salt/pki"
saltmaster_config = "/etc/salt/master"
sock_dir = "/var/run/salt/master"
pool = ThreadPool(8)

local = salt.client.LocalClient()

def listen_event():
    event = salt.utils.event.MasterEvent(sock_dir)
    for eachevent in event.iter_events(tag='salt/job/',full=True):
            pool.run(target=save_data,args=(eachevent,),callback=callback)
    pool.close()

def callback():
    pass

def save_data(eachevent):
    data = eachevent["data"]
    now_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    if "return" in data:
        if  data["fun"] == "mine.update":
            # print("-------------%s"%now_time)
            if Assets.objects.all().filter(assert_id=data['id']).count():
                # Assets.objects.update(assert_id=data['id'],update_time=data['_stamp'])
                Assets.objects.filter(assert_id=data['id']).update(update_time=now_time)
            else:
                Assets.objects.create(assert_id=data['id'],update_time=now_time)
            logger.info("[%s] [%s] 还存活着！"%(threading.current_thread(),data['id']))
        elif data["fun"] == "grains.items":
            # print("[jid] is [%s], [id] is [%s], [fun] is [%s],[mem_total] is [%s],[num_cpus] is [%s]"%(data['jid'],data['id'],data['fun'],data['return']['mem_total'],data['return']['num_cpus']))
            # print("[jid] is [%s], [id] is [%s], [fun] is [%s], [mem_total] is [%s],[num_cpus] is [%s], [os] is [%s],[manufacturer] is [%s],[cpu_model] is [%s]"%(data['jid'],data['id'],data['fun'],data['mem_total'],data['num_cpus'],data['osfinger'],data['manufacturer'],data['cpu_model']))
            try:
                total_mem = str(data['return']['mem_total']).strip()
                if total_mem == "":
                    total_mem =0
                else:total_mem = int(total_mem) / 1024
                if total_mem > 30 and total_mem < 40 :
                    total_mem=32
                elif total_mem > 50 and total_mem <= 66 :
                    total_mem=64
                elif total_mem > 80 and total_mem <= 100 :
                    total_mem=96
                elif total_mem > 100 and total_mem <= 130 :
                    total_mem=128
                elif total_mem > 150 and total_mem <= 200 :
                    total_mem=196
                elif total_mem > 200 :
                    total_mem=256
                else:total_mem=""
            except Exception,e:
                total_mem=""
                logger.warning("[%s] The exception is %s"%(threading.current_thread(),str(e)))
            # total_mem = data['return']['mem_total']
            try:
                if Server_info.objects.all().filter(assert_id=data['id']).count():
                    # Assets.objects.update(assert_id=data['id'],update_time=data['_stamp'])
                    Server_info.objects.filter(assert_id=data['id']).update(memory=total_mem,cpu_num=data['return']['num_cpus'],cpu_model=data['return']['cpu_model'],
                                                                       os="%s %s"%(data['return']['osfullname'],data['return']['osrelease']),hostname=data['return']['localhost'],
                                                                       sn=data['return']['serialnumber'],manufacturer=data['return']['manufacturer'],kernelrelease=data['return']['kernelrelease'],update_time=now_time)
                else:
                    Server_info.objects.create(assert_id=data['id'],memory=total_mem,cpu_num=data['return']['num_cpus'],cpu_model=data['return']['cpu_model'],
                                                                       os="%s %s"%(data['return']['osfullname'],data['return']['osrelease']),hostname=data['return']['localhost'],
                                                                       sn=data['return']['serialnumber'],manufacturer=data['return']['manufacturer'],kernelrelease=data['return']['kernelrelease'],update_time=now_time)
            except Exception,e:
                logger.warning("[%s] The exception is %s"%(threading.current_thread(),str(e)))
            # logger.info("[%s] [jid] is [%s], [id] is [%s], [fun] is [%s], [mem_total] is [%s],[num_cpus] is [%s], [os] is [%s %s],[manufacturer] is [%s],[cpu_model] is [%s],[hostname] is [%s],[sn] is [%s]"%(
            #     threading.current_thread(),data['jid'],data['id'],data['fun'],data['return']['mem_total'],data['return']['num_cpus'],data['return']['osfullname'],data['return']['osrelease'],data['return']['manufacturer'],
            #     data['return']['cpu_model'],data['return']['localhost'],data['return']['serialnumber']))
            logger.info("[%s] [jid] is [%s], [id] is [%s], [fun] is [%s], [mem_total] is [%s],[num_cpus] is [%s], [os] is [%s %s],[manufacturer] is [%s],[cpu_model] is [%s],[hostname] is [%s],[sn] is [%s],[kernelrelease] is [%s]"%(
                threading.current_thread(),data['jid'],data['id'],data['fun'],total_mem,data['return']['num_cpus'],data['return']['osfullname'],data['return']['osrelease'],data['return']['manufacturer'],
                data['return']['cpu_model'],data['return']['localhost'],data['return']['serialnumber'],data['return']['kernelrelease']))

        elif eachevent["tag"].count("salt/job/") == 1 and eachevent["tag"].count("ret") == 1:
            logger.debug("[%s] [jid] is [%s], [id] is [%s], [fun] is [%s], [fun_args] is [%s],[time] is [%s]"%(threading.current_thread(),data['jid'],data['id'],data['fun'],data['fun_args'],data['_stamp']))
    else:
        logger.debug("[%s] [%s]"%(threading.current_thread(),data))

def memory(mem):
    pass

#参考https://my.oschina.net/anylain/blog/273927
#参考http://www.tuicool.com/articles/jEBrYz2
def grain_data():
    while True:
        # ret=Assets.objects.all().values('assert_id')
        # ip_list=""
        # logger.info(" [%s] It's time to grain the information !"%multiprocessing.current_process().name)
        # for value in ret:
        #     ip_list = ip_list + ','+value['assert_id']
        # local.cmd(tgt=ip_list,fun="grains.items",expr_form="list")
        # flag = 0
        # while True:
        #     #1天执行一次
        #     if flag == 144:
        #         logger.info('[%s] The waiting time is over !'%multiprocessing.current_process().name)
        #         break
        #     flag += 1
        #     logger.info('[%s] The grain_data process is working and the flag number is [%s] !'%multiprocessing.current_process().name,flag)
        #     time.sleep(600)
        now_date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        if Static.objects.all().count():
            old_time = Static.objects.all().values('update_time')
            flag = Caltime(now_date,str(old_time[0]['update_time']))
            #1天执行一次
            if  flag == 1:
                logger.info(" [%s] It's time to grain the information !"%multiprocessing.current_process().name)
                update_grains()
                Static.objects.update(update_time=now_date)
            Static.objects.update(flag=flag)
        else:
            Static.objects.create(update_time=now_date)
            update_grains()
        logger.info('[%s] The grain_data process is working!'%multiprocessing.current_process().name)
        time.sleep(600)

def update_grains():
    ret=Assets.objects.all().values('assert_id')
    ip_list=""
    for value in ret:
        ip_list = ip_list + ','+value['assert_id']
    local.cmd(tgt=ip_list,fun="grains.items",expr_form="list")


def Caltime(date1,date2):
    date1=time.strptime(date1,"%Y-%m-%d %H:%M:%S")
    date2=time.strptime(date2,"%Y-%m-%d %H:%M:%S")
    date1=datetime.datetime(date1[0],date1[1],date1[2],date1[3],date1[4],date1[5])
    date2=datetime.datetime(date2[0],date2[1],date2[2],date2[3],date2[4],date2[5])
    return (date1-date2).days

def main():
    event = Process(target=listen_event,args=())
    event.start()

    process = Process(target=grain_data,args=())
    process.start()

if __name__ == "__main__":
    main()



