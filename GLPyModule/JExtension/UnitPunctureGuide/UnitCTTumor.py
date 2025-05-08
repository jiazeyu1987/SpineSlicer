import slicer,qt,vtk,ctk,os,json
import slicer.util as util
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from Base.JBaseExtension import JBaseExtensionWidget
import UnitPunctureGuideLib.G_UnitPunctureGuide as G
#
# UnitCTTumor
#



class UnitCTTumor(ScriptedLoadableModule):
  mask_segment_id = ""
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UnitCTTumor"  # TODO: make this more human readable by adding spaces
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
# UnitCTTumorWidget
#

class UnitCTTumorWidget(JBaseExtensionWidget):
  index = 0
  templateList = {}
  templateListMRI = {}
  #0:血肿； 1:脑室
  use_type = 0
  def setup(self):
    super().setup()
    self.ui.tabWidget_6.tabBar().hide()
    self.ui.tabWidget_5.tabBar().hide()
    self.ui.tabWidget_4.tabBar().hide()
    self.ui.tabWidget_7.tabBar().hide()
    self.ui.tabWidget_2.tabBar().hide()
    self.ui.pushButton_2.hide()
    self.ui.pushButton_9.hide()
    
    self.ui.tabWidget.tabBar().hide()
    self.ui.btnSaveMaxLand.setVisible(False)
    self.ui.label_18.setVisible(False)
    self.ui.btnMaxLand.setVisible(False)
    self.ui.label_7.setVisible(False)
    #self.ui.cbox_mask.setVisible(False)
  
  def set_use_type(self, use_type):
    title = "创建血肿"
    if use_type == 1:
      title = "创建脑室"
    self.use_type = use_type
    self.ui.lbl_title.setText(title)

  def find_chinese_name(self,english_name):
    for i in range(len(self.english_v)):
      if self.english_v[i] == english_name:
        if self.chinese_v[i] not in self.chinese_json:
          print(self.chinese_v[i])
        return self.chinese_v[i]
      
      
  def init_ui(self):
    
      
    self.ui.pushButton_7.connect('clicked()',self.on_redo)
    self.ui.pushButton_8.connect('clicked()',self.on_undo)
    self.ui.checkBox_2.connect('toggled(bool)',self.on_choose_all)
    
    util.paras["血肿"] = 1
    util.paras["脑室"] = 0

    
    util.registe_view_tool(self.ui.btnLeveltracing,"Level tracing")    
    self.ui.btnLeveltracing.connect('toggled(bool)',self.on_leveltracing)
    util.registe_view_tool(self.ui.btnDraw,"Draw")    
    self.ui.btnCut.connect('toggled(bool)',self.on_scissors)
    util.registe_view_tool(self.ui.btnCut,"scissors")    
    self.ui.btnDraw.connect('toggled(bool)',self.on_draw)
    self.ui.btnPaint.connect('toggled(bool)',self.on_start_paint)
    util.registe_view_tool(self.ui.btnPaint,"Paint")

    self.ui.btnMaxLand.connect('toggled(bool)',self.on_island)    
    util.registe_view_tool(self.ui.btnMaxLand,"islands")
    self.ui.btnSaveMaxLand.connect('toggled(bool)',self.on_save_island)   
    util.registe_view_tool(self.ui.btnSaveMaxLand,"islands_keep") 
    self.ui.btnFill.connect('clicked()',self.on_fill)    
    self.ui.pushButton_6.connect('clicked()',self.on_threshold_start)
    #self.ui.cbox_mask.connect('toggled(bool)',self.on_mask_state_change)   
    
    self.ui.ctkRangeWidget.setRange(1, 100)
    self.ui.ctkRangeWidget.singleStep = 1
    self.ui.ctkRangeWidget.setMinimumValue(10)
    self.ui.ctkRangeWidget.setMaximumValue(50)
    self.ui.ctkRangeWidget.connect('valuesChanged(double,double)', self.onThresholdValuesChanged2)
    
    self.ui.ctkRangeWidget.setDecimals(1)
    self.ui.ctkSliderWidget.singleStep = 0.1
    self.ui.ctkSliderWidget.minimum = 0.1
    self.ui.ctkSliderWidget.maximum = 25
    self.ui.ctkSliderWidget.value = 1
    self.ui.ctkSliderWidget.connect("valueChanged(double)", self.on_paint)
    
    self.ui.ctkSliderWidget2.singleStep = 0.1
    self.ui.ctkSliderWidget2.minimum = 0.1
    self.ui.ctkSliderWidget2.maximum = 10
    self.ui.ctkSliderWidget2.value = 1
    self.ui.ctkSliderWidget2.connect("valueChanged(double)", self.on_paint2)
    
    
    self.ui.pushButton.connect('clicked()',self.on_confirm_tumor)
    self.ui.pushButton_4.connect('clicked()',self.on_finish_segment_tumor)
    self.ui.pushButton_10.connect('clicked()',self.on_split_mri)
    self.ui.pushButton_2.connect('toggled(bool)',self.on_switch_to_normal)
    self.ui.pushButton_9.connect('toggled(bool)',self.on_switch_to_ai)
    self.ui.BrushSphereCheckbox.connect('toggled(bool)', self.on_brush_state_change)
    self.ui.tabWidget_6.hide()
    self.ui.tabWidget_2.setCurrentIndex(0)
    self.TagMaps[util.ResetVersion] = slicer.mrmlScene.AddObserver(util.ResetVersion, self.OnResetVersion)
    self.TagMaps[util.BeginSaveSolution] = slicer.mrmlScene.AddObserver(util.BeginSaveSolution, self.OnBeginSaveSolution)

    self.ui.btnGrowSeed.connect('toggled(bool)', self.on_grow_seed)
    self.ui.btnGrowRange.connect('toggled(bool)', self.on_grow_range)
    self.ui.btnGrowSeed.setCheckable(True)
    self.ui.btnGrowRange.setCheckable(True)
    self.ui.btnGrow.connect('clicked()', self.on_grow)

  
  def on_paint2(self):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    effect = segmentEditorWidget.activeEffect()
    effect.setCommonParameter("BrushRelativeDiameter", self.ui.ctkSliderWidget2.value)
    
    
  def on_grow_seed(self,boolval):
    if boolval:
      self.ui.btnGrowRange.setChecked(False)
    self.set_draw_segment(boolval, 0)
    self.on_paint2()

  def on_grow_range(self,boolval):
    if boolval:
      self.ui.btnGrowSeed.setChecked(False)
      
    self.set_draw_segment(boolval, 1)
    self.on_paint2()

  def set_draw_segment(self, boolval, segment_index):
    if boolval:
      util.trigger_view_tool("Paint")
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      volume_node = self.get_volume()
      seg_node = self.get_segment_node()
      tmpsegmentation = seg_node.GetSegmentation()
      segmentIDs = vtk.vtkStringArray()
      tmpsegmentation.GetSegmentIDs(segmentIDs)
      segmentId = segmentIDs.GetValue(0)
      if segment_index == 1:        
        num = segmentIDs.GetNumberOfValues()
        if num >= 2:
          segmentId = segmentIDs.GetValue(1)
        else:
          segmentId = tmpsegmentation.AddEmptySegment("layer")
      segmentEditorWidget.setSegmentationNode(seg_node)
      segmentEditorWidget.setCurrentSegmentID(segmentId)
      segmentEditorWidget.setSourceVolumeNode(volume_node)
      segmentEditorWidget.setActiveEffectByName("Paint")
      self.ui.lblCover2.hide()
    else:
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setActiveEffectByName("None")
      self.ui.lblCover2.show()

  def on_grow(self):
    self.ui.btnGrowRange.setChecked(False)
    self.ui.btnGrowSeed.setChecked(False)
    volume_node = self.get_volume()
    seg_node = self.get_segment_node()
    tmpsegmentation = seg_node.GetSegmentation()
    segmentIDs = vtk.vtkStringArray()
    tmpsegmentation.GetSegmentIDs(segmentIDs)
    num = segmentIDs.GetNumberOfValues()
    if num < 2:
      return
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(seg_node)
    segmentEditorWidget.setSourceVolumeNode(volume_node)
    segmentEditorWidget.setActiveEffectByName("Grow from seeds")
    effect = segmentEditorWidget.activeEffect()
    effect.self().onPreview()
    effect.self().onApply()
    segmentId = segmentIDs.GetValue(1)
    tmpsegmentation.RemoveSegment(segmentId)
    segmentId = segmentIDs.GetValue(0)
    segmentEditorWidget.setCurrentSegmentID(segmentId)
    seg_node.SetAttribute("is_threshold_seg", "1")
    #util.singleShot(0,lambda:effect.self().onApply())
    pass

  def OnBeginSaveSolution(self,_a,_b):
    if self.ui.btnPaint.isChecked():
      self.ui.btnPaint.setChecked(False)
    pass

  def exit(self):
    util.trigger_view_tool("")
  
  def on_switch_to_normal(self, state):
    if state == False:
      return
    self.ui.pushButton_9.setChecked(False)
    self.ui.tabWidget_2.setCurrentIndex(0)
  
  def on_mask_state_change(self, state):
    if state == True:
      seg_name = self.get_segment_name()
      seg_node = util.getFirstNodeByName(seg_name)
      if seg_node == None:
        util.showWarningText('请先用“阈值创建”创建一个遮罩')
        return
      is_threshold_seg = seg_node.GetAttribute("is_threshold_seg")
      if is_threshold_seg != "1":
        util.showWarningText('请先用“阈值创建”创建一个遮罩')
        return
      segment = util.GetNthSegment(seg_node,0)
      print(segment)
      segment.SetColor([0, 1, 0])
      tmpsegmentation = seg_node.GetSegmentation()
      
      segmentIDs = vtk.vtkStringArray()
      tmpsegmentation.GetSegmentIDs(segmentIDs)
      segmentId = segmentIDs.GetValue(0)
      self.mask_segment_id = segmentId
      currentSegmentID = tmpsegmentation.AddEmptySegment("layer")
      print(currentSegmentID)
      segment2 = tmpsegmentation.GetSegment(currentSegmentID)
      segment2.SetColor([1, 0, 0])
      
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor      
      segmentEditorWidget.setCurrentSegmentID(currentSegmentID)
      segmentEditorNode = segmentEditorWidget.mrmlSegmentEditorNode()
      # 获取所有分段 ID

      segmentEditorNode.SetMaskSegmentID(segmentId)
      segmentEditorNode.SetMaskMode(5)
      pass
    else:
      if self.mask_segment_id == "":
        return
      seg_name = self.get_segment_name()
      seg_node = util.getFirstNodeByName(seg_name)
      if seg_node == None:
        return
      is_threshold_seg = seg_node.GetAttribute("is_threshold_seg")
      if is_threshold_seg != "1":
        return
      segment = util.GetNthSegment(seg_node,0)
      tmpsegmentation = seg_node.GetSegmentation()
      tmpsegmentation.RemoveSegment(self.mask_segment_id)
      self.mask_segment_id = ""
      self.ui.btnPaint.setChecked(False)
      util.color_unit_list.fresh_node_color(seg_node)
      pass
  
  def is_mri(self):
    volumeNode = self.get_volume()
    scalarRange = util.GetScalarRange(volumeNode)
    if scalarRange[1]-scalarRange[0] < 1500:
      # Small dynamic range, probably MRI
      return True
    else:
      # Larger dynamic range, probably CT
      return False
  
  def on_split_mri(self):
    util.getModuleWidget("BrainParcellation").inputNode = self.get_volume()
    util.getModuleWidget("BrainParcellation").onRunButton()
    # segmentationNode = slicer.mrmlScene.GetFirstNodeByName("脑功能区")
    # if segmentationNode is None:
    #   return
    # segmentationNode.SetAttribute("alias_name","脑区")
    # util.color_unit_list.add_item(segmentationNode, 2)
    # util.tips_unit_list.add_item(segmentationNode, 2)
    # coloararr = []
    # segmentIds = vtk.vtkStringArray()
    # segmentationNode.GetSegmentation().GetSegmentIDs(segmentIds)
    # for sname1 in self.english_v:
    #   for segmentIdindex in range(segmentIds.GetNumberOfValues()):
    #     segmentId = segmentIds.GetValue(segmentIdindex)
    #     segment = segmentationNode.GetSegmentation().GetSegment(segmentId)
    #     sname = segment.GetName()
    #     if sname1  == sname:
    #       coloararr.append(segment.GetColor())
    # print("*******************************\n")
    # print(coloararr)
    # print("\n*******************************************")
        
      
  
  def on_switch_to_ai(self, state):
    if state == False:
      return
    self.ui.pushButton_2.setChecked(False)
    if self.is_mri():
      self.ui.tabWidget_2.setCurrentIndex(2)
    else:
      self.ui.tabWidget_2.setCurrentIndex(1)
  
  def OnResetVersion(self,_a,_b):
    pass
  
  def on_redo(self):
      util.trigger_view_tool("")
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.redo()
  
  def on_choose_all(self,val):
    for key in self.templateListMRI:
      key.ui.checkBox.setChecked(val)
  
  def on_undo(self):
      util.trigger_view_tool("")
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.undo()    
  
  def enter(self):
    pass
      
    
  def on_finish_segment_tumor(self):
    util.trigger_view_tool("")
    self.on_grow()
    #self.ui.tabWidget_2.setCurrentIndex(1)
    if self.ui.tabWidget_5.currentIndex == 0:
      self.on_confirm_tumor()
    seg_name = self.get_segment_name()
    seg_node = util.getFirstNodeByName(seg_name)
    if seg_node == None:
      util.getModuleWidget("UnitCTHeadVolumes").ui.btnTurmo_2.setChecked(False)
      return
    segment = util.GetNthSegment(seg_node,0)
    seg_alias = self.get_segment_alias()    
    seg_node.SetAttribute("alias_name",seg_alias)
    util.color_unit_list.add_item(seg_node, 2)
    util.tips_unit_list.add_item(seg_node, 2)
    util.send_event_str(G.FinishCreateTumor)
    util.getModuleWidget("UnitCTHeadVolumes").ui.btnTurmo_2.setChecked(False)

  def on_leveltracing(self,boolval):
    if boolval:
      util.trigger_view_tool("Level tracing")
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      volume_node = self.get_volume()
      segmentEditorWidget.setSegmentationNode(self.get_segment_node())
      segmentEditorWidget.setSourceVolumeNode(volume_node)
      segmentEditorWidget.setActiveEffectByName("Level tracing")
    else:
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setActiveEffectByName("None")
    
  def on_fill(self):
    util.trigger_view_tool("")
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setActiveEffectByName("Fill between slices")
    effect = segmentEditorWidget.activeEffect()
    effect.self().onPreview()
    util.singleShot(0,lambda:effect.self().onApply())
  
  def on_draw(self,boolval):
    if boolval:
      util.trigger_view_tool("Draw")
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      volume_node = self.get_volume()
      segmentEditorWidget.setSegmentationNode(self.get_segment_node())
      segmentEditorWidget.setSourceVolumeNode(volume_node)
      segmentEditorWidget.setActiveEffectByName("Draw")
    else:
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setActiveEffectByName("None")
  
  
  def get_segment_node(self):
    segment_node = util.getFirstNodeByName(self.get_segment_name())
    if segment_node is None:
      util.CreateDefaultSegmentationNode(self.get_segment_name())
      
      segment_node = util.getFirstNodeByName(self.get_segment_name())
      segment = util.GetNthSegment(segment_node,0)
      util.GetDisplayNode(segment_node)
      segment.SetColor([1,0,0])      
      seg_alias = self.get_segment_alias()    
      segment_node.SetAttribute("alias_name",seg_alias)
      util.color_unit_list.add_item(segment_node, 2)
      util.tips_unit_list.add_item(segment_node, 2)
      
    return segment_node
  
  def monai_3dseg(self):
    pass
  
  def on_start_paint(self,boolval):
    if boolval:
      self.ui.tabWidget_5.setCurrentIndex(1)
      self.ui.lblCover.hide()
      util.trigger_view_tool("Paint")
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      volume_node = self.get_volume()
      segmentEditorWidget.setSegmentationNode(self.get_segment_node())
      segmentEditorWidget.setSourceVolumeNode(volume_node)
      segmentEditorWidget.setActiveEffectByName("Paint")
      effect = segmentEditorWidget.activeEffect()
      effect.setCommonParameter("EditIn3DViews", 1)
      effect.setCommonParameter("BrushRelativeDiameter", self.ui.ctkSliderWidget.value)
      effect.setCommonParameter("BrushSphere", int(self.ui.BrushSphereCheckbox.isChecked()))
      #self.ui.cbox_mask.setEnabled(True)
    else:
      self.ui.lblCover.show()
      #self.ui.cbox_mask.setChecked(False)
      #self.ui.cbox_mask.setEnabled(False)
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setActiveEffectByName("None")

  def on_brush_state_change(self, boolval):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    effect = segmentEditorWidget.activeEffect()
    effect.setCommonParameter("BrushSphere", int(self.ui.BrushSphereCheckbox.isChecked()))    
      
  def on_paint(self):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    effect = segmentEditorWidget.activeEffect()
    effect.setCommonParameter("EditIn3DViews", 1)
    effect.setCommonParameter("BrushRelativeDiameter", self.ui.ctkSliderWidget.value)
  
  def on_scissors(self,boolval):
    if boolval:
      util.trigger_view_tool("scissors")
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      volume_node = self.get_volume()
      segment_node = util.getFirstNodeByName(self.get_segment_name())
      segmentEditorWidget.setSegmentationNode(segment_node)
      segmentEditorWidget.setSourceVolumeNode(volume_node)
      segmentEditorWidget.setActiveEffectByName("Scissors")
    else:
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setActiveEffectByName("None")
  
  def on_island(self,boolval):
    if boolval:
      util.trigger_view_tool("islands")
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      volume_node = self.get_volume()
      segment_node = util.getFirstNodeByName(self.get_segment_name())
      if segment_node == None:
        print("segment_node == None")
        return
      segmentEditorWidget.setSegmentationNode(segment_node)
      segmentEditorWidget.setSourceVolumeNode(volume_node)
      segmentEditorWidget.setActiveEffectByName("Islands")
      effect = segmentEditorWidget.activeEffect()
      effect.setParameter("Operation", "KEEP_LARGEST_ISLAND")
      effect.self().onApply()
      segmentEditorWidget.setActiveEffectByName("None")
    else:
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setActiveEffectByName("None")
  
  def on_save_island(self,boolval):
    if boolval:
      util.trigger_view_tool("islands_keep")
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      volume_node = self.get_volume()
      segment_node = util.getFirstNodeByName(self.get_segment_name())
      if segment_node == None:
        print("segment_node == None")
        return
      segmentEditorWidget.setSegmentationNode(segment_node)
      segmentEditorWidget.setSourceVolumeNode(volume_node)
      segmentEditorWidget.setActiveEffectByName("Islands")
      effect = segmentEditorWidget.activeEffect()
      effect.setParameter("Operation", "KEEP_SELECTED_ISLAND")
      effect.setParameter("MinimumSize","1000")
    else:
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setActiveEffectByName("None")

  def get_segment_name(self):
    type_des = "血肿"
    if self.use_type == 1:
      type_des = "脑室"
    index = util.paras[type_des]
    name1 = f"{type_des}"    
    return name1

  def get_segment_alias(self):
    alias = "血肿"
    if self.use_type == 1:
      alias = "脑室"
    return alias
  
  def on_confirm_tumor(self):
    volume_node = self.get_volume()
    if not volume_node:
      print("not volume_node")
      return
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    effect = segmentEditorWidget.activeEffect()
    effect.self().onApply()
    
    seg_name = self.get_segment_name()
    seg_node = util.getFirstNodeByName(seg_name)
    color255 = util.color_unit_list.get_unique_color()
    segment = util.GetNthSegment(seg_node,0)
    segment.SetColor([1,0,0])
    seg_alias = self.get_segment_alias()  
    seg_node.SetAttribute("alias_name",seg_alias)
    seg_node.SetAttribute("is_threshold_seg", "1")
    util.color_unit_list.add_item(seg_node, 2)
    util.tips_unit_list.add_item(seg_node, 2)
    self.ui.tabWidget_5.setCurrentIndex(1)
    util.GetDisplayNode(seg_node).SetOpacity3D(1)
    layoutManager = slicer.app.layoutManager()

    for threeDViewIndex in range(layoutManager.threeDViewCount) :
      controller = layoutManager.threeDWidget(threeDViewIndex).threeDController()
      controller.resetFocalPoint()
      threeDView = layoutManager.threeDWidget(threeDViewIndex).threeDView()
      threeDView.resetCamera()

  def onThresholdValuesChanged2(self,v1,v2):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    effect = segmentEditorWidget.activeEffect()
    if not effect:
      return
    effect.setParameter("MinimumThreshold", self.ui.ctkRangeWidget.minimumValue)
    effect.setParameter("MaximumThreshold", self.ui.ctkRangeWidget.maximumValue)
  
  def on_cancel_active(self):
    util.trigger_view_tool("")
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setActiveEffectByName("None")

  def on_threshold_start(self):
    self.ui.tabWidget_5.setCurrentIndex(0)
    
    volume_node = self.get_volume()
    if not volume_node:
      return
    seg_name = self.get_segment_name()
    if util.getFirstNodeByName(seg_name) is None:
      util.CreateDefaultSegmentationNode(seg_name)
    segment_node = util.getFirstNodeByName(seg_name)  
    segment = util.GetNthSegment(segment_node,0)
    segment.SetColor([1,0,0])
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

  def reset_state(self):
    self.ui.tabWidget_5.setCurrentIndex(1)
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setActiveEffectByName("None")
    util.trigger_view_tool("")
    pass