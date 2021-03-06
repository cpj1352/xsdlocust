# -*-coding:utf-8 -*-
import ConfigParser
import json
import logging
import socket
import time,os
from logging.handlers import TimedRotatingFileHandler
import redis
import requests
import sys
from Interface import firstLevel


def log(name, err):
    time1=time.strftime('%Y%m%d',time.localtime(time.time()))
    file_name = os.getcwd()+"/"+time1+"-"+name+".log"
    log=logging.getLogger(name)
    logformatter = logging.Formatter('%(asctime)s %(filename)s:%(module)s %(levelname)s %(message)s')
    loghandle = TimedRotatingFileHandler(file_name, 'midnight', 1, 10)
    loghandle.setFormatter(logformatter)
    loghandle.suffix = '%Y%m%d'
    log.addHandler(loghandle)
    log.setLevel(logging.DEBUG)
    log.exception(err)
    log.removeHandler(loghandle)


def exportTicket(num=1):
    '''
    :param num:获取登录凭证的数量（数量多，启动时间过长）
    :return:
    '''
    host="115.28.106.133"
    pool=redis.Redis(host=host,port='6379',db='3',password="123456")
    listkey=pool.keys('h-member-session*')
    listTicket=map(lambda x:'v-session-ticket:'+x,pool.mget(listkey[0:num]))
    ticket=[]
    for i in listTicket:
        try:
            key=pool.hscan(i)[1]
            ticket.append([key.keys()[0],eval(key.values()[0])['appToken']])
        except:pass
    return ticket

def checklive(num=1):
    '''
    :param num:获取正直播的数量
    :return:
    '''
    liveID=[]
    try:
        data=requests.post(url="https://test3.txdsd.com/platform-rest/service.jws", json=firstLevel[0][1],timeout=3).json()
        listdata=data['b']['data']['liveList']
        for k,i in enumerate(listdata):
            if i['state']==1:
                liveID.append(i['liveId'])
            if k>5 or len(liveID)>num:
                break
        if liveID==[]:
            print >> sys.stderr,u'目前沒有正在直播的直播间'
    except:
         print >> sys.stderr,u'获取直播间信息失败'

    return liveID


cf = ConfigParser.ConfigParser()

class cfg():
    def __init__(self,file):
        self.file=file

    def query(self,name,key):
        cf.read(self.file)
        content=cf.get(name,key)
        return content

    def cfgdict(self,name):
        cf.read(self.file)
        configdict={}
        for i in cf.items(name):
            configdict[i[0]]=i[1]
        return configdict

    def write(self,name,key,content):
        '''
        :param content: 写入内容
        :return:
        '''
        cf.set(name,key,content)
        cf.write(open(self.file,"w"))
        cf.read(self.file)
        text=cf.get(name,key)
        assert text==str(content)#检查是否写入成功
