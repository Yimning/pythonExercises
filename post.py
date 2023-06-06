#!/usr/bin/env python3
# _*_coding:utf-8_*_
# Author: Yimning
# Date: 2022-11-03 15:00:15
# Description: uploadFile

import os
import sys
import requests


# uploadFile
def uploadFile(url,fileName):
    try: 
        headers = {
            'Connection':'close',
            'content-type': 'application/json;charset=UTF-8'
        }
  
        payload={}


        response = requests.request("POST",url, headers=headers, data=payload, verify=False)
        # 经过观察发现，使用后关闭res.close()，可以解决Max retries exceeded with url 的错误
        return  response
    except Exception as e:
        print('异常:',e)
        return 

 
if __name__ == "__main__":
    # data={
    #     'id':'8989-dddvdg',
    #     'name':'文章标题-JSON格式参数演示',
    #     "brief":'快速入门json参数',
    #     'category':'分类'
    #     }
    data={}
    response = uploadFile('https://api.crap.cn/visitor/example/json.do',data)
    if(response != None):
        print("status_code: %s,response_result: %s" % (response.status_code,response.text) )
        response.close()

