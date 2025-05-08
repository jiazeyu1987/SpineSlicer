import slicer,qt,vtk,ctk
import slicer.util as util
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from Base.JBaseExtension import JBaseExtensionWidget
import UnitPunctureGuideLib.G_UnitPunctureGuide as G
#
# UnitCTHeadVolumes
#


class UnitCTHeadVolumes(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UnitCTHeadVolumes"  # TODO: make this more human readable by adding spaces
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
# UnitCTHeadVolumesWidget
#

class UnitCTHeadVolumesWidget(JBaseExtensionWidget):
  button_map = {}
  volume=None
  old_value=0
  chest_value = -254
  ctaaa_value = -762
  ctaaa2_value = 0
  is_use_event = True
  container_register = None
  container_rotate = None
  def setup(self):
    super().setup()
    
    
  def init_ui(self):    
    self.ui.btnROI.connect('toggled(bool)',self.on_roi)    
    self.ui.btn3D.connect('toggled(bool)',self.on_volumerendering)
    self.ui.btnGrayAdjust.connect('toggled(bool)',self.on_gray_scale)
    self.button_map['wl_auto'] = self.ui.btnGrayAdjust
    self.ui.btnMPR.connect('toggled(bool)',self.on_mpr)
    self.button_map['mpr'] = self.ui.btnMPR


    self.ui.btnCut.connect('clicked()',self.on_confirm_scissors)
    self.ui.btnRemove.connect('clicked()',self.on_strip_board)
    self.ui.btnLongmen.connect('clicked()',self.on_strip_longmen)
    
    self.button_map['strip_board'] = self.ui.btnRemove
    self.button_map['strip_longmen'] = self.ui.btnLongmen
    
    self.button_map['visible'] = self.ui.btn3D
    self.ui.btnCT1.connect('toggled(bool)',self.on_ctaaa)
    self.button_map['ctaaa'] = self.ui.btnCT1
    self.ui.btnCT2.connect('toggled(bool)',self.on_ctaaa2)
    self.button_map['ctaaa2'] = self.ui.btnCT2
    self.ui.btnCTChest.connect('toggled(bool)',self.on_chest)
    self.button_map['ctchest'] = self.ui.btnCTChest
    self.ui.btnGray.connect('toggled(bool)',self.on_preset_gray)
    self.button_map['preset_gray'] = self.ui.btnGray
    self.ui.btnColor.connect('toggled(bool)',self.on_preset_rainbow)
    self.button_map['preset_color'] = self.ui.btnColor
    
    self.ui.btnRotate.connect('toggled(bool)',self.on_rotate)
    self.button_map['rotate'] = self.ui.btnRotate
    self.ui.widget_8.setVisible(False)
    
    self.ui.shift_slider.connect('valueChanged(double)',self.on_shift_change)
    
    self.ui.lblCT1.setAttribute(qt.Qt.WA_TransparentForMouseEvents, True)
    self.ui.lblCT2.setAttribute(qt.Qt.WA_TransparentForMouseEvents, True)
    self.ui.lblCTChest.setAttribute(qt.Qt.WA_TransparentForMouseEvents, True)
    self.ui.label_11.setAttribute(qt.Qt.WA_TransparentForMouseEvents, True)
    self.ui.label_12.setAttribute(qt.Qt.WA_TransparentForMouseEvents, True)
    self.ui.label_13.setAttribute(qt.Qt.WA_TransparentForMouseEvents, True)
    
    self.ui.qLNodeComboBox.setMRMLScene(slicer.mrmlScene)
    self.ui.qLNodeComboBox.setProperty("nodeTypes", ["vtkMRMLScalarVolumeNode"])
    self.ui.qLNodeComboBox.setProperty("noneEnabled", False)
    self.ui.qLNodeComboBox.setProperty("addEnabled", False)
    self.ui.qLNodeComboBox.setProperty("renameEnabled", False)
    self.ui.qLNodeComboBox.setProperty("removeEnabled", False)
    
    self.ui.btnRegister.connect('toggled(bool)',self.on_register)
    self.ui.qLNodeComboBox.connect('currentNodeChanged(bool)', self.oncurrentNodeChanged)
    
    self.ui.pushButton.connect('clicked()',self.use_as_main)
    
    self.TagMaps[util.ResetVersion] = slicer.mrmlScene.AddObserver(util.ResetVersion, self.OnResetVersion)
    self.TagMaps[util.close_volume_rendering] = slicer.mrmlScene.AddObserver(util.close_volume_rendering, self.Onclose_volume_rendering)
    self.TagMaps[G.show_volume_rendering] = slicer.mrmlScene.AddObserver(G.show_volume_rendering, self.Onshow_volume_rendering)
    slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeAddedEvent, self.onNodeAdded)
    slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeRemovedEvent, self.onNodeRemove)
    
    self.ui.btnCT1.setChecked(True)
    self.on_ctaaa(True)

    self.container_register = util.getModuleWidget("UnitRegister").get_container()
    util.addWidget2(self.ui.contain_register, self.container_register)
    
    self.container_rotate = util.getModuleWidget("UnitRotateVolume").get_container()
    util.addWidget2(self.ui.contain_rotate, self.container_rotate)
    self.ui.tabWidget.tabBar().hide()
    
    self.ui.widget_9.setVisible(False)
    self.ui.widget_8.setVisible(False)
    self.ui.widget_19.setVisible(False)
    self.ui.widget_18.setVisible(False)
    self.ui.btn3D.setVisible(False)
    import os
    
    module_path = os.path.dirname(util.modulePath('UnitReconstruction'))
    file_path = (module_path + '/Resources/Icons/seg_turmo.png').replace("\\", "/")
    file_style = "background-image: url(" + file_path + ");"
    self.ui.btnTurmo_2.setStyleSheet(file_style)
    
    file_path = (module_path + '/Resources/Icons/seg_skin.png').replace("\\", "/")
    file_style = "background-image: url(" + file_path + ");"
    self.ui.btn_quick_skin_2.setStyleSheet(file_style)
    
    file_path = (module_path + '/Resources/Icons/seg_bone.png').replace("\\", "/")
    file_style = "background-image: url(" + file_path + ");"
    self.ui.btn_quick_bone_2.setStyleSheet(file_style)
    
    self.ui.btn_quick_skin_2.connect('clicked()', lambda:util.getModuleWidget("UnitReconstruction").on_quick_skin())
    self.ui.btn_quick_bone_2.connect('clicked()', lambda:util.getModuleWidget("UnitReconstruction").on_quick_bone())
    
    self.ui.btnTurmo_2.connect('toggled(bool)', self.on_tumor_click)
  
  
  def on_tumor_click(self,val):
    val1  =  util.getModuleWidget("UnitReconstruction").on_turmo_click(val)
    if val1 == -1:
      self.ui.btnTurmo_2.blockSignals(True)
      self.ui.btnTurmo_2.setChecked(False)
      self.ui.btnTurmo_2.blockSignals(False)
      
  def on_rotate(self,val):
    self.ui.tabWidget.setCurrentIndex(1)
    left_width = 205
    is_visible = False
    if val:
      left_width = 607
      is_visible = True
      volume = util.getFirstNodeByClassByAttribute(util.vtkMRMLScalarVolumeNode,"main_node","1")
      util.getModuleWidget("UnitRotateVolume").show_volume(volume)
    else:
      if not util.getModuleWidget("UnitRotateVolume").confirm:
        transform_node = util.getModuleWidget("UnitRotateVolume").rotated_volume.GetParentTransformNode()
        util.RemoveNode(transform_node)
        util.RemoveNode(util.getModuleWidget("UnitRotateVolume").rotated_volume)
      else:
        util.getModuleWidget("UnitRotateVolume").rotated_volume.HardenTransform()
        self.ui.qLNodeComboBox.setCurrentNode(util.getModuleWidget("UnitRotateVolume").rotated_volume)
        self._use_as_main()
      left_width = 205
      
    self.ui.line.setVisible(is_visible)
    self.ui.contain_register.setVisible(is_visible)
    self.ui.UnitCTHeadVolumes.setMaximumWidth(left_width)
    self.ui.UnitCTHeadVolumes.setMinimumWidth(left_width)
    util.layout_panel("middle_left").setMaximumWidth(left_width)
    util.layout_panel("middle_left").setMinimumWidth(left_width)
  
  
  def enter(self):
    print(self.ui.UnitCTHeadVolumes)
    print("volume enter")
    self.show_register(False)
    pass

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def onNodeAdded(self,caller, event, calldata):
    if isinstance(calldata, slicer.vtkMRMLScalarVolumeNode):
      util.singleShot(100,lambda:calldata.GetScalarVolumeDisplayNode().AutoWindowLevelOff())
      util.singleShot(200,lambda:calldata.GetScalarVolumeDisplayNode().SetWindowLevel(80,40))
      self.fresh_scalaers()
      
  @vtk.calldata_type(vtk.VTK_OBJECT)
  def onNodeRemove(self,caller, event, calldata):
    if isinstance(calldata, slicer.vtkMRMLScalarVolumeNode):
      self.fresh_scalaers()   
  
  def oncurrentNodeChanged(self,val):
    node = self.ui.qLNodeComboBox.currentNode()
    if node is None:
      return

    self.ui.btnGrayAdjust.setChecked(False)
    #self.ui.btnMPR.setChecked(False)
    self.ui.btnGray.setChecked(True)

    if not self.is_mri(node):
      self.ui.btnCT1.setChecked(True)
      self.on_ctaaa(True)
    else:
      self.ui.btnCT2.setChecked(True)
      self.on_ctaaa2(True)
  
    if node.GetAttribute("main_node") == "1":
      self.ui.pushButton.setVisible(False)
      self.ui.label_4.setVisible(True)
    else:
      self.ui.pushButton.setVisible(True)
      self.ui.label_4.setVisible(False)
    
  def use_as_main(self):
    res = util.messageBox("更换主影像将删除现有的所有数据，是否继续？",windowTitle=util.tr("提示"))
    if res == 0:
      return
    self._use_as_main()

  def _use_as_main(self):
    nodes = util.getNodesByClass(util.vtkMRMLScalarVolumeNode)
    for node in nodes:
      node.SetAttribute("main_node","0")
    node = self.ui.qLNodeComboBox.currentNode()
    node.SetAttribute("main_node","1")
    util.send_event_str(G.ChangeMainVolume)
    util.RemoveNodeByName("FullHeadSegmentationNode")
    #util.color_unit_list.clear_with_nodes()
    self.ui.pushButton.setVisible(False)
    self.ui.label_4.setVisible(True)
    
  def on_register(self,val):
    self.show_register(val)
  
  def show_register(self, val):
    self.ui.tabWidget.setCurrentIndex(0)
    left_width = 205
    is_visible = False
    if val:
      left_width = 607
      is_visible = True
    self.ui.line.setVisible(is_visible)
    self.ui.contain_register.setVisible(is_visible)
    self.ui.UnitCTHeadVolumes.setMaximumWidth(left_width)
    self.ui.UnitCTHeadVolumes.setMinimumWidth(left_width)
    util.layout_panel("middle_left").setMaximumWidth(left_width)
    util.layout_panel("middle_left").setMinimumWidth(left_width)
  
  def Onclose_volume_rendering(self,_a,_b):
    self.button_map['visible'].setChecked(False)
    
  def Onshow_volume_rendering(self,_a,_b):
    self.button_map['visible'].setChecked(True)
  
  def OnResetVersion(self,_a,_b):
    pass
  
  
  
  def on_strip_longmen(self):
    if self.get_volume() is None:
      util.showWarningText("当前没有加载数据")
      return
    lmj = util.getModuleWidget("LMJ")
    need_longmen = lmj.is_error(self.get_volume())
    if not need_longmen:
      util.showWarningText("当前数据没有龙门角")
      return
    res = util.messageBox("是否要修正龙门角",windowTitle=util.tr("提示"))
    if res == 0:
      return
    util.send_event_str(util.ProgressStart,"正在修正龙门角")
    util.send_event_str(util.ProgressValue,"30")
    lmj.ui.volumeSelector.setCurrentNode(self.get_volume())
    try:
      lmj.createAcquisitionTransform()
      self.get_volume().HardenTransform()
      self.get_volume().SetAttribute("no_longmen_check","true")
      util.send_event_str(util.ProgressValue,"100")
      util.showWarningText("龙门矫正成功")
    except Exception as e:
      util.send_event_str(util.ProgressValue,"100")
      util.showWarningText("龙门矫正失败")
    util.reinit(background_node=self.get_volume())
  
  
  def on_shift_change(self,value):
    if not self.get_volume():
      return
    if not self.is_use_event:
      return
    volRenWidget = slicer.modules.volumerendering.widgetRepresentation()
    if volRenWidget is None:
      return
    volRenLogic = slicer.modules.volumerendering.logic()
    displayNode = volRenLogic.CreateDefaultVolumeRenderingNodes(self.get_volume())
    # Make sure the proper volume property node is set
    volumePropertyNode = displayNode.GetVolumePropertyNode()
    if volumePropertyNode is None:
      return
    differ = value-self.old_value
    self.old_value = value
    volumePropertyNodeWidget = slicer.util.findChild(volRenWidget, "VolumePropertyNodeWidget")
    volumePropertyNodeWidget.setMRMLVolumePropertyNode(volumePropertyNode)
    # Adjust the transfer function
    volumePropertyNodeWidget.moveAllPoints(differ, 0, False)
    return
  
  def on_confirm_scissors(self):
    cropLogic = slicer.modules.cropvolume.logic()
    cvpn = slicer.vtkMRMLCropVolumeParametersNode()
    node = self.get_volume()
    volRenLogic = slicer.modules.volumerendering.logic()
    displayNode = volRenLogic.CreateDefaultVolumeRenderingNodes(node)
    roid_node = displayNode.GetROINode()
    
    if not node:
      util.showWarningText("请先加载DICOM数据")
      return
    if not roid_node:
      util.showWarningText("请先打开ROI")
      return
    new_node = util.AddNewNodeByClass(util.vtkMRMLScalarVolumeNode)
    new_node.SetName(node.GetName())
    cvpn.SetROINodeID(roid_node.GetID())
    cvpn.SetInputVolumeNodeID(node.GetID())
    cvpn.SetOutputVolumeNodeID(new_node.GetID())
    cvpn.SetFillValue(-1000)
    util.send_event_str(util.ProgressStart,"正在剪切DICOM数据")
    util.send_event_str(util.ProgressValue,"30")
    cropLogic.Apply(cvpn)
    self.ui.btnROI.setChecked(False)
    self.ui.btn3D.setChecked(False)
    util.RemoveNode(roid_node)
    self.ui.qLNodeComboBox.setCurrentNode(new_node)
    self.ui.btn3D.setChecked(True)
    util.send_event_str(util.ProgressValue,"100")
    util.RemoveNode(node)
  
  def on_roi(self,boolval):
    if boolval:
      self.ui.btnCut.setEnabled(True)
    else:
      self.ui.btnCut.setEnabled(False)
    volume = self.get_volume()
    if not volume:
      return
    volRenLogic = slicer.modules.volumerendering.logic()
    displayNode = volRenLogic.CreateDefaultVolumeRenderingNodes(volume)
    roiNode = displayNode.GetROINode()
    if not roiNode:
      roiNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsROINode")
      displayNode.SetAndObserveROINodeID(roiNode.GetID())
      util.GetDisplayNode(roiNode).SetPropertiesLabelVisibility(False)
      roiNodeDisplayNode = roiNode.GetDisplayNode()
      roiNode = displayNode.GetROINode()
      roiNodeDisplayNode.SetFillOpacity(0)
      cropVolumeParameters = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLCropVolumeParametersNode")
      cropVolumeParameters.SetInputVolumeNodeID(volume.GetID())
      cropVolumeParameters.SetROINodeID(roiNode.GetID())
      slicer.modules.cropvolume.logic().SnapROIToVoxelGrid(cropVolumeParameters)  # optional (rotates the ROI to match the volume axis directions)
      slicer.modules.cropvolume.logic().FitROIToInputVolume(cropVolumeParameters)
      slicer.mrmlScene.RemoveNode(cropVolumeParameters)
    
    displayNode.SetCroppingEnabled(True)
    roiNode.GetDisplayNode().SetVisibility(boolval)
      
  
  def on_gray_scale(self,boolval):
    print("on_gray_scale")
    if boolval:
      util.trigger_view_tool("")
      util.getModuleWidget("UnitScore").do_gray_scale = True
      self.button_map['mpr'].setChecked(False)
      slicer.app.applicationLogic().GetInteractionNode().SetAttribute("AdjustWindowLevelMode","Rectangle")
      slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(slicer.vtkMRMLInteractionNode.AdjustWindowLevel)
    else:
      slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(2)
  
  def showVolumeRendering(self,volumeNode,boolval):
    print("Show volume rendering of node " + volumeNode.GetName())
    volRenLogic = slicer.modules.volumerendering.logic()
    displayNode = volRenLogic.CreateDefaultVolumeRenderingNodes(volumeNode)
    displayNode.SetVisibility(boolval)
    if boolval:
      displayNode.GetVolumePropertyNode().Copy(volRenLogic.GetPresetByName(self.get_preset_name()))
      self.ui.shift_slider.blockSignals(True)
      self.ui.shift_slider.setValue(0)
      self.ui.lblCover.setVisible(False)
      self.ui.shift_slider.blockSignals(False)
    else:
      self.ui.lblCover.setVisible(True)

  def get_preset_name(self):
    preset = "CT-AAA"
    if self.ui.btnCT2.isChecked():
      preset = "CT-AAA2"
    elif self.ui.btnCTChest.isChecked():
      preset = "CT-Chest-Contrast-Enhanced"
    return preset
  def is_mri(self,volumeNode):
    if not volumeNode:
      return
    if not  volumeNode.GetImageData():
      return
    scalarRange = util.GetScalarRange(volumeNode)
    if scalarRange[1]-scalarRange[0] < 1500:
      # Small dynamic range, probably MRI
      return True
    else:
      # Larger dynamic range, probably CT
      return False
  
  def exit(self):
    layoutManager = slicer.app.layoutManager()
    volume = util.getFirstNodeByClassByAttribute(util.vtkMRMLScalarVolumeNode,"main_node","1")
    self.ui.qLNodeComboBox.setCurrentNode(volume)
    self.ui.btnTurmo_2.setChecked(False)
    
    
  def fresh_scalaers(self):
    volumes = util.getNodesByClass(util.vtkMRMLScalarVolumeNode)
    if len(volumes) == 1:
      self.ui.qLNodeComboBox.setCurrentNode(volumes[0])
      self.ui.widget_18.setVisible(False)
      volumes[0].SetAttribute("main_node","1")
      util.send_event_str(G.ChangeMainVolume)
      self.ui.pushButton.setVisible(False)
      self.ui.label_4.setVisible(True)
      self.oncurrentNodeChanged("")
    else:
      self.ui.widget_18.setVisible(False)
      
    

  def OnArchiveLoaded(self,_a,_b):
    volumeNode = self.get_volume()
    print("volumeNode") 
    if not volumeNode:
      return
    
    volRenLogic = slicer.modules.volumerendering.logic()
    displayNode = volRenLogic.GetFirstVolumeRenderingDisplayNode(volumeNode)
    
    if not displayNode:
      displayNode = volRenLogic.CreateDefaultVolumeRenderingNodes(volumeNode)
    boolval = displayNode.GetVisibility()
    #self.button_map['visible'].setChecked(boolval)
    
    boolval = slicer.app.applicationLogic().GetIntersectingSlicesEnabled(slicer.vtkMRMLApplicationLogic.IntersectingSlicesVisibility)
    if boolval:
      self.button_map['mpr'].setChecked(True)
    else:
      self.button_map['mpr'].setChecked(False)
      
    roiNode = displayNode.GetROINode()
    if roiNode:
      vis = roiNode.GetDisplayNode().GetVisibility()
      if vis==1:
        self.button_map['roi'].setChecked(vis)
    
    self.button_map['visible'].setChecked(True)
    self.button_map['visible'].setChecked(False)
    
  def on_volumerendering(self,boolval):
    if self.get_volume():
      if boolval:
        self.ui.shift_slider.setValue(0)
        self.showVolumeRendering(self.get_volume(),True)
      else:
        self.ui.shift_slider.setValue(0)
        self.showVolumeRendering(self.get_volume(),False)
    util.reinit3D()
  
  def on_mpr(self,boolval):
    print("on_mpr")
    if boolval:
      util.getModuleWidget("UnitScore").do_mpr = True

      util.trigger_view_tool("")
      self.button_map['wl_auto'].setChecked(False)
    slicer.app.applicationLogic().SetIntersectingSlicesEnabled(slicer.vtkMRMLApplicationLogic.IntersectingSlicesVisibility, boolval)
    slicer.app.applicationLogic().SetIntersectingSlicesEnabled(slicer.vtkMRMLApplicationLogic.IntersectingSlicesInteractive,boolval)
    displayNodes = util.getNodesByClass("vtkMRMLSliceDisplayNode")
    for displayNode in displayNodes:
      displayNode.SetIntersectingSlicesLineThicknessMode(2)
    sliceNodes = util.getNodesByClass("vtkMRMLSliceNode")
    for sliceNode in sliceNodes:
      sliceNode.Modified()
  
  def on_preset_rainbow(self, boolval):
    if not boolval:
      return
    self.ui.btnGray.setChecked(False)
    print("on_preset_rainbow")
    if self.get_volume():
      util.GetDisplayNode(self.get_volume()).SetAndObserveColorNodeID("vtkMRMLColorTableNodeRainbow")
  def on_preset_gray(self, boolval):
    if not boolval:
      return
    self.ui.btnColor.setChecked(False)
    print("on_preset_gray")
    if self.get_volume():
      util.GetDisplayNode(self.get_volume()).SetAndObserveColorNodeID("vtkMRMLColorTableNodeGrey")
  
  def on_ctaaa(self, boolval):
    if not boolval:
      return
    self.ui.btnCT2.setChecked(False)
    self.ui.btnCTChest.setChecked(False)
    self.ui.shift_slider.setValue(0)
    volumeNode = self.get_volume()
    if volumeNode:
      volRenLogic = slicer.modules.volumerendering.logic()
      displayNode = volRenLogic.CreateDefaultVolumeRenderingNodes(volumeNode)
      displayNode.GetVolumePropertyNode().Copy(volRenLogic.GetPresetByName("CT-AAA"))
      self.updatePresetSliderRange(displayNode.GetVolumePropertyNode())
      self.ui.shift_slider.setValue(0)
      #self.ui.shift_slider.setValue(self.ctaaa_value)
      #qt.QTimer.singleShot(1000,lambda:self.ui.shift_slider.setValue(self.ctaaa_value))
    
  def on_ctaaa2(self, boolval):
    if not boolval:
      return
    self.ui.btnCT1.setChecked(False)
    self.ui.btnCTChest.setChecked(False)
    self.ui.shift_slider.setValue(0)
    volumeNode = self.get_volume()
    print("ctaaaa2")
    if volumeNode:
      print("ctaaaa2 ed")
      volRenLogic = slicer.modules.volumerendering.logic()
      displayNode = volRenLogic.CreateDefaultVolumeRenderingNodes(volumeNode)
      displayNode.GetVolumePropertyNode().Copy(volRenLogic.GetPresetByName("CT-AAA2"))
      self.updatePresetSliderRange(displayNode.GetVolumePropertyNode())
      self.ui.shift_slider.setValue(0)
      #self.ui.shift_slider.setValue(self.ctaaa2_value)
      #qt.QTimer.singleShot(1000,lambda:self.ui.shift_slider.setValue(self.ctaaa2_value))

  
  def on_chest(self, boolval):
    if not boolval:
      return
    self.ui.btnCT2.setChecked(False)
    self.ui.btnCT1.setChecked(False)
    self.ui.shift_slider.setValue(0)
    volumeNode = self.get_volume()
    if volumeNode:
      volRenLogic = slicer.modules.volumerendering.logic()
      displayNode = volRenLogic.CreateDefaultVolumeRenderingNodes(volumeNode)
      displayNode.GetVolumePropertyNode().Copy(volRenLogic.GetPresetByName("CT-Chest-Contrast-Enhanced"))
      self.updatePresetSliderRange(displayNode.GetVolumePropertyNode())
      self.ui.shift_slider.setValue(0)
      #qt.QTimer.singleShot(1000,lambda:self.ui.shift_slider.setValue(self.chest_value))

  def updatePresetSliderRange(self, volumePropertyNode):
    tmp_range = volumePropertyNode.GetEffectiveRange()
    transferWidth = tmp_range[1] - tmp_range[0]
    self.ui.shift_slider.minimum = -transferWidth
    self.ui.shift_slider.maximum = transferWidth

    print(tmp_range)
    self.is_use_event = False
    self.is_use_event = True
  def get_volume(self):
    #volume = util.getFirstNodeByClassByAttribute(util.vtkMRMLScalarVolumeNode,"main_node","1")
    #return volume
  
    node = self.ui.qLNodeComboBox.currentNode()
    return node
  
  def on_step1(self):
    print("on_step1")
    
  def on_step2(self):
    print("on_step2")
    
  def on_strip_board(self):
    self.goto_mask_step(1)
  
  
  def goto_mask_step(self,step):
    print("goto_mask_step:",step)
    if step == 1:
      if self.get_volume() is None:
        return
      util.send_event_str(util.ProgressStart,"正在去除背板")
      util.send_event_str(util.ProgressValue,"10")
      if util.getFirstNodeByName("skull_mask_segmentation_node") is None:
        self.m_SegmentationNode = util.CreateDefaultSegmentationNode("skull_mask_segmentation_node")
        self.m_SegmentationNode.SetAttribute("show_in_manager","1")
        self.m_SegmentationNode.SetAttribute("alias_name","初始颅骨")
      else:
        self.m_SegmentationNode = util.getFirstNodeByName("skull_mask_segmentation_node")
      util.send_event_str(util.ProgressValue,"20")
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setSegmentationNode(self.m_SegmentationNode)
      segmentEditorWidget.setSourceVolumeNode(self.get_volume())
      segmentEditorWidget.setActiveEffectByName("Threshold")
      effect = segmentEditorWidget.activeEffect()
      lo, hi = util.GetScalarRange(self.get_volume())
      effect.setParameter("MinimumThreshold", -400)
      effect.setParameter("MaximumThreshold", hi)
      effect.self().onApply()
      
      util.ShowNode3D(self.m_SegmentationNode)
      util.send_event_str(util.ProgressValue,"40")
    
      util.send_event_str(util.ProgressValue,"50")
      cloned_node = util.clone(self.m_SegmentationNode)
      cloned_node.SetName("skull_1")
      util.getModuleLogic('JSegmentEditorTool').islands_max(self.get_volume(),cloned_node)
      cloned_node2 = util.clone(self.m_SegmentationNode)
      util.getModuleLogic('JSegmentEditorTool').substract(self.get_volume(),cloned_node2,cloned_node)
      
      util.RemoveNode(cloned_node)
      self.m_MaskBoardSegmentationNode = cloned_node2
      self.m_MaskBoardSegmentationNode.SetName("m_MaskBoardSegmentationNode")
      
      util.HideNode(self.m_SegmentationNode)
      self.goto_mask_step(2)
    if step == 2:
      
      util.send_event_str(util.ProgressValue,"60")
      cloned_node = util.clone(self.m_MaskBoardSegmentationNode)
      util.getModuleLogic('JSegmentEditorTool').margin_out(self.get_volume(),cloned_node)
      cloned_node.SetName("m_MaskMarginedNode")
      util.HideNode(self.m_MaskBoardSegmentationNode)
      self.m_MaskMarginedNode = cloned_node
      util.HideNode(self.m_MaskMarginedNode)
      self.goto_mask_step(3)
    if step == 3:
      
      
      util.send_event_str(util.ProgressValue,"70")
      out_node = util.AddNewNodeByClass(util.vtkMRMLScalarVolumeNode)
      out_node.SetName("stripeed_mask_basic")
      util.getModuleLogic('JSegmentEditorTool').mask_volume(self.get_volume(),self.m_MaskMarginedNode,self.get_volume(),out_node)
      self.m_OutNode = out_node
      
      util.send_event_str(util.ProgressValue,"100")
      util.singleShot(100,lambda:self.get_volume().SetAndObserveImageData(out_node.GetImageData()))
      util.singleShot(1000,lambda:util.RemoveNode(out_node))
      
      
  def OnBeforeSceneDestroyEvent(self,_a,_b):
    self.button_map['mpr'].setChecked(False)
    self.button_map['wl_auto'].setChecked(False)
    self.button_map['visible'].setChecked(False)
    self.ui.btnROI.setChecked(False)