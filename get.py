#!/usr/bin/env python3
# _*_coding:utf-8_*_
# Author: Yimning
# Date: 2022-11-03 15:00:15
# Description: test


import requests


# uploadFile
def uploadFile(url,fileName):
    try: 
        headers = {
            'Connection':'close',
            'content-type': 'application/json;charset=UTF-8'
        }

        payload={}

        response = requests.request("GET",url, headers=headers, data=payload, verify=False)
        # 经过观察发现，使用后关闭res.close()，可以解决Max retries exceeded with url 的错误
        return  response
    except Exception as e:
        print('异常:',e)
        return 

 
if __name__ == "__main__":

    response = uploadFile('https://cx.shouji.360.cn/phonearea.php?number=17878416534',"data")
    if(response != None):
         print("status_code: %s,response_result: %s" % (response.status_code,response.text) )
         response.close()

