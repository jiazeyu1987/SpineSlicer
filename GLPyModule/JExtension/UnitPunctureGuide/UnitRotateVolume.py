import slicer,qt,vtk,ctk
import slicer.util as util
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from Base.JBaseExtension import JBaseExtensionWidget
import UnitPunctureGuideLib.G_UnitPunctureGuide as G
#
# UnitRotateVolume
#


class UnitRotateVolume(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UnitRotateVolume"  # TODO: make this more human readable by adding spaces
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
# UnitRotateVolumeWidget
#

class UnitRotateVolumeWidget(JBaseExtensionWidget):
  progressvalue = 0
  _cliObserver = None
  volume = None
  rotated_volume = None
  confirm = False
  def setup(self):
    print("UnitRotateVolumeWidget")
    super().setup()    
    
    TransformedCollapsibleButton = util.findChild(util.getModuleWidget("Transforms"), "TransformedCollapsibleButton")
    TransformedCollapsibleButton.setVisible(False)
    TransformNodeSelector = util.findChild(util.getModuleWidget("Transforms"), "TransformNodeSelector")
    TransformNodeSelector.setVisible(False)
    TransformNodeSelectorLabel = util.findChild(util.getModuleWidget("Transforms"), "TransformNodeSelectorLabel")
    TransformNodeSelectorLabel.setVisible(False)
    InfoCollapsibleWidget = util.findChild(util.getModuleWidget("Transforms"), "InfoCollapsibleWidget")
    InfoCollapsibleWidget.setVisible(False)
    DisplayCollapsibleButton = util.findChild(util.getModuleWidget("Transforms"), "DisplayCollapsibleButton")
    DisplayCollapsibleButton.setVisible(False)
    ConvertCollapsibleButton = util.findChild(util.getModuleWidget("Transforms"), "ConvertCollapsibleButton")
    ConvertCollapsibleButton.setVisible(False)
    CopyTransformToolButton = util.findChild(util.getModuleWidget("Transforms"), "CopyTransformToolButton")
    CopyTransformToolButton.setMaximumWidth(0)
    PasteTransformToolButton = util.findChild(util.getModuleWidget("Transforms"), "PasteTransformToolButton")
    PasteTransformToolButton.setMaximumWidth(0)
    SplitPushButton = util.findChild(util.getModuleWidget("Transforms"), "SplitPushButton")
    SplitPushButton.setVisible(False)
    TranslateFirstToolButton = util.findChild(util.getModuleWidget("Transforms"), "TranslateFirstToolButton")
    TranslateFirstToolButton.setMaximumWidth(0)
    IdentityPushButton = util.findChild(util.getModuleWidget("Transforms"), "IdentityPushButton")
    IdentityPushButton.setMinimumWidth(100)
    IdentityPushButton.setMinimumHeight(32)
    InvertPushButton = util.findChild(util.getModuleWidget("Transforms"), "InvertPushButton")
    InvertPushButton.setMinimumWidth(100)
    InvertPushButton.setMinimumHeight(32)
    
    MatrixViewGroupBox = util.findChild(util.getModuleWidget("Transforms"), "MatrixViewGroupBox")
    MatrixViewGroupBox.setTitle("旋转数组")
    
    
    DisplayEditCollapsibleWidget = util.findChild(util.getModuleWidget("Transforms"), "DisplayEditCollapsibleWidget")
    DisplayEditCollapsibleWidget.setText("编辑")
    IdentityPushButton = util.findChild(util.getModuleWidget("Transforms"), "IdentityPushButton")
    IdentityPushButton.setText("重置")
    InvertPushButton = util.findChild(util.getModuleWidget("Transforms"), "InvertPushButton")
    InvertPushButton.setText("反转")
    TranslationSliders = util.findChild(util.getModuleWidget("Transforms"), "TranslationSliders")
    SlidersGroupBox = util.findChild(TranslationSliders, "SlidersGroupBox")
    SlidersGroupBox.setTitle("平移")
    names = ["LRSlider","LRLabel","PALabel","PASlider","ISLabel","ISSlider","MinLabel","MaxLabel"]
    for key in names:
      util.findChild(TranslationSliders, key).setMinimumHeight(32)
    SlidersGroupBox = util.findChild(TranslationSliders, "MinLabel")
    SlidersGroupBox.setText("最小值")
    SlidersGroupBox = util.findChild(TranslationSliders, "MaxLabel")
    SlidersGroupBox.setText("最大值")
    
    RotationSliders = util.findChild(util.getModuleWidget("Transforms"), "RotationSliders")
    for key in names:
      util.findChild(RotationSliders, key).setMinimumHeight(32)
    SlidersGroupBox = util.findChild(RotationSliders, "SlidersGroupBox")
    SlidersGroupBox.setTitle("旋转")
    
    self.ui.translate_panel.setModuleManager(slicer.app.moduleManager())
    self.ui.translate_panel.setModule("Transforms")
    self.ui.translate_panel.show()
    
    self.ui.confirm.connect('clicked()',self.on_confirm)
    self.ui.cancel.connect('clicked()',self.on_cancel)

  def on_cancel(self):
    self.confirm = False
    
    util.getModuleWidget("UnitCTHeadVolumes").ui.btnRotate.setChecked(False)
  
  def on_confirm(self):
    
    self.confirm = True
    util.getModuleWidget("UnitCTHeadVolumes").ui.btnRotate.setChecked(False)
    
    
  def get_container(self):
    return self.ui.UnitRotateVolumeInner

  
  def show_volume(self,volume):
    self.confirm = False
    self.volume = volume
    vname = volume.GetName()+"_rotated"
    if util.getFirstNodeByName(vname):
      rotated_volume =util.getFirstNodeByName(vname)
    else:
      rotated_volume = util.clone(volume)
      rotated_volume.SetName(vname)
    self.rotated_volume = rotated_volume
    rotated_volume.SetAttribute("origin_volume",volume.GetID())
    transform_node = rotated_volume.GetParentTransformNode()
    util.reinit(rotated_volume)
    if not transform_node:
      transform_node = util.AddNewNodeByClass(util.vtkMRMLTransformNode)
      rotated_volume.SetAndObserveTransformNodeID(transform_node.GetID())
      util.getModuleWidget("Transforms").setEditedNode(transform_node)