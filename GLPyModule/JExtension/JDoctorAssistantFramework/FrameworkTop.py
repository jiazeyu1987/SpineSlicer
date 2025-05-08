import slicer,qt,vtk,ctk
import slicer.util as util
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from Base.JBaseExtension import JBaseExtensionWidget
import numpy as np
#
# FrameworkTop
#


class FrameworkTop(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "FrameworkTop"  # TODO: make this more human readable by adding spaces
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
# FrameworkTopWidget
#

class FrameworkTopWidget(JBaseExtensionWidget):
  logindlg = None
  update_timer = None
  version = ""
  version_file = ""
  first_init = None
  def setup(self):
    super().setup()
    if util.curr_language == 1:
      self.ui.btnClear.setMinimumWidth(86)
      self.ui.btnSetting.setMinimumWidth(98)
      self.ui.pushButton_9.setMinimumWidth(70)
      self.ui.pushButton_2.setMinimumWidth(70)
      self.ui.pushButton_3.setMinimumWidth(70)
    #self.ui.pushButton.connect('clicked()',self.on_show_menu)
    self.ui.btnSwitch.connect('clicked()',self.on_show_menu)
    #self.ui.btnLanguage.connect('clicked()',self.on_switch_language)
    self.ui.pushButton_9.connect('clicked()',self.on_update_version)
    self.ui.lblInfo.setAttribute(qt.Qt.WA_TransparentForMouseEvents, True)
    self.ui.lblIcon.setAttribute(qt.Qt.WA_TransparentForMouseEvents, True)
    print("FrameworkTopWidget")
    self.TagMaps[util.FrameworkTopRefreshCache] = slicer.mrmlScene.AddObserver(util.FrameworkTopRefreshCache, self.OnFrameworkTopRefreshCache)
    self.TagMaps[util.FrameworkTopNeedUpdate] = slicer.mrmlScene.AddObserver(util.FrameworkTopNeedUpdate, self.OnFrameworkTopNeedUpdate)
    self.TagMaps[util.FrameworkTopLoginSucceed] = slicer.mrmlScene.AddObserver(util.FrameworkTopLoginSucceed, self.OnFrameworkTopLoginSucceed)
    self.TagMaps[util.AddSolutionScore] = slicer.mrmlScene.AddObserver(util.AddSolutionScore, self.OnAddSolutionScore)
    self.TagMaps[util.UpdateVIPTime] = slicer.mrmlScene.AddObserver(util.UpdateVIPTime, self.OnUpdateVip)
    self.TagMaps[util.UpdateTitle] = slicer.mrmlScene.AddObserver(util.UpdateTitle, self.update_title2)
    self.TagMaps[util.SaveSolution] = slicer.mrmlScene.AddObserver(util.SaveSolution, self.save_solution)
    self.ui.pushButton_5.connect('clicked()',self.on_test1)
    self.update_timer = qt.QTimer()
    self.update_timer.connect('timeout()', self.display_update_note)
    need_update = util.get_from_PAAA("need_update","0")
    if need_update == "1":
      self.OnFrameworkTopNeedUpdate("","")
    test_module = util.getjson2("Global","test_module",default_value="0")
    if test_module != "2":
      self.ui.btnData.hide()
      self.ui.pushButton_4.hide()
      self.ui.pushButton_5.hide()      
    else:      
      util.mainWindow().setNeedConfirm(False)
    self.update_timer.start(1000)
    self.create_setting_menu()

  def create_setting_menu(self):    
    menu = qt.QMenu(self.ui.btnSetting)
    self.ui.btnSetting.setMenu(menu)
    menu.addAction(util.tr("语言设置"), self.on_set_language)
    pass

  def on_set_language(self):
    dialog = util.getModuleWidget("JMessageBox").on_popup_ui_dialog(util.tr("语言设置"),util.getModuleWidget("FrameworkLanguage").get_widget(), 700, 450)
    util.getModuleWidget("FrameworkLanguage").set_dialog(dialog)
    dialog.exec_()
    pass

  def display_update_note(self):
    if self.version == "":
      return
    util.show_update_reminder(self.version, self.version_file)  
    self.version = ""
    self.update_timer.stop()

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def OnUpdateVip(self,caller,str_event,calldata):
    val = calldata.GetAttribute("value")
    from FrameworkLib.datas import fdb
    util.is_connect_internet = util.is_internet_connect()

    fdb.set_user_viplevel(util.username,'1', val)
    self.ui.label_2.setText(util.username+"(VIP)")
    self.ui.label_2.setStyleSheet("color:yellow;font:14px;")
    self.ui.pushButton_6.setVisible(False)

  def on_test1(self):
    slicer.util.reloadScriptedModule("UnitCTMask")
    return
    # util.loadScene("D:/save.mrb")
    # util.singleShot(1000,self.on_test2)
    
    
    # from FrameworkLib import printer3dlib
    # modelnode = util.getFirstNodeByName("导板")
    # if not modelnode:
    #   util.showWarningText("111111111")
    #   return
    # tmp_path = self.resourcePath('Data/puncture_guide.stl')
    # gcode_path = self.resourcePath('Data/puncture_guide.gcode')
    # util.saveNode(modelnode,tmp_path)
    # util.saveNode(modelnode,self.resourcePath('Data/A1111.stl'))
    # printer3dlib.run(tmp_path,gcode_path)
    tmp_path = self.resourcePath('Data/puncture_guide.stl')
    gcode_path = self.resourcePath('Data/puncture_guide.gcode')
    self.run(tmp_path,gcode_path)
    return
    import os
    if os.path.exists(tmp_path):
      os.remove(tmp_path)
    if os.path.exists(gcode_path):
      os.remove(gcode_path)
    
    planet = [300,300,300]
    
    from FrameworkLib import printer3dlib
    modelnode = util.getFirstNodeByName("导板2")
    if  modelnode:
      util.RemoveNode(modelnode)
      
    cloned_node = util.clone(util.getFirstNodeByName("导板"))
    cloned_node.SetName("导板2")
    modelnode = cloned_node
    modelnode.HardenTransform()
    
    EntryPoint = util.getFirstNodeByName("EntryPoint")
    TargetPoint = util.getFirstNodeByName("TargetPoint")
    entry_world = util.get_world_position(EntryPoint)
    target_world = util.get_world_position(TargetPoint)
    
    length = float(EntryPoint.GetAttribute("length_slider"))
    self.rotate_fiber_model_to_vector(modelnode,entry_world,target_world,100)
    
    outputVolumeSpacingMm = [0.5, 0.5, 0.5]
    outputVolumeMarginMm = [10.0, 10.0, 10.0]
    import math
    import numpy as np
    bounds = np.zeros(6)
    center = np.zeros(3)
    modelnode.GetBounds(bounds)
    modelnode.GetMesh().GetCenter(center)
    imageData = vtk.vtkImageData()
    imageSize = [ int((bounds[axis*2+1]-bounds[axis*2]+outputVolumeMarginMm[axis]*2.0)/outputVolumeSpacingMm[axis]) for axis in range(3) ]
    imageOrigin = [ bounds[axis*2]-outputVolumeMarginMm[axis] for axis in range(3) ]
    imageData.SetDimensions(imageSize)
    imageData.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
    imageData.GetPointData().GetScalars().Fill(0)

    
    
    
    
    
    transformToParentMatrix = vtk.vtkMatrix4x4()
    handleToParentMatrix=vtk.vtkTransform()
    handleToParentMatrix.PostMultiply()
    handleToParentMatrix.Translate(-center[0], -center[1], -center[2])
    transformToParentMatrix.DeepCopy(handleToParentMatrix.GetMatrix())
    transform_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
    transform_node.SetMatrixTransformToParent(transformToParentMatrix)
    modelnode.SetAndObserveTransformNodeID(transform_node.GetID())
    modelnode.HardenTransform()

    
   
    
    util.saveNode(modelnode,tmp_path)
    self.run(tmp_path,gcode_path)
    
    
    vector1 = [target_world[0]-entry_world[0],target_world[1]-entry_world[1],target_world[2]-entry_world[2]]
    tdk = math.sqrt(vector1[0]*vector1[0] + vector1[1]*vector1[1] + vector1[2]*vector1[2])
    vector2 = [vector1[0]/tdk*length,vector1[1]/tdk*length,vector1[2]/tdk*length]
    tdk_point = [target_world[0]-vector2[0]-center[0],target_world[1]-vector2[1]-center[1],target_world[2]-vector2[2]-center[2]]
    #util.showWarningText(f"entry:{entry_world[0]},{entry_world[1]},{entry_world[2]}\ntarget:{target_world[0]},{target_world[1]},{target_world[2]}\nentry:{entry_world[0]-center[0]},{entry_world[1]-center[1]},{entry_world[2]-center[2]}\ntarget:{target_world[0]-center[0]},{target_world[1]-center[1]},{target_world[2]-center[2]}")

    
    
  def run(self,stl_path,gcode_path):
    import subprocess

    import os
    from stl import mesh
    import numpy as np

    
    # 读取STL文件
    your_mesh = mesh.Mesh.from_file(stl_path)

    # 计算模型的尺寸
    minx, maxx, miny, maxy, minz, maxz = np.inf, -np.inf, np.inf, -np.inf, np.inf, -np.inf
    for v in your_mesh.vectors:
        minx = min(minx, v[:,0].min())
        maxx = max(maxx, v[:,0].max())
        miny = min(miny, v[:,1].min())
        maxy = max(maxy, v[:,1].max())
        minz = min(minz, v[:,2].min())
        maxz = max(maxz, v[:,2].max())

    # 计算需要移动的距离以将模型中心移至原点
    move_x = -(minx + (maxx - minx) / 2)
    move_y = -(miny + (maxy - miny) / 2)
    move_z = -minz  # 通常 Z 轴不需要调整，除非需要模型底部与打印平台表面对齐

    # 更新模型的位置
    your_mesh.translate([move_x, move_y, move_z])

    # 保存修改后的STL文件
    your_mesh.save(stl_path)

    project_path = slicer.app.applicationDirPath()
    
    # 设置CuraEngine的路径
    cura_engine_path = project_path+'/UltiMakerCura/CuraEngine'

    # STL文件的路径
    stl_file = stl_path

    # 输出G-code文件的路径
    gcode_file = gcode_path
    import os
    # 配置文件的路径
    #config_file = project_path+'/UltiMakerCura/resources/definitions/ultimaker_s4.def.json'
    config_file = project_path+'/UltiMakerCura/resources/definitions/xiaoluban1.json'
    # 构建命令行命令
    command = [
      cura_engine_path,
      'slice',
      '-v',
      '-p',
      '-s', 'support_enable=true',
      '-s', 'roofing_layer_count=3',
      '-j', config_file,  # 加载配置文件
      '-l', stl_file,  # 加载STL文件
      '-o', gcode_file  # 输出G-code文件
    ]

    # 调用CuraEngine
    result = subprocess.run(command, capture_output=True, encoding='utf-8', text=True)
    print("===============================================================================================")
    print("===============================================================================================")
    print(result.stdout)
  
  
  def rotate_fiber_model_to_vector(self,model_node,m_PointInput,m_PointTarget,length):
    length = length/2
    half_vector = (np.array(m_PointInput) - np.array(m_PointTarget))/2
    half_vector_len = np.sqrt(half_vector[0]*half_vector[0]+half_vector[1]*half_vector[1]+half_vector[2]*half_vector[2])

    transformToParentMatrix = vtk.vtkMatrix4x4()

    rotationVector_Local = np.array([0,0,0])
    vector1 = np.array(m_PointInput) - np.array(m_PointTarget)
    vector0 = np.array([0,0,1])
    angle = vtk.vtkMath.DegreesFromRadians(vtk.vtkMath.AngleBetweenVectors(vector0,vector1))
    vtk.vtkMath.Cross(vector0, vector1, rotationVector_Local)
    handleToParentMatrix=vtk.vtkTransform()
    handleToParentMatrix.PostMultiply()
    handleToParentMatrix.Translate(-m_PointTarget[0], -m_PointTarget[1], -m_PointTarget[2])
    handleToParentMatrix.RotateWXYZ(angle, rotationVector_Local)
    handleToParentMatrix.Translate(m_PointTarget[0]+half_vector[0]*length/half_vector_len,m_PointTarget[1]+half_vector[1]*length/half_vector_len,m_PointTarget[2]+half_vector[2]*length/half_vector_len)
    transformToParentMatrix.DeepCopy(handleToParentMatrix.GetMatrix())

    transform_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
    transform_node.SetMatrixTransformToParent(transformToParentMatrix)
    model_node.SetAndObserveTransformNodeID(transform_node.GetID())
    model_node.HardenTransform()
    
  def on_test2(self):
    seg = util.getFirstNodeByName("teaching_data2 segmentation")
    util.color_unit_list.add_item(seg)
  
  def OnAddSolutionScore(self,a,b):
    solution_name = util.get_cache_from_PAAA("sub_solution","UnitPunctureGuide")
    hard = util.get_cache_from_PAAA("sub_solution_hard","1")
    patientname = util.username
    from FrameworkLib.datas import fdb
    fdb.add_score(patientname,solution_name,hard)
    self.update_title()
    
  def update_title2(self,a,b):
    self.update_title()

  def save_solution(self, a, b):
    self.on_save()

  def update_title(self):
    print("update_title")
    sub_project_alias_name = util.get_cache_from_PAAA("sub_project_alias_name","穿刺导板")
    solution_name = util.get_cache_from_PAAA("sub_solution","UnitPunctureGuide")
    hard = util.get_cache_from_PAAA("sub_solution_hard","1")
    patientname = util.username
    from FrameworkLib.datas import fdb
    score = fdb.get_score(patientname,solution_name,hard)
    hardstr = str(hard)
    if hardstr in util.teacher_info:
      data = util.teacher_info[hardstr]
      teacher_name = data['doctor_name']
      self.ui.lblInfo.setText(f"{sub_project_alias_name}({teacher_name})-[次数：{score}]")
    self.ui.lblInfo.setText("全息脑出血方体定位系统")
    self.ui.widget_6.setVisible(False)
    self.ui.btnSetting.setVisible(False)
    self.ui.pushButton_9.setVisible(False)
    self.ui.pushButton_2.setVisible(False)
    self.ui.lbl_icon.setVisible(False)
    self.ui.lblIcon.setVisible(False)
  
  def OnFrameworkTopLoginSucceed(self,_a,_b):
    if not self.logindlg:
      return
    self.logindlg.accept()
  
  def set_style(self,style):
    if style == "simple":
      self.ui.btnLoad.setEnabled(False)
      self.ui.btnClear.setEnabled(False)
      self.ui.btnSave.setEnabled(False)
    else:
      self.ui.btnLoad.setEnabled(True)
      self.ui.btnClear.setEnabled(True)
      self.ui.btnSave.setEnabled(True)
  
  def on_update_version(self):
    need_update = util.get_from_PAAA("need_update",default="0")
    if need_update== "1":
      import os,json,shutil
      framework_version = util.get_from_PAAA("version")
      solution_name = util.get_cache_from_PAAA("solution_name",default="UnitPunctureGuide")
      jextension_file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
      config_path = os.path.join(jextension_file_path,solution_name,"Resources","config.ini")
      setting_obj = qt.QSettings(config_path,qt.QSettings.IniFormat)
      solution_version = util.settingsValue("VERSION/version","1.0.0",settings=setting_obj)
      print("version:",framework_version,solution_version)
      json1 = {}
      json1['deptId'] = framework_version
      isSucceed,val = util.httplib.httpget("/system/info/update_to_current_version",json1,need_login=False)
      print('on_update_version:',isSucceed,val)
      if isSucceed:
        msg = val['msg']
        if msg['framework'].strip()=="":
          util.showWarningText("当前已经是最新的版本")
          util.save_to_PAAA("need_update","0")
          return
        framework_file_list = msg['framework'].split(",")
        #solution_file = msg['solution']
        #solution_name = msg['solution_name']
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        #prepare progress
        count = 0
        step = int(100/(len(framework_file_list)+1))
        util.send_event_str(util.ProgressStart,"正在更新")
        util.send_event_str(util.ProgressValue,count)
        
        #update solution 
        solution_path = os.path.join(base_path,"version","solution")
        if os.path.exists(solution_path):
          shutil.rmtree(solution_path)
        os.makedirs(solution_path)  
        #util.httplib.download_zip(os.path.join(solution_path,os.path.basename(solution_file)),solution_file)
        count+=step
        util.send_event_str(util.ProgressValue,count)
        
        #update framework
        framework_path = os.path.join(base_path,"version","framework")
        if os.path.exists(framework_path):
          shutil.rmtree(framework_path)
        os.makedirs(framework_path)
        if len(framework_file_list)>0:
          for frameworkpack in framework_file_list:
            util.httplib.download_zip(os.path.join(framework_path,os.path.basename(frameworkpack)),frameworkpack)
            count+=step
            util.send_event_str(util.ProgressValue,count)

        #finished
        self.ui.pushButton_9.setText("重启更新")
        stylesheet = self.ui.pushButton_9.styleSheet
        stylesheet += "background-color: rgb(189, 0, 0);"
        self.ui.pushButton_9.setStyleSheet(stylesheet)
        util.send_event_str(util.ProgressValue,100)
        util.save_to_PAAA("need_update","2")
        self.ui.pushButton_9.animateClick(0)
      else:
        self.show_error(val)
    elif need_update == "0":
      util.showWarningText("当前已经是最新的版本")
      return
    else:
      res = util.messageBox(f"重启软件可以浏览最新内容，是否现在开始重启软甲？")
      if res == 0:
        return
      import subprocess,os
      util.save_to_PAAA("need_update","0")
      filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),"定海神针.exe").replace("\\","/")
      print("restart of file:",filepath)
      subprocess.Popen([filepath])
      slicer.app.quit()
  
  def on_show_menu(self):
    if self.first_init is None:
      self.first_init = 1
      return
    util.send_event_str(util.ProgressStart,util.tr("正在切换方案"))
    util.send_event_str(util.ProgressValue,0)
    util.layout_panel("middle_left").setMaximumWidth(100000)
    util.layout_panel("middle_left").setMinimumWidth(200)
    util.layout_panel("middle_left").setModule("FrameworkMenu")
    slicer.util.findChildren(name="CentralWidget")[0].hide()
    util.send_event_str(util.ProgressValue,30)
    util.send_event_str(util.DoctorAssitButttonResetState)
    util.send_event_str(util.ProgressValue,50)
    util.send_event_str(util.DoctorAssitLeftButttonResetState)
    util.send_event_str(util.ProgressValue,70)
    util.send_event_str(util.DoctorAssitRightButttonResetState)
    util.send_event_str(util.ProgressValue,90)
    util.layout_panel("middle_left").show()
    util.singleShot(0,lambda:util.send_event_str(util.ProgressValue,100))
  
  def show_error(self,val):
    util.showWarningText(val)
  
  def OnFrameworkTopNeedUpdate(self,_a,c):
    import os,sys
    stylesheet = self.ui.pushButton_9.styleSheet
    stylesheet += "background-color: rgb(189, 126, 0);"
    self.ui.pushButton_9.setStyleSheet(stylesheet)
    reminder = util.get_cache_from_PAAA(f"version_{c}_no_more_reminder", 0)
    self.version = ""
    if reminder == 0 or reminder == "0":
      # 获取当前脚本所在的目录
      self.version = c
      base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
      logdir = os.path.join(base_path,"version","log", self.version+".txt").replace("\\", "/")
      qfile = qt.QFile(logdir)
      if not qfile.exists():
        self.version = ""
        return
      self.version_file = logdir
      #不在线程里处理任何UI相关的事情，也不在线程里启动计时器
  
  def OnFrameworkTopRefreshCache(self,_a,c):
    self.refresh_cache()
  
  def on_test_upload_file(self):
     isSucceed,val = util.httplib.httpupload("/system/file/upload_file","D:/save.mrb")
     print("------------------------",isSucceed,val)
  
  
  def on_test_post(self):
     isSucceed,val = util.httplib.httppost("/system/info/update_version_md5",None)
     print("------------------------",isSucceed,val)
  
  def on_test_version(self):
    isSucceed,val = util.httplib.httppost("/system/info/get_version",None)
    if isSucceed:
      util.showWarningText(val)
      value = val['msg']
      version = value['version']
      name = value['name']
      util.mainWindow().setWindowTitle(name+" v"+version)
    else:
      print("httppost error:",val)
    
  def on_test_get(self):
     isSucceed,val = util.httplib.httpget("/system/passport/test_login_get",None)
     print("------------------------",isSucceed,val)
    
  
    
  
    
  def refresh_cache(self):
    from FrameworkLib.datas import fdb
    print("refresh_cache")
    import os
        
    cache_exist,username,session = util.httplib.get_cache()
    util.username= username
    print("refresh_cache value:",cache_exist,username,session)
    if cache_exist:
      
      if fdb.user_exist_in_database(username) == False:
        self.ui.label_2.setText(util.tr("游客"))
        self.ui.pushButton_3.setText(util.tr("登录"))
        self.ui.label_2.setStyleSheet("color:white;font:14px;")
        util.username= "游客"
        self.ui.pushButton_6.setVisible(False)
        fdb.connect_to_database()
        util.send_event_str(util.ClearPatientInfo)
        self.on_login_logout()
        return
    
    
      self.ui.pushButton_3.setText(util.tr("登出"))
      util.is_connect_internet = util.is_internet_connect()
      viplevel = fdb.get_user_viplevel(username)
      print("cache exist :",username,viplevel)
      util.username= username
      if viplevel == -1:
        self.ui.label_2.setText(util.tr("游客"))
        self.ui.pushButton_3.setText(util.tr("登录"))
        self.ui.label_2.setStyleSheet("color:white;font:14px;")
        util.username= "游客"
        self.ui.pushButton_6.setVisible(False)
      elif viplevel == 1:
        self.ui.label_2.setText(username+"(VIP)")
        self.ui.label_2.setStyleSheet("color:yellow;font:14px;")
        self.ui.pushButton_6.setVisible(False)
      else:
        self.ui.label_2.setText(username)
        self.ui.label_2.setStyleSheet("color:white;font:14px;")
        self.ui.pushButton_6.setVisible(True)
    else:
      self.ui.label_2.setText(util.tr("游客"))
      self.ui.pushButton_3.setText(util.tr("登录"))
      self.ui.label_2.setStyleSheet("color:white;font:14px;")
      util.username= "游客"
      self.ui.pushButton_6.setVisible(False)
    
    #用来创建不存在的数据库，不能删除
    fdb.connect_to_database()
    util.send_event_str(util.ClearPatientInfo)
  
  def init_ui(self):
    self.ui.pushButton_3.connect('clicked()',self.on_login_logout)
    self.ui.pushButton_2.connect('clicked()',self.on_contact_us)
    self.ui.pushButton_4.connect('clicked()',self.on_reload)
    self.ui.pushButton_6.connect('clicked()',self.on_add_vip)
    self.ui.btnClear.connect('clicked()',self.on_clear)
    self.ui.btnSave.connect('clicked()',self.on_save)
    self.ui.btnLoad.connect('clicked()',self.on_load)
    self.ui.btnDoc.connect('toggled(bool)',self.show_artical)
    self.ui.btnData.connect('toggled(bool)',self.show_data)
    self.ui.btnDoc.setCheckable(True)
    self.ui.btnData.setCheckable(True)
    util.mainWindow().setNeedConfirm(True)
    #self.ui.btnData.hide()
    self.ui.btnDoc.hide()
    #widget = util.getModuleWidget("CPlusPlusThreadingMain")
    #widget.connect('on_tick_python(QString)',self.tickEvent)
    #util.getModuleWidget("CPlusPlusThreadingMain").add_handler("Net")
    #util.getModuleWidget("CPlusPlusThreadingMain").send_cmd(f"Net, SetGapMax, 5")
    
  def show_data(self,val):
    if val:
      util.layout_panel("middle_right").setMaximumWidth(350)
      util.layout_panel("middle_right").setMinimumWidth(350)
      util.layout_panel("middle_right").setModule("Data")
      self.ui.btnDoc.setChecked(False)
      util.layout_panel("middle_right").show()
    else:
      self.right_side_disable_check()
      
  def show_artical(self,val):
    if val:
      util.layout_panel("middle_right").setMaximumWidth(350)
      util.layout_panel("middle_right").setMinimumWidth(350)
      util.layout_panel("middle_right").setModule("")
      self.ui.btnData.setChecked(False)
      util.layout_panel("middle_right").show()
    else:
      self.right_side_disable_check()

  def right_side_disable_check(self):
    if not self.ui.btnData.isChecked() and not self.ui.btnDoc.isChecked():
        util.layout_panel("middle_right").hide()

  def on_load(self):
    util.layout_panel("middle_left").setMaximumWidth(10000000)
    util.layout_panel("middle_left").setMinimumWidth(400)
    util.layout_panel("middle_left").setModule("FrameworkPACS")
    slicer.util.findChildren(name="CentralWidget")[0].hide()
    util.send_event_str(util.DoctorAssitButttonResetState)
    util.layout_panel("middle_left").show()
  
  def on_clear(self):
    util.layout_panel("middle_right").hide()
    util.layout_panel("middle_right2").hide()
    res = util.messageBox(f"确定将清除当前数据吗？")
    if res == 0:
      return
    util.close_scene()
    util.getModuleWidget("UnitCreateChannel").on_delete()
  def on_save(self):
    import sqlite3,os
    from datetime import datetime
    import time
    if True:
      util.send_event_str(util.BeginSaveSolution)
      save_path = util.get_common_save_path("bak")
      fileName = qt.QFileDialog.getSaveFileName(None, ("保存文件"),
                              f"{save_path}/save.{self.get_extension()}",
                              ("存档 (*.%s)"%(self.get_extension())))
      print("save file name is:",fileName)
      if fileName != "":
        filepath = fileName
      else:
        return
      
    util.send_event_str(util.ProgressStart,"正在保存")
    util.send_event_str(util.ProgressValue,30)
    
    
    sliceViewName = "Red"
    image_path = self.resourcePath('UI/tmp_screenshot.png')
    layoutManager = slicer.app.layoutManager()
    threeDView = layoutManager.threeDWidget(0).threeDView()
    import ScreenCapture
    cap = ScreenCapture.ScreenCaptureLogic()
    cap.captureImageFromView(threeDView, image_path)
    
    util.saveScene(filepath)
    from FrameworkLib.datas import fdb
    fdb.save_analyse_info(image_path,filepath)
    util.save_to_PAAA("latest_save_path",filepath)
    util.send_event_str(util.ProgressValue,100)
    util.showWarningText("文件保存至: "+filepath)
    os.remove(image_path)

  def on_add_vip(self):
    util.show_vip()
    return
  
  @vtk.calldata_type(vtk.VTK_OBJECT)
  def tickEvent(self,info1):
    try:
      self._tickEvent(info1)
    except Exception as e:
      util.write_rdn_communicate_log(e.__str__())
  def _tickEvent(self,info1):
    all_info_list = info1.split("&H&, ")
    for row in all_info_list:
      key_pair_list = row.split("*Y*, ")
      if len(key_pair_list)!=2:
        continue
      key = key_pair_list[0]
      value = key_pair_list[1]
      
      map_info = {}
      info_list_str = value.split("*V* ")
      for row in info_list_str:
        if row == "":
          continue
        key_value_pair_list = row.split("*U* ")
        assert(len(key_value_pair_list)==2)
        key1 = key_value_pair_list[0]
        value1 = key_value_pair_list[1]
        map_info[key1] = value1
      #util.write_rdn_communicate_log(key + "->" + map_info.__str__())
      if 'fsm' in util.global_data_map:
        util.global_data_map['fsm'].tickEvent(key,map_info)
      
      if key == "Net":
        #print("------------------------------------",value)
        pass
  
  def get_extension(self):
    return "mrb"

  def on_popup_login_dialog(self):
    dialog = util.getModuleWidget("JMessageBox").on_popup_ui_dialog("登录",util.getModuleWidget("FrameworkLogin").get_widget(), 700, 450)
    util.getModuleWidget("FrameworkLogin").set_dialog(dialog)
    dialog.exec_()
  
  def on_contact_us(self):
    self._on_contact_us()
  def _on_contact_us(self):
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/Contact.ui'))
    ui = slicer.util.childWidgetVariables(uiWidget)
    
    contact_path = self.resourcePath('Icons/contact.png')
    slicer.util.addPictureFromFile(contact_path,ui.label_2,size_width=381,size_height=381)
    util.getModuleWidget("JMessageBox").on_popup_ui_dialog("微信群",uiWidget, 400, 510).exec_()
        
  def on_login_logout(self):
    if self.ui.pushButton_3.text == util.tr("登录"):
      self.on_popup_login_dialog()
    else:
      res = util.messageBox("确认要登出当前账号吗？",windowTitle=util.tr("提示"))
      if res == 0:
        return
      util.httplib.clear_cache()
      self.refresh_cache()
  
  def on_reload(self):
    print("on reload")
    # import os
    # file_name = os.path.basename(__file__)
    # print(f"Reloading {file_name}")         
    # packageName='FrameworkLib'
    # submoduleNames = ['BottomUnit']
    # import imp
    # f, filename, description = imp.find_module(packageName)
    # package = imp.load_module(packageName, f, filename, description)
    # for submoduleName in submoduleNames:
    #   f, filename, description = imp.find_module(submoduleName, package.__path__)
    #   try:
    #       imp.load_module(packageName+'.'+submoduleName, f, filename, description)
    #   finally:
    #       f.close()
    #util.getModuleWidget("FrameworkLogin").onReload()
    #util.getModuleWidget("FrameworkRouter").onReload()
    # util.getModuleWidget("UnitPunctureGuideBottom").onReload()
    #util.getModuleWidget("UnitCTHeadVolumes").onReload()
    # util.getModuleWidget("UnitCTMask").onReload()
    # util.getModuleWidget("UnitCTTumor").onReload()
    # util.getModuleWidget("UnitCreateChannel").onReload()
    util.getModuleWidget("sunModule").onReload()
    util.getModuleWidget("sunHeadFrame").onReload()
    self.onReload()
    