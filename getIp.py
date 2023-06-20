#!/usr/bin/env python3
# _*_coding:utf-8_*_
# Author: Yimning
# Date: 2022-11-03 15:00:15
# Description: getIp


#  Development ENV:
#       pip install IPy
#  
#
#  RUN:
#       python -u "e:\Work\python\01\logCollection.py"
#       pyinstaller -D -w .\logCollection.py
#
import os   

#ip = IP('192.168.43.0/16')

# 查找0～255的地址
for i in range(255):
    ip = "192.168.43.{}".format(i)
    ret =os.system('ping -c 1 -w 1 %s'%ip) #每个ip ping 1次，等待时间为1s
    if ret:
        print('ping %s is fail'%ip)
    else:
        print('ping %s is ok'%ip)
        # break
