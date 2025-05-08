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
from Base.JBaseExtension import JBaseExtensionWidget

class JPC_Template:
  node = None
  ui = None
  widget =None
  main = None
  def __init__(self,main,widget,in_ui) -> None:
    self.ui = in_ui
    self.main = main
    self.widget = widget

class JPC_Normal(JPC_Template):
  manager  = None
  item = None
  paras = {}
  ShrinkHeight = 64
  ShrinkWidth = 100
  def __init__(self, main, in_present,in_ui) -> None:
    super().__init__(main,in_present,in_ui)

  def init(self,node,manager,item):
    if node is None:
      return
    if node == self.node:
      return
    self.manager = manager
    self.item = item
    self.node = node
    
    vs = False
    if node.GetAttribute("markups_measure_disalble") is None:
      vs = True
      
    if node.IsA(util.vtkMRMLMarkupsLineNode):
      self.ui.markups_name.setText("线段")
      iconpath = util.get_resource("tool_line.png")
      node.GetMeasurement('length').SetEnabled(vs)
    elif node.IsA(util.vtkMRMLMarkupsAngleNode):
      self.ui.markups_name.setText("角度")
      iconpath = util.get_resource("tool_angle.png")
      node.GetMeasurement('angle').SetEnabled(vs)
    elif node.IsA(util.vtkMRMLMarkupsClosedCurveNode):
      self.ui.markups_name.setText("面积")
      iconpath = util.get_resource("tool_closed_curve.png")
      node.GetMeasurement('area').SetEnabled(vs)
      node.GetMeasurement('length').SetEnabled(False)
    elif node.IsA(util.vtkMRMLMarkupsCurveNode):
      self.ui.markups_name.setText("曲线")
      node.GetMeasurement('length').SetEnabled(vs)
      iconpath = util.get_resource("tool_curve.png")
    elif node.IsA(util.vtkMRMLMarkupsPlaneNode):
      self.ui.markups_name.setText("矩形")
      node.GetMeasurement('area').SetEnabled(vs)
      iconpath = util.get_resource("tool_area.png")
    elif node.IsA(util.vtkMRMLMarkupsROINode):
      self.ui.markups_name.setText("ROI")
      node.GetMeasurement('volume').SetEnabled(vs)
      iconpath = util.get_resource("tool_roi.png")
      
    util.add_pixelmap_to_label(iconpath,self.ui.lblImage)
    
    if node.IsA(util.vtkMRMLMarkupsROINode):
      txt = ""
      transformMatrix = node.GetObjectToWorldMatrix()
      center_world = [0,0,0]
      node.GetCenterWorld(center_world)
      size_world = [0,0,0]
      node.GetSizeWorld(size_world)
      txt = txt + "变换矩阵" + "\n"
      txt = txt + " [{:.2f}, {:.2f}, {:.2f}, {:.2f}]".format(
          transformMatrix.GetElement(0, 0),
          transformMatrix.GetElement(0, 1),
          transformMatrix.GetElement(0, 2),
          transformMatrix.GetElement(0, 3)
      ) + "\n"
      txt = txt + " [{:.2f}, {:.2f}, {:.2f}, {:.2f}]".format(
          transformMatrix.GetElement(1, 0),
          transformMatrix.GetElement(1, 1),
          transformMatrix.GetElement(1, 2),
          transformMatrix.GetElement(1, 3)
      ) + "\n"
      txt = txt + " [{:.2f}, {:.2f}, {:.2f}, {:.2f}]".format(
          transformMatrix.GetElement(2, 0),
          transformMatrix.GetElement(2, 1),
          transformMatrix.GetElement(2, 2),
          transformMatrix.GetElement(2, 3)
      ) + "\n"
      txt = txt + " [{:.2f}, {:.2f}, {:.2f}, {:.2f}]".format(
          transformMatrix.GetElement(3, 0),
          transformMatrix.GetElement(3, 1),
          transformMatrix.GetElement(3, 2),
          transformMatrix.GetElement(3, 3)
      ) + "\n"
      txt = txt + "中心点:" + " [{:.2f}, {:.2f}, {:.2f}]".format(
          center_world[0],
          center_world[1],
          center_world[2]
      ) + "\n"
      txt = txt + "长宽高:"+ " [{:.2f}, {:.2f}, {:.2f}]".format(
          size_world[0],
          size_world[1],
          size_world[2]
      ) 
      self.ui.propertyText.setText(txt)
    else:
      txt = node.GetPropertiesLabelText()
      txt = self.replace_suffix(txt, "cm2", "cm²")
      self.ui.propertyText.setText(txt)
      
    self.ui.BtnJump.connect('clicked()', self.on_jump)
    self.ui.BtnDelete.connect('clicked()', self.on_delete)
  
  def replace_suffix(self,input_string, old_suffix, new_suffix):
    if input_string.endswith(old_suffix):
        # 如果字符串以 old_suffix 结尾，则进行替换
        modified_string = input_string[:-len(old_suffix)] + new_suffix
        return modified_string
    else:
        # 如果字符串不以 old_suffix 结尾，则返回原始字符串
        return input_string
      
  def on_delete(self):
    if self.node is None:
      return
    scene_view_node_id = self.node.GetAttribute("scene_view_node_id")
    if scene_view_node_id:
      node = util.GetNodeByID(scene_view_node_id)
      util.RemoveNode(node)
    self.manager.remove_node(self.node)

  def on_jump(self):
    if self.node is None:
      return
    scene_view_node_id = self.node.GetAttribute("scene_view_node_id")
    if scene_view_node_id:
      scene_view_node = util.GetNodeByID(scene_view_node_id)
      print("on jump to scene view:",scene_view_node_id)
      if scene_view_node:
        scene_view_node.AddMissingNodes()
        util.getModuleLogic("SceneViews").RestoreSceneView(scene_view_node_id,False)
    # point_World = [0,0,0]
    # self.node.GetNthControlPointPositionWorld(0, point_World)
    # if point_World != [0,0,0]:
    #   slicer.modules.markups.logic().JumpSlicesToLocation(point_World[0], point_World[1], point_World[2], True)

  def shrink(self):
    if self.node.IsA(util.vtkMRMLMarkupsROINode):
      self.item.setSizeHint(qt.QSize(self.ShrinkWidth , 180))
    else:
      self.item.setSizeHint(qt.QSize(self.ShrinkWidth , self.ShrinkHeight))

class MarkupsManager:
  #MarkupsManager 对应的 UI
  m_ui = None
  logic = None
  main = None
  m_TemplateList = {}
  m_Index = -1
  m_Scene = None
  resourcelist={}
  old_strict_name = ""
  def __init__(self,in_main,in_ui,scene):
    self.main = in_main
    self.m_ui = in_ui
    self.m_Scene = scene
    self.logic = self.main.logic

    util.getModuleLogic("JUITool").create_labeled_clicked_button(self.main,self.m_ui.btnFresh,"tool_fresh.png","刷新列表",rlist=self.resourcelist)
    util.getModuleLogic("JUITool").create_labeled_clicked_button(self.main,self.m_ui.btnReturn,"tool_return.png","返回",rlist=self.resourcelist)
    slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeRemovedEvent, self.onNodeRemove)
    self.m_ui.btnReturn.connect('clicked()', self.on_return)
    self.m_ui.btnFresh.connect('clicked()', self.fresh_list)
    self.m_ui.ListWidget.connect('currentItemChanged(QListWidgetItem*,QListWidgetItem*)', self.on_change)
    self.m_ui.ListWidget.setSpacing(0)

  def remove_node(self,node):
    util.RemoveNode(node)
    

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def onNodeRemove(self,caller, event, calldata):
    self.fresh_list()
    
  def on_change(self,item,_):
    pass

  def on_return(self):
    util.send_event_str(util.GotoPrePage,self.m_Index.__str__())

  def get_resource_list(self):
    txt = ""
    for key in self.resourcelist:
      value = self.resourcelist[key]
      txt = txt+key+":\t\t"+value+"\n"
    filepath = util.get_resource("markups_list.txt",use_default_path=False)
    if txt != "":
      with open(filepath, "w") as file:
        file.write(txt)
    return txt

  def fresh_list(self,strict_outer_name='current'):
    #外部调用的时候
    if strict_outer_name == 'current' and self.old_strict_name!=util.current_main_module_name:
      print("fresh_list forbidden",self.old_strict_name,util.current_main_module_name)
      return
    if strict_outer_name != 'current'  and strict_outer_name != util.current_main_module_name:
      print("fresh_list forbidden2",strict_outer_name,util.current_main_module_name)
      return
    print("fresh list inner",strict_outer_name)
    self.old_strict_name = util.current_main_module_name
    
    self.m_ui.ListWidget.clear()
    self.m_TemplateList = {}
    strict_name = self.old_strict_name
    model_list = util.getNodesByClass(util.vtkMRMLMarkupsNode)
    list1 = []
    for item in model_list:
      if item.GetAttribute("not_show_in_manager") == "1":
        continue
      if item.IsA("vtkMRMLMarkupsFiducialNode"):
        pass
      else:
        current_main_module_name = item.GetAttribute("current_main_module_name")
        if current_main_module_name == strict_name:
          #util.ShowNode(item)
          list1.append(item)
        else:
          print(item.GetID(),current_main_module_name,strict_name,strict_outer_name)
          #util.HideNode(item)
        
    model_list = list1

    print("on fresh markups fresh list:",len(model_list))
    for model in model_list:
      displaynode = util.GetDisplayNode(model)
      if displaynode.GetVisibility() == False:
        continue
      if model.GetAttribute("not_show_in_manager") is not None:
        continue
      template = self.main.get_new_widget('normal_widget')
      item = qt.QListWidgetItem(self.m_ui.ListWidget)
      template.init(model,self,item)
      self.m_ui.ListWidget.setItemWidget(item,template.widget)
      self.m_ui.ListWidget.addItem(item)
      self.m_TemplateList[model] = template
      template.shrink()
    self.get_resource_list()
#
# JManagerMarkups
#

class JManagerMarkups(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "JManagerMarkups"  # TODO: make this more human readable by adding spaces
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
# JManagerMarkupsWidget
#

class JManagerMarkupsWidget(JBaseExtensionWidget):
  inner_manager = None
  def init_ui(self):
    self.ensure_manager_loaded()

  def ensure_manager_loaded(self):
    if self.inner_manager is None:
      uiwidget,manager = self.create_model_manager("markups_manager")
      util.addWidget2(self.ui.widget,uiwidget)
      self.inner_manager = manager
  
  def create_model_manager(self,name):
    if name == "markups_manager":
      uiWidget = util.loadUI(self.resourcePath('UI/Markups_Manager.ui'))
      #uiWidget.setFixedSize(400,1080)
      m_ui = slicer.util.childWidgetVariables(uiWidget)
      manager = MarkupsManager(self,m_ui,slicer.mrmlScene)
      return uiWidget,manager

  def get_new_widget(self,name):
    if name == "normal_widget":
      template1 = slicer.util.loadUI(self.resourcePath('UI/JPC_Normal.ui'))
      template1ui = slicer.util.childWidgetVariables(template1)
      widget = JPC_Normal(self,template1,template1ui)
      return widget

  def point_collision_detection_with_segmentation(self,point_node,segmentationNode):
    sliceViewWidget = slicer.app.layoutManager().sliceWidget('Red')
    segmentationsDisplayableManager = sliceViewWidget.sliceView().displayableManagerByClassName("vtkMRMLSegmentationsDisplayableManager2D")
    entry_point_world = [0,0,0]
    point_node.GetNthControlPointPositionWorld(0, entry_point_world)
    segmentIdsP = vtk.vtkStringArray()
    segmentationsDisplayableManager.GetVisibleSegmentsForPosition(entry_point_world, segmentationNode.GetDisplayNode(), segmentIdsP)
    if segmentIdsP.GetNumberOfValues()>0:
      return True
    else:
      return False
  
  def land_point_on_model(self,point,model):
    nOfFiducialPoints = point.GetNumberOfFiducials()
    if nOfFiducialPoints!= 1:
      raise Exception("only support fiducai number of 1")

    logic = util.getModuleLogic("FiducialsToModelDistance")
    pointDistances, labels, closest_points1 = logic.pointDistancesLabelsFromSurface(point, model)
    point.SetNthControlPointPositionWorld(0,closest_points1[0])


  

  