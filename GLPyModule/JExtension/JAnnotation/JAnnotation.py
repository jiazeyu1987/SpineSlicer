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
# JAnnotation
#

class JAnnotationSettingsPanel(ctk.ctkSettingsPanel):
    def __init__(self, *args, **kwargs):
        ctk.ctkSettingsPanel.__init__(self, *args, **kwargs)
        self.ui = _ui_JAnnotationSettingsPanel(self)

class _ui_JAnnotationSettingsPanel:
    def __init__(self, parent):
        util.getModuleWidget("JAnnotation").init_setting_panel_ui(parent)


class JAnnotation(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "JAnnotation"  # TODO: make this more human readable by adding spaces
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
# JAnnotationWidget
#

class JAnnotationWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  panel_settings = {}
  intesection_point = [0,0,0]
  curr_point = [0, 0, 0]
  show_corner = False
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

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    self.logic = JAnnotationLogic()
    self.logic.setWidget(self)

    
    
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/JAnnotation.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)
    
   
    uiWidget.setMRMLScene(slicer.mrmlScene)
    
    
    self.init_ui()
  


  def enter(self):
    self.addEvent(True)

  def exit(self):
    self.addEvent(False)


  def init_setting_panel_ui(self,parent):
    template1 = slicer.util.loadUI(self.resourcePath("UI/JAnnotationSettingPanel.ui"))
    panelui = slicer.util.childWidgetVariables(template1)

    import math
    vBoxLayout = qt.QVBoxLayout(parent)
    vBoxLayout.addWidget(panelui.JAnnotationSettingPanel)

    parent.registerProperty(
              "JAnnotation/ShowAnnotation",
              ctk.ctkBooleanMapper(panelui.cb_show_anno, "checked", str(qt.SIGNAL("toggled(bool)"))),
              "valueAsInt",
              str(qt.SIGNAL("valueAsIntChanged(int)")),
          )

    parent.registerProperty(
              "JAnnotation/ShowWindowStyle",
              ctk.ctkBooleanMapper(panelui.cb_window_style, "checked", str(qt.SIGNAL("toggled(bool)"))),
              "valueAsInt",
              str(qt.SIGNAL("valueAsIntChanged(int)")),
          )

    parent.registerProperty(
              "JAnnotation/ShowLayer",
              ctk.ctkBooleanMapper(panelui.cb_layer, "checked", str(qt.SIGNAL("toggled(bool)"))),
              "valueAsInt",
              str(qt.SIGNAL("valueAsIntChanged(int)")),
          )

    parent.registerProperty(
              "JAnnotation/ShowGrey",
              ctk.ctkBooleanMapper(panelui.cb_grey, "checked", str(qt.SIGNAL("toggled(bool)"))),
              "valueAsInt",
              str(qt.SIGNAL("valueAsIntChanged(int)")),
          )
    parent.registerProperty("JAnnotation/ShowPos", panelui.lineEdit, "text", str(qt.SIGNAL("textChanged(QString)")))
    self.panel_settings["cb_show_anno"] = panelui.cb_show_anno
    self.panel_settings["cb_layer"] = panelui.cb_layer
    self.panel_settings["cb_grey"] = panelui.cb_grey
    self.panel_settings["ShowPos"] = panelui.lineEdit
    self.panel_settings["cb_window_style"] = panelui.cb_window_style
    
    

  def addEvent(self,bool_val):
    if bool_val:
      pass
    else:
      pass
  
  def show_or_hide_info(self, is_show):
    self.show_corner = is_show
    if not is_show:
      arlist = ["Green","Red","Yellow"]
      layoutManager = slicer.app.layoutManager()
      for sliceViewName in arlist:
        renderer = layoutManager.sliceWidget(sliceViewName).sliceView().renderWindow().GetRenderers().GetFirstRenderer()
        renderWindow = renderer.GetRenderWindow()
        cornerAnnotationDisplay = layoutManager.sliceWidget(sliceViewName).overlayCornerAnnotation()
        cornerAnnotationDisplay.ClearAllTexts()
        renderWindow.Render()

  def init_ui(self):
    print("init jannotation ")
    util.singleShot(100,self.show)
    
    if util.getjson2("annotation","intersection_point",default_value=0)!=0:
      #焦点坐标移动
      colors = ["Red","Green","Yellow"]
      for color in colors:
        sliceNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNode%s" % color)
        sliceNode.AddObserver(vtk.vtkCommand.ModifiedEvent, self.UpdateSliceAnnotation)
    
    if util.getjson2("annotation","mouse_cursor_value",default_value=0)!=0:
      #鼠标移动
      CrosshairNode = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLCrosshairNode')
      if CrosshairNode:
          self.CrosshairNodeObserverTag = CrosshairNode.AddObserver(slicer.vtkMRMLCrosshairNode.CursorPositionModifiedEvent, self.processEvent)
    
  def processEvent(self, observee, event):
    if not self.show_corner:
      return
    pixel_value = self.get_pixel_value_by_mouse_position()
    self.get_interpos_by_mouse_position()
    self._UpdateSliceAnnotationByPixelValue(pixel_value)

  def get_pixel_value_by_mouse_position(self):
    # TODO: use a timer to delay calculation and compress events
    txt = ""
    insideView = False
    ras = [0.0, 0.0, 0.0]
    xyz = [0.0, 0.0, 0.0]
    sliceNode = None
    CrosshairNode=slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLCrosshairNode')
    insideView = CrosshairNode.GetCursorPositionRAS(ras)
    sliceNode = CrosshairNode.GetCursorPositionXYZ(xyz)
    sliceLogic = None
    if sliceNode:
        appLogic = slicer.app.applicationLogic()
        if appLogic:
            sliceLogic = appLogic.GetSliceLogic(sliceNode)

    

    if not insideView or not sliceNode or not sliceLogic:
        # reset all the readouts
        return ""
    hasVolume = False
    layerLogicCalls = (('L', sliceLogic.GetLabelLayer),
                        ('F', sliceLogic.GetForegroundLayer),
                        ('B', sliceLogic.GetBackgroundLayer))
    pixel_value = ""
    for layer, logicCall in layerLogicCalls:
        layerLogic = logicCall()
        volumeNode = layerLogic.GetVolumeNode()
        ijk = [0, 0, 0]
        if volumeNode:
            hasVolume = True
            xyToIJK = layerLogic.GetXYToIJKTransform()
            ijkFloat = xyToIJK.TransformDoublePoint(xyz)
            ijk = [self._roundInt(value) for value in ijkFloat]
            pixel_value = self.generateIJKPixelValueDescription(ijk, layerLogic)

    txt = txt + pixel_value
    return txt

  def _roundInt(self,value):
      try:
          return int(round(value))
      except ValueError:
          return 0

  def generateIJKPixelValueDescription(self, ijk, slicerLayerLogic):
        volumeNode = slicerLayerLogic.GetVolumeNode()
        return self.getPixelString(volumeNode, ijk) if volumeNode else ""

  def getPixelString(self, volumeNode, ijk):
      """Given a volume node, create a human readable
      string describing the contents"""
      # TODO: the volume nodes should have a way to generate
      # these strings in a generic way
      if not volumeNode:
          return "No volume"
      imageData = volumeNode.GetImageData()
      if not imageData:
          return "No Image"
      dims = imageData.GetDimensions()
      for ele in range(3):
          if ijk[ele] < 0 or ijk[ele] >= dims[ele]:
              return "Out of Frame"
      pixel = ""
      if volumeNode.IsA("vtkMRMLLabelMapVolumeNode"):
          labelIndex = int(imageData.GetScalarComponentAsDouble(ijk[0], ijk[1], ijk[2], 0))
          labelValue = "Unknown"
          displayNode = volumeNode.GetDisplayNode()
          if displayNode:
              colorNode = displayNode.GetColorNode()
              if colorNode:
                  labelValue = colorNode.GetColorName(labelIndex)
          return "%s (%d)" % (labelValue, labelIndex)

      if volumeNode.IsA("vtkMRMLDiffusionTensorVolumeNode"):
          point_idx = imageData.FindPoint(ijk[0], ijk[1], ijk[2])
          if point_idx == -1:
              return "Out of bounds"

          if not imageData.GetPointData():
              return "No Point Data"

          tensors = imageData.GetPointData().GetTensors()
          if not tensors:
              return "No Tensor Data"

          tensor = imageData.GetPointData().GetTensors().GetTuple9(point_idx)
          scalarVolumeDisplayNode = volumeNode.GetScalarVolumeDisplayNode()

          if scalarVolumeDisplayNode:
              operation = scalarVolumeDisplayNode.GetScalarInvariant()
          else:
              operation = None

          value = self.calculateTensorScalars(tensor, operation=operation)
          if value is not None:
              valueString = ("%f" % value).rstrip('0').rstrip('.')
              return f"{scalarVolumeDisplayNode.GetScalarInvariantAsString()} {valueString}"
          else:
              return scalarVolumeDisplayNode.GetScalarInvariantAsString()

      # default - non label scalar volume
      numberOfComponents = imageData.GetNumberOfScalarComponents()
      if numberOfComponents > 3:
          fc = util.getModuleWidget("JMultiVolumeTool").GetFrameCount()
          pixel = util.getModuleWidget("JMultiVolumeTool").GetCurrentPixelValue(ijk[0], ijk[1], ijk[2])
          return "%d of %d" % (fc,pixel)
      for c in range(numberOfComponents):
          component = imageData.GetScalarComponentAsDouble(ijk[0], ijk[1], ijk[2], c)
          if component.is_integer():
              component = int(component)
          # format string according to suggestion here:
          # https://stackoverflow.com/questions/2440692/formatting-floats-in-python-without-superfluous-zeros
          # also set the default field width for each coordinate
          componentString = ("%4f" % component).rstrip('0').rstrip('.')
          pixel += ("%s, " % componentString)
      return pixel[:-2]

  def show(self):
    self.settingsPanel = JAnnotationSettingsPanel()
    #slicer.app.settingsDialog().addPanel("角标", self.settingsPanel)

  def UpdateGreyValue(self,unused1=None, unused2=None):
    if self.panel_settings["cb_show_anno"].isChecked():
      arlist = ["Green","Red","Yellow"]
      layoutManager = slicer.app.layoutManager()
      for sliceViewName in arlist:
        renderer = layoutManager.sliceWidget(sliceViewName).sliceView().renderWindow().GetRenderers().GetFirstRenderer()
        renderWindow = renderer.GetRenderWindow()
        cornerAnnotationDisplay = layoutManager.sliceWidget(sliceViewName).overlayCornerAnnotation()
        cornerAnnotationDisplay.ClearAllTexts()
        renderWindow.Render()
    else:
      return
    ras=[0,0,0]
    crosshairNode=slicer.util.getNode("Crosshair")
    crosshairNode.GetCursorPositionRAS(ras)
    layoutManager = slicer.app.layoutManager()
    red = layoutManager.sliceWidget("Red")
    redLogic = red.sliceLogic()
    compositeNode = redLogic.GetSliceCompositeNode()
    id = compositeNode.GetBackgroundVolumeID()
    if id is None:
      return
    volumeNode = util.GetNodeByID(id)
    volumeRasToIjk = vtk.vtkMatrix4x4()
    volumeNode.GetRASToIJKMatrix(volumeRasToIjk)
    point_Ijk = [0, 0, 0, 1]
    volumeRasToIjk.MultiplyPoint(np.append(ras,1.0), point_Ijk)
    point_Ijk = [ int(round(c)) for c in point_Ijk[0:3] ]
    array1 = util.arrayFromVolume(volumeNode).T
    grey_value = array1[point_Ijk[0],point_Ijk[1],point_Ijk[2]]
    arlist = ["Green","Red","Yellow"]
    index=0
    for sliceViewName in arlist:
      renderer = layoutManager.sliceWidget(sliceViewName).sliceView().renderWindow().GetRenderers().GetFirstRenderer()
      renderWindow = renderer.GetRenderWindow()
      cornerAnnotationDisplay = layoutManager.sliceWidget(sliceViewName).overlayCornerAnnotation()
      cornerAnnotationDisplay.SetText(3,"V:%d"%(grey_value))
      renderWindow.Render()
      index+=1
      if index > 2:
        break
  
  #get domain axis
  def GetValueOrder(self):
    order = ["Red", "Green", "Yellow"]
    layoutManager = slicer.app.layoutManager()
    red = layoutManager.sliceWidget("Red")
    redLogic = red.sliceLogic()
    compositeNode = redLogic.GetSliceCompositeNode()
    id = compositeNode.GetBackgroundVolumeID()
    if id is None:
      return order
    volumeNode = util.GetNodeByID(id)
    volumeIjk2Ras = vtk.vtkMatrix4x4()
    volumeNode.GetIJKToRASMatrix(volumeIjk2Ras)
    value0 = abs(volumeIjk2Ras.GetElement(0, 0))
    value1 = abs(volumeIjk2Ras.GetElement(0, 1))
    value2 = abs(volumeIjk2Ras.GetElement(0, 2))
    value = [value0, value1, value2]
    result = [0, 0, 0]
    tmp_arr = ["Yellow", "Green", "Red"]
    for i in range(0,3):
      for j in range(1,3):
        tmp_value = abs(volumeIjk2Ras.GetElement(j, i))
        if tmp_value > value[i]:
          value[i] = tmp_value
          result[i] = j
    for i in range(3):
      order[i] = tmp_arr[result[i]]
    return order

  def get_interpos_by_mouse_position(self):
    txt = ""
    insideView = False
    xyz = [0.0, 0.0, 0.0]
    ras = [0.0, 0.0, 0.0]
    CrosshairNode=slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLCrosshairNode')
    insideView = CrosshairNode.GetCursorPositionRAS(ras)
    sliceNode = CrosshairNode.GetCursorPositionXYZ(xyz)
    sliceLogic = None
    if sliceNode:
      appLogic = slicer.app.applicationLogic()
      if appLogic:
        sliceLogic = appLogic.GetSliceLogic(sliceNode)

    

    if not insideView or not sliceNode or not sliceLogic:
      self.curr_point = [0, 0, 0]
      return
    # layoutManager = slicer.app.layoutManager()
    # red = layoutManager.sliceWidget("Red")
    # redLogic = red.sliceLogic()
    compositeNode = sliceLogic.GetSliceCompositeNode()
    id = compositeNode.GetBackgroundVolumeID()
    if id is None:
      return
    volumeNode = util.GetNodeByID(id)
    imageData = volumeNode.GetImageData()
    if not imageData:
      return
    dims = imageData.GetDimensions()
    xyToIJK = sliceLogic.GetBackgroundLayer().GetXYToIJKTransform()
    ijkFloat = xyToIJK.TransformDoublePoint(xyz)
    ijk = [self._roundInt(value) for value in ijkFloat]
    for i in range(3):
      if ijk[i] < 0:
        ijk[i] = 0
      if ijk[i] > dims[i]:
        ijk[i] = dims[i]
    self.curr_point = ijk
    pass

  def clear_selected_layer_data(self,lower,higher):
    layoutManager = slicer.app.layoutManager()
    red = layoutManager.sliceWidget("Red")
    sliceLogic = red.sliceLogic()
    compositeNode = sliceLogic.GetSliceCompositeNode()
    id = compositeNode.GetBackgroundVolumeID()
    if id is None:
      return
    volumeNode = util.GetNodeByID(id)
    imageData = volumeNode.GetImageData()
    if not imageData:
      return
    dims = imageData.GetDimensions()
    if lower < 0:
      lower = 0
    if lower >= higher:
      return
    if higher > dims[2]:
      higher = dims[2]
    print(dims)
    for z in range(lower, higher):
      for y in range(dims[0]):
        for x in range(dims[1]):
          imageData.SetScalarComponentFromDouble(x, y, z, 0, 0.0)
    imageData.Modified()
    pass

  def UpdateSliceAnnotation(self,unused1=None, unused2=None):
    # position = util.getPlaneIntersectionPoint()
    # crosshairNode = slicer.util.getNode("Crosshair")
    # crosshairNode.SetCrosshairRAS(position)
    xyz=[0,0,0]
    crosshairNode=slicer.util.getNode("Crosshair")
    sliceNode = crosshairNode.GetCursorPositionXYZ(xyz)
    
    layoutManager = slicer.app.layoutManager()
    colors = self.GetValueOrder()
    result = [0,0,0]
    for idx,color in enumerate(colors):
      red = layoutManager.sliceWidget(color)
      sliceLogic = red.sliceLogic()
      xyToIJK = sliceLogic.GetBackgroundLayer().GetXYToIJKTransform()
      ijkFloat = xyToIJK.TransformDoublePoint(xyz)
      ijk = [self._roundInt(value) for value in ijkFloat]
      result[idx] = ijk[idx]
    self._UpdateSliceAnnotationByIntersection(result)
    return

  def _UpdateSliceAnnotationByPixelValue(self,pixel_value):
    layoutManager = slicer.app.layoutManager()
    arlist = ["Green","Red","Yellow"]
    maps = {}
    maps["Red"] = "Axial"
    maps["Yellow"] = "Sagittal"
    maps["Green"] = "Coronal"
    for sliceViewName in arlist:
      renderer = layoutManager.sliceWidget(sliceViewName).sliceView().renderWindow().GetRenderers().GetFirstRenderer()
      renderWindow = renderer.GetRenderWindow()
      cornerAnnotationDisplay = layoutManager.sliceWidget(sliceViewName).overlayCornerAnnotation()
      cornerAnnotationDisplay.ClearAllTexts()
      txt1 = ""
      if True:
        txt1 = maps[sliceViewName] + "\n"
        txt2 = "%s"%(pixel_value) + "\n"
        txt3 = "(%d,%d,%d)"%(self.intesection_point[0],self.intesection_point[1],self.intesection_point[2])
        txt4 = "(%d,%d,%d)"%(self.curr_point[0],self.curr_point[1],self.curr_point[2])
        pos1 = util.getjson2("annotation","ACS",default_value=0)
        if pos1!=0:
          cornerAnnotationDisplay.SetText(2,txt1)
          cornerAnnotationDisplay.SetText(0,txt2)
        pos2 = util.getjson2("annotation","mouse_cursor_value",default_value=0)
        # if pos2!=0:
        #   cornerAnnotationDisplay.SetText(pos2-1,txt4)
        pos3 = util.getjson2("annotation","intersection_point",default_value=0)
        if pos3!=0:
          cornerAnnotationDisplay.SetText(pos3-1,txt3)
      renderWindow.Render()
    

  def _UpdateSliceAnnotationByIntersection(self,intesection):
    self.intesection_point = intesection
    self.processEvent("","")

  def old(self):
    aa=slicer.mrmlScene.GetNodesByClass('vtkMRMLCrosshairNode').GetItemAsObject(0)
    layoutManager = slicer.app.layoutManager()
    red = layoutManager.sliceWidget("Red")
    redLogic = red.sliceLogic()
    compositeNode = redLogic.GetSliceCompositeNode()
    id = compositeNode.GetBackgroundVolumeID()
    if id is None:
      return
    volumeNode = util.GetNodeByID(id)
    array1 = util.arrayFromVolume(volumeNode).T
    grey_value = 0
    shape = array1.shape
    point_Ijk = [ int(round(c)) for c in slicer.mrmlScene.GetNodesByClass('vtkMRMLCrosshairNode').GetItemAsObject(0).GetCrosshairRAS() ]
    if point_Ijk[0]>0 and point_Ijk[0] < shape[0] and point_Ijk[1]>0 and point_Ijk[1] < shape[1] and  point_Ijk[2]>0 and point_Ijk[2] < shape[2]:
      grey_value = array1[point_Ijk[0],point_Ijk[1],point_Ijk[2]]
    index = 0
    arlist = ["Green","Red","Yellow"]
    maps = {}
    maps["Red"] = "Axial"
    maps["Yellow"] = "Sagittal"
    maps["Green"] = "Coronal"
    for sliceViewName in arlist:
      renderer = layoutManager.sliceWidget(sliceViewName).sliceView().renderWindow().GetRenderers().GetFirstRenderer()
      renderWindow = renderer.GetRenderWindow()
      cornerAnnotationDisplay = layoutManager.sliceWidget(sliceViewName).overlayCornerAnnotation()
      cornerAnnotationDisplay.ClearAllTexts()
      txt1 = ""
      if True:
        txt1 = maps[sliceViewName] + "\n"
        txt2 = "%d"%(point_Ijk[index]) + "\n"
        txt3 = "(%d,%d,%d,%d)"%(point_Ijk[0],point_Ijk[1],point_Ijk[2],grey_value)
        cornerAnnotationDisplay.SetText(1,txt1)
        cornerAnnotationDisplay.SetText(2,txt2)
        cornerAnnotationDisplay.SetText(3,txt3)
      renderWindow.Render()
      index+=1
      if index > 2:
        break
    return
    if self.panel_settings["cb_show_anno"].isChecked():
      pass
    else:
      arlist = ["Green","Red","Yellow"]
      layoutManager = slicer.app.layoutManager()
      for sliceViewName in arlist:
        renderer = layoutManager.sliceWidget(sliceViewName).sliceView().renderWindow().GetRenderers().GetFirstRenderer()
        renderWindow = renderer.GetRenderWindow()
        cornerAnnotationDisplay = layoutManager.sliceWidget(sliceViewName).overlayCornerAnnotation()
        cornerAnnotationDisplay.ClearAllTexts()
        renderWindow.Render()
      return
    ras=[0,0,0]
    crosshairNode=slicer.util.getNode("Crosshair")
    crosshairNode.GetCursorPositionRAS(ras)
    layoutManager = slicer.app.layoutManager()
    red = layoutManager.sliceWidget("Red")
    redLogic = red.sliceLogic()
    compositeNode = redLogic.GetSliceCompositeNode()
    id = compositeNode.GetBackgroundVolumeID()
    if id is None:
      return
    volumeNode = util.GetNodeByID(id)
    volumeRasToIjk = vtk.vtkMatrix4x4()
    volumeNode.GetRASToIJKMatrix(volumeRasToIjk)
    point_Ijk = [0, 0, 0, 1]
    volumeRasToIjk.MultiplyPoint(np.append(ras,1.0), point_Ijk)
    point_Ijk = [ int(round(c)) for c in point_Ijk[0:3] ]
    array1 = util.arrayFromVolume(volumeNode).T
    grey_value = 0
    shape = array1.shape
    if len(shape) == 4:
      #mvDisplayNode = volumeNode.GetDisplayNode()
      #frame =  mvDisplayNode.GetFrameComponent()
      array1 = array1[0]
      shape = array1.shape
    if point_Ijk[0]>0 and point_Ijk[0] < shape[0] and point_Ijk[1]>0 and point_Ijk[1] < shape[1] and  point_Ijk[2]>0 and point_Ijk[2] < shape[2]:
      grey_value = array1[point_Ijk[0],point_Ijk[1],point_Ijk[2]]
    index = 0
    arlist = ["Green","Red","Yellow"]
    maps = {}
    maps["Red"] = "Axial"
    maps["Yellow"] = "Sagittal"
    maps["Green"] = "Coronal"
    for sliceViewName in arlist:
      renderer = layoutManager.sliceWidget(sliceViewName).sliceView().renderWindow().GetRenderers().GetFirstRenderer()
      renderWindow = renderer.GetRenderWindow()
      cornerAnnotationDisplay = layoutManager.sliceWidget(sliceViewName).overlayCornerAnnotation()
      cornerAnnotationDisplay.ClearAllTexts()
      txt1 = ""
      if self.panel_settings['cb_window_style'].isChecked():
        txt1 =txt1+maps[sliceViewName] + "\n"
      if self.panel_settings["cb_layer"].isChecked():
        txt1 = txt1+"L:%d"%(point_Ijk[index]) + "\n"
      if self.panel_settings["cb_grey"].isChecked():
        txt1 = txt1 + "(%d,%d,%d,%d)"%(point_Ijk[0],point_Ijk[1],point_Ijk[2],grey_value)
      if self.panel_settings["ShowPos"].text == "左上":
        cornerAnnotationDisplay.SetText(2,txt1)
      if self.panel_settings["ShowPos"].text == "左下":
        cornerAnnotationDisplay.SetText(0,txt1)
      if self.panel_settings["ShowPos"].text == "右下":
        cornerAnnotationDisplay.SetText(1,txt1)
      if self.panel_settings["ShowPos"].text == "右上":
        cornerAnnotationDisplay.SetText(3,txt1)
      renderWindow.Render()
      index+=1
      if index > 2:
        break

  

  
  

class JAnnotationLogic(ScriptedLoadableModuleLogic):
  m_Node = None
  def __init__(self):
    """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
    ScriptedLoadableModuleLogic.__init__(self)
    slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeAddedEvent, self.onNodeAdded)
  

  def setWidget(self,widget):
    self.m_Widget = widget

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def onNodeAdded(self,caller, event, calldata):
    node = calldata
    #if isinstance(node, slicer.vtkMRMLMarkupsFiducialNode):
      #self.m_Widget.on_node_added(node)


 