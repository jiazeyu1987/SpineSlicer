import slicer,qt,vtk,ctk
import slicer.util as util
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from Base.JBaseExtension import JBaseExtensionWidget
import numpy as np
#
# UnitCTMask
#


class UnitCTMask(ScriptedLoadableModule):
  
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UnitCTMask"  # TODO: make this more human readable by adding spaces
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
# UnitCTMaskWidget
#

class UnitCTMaskWidget(JBaseExtensionWidget):
  button_map = {}
  def setup(self):
    super().setup()
    
    
  def init_ui(self):
    self.ui.tabWidget_6.tabBar().hide()
    self.ui.tabWidget_4.tabBar().hide()
    self.ui.tabWidget_5.tabBar().hide()
    self.ui.tabBone.tabBar().hide()
    
    self.ui.ctkRangeWidget.setRange(1, 100)
    self.ui.ctkRangeWidget.singleStep = 1
    self.ui.ctkRangeWidget.setMinimumValue(10)
    self.ui.ctkRangeWidget.setMaximumValue(50)
    self.ui.ctkRangeWidget.connect('valuesChanged(double,double)', self.onThresholdValuesChanged)
    
    self.ui.btnCut.connect('toggled(bool)',self.on_scissors)
    self.ui.btnSelectLand.connect('toggled(bool)',self.on_select_land)
    self.ui.btnMaxLand.connect('clicked()',self.on_islands)
    self.button_map['select_islands'] = self.ui.btnSelectLand
    self.button_map['scissors'] = self.ui.btnCut
    

    self.ui.pushButton_6.connect('clicked()',self.on_undo)
    self.ui.pushButton_7.connect('clicked()',self.on_redo)
    self.ui.pushButton_4.connect('clicked()',self.on_start_threshold)
    self.ui.pushButton_8.connect('clicked()',self.on_cancel)
    self.ui.pushButton_10.connect('clicked()',self.on_high_resolution_mask)
    self.ui.pushButton_11.connect('clicked()',self.on_high_resolution_skin)
    self.ui.pushButton.connect('clicked()',self.on_confirm_mask)
    util.registe_view_tool(self.ui.btnCut,"scissors")
    util.registe_view_tool(self.ui.btnSelectLand,"select_islands")
    self.ui.lineEdit.setValidator(qt.QDoubleValidator(self.ui.lineEdit))
    
    self.ui.ctkSliderWidget.singleStep = 0.1
    self.ui.ctkSliderWidget.minimum = 0.1
    self.ui.ctkSliderWidget.maximum = 25
    self.ui.ctkSliderWidget.value = 5
    self.ui.ctkSliderWidget.connect("valueChanged(double)", self.on_erase)
    
    self.ui.btnHollow.connect('toggled(bool)',self.on_hollow)
    util.registe_view_tool(self.ui.btnHollow,"Erase")
    
    self.ui.pushButton_5.connect('clicked()',self.on_start_skin)
    self.ui.pushButton_2.connect('clicked()',self.on_confirm_skin)
    self.ui.pushButton_9.connect('clicked()',self.on_cancel_skin)
    
    self.ui.pushButton_16.connect('clicked()',self.on_start_bone)
    self.ui.pushButton_3.connect('clicked()',self.on_confirm_bone)
    self.ui.pushButton_15.connect('clicked()',self.on_cancel_bone)
    
    self.ui.pushButton_12.connect('clicked()',self.on_reverse)
    
    self.ui.ctkRangeWidget_2.setRange(-1000, 2100)
    self.ui.ctkRangeWidget_2.singleStep = 1
    self.ui.ctkRangeWidget_2.setMinimumValue(-1000)
    self.ui.ctkRangeWidget_2.setMaximumValue(2100)
    self.ui.ctkRangeWidget_2.connect('valuesChanged(double,double)', self.onThresholdValuesChanged2)

    self.ui.ctkRangeWidget_3.setRange(-1000, 2100)
    self.ui.ctkRangeWidget_3.singleStep = 1
    self.ui.ctkRangeWidget_3.setMinimumValue(-1000)
    self.ui.ctkRangeWidget_3.setMaximumValue(2100)
    self.ui.ctkRangeWidget_3.connect('valuesChanged(double,double)', self.onThresholdValuesChanged3)
    self.ui.ctkRangeWidget.setDecimals(1)
    self.ui.ctkRangeWidget_2.setDecimals(1)
    self.ui.ctkRangeWidget_3.setDecimals(1)
    self.ui.tabWidget_5.setCurrentIndex(1)
    
    slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeAddedEvent, self.onNodeAdded)
    slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeRemovedEvent, self.onNodeRemoved)
    self.TagMaps[util.ResetVersion] = slicer.mrmlScene.AddObserver(util.ResetVersion, self.OnResetVersion)
  
  def exit(self):
    util.trigger_view_tool("")

  def on_cancel(self):
    util.trigger_view_tool("")
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setActiveEffectByName("None")
    self.ui.tabWidget_5.setCurrentIndex(1)
  
  def on_cancel_skin(self):
    util.trigger_view_tool("")
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setActiveEffectByName("None")
    self.ui.tabWidget_6.setCurrentIndex(1)
  
  def reset_skin_state(self):
    current_index = self.ui.tabWidget_6.currentIndex
    if current_index == 2:
      return
    self.ui.tabWidget_6.setCurrentIndex(1)

  def reset_bone_state(self):
    current_index = self.ui.tabBone.currentIndex
    if current_index == 2:
      return
    self.ui.tabBone.setCurrentIndex(1)

  def on_redo(self):
      util.trigger_view_tool("")
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.redo()
  
  def on_undo(self):
      util.trigger_view_tool("")
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.undo()    
  
  def get_sub_solution_hard(self):
    sub_solution_hard = util.get_cache_from_PAAA("sub_solution_hard",1)
    return int(sub_solution_hard)
  
  def OnResetVersion(self,_a,_b):
    sub_solution_hard = self.get_sub_solution_hard()
    self.ui.pushButton_10.setText("高精度创建")
    self.ui.pushButton_10.setEnabled(True)
    self.ui.pushButton_11.setText("高精度创建")
    self.ui.pushButton_11.setEnabled(True)
      
    state = True
    if sub_solution_hard == 4:
      state = False
    self.hide_all_but_mask(state)

  def on_confirm_skin(self):
    util.send_event_str(util.ProgressStart,"正在创建皮肤")
    volume_node = self.get_volume()
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    effect = segmentEditorWidget.activeEffect()
    m_ActiveEffect = effect
    lo, hi = util.GetScalarRange(volume_node)
    tmp = float(self.ui.ctkRangeWidget_2.minimumValue)
    effect.setParameter("MinimumThreshold", tmp)
    effect.setParameter("MaximumThreshold", hi)
    m_ActiveEffect.self().onApply()
    util.send_event_str(util.ProgressValue,30)
    segmentEditorWidget.setActiveEffectByName("Hollow")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("ShellThicknessMm", float(self.ui.lineEdit_2.text))
    effect.setParameter("ShellMode", 'OUTSIDE_SURFACE')
    effect.self().onApply()
    util.send_event_str(util.ProgressValue,60)  
      
    node = util.getFirstNodeByName("皮肤")
    util.getModuleLogic("JSegmentEditorTool").islands_max(volume_node,node) 
    util.send_event_str(util.ProgressValue,90)  
   
    self.ui.tabWidget_5.setCurrentIndex(1)
    self.ui.tabWidget_6.setCurrentIndex(1)
    self.reset_bone_state()
    util.reinit3D()
    util.GetNthSegment(node,0).SetColor([177/255.0,122/255.0,101/255.0])
    node.SetAttribute("alias_name","皮肤")
    
    util.color_unit_list.add_item(node, 2)
    util.tips_unit_list.add_item(node, 2)
    util.send_event_str(util.ProgressValue,100)
    segmentEditorWidget.setActiveEffectByName("None")
  
  
  
  def onThresholdValuesChanged(self,v1,v2):
    self.thresholdValuesChanged(self.ui.ctkRangeWidget)

  def onThresholdValuesChanged2(self,v1,v2):
    self.thresholdValuesChanged(self.ui.ctkRangeWidget_2)
  
  def onThresholdValuesChanged3(self,v1,v2):
    self.thresholdValuesChanged(self.ui.ctkRangeWidget_3)
  
  
  def thresholdValuesChanged(self, ctkRangeWidgetUI):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    effect = segmentEditorWidget.activeEffect()
    if not effect:
      return
    effect.setParameter("MinimumThreshold", ctkRangeWidgetUI.minimumValue)
    effect.setParameter("MaximumThreshold", ctkRangeWidgetUI.maximumValue)
  
  
  def on_start_skin(self):
    if self.get_volume() is None:
      util.showWarningText("请先加载DICOM数据")
      return
    
    
    self.ui.tabWidget_6.setCurrentIndex(0)
    self.ui.tabWidget_5.setCurrentIndex(1)
    self.reset_bone_state()
    
    volume_node = self.get_volume()
    seg_name = "皮肤"
    if util.getFirstNodeByName(seg_name) is None:
      util.CreateDefaultSegmentationNode(seg_name)
    segment_node = util.getFirstNodeByName(seg_name)  
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(volume_node)
    segmentEditorWidget.setActiveEffectByName("Threshold")
    lo, hi = util.GetScalarRange(volume_node)
    self.ui.ctkRangeWidget_2.setRange(lo, hi)
    self.ui.ctkRangeWidget_2.singleStep = 1
    self.ui.ctkRangeWidget_2.setMinimumValue(-400)
    self.ui.ctkRangeWidget_2.setMaximumValue(hi)
  
  def on_erase(self,value):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setActiveEffectByName("Erase")
    effect = segmentEditorWidget.activeEffect()
    volume_node = self.get_volume()
    segment_node = util.getFirstNodeByName("面具")
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(volume_node)
    effect.setCommonParameter("BrushRelativeDiameter", value)
    effect.setCommonParameter("EditIn3DViews", 1)
  
  def on_hollow(self,boolval):
    if boolval:
      self.ui.lblCover.hide()
      util.trigger_view_tool("Erase")
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      volume_node = self.get_volume()
      segment_node = util.getFirstNodeByName("面具")
      segmentEditorWidget.setSegmentationNode(segment_node)
      segmentEditorWidget.setSourceVolumeNode(volume_node)
      segmentEditorWidget.setActiveEffectByName("Erase")
      effect = segmentEditorWidget.activeEffect()
      if effect:
        effect.setCommonParameter("EditIn3DViews", 1)
        effect.setCommonParameter("BrushRelativeDiameter", self.ui.ctkSliderWidget.value)
    else:
      self.ui.lblCover.show()
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setActiveEffectByName("None")
  
  def on_scissors(self,boolval):
    if boolval:
      util.trigger_view_tool("scissors")
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      volume_node = self.get_volume()
      segment_node = util.getFirstNodeByName("面具")
      segmentEditorWidget.setSegmentationNode(segment_node)
      segmentEditorWidget.setSourceVolumeNode(volume_node)
      segmentEditorWidget.setActiveEffectByName("Scissors")
    else:
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setActiveEffectByName("None")
  
  def on_select_land(self, boolval):
    if boolval:
      util.trigger_view_tool("select_islands")
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      volume_node = self.get_volume()
      segment_node = util.getFirstNodeByName("面具")
      segmentEditorWidget.setSegmentationNode(segment_node)
      segmentEditorWidget.setSourceVolumeNode(volume_node)
      segmentEditorWidget.setActiveEffectByName("Islands")
      effect = segmentEditorWidget.activeEffect()
      effect.setParameter("Operation", "KEEP_SELECTED_ISLAND")
      pass
    else:
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setActiveEffectByName("None")
      pass

  def on_islands(self):
    util.trigger_view_tool("")
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    volume_node = self.get_volume()
    segment_node = util.getFirstNodeByName("面具")
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(volume_node)
    segmentEditorWidget.setActiveEffectByName("Islands")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("Operation", "KEEP_LARGEST_ISLAND")
    operationName = effect.parameter("Operation")
    print("whm test ", operationName)
    effect.self().onApply()
    segmentEditorWidget.setActiveEffectByName("None")  
  

  
  def on_confirm_mask(self):
    segment_node = util.getFirstNodeByName("FullHeadSegmentationNode")
    util.send_event_str(util.ProgressStart,"正在创建面具")
    volume_node = self.get_volume()
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    effect = segmentEditorWidget.activeEffect()
    m_ActiveEffect = effect
    lo, hi = util.GetScalarRange(volume_node)
    tmp = float(self.ui.ctkRangeWidget.minimumValue)
    effect.setParameter("MinimumThreshold", tmp)
    effect.setParameter("MaximumThreshold", hi)
    m_ActiveEffect.self().onApply()
    util.send_event_str(util.ProgressValue,30)
    segmentEditorWidget.setActiveEffectByName("Hollow")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("ShellThicknessMm", float(self.ui.lineEdit.text))
    effect.setParameter("ShellMode", 'INSIDE_SURFACE')
    effect.self().onApply()
    util.send_event_str(util.ProgressValue,60)  
      
    segment_node = util.getFirstNodeByName("面具")
    util.getModuleLogic("JSegmentEditorTool").islands_max(volume_node,segment_node) 
    util.send_event_str(util.ProgressValue,80)  
   
    full_head_segment = util.CreateDefaultSegmentationNode("FullHeadSegmentationNode")
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(full_head_segment)
    segmentEditorWidget.setSourceVolumeNode(volume_node)
    segmentEditorWidget.setActiveEffectByName("Threshold")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("MinimumThreshold", -400)
    effect.setParameter("MaximumThreshold", 100000)
    effect.self().onApply()
    util.HideNodeByName("FullHeadSegmentationNode")
    util.send_event_str(util.ProgressValue,90)  
      
    self.ui.tabWidget_5.setCurrentIndex(1)
    util.GetNthSegment(segment_node,0).SetColor([152/255.0,189/255.0,207/255.0])
    
    segment_node.SetAttribute("alias_name","面具")
    util.color_unit_list.add_item(segment_node, 2)
    util.tips_unit_list.add_item(segment_node, 2)
    util.send_event_str(util.close_volume_rendering)
    util.singleShot(0,self.re3d)
    util.send_event_str(util.ProgressValue,100)
    
    self.ui.pushButton_12.setVisible(False)
    #util.singleShot(1000,self.copy_mask)
    
  def copy_mask(self):
    clonded_segment = util.clone(util.getFirstNodeByClassByName(util.vtkMRMLSegmentationNode,"面具"))
    clonded_segment.SetAttribute("cloned_mask","1")
    clonded_segment.SetName("面备份具")
    util.RemoveNode(clonded_segment)
    util.AddNode(clonded_segment)
    util.HideNode(clonded_segment)
  
  @vtk.calldata_type(vtk.VTK_OBJECT)
  def onNodeAdded(self, node, event, calldata):
      node = calldata
      if node.GetAttribute("cloned_mask") == "1":
        self.ui.pushButton_12.setEnabled(True)
  
  @vtk.calldata_type(vtk.VTK_OBJECT)
  def onNodeRemoved(self, node, event, calldata):
      node = calldata
      if node.GetAttribute("cloned_mask") == "1":
        self.ui.pushButton_12.setEnabled(False)
      
      
      
  def re3d(self):
    controller = slicer.app.layoutManager().threeDWidget(0).threeDController()
    AxesWidget = util.findChild(controller,"AxesWidget")
    AxesWidget.setCurrentAxis(5)
  
  def on_high_resolution_skin(self):
    segment_node = util.getFirstNodeByName("FullHeadSegmentationNode")
    if segment_node:
      if segment_node.GetAttribute("high_resolution") == None:
        util.RemoveNode(segment_node)
    util.RemoveNodeByName("皮肤")
    
    volume_node = self.get_volume()
    segment_node = util.getFirstNodeByNameByAttribute("FullHeadSegmentationNode","high_resolution","1")
    seg_name = "FullHeadSegmentationNode"
    if  segment_node is None:
      util.CreateDefaultSegmentationNode(seg_name)
      segment_node = util.getFirstNodeByName(seg_name) 
      segment_node.SetAttribute("high_resolution","1") 
      segment = util.GetNthSegment(segment_node,0)
      segment.SetColor([255/255.0,255/255.0,0/255.0])
      util.getModuleLogic("SkinExtractor").process(volume_node,segment_node)
      util.RemoveNthSegmentID(segment_node,0)
    
    util.RemoveNodeByName("皮肤")
    SkinSegmentation = util.clone(segment_node)
    SkinSegmentation.SetName("皮肤")
    util.send_event_str(util.ProgressStart,"正在分割皮肤")
    util.send_event_str(util.ProgressValue,30)
    
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(SkinSegmentation)
    segmentEditorWidget.setSourceVolumeNode(volume_node)
    segmentEditorWidget.setActiveEffectByName("Hollow")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("ShellThicknessMm", self.ui.lineEdit_2.text)
    effect.setParameter("ShellMode", 'OUTSIDE_SURFACE')
    effect.self().onApply()
    
    util.GetNthSegment(SkinSegmentation,0).SetColor([177/255.0,122/255.0,101/255.0])
    SkinSegmentation.SetAttribute("alias_name","皮肤")
    util.color_unit_list.add_item(SkinSegmentation, 2)
    util.tips_unit_list.add_item(SkinSegmentation, 2)
    util.HideNode(segment_node)
    util.ShowNode(SkinSegmentation)
    util.send_event_str(util.ProgressValue,100)
  
  def on_high_resolution_mask(self):
    segment_node = util.getFirstNodeByName("FullHeadSegmentationNode")
    if segment_node:
      if segment_node.GetAttribute("high_resolution") == None:
        util.RemoveNode(segment_node)
    util.RemoveNodeByName("面具")
    volume_node = self.get_volume()
    segment_node = util.getFirstNodeByNameByAttribute("FullHeadSegmentationNode","high_resolution","1")
    if not segment_node:
      seg_name = "FullHeadSegmentationNode"
      if util.getFirstNodeByName(seg_name) is None:
        util.CreateDefaultSegmentationNode(seg_name)
      segment_node = util.getFirstNodeByName(seg_name) 
      segment_node.SetAttribute("high_resolution","1") 
      util.getModuleLogic("SkinExtractor").process(volume_node,segment_node)
      util.RemoveNthSegmentID(segment_node,0)
    
    util.RemoveNodeByName("面具")
    MaskSegmentation = util.clone(segment_node)
    MaskSegmentation.SetName("面具")
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(MaskSegmentation)
    segmentEditorWidget.setSourceVolumeNode(volume_node)
    segmentEditorWidget.setActiveEffectByName("Hollow")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("ShellThicknessMm", self.ui.lineEdit.text)
    effect.setParameter("ShellMode", 'INSIDE_SURFACE')
    effect.self().onApply()
    
    util.GetNthSegment(MaskSegmentation,0).SetColor([152/255.0,189/255.0,207/255.0])
    util.HideNode(segment_node)
    MaskSegmentation.SetAttribute("alias_name","面具")
    util.color_unit_list.add_item(MaskSegmentation, 2)
    util.tips_unit_list.add_item(MaskSegmentation, 2)

    util.ShowNode(MaskSegmentation)
    util.send_event_str(util.close_volume_rendering)
    util.singleShot(0,self.re3d)
  
  def on_start_threshold(self):
    if self.get_volume() is None:
      util.showWarningText("请先加载DICOM数据")
      return
    self.ui.tabWidget_5.setCurrentIndex(0)
    self.reset_bone_state()
    self.reset_skin_state()
    volume_node = self.get_volume()
    seg_name = "面具"
    if util.getFirstNodeByName(seg_name) is None:
      util.CreateDefaultSegmentationNode(seg_name)
    segment_node = util.getFirstNodeByName(seg_name)  
    segment = util.GetNthSegment(segment_node,0)
    segment.SetColor([255/255.0,255/255.0,0/255.0])
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(volume_node)
    segmentEditorWidget.setActiveEffectByName("Threshold")
    lo, hi = util.GetScalarRange(volume_node)
    self.ui.ctkRangeWidget.setRange(lo, hi)
    self.ui.ctkRangeWidget.singleStep = 1
    self.ui.ctkRangeWidget.setMinimumValue(-400)
    self.ui.ctkRangeWidget.setMaximumValue(hi)
    
  
  def get_volume(self):
    volume = util.getFirstNodeByClassByAttribute(util.vtkMRMLScalarVolumeNode,"main_node","1")
    return volume
    
  def on_step1(self):
    print("on_step1")
    
  def on_step2(self):
    print("on_step2")

  def on_start_bone(self):
    if self.get_volume() is None:
      util.showWarningText("请先加载DICOM数据")
      return
    
    
    self.reset_skin_state()
    self.ui.tabWidget_5.setCurrentIndex(1)
    self.ui.tabBone.setCurrentIndex(0)
    
    volume_node = self.get_volume()
    seg_name = "颅骨"
    if util.getFirstNodeByName(seg_name) is None:
      util.CreateDefaultSegmentationNode(seg_name)
    segment_node = util.getFirstNodeByName(seg_name)  
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(volume_node)
    segmentEditorWidget.setActiveEffectByName("Threshold")
    lo, hi = util.GetScalarRange(volume_node)
    default_low_value = 180
    self.ui.ctkRangeWidget_3.setRange(lo, hi)
    self.ui.ctkRangeWidget_3.singleStep = 1
    self.ui.ctkRangeWidget_3.setMaximumValue(hi)
    self.ui.ctkRangeWidget_3.setMinimumValue(default_low_value)
      
  def on_confirm_bone(self):
    util.send_event_str(util.ProgressStart,"正在创建颅骨...")
    volume_node = self.get_volume()
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    effect = segmentEditorWidget.activeEffect()
    m_ActiveEffect = effect
    lo, hi = util.GetScalarRange(volume_node)
    tmp = float(self.ui.ctkRangeWidget_3.minimumValue)
    effect.setParameter("MinimumThreshold", tmp)
    effect.setParameter("MaximumThreshold", hi)
    m_ActiveEffect.self().onApply()
    util.send_event_str(util.ProgressValue,50)
      
    node = util.getFirstNodeByName("颅骨")
    #util.getModuleLogic("JSegmentEditorTool").islands_max(volume_node,node) 
    #util.send_event_str(util.ProgressValue,90)  
   
    self.ui.tabWidget_5.setCurrentIndex(1)
    self.reset_skin_state()
    self.ui.tabBone.setCurrentIndex(1)
    util.reinit3D()
    util.getModuleLogic("JSegmentEditorTool").islands_max(volume_node,node) 
    node.SetAttribute("alias_name","颅骨")
    util.GetNthSegment(node,0).SetColor([1,1,1])
    
    util.color_unit_list.add_item(node, 2)
    util.tips_unit_list.add_item(node, 2)
    util.send_event_str(util.ProgressValue,100)
    segmentEditorWidget.setActiveEffectByName("None")
    
  def on_split_point(self,val):
    if val:
      segment_node = util.getFirstNodeByName("面具")
      if not segment_node:
        util.showWarningText("请先创建一个面具")
        self.ui.pushButton_12.setChecked(False)
        return
      
      volume_node = self.get_volume()
      if not volume_node:
        util.showWarningText("请先加载一个节点")
        self.ui.pushButton_12.setChecked(False)
        return
        
      util.getModuleWidget("UnitAutoHollow").init(volume_node,segment_node,"",self.ui.pushButton_12)
      util.layout_panel("middle_right").setMaximumWidth(210)
      util.layout_panel("middle_right").setMinimumWidth(210)
      util.layout_panel("middle_right").setModule("UnitAutoHollow")
      util.layout_panel("middle_right").show()
    else:
      if util.layout_panel("middle_right").currentModuleName()=="UnitAutoHollow":
        util.layout_panel("middle_right").hide()
        util.layout_panel("middle_right").setModule("")
    return
    
  
  
  def on_reverse(self):
    cloned_segment = util.getFirstNodeByClassByAttribute(util.vtkMRMLSegmentationNode,"cloned_mask","1")
    if cloned_segment:
      segment_node = util.clone(cloned_segment)
      segment_node.SetName("面具")
      segment_node.SetAttribute("alias_name","面具")
      util.color_unit_list.add_item(segment_node, 2)
      util.tips_unit_list.add_item(segment_node, 2)
      util.ShowNode(segment_node)

  def on_cancel_bone(self):
    util.trigger_view_tool("")
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setActiveEffectByName("None")
    self.ui.tabBone.setCurrentIndex(1)

  def on_high_resolution_bone(self):
    segment_node = util.getFirstNodeByName("FullHeadSegmentationNode")
    if segment_node:
      if segment_node.GetAttribute("high_resolution") == None:
        util.RemoveNode(segment_node)
    util.RemoveNodeByName("颅骨")
    
    volume_node = self.get_volume()
    segment_node = util.getFirstNodeByNameByAttribute("FullHeadSegmentationNode","high_resolution","1")
    seg_name = "FullHeadSegmentationNode"
    if  segment_node is None:
      util.CreateDefaultSegmentationNode(seg_name)
      segment_node = util.getFirstNodeByName(seg_name) 
      segment_node.SetAttribute("high_resolution","1") 
      segment = util.GetNthSegment(segment_node,0)
      segment.SetColor([255/255.0,255/255.0,0/255.0])
      util.getModuleLogic("SkinExtractor").process(volume_node,segment_node)
      util.RemoveNthSegmentID(segment_node,0)
    
    util.RemoveNodeByName("颅骨")
    BoneSegmentation = util.clone(segment_node)
    BoneSegmentation.SetName("颅骨")
    util.send_event_str(util.ProgressStart,"正在分割骨骼")
    util.send_event_str(util.ProgressValue,30)
    
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(BoneSegmentation)
    segmentEditorWidget.setSourceVolumeNode(volume_node)
    segmentEditorWidget.setActiveEffectByName("Hollow")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("ShellThicknessMm", self.ui.lineEdit_2.text)
    effect.setParameter("ShellMode", 'OUTSIDE_SURFACE')
    effect.self().onApply()
    
    util.GetNthSegment(BoneSegmentation,0).SetColor([177/255.0,122/255.0,101/255.0])
    BoneSegmentation.SetAttribute("alias_name","颅骨")
    util.color_unit_list.add_item(BoneSegmentation, 2)
    util.tips_unit_list.add_item(BoneSegmentation, 2)
    util.HideNode(segment_node)
    util.ShowNode(BoneSegmentation)
    util.send_event_str(util.ProgressValue,100)

    

  def hide_all_but_mask(self, state):
    self.ui.tabBone.setVisible(state)
    self.ui.tabWidget_6.setVisible(state)
    pass