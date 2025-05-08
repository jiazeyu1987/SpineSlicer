import slicer,qt,vtk,ctk,os,requests,json,pickle
import slicer.util as util
import re
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from Base.JBaseExtension import JBaseExtensionWidget
#
# FrameworkLogin
#


class FrameworkLogin(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "FrameworkLogin"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["JPlugins"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["jia ze yu"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """

"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """

"""


#
# FrameworkLoginWidget
#

class FrameworkLoginWidget(JBaseExtensionWidget):
  login_agreement=2
  login_privacy=2
  login_dialog = None
  def setup(self):
    super().setup()
    self.ui.tabWidget.tabBar().hide()
    self.ui.tabWidget.setCurrentIndex(0)
    self.init_database()
    qt.QWidget.setTabOrder(self.ui.r_username, self.ui.r_password_1)
    qt.QWidget.setTabOrder(self.ui.r_password_1, self.ui.r_password_2)
    qt.QWidget.setTabOrder(self.ui.r_password_2, self.ui.BtnDoRegister)
    qt.QWidget.setTabOrder(self.ui.l_username, self.ui.l_password)
    qt.QWidget.setTabOrder(self.ui.l_password, self.ui.BtnDoLogin)
    
    self.add_button_event('BtnDoLogin', 'clicked()', self.on_do_login, True)
    self.add_button_event('BtnDoModifyPassword', 'clicked()', self.on_modify_password, True)
    self.add_button_event('BtnDoRegister', 'clicked()', self.on_do_register, True)
    self.add_button_event('BtnReturnToRegister', 'clicked()', self.on_register, True)
    self.add_button_event('BtnReturnToLogin', 'clicked()', self.on_return_to_login, True)
    self.add_button_event('BtnReturnToLogin_2', 'clicked()', self.on_return_to_login, True)
    self.add_button_event('BtnReturnToLogin_3', 'clicked()', self.on_return_to_login, True)

    self.add_button_event('btnPrivacyPolicy', 'clicked()', self.on_click_privacy, True)
    self.add_button_event('btnUserAgreement', 'clicked()', self.on_click_agreement, True)
    

    self.add_button_event('l_cb_show_password', 'toggled(bool)', self.on_show_password, True)
  

  def add_button_event(self, btn_name, operate_type, callback_func, is_connect=True):
    if hasattr(self.ui, btn_name) == False:
      return
    button = getattr(self.ui, btn_name)
    if is_connect == True:
      button.connect(operate_type, callback_func)
    else:
      button.disconnect(operate_type, callback_func)
  
  def set_dialog(self, dialog):
    self.login_dialog = dialog
    self.load_settings()
  
  def on_show_password(self,boolva):
    if not boolva:
      self.ui.l_password.setEchoMode(qt.QLineEdit.Password)
    else:
      self.ui.l_password.setEchoMode(qt.QLineEdit.Normal)
      

  def load_settings(self):
    print('load_setting')
    self.cursor.execute('''SELECT * FROM settings LIMIT 1''')
    result = self.cursor.fetchone()
    if result:
      id, username, password,remember_password, show_password, agree_protocol= result
      if remember_password:
        self.ui.l_password.setText("")
        self.ui.l_username.setText("")
      else:
        self.ui.l_password.setText("")
        self.ui.l_username.setText("")

      self.ui.l_cb_remember_password.setChecked(remember_password)
      self.ui.l_cb_show_password.setChecked(show_password)
      self.on_show_password(show_password)
      if hasattr(self.ui, 'checkUserAgreement'):
        self.ui.checkUserAgreement.setChecked(True)

    else:
      self.ui.l_password.setText("")
      self.ui.l_username.setText("")
      pass
  
  def init_database(self):
    import sqlite3
    storage_dir = qt.QStandardPaths.writableLocation(qt.QStandardPaths.GenericDataLocation)
    target_path = f'{storage_dir}/paaa'
    if not os.path.exists(target_path):
      os.mkdir(target_path)
    dbpath = os.path.join(target_path,"user_data.db")
    # 创建数据库连接
    self.conn = sqlite3.connect(dbpath)
    self.cursor = self.conn.cursor()

    # 创建用户表格
    self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            permission INTEGER DEFAULT 0,
            registration_time TEXT,
            last_login_time TEXT,
            md5 TEXT
        )
    ''')
    self.conn.commit()
    
    # 创建用户表格
    self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS cache_user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            cache TEXT NOT NULL
        )
    ''')
    self.conn.commit()

    self.cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT NOT NULL UNIQUE,
                      password TEXT NOT NULL,
                      remember_password INTEGER,
                      show_password INTEGER,
                      agree_protocol BOOLEAN
                      )''')
    
    # 提交更改并关闭连接
    self.conn.commit()
    
  def get_widget(self):
    return self.ui.JLoginContainer
  
  def get_md5_value(self, value_list):
    tmp_str = ",".join(value_list)
    input_byte = bytes(tmp_str, 'utf-8')
    hash_object = qt.QCryptographicHash(qt.QCryptographicHash.Md5)
    hash_object.addData(input_byte)
    result = hash_object.result().toHex().data().decode('utf-8')
    return result
  
  def show_error(self,text):
    self.ui.r_error_text.setText(text)
    self.ui.r_error_text_2.setText(text)
    if hasattr(self.ui, 'r_error_text_4'):
      self.ui.r_error_text_4.setText(text)
  
  
  
  def on_do_login(self):
    print("on do login")
    user_name = self.ui.l_username.text
    password1 = self.ui.l_password.text
    
    if len(user_name) == 0 or len(password1) == 0:
      util.showWarningText("用户名或者密码为空")
      return False

    if not self.is_valid_username(user_name):
      util.showWarningText("用户名非法")
      return False

    error_info_tmp = "" 
    if self.login_agreement == "2" and self.login_privacy == "2":
      error_info_tmp = "请阅读并同意服务协议和隐私政策"
    elif self.login_agreement == "2":
      error_info_tmp = "请阅读并同意服务协议"
    elif self.login_privacy == "2":
      error_info_tmp = "请阅读并同意隐私政策"
    if error_info_tmp != "" and not self.ui.checkUserAgreement.checked:
      util.showWarningText(error_info_tmp)
      return False
    isSucceed,info=util.httplib.login_to_server(user_name,password1)
    if not isSucceed:
      if info == -999:
        self.show_error("当前无法连接到服务器")
        return
        self.login_offline(user_name,password1)
      else:
        self.show_error(info)
    else:
      self.show_error("")
      if self.ui.l_cb_remember_password.isChecked():
        remember_password = 1
      else:
        remember_password = 0
        
      if self.ui.l_cb_show_password.isChecked():
        show_password = 1
      else:
        show_password = 0
      self.cursor.execute('''SELECT * FROM settings LIMIT 1''')
      result = self.cursor.fetchone()
      if result:           
        sql1 = f"UPDATE settings set username='{user_name}',password='{password1}',remember_password='{remember_password}',show_password='{show_password}' where id='{result[0]}"
        print("login sql:",sql1)
        self.cursor.execute('UPDATE settings set username=?, password=?, remember_password=?, show_password=? WHERE id = ?', (user_name, password1, remember_password,show_password,result[0]))
        self.conn.commit()
      else:
        self.cursor.execute('Insert into settings (username, password, remember_password, show_password) VALUES (?, ?, ?, ?)', (user_name, password1, remember_password,show_password))
        self.conn.commit()
      util.send_event_str(util.FrameworkTopRefreshCache)
      util.send_event_str(util.FrameworkTopLoginSucceed)
      util.showSuccessText("登录成功")
      if self.login_dialog:
        self.login_dialog.close()
        self.login_dialog = None
    return
  
  def login_offline(self,user_name,password1):
    # 查询用户信息
    self.cursor.execute('SELECT id, username, password, permission, registration_time, last_login_time, md5 FROM users WHERE username = ?', (user_name,))
    user_data = self.cursor.fetchone()

    if user_data:
      #管理员
        
      # 用户名存在，验证密码
      _, self.username, stored_password, self.permission, registration_time, last_login_time, md5 = user_data
      if stored_password == password1:
        if int(user_data[3]) == 0 :
          self.show_error("")
          self.ui.tabWidget.setCurrentIndex(3)
        else:
          login_info = [self.username, stored_password, str(self.permission), registration_time, last_login_time]
          md5_value = self.get_md5_value(login_info)
          self.show_error("")
          if md5 != md5_value:
            self.show_error("md5验证失败,数据被篡改")
            return False
          else:
            from datetime import datetime
            login_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            login_info[4] = login_time
            md5_value = self.get_md5_value(login_info)
            self.cursor.execute('UPDATE users set last_login_time=?, md5=? WHERE username = ?', (login_time, md5_value, user_name))
            return True
      else:
        return False
    else:
        return False

  
  def on_modify_password(self):
    user_name = self.ui.r_username_3.text
    password1 = self.ui.r_password_5.text
    password2 = self.ui.r_password_3.text
    if user_name == "":
      self.show_error("请输入用户名")
      return
    if not self.is_valid_username(user_name):
      return
    if password1 == "":
      self.show_error("请输入密码")
      return
    if password2 == "":
      self.show_error("请输入重复密码")
      return
    if password1 != password2:
      self.show_error("两次输入的密码不一样")
      return
    if not self.is_valid_password(password1,user_name):
      return
    self.show_error("")
    util.showWarningText("修改成功")
    self.ui.tabWidget.setCurrentIndex(0)

  def is_valid_phone(self, phone_number):
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone_number) is not None
    pass

  def on_do_register(self):
    user_name = self.ui.r_username.text
    password1 = self.ui.r_password_1.text
    password2 = self.ui.r_password_2.text
    phone = self.ui.r_phone.text
    address = self.ui.r_address.text
    if not self.is_valid_phone(phone):
      self.show_error("请输入正确的11位手机号")
      return
    if user_name == "":
      self.show_error("请输入用户名")
      return
    if not self.is_valid_username(user_name):
      return
    if password1 == "":
      self.show_error("请输入密码")
      return
    if password2 == "":
      self.show_error("请输入重复密码")
      return
    if address == "":
      self.show_error("请输入地址")
      return
    if password1 != password2:
      self.show_error("两次输入的密码不一样")
      return
    if not self.is_valid_username(user_name):
      self.show_error("用户名非法")
      return
    if not self.register_user(user_name,password1):
      return
    login_auth = util.getjson("login_auth",0)
    if login_auth == 2:
      flag,message = util.httplib.register_to_server(user_name,password1,phone,address)
      if not flag:
        self.show_error(message)
        return
    self.show_error("")
    util.showWarningText("注册成功")
    self.ui.l_username.setText(user_name)
    self.ui.l_password.setText(password1)
    self.ui.l_cb_show_password.setChecked(True)
    self.on_return_to_login()


  def register_user(self,username, password):
    from datetime import datetime
    # 检查用户名是否已经存在
    self.cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    existing_user = self.cursor.fetchone()

    # if existing_user:
    #     self.show_error("用户名已经存在")
    #     return False

    # 获取当前时间作为注册时间
    registration_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 插入新用户信息
    sign_up_list = [username, password, str(1), registration_time, registration_time]
    md5_value = self.get_md5_value(sign_up_list)
    self.cursor.execute('INSERT INTO users (username, password, permission, registration_time, last_login_time, md5) VALUES (?, ?, ?, ?, ?, ?)', (username, password, 1, registration_time, registration_time, md5_value))
    res = self.conn.commit()
    print("User registered successfully.",res)
    return True

  def is_valid_username(self, username):
    limit_type = util.getjson2("Global","username_limit",default_value="0")
    print("limit_type", limit_type)
    if limit_type != "2":
      return True
    # 长度限制：设置用户名最小和最大长度为6和20
    if len(username) < 6 or len(username) > 20:
      self.show_error("用户名限制在4到20个字符之内")
      return False
    
    # 字符限制：用户名只能包含字母、数字和下划线
    if not username.isalnum():
      self.show_error("用户名只能包含字母、数字")
      return False
    
    # # 禁止纯数字或纯字母用户名
    if username.isdigit() or username.isalpha():
      self.show_error("用户名不能是纯字母或者数字")
      return False

    # 敏感词过滤：检查用户名中是否包含敏感词
    sensitive_words = ["admin", "root", "password", "123456"]
    if any(word in username.lower() for word in sensitive_words):
      self.show_error("用户名不能包含敏感词")
      return False

    # 唯一性检查：确保用户名在系统中是唯一的
    if username.lower() in self.registered_usernames:
      self.show_error("已注册过该用户")
      return False

    return True
  
  def on_register(self):
    self.ui.tabWidget.setCurrentIndex(1)

  def on_return_to_login(self):
    self.ui.tabWidget.setCurrentIndex(0)
    
  def on_click_privacy(self):
    agreement_file = "text/privacy2.txt"
    file_path = self.resourcePath(agreement_file)
    util.getModuleWidget("JMessageBox").show_pop_window("隐私条款", file_path, 700, 600)

  def on_click_agreement(self):
    agreement_file = "text/agreement2.txt"
    file_path = self.resourcePath(agreement_file)
    util.getModuleWidget("JMessageBox").show_pop_window("服务协议", file_path, 700, 600)
  
  def _message_box_path(self,file_path,title):
    content = "empty content"
    with open(file_path, "r") as file:
       content = file.read()

    #icon_path = self.resourcePath('Icons/ticon.png')
    #pixelmap = qt.QPixmap(icon_path)
    msg_box = qt.QMessageBox()
    #dialog.SetTitle("服务协议")
    msg_box.setWindowTitle(title)
    #msg_box.setIconPixmap(pixelmap)
    text_widget = qt.QWidget()
    text_layout = qt.QVBoxLayout(text_widget)
    
    scroll_area = qt.QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setHorizontalScrollBarPolicy(qt.Qt.ScrollBarAlwaysOff)
    
    text_label = qt.QLabel()
    text_label.setWordWrap(True)
    
    scroll_area.setWidget(text_label)
    
    text_layout.addWidget(scroll_area)
    text_widget.setLayout(text_layout)
    
    msg_box.layout().addWidget(text_widget)
    text_widget.setFixedSize(600,800)
    msg_box.setFixedSize(600,800)
    text_label.setText(content)
    msg_box.exec()