import slicer,qt,vtk,ctk
import slicer.util as util
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from Base.JBaseExtension import JBaseExtensionWidget
import UnitPunctureGuideLib.G_UnitPunctureGuide as G
#
# UnitPunctureGuideBottom
#


class UnitPunctureGuideBottom(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UnitPunctureGuideBottom"  # TODO: make this more human readable by adding spaces
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
# UnitPunctureGuideBottomWidget
#

class UnitPunctureGuideBottomWidget(JBaseExtensionWidget):
  buttonmap = {}
  old_select_module = ''
  def setup(self):
    super().setup()
    if util.curr_language == 1:
      self.ui.btnData.setMinimumWidth(120)
      self.ui.btnData.setMaximumWidth(120)
      self.ui.btnProcess.setMinimumWidth(145)
      self.ui.btnProcess.setMaximumWidth(145)
      self.ui.btnMask.setMinimumWidth(125)
      self.ui.btnMask.setMaximumWidth(125)
      self.ui.btnBlood.setMinimumWidth(145)
      self.ui.btnBlood.setMaximumWidth(145)
      self.ui.btnReconstruction.setMinimumWidth(135)
      self.ui.btnReconstruction.setMaximumWidth(135)
      self.ui.btnChannel.setMinimumWidth(155)
      self.ui.btnChannel.setMaximumWidth(155)
      self.ui.btnGuide.setMinimumWidth(145)
      self.ui.btnGuide.setMaximumWidth(145)
      self.ui.btnScore.setMinimumWidth(93)
      self.ui.btnScore.setMaximumWidth(93)
    self.buttonmap['教学数据'] = self.ui.btnData
    self.buttonmap['预处理'] = self.ui.btnProcess
    self.buttonmap['制作面具'] = self.ui.btnMask
    self.buttonmap['创建血肿'] = self.ui.btnBlood    
    self.buttonmap['三维重建'] = self.ui.btnReconstruction    
    self.buttonmap['创建通道'] = self.ui.btnChannel
    self.buttonmap['制作导板'] = self.ui.btnGuide
    self.buttonmap['打分'] = self.ui.btnScore
    self.ui.btnReconstruction.setCheckable(True)
    self.ui.btnData.connect('toggled(bool)',self.on_step0)
    self.ui.btnProcess.connect('toggled(bool)',self.on_step1)
    self.ui.btnMask.connect('toggled(bool)',self.on_step2)
    self.ui.btnBlood.connect('toggled(bool)',self.on_step3)
    self.ui.btnReconstruction.connect('toggled(bool)',self.on_step7)
    self.ui.btnChannel.connect('toggled(bool)',self.on_step4)
    self.ui.btnGuide.connect('toggled(bool)',self.on_step5)
    self.ui.btnScore.connect('toggled(bool)',self.on_step6)
    self.ui.btnScore.setVisible(False)
    self.ui.lblArrow6.setVisible(False)
    self.ui.btnGuide.setVisible(False)
    self.ui.lblArrow5.setVisible(False)
    self.ui.btnMask.setText("测量标记")
    util.layout_panel("middle_left").setModule("UnitSpineChannel")
    util.layout_panel("middle_left").setModule("UnitCreatePunctureGuide")
    util.layout_panel("middle_left").setModule("UnitCTHeadVolumes")
    util.layout_panel("middle_left").setModule("UnitCTMask")
    util.layout_panel("middle_left").setModule("UnitCTTumor")
    util.layout_panel("middle_left").setModule("UnitPunctureGuide")
    util.layout_panel("middle_left").setModule("UnitScore")
    util.layout_panel("middle_left").setModule("UnitReconstruction")
    util.layout_panel("middle_left").setModule("sunHeadExport")
    
    slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeAddedEvent, self.onNodeAdded)
    slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeRemovedEvent, self.onNodeRemove)
    #util.singleShot(UnitTeaching,self.test1)
    self.TagMaps[util.NewFileLoadedFromMain] = slicer.mrmlScene.AddObserver(util.NewFileLoadedFromMain, self.OnNewFileLoaded)
    self.TagMaps[util.DoctorAssitButttonResetState] = slicer.mrmlScene.AddObserver(util.DoctorAssitButttonResetState, self.OnClearButtonState)
    self.TagMaps[util.ResetVersion] = slicer.mrmlScene.AddObserver(util.ResetVersion, self.OnResetVersion)
    self.TagMaps[G.FinishCreateTumor] = slicer.mrmlScene.AddObserver(G.FinishCreateTumor, self.OnFinishCreateTumor)
    self.TagMaps[G.FinishCreateChannel] = slicer.mrmlScene.AddObserver(G.FinishCreateChannel, self.OnFinishCreateChannel)
    self.TagMaps[G.OnFinishCreateLoadTeachingDICOM] = slicer.mrmlScene.AddObserver(G.OnFinishCreateLoadTeachingDICOM, self.OnOnFinishCreateLoadTeachingDICOM)

    self.ui.btnReconstruction.setVisible(False)
    self.ui.lblArrow3.setVisible(False)
    self.ui.btnProcess.setMinimumWidth(115)
    self.ui.btnProcess.setMaximumWidth(115)
    
  def OnOnFinishCreateLoadTeachingDICOM(self,a,b):
    self.buttonmap['预处理'].setChecked(True)
    util.getModuleWidget("UnitScore").set_project_start()
  
  def checkSegmentNode(self):
    full_head_segment = util.getFirstNodeByName("面具")
    if full_head_segment:
      self.buttonmap['制作导板'].setEnabled(True)
    else:
       if self.buttonmap['制作导板'].isChecked():
         self.buttonmap['制作面具'].setChecked(True)
       self.buttonmap['制作导板'].setEnabled(True)
      
  def checkMainNode(self):
    volume = util.getFirstNodeByClassByAttribute(util.vtkMRMLScalarVolumeNode,"main_node","1")
    if not volume:
      print("checkMainNode 1")
      self.buttonmap['教学数据'].setChecked(False)
      self.buttonmap['教学数据'].setChecked(True)
      util.processEvents()
      for key in self.buttonmap:
        button = self.buttonmap[key]
        if key != "教学数据":
          button.setEnabled(False)
        else:
          button.setEnabled(True)
    else:
      util.singleShot(11,self.set_btns_state)
          
  def set_btns_state(self):
    self.buttonmap['预处理'].setEnabled(True)
    self.buttonmap['制作面具'].setEnabled(True)
    self.buttonmap['创建血肿'].setEnabled(True)
    self.buttonmap['三维重建'].setEnabled(True)
    self.buttonmap['创建通道'].setEnabled(True)
    self.buttonmap['制作导板'].setEnabled(True)
    self.buttonmap['打分'].setEnabled(True)

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def onNodeRemove(self,caller, event, calldata):
    if isinstance(calldata, slicer.vtkMRMLScalarVolumeNode):
      util.singleShot(11,self.checkMainNode)
    elif isinstance(calldata, slicer.vtkMRMLSegmentationNode):
      util.singleShot(11,self.checkSegmentNode)
    #print("onNodeRemove:",calldata.GetName())
  
  @vtk.calldata_type(vtk.VTK_OBJECT)
  def onNodeAdded(self,caller, event, calldata):
    self._onNodeAdded(calldata)
  def _onNodeAdded(self,calldata):
    if isinstance(calldata, slicer.vtkMRMLScalarVolumeNode):
      #如果没有mainnode，当加载node为vtkMRMLScalarVolumeNode就设为mainnode
      volume = util.getFirstNodeByClassByAttribute(util.vtkMRMLScalarVolumeNode,"main_node","1")
      if not volume:
        calldata.SetAttribute("main_node","1")
      util.singleShot(11,self.checkMainNode)
      print("_onNodeAdded checkMainNode")
    elif isinstance(calldata, slicer.vtkMRMLSegmentationNode):
      util.singleShot(11,self.checkSegmentNode)
    
  def OnFinishCreateChannel(self,a,b):
    self.buttonmap["制作面具"].setChecked(True)
  
  def OnFinishCreateTumor(self,a,b):
    self.buttonmap["创建通道"].setChecked(True)
  
  def get_sub_solution_hard(self):
    sub_solution_hard = util.get_cache_from_PAAA("sub_solution_hard",1)
    return int(sub_solution_hard)
  
  def OnResetVersion(self,_a,_b):
    sub_solution_hard = self.get_sub_solution_hard()
    print("whm test OnResetVersion")
    
    auto_enter = int(util.get_cache_from_PAAA("auto_enter",0))
    display_turmo = True
    if sub_solution_hard == 4:
      display_turmo = False
    self.buttonmap["创建血肿"].setVisible(display_turmo)
    #self.buttonmap["三维重建"].setVisible(not display_turmo)

    if auto_enter == "1" or auto_enter == 1:
      self.ui.lblArrow1.hide()
      self.buttonmap["教学数据"].setVisible(False)
    else:      
      self.buttonmap["教学数据"].setVisible(True)
      self.ui.lblArrow1.show()

    display_score = util.get_cache_from_PAAA("display_score","0")
    if display_score == "1" or display_score == 1:
      self.buttonmap["打分"].setVisible(True)
      self.ui.lblArrow6.show()
    else:
      self.buttonmap["打分"].setVisible(False)
      self.ui.lblArrow6.hide()

    self.buttonmap["教学数据"].setChecked(False)
    self.buttonmap["教学数据"].setChecked(True)
    self.checkMainNode()
    
  def solution_init(self):
    print("whm test solution_init")
    util.singleShot(100,lambda:self.buttonmap["教学数据"].setChecked(True))
    util.send_event_str(util.ResetVersion)
  
  def OnClearButtonState(self,a,b):
    self.buttonmap["教学数据"].setChecked(False)
    self.buttonmap["预处理"].setChecked(False)
    self.buttonmap["制作面具"].setChecked(False)
    self.buttonmap["创建血肿"].setChecked(False)
    self.buttonmap["三维重建"].setChecked(False)
    self.buttonmap["创建通道"].setChecked(False)
    self.buttonmap["制作导板"].setChecked(False)
    self.buttonmap["打分"].setChecked(False)
  
  def get_volume(self):
    volume = util.getFirstNodeByClassByAttribute(util.vtkMRMLScalarVolumeNode,"main_node","1")
    return volume
  
  
  @vtk.calldata_type(vtk.VTK_OBJECT)
  def OnNewFileLoaded(self,caller,str_event):
      volume = self.get_volume()
      if not volume:
        volume = util.getFirstNodeByClass(util.vtkMRMLScalarVolumeNode)
        if volume:
          volume.SetAttribute("main_node","1")
          self.checkMainNode()
      util.reinit(volume)
      self.buttonmap['预处理'].setChecked(False)
      self.buttonmap['预处理'].setChecked(True)
  
  def test1(self):
    util.getModuleWidget("JMeasure")._onload(f"D:/save.mrb")
    
  def get_control_panel(self):
    return self.ui.UnitPunctureGuideBottom2
  
  def clear_info(self,unit_in):
    for key in self.buttonmap:
      unit = self.buttonmap[key]
      if unit == unit_in:
        continue
      unit.setChecked(False)
    left_width = 205
    util.layout_panel("middle_left").setMaximumWidth(left_width)
    util.layout_panel("middle_left").setMinimumWidth(left_width)
    
    slicer.util.findChildren(name="CentralWidget")[0].show()
    util.send_event_str(util.DoctorAssitLeftButttonResetState)
    util.layout_panel("middle_left").show()
  
  def OnArchiveLoaded(self,_a,_b):
    for key in self.buttonmap:
      button = self.buttonmap[key]
      button.setChecked(False)
    unit_bottom_index = util.GetGlobalSaveValue("unit_bottom_index")
    print("whm test OnArchiveLoaded", unit_bottom_index)
    if unit_bottom_index == "0":
      util.singleShot(20,lambda:self.buttonmap["教学数据"].setChecked(True))
    elif unit_bottom_index == "1":
      util.singleShot(20,lambda:self.buttonmap["预处理"].setChecked(True))
    elif unit_bottom_index == "2":
      util.singleShot(20,lambda:self.buttonmap["制作面具"].setChecked(True))
    elif unit_bottom_index == "3":
      util.singleShot(20,lambda:self.buttonmap["创建血肿"].setChecked(True))
    elif unit_bottom_index == "4":
      util.singleShot(20,lambda:self.buttonmap["创建通道"].setChecked(True))
    elif unit_bottom_index == "5":
      util.singleShot(20,lambda:self.buttonmap["制作导板"].setChecked(True))
    elif unit_bottom_index == "6":
      util.singleShot(20,lambda:self.buttonmap["打分"].setChecked(True))
    elif unit_bottom_index == "7":
      util.singleShot(20,lambda:self.buttonmap["三维重建"].setChecked(True))
    else:
      util.singleShot(20,lambda:self.buttonmap["教学数据"].setChecked(True))
  
  def left_side_disable_check(self):
    for key in self.buttonmap:
      button = self.buttonmap[key]
      if button.isChecked():
        return
    util.layout_panel("middle_left").hide()
  
  def on_step0(self,boolval):
    if boolval:
      self.old_select_module = '教学数据'
      self.clear_info(self.buttonmap['教学数据'])
      util.layout_panel("middle_left").setModule("UnitSimpleTeacherData")
      #util.SetGlobalSaveValue("unit_bottom_index","0")
    else:
      self.left_side_disable_check()
  
  def on_step1(self,boolval):
    if boolval:
      self.old_select_module = '预处理'
      self.clear_info(self.buttonmap['预处理'])
      util.layout_panel("middle_left").setModule("UnitCTHeadVolumes")
      util.SetGlobalSaveValue("unit_bottom_index","1")
      print("whm test on_step1")
    else:
      self.left_side_disable_check()
    
  def on_step2(self,boolval):
    if boolval:
      self.old_select_module = '制作面具'
      self.clear_info(self.buttonmap['制作面具'])
      util.layout_panel("middle_left").setModule("sunModule")
      util.getModuleWidget("sunModule").enter_widget()
      util.SetGlobalSaveValue("unit_bottom_index","2")
      print("whm test on_step2")
    else:
      self.left_side_disable_check()
       
  def on_step3(self,boolval):
    if boolval:
      self.old_select_module = '创建血肿'
      self.clear_info(self.buttonmap['创建血肿'])
      util.layout_panel("middle_left").setModule("UnitReconstruction")
      util.SetGlobalSaveValue("unit_bottom_index","3")
      print("whm test on_step3")
    else:
      self.left_side_disable_check()
       
  def on_step7(self,boolval):
    if boolval:
      self.old_select_module = '三维重建'
      self.clear_info(self.buttonmap['三维重建'])
      util.layout_panel("middle_left").setModule("UnitReconstruction")
      util.SetGlobalSaveValue("unit_bottom_index","7")
    else:
      self.left_side_disable_check()
    
  def on_step4(self,boolval):
    if boolval:
      self.old_select_module = '创建通道'
      self.clear_info(self.buttonmap['创建通道'])
      util.layout_panel("middle_left").setModule("UnitSpineChannel")
      util.SetGlobalSaveValue("unit_bottom_index","4")
      print("whm test on_ste4p")
    else:
      self.left_side_disable_check()
    
  def on_step5(self,boolval):
    if boolval:
      self.old_select_module = '制作导板'
      self.clear_info(self.buttonmap['制作导板'])
      util.layout_panel("middle_left").setModule("UnitCreatePunctureGuide")
      util.SetGlobalSaveValue("unit_bottom_index","5")
    else:
      self.left_side_disable_check()
    
  def on_step6(self,boolval):
    if boolval:
      self.old_select_module = '打分'
      for key in self.buttonmap:
        unit = self.buttonmap[key]
        if unit == self.buttonmap['打分']:
          continue
        unit.setChecked(False)
      util.layout_panel("middle_left").setMaximumWidth(10000000)
      util.layout_panel("middle_left").setMinimumWidth(400)
      util.layout_panel("middle_left").setModule("UnitScore")
      slicer.util.findChildren(name="CentralWidget")[0].hide()
      util.send_event_str(util.DoctorAssitButttonResetState)
      util.layout_panel("middle_left").show()

  def back_to_solution(self):
    if self.old_select_module not in self.buttonmap:
      return
    self.buttonmap[self.old_select_module].setChecked(True)
    #qt.QTimer.singleShot(10, lambda:self.buttonmap[self.old_select_module].setChecked(True))
    
    