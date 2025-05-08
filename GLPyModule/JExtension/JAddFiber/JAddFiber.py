import imp
import os
from re import A
from tabnanny import check
from time import sleep
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import slicer.util as util
import SlicerWizard.Utilities as su 
import numpy as np
from AddFiberLib.BaseUnit import FiberUnit
from AddFiberLib.NormalUnit import NormalUnit

#
# JAddFiber
#

class JAddFiber(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "JAddFiber"  # TODO: make this more human readable by adding spaces
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
# JAddFiberWidget
#

class JAddFiberWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  TagMaps = {}
  refresh_tab_enabled = False
  m_FiberUnitWidget = None
  m_FWList = []
  btn_config = None
  btn_maps = None
  unit_class_maps = {}
  def __init__(self, parent=None):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)  # needed for parameter node observation
    self.logic = None
    #self.doc = None
    self._parameterNode = None
    self._updatingGUIFromParameterNode = False

  def setup(self):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    self.logic = JAddFiberLogic()
    self.logic.setWidget(self)
    #self.doc = JAddFiberLogicDoc()
    #self.doc.setWidget(self)

    uiWidget = slicer.util.loadUI(self.resourcePath('UI/JAddFiber.ui'))
    
    self.layout.addWidget(uiWidget)
    

    self.ui = slicer.util.childWidgetVariables(uiWidget)
    
    uiWidget.setMRMLScene(slicer.mrmlScene)
    self.init_ui()
    self.ui.btn_add_fiber.setVisible(False)
    units= ["NormalUnit"]
    for utype in units:
      module_path = "AddFiberLib.%s"%(utype)
      import importlib
      module = importlib.import_module(module_path)
      class_obj = getattr(module, utype)
      self.unit_class_maps[utype] = class_obj

    self.TagMaps[util.MainNodeLoadedEvent] = slicer.mrmlScene.AddObserver(util.MainNodeLoadedEvent, self.OnMainNodeAdded)
    self.TagMaps[util.MainNodeRemovedEvent] = slicer.mrmlScene.AddObserver(util.MainNodeRemovedEvent, self.OnMainNodeRemoved)
    self.TagMaps[util.ArchiveFileLoadedEvent] = slicer.mrmlScene.AddObserver(util.ArchiveFileLoadedEvent, self.OnArchiveLoaded)
    self.TagMaps[util.SceneDestroyEvent] = slicer.mrmlScene.AddObserver(util.SceneDestroyEvent, self.OnSceneDestroyEvent)
    
  '''
    新建一页规划,可以是规划普通导管也可以是规划模型导管
  '''
  def add_unit(self,fu):
    #fu = FiberUnit(style)
    uiwidget = slicer.util.loadUI(self.resourcePath('UI/JAddFiberUnit.ui'))
    if fu.style.split(":")[0] == "NormalUnit":
      if util.get_from_PAAA("current_project_selector_project_name")!="SunSlicer":
        uiwidget = slicer.util.loadUI(self.resourcePath('UI/JNormalUnit.ui'))
      else:
        uiwidget = slicer.util.loadUI(self.resourcePath('UI/JNormalUnitAssist.ui'))
    fu.set_widget(uiwidget,self) 
    reddot_path = self.resourcePath('Icons/reddot.png').replace('\\','/')
    reddot_icon = qt.QIcon(reddot_path)
    self.m_FWList.append(fu)
    self.ui.tabWidget.addTab(fu.widget,reddot_icon,""+len(self.m_FWList).__str__())
    self.ui.tabWidget.setCurrentWidget(fu.widget)
    self.refresh_tab()
    return fu

  def create_alone_widget(self,style):
    fu = FiberUnit(style)
    fu.set_widget(slicer.util.loadUI(self.resourcePath('UI/JAddFiberUnit.ui')),self) 
    return fu,fu.widget
    
  '''
    删除一页规划
  '''
  def delete_unit(self,fu):
    if fu in self.m_FWList:
      for i in range(len(self.m_FWList)):
        fu_inner = self.m_FWList[i]
        if fu_inner == fu:
          self.ui.tabWidget.removeTab(i)
      self.m_FWList.remove(fu)
      self.refresh_tab()
    else:
      for i in range(len(self.m_FWList)):
        fu_inner = self.m_FWList[i]
        if fu_inner.GetID() == fu.GetID():
          self.ui.tabWidget.removeTab(i)
          self.m_FWList.remove(fu_inner)
          break
        else:
          pass
      self.refresh_tab()
      util.removeFromParent2(fu.widget)
     
      #util.send_event_str(util.JAddFiberUnitRemvoed,fu.entry_point)
      slicer.mrmlScene.InvokeEvent(util.JAddFiberUnitRemvoed,fu.entry_point)

  '''
    当规划页发生了新增,删除等变化时,刷新标签页,没有成功创建的有一个小红点,成功创建的没有
  '''
  def refresh_tab(self):
    if not self.refresh_tab_enabled:
      return
    for i in range(len(self.m_FWList)):
      fu_inner = self.m_FWList[i]
      if fu_inner.is_not_empty():
        self.ui.tabWidget.setTabIcon(i,qt.QIcon(""))
      else:
        reddot_path = self.resourcePath('Icons/reddot.png').replace('\\','/')
        reddot_icon = qt.QIcon(reddot_path)
        self.ui.tabWidget.setTabIcon(i,reddot_icon)
      self.ui.tabWidget.setTabText(i,"导向器"+(i+1).__str__())


  def OnArchiveLoaded(self,_a,_b):
    print(f"load archive from {self.__class__.__name__}")
    nodeid = util.GetGlobalSaveValue("JAddFiber_MainNodeID")
    print("OnArchiveLoaded main nodeid is",nodeid)
    if nodeid is None:
      return
    node = util.GetNodeByID(nodeid)
    self.logic.m_Node = node  
    if node is not None:
      self.ui.btn_add_fiber.setVisible(False)
      self.ui.btn_add_fiber.setEnabled(True)
      self.ui.tabWidget0.setCurrentIndex(0)
      #util.reset_pixel_label_style(self.ui.btn_add_fiber,3)

    vals = {}
    for node in util.get_all_nodes():
      key = node.GetAttribute("fiber_unit_id")
      is_single = node.GetAttribute("is_single")
      # if is_single:
      #   continue
      if key != None:
        if key in vals:
          vals[key].append(node)
        else:
          vals[key] = [node]
    
    for key in vals: 
      self.add_archive_uint(key,vals[key])
  

  def get_single_fiber(self,sigle_item,entry_point_id=None,type=None):
    from AddFiberLib.NormalUnit import NormalUnit 
    if type == "NormalUnit":
      if util.get_from_PAAA("current_project_selector_project_name")!="SunSlicer":
        widget = slicer.util.loadUI(self.resourcePath('UI/JNormalUnit.ui'))
      else:
        widget = slicer.util.loadUI(self.resourcePath('UI/JNormalUnitAssist.ui'))
      template1ui = slicer.util.childWidgetVariables(widget)
      template = NormalUnit()
      template.set_widget(widget,self)
      template.tag = "get_single_fiber"
    else:
      raise Exception("sdlsjdksdjfk")
    if entry_point_id is not None:
      node = util.GetNodeByID(entry_point_id)
      if node is not None:
        template.init_from_single(template1ui,node,sigle_item)
    else:
     pass
    return template


  def add_archive_uint(self,id,nodelist):
    node_type = 0
    for node in nodelist:
      if node.GetAttribute("fiber_unit_type")=="entry_point":
        node_type1 = node.GetAttribute("node_type")
        if node_type1 != None:
          node_type = node_type1
        break
    print('on load node type of %s'%(node_type),len(nodelist),id)
    tmplist = node_type.split(":")
    if len(tmplist)!= 2:
      return
    utype = tmplist[0]
    class_obj = self.unit_class_maps[utype]
    fu = class_obj()
    fu.update_archive_flag = False
    self.add_unit(fu)
    fu.load_archive(id,nodelist)
    #fu.fresh_result()
    fu.style = node_type
    self.ui.tabWidget0.setCurrentIndex(0)
    self.ui.btn_add_fiber.setEnabled(True)
    self.refresh_tab()
    fu.update_archive_flag = True

  '''
    当有新的ScalarVolumeNode添加的时候,恢复初始设置
  '''
  @vtk.calldata_type(vtk.VTK_OBJECT)
  def OnMainNodeAdded(self,caller,str_event,calldata):
    self.logic.m_Node = calldata  
    self.ui.tabWidget0.setCurrentIndex(1)
    #util.reset_pixel_label_style(self.ui.btn_add_fiber,3)
    if self.logic.m_Node:
      util.SetGlobalSaveValue("JAddFiber_MainNodeID",self.logic.m_Node.GetID())

  '''
    当原有的ScalarVolumeNode删除的时候,删除所有的标签
  '''
  @vtk.calldata_type(vtk.VTK_OBJECT)
  def OnMainNodeRemoved(self,caller,str_event,calldata):
    print("JAddFiber OnMainNodeRemoved")
    self.logic.m_Node = None  
    self.ui.btn_add_fiber.setVisible(False)
    self.ui.btn_add_fiber.setEnabled(False)
    self.ui.tabWidget0.setCurrentIndex(2)
    #util.reset_pixel_label_style(self.ui.btn_add_fiber,0)
    while(len(self.m_FWList)>0):
      unit = self.m_FWList[0]
      unit.delete_unit_without_warning()
    util.SetGlobalSaveValue("JAddFiber_MainNodeID",None)
  

  def addEvent(self,bool_val):
    if bool_val:
      print("addEvent JAddFiber")
      self.ui.btn_add_fiber.connect('clicked()', self.on_choose_style)
      self.ui.btnConfirm.connect("clicked()",self.on_btnConfirm)
      self.ui.btnReturn.connect("clicked()",self.on_btnReturn)
    else:
      print("removeEvent JAddFiber")
      self.ui.btn_add_fiber.disconnect('clicked()', self.on_choose_style)
      self.ui.btnConfirm.disconnect("clicked()",self.on_btnConfirm)
      self.ui.btnReturn.disconnect("clicked()",self.on_btnReturn)

  def OnSceneDestroyEvent(self,_a,_b):
    print("on add fiber:OnSceneDestroyEvent")
    for fu in self.m_FWList:
      self.delete_unit(fu)
    self.m_FWList = []
    self.refresh_tab()

  def on_btnConfirm(self):
    # if len(self.m_FWList) > 1:
    #   util.showWarningText("最多只可以选择一个导向器,请删除额外的导向器")
    #   return
    # if len(self.m_FWList) == 0:
    #   util.send_event_str(util.GotoPrePage,"1")
    #   return
    # fu = self.m_FWList[0]
    # fu.on_btnConfirm()

    if len(self.m_FWList) == 0:
      util.send_event_str(util.GotoPrePage,"1")
      return
    ids = []
    for fu in self.m_FWList:
      if fu.entry_point:
        ids.append(fu.entry_point.GetID())
    idstr=",".join(ids)
    util.send_event_str(util.JAddFiberReturn,idstr)
    util.send_event_str(util.GotoPrePage,"1")

  def on_btnReturn(self):
    self.on_btnConfirm()

  def enter(self):
    self.addEvent(True)
    
  

  def exit(self):
    self.addEvent(False)



  def generate_final_fiber_model(self):
    fibers = []
    for unit in self.m_FWList:
      node = unit.generate_final_fiber_model()
      if node is not None:
        fibers.append(node)
    return fibers

  def show_fiber(self):
    for unit in self.m_FWList:
      unit.show_fiber()

  def hide_fiber(self):
    for unit in self.m_FWList:
      unit.hide_fiber()

  
  def on_choose_style(self):
    if len(self.btn_config) == 1:
      key = self.btn_config[0]
      btn = self.btn_maps[key]
      if not isinstance(btn, qt.QToolButton):
        btn.animateClick(0)
        return
    self.ui.tabWidget0.setCurrentIndex(1)

  def create_pushbutton(self,key,label):
    button = qt.QPushButton('执行')
    button.setText(label)
    button.setFixedHeight(51)
    button.setFixedWidth(200)
    return button

  def create_toolbutton(self,key,label):
    toolButton = qt.QToolButton()
    toolButton.setFixedSize(200, 51)
    toolButton.setToolButtonStyle(3)
    toolButton.setPopupMode(1)
    menu = qt.QMenu(toolButton)
    toolButton.setMenu(menu)
    
    

    stylesheet = ""
    stylesheet = stylesheet + "QToolButton {background-color: #525F7B;font-size: 12pt;font-family: Source Han Sans CN-Regular, Source Han Sans CN;border-radius: 4px;}"
    stylesheet = stylesheet + "QToolButton:hover {background-color: #527FD9;}"
    stylesheet = stylesheet + "QToolButton:pressed {background-color: #0D1632;}"
    stylesheet = stylesheet + "QToolButton::menu-button {background-color: transparent;width: 10px;margin: 4px;}"
    #toolButton.setStyleSheet(stylesheet)

    return toolButton,menu

  def on_normal_style1(self,add_unit=True):
    class_obj = self.unit_class_maps["NormalUnit"]
    fu = class_obj()
    fu.style = "NormalUnit"+":1"
    if add_unit:
      self.add_unit(fu)
    self.ui.tabWidget0.setCurrentIndex(0)
    self.ui.btn_add_fiber.setVisible(False)
    self.ui.btn_add_fiber.setEnabled(True)
    self.ui.label.setText("设置")
    
  
    

  def init_from_config(self):
    import json
    btns = {}
    self.left_to_right = util.getjson("JAddFiber")
    left_to_rights = self.left_to_right.split("|")
    keys = []
    funcs = []
    for bundle in left_to_rights:
      list1 = bundle.split(",")
      if len(list1) != 4:
        return
        raise Exception("error format d")
      key = list1[0]
      button_type = list1[1]
      unit_type =list1[2]
      label = list1[3]
      keys.append(key)
      if button_type == "pushbutton":
        def pushbuttonevent(utype):
            class_obj = self.unit_class_maps[utype]
            fu = class_obj()
            self.add_unit(fu)
            self.ui.tabWidget0.setCurrentIndex(0)
            self.ui.btn_add_fiber.setVisible(False)
            self.ui.btn_add_fiber.setEnabled(True)
            
        btn = self.create_pushbutton(key,label)
        btn.connect("clicked()",lambda a=unit_type:pushbuttonevent(a))
        btns[key] = btn
      if button_type == "toolbutton":
        def toolbuttonevent(button_type,utype,style):
          class_obj = self.unit_class_maps[utype]
          fu = class_obj()
          fu.style = utype+":"+style.__str__()
          self.add_unit(fu)
          self.ui.tabWidget0.setCurrentIndex(0)
          self.ui.btn_add_fiber.setVisible(False)
          self.ui.btn_add_fiber.setEnabled(True)

        btn,menu = self.create_toolbutton(key,label)
        btns[key] = btn
        labellist = label.split("&")
        index = 0
        for labeld in labellist:
          if index != 0:
            print(unit_type,index)
            menu.addAction(labeld,lambda k=button_type,a=unit_type,b=index:toolbuttonevent(k,a,b))
            if index == 1:
              btn.connect("clicked()",lambda k=button_type,a=unit_type,b=index:toolbuttonevent(k,a,b))
          else:
            btn.setText(labeld)
          index+=1
          
       
    if len(keys) == 1:
      util.addWidget2(self.ui.container,btns[keys[0]])
    elif len(keys) == 2:
      util.addWidget2(self.ui.container,btns[keys[0]])
      util.addWidget2(self.ui.container,btns[keys[1]])
    else:
      raise Exception("not support more than 2")
    
    self.btn_config = keys
    self.btn_maps = btns


  def SetFiber(self,entry_point,title=None):
    self.ui.tabWidget0.setCurrentIndex(0)
    count = self.ui.tabWidget.count
    target_fu = None
    for fu in self.m_FWList:
      if fu.entry_point == entry_point:
        target_fu = fu
    if target_fu is None:
      print("empty fiber info")
      return
    
    for i in range(count):
      widget1 = self.ui.tabWidget.widget(i)
      if widget1 == target_fu.widget:
        print("edit unit:",entry_point.GetAttribute("fiber_unit_id"),self.ui.tabWidget.currentWidget(),target_fu,i)
        self.ui.tabWidget.setCurrentIndex(i)
        
    if title:
      self.ui.label.setText(title)
    else:
      self.ui.label.setText("导向器设置")
    
  def init_ui(self):
    #util.getModuleLogic("JUITool").add_picture_to_widget(self,self.ui.btnReturn,"back.png")
    #util.getModuleLogic("JUITool").add_picture_to_widget(self,self.ui.btnConfirm,"confrim.png")
    
    self.init_from_config()

    self.ui.tabWidget0.tabBar().hide()
    self.ui.tabWidget0.tabBar().setCurrentIndex(1)
    
    vn = util.getFirstNodeByClass("vtkMRMLScalarVolumeNode")
    self.logic.m_Node = vn
    if vn is not None:
      self.ui.btn_add_fiber.setEnabled(True)
      self.ui.btn_add_fiber.setVisible(False)
      #util.reset_pixel_label_style(self.ui.btn_add_fiber,3)
    else:
      self.ui.btn_add_fiber.setEnabled(False)
      self.ui.btn_add_fiber.setVisible(False)
    self.ui.tabWidget0.setCurrentIndex(0)
    self.ui.tabWidget0.setStyleSheet("QTabWidget::pane { border: none; }")
    self.ui.btnReturn.setVisible(False)
    self.ui.tabWidget.setStyleSheet("QTabBar::tab { width: 100px; }")
    self.ui.btnConfirm.setVisible(False)
    self.ui.tabWidget.tabBar().hide()
    return

  def create_puncture(self,param_dict,key,entry_point_world,target_point_world,radius,thick,length):
      distance = np.sqrt( (entry_point_world[0]-target_point_world[0])*(entry_point_world[0]-target_point_world[0])+
                              (entry_point_world[1]-target_point_world[1])*(entry_point_world[1]-target_point_world[1])+
                              (entry_point_world[2]-target_point_world[2])*(entry_point_world[2]-target_point_world[2])
                              )
      if key not in param_dict:
        param_dict[key] = {}
      dict1 = param_dict[key]
      print("入点到靶点距离:"+round(distance, 2).__str__()+"mm")
      if "fiber_model"in dict1 and dict1["fiber_model"] and "fiber_model_inner" in dict1 and dict1["fiber_model_inner"]:
          
        util.getModuleLogic("JTransformTool").rotate_fiber_model_to_vector(dict1["fiber_model"],entry_point_world,target_point_world,length)
        old_transform_node = dict1["fiber_model_inner"].GetParentTransformNode()
        util.RemoveNode(old_transform_node)
        transform_node = dict1["fiber_model"].GetParentTransformNode()
        dict1["fiber_model_inner"].SetAndObserveTransformNodeID(transform_node.GetID())
      else:
        
        fiber_model,fiber_model_inner = self.on_add_normal_fiber(entry_point_world,target_point_world,qt.QColor.fromRgbF(1,1,1),length,radius/2,thick)
        dict1["fiber_model"]=fiber_model
        dict1["fiber_model_inner"] = fiber_model_inner
        util.GetDisplayNode(fiber_model).SetSelectable(False)
        util.GetDisplayNode(fiber_model_inner).SetSelectable(False)
  
  def add_cylinder(self,radius,inner_radius,height,red=1,green=1,blue=1):
        print("add_cylinder",radius,inner_radius,height)
        cy_source = vtk.vtkCylinderSource()
        cy_source.SetHeight(height)
        cy_source.SetRadius(radius)
        cy_source.SetResolution(160)
        modelNode = slicer.modules.models.logic().AddModel(cy_source.GetOutputPort())
        modelNode.GetDisplayNode().SetColor([red,green,blue])
        modelNode.GetDisplayNode().SetVisibility2D(True)
        modelNode.GetDisplayNode().SetSliceIntersectionThickness(2)

        cy_source_inner = vtk.vtkCylinderSource()
        cy_source_inner.SetHeight(height)
        cy_source_inner.SetRadius(inner_radius)
        cy_source_inner.SetResolution(160)
        modelNode_inner = slicer.modules.models.logic().AddModel(cy_source_inner.GetOutputPort())
        
        modelNode_inner.GetDisplayNode().SetSliceIntersectionThickness(2)
        modelNode.SetAttribute("JAddFiberWidget_Fiber","1")
        modelNode_inner.SetAttribute("JAddFiberWidget_FiberInner","1")
        return modelNode,modelNode_inner
  
  def delete_normal_fiber(self,param_dict,key):
    if key not in param_dict:
        param_dict[key] = {}
    dict1 = param_dict[key]
      
    if dict1["fiber_model"] is not None:
      transform_node = dict1["fiber_model"].GetParentTransformNode()
      if transform_node is not None:
        util.RemoveNode(transform_node)
    if dict1["fiber_model"]:
      util.RemoveNode(dict1["fiber_model"])
      dict1["fiber_model"]=None
    if dict1["fiber_model_inner"]:
      util.RemoveNode(dict1["fiber_model_inner"])
      dict1["fiber_model_inner"]=None
      
  def on_add_normal_fiber(self,entry_point_world,target_point_world,qcolor,length,radius,thick):
      # model_node = self.add_hollow_cylinder(radius,radius+thick,length,qcolor.red()/255.0,qcolor.green()/255.0,qcolor.blue()/255.0,)
      print("on_add_normal_fiber")
      import slicer.util as util
      slicer.app.applicationLogic().PauseRender()
      model_node,modelNode_inner = self.add_cylinder(radius+thick,radius,length,qcolor.red()/255.0,qcolor.green()/255.0,qcolor.blue()/255.0)
      util.getModuleLogic("JTransformTool").rotate_fiber_model_to_vector(model_node,entry_point_world,target_point_world,length)
      transform_node = model_node.GetParentTransformNode()
      modelNode_inner.SetAndObserveTransformNodeID(transform_node.GetID())
      slicer.app.applicationLogic().ResumeRender()
      model_node.SetName("outer_normal_fiber")
      modelNode_inner.SetName("inner_normal_fiber")
      return model_node,modelNode_inner
    
class JAddFiberLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
  m_Widget = None
  m_Node = None
  def __init__(self):
    """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
    ScriptedLoadableModuleLogic.__init__(self)
  

  def setWidget(self,widget):
    self.m_Widget = widget

  
  



  def generate_final_fiber_model(self):
    return self.m_Widget.generate_final_fiber_model()

  def hide_fiber(self):
    self.m_Widget.hide_fiber()

  def show_fiber(self):
    self.m_Widget.show_fiber()

  def hide_reload(self,show):
    pass

  
  
    

 
 