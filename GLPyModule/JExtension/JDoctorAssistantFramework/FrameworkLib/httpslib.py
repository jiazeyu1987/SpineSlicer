import slicer.util as util
import json,slicer,os,qt,requests
from datetime import datetime
import concurrent.futures
class httplibClass: 
  cache_name='da_session_cookies.pkl'
  #host = "http://127.0.0.1:5000"
  host = "http://47.120.2.163/"
  #host = "http://192.168.101.85:5000"
  
  def __init__(self):
    self.executor = concurrent.futures.ThreadPoolExecutor()
    self.host = util.getjson("host")
    print("test host:",self.host)
    
  
  def httpuploads(self,urlpath,files=[],data=[]):
    cache,usesrname,session = self.get_cache()
    if not cache:
      util.showWarningText("当前功能需要先登录。。。\n请点击右上方登录按钮进行登录")
      return False,0
    url = self.host + urlpath
    # Optionally, you can add headers or other form data
    headers = {}

    # Send POST request
    response = session.post(url, files=files, headers=headers, data=data)
    
    # 检查服务器响应
    if response.status_code == 200:
        try:
            print("--------httpupload response.status_code-------",response.status_code,response.text)
            json_obj = json.loads(response.text)
            successs = json_obj['success']
            if successs == "false" or successs == "False" or successs==False:
                if json_obj['msg'] == "need login":
                  self.clear_cache()
                  util.send_event_str(util.FrameworkTopRefreshCache)
                  util.showWarningText("当前登录信息已失效，请重新登录")
                  return False,-998
                else:
                  return False,json_obj['msg']
            else:
              return True,json_obj
        except Exception as e:
            print("parse error with4:"+e.__str__())
            return False,"parse error"
    else:
        return False,response.status_code
      
      
  def httpupload(self,urlpath,file_path):
    cache,usesrname,session = self.get_cache()
    if not cache:
      util.showWarningText("当前功能需要先登录。。。\n请点击右上方登录按钮进行登录")
      return False,0
    url = self.host + urlpath
    base_file_name = os.path.basename(file_path)
    # Prepare the file dictionary to send as files parameter in requests
    files = {'file': (base_file_name, open(file_path, 'rb'), 'application/x-rar-compressed')}
    # Optionally, you can add headers or other form data
    headers = {}
    data = {'key': 'value'}  # additional parameters if needed

    # Send POST request
    response = session.post(url, files=files, headers=headers, data=data)
    
    # 检查服务器响应
    if response.status_code == 200:
        try:
            print("--------httpupload response.status_code-------",response.status_code,response.text)
            json_obj = json.loads(response.text)
            successs = json_obj['success']
            if successs == "false" or successs == "False" or successs==False:
                if json_obj['msg'] == "need login":
                  self.clear_cache()
                  util.send_event_str(util.FrameworkTopRefreshCache)
                  util.showWarningText("当前登录信息已失效，请重新登录")
                  return False,-998
                else:
                  return False,json_obj['msg']
            else:
              return True,json_obj
        except Exception as e:
            print("parse error with4:"+e.__str__())
            return False,"parse error"
    else:
        return False,response.status_code
  
  
  def runAsync(self, func):
        self.executor.submit(func)
        
  def asyncTask(self, url, data,timeout=7):
    message = None
    response_json = None
    try:
        cache,usesrname,session = self.get_cache()
        response = session.post(self.host + url, data=data,timeout=timeout)
        response_json = response.json()
        message = f"receive message {response_json.__str__()}"
    except requests.exceptions.RequestException as e:
        message = f'Error: {e}'
    finally:
        print(message)
    print(response.text)
    return json.loads(response.text)
            
            
  def httpget(self,path,json_val,need_login=True):
    if need_login:
      cache,usesrname,session = self.get_cache()
      if not cache:
        util.showWarningText("当前功能需要先登录。\n请点击右上方登录按钮进行登录")
        return False,0
    url = self.host + path
    try:
      if need_login:
        response = session.get(url, data=json_val)
      else:
        response = requests.get(url, params=json_val)
    except requests.exceptions.ConnectionError as cerror:
      util.showWarningText("无法连接到服务器")
      return False,-999
    # 检查服务器响应
    if response.status_code == 200:
        try:
            print("--------response.status_code-------",response.text)
            json_obj = json.loads(response.text)
            successs = json_obj['success']
            if successs == "false" or successs == "False" or successs==False:
                if json_obj['msg'] == "need login":
                  self.clear_cache()
                  util.send_event_str(util.FrameworkTopRefreshCache)
                  util.showWarningText("当前登录信息已失效，请重新登录")
                  return False,-998
                else:
                  return False,json_obj['msg']
            else:
              return True,json_obj
        except Exception as e:
            print("parse error with5:"+e.__str__())
            return False,"parse error"
    else:
        return False,response.status_code
  
  def httppostasync(self, path, json_val, timeout=3, silent=True, need_login=True, file_path=None,callback=None):
    #return self.executor.submit(lambda:self._httppostasync(self, path, json_val, timeout, silent, need_login, file_path,callback))
    
    util.global_data_map["tmp"] = {}
    util.global_data_map["tmp"]["path"] = path
    util.global_data_map["tmp"]["json_val"] = json_val
    util.global_data_map["tmp"]["timeout"] = timeout
    util.global_data_map["tmp"]["silent"] = silent
    util.global_data_map["tmp"]["need_login"] = need_login
    util.global_data_map["tmp"]["file_path"] = file_path
    util.global_data_map["tmp"]["callback"] = callback
    return self.executor.submit(self.test1)
  
  def httpgetasync(self, path, json_val, timeout=3, silent=True, need_login=True, file_path=None,callback=None):
    #return self.executor.submit(lambda:self._httppostasync(self, path, json_val, timeout, silent, need_login, file_path,callback))
    
    util.global_data_map["tmp"] = {}
    util.global_data_map["tmp"]["path"] = path
    util.global_data_map["tmp"]["json_val"] = json_val
    util.global_data_map["tmp"]["timeout"] = timeout
    util.global_data_map["tmp"]["silent"] = silent
    util.global_data_map["tmp"]["need_login"] = need_login
    util.global_data_map["tmp"]["file_path"] = file_path
    util.global_data_map["tmp"]["callback"] = callback
    return self.executor.submit(self.test_get)
  
  def test_get(self):
    path = util.global_data_map["tmp"]["path"]
    json_val = util.global_data_map["tmp"]["json_val"]
    timeout = util.global_data_map["tmp"]["timeout"]
    silent = util.global_data_map["tmp"]["silent"]
    need_login = util.global_data_map["tmp"]["need_login"]
    file_path = util.global_data_map["tmp"]["file_path"]
    callback = util.global_data_map["tmp"]["callback"]
    util.global_data_map["tmp"] = {}
    print("test get",util.global_data_map["tmp"] )
    if need_login:
      cache,usesrname,session = self.get_cache()
      if not cache:
        callback(False,"当前功能需要先登录。。\n请点击右上方登录按钮进行登录")
    url = self.host + path
    try:
      if file_path:
        base_file_name = os.path.basename(file_path)
        files = {'file': (base_file_name, open(file_path, 'rb'), 'application/x-rar-compressed')}
        headers = {}
        if need_login:
          response = session.get(url, files=files, headers=headers, data=json_val,timeout=timeout)
        else:
           response = requests.get(url, files=files, headers=headers, data=json_val,timeout=timeout)
      else:
        if need_login:
          response = session.get(url, data=json_val,timeout=timeout)
        else:
          response = requests.get(url, data=json_val,timeout=timeout)
    except requests.exceptions.ConnectionError as cerror:
      callback(False,-999)
    except requests.exceptions.ReadTimeout:
      callback(False,-998)
    finally:
      print(response.__str__())
    # 检查服务器响应
    if response.status_code == 200:
        print("http get result1:",response.text)
        try:
            json_obj = json.loads(response.text)
            successs = json_obj['success']
            if successs == "false" or successs == "False" or successs==False:
                if json_obj['msg'] == "need login":
                  self.clear_cache()
                  util.send_event_str(util.FrameworkTopRefreshCache)
                  callback(False,-991)
                else:
                  callback(False,json_obj['msg'])
            else:
                  callback(True,json_obj)
        except Exception as e:
            print("parse error with11:"+e.__str__())
            callback(False,"parse error")
    else:
        callback(False,response.status_code)
        
        
  def test1(self):
    path = util.global_data_map["tmp"]["path"]
    json_val = util.global_data_map["tmp"]["json_val"]
    timeout = util.global_data_map["tmp"]["timeout"]
    silent = util.global_data_map["tmp"]["silent"]
    need_login = util.global_data_map["tmp"]["need_login"]
    file_path = util.global_data_map["tmp"]["file_path"]
    callback = util.global_data_map["tmp"]["callback"]
    util.global_data_map["tmp"] = {}
    print("11111111111122222221111",util.global_data_map["tmp"] )
    if need_login:
      cache,usesrname,session = self.get_cache()
      if not cache:
        callback(False,"当前功能需要先登录。。\n请点击右上方登录按钮进行登录")
    url = self.host + path
    try:
      if file_path:
        base_file_name = os.path.basename(file_path)
        files = {'file': (base_file_name, open(file_path, 'rb'), 'application/x-rar-compressed')}
        headers = {}
        if need_login:
          response = session.post(url, files=files, headers=headers, data=json_val,timeout=timeout)
        else:
          response = requests.post(url, files=files, headers=headers, data=json_val,timeout=timeout)
      else:
        if need_login:
          response = session.post(url, data=json_val,timeout=timeout)
        else:
          response = session.post(url, data=json_val,timeout=timeout)
    except requests.exceptions.ConnectionError as cerror:
      callback(False,-999)
    except requests.exceptions.ReadTimeout:
      callback(False,-998)
    finally:
      print(response.__str__())
    # 检查服务器响应
    if response.status_code == 200:
        print("http post result1:",response.text)
        try:
            json_obj = json.loads(response.text)
            successs = json_obj['success']
            if successs == "false" or successs == "False" or successs==False:
                if json_obj['msg'] == "need login":
                  self.clear_cache()
                  util.send_event_str(util.FrameworkTopRefreshCache)
                  callback(False,-991)
                else:
                  callback(False,json_obj['msg'])
            else:
                  callback(True,json_obj)
        except Exception as e:
            print("parse error with12:"+e.__str__())
            callback(False,"parse error")
    else:
        callback(False,response.status_code)
        
  def _httppostasync(self, path, json_val, timeout=3, silent=True, need_login=True, file_path=None,callback=None):
    util.showWarningText(path)
    if need_login:
      cache,usesrname,session = self.get_cache()
      if not cache:
        if not silent:
          util.showWarningText("当前功能需要先登录。。\n请点击右上方登录按钮进行登录")
        callback(False,"当前功能需要先登录。。\n请点击右上方登录按钮进行登录")
    url = self.host + path
    try:
      if file_path:
        base_file_name = os.path.basename(file_path)
        files = {'file': (base_file_name, open(file_path, 'rb'), 'application/x-rar-compressed')}
        headers = {}
        response = session.post(url, files=files, headers=headers, data=json_val,timeout=timeout)
      else:
        response = session.post(url, data=json_val,timeout=timeout)
    except requests.exceptions.ConnectionError as cerror:
      if not silent:
        util.showWarningText("无法连接到服务器")
      callback(False,-999)
    except requests.exceptions.ReadTimeout:
      if not silent:
        util.showWarningText("读取超时")
      callback(False,-998)
    finally:
      util.showWarningText(response.__str__())
    # 检查服务器响应
    if response.status_code == 200:
        print("http post result:",response.text)
        try:
            json_obj = json.loads(response.text)
            successs = json_obj['success']
            if successs == "false" or successs == "False" or successs==False:
                if json_obj['msg'] == "need login":
                  self.clear_cache()
                  util.send_event_str(util.FrameworkTopRefreshCache)
                  util.showWarningText("当前登录信息已失效，请重新登录")
                  callback(False,-991)
                else:
                  callback(False,json_obj['msg'])
            else:
              return True,json_obj
        except Exception as e:
            print("parse error with13:"+e.__str__())
            callback(False,"parse error")
    else:
        callback(False,response.status_code)
      
      
      
  def httppost(self,path,json_val,timeout=3,silent=False,need_login=True,file_path=None):
    if need_login:
      cache,usesrname,session = self.get_cache()
      if not cache:
        if not silent:
          util.showWarningText("当前功能需要先登录。。\n请点击右上方登录按钮进行登录")
        return False,"当前功能需要先登录。。\n请点击右上方登录按钮进行登录"
    url = self.host + path
    try:
      if file_path:
        base_file_name = os.path.basename(file_path)
        files = {'file': (base_file_name, open(file_path, 'rb'), 'application/x-rar-compressed')}
        headers = {}
        if need_login:
          response = session.post(url, files=files, headers=headers, data=json_val,timeout=timeout)
        else:
          response = requests.post(url, files=files, headers=headers, data=json_val,timeout=timeout)
      else:
        if need_login:
          response = session.post(url, data=json_val,timeout=timeout)
        else:
          response = requests.post(url, data=json_val,timeout=timeout)
    except requests.exceptions.ConnectionError as cerror:
      if not silent:
        util.showWarningText("无法连接到服务器")
      return False,-999
    except requests.exceptions.ReadTimeout:
      if not silent:
        util.showWarningText("读取超时")
      return False,-998
    # 检查服务器响应
    if response.status_code == 200:
        print("http post result:",response.text)
        try:
            json_obj = json.loads(response.text)
            successs = json_obj['success']
            if successs == "false" or successs == "False" or successs==False:
                if json_obj['msg'] == "need login":
                  self.clear_cache()
                  util.send_event_str(util.FrameworkTopRefreshCache)
                  util.showWarningText("当前登录信息已失效，请重新登录")
                  return False,-991
                else:
                  return False,json_obj['msg']
            else:
              return True,json_obj
        except Exception as e:
            print("4:"+e.__str__())
            return False,"parse error"
    else:
        return False,response.status_code

  def get_cache(self):
    cache = util.get_cache_from_PAAA("cache")
    cache_session = util.get_cache_from_PAAA("cache_session")
    cache_user_name = util.get_cache_from_PAAA("cache_user_name")
    if cache and cache_user_name:
      session = requests.Session()
      session.cookies.set("remember_token",cache)
      session.cookies.set("session",cache_session)
      return True,cache_user_name,session
    return False,0,None
  
  def clear_cache(self):
    util.save_cache_to_PAAA("cache","")
    util.save_cache_to_PAAA("cache_session","")
    util.save_cache_to_PAAA("cache_user_name","")
  
  
  def register_to_server(self,account, pwd,phone,address):
        # 设置登录的URL
        login_url = self.host+'/system/passport/register'

        # 设定要发送的登录凭据，通常是用户名和密码
        login_data = {
            'roleIds': '2',
            'username': account,
            'realName': address,
            'phone':phone,
            'password': pwd
        }

        # 发送POST请求
        response = requests.post(login_url, data=login_data)
        print("register response:",response.text)
         # 检查服务器响应
        if response.status_code == 200:
            try:
                json_obj = json.loads(response.text)
                successs = json_obj['success']
                if successs == "false" or successs == "False" or successs==False:
                    return False,json_obj['msg']
                else:
                    return True,response.status_code
            except Exception as e:
                print("parse error with2:"+e.__str__())
                return False,"parse error"
        else:
            print("register fail", response.status_code)
            return False,response.status_code
          
          
  def login_to_server(self, account, pwd):
        session = requests.Session()
        # 设置登录的URL
        login_url = self.host+'/system/passport/login'

        # 设定要发送的登录凭据，通常是用户名和密码
        login_data = {
            'username': account,
            'password': pwd
        }

        try:
          # 发送POST请求
          response = session.post(login_url, data=login_data,timeout=3)
          print("login result:",response.text)
        except requests.exceptions.ConnectionError as cerror:
          return False,-999

        # 检查服务器响应
        if response.status_code == 200:
            try:
                json_obj = json.loads(response.text)
                print(response.text)
                successs = json_obj['success']
                if successs == "false" or successs == "False" or successs==False:
                    return False,json_obj['msg']
                else:
                  if "vip_time" in json_obj:
                    time_format = "%a, %d %b %Y %H:%M:%S GMT"
                    parsed_time = datetime.strptime(json_obj["vip_time"], time_format)
                    # 将解析的时间转换为 UTC，因为 GMT 与 UTC 在现代基本是等同的
                    current_utc_time = datetime.utcnow()
                    # 比较时间
                    if current_utc_time > parsed_time:
                        vip_level = 0
                        print("当前 UTC 时间大于指定时间")
                    else:
                        print("当前 UTC 时间小于或等于指定时间")
                        vip_level = 1
                  
                  #vip_level = json_obj['vip_level']
                  from FrameworkLib.datas import fdb
                  util.username = account
                  fdb.connect_to_database()
                  fdb.set_user_viplevel(account,vip_level,json_obj["vip_time"])
                  print("set_user_viplevel:",vip_level,json_obj["vip_time"])
                  cookie = (session.cookies.get('remember_token'))
                  cache_session = (session.cookies.get('session'))
                  util.save_cache_to_PAAA("cache",cookie)
                  util.save_cache_to_PAAA("cache_session",cache_session)
                  
                  util.save_cache_to_PAAA("cache_user_name",account)
                  return True,account
            except Exception as e:
                print("parse error with3:"+e.__str__())
                return False,"parse error"
        else:
            print("login fail", response.status_code)
            return False,response.status_code
          
          
  def download_zip(self,local_filename,url):
    if not os.path.exists(os.path.dirname(local_filename)):
      os.mkdir(os.path.dirname(local_filename))
    if len(url)>0 and url[0]=="/":
        url = self.host+url
    else:
        url = self.host+"/"+url
    print("from",local_filename,"to",url)
    import requests
    # 发送 GET 请求
    with requests.get(url, stream=True) as r:
        r.raise_for_status()  # 检查请求是否成功
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

