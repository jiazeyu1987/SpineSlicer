import slicer,os,qt
from slicer.ScriptedLoadableModule import *
import slicer.util as util
class ParcellationItem:
  def __init__(self,uiwidget,ui,main,item,color,tag,name, file_path):
    self.uiwidget = uiwidget
    self.ui = ui
    self.main = main
    self.item = item
    self.color = color
    self.tag = tag
    self.name = name

    # renderer = QSvgRenderer("bin/images/water.svg")
    # pixmap = qt.QPixmap(renderer.defaultSize())
    # pixmap.fill(qt.Qt.transparent)
    # painter = qt.QPainter(pixmap)
    # renderer.render(painter)
    # painter.setCompositionMode(qt.QPainter.CompositionMode_SourceIn)
    # painter.fillRect(pixmap.rect(), self.color)
    # painter.end()
    # self.ui.pushButton.setIcon(QIcon(pixmap))
    # self.ui.pushButton.setIconSize(QSize(24, 24))
    save_path = "bin/tmp/svg.png"
    util.getModuleWidget("SVGT").ChangeColor("bin/images/water.svg",self.ui.pushButton,qt.QColor(color[0]*255,color[1]*255,color[2]*255))
    #self.ui.pushButton.setIcon(qt.QIcon(save_path))
    self.ui.pushButton.setIconSize(qt.QSize(24, 24))
    self.ui.pushButton.setStyleSheet("background: transparent;")
    
    self.ui.checkBox.connect("toggled(bool)",self.on_changed)
    self.ui.checkBox.setText(tag)
    
  def on_changed(self,boolval):
    node = util.getFirstNodeByName("脑功能区")
    if not node:
      return
    sid = node.GetSegmentation().GetSegmentIdBySegmentName(self.name)
    if not sid:
      return
    util.GetDisplayNode(node).SetSegmentVisibility(sid,True)
    if boolval:
      util.GetDisplayNode(node).SetSegmentOpacity(sid,1)
      util.GetDisplayNode(node).SetSegmentVisibility3D(sid,True)
    else:
      util.GetDisplayNode(node).SetSegmentOpacity(sid,0.01)
      util.GetDisplayNode(node).SetSegmentVisibility3D(sid,False)
    
  def update_from_mrml(self):
    node = util.getFirstNodeByName("脑功能区")
    if not node:
      return
    sid = node.GetSegmentation().GetSegmentIdBySegmentName(self.name)
    util.GetDisplayNode(node).SetSegmentVisibility(True)
    if self.ui.checkBox.isChecked():
       util.GetDisplayNode(node).SetSegmentOpacity(sid,1)
       util.GetDisplayNode(node).SetSegmentVisibility3D(sid,True)
    else:
      util.GetDisplayNode(node).SetSegmentOpacity(sid,0.01)
      util.GetDisplayNode(node).SetSegmentVisibility3D(sid,False)
    
    
class MonaiItem:
  def __init__(self,uiwidget,ui,main,item,color,tag,name, file_path):
    self.uiwidget = uiwidget
    self.ui = ui
    self.main = main
    self.item = item
    self.color = color
    self.tag = tag
    self.name = name

    # renderer = QSvgRenderer("bin/images/water.svg")
    # pixmap = qt.QPixmap(renderer.defaultSize())
    # pixmap.fill(qt.Qt.transparent)
    # painter = qt.QPainter(pixmap)
    # renderer.render(painter)
    # painter.setCompositionMode(qt.QPainter.CompositionMode_SourceIn)
    # painter.fillRect(pixmap.rect(), self.color)
    # painter.end()
    # self.ui.pushButton.setIcon(QIcon(pixmap))
    # self.ui.pushButton.setIconSize(QSize(24, 24))
    save_path = "bin/tmp/svg.png"
    util.getModuleWidget("SVGT").ChangeColor("bin/images/water.svg",self.ui.pushButton,qt.QColor(color[0]*255,color[1]*255,color[2]*255))
    #self.ui.pushButton.setIcon(qt.QIcon(save_path))
    self.ui.pushButton.setIconSize(qt.QSize(24, 24))
    self.ui.pushButton.setStyleSheet("background: transparent;")
    
    self.ui.checkBox.connect("toggled(bool)",self.on_changed)
    self.ui.checkBox.setText(tag)
    if tag == "血肿":
      self.ui.checkBox.setChecked(True)
    
  def on_changed(self,boolval):
    node = util.getFirstNodeByName("CTHeadSegmentNode")
    if not node:
      return
    sid = node.GetSegmentation().GetSegmentIdBySegmentName(self.name)
    if not sid:
      return
    util.GetDisplayNode(node).SetSegmentVisibility(sid,True)
    if boolval:
      util.GetDisplayNode(node).SetSegmentOpacity(sid,1)
    else:
      util.GetDisplayNode(node).SetSegmentOpacity(sid,0.01)
    
  def update_from_mrml(self):
    node = util.getFirstNodeByName("CTHeadSegmentNode")
    if not node:
      return
    sid = node.GetSegmentation().GetSegmentIdBySegmentName(self.name)
    util.GetDisplayNode(node).SetSegmentVisibility(sid,self.ui.checkBox.isChecked())
