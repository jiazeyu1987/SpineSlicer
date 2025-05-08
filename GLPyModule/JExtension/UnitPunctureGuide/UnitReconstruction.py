import slicer,qt,vtk,ctk,os
import slicer.util as util
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from Base.JBaseExtension import JBaseExtensionWidget
import numpy as np
import UnitPunctureGuideStyle as style
#
# UnitReconstruction
#


class UnitReconstruction(ScriptedLoadableModule):
  
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UnitReconstruction"  # TODO: make this more human readable by adding spaces
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
# UnitReconstructionWidget
#

class UnitReconstructionWidget(JBaseExtensionWidget):
  button_map = {}
  def setup(self):
    super().setup()
    
    
  def init_ui(self):
    self.ui.tabSkin.tabBar().hide()
    self.ui.tabBone.tabBar().hide()
    
    self.ui.pushButton_11.connect('clicked()',self.on_high_resolution_skin)
    self.ui.lineEdit_2.setValidator(qt.QDoubleValidator(self.ui.lineEdit_2))
    self.ui.lineEdit_3.setValidator(qt.QDoubleValidator(self.ui.lineEdit_3))
    
    self.ui.pushButton_5.connect('clicked()',self.on_start_skin)
    self.ui.pushButton_2.connect('clicked()',self.on_confirm_skin)
    self.ui.pushButton_9.connect('clicked()',self.on_cancel_skin)
    
    self.ui.pushButton_16.connect('clicked()',self.on_start_bone)
    self.ui.pushButton_3.connect('clicked()',self.on_confirm_bone)
    self.ui.pushButton_15.connect('clicked()',self.on_cancel_bone)

    self.ui.btn_quick_skin.connect('clicked()', self.on_quick_skin)
    self.ui.btn_quick_bone.connect('clicked()', self.on_quick_bone)
    
    self.ui.btnTurmo.connect('toggled(bool)', self.on_turmo_click)
    self.ui.btnVentricle.connect('toggled(bool)', self.on_ventricle_click)
    self.ui.btnBrain.connect('toggled(bool)', self.on_brain_click)
    self.ui.btnVentricle.hide()
    self.ui.btnBrain.hide()
    self.ui.label_3.hide()
    self.ui.label_8.hide()
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
    self.ui.ctkRangeWidget_2.setDecimals(1)
    self.ui.ctkRangeWidget_3.setDecimals(1)
    
    self.TagMaps[util.ResetVersion] = slicer.mrmlScene.AddObserver(util.ResetVersion, self.OnResetVersion)
    module_path = os.path.dirname(util.modulePath('UnitReconstruction'))
    style.set_reconstruction_style(module_path, self.ui)
  def exit(self):
    util.trigger_view_tool("")
    self.ui.btnTurmo.setChecked(False)
    self.ui.btnVentricle.setChecked(False)

  
  
  def on_turmo_click(self,val):
    if val:
      nod1 = util.getFirstNodeByName("血肿")
      if nod1:
        util.RemoveNode(nod1)
      util.trigger_view_tool("")
      self.ui.btnVentricle.setChecked(False)
      self.ui.btnBrain.setChecked(False)
      util.layout_panel("middle_right").setMaximumWidth(200)
      util.layout_panel("middle_right").setMinimumWidth(200)
      util.layout_panel("middle_right").setModule("UnitCTTumor")
      util.getModuleWidget("UnitCTTumor").set_use_type(0)
      util.layout_panel("middle_right").show()
    else:
      util.layout_panel("middle_right").setModule("")
      util.layout_panel("middle_right").hide()
      util.getModuleWidget("UnitCTTumor").reset_state()
    pass

  def on_ventricle_click(self, val):
    if val:
      util.trigger_view_tool("")
      self.ui.btnTurmo.setChecked(False)
      self.ui.btnBrain.setChecked(False)
      util.layout_panel("middle_right").setMaximumWidth(200)
      util.layout_panel("middle_right").setMinimumWidth(200)
      util.layout_panel("middle_right").setModule("UnitCTTumor")
      util.getModuleWidget("UnitCTTumor").set_use_type(1)
      util.layout_panel("middle_right").show()
    else:
      util.layout_panel("middle_right").setModule("")
      util.layout_panel("middle_right").hide()
      util.getModuleWidget("UnitCTTumor").reset_state()
    pass
  
  
  def on_quick_bone(self):
    self.on_start_bone()
    self.on_confirm_bone()
    pass

  
  def on_quick_skin(self):
    self.on_start_skin()
    self.on_confirm_skin()
    pass

  def on_brain_click(self, val):
    if val:
      volume_node = self.get_t1volume()
      if not volume_node:
        util.showWarningText("目前只支持T1数据(不支持T1增强,MRA数据)\n请先加载一个T1数据并设置为主节点，或者将T1数据配准到CT上")
        #self.ui.btn_split_mri.setChecked(False)
        return
      self.ui.btnVentricle.setChecked(False)
      self.ui.btnTurmo.setChecked(False)
        
      util.getModuleWidget("SegmentTemplateBrainArea").init(volume_node,self.ui.btnBrain)
      util.layout_panel("middle_right").setMaximumWidth(215)
      util.layout_panel("middle_right").setMinimumWidth(215)
      util.layout_panel("middle_right").setModule("SegmentTemplateBrainArea")
      util.layout_panel("middle_right").show()
    else:
      util.layout_panel("middle_right").setModule("")
      util.layout_panel("middle_right").hide()
      util.getModuleWidget("UnitCTTumor").reset_state()

  def on_cancel(self):
    util.trigger_view_tool("")
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setActiveEffectByName("None")
  
  def on_cancel_skin(self):
    util.trigger_view_tool("")
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setActiveEffectByName("None")
    self.ui.tabSkin.setCurrentIndex(1)
  
  def reset_skin_state(self):
    current_index = self.ui.tabSkin.currentIndex
    if current_index == 2:
      return
    self.ui.tabSkin.setCurrentIndex(1)

  def reset_bone_state(self):
    current_index = self.ui.tabBone.currentIndex
    if current_index == 2:
      return
    self.ui.tabBone.setCurrentIndex(1)
  
  def OnResetVersion(self,_a,_b):
    pass
      
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
   
    self.ui.tabSkin.setCurrentIndex(1)
    self.reset_bone_state()
    util.reinit3D()
    util.GetNthSegment(node,0).SetColor([177/255.0,122/255.0,101/255.0])
    node.SetAttribute("alias_name","皮肤")
    
    util.color_unit_list.add_item(node, 2)
    util.tips_unit_list.add_item(node, 2)
    node.CreateClosedSurfaceRepresentation()
    node.GetClosedSurfaceInternalRepresentation("皮肤")
    util.send_event_str(util.ProgressValue,100)
    segmentEditorWidget.setActiveEffectByName("None")
    
    util.color_unit_list.zero_opacity_by_type(slicer.vtkMRMLScalarVolumeNode)
  
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
    
    
    self.ui.tabSkin.setCurrentIndex(0)
    self.reset_bone_state()
    self.ui.btnTurmo.setChecked(False)
    
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
  
  def get_t1volume(self):
    volumes = util.getNodesByClass(util.vtkMRMLScalarVolumeNode)
    main_volume = util.getFirstNodeByClassByAttribute(util.vtkMRMLScalarVolumeNode,"main_node","1")
    if util.is_mrinode(main_volume):
      return main_volume
    for volume in volumes:
      if util.is_mrinode(volume) and (volume.GetAttribute("registed_info") == "fixed_node" or volume.GetAttribute("registed_info") == "moved_node"):
        return volume
    return None
    
  def get_volume(self):
    volume = util.getFirstNodeByClassByAttribute(util.vtkMRMLScalarVolumeNode,"main_node","1")
    return volume

  def on_start_bone(self):
    if self.get_volume() is None:
      util.showWarningText("请先加载DICOM数据")
      return
    
    self.ui.btnTurmo.setChecked(False)
    
    self.reset_skin_state()
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
    util.color_unit_list.zero_opacity_by_type(slicer.vtkMRMLScalarVolumeNode)

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
    