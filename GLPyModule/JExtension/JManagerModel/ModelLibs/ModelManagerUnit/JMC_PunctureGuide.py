import vtk, qt, ctk, slicer
import slicer.util as util
from ModelLibs.ModelManagerUnit.JMC_Template import JMC_Template
class JMC_PunctureGuide(JMC_Template):
  PresetComboBox = None
  def __init__(self, main, widget,in_ui) -> None:
    super().__init__(main,widget,in_ui)
  
  def init(self,node):
    if self.node:
      self.clear_info("")
      util.RemoveNode(self.node)
    self.node = node
    if node.GetDisplayNode() is None:
      node.CreateDefaultDisplayNodes()
    node.GetDisplayNode().SetVisibility2D(True)
    node.GetDisplayNode().SetSliceIntersectionThickness(3)
    self.main.create_btnVisible(node,self.ui.btnVisible)
    self.main.create_btnColor(node,self.ui.btnColor)
    self.main.create_btnModify(node,self.ui.btnModify)
    self.main.create_btnDelete(self,node,self.ui.btnDelete)
    self.main.create_sliderOpacity(node,self.ui.sliderOpacity)
    self.ui.btnVisible.setChecked(True)
    self.add_default_info("")

  def on_delete(self,node):
    res = util.messageBox("确定删除吗",windowTitle=util.tr("提示"))
    if res == 0:
      return
    slicer.mrmlScene.InvokeEvent(util.JManagerModel_Delete,node)

  def set_title(self,title,img):
    self.ui.lblName.setText(title)
    image = self.ui.lblImage
    pixelmap = qt.QPixmap.fromImage(img)
    if img.width() > img.height():
        gap = (img.width()-img.height())/2
        rect = qt.QRect(gap,0,img.height(),img.height())
        pixelmap_cropped = pixelmap.copy(rect)
        pixelmap_scaled = pixelmap_cropped.scaled(80,80, 0,1)
        image.setPixmap(pixelmap_scaled)
    else:
      gap = (img.height()-img.width())/2
      rect = qt.QRect(0,gap,img.width(),img.width())
      pixelmap_cropped = pixelmap.copy(rect)
      pixelmap_scaled = pixelmap_cropped.scaled(80,80, 0,1)
      image.setPixmap(pixelmap_scaled)

  def add_default_info(self,type):
    if type == "":
      pass
  
  def clear_info(self,type):
    if type == "":
      pass
