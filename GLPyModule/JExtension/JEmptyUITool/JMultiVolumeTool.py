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
#
# JMultiVolumeTool
#

class JMultiVolumeTool(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "JMultiVolumeTool"  # TODO: make this more human readable by adding spaces
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
# JMultiVolumeToolWidget
#

class JMultiVolumeToolWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  slider_tool = None
  point_tool = None
  def __init__(self, parent=None):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)  # needed for parameter node observation
    self.logic = None

  def setup(self):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.setup(self)

    self.logic = JMultiVolumeToolLogic()
    self.logic.setWidget(self)
    slicer.mrmlScene.AddObserver(util.MultiVolumeLoadComplete, self.OnMultiVolumeLoadComplete)
    

  #当MultiVolume加载完成的时候才会初始化部分插件
  def enter(self):
    pass

  def exit(self):
    pass

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def OnMultiVolumeLoadComplete(self,caller,str_event,calldata):
    print("OnMultiVolumeLoadComplete:",calldata.GetID()) 
    #self.init_mutivolume_node_tool(calldata)

  def set_point_tool(self,tool):
    self.point_tool = tool
    tool.btn.connect('toggled(bool)', self.on_multivolume_point)

  def set_slider_tool(self,tool):
    self.slider_tool = tool
    tool.timer.connect('timeout()', self.play_multivolume_slider)
    tool.btn.connect('toggled(bool)', self.on_multivolume_control)
    tool.slider.setEnabled(False)
    tool.btn.setEnabled(False)

  def init_mutivolume_node_tool(self,slider,node):
      self.reinit_multivolume_slider(slider,node)
      util.reinit(background_node=node)


  def get_multivolumenode(self):
    for node in util.getNodes("*").values():
      if node.GetAttribute("main_multi_node") == "1":
        return node
    return None


  def create_slide_layout(self,parent,widget_height):
    widget = qt.QWidget(parent)
    btn_width = 24
    spacing = 8

    btn = qt.QPushButton(widget)
    btn.setGeometry(0,0,btn_width,widget_height)
    btn.setCheckable(True)
    btn_checked_true = self.resourcePath(('Icons/'+"btn_pause.png")).replace('\\','/')
    btn_checked_false = self.resourcePath(('Icons/'+"btn_play.png")).replace('\\','/')
    btn_stylesheet = ""
    btn_stylesheet = btn_stylesheet + "QPushButton{image: url("+btn_checked_false+");background-color:transparent;border: 0px;}"
    btn_stylesheet = btn_stylesheet + "QPushButton:checked{image: url("+btn_checked_true+");background-color:transparent;border: 0px;}"
    btn.setStyleSheet(btn_stylesheet)
    
    multivolume_slider = ctk.ctkSliderWidget(widget)
    multivolume_slider.setObjectName("multivolume_slider")
    multivolume_slider.setProperty("decimals", 0)
    multivolume_slider.setProperty("singleStep", 0.100000000000000)
    multivolume_slider.setProperty("maximum", 100.000000000000000)
    multivolume_slider.setProperty("value", 100.000000000000000)
    multivolume_slider.setGeometry(btn_width+spacing,0,250,widget_height)
    multivolume_slider.connect('valueChanged(double)', self.on_multi_slider_changed)
    
    timer = qt.QTimer()
    timer.setInterval(50)   
    timer.connect('timeout()', lambda slider=multivolume_slider:self.play_multivolume_slider(slider))
    btn.connect('toggled(bool)',lambda toggle,timer1=timer:self.on_multivolume_control(toggle,timer1))
    return widget,btn,multivolume_slider

  
  def on_multivolume_control(self,is_show,timer):
    if self.get_multivolumenode() is None:
      print("self.get_multivolumenode() is None")
      return
    if is_show:
     timer.start()
    else:
      timer.stop()
  def add_multivolume_slider_tool_paras(self,slider,min,max,step,value):
    slider.setProperty("singleStep", step)
    slider.setProperty("minimum", min)
    slider.setProperty("maximum", max)
    slider.setProperty("value", value)
  def on_multi_slider_changed(self, frameId):
    if self.get_multivolumenode() is None:
      return
    newValue = int(frameId)-1
    self.set_multivolume_frame_number(newValue) 
  def set_multivolume_frame_number(self, frameNumber):
    if self.get_multivolumenode() is None:
      return
    mvDisplayNode = self.get_multivolumenode().GetDisplayNode()
    mvDisplayNode.SetFrameComponent(frameNumber)
  def reinit_multivolume_slider(self,slider,node):
    nFrames = node.GetNumberOfFrames()
    self.add_multivolume_slider_tool_paras(slider,1,nFrames,1,1)
  def play_multivolume_slider(self,slider):
    if self.get_multivolumenode() is None:
      return
    currentElement = slider.value
    currentElement += 1
    if currentElement > slider.maximum:
      currentElement = 0
    slider.value = currentElement
    CrosshairNode = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLCrosshairNode')
    CrosshairNode.InvokeEvent(slicer.vtkMRMLCrosshairNode.CursorPositionModifiedEvent)

  def getMaxFrameCount(self):
    if self.get_multivolumenode() is None:
      return -1
    nFrames = self.get_multivolumenode().GetNumberOfFrames()
    return nFrames

  def GetFrameCount(self):
    if self.get_multivolumenode() is None:
      return -1
    mvDisplayNode = self.get_multivolumenode().GetDisplayNode()
    return mvDisplayNode.GetFrameComponent()
  
  def GetCurrentPixelValue(self,x,y,z):
    if self.get_multivolumenode() is None:
      return None
    array4d = util.arrayFromVolume(self.get_multivolumenode()).T
    fc = self.GetFrameCount()
    pixel = array4d[fc][x][y][z]
    return pixel 


  def on_multivolume_point(self,is_show):
      logic = util.getModuleLogic("Markups")
      if is_show:
        util.trigger_view_tool("tool_point")
        node = util.EnsureFirstNodeByNameByClass("MultiVolumePoint",classname="vtkMRMLMarkupsFiducialNode")
        node.CreateDefaultDisplayNodes()
        dn = node.GetDisplayNode()
        dn.SetPointLabelsVisibility(False)
        logic.SetActiveList(node)
        node.AddObserver(slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent,self.on_multivolume_node_define)
        node.AddObserver(slicer.vtkMRMLMarkupsNode.PointPositionUndefinedEvent,self.on_multivolume_node_remove)
        # Use crosshair glyph to allow more accurate point placement
        
        # Hide measurement result while markup up
        slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(slicer.vtkMRMLInteractionNode.Place)
        
      else:
        slicer.app.applicationLogic().GetInteractionNode().SetCurrentInteractionMode(2)

  def on_multivolume_node_remove(self,observer=None, eventid=None):
        self.on_multivolume_node_define(observer=observer,eventid=eventid)
        pointListNode = observer
        numControlPoints = pointListNode.GetNumberOfControlPoints()
        if numControlPoints==0:
          slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutTwoOverTwoView)

  def on_multivolume_node_define(self,observer=None, eventid=None):
    
    tool = self.point_tool
    tool.btn.setChecked(False)
    pointListNode = observer
    numControlPoints = pointListNode.GetNumberOfControlPoints()

    multi_volume_node = util.getFirstNodeByClassByAttribute(util.vtkMRMLScalarVolumeNode,"main_multi_node","1")
    # If volume node is transformed, apply that transform to get volume's RAS coordinates
    transformRasToVolumeRas = vtk.vtkGeneralTransform()
    slicer.vtkMRMLTransformNode.GetTransformBetweenNodes(None, multi_volume_node.GetParentTransformNode(), transformRasToVolumeRas)
    
    nparray = util.arrayFromVolume(multi_volume_node).T
    nparrayshape = util.arrayFromVolume(multi_volume_node).T.shape
    volumeRasToIjk = vtk.vtkMatrix4x4()
    multi_volume_node.GetRASToIJKMatrix(volumeRasToIjk)

    tool = self.slider_tool

    datas = []
    for markupsIndex in range(numControlPoints):
      array1D = []
      point_Ras = [0, 0, 0]
      pointListNode.GetNthControlPointPositionWorld(markupsIndex, point_Ras)
      point_VolumeRas = transformRasToVolumeRas.TransformPoint(point_Ras)
      ras = vtk.vtkVector3d(0,0,0)
      pointListNode.GetNthControlPointPosition(markupsIndex,ras)
      # the world position is the RAS position with any transform matrices applied
      world = [0.0, 0.0, 0.0]
      pointListNode.GetNthControlPointPositionWorld(markupsIndex,world)
      for i in range(nparrayshape[0]):
        point_Ijk = [0, 0, 0, 1]
        volumeRasToIjk.MultiplyPoint(np.append(point_VolumeRas,1.0), point_Ijk)
        point_Ijk = [ int(round(c)) for c in point_Ijk[0:3] ]
        volumeArray = nparray[i]
        try:
          voxelValue = volumeArray[point_Ijk[0], point_Ijk[1], point_Ijk[2]] 
        except IndexError as e:
          voxelValue = 0
        array1D.append(voxelValue)
      datas.append(array1D)
    util.getModuleLogic("JPlot").show_plot_in_multiwidget(datas,title="grey",backgroundcolor=[0,0,0],axisColor=[1,1,1],is_unique_color=False)
    slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutConventionalPlotView)

    

class JMultiVolumeToolLogic(ScriptedLoadableModuleLogic):
  m_Widget = None
  def __init__(self):
    """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
    ScriptedLoadableModuleLogic.__init__(self)

  def setWidget(self,widget):
    self.m_Widget = widget

 
  