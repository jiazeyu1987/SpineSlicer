import vtk, qt, ctk, slicer,os
from slicer.ScriptedLoadableModule import *
import slicer.util as util
from Base.JBaseProject import *
from qt import QFontDatabase
#import nest_asyncio

#
# PAAA
#

class PAAA(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "base project"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["JPlugins"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["jia ze yu"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """

"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """

"""
# PAAAWidget
#

class PAAAWidget(JBaseProjectWidget):
  settings = None
  setting_panel_ui = None
  pagelist = {}
  sub_project = None
  argc = None
  argv = None
  arg_map = {}
  def __init__(self, parent=None):
    super().__init__(parent)
    


  def setup(self):
    super().setup()
    #nest_asyncio.apply()
    print("in argc:",util.mainWindow().get_argc())
    print("in argc:",util.mainWindow().get_argv())
    self.argc = util.mainWindow().get_argc()
    self.argv = util.mainWindow().get_argv()
    self.argv_arr = self.argv.split(",")
    self.arg_map = {}
    for i in range(self.argc):
      if i == 0 :
        continue
      if i % 2 == 0:
        continue
      key = self.argv_arr[i]
      value = self.argv_arr[i+1]
      self.arg_map[key] = value
    for key in self.arg_map:
      print("key:",key)
      print("value:",value)
      
    settings = qt.QSettings() 
    style =  settings.value("Styles/Style")
    if util.get_from_PAAA("style",default=0) == 0:
      new_style = "Dark Slicer"
    else:
      new_style = "Dark Slicer"
    settings.setValue("Styles/Style", new_style)
    print("Settings style:",style)
    
    util.curr_language = int(util.get_from_PAAA("qm_type", "0"))  
  def loadjson(self,json_path,discription_json_path):
    layoutManager = slicer.app.layoutManager()
    #layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutConventionalPlotView)
    #layoutManager.setLayout(16)
    layoutManager.setLayout(3)
    
    import json
    if os.path.exists(json_path):
      with open(json_path, encoding='utf-8') as json_file:
        util.JsonData = json.load(json_file)

    if os.path.exists(discription_json_path):
      with open(discription_json_path, encoding='utf-8') as json_file:
        util.InfoJson = json.load(json_file)
        self.init_from_info()

  def init_from_info(self):
    import os
    
    
    filepath = os.path.dirname(__file__)
    scriptedDirPath = os.path.abspath(os.path.dirname(filepath))
    filepath = os.path.join(scriptedDirPath,"GLPyModule","abc")

    util.add_search_paths(["JLogin", "JProjectSelector"],"","",filepath)

    moduleManager = slicer.app.moduleManager()
    moduleFactoryManager = moduleManager.factoryManager()
    moduleFactoryManager.registerModules()
    #moduleFactoryManager.instantiateModules()
    moduleFactoryManager.instantiateModules()
    moduleFactoryManager.loadModules()

  

  

  

  

  

  def init_event(self):
    self.TagMaps[util.ProgressStart] = slicer.mrmlScene.AddObserver(util.ProgressStart, self.OnProgressStart)
    self.TagMaps[util.ProgressValue] = slicer.mrmlScene.AddObserver(util.ProgressValue, self.OnProgressValue)
    self.TagMaps[util.ProgressStep] = slicer.mrmlScene.AddObserver(util.ProgressStep, self.OnProgressStep)
    
    self.TagMaps[util.ApplicationDisActivate] = slicer.mrmlScene.AddObserver(util.ApplicationDisActivate, self.OnApplicationDisActivate)
    self.TagMaps[util.SetPage] = slicer.mrmlScene.AddObserver(util.SetPage, self.OnSetPage)  
    self.TagMaps[util.GotoPrePage] = slicer.mrmlScene.AddObserver(util.GotoPrePage, self.OnGotoPrePage)
    self.TagMaps[util.GotoNextPage] = slicer.mrmlScene.AddObserver(util.GotoNextPage, self.OnGotoNextPage)
    self.TagMaps[util.GotoCurrentPage] = slicer.mrmlScene.AddObserver(util.GotoCurrentPage, self.OnGotoCurrentPage)
    self.TagMaps[util.NewFileLoadedFromMain] = slicer.mrmlScene.AddObserver(util.NewFileLoadedFromMain, self.OnNewFileLoaded)
    self.TagMaps[util.ArchiveFileLoadedEvent] = slicer.mrmlScene.AddObserver(util.ArchiveFileLoadedEvent, self.OnArchiveFileLoadedEvent)
    
    self.TagMaps[util.SceneDestroyEvent] = slicer.mrmlScene.AddObserver(util.SceneDestroyEvent, self.OnSceneDestroyEvent)
    self.TagMaps[util.InitPageList] = slicer.mrmlScene.AddObserver(util.InitPageList, self.OnInitPageList)
    self.TagMaps[util.UnitTestFinished] = slicer.mrmlScene.AddObserver(util.UnitTestFinished, self.OnUnitTestFinished)
    self.TagMaps[1481265] = slicer.mrmlScene.AddObserver(1481265, self.OnESCPressEvent)

  def OnESCPressEvent(self,_a,_ab):
    util.trigger_view_tool("")
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setActiveEffectByName("None")

  def OnUnitTestFinished(self,a,b):
    unit_test_module_names = util.unit_test['unit_test_module_names']
    unit_test_module_index = util.unit_test['unit_test_module_index']
    if unit_test_module_index >= len(unit_test_module_names):
      process_name = 'SlicerApp-real.exe'
      util.singleShot(0,lambda:util.kill_process_by_name(process_name))
      return
    TestModuleName = unit_test_module_names[unit_test_module_index]
    module_path = f"Test.{TestModuleName}Test"
    import importlib
    module = importlib.import_module(module_path)
    class_obj = getattr(module, f"{TestModuleName}Test")
    obj = class_obj()
    util.unit_test['unit_test_module_index'] = util.unit_test['unit_test_module_index']+1
    util.singleShot(0,lambda:obj.runTest())

  def OnSceneDestroyEvent(self,_a,_b):
    threeD_view_background_color = util.getjson("threeD_view_background_color","0|0|0")
    tl = threeD_view_background_color.split("|")
    threeD_view_background_color2 = util.getjson("threeD_view_background_color2","0|0|0")
    tl2 = threeD_view_background_color2.split("|")
    for viewIndex in range(slicer.app.layoutManager().threeDViewCount):
      viewNode = slicer.app.layoutManager().threeDWidget(viewIndex).mrmlViewNode()
      viewNode.SetBackgroundColor(float(tl[0]),float(tl[1]),float(tl[2]))
      viewNode.SetBackgroundColor2(float(tl2[0]),float(tl2[1]),float(tl2[2]))

    is_axis_visible = util.getjson("show_axis","0")=="2"
    is_box_visible = util.getjson("show_box","0")=="2"
    is_link_control = util.getjson("link_control","0")=="2"
    show_controller = util.getjson("show_controller","0")=="2"

    sliceCompositeNodes = slicer.util.getNodesByClass("vtkMRMLSliceCompositeNode")
    for sliceCompositeNode in sliceCompositeNodes:
      sliceCompositeNode.SetLinkedControl(True)
    
    layoutManager=slicer.app.layoutManager()
    for threeDViewIndex in range(layoutManager.threeDViewCount) :
      viewNode = slicer.app.layoutManager().threeDWidget(threeDViewIndex).mrmlViewNode()
      viewNode.SetAxisLabelsVisible(is_axis_visible)
      #viewNode.SetBoxVisible(is_box_visible)
    util.setViewControllersVisible(show_controller)
    #self.preinit_modules()
    
  def OnInitPageList(self,_a,_b):
    self.init_from_data()

  
  def unique_border_color(self):
    flag = util.getjson2("controller","window_border_color","0")
    if flag == "2":
      slicer.app.layoutManager().sliceWidget("Red").setStyleSheet("border: 1px solid #ff0000")
      slicer.app.layoutManager().sliceWidget("Yellow").setStyleSheet("border: 1px solid #edd94c")
      slicer.app.layoutManager().sliceWidget("Green").setStyleSheet("border: 1px solid #6eb04b")
      #slicer.app.layoutManager().threeDWidget(0).setStyleSheet("border: 2px solid #0000ff")
      
      slicer.app.layoutManager().sliceWidget("Red+").setStyleSheet("border: 1px solid #ff0000")
      slicer.app.layoutManager().sliceWidget("Yellow+").setStyleSheet("border: 1px solid #edd94c")
      slicer.app.layoutManager().sliceWidget("Green+").setStyleSheet("border: 1px solid #6eb04b")
      #slicer.app.layoutManager().threeDWidget(1).setStyleSheet("border: 2px solid #0000ff")

  def update_menu(self):
    mw = util.mainWindow()
    menubar = util.findChild(mw, "menubar")
    show_menu_bar = util.getjson2("menu_bar","show_menu_bar",False)
    file_add_data = util.getjson2("menu_bar","file_add_data",False)
    file_add_dicom_data = util.getjson2("menu_bar","file_add_dicom_data",False)
    file_recent = util.getjson2("menu_bar","file_recent",False)
    file_donwload_sample_data = util.getjson2("menu_bar","file_donwload_sample_data",False)
    file_save_data = util.getjson2("menu_bar","file_save_data",False)
    file_close_scene = util.getjson2("menu_bar","file_close_scene",False)
    file_exit = util.getjson2("menu_bar","file_exit",False)
    edit_cut = util.getjson2("menu_bar","edit_cut",False)
    edit_copy = util.getjson2("menu_bar","edit_copy",False)
    edit_paste = util.getjson2("menu_bar","edit_paste",False)
    edit_settings = util.getjson2("menu_bar","edit_settings",False)
    view_layout = util.getjson2("menu_bar","view_layout",False)
    view_toolbars = util.getjson2("menu_bar","view_toolbars",False)
    view_appearance = util.getjson2("menu_bar","view_appearance",False)
    view_module_finder = util.getjson2("menu_bar","view_module_finder",False)
    view_extensions_manager = util.getjson2("menu_bar","view_extensions_manager",False)
    view_python_console = util.getjson2("menu_bar","view_python_console",False)
    view_home = util.getjson2("menu_bar","view_home",False)
    view_error_log = util.getjson2("menu_bar","view_error_log",False)
    help_about = util.getjson2("menu_bar","help_about",False)
    
    if not show_menu_bar:
      util.setMenuBarsVisible(False)
      return
    
    util.setMenuBarsVisible(True)
    FileMenu = util.findChild(mw, "FileMenu")
    show_file_menu = util.getjson2("menu_bar","show_file_menu",False)
    if not show_file_menu:
      menubar.removeAction(FileMenu.menuAction())
    else:
      actionlist = []
      for action in FileMenu.actions():
        FileMenu.removeAction(action)
        actionlist.append(action)
        
      for action in actionlist:
        if file_add_data and (action.text.find("Add Data")!=-1 or action.text.find("添加数据")!=-1):
            FileMenu.addAction(action)
        if file_add_dicom_data and action.text.find("Add DICOM Data")!=-1:
            FileMenu.addAction(action)
        if file_recent and (action.text.find("Recent")!=-1 or action.text.find("最近加载")!=-1):
            FileMenu.addAction(action)
        if file_donwload_sample_data and (action.text.find("Download Sample Data")!=-1 or action.text.find("添加数据")!=-1):
            FileMenu.addAction(action)
        if file_save_data and (action.text.find("Save Data")!=-1 or action.text.find("保存数据")!=-1):
            FileMenu.addAction(action)
        if file_close_scene and (action.text.find("Close Scene")!=-1 or action.text.find("关闭场景")!=-1):
            FileMenu.addAction(action)
        if file_exit and (action.text.find("Exit")!=-1 or action.text.find("退出")!=-1):
            FileMenu.addAction(action)
    
    util.setMenuBarsVisible(True)
    EditMenu = util.findChild(mw, "EditMenu")
    show_edit_menu = util.getjson2("menu_bar","show_edit_menu",False)
    if not show_edit_menu:
      menubar.removeAction(EditMenu.menuAction())
    else:
      actionlist = []
      for action in EditMenu.actions():
        EditMenu.removeAction(action)
        actionlist.append(action)
        
      for action in actionlist:
        if edit_cut and (action.text.find("Cut")!=-1 or action.text.find("剪切")!=-1):
            EditMenu.addAction(action)
        if edit_copy and (action.text.find("Copy")!=-1 or action.text.find("复制")!=-1):
            EditMenu.addAction(action)
        if edit_paste and (action.text.find("Paste")!=-1 or action.text.find("粘贴")!=-1):
            EditMenu.addAction(action)
        if edit_settings and (action.text.find("Application Settings")!=-1 or action.text.find("应用程序设置")!=-1):
            EditMenu.addAction(action)
            
        
    util.setMenuBarsVisible(True)
    ViewMenu = util.findChild(mw, "ViewMenu")
    show_view_menu = util.getjson2("menu_bar","show_view_menu",False)
    if not show_view_menu:
      menubar.removeAction(ViewMenu.menuAction())
    else:
      actionlist = []
      for action in ViewMenu.actions():
        ViewMenu.removeAction(action)
        actionlist.append(action)
      
      for action in actionlist:
        if view_layout and (action.text.find("Layout")!=-1 or action.text.find("布局")!=-1):
            ViewMenu.addAction(action)
        if view_toolbars and (action.text.find("Toolbars")!=-1 or action.text.find("工具栏")!=-1):
            ViewMenu.addAction(action)
        if view_appearance and (action.text.find("Appearance")!=-1 or action.text.find("外观")!=-1):
            ViewMenu.addAction(action)
        if view_extensions_manager and (action.text.find("Extensions Manager")!=-1 or action.text.find("扩展管理器")!=-1):
            ViewMenu.addAction(action)
        if view_home and (action.text.find("Home")!=-1 or action.text.find("首页")!=-1):
            ViewMenu.addAction(action)
        if view_python_console and (action.text.find("Python Console")!=-1 or action.text.find("Python控制台")!=-1):
            ViewMenu.addAction(action)
        if view_error_log and (action.text.find("Error Log")!=-1 or action.text.find("错误日志")!=-1):
            ViewMenu.addAction(action)
        if view_module_finder and (action.text.find("Module Finder")!=-1):
            ViewMenu.addAction(action)
      
      # measure_page_action = qt.QAction("测量页面",ViewMenu)
      # measure_page_action.connect('triggered()', lambda:util.send_event_str(util.SetPage,"915")) 
      # ViewMenu.addAction(measure_page_action)     
        
    util.setMenuBarsVisible(True)
    HelpMenu = util.findChild(mw, "HelpMenu")
    show_help_menu = util.getjson2("menu_bar","show_help_menu",False)
    if not show_help_menu:
      menubar.removeAction(HelpMenu.menuAction())
    else:
      actionlist = []
      for action in HelpMenu.actions():
        HelpMenu.removeAction(action)
        actionlist.append(action)
        
      for action in actionlist:
        if help_about and (action.text.find("About 3D Slicer")!=-1 or action.text.find("关于 3D Slicer")!=-1):
            HelpMenu.addAction(action)
  
  def cancel_stay_on_top(self):
    util.mainWindow().setWindowFlags(util.mainWindow().windowFlags() & ~qt.Qt.WindowStaysOnTopHint)
    util.mainWindow().show()

  def init_from_data(self):
    import os
    print("init_from_data")
    
    
    
    util.mainWindow().setWindowTitle(util.getjson("window_title")+util.getjson("version"))
    project_name = util.getjson("project_name","0")
    self.init_sub_project()
    unique_color_controller = util.getjson("unique_color_controller","0")=="2"
    controller_direction =  util.getjson("controller_direction","0")=="2"
    is_axis_visible = util.getjson("show_axis","0")=="2"
    is_box_visible = util.getjson("show_box","0")=="2"
    is_link_control = util.getjson("link_control","0")=="2"
    show_controller = util.getjson("show_controller","0")=="2"
    slice_view_background_color = util.getjson("slice_view_background_color","0|0|0")
    sl = slice_view_background_color.split("|")
    threeD_view_background_color = util.getjson("threeD_view_background_color","0|0|0")
    tl = threeD_view_background_color.split("|")
    threeD_view_background_color2 = util.getjson("threeD_view_background_color2","0|0|0")
    tl2 = threeD_view_background_color2.split("|")
    if controller_direction:
      util.set_controller_vertical_layout()
    if not unique_color_controller:
      #nodes = util.getNodesByClass("vtkMRMLAbstractViewNode")
      #for node in nodes:
      #  node.SetLayoutColor([155/255.0,155/255.0,155/255.0])
      layoutManager = slicer.app.layoutManager()
      for sliceViewName in layoutManager.sliceViewNames():
        qMRMLSliceWidget = layoutManager.sliceWidget(sliceViewName)
        if controller_direction:
          qMRMLSliceWidget.layout().setDirection(0)
        sliceController = qMRMLSliceWidget.sliceController()
        SliceOffsetSlider = sliceController.sliceOffsetSlider()
        SliceOffsetSlider.setStyleSheet("background-color: rgb(255, 255, 255);")
        
    sliceCompositeNodes = slicer.util.getNodesByClass("vtkMRMLSliceCompositeNode")
    for sliceCompositeNode in sliceCompositeNodes:
      sliceCompositeNode.SetLinkedControl(True)
    
    layoutManager=slicer.app.layoutManager()
    for threeDViewIndex in range(layoutManager.threeDViewCount) :
      viewNode = slicer.app.layoutManager().threeDWidget(threeDViewIndex).mrmlViewNode()
      viewNode.SetAxisLabelsVisible(is_axis_visible)
      #viewNode.SetBoxVisible(is_box_visible)
      viewNode.SetLinkedControl(True)
    util.setViewControllersVisible(show_controller)
    
    if tl[0] == "0" and tl2[0] == "0" and tl[1] == "0" and tl2[1] == "0" and tl[2] == "0" and tl2[2] == "0":
      for viewIndex in range(slicer.app.layoutManager().threeDViewCount):
        viewNode = slicer.app.layoutManager().threeDWidget(viewIndex).mrmlViewNode()
        viewNode.SetBackgroundColor(0.7568627450980392, 0.7647058823529412, 0.9098039215686275)
        viewNode.SetBackgroundColor2(0.4549019607843137, 0.4705882352941176, 0.7450980392156863)
    else: 
      for viewIndex in range(slicer.app.layoutManager().threeDViewCount):
        viewNode = slicer.app.layoutManager().threeDWidget(viewIndex).mrmlViewNode()
        viewNode.SetBackgroundColor(float(tl[0]),float(tl[1]),float(tl[2]))
        viewNode.SetBackgroundColor2(float(tl2[0]),float(tl2[1]),float(tl2[2]))
        
    slicer.util.QSS_QWidget_MV_color = util.getjson("QSS_QWidget_MV_color","#000000")
    slicer.util.QSS_QWidget_background_color = util.getjson("QSS_QWidget_background_color","#000000")
    # if util.getjson("full_screen","0") == "2":
    #   util.mainWindow().show_full_screen(True)
    # else:
    #   util.mainWindow().show_full_screen(False)
    
    self.add_depend_modules()
    self.init_pagelist()
    self.init_system_extra_module()
    self.init_modules_settings()
    self.unique_border_color()
    self.update_menu()
    if self.sub_project:
      if hasattr(self.sub_project, "after_init_from_data"):
        self.sub_project.after_init_from_data()
    self.abc()
    util.singleShot(0,self.reset_ruler)
  
  def abc(self):
    import os
    dirname = os.path.dirname(util.get_project_base_path())
    dirname = os.path.dirname(dirname)
    GLPyModuleFolder = dirname
    
    folder_path = GLPyModuleFolder+"/JExtension"
    for dirpath, dirnames, filenames in os.walk(folder_path):
        # 检查当前文件夹中是否有 .yp 文件
        has_yp_file = any(filename.endswith('.yp') for filename in filenames)
        
        if has_yp_file:
            # 打印当前文件夹的路径
            self.remove_ddd(dirpath)
            
    folder_path = GLPyModuleFolder+"/Project"
    for dirpath, dirnames, filenames in os.walk(folder_path):
        # 检查当前文件夹中是否有 .yp 文件
        has_yp_file = any(filename.endswith('.yp') for filename in filenames)
        
        if has_yp_file:
            # 打印当前文件夹的路径
            self.remove_ddd(dirpath)
            
  def remove_ddd(self,folder_path):
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        
        # 检查是否是文件且后缀为.py
        if os.path.isfile(item_path) and item_path.endswith('.py'):
            os.remove(item_path)
            print(f"Deleted: {item_path}")
        
  
  def reset_ruler(self):
    ruler_type = util.getjson2("annotation","Ruler","0")
    ruler_type = int(ruler_type)
    layoutManager = slicer.app.layoutManager()
    for sliceViewName in layoutManager.sliceViewNames():
      layoutManager.sliceWidget(sliceViewName).mrmlSliceNode().SetRulerType(ruler_type)
      layoutManager.sliceWidget(sliceViewName).mrmlSliceNode().SetRulerColor(0)
      
  def init_modules_settings(self):
    modulenames = util.moduleNames()
    for key in util.JsonData:
      value = util.JsonData[key]
      if isinstance(value,dict):
        if "module_config" in value:
          if  key in modulenames:
            util.getModuleWidget(key).init_from_config_json(value)
          else:
            raise Exception("unsupport key:",key)

  def init_system_extra_module(self):
    SystemModules = util.getjson("SystemModules","").split(", ")
    modulesToIgnore = slicer.app.moduleManager().factoryManager().modulesToIgnore
    from typing import cast
    modulesToIgnore = list(cast(tuple, modulesToIgnore))
    for modulename in SystemModules:
      if modulename in modulesToIgnore:
        modulesToIgnore.remove(modulename)
    slicer.app.moduleManager().factoryManager().modulesToIgnore = modulesToIgnore
    slicer.app.moduleManager().factoryManager().modulesToIgnore = modulesToIgnore
    moduleManager = slicer.app.moduleManager()
    moduleFactoryManager = moduleManager.factoryManager()
    moduleFactoryManager.registerModules()
    moduleFactoryManager.instantiateModules()
    moduleFactoryManager.loadModules()

  def init_pagelist(self):
    PageListStr = util.getjson("Page","")
    for pst in PageListStr:
      PageNumber = int(util.getcustomjson(pst,"PageNumber","1"))
      self.pagelist[PageNumber] = pst

  def add_depend_modules(self):
    import slicer,os
    filepath = os.path.dirname(__file__)
    scriptedDirPath = os.path.abspath(os.path.dirname(filepath))
    GLPyDirPath = os.path.abspath(os.path.dirname(scriptedDirPath))
    filepath = os.path.join(scriptedDirPath,"GLPyModule","abc")
    modules = []
    p_module_need_to_load = util.getjson2("JModules","p_module_need_to_load","").split(", ")
    c_module_need_to_load = util.getjson2("JModules","c_module_need_to_load","").split(", ")
    r_module_need_to_load = util.getjson2("JModules","r_module_need_to_load","").split(", ")
    moduleManager = slicer.app.moduleManager()
    moduleFactoryManager = moduleManager.factoryManager()
    util.decrypt_PAAA(GLPyDirPath,p_module_need_to_load,c_module_need_to_load)
    util.add_search_paths(p_module_need_to_load,c_module_need_to_load,r_module_need_to_load,filepath)
    util.decrypt_remove_PAAA(GLPyDirPath,p_module_need_to_load,c_module_need_to_load)
    
    p_module_need_to_load = util.getjson2("DModules","p_module_need_to_load","").split(", ")
    c_module_need_to_load = util.getjson2("DModules","c_module_need_to_load","").split(", ")
    util.add_d_search_paths(p_module_need_to_load,c_module_need_to_load,filepath)

    
    
    moduleFactoryManager.registerModules()
    #moduleFactoryManager.instantiateModules()
    moduleFactoryManager.instantiateModules()
    moduleFactoryManager.loadModules()
    
    return
  
    

  def init_sub_project(self):
    import os
    project_name = util.getjson("project_name","0")
    filepath = os.path.dirname(__file__)
    sub_project_file_path = "ProjectCache.%s.SubProject"%(project_name)
    file_path = os.path.join(filepath,"ProjectCache",project_name,"SubProject.py").replace("\\","/")
    print("init sub project:",file_path)
    if os.path.exists(file_path):
      import importlib
      module = importlib.import_module(sub_project_file_path)
      class_obj = getattr(module, "SubProject")
      self.sub_project = class_obj(self)
      self.sub_project.init_sub_project()
    else:
      print(f"{file_path} init_sub_project is not exist")

  

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def OnApplicationDisActivate(self,caller,str_event,calldata):
    raise Exception("PDuruofei Don't Have OnApplicationDisActivate Action")


  @vtk.calldata_type(vtk.VTK_OBJECT)
  def OnProgressStart(self,caller,str_event,calldata):
    val = calldata.GetAttribute("value")
    
    if val is None:
      val = "请稍候..."
    util.createProgressDialog2(parent=self, value=0, maximum=100,windowTitle=val)
    slicer.app.processEvents()



  @vtk.calldata_type(vtk.VTK_OBJECT)
  def OnProgressValue(self,caller,str_event,calldata):
    val = calldata.GetAttribute("value")
    util.setProgress(int(float(val)))
    slicer.app.processEvents()

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def OnProgressStep(self,caller,str_event,calldata):
    val = calldata.GetAttribute("value")
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX:",val)
    util.SetProgressStep(float(val))
    util.UpdateProgress()
    slicer.app.processEvents()
  
  
  @vtk.calldata_type(vtk.VTK_OBJECT)
  def OnNewFileLoaded(self,caller,str_event):
    if util.get_from_PAAA("current_project_selector_project_name")!="DoctorAssitant":
      self.OnGotoNextPage("","")
  
  @vtk.calldata_type(vtk.VTK_OBJECT)
  def OnArchiveFileLoadedEvent(self,caller,str_event,calldata):
    page_list = util.GetGlobalSaveValue("page_list")
    if page_list is not None:
      page_list = page_list.split(",")
      self.linked_list = LinkedList()
      for page in page_list:
        self.linked_list.append(page)

  
    

  def init_ui(self):
    import os
    #super().init_ui()
    current_project_selector_project_name = util.get_from_PAAA("current_project_selector_project_name")
    json_path = os.path.join(util.mainWindow().GetProjectBasePath(),"ProjectCache",current_project_selector_project_name,"sub_project.json")
    discription_json_path = os.path.join(util.mainWindow().GetProjectBasePath(),"ProjectCache","discription_json.json")
    self.loadjson(json_path,discription_json_path)
    self.init_event()
    util.mainWindow().setWindowTitle(util.getjson("window_title")+util.getjson("version"))
    
  
  
  
    

  def SetPage(self,page):
    
    if page!=1:
      raise Exception("only support 1 from C++ framework")
    if self.linked_list.get_last()!= 1:
      self.linked_list.append(1)
      
    #util.fresh_project_ui_frame()
    self._SetPage(self.linked_list.get_last())

  def _SetPage(self,page):
    super()._SetPage(page)
    
    if self.sub_project:
      if hasattr(self.sub_project, "SetPageBefore"):
        self.sub_project.SetPageBefore(page)
    layout_style = util.getjson2("Global","layout_style",default_value="0")
    layout_style = int(layout_style)
      
    print("on set layout style:",layout_style,page)
    if layout_style == 99:
      self._SetPageStyle99(page)

    if self.sub_project:
      if hasattr(self.sub_project, "SetPageAfter"):
        self.sub_project.SetPageAfter(page)

  def get_center_widget(self):
     return slicer.util.findChildren(name="CentralWidget")[0]
  def get_left_docker(self):
    return slicer.util.findChildren(name="PanelDockWidget")[0]
  def get_right_docker(self):
    return slicer.util.findChildren(name="PanelDockRightTitle")[0]
  def get_left_panel(self):
    return slicer.util.findChildren(name="ModulePanel")[0]
 
  def on_auth(self):
    import datetime
    current_date = datetime.datetime.now().date()

    # 定义截止日期
    end_date = datetime.date(2025, 6, 1)

    # 判断当前日期是否大于截止日期
    if current_date > end_date:
        # 创建一个隐藏的主窗口
        util.showRealWarningText("试用期已结束，请获取最新版本")
        util.quit()
          
            
  def test(self):
    import shutil
    return
    # shutil.rmtree(r"D:\2\ssc")
    # os.makedirs(r"D:\2\ssc")
    util.getModuleWidget("UnitSimpleTeacherData").on_add_data_2()
    
    #util.getModuleWidget("sunModule").ui.radioButton.setChecked(True)
    return
    
    util.on_camera_direction("R")
    
    util.getModuleWidget("sunModule").on_whole()
    
    #util.getModuleWidget("sunModule").on_place_head_frame()
    #util.getModuleWidget("sunModule").on_export()
    #util.getModuleWidget("sunModule").test()
    return
    util.getModuleWidget("sunModule").load_head_frame()
    
    # layoutManager=slicer.app.layoutManager()
    # for threeDViewIndex in range(layoutManager.threeDViewCount) :
    #   viewNode = slicer.app.layoutManager().threeDWidget(threeDViewIndex).mrmlViewNode()
    #   #viewNode.SetBoxVisible(True)
    #   viewNode.SetAxisLabelsVisible(True)
  
   #左边控制栏，测量栏顶部放置，不限分辨率
  def _SetPageStyle99(self,page):
    if page == "1" or page == 1:
      
      util.project_enter()
      util.setToolbarsVisible(False)
      
      self.init_from_data()
      self.preinit_modules()
      util.layout_dock("left").hide()
      util.layout_dock("right").hide()
      util.layout_dock("top").hide()
      util.layout_dock("bottom").hide()
      util.layout_panel("middle_left").hide()
      util.layout_panel("middle_bottom").hide()
      util.layout_dock("right_title").hide()
      util.layout_panel("middle_top").hide()
      util.layout_panel("middle_left").show()
      util.layout_panel("middle_left").setModule("")
      util.layout_panel("middle_left2").hide()
      util.layout_panel("middle_right").hide()
      util.layout_panel("middle_right2").hide()
      util.layout_panel("middle_bottom").setModule("")
      util.layout_panel("right").setModule("")
      util.main_panel = util.layout_panel("middle_left")
      util.layout_panel("bottom").setModule("")
      util.layout_panel("middle_left").setMaximumWidth(205)
      util.layout_panel("middle_left").setMinimumWidth(205)
      
     # util.layout_panel("middle_left").setModule("FrameworkMenu")
      slicer.util.findChildren(name="CentralWidget")[0].hide()
      slicer.app.layoutManager().threeDWidget(0).mrmlViewNode().SetBoxVisible(False)
      util.singleShot(100,lambda:self._SetPageStyle99(4))
    if page == "4" or page == 4:
      util.layout_dock("top").show()
      util.layout_panel("top").setFixedHeight(40)
      util.layout_dock("top").setFixedHeight(40)
      util.layout_panel("top").setModule("FrameworkTop")
      
      
      util.layout_panel("middle_top").show()
      util.layout_panel("middle_top").setFixedHeight(46)
      util.layout_panel("middle_top").setModule("FrameworkBottom")
      util.layout_panel("middle_top").show()
      
      key = "UnitPunctureGuide"
      button_unit = key+"Bottom"
      fra = util.getModuleWidget(button_unit)
      util.addWidgetOnly(util.getModuleWidget("FrameworkBottom").ui.menu, fra.get_control_panel())
      hard = util.get_cache_from_PAAA("sub_solution_hard","-1")
      if hard == "-1":
        util.save_cache_to_PAAA("sub_solution_hard",2)
      util.getModuleWidget("FrameworkTop").update_title()
      fra.solution_init()
      
      
      if hard == "-1":
        util.getModuleWidget("FrameworkTop").on_show_menu()
      
      util.singleShot(0,lambda:util.mainWindow().showMaximized())
      
      util.singleShot(0,self.on_auth)
      if util.getjson2("Global","test_module") == "2":
        util.singleShot(1000,self.test)

      