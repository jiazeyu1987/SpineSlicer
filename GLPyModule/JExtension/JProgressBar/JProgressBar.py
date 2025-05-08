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
# JProgressBar
#
class JProgressItem(qt.QDialog,ScriptedLoadableModuleWidget):
  max_mum = 0
  min_mum = 0
  def __init__(self, parent=None):
    super(JProgressItem, self).__init__(parent)
    self.setWindowFlag(qt.Qt.FramelessWindowHint)
    self.setAttribute(qt.Qt.WA_TranslucentBackground)  # 使窗口透明
    
    # 设置对话框为全屏
    #self.showFullScreen()
    self.module_path = os.path.dirname(slicer.util.modulePath("JProgressBar"))
    print(self.module_path)
    uiWidget = slicer.util.loadUI(self.module_path + '/Resources/UI/JProgressItem.ui')
    slicer.util.addWidget2(self, uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)
    self.reset_window_size()

  def init_progress_bar(self, txt, min, max):
    self.ui.lblInfo.setText(txt)
    self.ui.bar.setMinimum(min)
    self.ui.bar.setMaximum(max)
    self.max_mum = max
    self.min_mum = min
    self.set_progress_bar_value(min)
    #self.reset_window_size()

  def reset_window_size(self):
    mw = slicer.util.mainWindow()
    #print("LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL:",mw.width,mw.height)
    self.ui.bg.setMinimumWidth(mw.width)
    self.ui.bg.setMaximumWidth(mw.width)
    self.ui.bg.setMinimumHeight(mw.height+100)
    self.ui.bg.setMaximumWidth(mw.height+100)

  def set_progress_bar_value(self, value):
    if value > self.max_mum:
      value = self.max_mum
    if value >= self.max_mum:
      self.hide()

    self.ui.bar.setValue(value)
    self.ui.label_3.setText(f"{value}%")
    slicer.app.processEvents()

  def get_progress_bar_value(self):
    return self.ui.bar.value()

  def add_prgress_bar_value(self, add_num):
    value = self.get_progress_bar_value()
    last_value = last_value + value
    if last_value >= max_mum:
      last_value = max_mum
    self.set_progress_bar_value(last_value)
  
class JProgressBar(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "JProgressBar"  # TODO: make this more human readable by adding spaces
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
# JProgressBarWidget
#

class JProgressBarWidget(JBaseExtensionWidget):
  bar_item = None
  def setup(self):
    super().setup()
    self.bar_item = JProgressItem(slicer.util.mainWindow())
    self.bar_item.show()
    self.bar_item.hide()
    
  def InitProgressBar(self, txt, min, max):
    print("InitProgressBar")
    self.bar_item.show()
    
    self.bar_item.move(0,0)
    #self.bar_item.showFullScreen()
    inter = 60
    self.bar_item.setFixedSize(slicer.util.mainWindow().width, slicer.util.mainWindow().height+inter)
    self.bar_item.ui.bg.setFixedSize(slicer.util.mainWindow().width, slicer.util.mainWindow().height+inter)
    self.bar_item.init_progress_bar(txt, min, max)

  def ShowProgressBar(self, txt, min, max):
    self.InitProgressBar(txt, 0, 100)

  def SetProgress(self, val):
    if self.bar_item.isHidden():
      print("isHidden")
      return
    self.bar_item.set_progress_bar_value(val)
    if val == 100:
      self.HideProgressBar()

  def UpdateProgressStep(self, step):
    if self.bar_item.isHidden():
      return
    if step < 1:
      step = 1
    self.bar_item.add_prgress_bar_value(step)
  
  def HideProgressBar(self):
    self.bar_item.hide()