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
#
# JRemoveSkullBoard
#

class JRemoveSkullBoard(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "JRemoveSkullBoard"  # TODO: make this more human readable by adding spaces
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
# JRemoveSkullBoardWidget
#

class JRemoveSkullBoardWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  TagMaps = {}
  m_SegmentationNode = None
  m_ModelNode = None
  m_BoardSegmentationNode = None
  m_MaskBoardSegmentationNode = None
  m_MarginedNode = None
  m_MaskMarginedNode = None
  m_OutNode = None
  apply_button = None
  thickness= "3"
  min_skin = -400
  max_skin = 100000
  def __init__(self, parent=None):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)  # needed for parameter node observation
    self.logic = None

  def setup(self):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    self.logic = JRemoveSkullBoardLogic()
    self.logic.setWidget(self)

    
    
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/JRemoveSkullBoard.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)
    
   
    uiWidget.setMRMLScene(slicer.mrmlScene)
    
    
    

    self.init_ui()
  


  def enter(self):
    self.addEvent(True)

  def exit(self):
    self.addEvent(False)


  def addEvent(self,bool_val):
    if bool_val:
      print("removeEvent JAddFiber")
      if util.MainNodeLoadedEvent in self.TagMaps:
        self.addEvent(False)

      self.TagMaps[util.MainNodeLoadedEvent] = slicer.mrmlScene.AddObserver(util.MainNodeLoadedEvent, self.OnMainNodeAdded)
      self.TagMaps[util.MainNodeRemovedEvent] = slicer.mrmlScene.AddObserver(util.MainNodeRemovedEvent, self.OnMainNodeRemoved)
      self.TagMaps[util.ArchiveFileLoadedEvent] = slicer.mrmlScene.AddObserver(util.ArchiveFileLoadedEvent, self.OnArchiveLoaded)
      self.TagMaps[util.ThresholdApplyed] = slicer.mrmlScene.AddObserver(util.ThresholdApplyed, self.OnThresholdApplyed)
      self.ui.btnReload.connect('clicked()', self.onReload)
      self.ui.pushButton.connect('clicked()', self.on_threshold_start)
    else:
      print("removeEvent JAddFiber")
      slicer.mrmlScene.RemoveObserver(self.TagMaps[util.MainNodeLoadedEvent])
      slicer.mrmlScene.RemoveObserver(self.TagMaps[util.MainNodeRemovedEvent])
      slicer.mrmlScene.RemoveObserver(self.TagMaps[util.ArchiveFileLoadedEvent])
      self.ui.btnReload.clicked.disconnect()
      self.ui.pushButton.clicked.disconnect()
  
  '''
    当有新的ScalarVolumeNode添加的时候,恢复初始设置
  '''
  @vtk.calldata_type(vtk.VTK_OBJECT)
  def OnMainNodeAdded(self,caller,str_event,calldata):
    self.logic.m_Node = calldata  
    if self.logic.m_Node:
      util.SetGlobalSaveValue("JRemoveSkullBoard_MainNodeID",self.logic.m_Node.GetID())
    self.init_after_load()
    
  
  '''
    当原有的ScalarVolumeNode删除的时候,删除所有的标签
  '''
  @vtk.calldata_type(vtk.VTK_OBJECT)
  def OnMainNodeRemoved(self,caller,str_event,calldata):
    self.logic.m_Node = None  
    util.SetGlobalSaveValue("JRemoveSkullBoard_MainNodeID",None)


  def on_threshold_start(self):
    print("on_threshold_start")
    if self.logic.m_Node is None:
      util.showWarningText("请先加载图像")
      return
    self.threshold_tool_1.btn.animateClick(1)

  def OnArchiveLoaded(self,_a,_b):
    nodeid = util.GetGlobalSaveValue("JRemoveSkullBoard_MainNodeID")
    print("OnArchiveLoaded JRemoveSkullBoard main nodeid is",nodeid)
    if nodeid is None:
      return
    node = util.GetNodeByID(nodeid)
    self.logic.m_Node = node  

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def OnThresholdApplyed(self,_a,_b,calldata):
    node_name = calldata.GetAttribute("value")
    node = util.getFirstNodeByName(node_name)
    util.ShowNode3D(node)
    self.goto_step(1)

  def init_ui(self):
    pass


  def DoStripToGetSkin(self,volume,min_skin1,max_skin1,thickness="3"):
    self.thickness = thickness
    self.min_skin = min_skin1
    self.max_skin = max_skin1
    import slicer.util as util
    util.RemoveNodeByName("skin_segment")
    util.RemoveNodeByName("m_SkinBoardSegmentationNode")
    util.RemoveNodeByName("m_SkinMarginedNode")
    util.RemoveNodeByName("stripeed_skin_basic")
    util.RemoveNodeByName("皮肤")
    util.RemoveNodeByName("FullHeadSegmentationNode")
    util.RemoveNodeByName("皮肤模型")
    
    util.send_event_str(util.ProgressStart,"正在分割皮肤")
    util.send_event_str(util.ProgressValue,"10")
    self.logic.m_Node = volume
    if util.getFirstNodeByName("skull_skin_segmentation_node") is None:
      self.m_SegmentationNode = util.CreateDefaultSegmentationNode("skull_skin_segmentation_node")
      self.m_SegmentationNode.SetAttribute("show_in_manager","1")
      self.m_SegmentationNode.SetAttribute("alias_name","初始皮肤")
      util.hidden(self.m_SegmentationNode,True)
    else:
      self.m_SegmentationNode = util.getFirstNodeByName("skull_skin_segmentation_node")
    util.send_event_str(util.ProgressValue,"20")
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(self.m_SegmentationNode)
    segmentEditorWidget.setSourceVolumeNode(volume)
    segmentEditorWidget.setActiveEffectByName("Threshold")
    
    effect = segmentEditorWidget.activeEffect()
    lo, hi = util.GetScalarRange(volume)
    effect.setParameter("MinimumThreshold", 180)
    effect.setParameter("MaximumThreshold", hi)
    effect.self().onApply()
    
    util.ShowNode3D(self.m_SegmentationNode)
    util.send_event_str(util.ProgressValue,"40")
    self.goto_skin_step(1)
    util.singleShot(110,lambda:util.reinit3D())
  
  
  def goto_skin_step(self,step):
    print("goto_skin_step:",step)
    if step == 1:
      util.send_event_str(util.ProgressValue,"50")
      cloned_node = util.clone(self.m_SegmentationNode)
      cloned_node.SetName("skull_skin")
      util.getModuleLogic('JSegmentEditorTool').islands_max(self.logic.m_Node,cloned_node)
      cloned_node2 = util.clone(self.m_SegmentationNode)
      util.getModuleLogic('JSegmentEditorTool').substract(self.logic.m_Node,cloned_node2,cloned_node)
      
      util.RemoveNode(cloned_node)
      self.m_SkinBoardSegmentationNode = cloned_node2
      self.m_SkinBoardSegmentationNode.SetName("m_SkinBoardSegmentationNode")
      util.hidden(self.m_SkinBoardSegmentationNode,True)
      util.HideNode(self.m_SegmentationNode)
      self.goto_skin_step(2)
    if step == 2:
      
      util.send_event_str(util.ProgressValue,"60")
      cloned_node = util.clone(self.m_SkinBoardSegmentationNode)
      util.getModuleLogic('JSegmentEditorTool').margin_out(self.logic.m_Node,cloned_node)
      cloned_node.SetName("m_SkinMarginedNode")
      util.hidden(cloned_node,True)
      util.HideNode(self.m_SkinBoardSegmentationNode)
      self.m_SkinMarginedNode = cloned_node
      util.HideNode(self.m_SkinMarginedNode)
      self.goto_skin_step(3)
    if step == 3:
      
      util.send_event_str(util.ProgressValue,"70")
      out_node = util.AddNewNodeByClass(util.vtkMRMLScalarVolumeNode)
      out_node.SetName("stripeed_skin_basic")
      util.getModuleLogic('JSegmentEditorTool').mask_volume(self.logic.m_Node,self.m_SkinMarginedNode,self.logic.m_Node,out_node)
      self.m_OutNode = out_node
      self.goto_skin_step(4)
    if step == 4:
      
      util.send_event_str(util.ProgressValue,"80")
      util.RemoveNodeByName("皮肤")
      util.RemoveNodeByName("FullHeadSegmentationNode")
      self.m_SegmentationNode = util.CreateDefaultSegmentationNode("皮肤")
      full_head_segment = util.CreateDefaultSegmentationNode("FullHeadSegmentationNode")
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setSegmentationNode(self.m_SegmentationNode)
      segmentEditorWidget.setSourceVolumeNode(self.m_OutNode)
      segmentEditorWidget.setActiveEffectByName("Threshold")
      self.m_SegmentationNode.SetAttribute("master_node",self.m_OutNode.GetID())
      effect = segmentEditorWidget.activeEffect()
      m_ActiveEffect = effect
      effect.setParameter("MinimumThreshold", self.min_skin)
      effect.setParameter("MaximumThreshold", self.max_skin)
      m_ActiveEffect.self().onApply()
      
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setSegmentationNode(full_head_segment)
      segmentEditorWidget.setSourceVolumeNode(self.m_OutNode)
      segmentEditorWidget.setActiveEffectByName("Threshold")
      full_head_segment.SetAttribute("master_node",self.m_OutNode.GetID())
      effect = segmentEditorWidget.activeEffect()
      m_ActiveEffect = effect
      effect.setParameter("MinimumThreshold", self.min_skin)
      effect.setParameter("MaximumThreshold", self.max_skin)
      m_ActiveEffect.self().onApply()

      util.getModuleLogic("JSegmentEditorTool").islands_max(self.logic.m_Node,self.m_SegmentationNode)
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setSegmentationNode(self.m_SegmentationNode)
      segmentEditorWidget.setSourceVolumeNode(self.logic.m_Node)
      segmentEditorWidget.setActiveEffectByName("Hollow")
      effect = segmentEditorWidget.activeEffect()
      effect.setParameter("ShellThicknessMm", self.thickness)
      effect.setParameter("ShellMode", 'OUTSIDE_SURFACE')
      effect.self().onApply()
      util.getModuleLogic('JSegmentEditorTool').islands_max(self.logic.m_Node,self.m_SegmentationNode)
      model_node = util.convert_segment_to_model(self.m_SegmentationNode)
      model_node.SetName("皮肤模型")
      model_node.SetAttribute("alias_name","皮肤模型")
      self.m_SegmentationNode.SetAttribute("alias_name","皮肤")
      model_node.SetAttribute("bind_segment",self.m_SegmentationNode.GetID())
      model_node.SetAttribute("full_head_segment",full_head_segment.GetID())
      util.HideNode(self.m_SegmentationNode)
      util.HideNode(full_head_segment)
      self.m_ModelNode = model_node
      self.goto_skin_step(5)
    if step == 5:
      slicer.mrmlScene.InvokeEvent(util.JRemoveSkullBoardWidgetMaskResult,self.m_ModelNode)
      util.send_event_str(util.ProgressValue,"100")
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setActiveEffectByName("None")
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
  def DoStripToGetMask(self,volume,thickness="3"):
    self.thickness = thickness
    import slicer.util as util
    util.RemoveNodeByName("m_MaskBoardSegmentationNode")
    util.RemoveNodeByName("m_MaskMarginedNode")
    util.RemoveNodeByName("面具模型")
    util.RemoveNodeByName("stripeed_mask_basic")
    util.RemoveNodeByName("FullHeadSegmentationNode")
    util.RemoveNodeByName("skull_mask_segmentation_node")
    util.RemoveNodeByName("面具")
    util.send_event_str(util.ProgressStart,"正在分割。")
    util.send_event_str(util.ProgressValue,"10")
    self.logic.m_Node = volume
    if util.getFirstNodeByName("skull_mask_segmentation_node") is None:
      self.m_SegmentationNode = util.CreateDefaultSegmentationNode("skull_mask_segmentation_node")
      self.m_SegmentationNode.SetAttribute("show_in_manager","1")
      self.m_SegmentationNode.SetAttribute("alias_name","初始面具")
      util.hidden(self.m_SegmentationNode,True)
    else:
      self.m_SegmentationNode = util.getFirstNodeByName("skull_mask_segmentation_node")
    util.send_event_str(util.ProgressValue,"20")
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(self.m_SegmentationNode)
    segmentEditorWidget.setSourceVolumeNode(volume)
    segmentEditorWidget.setActiveEffectByName("Threshold")
    print(self.m_SegmentationNode.GetID())
    print(volume.GetID())
    effect = segmentEditorWidget.activeEffect()
    lo, hi = util.GetScalarRange(volume)
    effect.setParameter("MinimumThreshold", 180)
    effect.setParameter("MaximumThreshold", hi)
    effect.self().onApply()
    
    util.ShowNode3D(self.m_SegmentationNode)
    util.send_event_str(util.ProgressValue,"40")
    self.goto_mask_step(1)
    util.singleShot(110,lambda:util.reinit3D())
    
    

  def DoStripToGetBone(self,volume, min_skin1,max_skin1,thickness="3"):
    import slicer.util as util
    self.thickness = thickness
    self.min_skin = min_skin1
    self.max_skin = max_skin1
    util.RemoveNodeByName("m_BoneBoardSegmentationNode")
    util.RemoveNodeByName("m_BoneMarginedNode")
    util.RemoveNodeByName("骨骼模型")
    util.RemoveNodeByName("stripeed_bone_basic")
    util.RemoveNodeByName("skull_bone_segmentation_node")
    util.RemoveNodeByName("颅骨")

    util.send_event_str(util.ProgressStart,"正在分割骨骼")
    util.send_event_str(util.ProgressValue,"10")
    self.logic.m_Node = volume
    if util.getFirstNodeByName("skull_bone_segmentation_node") is None:
      self.m_SegmentationNode = util.CreateDefaultSegmentationNode("skull_bone_segmentation_node")
      self.m_SegmentationNode.SetAttribute("show_in_manager","1")
      self.m_SegmentationNode.SetAttribute("alias_name","init_bone")
      util.hidden(self.m_SegmentationNode,True)
    else:
      self.m_SegmentationNode = util.getFirstNodeByName("skull_bone_segmentation_node")
    util.send_event_str(util.ProgressValue,"20")
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(self.m_SegmentationNode)
    segmentEditorWidget.setSourceVolumeNode(volume)
    segmentEditorWidget.setActiveEffectByName("Threshold")
    effect = segmentEditorWidget.activeEffect()
    lo, hi = util.GetScalarRange(volume)
    effect.setParameter("MinimumThreshold", 180)
    effect.setParameter("MaximumThreshold", hi)
    effect.self().onApply()
    
    util.ShowNode3D(self.m_SegmentationNode)
    util.send_event_str(util.ProgressValue,"40")
    #self.goto_bone_step(1)
    self.m_SegmentationNode.SetName("颅骨")
    self.m_SegmentationNode.SetAttribute("alias_name","骨骼")
    util.send_event_str(util.ProgressValue,"100")
    util.singleShot(110,lambda:util.reinit3D())
  
  def init_after_load(self):
    if util.getFirstNodeByName("skull_segmentation_node") is None:
      self.m_SegmentationNode = util.CreateDefaultSegmentationNode("skull_segmentation_node")
      
      self.m_SegmentationNode.SetAttribute("show_in_manager","1")
      self.m_SegmentationNode.SetAttribute("alias_name","初始颅骨")
      
    self.threshold_tool_1,layout,self.apply_button = util.getModuleWidget('JSegmentEditorTool').add_threshold_tool(self.ui.pushButton)
    self.ui.widget_2.setLayout(layout)
    self.threshold_tool_1.para["master_node_name"]=self.logic.m_Node.GetName()
    self.threshold_tool_1.para["segment_node_name"]="skull_segmentation_node"
    self.threshold_tool_1.para["min"]=180
    #self.threshold_tool_1.btn.setVisible(False)
  
  def goto_step(self,step):
    print("goto_step:",step)
    if step == 1:
      util.send_event_str(util.ProgressValue,"50")
      cloned_node = util.clone(self.m_SegmentationNode)
      cloned_node.SetName("skull_1")
      util.getModuleLogic('JSegmentEditorTool').islands_max(self.logic.m_Node,cloned_node)
      cloned_node2 = util.clone(self.m_SegmentationNode)
      util.getModuleLogic('JSegmentEditorTool').substract(self.logic.m_Node,cloned_node2,cloned_node)
      
      util.RemoveNode(cloned_node)
      self.m_BoardSegmentationNode = cloned_node2
      self.m_BoardSegmentationNode.SetName("m_BoardSegmentationNode")
      # util.getModuleLogic('JSegmentEditorTool').remove_island_smaller_than(self.logic.m_Node,self.m_BoardSegmentationNode)
      
      util.HideNode(self.m_SegmentationNode)
      self.goto_step(2)
    if step == 2:
      
      util.send_event_str(util.ProgressValue,"60")
      cloned_node = util.clone(self.m_BoardSegmentationNode)
      util.getModuleLogic('JSegmentEditorTool').margin_out(self.logic.m_Node,cloned_node)
      cloned_node.SetName("m_MarginedNode")
      util.HideNode(self.m_BoardSegmentationNode)
      self.m_MarginedNode = cloned_node
      util.HideNode(self.m_MarginedNode)
      self.goto_step(3)
    if step == 3:
      
      util.send_event_str(util.ProgressValue,"70")
      out_node = util.AddNewNodeByClass(util.vtkMRMLScalarVolumeNode)
      out_node.SetName("stripeed_board_basic")
      util.getModuleLogic('JSegmentEditorTool').mask_volume(self.logic.m_Node,self.m_MarginedNode,self.logic.m_Node,out_node)
      self.m_OutNode = out_node
      self.goto_step(4)
    if step == 4:
      
      util.send_event_str(util.ProgressValue,"80")
      self.m_SegmentationNode = util.CreateDefaultSegmentationNode("HeadSegmentation")
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setSegmentationNode(self.m_SegmentationNode)
      segmentEditorWidget.setSourceVolumeNode(self.m_OutNode)
      segmentEditorWidget.setActiveEffectByName("Threshold")
      self.m_SegmentationNode.SetAttribute("master_node",self.m_OutNode.GetID())
      effect = segmentEditorWidget.activeEffect()
      m_ActiveEffect = effect
      lo, hi = util.GetScalarRange(self.m_OutNode) 
      tmp = -400
      tmp = int(util.settingsValue("PDuruofei/le_skin_threshold",-400))
      
      effect.setParameter("MinimumThreshold", tmp)
      effect.setParameter("MaximumThreshold", hi)
      m_ActiveEffect.self().onApply()

      util.getModuleLogic("JSegmentEditorTool").islands_max(self.logic.m_Node,self.m_SegmentationNode)
      util.HideNode(self.m_SegmentationNode)
      model_node = util.convert_segment_to_model(self.m_SegmentationNode)
      model_node.SetName("头部模型")
      model_node.SetAttribute("alias_name","头部模型")
      self.m_SegmentationNode.SetAttribute("alias_name","头部")

      model_node.SetAttribute("bind_segment",self.m_SegmentationNode.GetID())
      self.m_ModelNode = model_node
      self.goto_step(5)
    if step == 5:
      self.m_ModelNode.SetAttribute("jduruofei_name","头部模型")
      slicer.mrmlScene.InvokeEvent(util.JRemoveSkullBoardWidgetResult,self.m_ModelNode)
      util.send_event_str(util.ProgressValue,"100")
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setActiveEffectByName("None")
      

  def goto_bone_step(self,step):
    print("goto_bone_step:",step)
    if step == 1:
      util.send_event_str(util.ProgressValue,"50")
      cloned_node = util.clone(self.m_SegmentationNode)
      cloned_node.SetName("skull_1")
      util.getModuleLogic('JSegmentEditorTool').islands_max(self.logic.m_Node,cloned_node)
      cloned_node2 = util.clone(self.m_SegmentationNode)
      util.getModuleLogic('JSegmentEditorTool').substract(self.logic.m_Node,cloned_node2,cloned_node)
      
      util.RemoveNode(cloned_node)
      self.m_BoneBoardSegmentationNode = cloned_node2
      self.m_BoneBoardSegmentationNode.SetName("m_BoneBoardSegmentationNode")
      util.hidden(self.m_BoneBoardSegmentationNode,True)
      util.HideNode(self.m_SegmentationNode)
      self.goto_bone_step(2)
    if step == 2:
      
      util.send_event_str(util.ProgressValue,"60")
      cloned_node = util.clone(self.m_BoneBoardSegmentationNode)
      util.getModuleLogic('JSegmentEditorTool').margin_out(self.logic.m_Node,cloned_node)
      cloned_node.SetName("m_BoneMarginedNode")
      util.hidden(cloned_node,True)
      util.HideNode(self.m_BoneBoardSegmentationNode)
      self.m_BoneMarginedNode = cloned_node
      util.HideNode(self.m_BoneMarginedNode)
      self.goto_bone_step(3)
    if step == 3:
      
      util.send_event_str(util.ProgressValue,"70")
      out_node = util.AddNewNodeByClass(util.vtkMRMLScalarVolumeNode)
      out_node.SetName("stripeed_bone_basic")
      util.getModuleLogic('JSegmentEditorTool').mask_volume(self.logic.m_Node,self.m_BoneMarginedNode,self.logic.m_Node,out_node)
      self.m_OutNode = out_node
      self.goto_bone_step(4)
    if step == 4:
      
      util.send_event_str(util.ProgressValue,"80")
      util.RemoveNodeByName("颅骨")
      util.RemoveNodeByName("FullHeadSegmentationNode")
      self.m_SegmentationNode = util.CreateDefaultSegmentationNode("颅骨")
      full_head_segment = util.CreateDefaultSegmentationNode("FullHeadSegmentationNode")
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setSegmentationNode(self.m_SegmentationNode)
      segmentEditorWidget.setSourceVolumeNode(self.m_OutNode)
      segmentEditorWidget.setActiveEffectByName("Threshold")
      self.m_SegmentationNode.SetAttribute("master_node",self.m_OutNode.GetID())
      effect = segmentEditorWidget.activeEffect()
      m_ActiveEffect = effect
      lo, hi = util.GetScalarRange(self.m_OutNode)
      
      
      effect.setParameter("MinimumThreshold", self.min_skin)
      effect.setParameter("MaximumThreshold", self.max_skin)
      m_ActiveEffect.self().onApply()
      
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setSegmentationNode(full_head_segment)
      segmentEditorWidget.setSourceVolumeNode(self.m_OutNode)
      segmentEditorWidget.setActiveEffectByName("Threshold")
      full_head_segment.SetAttribute("master_node",self.m_OutNode.GetID())
      effect = segmentEditorWidget.activeEffect()
      m_ActiveEffect = effect
      lo, hi = util.GetScalarRange(self.m_OutNode)
      tmp = -400
      tmp = int(util.settingsValue("PDuruofei/le_bone_threshold",-400))
      
      
      effect.setParameter("MinimumThreshold", self.min_skin)
      effect.setParameter("MaximumThreshold", self.max_skin)
      m_ActiveEffect.self().onApply()

      util.getModuleLogic("JSegmentEditorTool").islands_max(self.logic.m_Node,self.m_SegmentationNode)
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setSegmentationNode(self.m_SegmentationNode)
      segmentEditorWidget.setSourceVolumeNode(self.logic.m_Node)
      segmentEditorWidget.setActiveEffectByName("Hollow")
      effect = segmentEditorWidget.activeEffect()
      effect.setParameter("ShellThicknessMm", self.thickness)
      effect.setParameter("ShellMode", 'INSIDE_SURFACE')
      effect.self().onApply()
      util.getModuleLogic('JSegmentEditorTool').islands_max(self.logic.m_Node,self.m_SegmentationNode)
      util.getModuleLogic("JSegmentEditorTool").margin_out(self.logic.m_Node,self.m_SegmentationNode,-2)
    
      model_node = util.convert_segment_to_model(self.m_SegmentationNode)
      model_node.SetName("骨骼模型")
      self.m_SegmentationNode.SetAttribute("alias_name","骨骼")
      model_node.SetAttribute("alias_name","骨骼模型")
      model_node.SetAttribute("bind_segment",self.m_SegmentationNode.GetID())
      model_node.SetAttribute("full_head_segment",full_head_segment.GetID())
      util.HideNode(self.m_SegmentationNode)
      util.HideNode(full_head_segment)
      self.m_ModelNode = model_node
      self.goto_bone_step(5)
    if step == 5:
      self.m_ModelNode.SetAttribute("jduruofei_name","骨骼模型")
      slicer.mrmlScene.InvokeEvent(util.JRemoveSkullBoardWidgetMaskResult,self.m_ModelNode)
      util.send_event_str(util.ProgressValue,"100")
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setActiveEffectByName("None")

  
  def goto_mask_step(self,step):
    print("goto_mask_step:",step)
    if step == 1:
      util.send_event_str(util.ProgressValue,"50")
      cloned_node = util.clone(self.m_SegmentationNode)
      cloned_node.SetName("skull_1")
      util.getModuleLogic('JSegmentEditorTool').islands_max(self.logic.m_Node,cloned_node)
      cloned_node2 = util.clone(self.m_SegmentationNode)
      util.getModuleLogic('JSegmentEditorTool').substract(self.logic.m_Node,cloned_node2,cloned_node)
      
      util.RemoveNode(cloned_node)
      self.m_MaskBoardSegmentationNode = cloned_node2
      self.m_MaskBoardSegmentationNode.SetName("m_MaskBoardSegmentationNode")
      util.hidden(self.m_MaskBoardSegmentationNode,True)
      util.HideNode(self.m_SegmentationNode)
      self.goto_mask_step(2)
    if step == 2:
      
      util.send_event_str(util.ProgressValue,"60")
      cloned_node = util.clone(self.m_MaskBoardSegmentationNode)
      util.getModuleLogic('JSegmentEditorTool').margin_out(self.logic.m_Node,cloned_node)
      cloned_node.SetName("m_MaskMarginedNode")
      util.hidden(cloned_node,True)
      util.HideNode(self.m_MaskBoardSegmentationNode)
      self.m_MaskMarginedNode = cloned_node
      util.HideNode(self.m_MaskMarginedNode)
      self.goto_mask_step(3)
    if step == 3:
      
      util.send_event_str(util.ProgressValue,"70")
      out_node = util.AddNewNodeByClass(util.vtkMRMLScalarVolumeNode)
      out_node.SetName("stripeed_mask_basic")
      util.getModuleLogic('JSegmentEditorTool').mask_volume(self.logic.m_Node,self.m_MaskMarginedNode,self.logic.m_Node,out_node)
      self.m_OutNode = out_node
      self.goto_mask_step(4)
    if step == 4:
      
      util.send_event_str(util.ProgressValue,"80")
      util.RemoveNodeByName("面具")
      util.RemoveNodeByName("FullHeadSegmentationNode")
      self.m_SegmentationNode = util.CreateDefaultSegmentationNode("面具")
      full_head_segment = util.CreateDefaultSegmentationNode("FullHeadSegmentationNode")
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setSegmentationNode(self.m_SegmentationNode)
      segmentEditorWidget.setSourceVolumeNode(self.m_OutNode)
      segmentEditorWidget.setActiveEffectByName("Threshold")
      self.m_SegmentationNode.SetAttribute("master_node",self.m_OutNode.GetID())
      effect = segmentEditorWidget.activeEffect()
      m_ActiveEffect = effect
      lo, hi = util.GetScalarRange(self.m_OutNode)
      tmp = -400
      tmp = int(util.settingsValue("PDuruofei/le_skin_threshold",-400))
      
      effect.setParameter("MinimumThreshold", tmp)
      effect.setParameter("MaximumThreshold", hi)
      m_ActiveEffect.self().onApply()
      
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setSegmentationNode(full_head_segment)
      segmentEditorWidget.setSourceVolumeNode(self.m_OutNode)
      segmentEditorWidget.setActiveEffectByName("Threshold")
      full_head_segment.SetAttribute("master_node",self.m_OutNode.GetID())
      effect = segmentEditorWidget.activeEffect()
      m_ActiveEffect = effect
      lo, hi = util.GetScalarRange(self.m_OutNode)
      tmp = -400
      tmp = int(util.settingsValue("PDuruofei/le_skin_threshold",-400))
      
      effect.setParameter("MinimumThreshold", tmp)
      effect.setParameter("MaximumThreshold", hi)
      m_ActiveEffect.self().onApply()

      util.getModuleLogic("JSegmentEditorTool").islands_max(self.logic.m_Node,self.m_SegmentationNode)
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setSegmentationNode(self.m_SegmentationNode)
      segmentEditorWidget.setSourceVolumeNode(self.logic.m_Node)
      segmentEditorWidget.setActiveEffectByName("Hollow")
      effect = segmentEditorWidget.activeEffect()
      effect.setParameter("ShellThicknessMm", self.thickness)
      effect.setParameter("ShellMode", 'INSIDE_SURFACE')
      effect.self().onApply()
      util.getModuleLogic('JSegmentEditorTool').islands_max(self.logic.m_Node,self.m_SegmentationNode)
      model_node = util.convert_segment_to_model(self.m_SegmentationNode)
      model_node.SetName("面具模型")
      model_node.SetAttribute("alias_name","面具模型")
      self.m_SegmentationNode.SetAttribute("alias_name","面具")

      model_node.SetAttribute("bind_segment",self.m_SegmentationNode.GetID())
      model_node.SetAttribute("full_head_segment",full_head_segment.GetID())
      util.HideNode(self.m_SegmentationNode)
      util.HideNode(full_head_segment)
      self.m_ModelNode = model_node
      self.goto_mask_step(5)
    if step == 5:
      self.m_ModelNode.SetAttribute("jduruofei_name","面具模型")
      slicer.mrmlScene.InvokeEvent(util.JRemoveSkullBoardWidgetMaskResult,self.m_ModelNode)
      util.send_event_str(util.ProgressValue,"100")
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setActiveEffectByName("None")


  
  

class JRemoveSkullBoardLogic(ScriptedLoadableModuleLogic):
  m_Node = None
  def __init__(self):
    """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
    ScriptedLoadableModuleLogic.__init__(self)
    slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeAddedEvent, self.onNodeAdded)
  

  def setWidget(self,widget):
    self.m_Widget = widget

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def onNodeAdded(self,caller, event, calldata):
    node = calldata
    #if isinstance(node, slicer.vtkMRMLMarkupsFiducialNode):
      #self.m_Widget.on_node_added(node)


 