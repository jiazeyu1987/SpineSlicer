def get_database_name():
    import slicer.util as util
    import os
    sqlname = "data.sql"
    absolute_file_path = os.path.abspath(__file__)
    sql_directory = os.path.dirname(os.path.dirname(os.path.join(absolute_file_path,util.username).replace('\\','/')))
    sql_directory = os.path.join(sql_directory,util.username)
    if not os.path.exists(sql_directory):
        os.makedirs(sql_directory)
    print("sql_directory",sql_directory)
    sql_path = os.path.join(sql_directory,sqlname).replace('\\','/')
    return sql_path

def get_globaldb_name():
    import slicer.util as util
    import os
    sqlname = "gloabal_data.sql"
    absolute_file_path = os.path.abspath(__file__)
    sql_directory = os.path.dirname(os.path.dirname(os.path.join(absolute_file_path,util.username).replace('\\','/')))
    if not os.path.exists(sql_directory):
        os.makedirs(sql_directory)
    print("global sql_directory",sql_directory)
    sql_path = os.path.join(sql_directory,sqlname).replace('\\','/')
    return sql_path


def connect_to_globaldb():
    import slicer.util as util
    import slicer,sqlite3,os
    sql_path = get_globaldb_name()
    if not os.path.exists(sql_path):
      dicomBrowser = slicer.modules.dicom.widgetRepresentation().self().browserWidget.dicomBrowser
      dicomDatabase = dicomBrowser.database()
      dicomDatabase.openDatabase(sql_path)
      print("open gloabl sql path:",sql_path)
    # 连接到数据库
    conn = sqlite3.connect(sql_path)
    # 创建一个游标对象，用于执行 SQL 语句
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS GlobalSettings (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            solution_name TEXT,
            md5 TEXT,
            cache TEXT ,
            cache_user_name TEXT ,
            cache_session TEXT ,
            version TEXT 
        );
    ''')

def connect_to_database():
    import slicer.util as util
    import slicer,sqlite3,os
    sql_path = get_database_name()
    if not os.path.exists(sql_path):
      dicomBrowser = slicer.modules.dicom.widgetRepresentation().self().browserWidget.dicomBrowser
      dicomDatabase = dicomBrowser.database()
      dicomDatabase.openDatabase(sql_path)
      print("open sql path:",sql_path)
    # 连接到数据库
    slicer.dicomDatabase.openDatabase(sql_path)
    conn = sqlite3.connect(sql_path)
    # 创建一个游标对象，用于执行 SQL 语句
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Analysis (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            solution_name TEXT,
            str_para1 TEXT ,
            str_para2 TEXT ,
            str_para3 TEXT ,
            int_para1 INTEGER ,
            int_para2 INTEGER ,
            int_para3 INTEGER ,
            pathlist TEXT,
            remark TEXT,
            cover BLOB,
            recordtime DATETIME,
            modifytime DATETIME
        );
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CombinInfo (
            PatientID INTEGER,
            NewPatientID INTEGER,
            StudyUID VARCHAR(64) UNIQUE
        );
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS UserInfo (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            vip_level INTEGER,
            expiration_time TEXT
        );
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SolutionInformations (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            solution_name TEXT,
            solution_hard INTEGER,
            score INTEGER,
            recordtime DATETIME,
            modifytime DATETIME
        );
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS UserSettings (
            ID INTEGER PRIMARY KEY AUTOINCREMENT
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS UserScore (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            score TEXT
        );
    ''')

def refresh_local_score(data):
    import os,sqlite3
    import slicer.util as util
    import datetime
    database_path = get_database_name()
    if os.path.exists(database_path):
        # 连接到数据库
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute("delete from UserScore")
        cursor.executemany('INSERT INTO UserScore (score) VALUES (?)', [(item,) for item in data])
        conn.commit()
        cursor.close()
        conn.close()

def get_score_list():
    import os,sqlite3
    import slicer.util as util
    import datetime
    database_path = get_database_name()
    if os.path.exists(database_path):
        # 连接到数据库
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute("select score from UserScore")
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    return None

def user_exist_in_database(patientname):
    import os,sqlite3
    database_path = get_database_name()
    if os.path.exists(database_path):
        # 连接到数据库
        conn = sqlite3.connect(database_path)
        print(database_path)
        cursor = conn.cursor()
        sql1 = f"SELECT ID, vip_level, expiration_time FROM UserInfo where patient_name = '{patientname}'"
        cursor.execute(sql1)
        res = cursor.fetchone()
        if res == None:
            return False
        else:
            return True
    return False

def get_user_viplevel(patientname):
    if patientname == '游客':
        return 0
    import os,sqlite3
    import slicer.util as util
    import datetime
    database_path = get_database_name()
    if os.path.exists(database_path):
        # 连接到数据库
        conn = sqlite3.connect(database_path)
        print(database_path)
        cursor = conn.cursor()
        sql1 = f"SELECT ID, vip_level, expiration_time FROM UserInfo where patient_name = '{patientname}'"
        cursor.execute(sql1)
        res = cursor.fetchone()
        if res == None:
            #-1代表有缓存没有数据库信息
            return -1
        vip_level = int(res[1])
        if True:
            print("lllllllllllllllllllllllll",util.is_connect_internet)
            if util.is_connect_internet == False:
                conn.close()
                return 0
            time_format = "%a, %d %b %Y %H:%M:%S GMT"
            parsed_time = datetime.datetime.strptime(res[2], time_format)
            # 将解析的时间转换为 UTC，因为 GMT 与 UTC 在现代基本是等同的
            current_utc_time = datetime.datetime.utcnow()
            offset = datetime.timedelta(hours=8)
            beijing_time = current_utc_time + offset
            # 比较时间
            print("oooooooooooooooooooooooooooo:", beijing_time, parsed_time)
            if beijing_time > parsed_time:
                return 0
            else:
                print("当前 UTC 时间小于或等于指定时间")
                return 1
        if res:
            conn.close()
            return vip_level
        else:
            conn.close()
            return 0

def save_to_user_db(key,value):
  pass

def save_to_global_db(key,value):
    print("save_to_global_db",key,value)
    import os,sqlite3
    import slicer.util as util
    connect_to_globaldb()
    database_path = get_globaldb_name()
    
    if os.path.exists(database_path):
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        sql1 = "SELECT * from GlobalSettings"
        cursor.execute(sql1)
        res = cursor.fetchone()
        if not res:
            cursor.execute('INSERT INTO GlobalSettings (solution_name, version) VALUES (?, ?)', ("UnitPunctureGuide", "1.0.0"))
            conn.commit()
        
        cursor.execute("SELECT * from GlobalSettings")
        res = cursor.fetchone()
        sql2 = f"UPDATE UserInfo set {key}='{value}' where ID='{res[0]}'"
        # 连接到数据库
        cursor.execute(sql2)
        conn.commit()
    conn.close()

def get_from_user_db(key,value):
    pass

def get_from_global_db(key,value=None):
    import os,sqlite3
    import slicer.util as util
    connect_to_globaldb()
    database_path = get_globaldb_name()
    
    if os.path.exists(database_path):
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        sql1 = f"SELECT {key} from GlobalSettings"
        cursor.execute(sql1)
        res = cursor.fetchone()
        if res:
            return res[0]
    return value
        

def set_user_viplevel(patientname,level, exp_time):
    import os,sqlite3
    import slicer.util as util
    database_path = get_database_name()
    if os.path.exists(database_path):
        # 连接到数据库
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        sql1 = f"SELECT ID,vip_level,expiration_time FROM UserInfo where patient_name = '{patientname}'"
        cursor.execute(sql1)
        res = cursor.fetchone()
        if res:
            sql2 = f"UPDATE UserInfo set vip_level='{level}', expiration_time='{exp_time}' where ID='{res[0]}'"
            print(sql2)
            cursor.execute(sql2)
            conn.commit()
        else:
            from datetime import datetime
            cursor.execute('INSERT INTO UserInfo (patient_name, vip_level, expiration_time) VALUES (?, ?, ?)', (patientname, level, exp_time))
            conn.commit()
        conn.close()

def add_score(patientname,solution_name,hard):
    import os,sqlite3
    import slicer.util as util
    database_path = get_database_name()
    if os.path.exists(database_path):
        # 连接到数据库
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        sql1 = f"SELECT ID,score FROM SolutionInformations where patient_name = '{patientname}' and solution_name = '{solution_name}' and solution_hard = '{hard}' ORDER BY recordtime DESC"
        print("----------------",sql1)
        cursor.execute(sql1)
        res = cursor.fetchone()
        print(res)
        if res:
            score = int(res[1])+1
            sql2 = f"UPDATE SolutionInformations set score='{score}' where ID='{res[0]}'"
            print(sql2)
            cursor.execute(sql2)
            conn.commit()
        else:
            from datetime import datetime
            cursor.execute('INSERT INTO SolutionInformations (patient_name, solution_name, solution_hard, score, recordtime, modifytime) VALUES (?, ?, ?, ?, ?, ?)', (patientname, solution_name, hard, 1, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
        # 关闭连接
        conn.close()
        
def get_score(patientname,solution_name,hard):
    import os,sqlite3
    import slicer.util as util
    database_path = get_database_name()
    if os.path.exists(database_path):
        # 连接到数据库
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        sql1 = f"SELECT ID,score FROM SolutionInformations where patient_name = '{patientname}' and solution_name = '{solution_name}' and solution_hard = '{hard}' ORDER BY recordtime DESC"
        print("----------------",sql1)
        cursor.execute(sql1)
        res = cursor.fetchone()
        if res:
            return int(res[1])
    return 0
    

def get_all_analyse_info():
    import os,sqlite3
    import slicer.util as util
    database_path = get_database_name()
    if os.path.exists(database_path):
        # 连接到数据库
        conn = sqlite3.connect(database_path)
        # 创建一个游标对象，用于执行 SQL 语句
        cursor = conn.cursor()
        sql1 = f"SELECT ID,solution_name,pathlist,cover,recordtime FROM Analysis where patient_name = '{util.username}' ORDER BY recordtime DESC"
        print("----------------",sql1)
        cursor.execute(sql1)
        items_list = cursor.fetchall()
        return items_list
    return []
        
def save_analyse_info(image_path,filepath):
    import os,sqlite3
    from datetime import datetime
    import slicer.util as util
    database_path = get_database_name()
    if os.path.exists(database_path):
      with open(image_path, 'rb') as file:
        blob_data = file.read()
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Analysis (patient_name, solution_name,pathlist,cover,recordtime,modifytime) VALUES (?, ?,?,?,?,?)', (util.username,util.solution_name,filepath,blob_data,datetime.now(),datetime.now()))
        conn.commit()
        # 关闭连接
        conn.close()
        
def remove_analyse(id1):
    import os,sqlite3
    database_path = get_database_name()
    if os.path.exists(database_path):
        # 连接到数据库
        conn = sqlite3.connect(database_path)
        # 创建一个游标对象，用于执行 SQL 语句
        cursor = conn.cursor()
        cursor.execute(f'DELETE FROM Analysis WHERE ID = ?', (id1,))

        # 提交更改
        conn.commit()

        # 关闭游标和连接
        cursor.close()
        conn.close()