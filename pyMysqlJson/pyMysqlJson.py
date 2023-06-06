#!/usr/bin/python3
# encoding:utf-8
# @Time    : 2023/03/12 16:08
# @Author  : Yimning
# @Comment : pyMysqlJson

import flask,json
from flask import url_for  # 进行网页跳转
import os  # 用于操作系统文件的依赖库
import re  # 引入正则表达式对用户输入进行限制
import pymysql  # 连接数据库
from pymysql import cursors # pymysql转json关键参数cursorclass=cursors.DictCursor
from datetime import datetime  
from collections import namedtuple
from json import JSONEncoder
import pandas as pd
from resultEntity import ResultEntity
from userEntity import UserEntity

# 实例化api，把当前这个python文件当作一个服务，__name__代表当前这个python文件
api = flask.Flask(__name__) 
# 初始化数据库连接
# 使用pymysql.connect方法连接本地mysql数据库
db = pymysql.connect(host='120.77.xxx.233', port=3306, user='root',
                     password='123456', database='test', charset='utf8',cursorclass=cursors.DictCursor)
                     
# 操作数据库，获取db下的cursor对象
cursor = db.cursor()

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self, obj)


def userDecoder(userDict):
    return namedtuple('userEntity', userDict.keys())(*userDict.values())

def resultDecoder(resultDict):
    return namedtuple('resultEntity', resultDict.keys())(*resultDict.values())


# eval()方法二次封装
def eval_str(str_data):
    # eval()对特殊值处理
    null = ""
    true = True
    false = False
    return eval(str_data)


def is_numeric(s):
    if s.startswith("-") or s.startswith("+") or "." in s:
        return all(c in "0123456789.+-" for c in s)
    else:
        return all(c in "0123456789" for c in s)


# 获取复杂嵌套list，json对应的下标（key）值, 可以去到任意值
# 格式:keytag: "2.a"      dict_data:[{"a": "111", "b": 222}, "bbbb", {"a": "555", "b": 222}]
def get_nestdict_value(keytag, dict_data):
    if not isinstance(dict_data,(dict,list)):
        # dict_data = json.loads(dict_data)
        dict_data = eval_str(dict_data)  # 效果同上
    sname = keytag.strip()
    obj = scmd = realval = ""
    for i in sname.split("."):
        if is_numeric(i):
            obj = "%s[%s]" % (obj, i)
        else:
            obj = "%s['%s']" % (obj, i)
    scmd = "%s%s" % ("dict_data", obj)
    try:
        realval = eval(scmd)
    except Exception as e:
        print (e.message)
        return "[Failed]:cmd change error,eval(%s)" % scmd
    return realval


def addUser(jsonStr):
    #from-data格式参数
    userEntity = json.loads(jsonStr, object_hook=userDecoder)
    ret = 0
    retEntity = ResultEntity(0,"")
    try:
        sql = "insert into user(user, password,step,total,steptime,type,url,jointime)values(%s,%s,%s,%s,%s,%s,%s,%s)"
        ret = cursor.execute(sql, (userEntity.user,userEntity.password,userEntity.step,userEntity.total,userEntity.steptime,userEntity.type,userEntity.url,userEntity.jointime))
        retEntity.code = ret
        retEntity.message = "Successfully saved User Info."
    except Exception as err:
        retEntity.code = -1
        retEntity.message = str(err)
        print(err)
        pass
    finally:
        db.commit()
    return retEntity


def updateUser(jsonStr):
    #from-data格式参数
    userEntity = json.loads(jsonStr, object_hook=userDecoder)
    
    ret = 0
    retEntity = ResultEntity(0,"")
    try:
        # 查询现有记录
        userEntity_update_before = findOneUser(userEntity.user)
        # 判断表单转成对象之后的某个属性是否存在。若不存在时则不update mysql

        if not hasattr(userEntity, 'user'):           
            userEntity.user = userEntity_update_before.user

        if not hasattr(userEntity, 'password'):
            userEntity.password = userEntity_update_before.password

        if not hasattr(userEntity, 'step'):
            userEntity.step = userEntity_update_before.step

        if not hasattr(userEntity, 'total'):
            userEntity.total = userEntity_update_before.total

        if not hasattr(userEntity, 'steptime'):
            userEntity.steptime = userEntity_update_before.steptime

        if not hasattr(userEntity, 'type'):
            userEntity.type = userEntity_update_before.type

        if not hasattr(userEntity, 'url'):
            userEntity.url = userEntity_update_before.url

        if not hasattr(userEntity, 'jointime'):
            userEntity.jointime = userEntity_update_before.jointime

        sql = "update user set user=%s,password=%s,step=%s,total=%s,steptime=%s,type=%s,url=%s,jointime=%s where user=%s;"
        ret = cursor.execute(sql, (userEntity.user,userEntity.password,userEntity.step,userEntity.total,userEntity.steptime,userEntity.type,userEntity.url,userEntity.jointime,userEntity.user))
        
        # 处理更新结果
        if ret == 1:    
            retEntity.code = 0
            retEntity.message = "Successfully updated User Info."
        else:
            retEntity.code = -1
            retEntity.message = f"User '{userEntity.user}' not found or no fields to update."

        # 提交事务
        db.commit()
    except Exception as err:
        # 发生异常时回滚事务
        db.rollback()
        retEntity.code = -1
        retEntity.message = str(err)
        print("updateUser:",err)
    finally:
        # 关闭游标和数据库连接
        # cursor.close()
        pass
    return retEntity

# deleteUser
def deleteUser(query):
    ret = 0
    retEntity = ResultEntity(0,"")
    try:
        sql_delete = "delete from user where user='" + query + "';"
        ret = cursor.execute(sql_delete)                    # ret = 1 --> oK,ret = 0 -->fail
        # 处理删除结果
        if ret == 1:
            delete_result = "Successfully deleted User %s." % query
            retEntity.code = ret
            retEntity.message = delete_result
        else:
            delete_result = f"User '{query}' not found."
            retEntity.code = -1
            retEntity.message = delete_result
        db.commit()
    except Exception as err:
        # 发生异常时回滚事务
        db.rollback()
        retEntity.code = -1
        retEntity.message = str(err)
        print("deleteUser Exception:",err)
        pass
    finally:
        # 关闭游标和数据库连接
        # cursor.close()
        pass
    return retEntity


def findOneUser(query):
    ret = 0
    retEntity = ResultEntity(-1,"")
    userEntity = None
    try:
        #from-data格式参数
        sql_list = "SELECT * from user where user = %s;"
        cursor.execute(sql_list,query)
        results = cursor.fetchone()
        if results is None:
            return userEntity  # 没有找到该用户，直接返回 None

        # 使用 Pandas 读取查询结果集合
        df = pd.DataFrame(results, columns=[col[0] for col in cursor.description], index=['user'])
        df.drop(df.columns[1], axis=1, inplace=True)  # 删除第二列
        # 将JSON字符串解析成Python对象
        json_str = json.dumps(df.to_dict(orient='records'), ensure_ascii=False, cls=DateEncoder)

        # 把一个JSON数组变成一个JSON字符串（即去掉方括号），可以先将其解析为Python对象，然后再转换成JSON字符串。
        python_obj = json.loads(json_str)
        json_str_new = json.dumps(python_obj[0], ensure_ascii=False)

        python_to_json = json.dumps(json_str_new,ensure_ascii=False,cls=DateEncoder)    # cls=DateEncoder 将字典格式转化为字符串格式
        # print("python_to_json",python_to_json)
        userEntity = json.loads(python_to_json, object_hook=userDecoder)
    except Exception as err:
        retEntity.code = -1
        retEntity.message = str(err)
        print("findOneUser Exception:",err)
        pass
    finally:
        # 关闭游标和数据库连接
        # cursor.close()
        pass
    return userEntity

def findAllUser():
    #from-data格式参数
    try:
        sql_list = "SELECT * from user;"
        cursor.execute(sql_list)
        results = cursor.fetchall()

        if results is None:
            return None  # 没有找到该用户，直接返回 None
        
        # <class 'str'>
        python_to_json = json.dumps(results,ensure_ascii=False,cls=DateEncoder)    # cls=DateEncoder 将字典格式转化为字符串格式
        # <class 'list'>
        jsonList = json.loads(python_to_json)

        # 使用 Pandas 读取查询结果集合
        df = pd.DataFrame(results, columns=[col[0] for col in cursor.description])

        # 删除第二列
        df.drop(df.columns[1], axis=1, inplace=True)
        # # 将JSON字符串解析成Python对象
        jsonList = json.dumps(df.to_dict(orient='records'), ensure_ascii=False, cls=DateEncoder)

    except Exception as e:
        print("Error occurred: ", e) 
     
    return jsonList

#post入参访问方式二:josn格式参数  
@api.route('/post',methods=['post'])
def testPostService():
    #from-data格式参数
    sql_list = "select * from user"
    cursor.execute(sql_list)
    results = cursor.fetchall()

    print(results)
    print(type(results))    # <class 'list'> of oringinal
    python_to_json = json.dumps(results,ensure_ascii=False,cls=DateEncoder)    # cls=DateEncoder 将字典格式转化为字符串格式
    print(python_to_json)
    print(type(python_to_json))   # <class 'str'>
    jsonList = json.loads(python_to_json)
    print(type(jsonList))         # <class 'list'>
    print("List_Len:",len(jsonList))
    print("List[0]:",jsonList[0])

    count = 0
    for list in jsonList:
        count += 1
        print("List[%d]:"%(count),list)

    # Parse JSON into an object with attributes corresponding to dict keys.
    userEntity = json.loads(json.dumps(list), object_hook=userDecoder)
    print("After Converting JSON Data into Custom Python Object")
    print(userEntity.user, userEntity.step)


    print(get_nestdict_value("0.user", python_to_json))

    json_str = json.dumps(python_to_json)
    print ("python原始数据:", repr(python_to_json))
    print ("json对象:", json_str)
    json_str2 = json.dumps(python_to_json)   
    print ("python原始数据:", repr(python_to_json))
    print ("json对象:", json_str2)
    # 将json对象转换为python字典
    data3 = json.loads(json_str)
    print ("python字典:", data3)


    str = findAllUser()
    print("findAllUser:",str)

    userJsonData = '{"user": "15***742064", "password": "xxxxxxxxx", "step": 18111, "total": 0, "steptime": "2023-03-31 13:00:03", "type": 1, "url":"111","jointime": "2022-06-28 21:15:04"}'
    addUser(userJsonData)

    ret = findOneUser("15***742064")
    # 将 JSON 字符串转换为 Python 对象
    obj = json.loads(ret, object_hook=userDecoder)
    print(type(obj))

    #输出 Python 对象
    print("findOneUser:",obj.user)

    updateRet = updateUser(userJsonData)
    print(updateRet)


    userJsonData = '{"user": "15***7420640", "password": "xxxxxxxxx", "step": 18111, "total": 0, "steptime": "2023-03-31 13:00:03", "type": 1, "url":"111","jointime": "2022-06-28 21:15:04"}'
    addUser(userJsonData)
    delRet = deleteUser("15***7420640")
    print(delRet)
    
    usrname = flask.request.json.get('user')
    pwd = flask.request.json.get('password')

    if usrname and pwd:
        if usrname =='1787841***' and pwd =='******':
            ren = {'msg':'登录成功','msg_code':200}
        else:
            ren = {'msg':'用户名或密码错误','msg_code':-1}
    else:
        ren = {'msg':'用户名或密码为空','msg_code':1001}
    return json.dumps(ren,ensure_ascii=False)

# findOneUser
@api.route('/findOneUser',methods=['GET'])
def findByUserService():
    try:
        # 获取 GET 请求中的参数
        param1 = flask.request.args.get('user')

        # 根据参数编写相应的处理逻辑
        result = {}

        if param1 is not None :
            result['success'] = True
            result['message'] = 'Received parameters: {}'.format(param1)
        else:
            result['success'] = False
            result['message'] = 'Missing parameters'

        # 将结果转换成 JSON 格式并返回给客户端
        ret = findOneUser(param1)
    except Exception as err:
        print(err)

    return json.dumps(ret,ensure_ascii=False)

# findAllUser
@api.route('/findAllUser',methods=['GET'])
def findAllUserService():
    try:
        ret = findAllUser()
        return json.dumps(ret,ensure_ascii=False)
    except Exception as err:
        print(err)

# addUser
@api.route('/addUser', methods=['POST'])
def addUserService():
    try:
        # 获取客户端提交的 JSON 数据
        jsonStr = flask.request.json
        jsonStr = json.dumps(jsonStr)

        # 调用 addUser() 方法，并传入相应的参数
        ret = addUser(jsonStr)

        # 将返回结果转换为 JSON 格式的字符串，并返回给客户端
        return json.dumps(ret.__dict__, ensure_ascii=False)
    except Exception as err:
        print(err)

# deleteUser(query)
@api.route('/delUser', methods=['GET'])
def delUserService():
    try:
        # 获取 GET 请求中的参数
        param1 = flask.request.args.get('user')

        # 将结果转换成 JSON 格式并返回给客户端
        result = deleteUser(param1)
        return json.dumps(result.__dict__,ensure_ascii=False)
    except Exception as err:
        print(err)


# updateUser(jsonStr)
@api.route('/updateUser', methods=['POST'])
def updateUserService():
    try:
        # 获取客户端提交的 JSON 数据
        jsonStr = flask.request.json
        jsonStr = json.dumps(jsonStr)

        # 调用 updateUser() 方法，并传入相应的参数
        ret = updateUser(jsonStr)

        # 将返回结果转换为 JSON 格式的字符串，并返回给客户端
        return json.dumps(ret.__dict__, ensure_ascii=False)
    except Exception as err:
        print(err)



if __name__ == '__main__':
  # 启动服务器
  #api.debug = True         #改了代码后，不用重启，它会自动重启
  # 增加session会话保护(任意字符串,用来对session进行加密)
  api.secret_key = 'carson' 
  try:
    api.run(port=8888,debug=True,host='127.0.0.1') # 启动服务
  except Exception as err:  
    print(err)
    db.close()  # 关闭数据库连接




# json.dumps() 是 Python 中将 JSON 对象转换为字符串的方法，除此之外，json 模块中还有一些其他常用的方法：

# json.loads(): 将 JSON 字符串转换为 Python 对象。

# json.dump(obj, fp, *, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None, separators=None, default=None, sort_keys=False, **kw): 将 Python 对象写入文件中，以 JSON 格式序列化。

# json.load(fp, *, cls=None, object_hook=None, parse_float=None, parse_int=None, parse_constant=None, object_pairs_hook=None, **kw): 从文件中读取数据，将 JSON 字符串反序列化成 Python 对象。

# json.JSONEncoder.default(self, obj): 自定义编码器的默认方法，用于将不可序列化的对象转换为可序列化的对象。

# json.JSONDecoder.object_hook(self, dct): 自定义解码器的回调函数，用于将 JSON 对象转换为 Python 对象。

# json.JSONDecoder.raw_decode(self, s, idx=0): 解码 JSON 字符串，返回一个元组，第一个元素是转换后的 Python 对象，第二个元素是下一个字符出现的位置。

# json.JSONEncoder.encode(self, obj): 将 Python 对象序列化为 JSON 字符串。

# json.JSONDecoder.decode(self, s, *, idx=0): 将 JSON 字符串反序列化为 Python 对象。

# 以上这些方法都是处理 JSON 格式数据必不可少的，它们提供了序列化和反序列化 JSON 数据的功能，同时还可以进行自定义编码和解码操作。在使用时，我们可以根据具体需求选择适合的方法来处理 JSON 数据。

# 程序打包 ：pyinstaller -F mistep_msyql.py  resultEntity.py  userEntity.py 