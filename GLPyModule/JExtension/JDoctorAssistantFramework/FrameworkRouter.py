import slicer,qt,vtk,ctk
import slicer.util as util
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from Base.JBaseExtension import JBaseExtensionWidget
from FrameworkLib.httpslib import httplibClass
#
# FrameworkRouter
#


class FrameworkRouter(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "FrameworkRouter"  # TODO: make this more human readable by adding spaces
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
# FrameworkRouterWidget
#

class FrameworkRouterWidget(JBaseExtensionWidget):
  def setup(self):
    super().setup()
    
  
    
  def init_ui(self):
    self.init_config()
    print("init color list")
    self.init_colorlist()
    util.singleShot(10,self.init_later)
    
  def init_later(self):    
    
    print("init httplib")
    util.httplib = httplibClass()
    
    print("init mouse default action")
    self.init_mouse_default_action()
    print("init local database")
    self.init_database()
    print("refresh login cache")
    util.send_event_str(util.FrameworkTopRefreshCache)
    print("check version")
    self.check_version()    
    #util.send_event_str(util.ResetSolution) 
    util.getModuleWidget("FrameworkTop").on_show_menu()
      
  
  def check_version(self):
    version = util.get_from_PAAA("version",default="1.0.0")
    project_name = "全息脑出血方体定位系统"
    solution_name = util.get_cache_from_PAAA("solution_name",default="PunctureGuide")
    util.mainWindow().setWindowTitle(project_name+" v"+version+" (科研版) ")
    
    json_val = {}
    json_val['solution_name'] = solution_name
    util.httplib.httpgetasync("/system/info/get_version",json_val,timeout=10.1,need_login=False,silent=True,callback=self.on_get_version_callback)
    
  def init_config(self):
    import json
    file_path = self.resourcePath(f'text/doctor.json')
    with open(file_path, 'r', encoding='utf-8') as file:
      util.teacher_info = json.load(file)    
  
  def on_get_version_callback(self,flag,data):
    import os
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA on_get_version_callback:",flag,data)
    if flag:
      version = util.get_from_PAAA("version",default="1.0.0")
      project_name = data['msg']['name']
      project_version = data['msg']['version']
      current_biggest_version_saved = "1.0.3"
      if project_version != current_biggest_version_saved:
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        project_version = data['msg']['version']
        logdir = os.path.join(base_path,"version","log")
        if not os.path.exists(logdir):
          os.makedirs(logdir)
        localpath = os.path.join(logdir,os.path.basename(data['msg']['path']))
        print("BBBBBBBB:",data['msg']['path'])
        util.httplib.download_zip(localpath,data['msg']['path'])
      print(f"get remote version {version} , current version is {project_version}")
      if project_version != version:
        util.save_to_PAAA("need_update","1")
        util.getModuleWidget("FrameworkTop").OnFrameworkTopNeedUpdate("",project_version)
        #util.send_event_str(util.FrameworkTopNeedUpdate)
  
  def init_database(self):
    from FrameworkLib.datas import fdb
    fdb.connect_to_database()
  
  def init_colorlist(self):
    from FrameworkLib.ColorUnitList import ColorUnitList
    from FrameworkLib.ColorUnitList import TipsUnitList
    util.color_unit_list = ColorUnitList(self)
    util.color_unit_list.show()
    util.tips_unit_list = TipsUnitList(self)
    util.tips_unit_list.show()
    
    
  def init_mouse_default_action(self):
    # 创建一个函数来处理鼠标点击事件
    def onMouseClick(caller, event):
        if event == "RightButtonReleaseEvent":
           util.trigger_view_tool("")
          #  print("AAAAAAAAAAAAAAAAAAAAAAAaaa")

    # 获取三个主要的2D视图（红色，绿色和黄色视图）
    viewNames = ["Red", "Yellow", "Green"]
    for viewName in viewNames:
        # 获取对应的2D视图的widget
        viewWidget = slicer.app.layoutManager().sliceWidget(viewName)
        viewInteractor = viewWidget.sliceView().interactor()
        
        # 为鼠标点击事件添加监听器
        viewInteractor.AddObserver("RightButtonReleaseEvent", onMouseClick,0)
    
    for threeDViewIndex in range(slicer.app.layoutManager().threeDViewCount) :
      # 获取3D视图的widget
      threeDWidget = slicer.app.layoutManager().threeDWidget(threeDViewIndex)
      threeDView = threeDWidget.threeDView()
      threeDInteractor = threeDView.interactor()

      # 为鼠标点击事件添加监听器
      threeDInteractor.AddObserver("RightButtonReleaseEvent", onMouseClick)
    