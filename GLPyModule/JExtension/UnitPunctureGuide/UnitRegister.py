import slicer,qt,vtk,ctk
import slicer.util as util
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from Base.JBaseExtension import JBaseExtensionWidget
import UnitPunctureGuideLib.G_UnitPunctureGuide as G
#
# UnitRegister
#


class UnitRegister(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UnitRegister"  # TODO: make this more human readable by adding spaces
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
# UnitRegisterWidget
#

class UnitRegisterWidget(JBaseExtensionWidget):
  progressvalue = 0
  _cliObserver = None
  def setup(self):
    print("UnitRegisterWidget")
    super().setup()    
    self.ui.qLNodeComboBox1.setMRMLScene(slicer.mrmlScene)
    self.ui.qLNodeComboBox1.setProperty("nodeTypes", ["vtkMRMLScalarVolumeNode"])
    self.ui.qLNodeComboBox1.setProperty("noneEnabled", False)
    self.ui.qLNodeComboBox1.setProperty("addEnabled", False)
    self.ui.qLNodeComboBox1.setProperty("renameEnabled", False)
    self.ui.qLNodeComboBox1.setProperty("removeEnabled", False)
    self.ui.qLNodeComboBox1.setEnabled(False)
    
    self.ui.qLNodeComboBox2.setMRMLScene(slicer.mrmlScene)
    self.ui.qLNodeComboBox2.setProperty("nodeTypes", ["vtkMRMLScalarVolumeNode"])
    self.ui.qLNodeComboBox2.setProperty("noneEnabled", True)
    self.ui.qLNodeComboBox2.setProperty("addEnabled", False)
    self.ui.qLNodeComboBox2.setProperty("renameEnabled", False)
    self.ui.qLNodeComboBox2.setProperty("removeEnabled", False)
    self.ui.qLNodeComboBox2.connect('currentNodeChanged(bool)', self.oncurrentNodeChanged)
    self.ui.qLNodeComboBox2.setCurrentNode(None)
    self.TagMaps[G.ChangeMainVolume] = slicer.mrmlScene.AddObserver(G.ChangeMainVolume, self.OnChangeMainVolume)
    self.TagMaps[util.RegisterActionSuccess] = slicer.mrmlScene.AddObserver(util.RegisterActionSuccess, self.OnRegisterActionSuccess)
    self.TagMaps[util.RegisterActionFail] = slicer.mrmlScene.AddObserver(util.RegisterActionFail, self.OnRegisterActionFail)
    
    self.ui.slider.singleStep = 1
    self.ui.slider.minimum = 0
    self.ui.slider.maximum = 100
    self.ui.slider.value = 30
    self.ui.slider.decimals = 0
    self.ui.slider.connect("valueChanged(double)", self.on_opacity_changed)
    
    self.ui.pushButton_2.connect('clicked()',self.on_reverse)
    self.ui.pushButton.connect('clicked()',self.on_register)
    self.ui.pushButton_3.connect('clicked()',self.on_return)
    self.m_AntsWidget = util.getModuleWidget("antsRegistration")
    if self.m_AntsWidget:
      self.m_AntsWidget.setup()
      
  def on_return(self):
    util.getModuleWidget("UnitCTHeadVolumes").ui.btnRegister.setChecked(False)
  
  def OnRegisterActionSuccess(self,caller, event):
    util.send_event_str(util.ProgressValue,100)
    util.processEvents()
    
  def OnRegisterActionFail(self,caller, event):
    util.send_event_str(util.ProgressValue,100)
    util.processEvents()
  def onProcessingStatusUpdate(self, caller, event):
    progress = self.m_AntsWidget.logic._cliNode.GetProgress()
    print(f"Current progress: {progress*100:.2f}%")

  def onProcessingStatusUpdate(self, caller, event):
    msec = 1000
    if caller.GetStatus() != 2:
      print("onProcessingStatusUpdate:")
    if caller.GetStatus() & caller.Cancelled:
      print("Run Registration Cancelled")
      self.m_AntsWidget.logic._cliNode.RemoveObserver(self._cliObserver)
      qt.QTimer.singleShot(msec, lambda:util.send_event_str(util.RegisterActionFail,"1"))
      util.send_event_str(util.ProgressValue,100)
    elif caller.GetStatus() & caller.Completed:
      print("Run Registration Completed1")
      self.m_AntsWidget.logic._cliNode.RemoveObserver(self._cliObserver)
      qt.QTimer.singleShot(msec, lambda:util.send_event_str(util.RegisterActionSuccess,"1"))
      self.set_registed_node_info()
      util.send_event_str(util.ProgressValue,100)
    elif caller.GetStatus() & caller.CompletedWithErrors:
      print("Run Registration Completed2")
      self.m_AntsWidget.logic._cliNode.RemoveObserver(self._cliObserver)
      qt.QTimer.singleShot(msec, lambda:util.send_event_str(util.RegisterActionSuccess,"1"))
      self.set_registed_node_info()
      util.send_event_str(util.ProgressValue,100)
    elif caller.GetStatus() & caller.Completing:
      print("Run Registration Completed3",caller.GetStatus(),caller.Completing)
      self.m_AntsWidget.logic._cliNode.RemoveObserver(self._cliObserver)
      self.m_AntsWidget.logic._cliNode.RemoveObserver(self._cliObserver)
      qt.QTimer.singleShot(msec, lambda:util.send_event_str(util.RegisterActionSuccess,"1"))
      self.set_registed_node_info()
      util.send_event_str(util.ProgressValue,100)
    elif caller.GetStatus() & caller.Cancelling:
      print("Run Registration Completed4",caller.GetStatus(),caller.Cancelling)
      self.m_AntsWidget.logic._cliNode.RemoveObserver(self._cliObserver)
      qt.QTimer.singleShot(msec, lambda:util.send_event_str(util.RegisterActionSuccess,"1"))
      self.set_registed_node_info()
      util.send_event_str(util.ProgressValue,100)
    elif caller.GetStatus() & caller.ErrorsMask:
      print("Run Registration Completed5")
      self.m_AntsWidget.logic._cliNode.RemoveObserver(self._cliObserver)
      qt.QTimer.singleShot(msec, lambda:util.send_event_str(util.RegisterActionFail,"1"))
      util.send_event_str(util.ProgressValue,100)
    else:
      self.progressvalue+=0.03
      progress = self.m_AntsWidget.logic._cliNode.GetProgress()
      if self.progressvalue < progress:
        self.progressvalue= progress
      if self.progressvalue < 100:
        util.send_event_str(util.ProgressValue,int(self.progressvalue))
        util.processEvents()
      pass
  
  def set_registed_node_info(self):
    fixed_node = self.ui.qLNodeComboBox1.currentNode()
    moved_node = self.ui.qLNodeComboBox2.currentNode()
    if not fixed_node:
      return
    if not moved_node:
      return
    fixed_node_old = util.getFirstNodeByClassByAttribute(util.vtkMRMLScalarVolumeNode,"registed_info","fixed_node")
    if fixed_node_old:
      if fixed_node_old == fixed_node:
        fixed_node.SetAttribute("registed_info","fixed_node")
        moved_node.SetAttribute("registed_info","moved_node")
      else:
        fixed_node_old.SetAttribute("registed_info","none")
        moved_olds = util.getNodesByAttribute("registed_info","moved_node")
        for moved_old in moved_olds:
          moved_old.SetAttribute("registed_info","none")
        fixed_node.SetAttribute("registed_info","fixed_node")
        moved_node.SetAttribute("registed_info","moved_node")
    else:
      fixed_node.SetAttribute("registed_info","fixed_node")
      moved_node.SetAttribute("registed_info","moved_node")
    util.reinit()
    
  def OnChangeMainVolume(self,_a,_b):
    volume = util.getFirstNodeByClassByAttribute(util.vtkMRMLScalarVolumeNode,"main_node","1")
    self.ui.qLNodeComboBox1.setCurrentNode(volume)
    self.ui.qLNodeComboBox2.setCurrentNode(None)
  
  def on_register(self):
    import slicer.util as util
    node2 = self.ui.qLNodeComboBox2.currentNode()
    node1 = self.ui.qLNodeComboBox1.currentNode()
    try:
      self.m_AntsWidget.ui.fixedImageNodeComboBox.setCurrentNodeID(node1.GetID())
      print("ants step2")
      self.m_AntsWidget.ui.movingImageNodeComboBox.setCurrentNodeID(node2.GetID())
      print("ants step3")
      self.m_AntsWidget.ui.stagesPresetsComboBox.setCurrentText('Rigid')
      print("ants step4")
      self.m_AntsWidget.ui.outputTransformComboBox.setCurrentNodeID(None)
      print("ants step5")
      self.m_AntsWidget.ui.outputVolumeComboBox.setCurrentNodeID(node2.GetID())
      print("ants step6")
      self.m_AntsWidget.ui.computationPrecisionComboBox.currentText = 'double'
      print("ants step7")
      self.m_AntsWidget.ui.initialTransformTypeComboBox.currentIndex = 3
      print("ants step8")
      self.m_AntsWidget.onRunRegistrationButton()
      util.send_event_str(util.ProgressStart,"正在配准，请稍候")
      util.send_event_str(util.ProgressValue,0)
      #util.SetProgressStep(2)
      print("ants stepb")
      slicer.app.processEvents()
      self.m_AntsWidget.logic._cliNode.RemoveObserver(self._cliObserver)
      self._cliObserver = self.m_AntsWidget.logic._cliNode.AddObserver('ModifiedEvent', self.onProcessingStatusUpdate)
      self.progressvalue = 0
      #util.showWaitText("正在配准，请稍候2分钟左右")
    except Exception as e:
      self.OnRegisterActionFail("","")
  
  def on_reverse(self):
    val = self.ui.slider.value
    self.ui.slider.setValue(100-val)
    
  def on_opacity_changed(self,val):
    value = self.ui.slider.value
    layoutManager = slicer.app.layoutManager()
    for sliceViewName in layoutManager.sliceViewNames():
      compositeNode = layoutManager.sliceWidget(sliceViewName).sliceLogic().GetSliceCompositeNode()
      compositeNode.SetForegroundOpacity(value/100)

  def get_container(self):
    return self.ui.UnitRegister2

  def oncurrentNodeChanged(self,val):
    node2 = self.ui.qLNodeComboBox2.currentNode()
    node1 = self.ui.qLNodeComboBox1.currentNode()
    
    if node1 == None:
      return 
    layoutManager = slicer.app.layoutManager()
    for sliceViewName in layoutManager.sliceViewNames():
      compositeNode = layoutManager.sliceWidget(sliceViewName).sliceLogic().GetSliceCompositeNode()
      if node2 is None:
        compositeNode.SetForegroundVolumeID(None)
      else:
        compositeNode.SetForegroundVolumeID(node2.GetID())
      compositeNode.SetBackgroundVolumeID(node1.GetID())
    self.on_opacity_changed("")
        
    if node1 == node2:
      util.showWarningText("两个要配准的数据不能相同")
      self.ui.qLNodeComboBox2.setCurrentNode(None)
      return