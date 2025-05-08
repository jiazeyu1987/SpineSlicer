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
from JSegmentEditorToolLibs.JSegmentPanel import JSegmentPanel
#
# JTestSegmentEditorTool
#

class JTestSegmentEditorTool(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "JTestSegmentEditorTool"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["test"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["jia ze yu"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """

"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """

"""



#
# JTestSegmentEditorTool
#

class JTestSegmentEditorToolWidget(JBaseExtensionWidget):
  def setup(self):
    super().setup()
    self.ui.pushButton.connect('clicked()',self.onCustomReload)
    self.ui.ActiveVolumeNodeSelector.setMRMLScene(slicer.mrmlScene)
    self.ui.ActiveSegmentNodeSelector.setMRMLScene(slicer.mrmlScene)
    self.ui.btn_start.connect('clicked()',self.on_start)
    
  
  
          
  def onCustomReload(self):
    import sys   
    util.getModuleWidget("JSegmentEditorTool").onReloadAll()
    util.singleShot(0,lambda:self.onReload())
  def enter(self):
    pass
  
  def on_start(self):
    if self.ui.ActiveVolumeNodeSelector.currentNode() is None:
      print("请选择一个Volume")
      return
    if self.ui.ActiveSegmentNodeSelector.currentNode() is None:
      print("请选择一个Segment")
      return
    print("on start test segment panel",self.ui.ActiveVolumeNodeSelector.currentNode().GetID(),self.ui.ActiveSegmentNodeSelector.currentNode().GetID())
    master_node=self.ui.ActiveVolumeNodeSelector.currentNode()
    segment_node=self.ui.ActiveSegmentNodeSelector.currentNode()
    title = "Test123"
    toollist = ["Paint","Draw","Threshold","Scissors","LevelTracing","FillBetweenSlice"]
    button_txt = "功能1"
    button_callback = lambda:print("123")
    cancel_callback = lambda:print("234")
    panel = util.getModuleWidget("JSegmentEditorTool").create_tool_panel(master_node,segment_node,title,toollist,button_callback,cancel_callback,button_txt)
    util.addWidget2(self.ui.widget,panel.uiWidget)
    
  