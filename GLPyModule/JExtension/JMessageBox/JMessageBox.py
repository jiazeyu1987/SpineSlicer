import imp
import os
from re import A
from tabnanny import check
from time import sleep
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import slicer.util as util
import SlicerWizard.Utilities as su 
import numpy as np
from Base.JBaseExtension import JBaseExtensionWidget
#
# JMessageBox
#
class JMessageUI(qt.QDialog,ScriptedLoadableModuleWidget):
  def __init__(self, parent=None):
    super(JMessageUI, self).__init__()
    self.setWindowFlag(qt.Qt.FramelessWindowHint)
    self.setAttribute(qt.Qt.WA_TranslucentBackground)  # 使窗口透明
    
    # 设置对话框为全屏
    #self.showFullScreen()
    self.module_path = os.path.dirname(slicer.util.modulePath("JMessageBox"))
    print(self.module_path)
    uiWidget = slicer.util.loadUI(self.module_path + '/Resources/UI/JMessageUI.ui')
    slicer.util.addWidget2(self, uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)
    self.ui.btnOK.connect("clicked()",self.accept)
    self.ui.btnOK2.connect("clicked()",lambda:self.done(2))
    self.ui.btnCancel.connect("clicked()",self.reject)
    self.start_pos = None
  # 设置弹框的信息
  # type 0:询问框3按钮;1:询问框2按钮;2:提示框;3:警示框;4:错误框
  def set_dialog_info(self, title, content, type, btnList, width, height):
    self.ui.container.setMaximumHeight(height)
    self.ui.container.setMinimumHeight(height)
    self.ui.container.setMaximumWidth(width)
    self.ui.container.setMinimumWidth(width)
    self.ui.lblTitle.setText(title)
    self.ui.lblMainMsg.setText(content)
    self.ui.btnOK.setText(btnList[0])
    icon_path = self.module_path + '/Resources/image/icon_question.png'
    self.ui.btnOK2.hide()
    self.ui.btnCancel.hide()
    if type == 0:
      self.ui.btnOK2.setText(btnList[1])
      self.ui.btnCancel.setText(btnList[2])
      self.ui.btnOK2.show()
      self.ui.btnCancel.show()
    elif type == 1:
      self.ui.btnCancel.setText(btnList[1])
      self.ui.btnCancel.show()
    elif type == 2:
      icon_path = self.module_path + '/Resources/image/icon_info.png'
      pass
    elif type == 3:
      icon_path = self.module_path + '/Resources/image/icon_warning.png'
      pass
    elif type == 4:
      icon_path = self.module_path + '/Resources/image/icon_error.png'
      pass
    elif type == 5:
      icon_path = self.module_path + '/Resources/image/icon_wait.png'
      pass
    elif type == 6:
      icon_path = self.module_path + '/Resources/image/icon_success.png'
      pass
    test_str = "border-image: url("+icon_path +");"
    print(test_str)
    self.ui.lblIcon.setStyleSheet(test_str)
  
  def mousePressEvent(self, event):
    """鼠标按下时记录位置"""
    if event.button() == qt.Qt.LeftButton:
      self.start_pos = event.globalPos() - self.frameGeometry.topLeft()
      event.accept()

  def mouseMoveEvent(self, event):
    """根据鼠标移动更新窗口位置"""
    if event.buttons() == qt.Qt.LeftButton and self.start_pos:
      self.move(event.globalPos() - self.start_pos)
      event.accept()

  def mouseReleaseEvent(self, event):
    """释放鼠标时重置位置记录"""
    if event.button() == qt.Qt.LeftButton:
      self.start_pos = None
      event.accept()     
    
class JPopWindow(qt.QDialog,ScriptedLoadableModuleWidget):
  def __init__(self, parent=None):
    super(JPopWindow, self).__init__()
    self.setWindowFlag(qt.Qt.FramelessWindowHint)
    self.setAttribute(qt.Qt.WA_TranslucentBackground)  # 使窗口透明
    
    # 设置对话框为全屏
    #self.showFullScreen()
    self.module_path = os.path.dirname(slicer.util.modulePath("JMessageBox"))
    print(self.module_path)
    uiWidget = slicer.util.loadUI(self.module_path + '/Resources/UI/JPopWindow.ui')
    slicer.util.addWidget2(self, uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)
    self.ui.tabWidget.tabBar().hide()
    self.ui.btnClose.connect("clicked()",self.accept)
    self.start_pos = None

  def set_info(self, title, content, width, height):
    self.ui.tabWidget.setCurrentIndex(3)
    self.ui.lblTitle.setText(title)
    self.set_window_size(width, height)
    self.ui.lblContent.setText(content)

  def set_module(self, title, module_name, width, height):
    self.ui.tabWidget.setCurrentIndex(0)
    self.ui.lblTitle.setText(title)
    self.set_window_size(width, height)
    panel = slicer.qSlicerModulePanel()
    panel.setModuleManager(slicer.app.moduleManager())    
    slicer.util.addWidget2(self.ui.container, panel)
    panel.setContentsMargins(0, 0, 0, 0)
    panel.setStyleSheet("background-color: rgb(0, 255, 0);")
    panel.setModule(module_name)

  def add_ui(self, title, ui, width, height):
    self.ui.tabWidget.setCurrentIndex(2)
    self.ui.lblTitle.setText(title)
    self.set_window_size(width, height)
    slicer.util.addWidget2(self.ui.tab_3, ui)

  def set_window_size(self, width, height):
    self.ui.JPopWindow2.setMaximumHeight(height)
    self.ui.JPopWindow2.setMinimumHeight(height)
    self.ui.JPopWindow2.setMaximumWidth(width)
    self.ui.JPopWindow2.setMinimumWidth(width)    
  
  def mousePressEvent(self, event):
    """鼠标按下时记录位置"""
    if event.button() == qt.Qt.LeftButton:
      self.start_pos = event.globalPos() - self.frameGeometry.topLeft()
      event.accept()

  def mouseMoveEvent(self, event):
    """根据鼠标移动更新窗口位置"""
    if event.buttons() == qt.Qt.LeftButton and self.start_pos:
      self.move(event.globalPos() - self.start_pos)
      event.accept()

  def mouseReleaseEvent(self, event):
    """释放鼠标时重置位置记录"""
    if event.button() == qt.Qt.LeftButton:
      self.start_pos = None
      event.accept()    

class JMessageBox(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "JMessageBox"  # TODO: make this more human readable by adding spaces
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
# JMessageBoxWidget
#

class JMessageBoxWidget(JBaseExtensionWidget):

  def setup(self):
    super().setup()
    #适用于两个选项的询问框
  def show_question(self,title,content, width=600, height=420,btnDes=[util.tr('是'),util.tr('否')]):
    dialog = JMessageUI(slicer.util.mainWindow())
    dialog.set_dialog_info(title, content, 1, btnDes, width, height)
    result = dialog.exec_()
    return result
   

  #适用于三个选项的询问框
  def show_question2(self,title,content,btnDes, width, height):    
    dialog = JMessageUI(slicer.util.mainWindow())
    dialog.set_dialog_info(title, content, 0, btnDes, width, height)
    result = dialog.exec_()
    return result

  #适用于提示信息
  #type 类型 0:提示,1:警示,2:错误,3等待,4,成功
  def show_infomation(self,title,content,dialog_type, width, height, btnDes=[util.tr("好")]): 
    dialog = JMessageUI(slicer.util.mainWindow())
    dialog.set_dialog_info(title, content, dialog_type+2, btnDes, width, height)
    result = dialog.exec_()
    return result

  #适用于有大量的文字要显示
  #title 标题, file_path 文本路径
  def show_pop_window(self, title, file_path, width, height):
    content = "empty content"
    with open(file_path, "r") as file:
       content = file.read()
    dialog = JPopWindow(slicer.util.mainWindow())
    dialog.set_info(title, content, width, height)    
    result = dialog.exec_()
    return result

  #适用于添加模块
  #title 标题, modulename 模块
  def on_popup_modulepanel_dialog(self, title, modulename, width, height):
    dialog = JPopWindow(slicer.util.mainWindow())
    dialog.set_module(title, modulename, width, height)    
    result = dialog.exec_()
    return result

  #适用于添加ui
  #title 标题, ui
  def on_popup_ui_dialog(self, title, ui, width, height):
    dialog = JPopWindow(slicer.util.mainWindow())
    dialog.add_ui(title, ui, width, height)    
    return dialog