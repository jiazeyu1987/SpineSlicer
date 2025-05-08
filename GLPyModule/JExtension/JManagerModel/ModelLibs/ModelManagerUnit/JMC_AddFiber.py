import vtk, qt, ctk, slicer
import slicer.util as util
from ModelLibs.ModelManagerUnit.JMC_Template import JMC_Template
class JMC_AddFiber(JMC_Template):
  PresetComboBox = None
  def __init__(self, main, in_present,in_ui) -> None:
    super().__init__(main,in_present,in_ui)
  
  def init(self,node):
    if node is None:
      return
    if self.node:
      self.clear_info("")
      util.RemoveNode(self.node)
    self.node = node
    util.GetDisplayNode(node).SetSliceIntersectionThickness(3)
    self.main.create_btn2D(node,self.ui.btn2D)
    self.main.create_btn3D(node,self.ui.btn3D)
    self.main.create_btnDelete(self,node,self.ui.btnDelete)
    self.main.create_btnColor(node,self.ui.btnColor)
    self.main.create_sliderOpacity(node,self.ui.sliderOpacity)
    self.main.create_sliderOpacity2D(node,self.ui.sliderOpacity2D)

  def on_delete(self,node):
    if node.GetAttribute("model_name"):
      if node.GetAttribute("model_name") in ["直柱","弯柱","导针"]:
        util.showWarningText("该模型不允许在这里删除")
        return
    transform_node = node.GetParentTransformNode()
    
    
    util.RemoveNode(node)
    if transform_node:
      util.RemoveNode(transform_node)
    self.main.show_list()

  def set_title(self,title):
    self.ui.lblName.setText(title)

  def add_default_info(self,type):
    if type == "":
      pass
  
  def clear_info(self,type):
    if type == "":
      pass
