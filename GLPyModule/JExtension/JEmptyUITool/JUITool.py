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
# JUITool
#

class JUITool(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "JUITool"  # TODO: make this more human readable by adding spaces
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
# JUIToolWidget
#

class JUIToolWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
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

    self.logic = JUIToolLogic()
    self.logic.setWidget(self)

  
  def on_popup_lineedit_dialog(self,callback):
    def on_data_edit_value(dlg,ui,callback):
      callback(ui.lineEdit.text)
      dlg.hide()
    def on_cancel(val):
      callback("")
    dlg = qt.QDialog()
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/LineEditDialog.ui'))
    ui = slicer.util.childWidgetVariables(uiWidget)
    ui.pushButton.connect('clicked()',lambda:on_data_edit_value(dlg,ui,callback))
    dlg.setWindowTitle("请输入")
    dlg.setWindowIcon(qt.QIcon(':/Icons/MouseRotateMode.png'))
    dlg.setWindowFlags(dlg.windowFlags() & ~0x00010000)
    dlg.setModal(True)
    dlg.connect('finished(int)',on_cancel)
    l = qt.QHBoxLayout(dlg)
    l.addWidget(uiWidget)
    dlg.exec()
  
  
  def on_popup_modulepanel_dialog(self,title,modulename,cancel_callback=None,width=600,height=400):
    def on_cancel(val):
      if cancel_callback:
        cancel_callback()
    panel = slicer.qSlicerModulePanel()
    panel.setModuleManager(slicer.app.moduleManager())
    dlg = qt.QDialog()
    dlg.setWindowTitle(title)
    dlg.setWindowIcon(qt.QIcon(':/Icons/MouseRotateMode.png'))
    dlg.setWindowFlags(dlg.windowFlags() & ~0x00010000)
    dlg.setModal(True)
    dlg.connect('finished(int)',on_cancel)
    dlg.setMinimumWidth(width)
    dlg.setMinimumHeight(height)
    l = qt.QHBoxLayout(dlg)
    l.addWidget(panel)
    panel.setModule(modulename)
    dlg.exec()


  def enter(self):
    pass

  def exit(self):
    pass

 

class JUIToolLogic(ScriptedLoadableModuleLogic):
  color_btn_map = {}
  def __init__(self):
    """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
    ScriptedLoadableModuleLogic.__init__(self)
  

  def setWidget(self,widget):
    self.m_Widget = widget

  def create_labeled_button(self,module_widget,picture_name,tooltip,label="无"):
    widget = qt.QWidget()
    layout = qt.QVBoxLayout(widget)
    button = qt.QPushButton()
    button.setFixedSize(32,32)
    layout.addWidget(button)
    self.add_picture_to_widget(module_widget,button,picture_name)
    labelText = qt.QLabel(widget)
    labelText.setText(label)
    labelText.setFixedSize(32,24)
    labelText.setAlignment(0x0084)
    labelText.setStyleSheet("font: 8px 'Source Han Sans CN-Regular, Source Han Sans CN';")
    layout.addWidget(labelText)
    widget.setToolTip(tooltip)
    return widget,button

  def create_labeled_button2(self,picture_name,tooltip,resource_list,label="无"):
    widget = qt.QWidget()
    layout = qt.QVBoxLayout(widget)
    button = qt.QPushButton()
    button.setFixedSize(32,32)
    layout.addWidget(button)
    self.add_picture_to_widget2(button,picture_name,resource_list,tooltip)
    labelText = qt.QLabel(widget)
    labelText.setText(label)
    labelText.setFixedSize(32,24)
    labelText.setAlignment(0x0084)
    labelText.setStyleSheet("font: 8px 'Source Han Sans CN-Regular, Source Han Sans CN';")
    layout.addWidget(labelText)
    widget.setToolTip(tooltip)
    return widget,button

  def registe_model_opacity_2D(self,slider,node):
    displaynode = util.GetDisplayNode(node)
    if displaynode:
      percent = util.GetDisplayNode(node).GetSliceIntersectionOpacity()
      slider.setValue(percent*100)
      slider.valueChanged.disconnect()
      slider.connect('valueChanged(double)',lambda val: util.GetDisplayNode(node).SetSliceIntersectionOpacity(val/100))


  def registe_model_opacity_3D(self,slider,node):
    displaynode = util.GetDisplayNode(node)
    if displaynode:
      percent = util.GetDisplayNode(node).GetOpacity()
      slider.setValue(percent*100)
      slider.valueChanged.disconnect()
      slider.connect('valueChanged(double)',lambda val: self.on_model_opacity_3d_chagned(node,val))

  def on_model_opacity_3d_chagned(self,node,val):
    displaynode = util.GetDisplayNode(node)
    if displaynode:
      bind_segment = node.GetAttribute("bind_segment")
      if bind_segment:
        bind_segment = util.GetNodeByID(bind_segment)
        util.HideNode(bind_segment)
      util.GetDisplayNode(node).SetOpacity(val/100)

  def registe_model_visible2d_button(self,button,node):
    button.setCheckable(True)
    displaynode = util.GetDisplayNode(node)
    if displaynode:
      visible2d = displaynode.GetVisibility2D() and displaynode.GetVisibility()
      if visible2d:
        button.setChecked(False)
      else:
        button.setChecked(True)
      button.toggled.disconnect()
      
      button.connect('toggled(bool)', lambda is_show:util.HideNode2D(node,not is_show))
    

  def registe_model_visible3d_button(self,button,node):
    displaynode = util.GetDisplayNode(node)
    if displaynode:
      visible3d = displaynode.GetVisibility3D() and displaynode.GetVisibility()
      if visible3d:
        button.setChecked(False)
      else:
        button.setChecked(True)
      button.toggled.disconnect()
      button.connect('toggled(bool)', lambda is_show:util.ShowNode3D(node,not is_show))

  def registe_color_button(self,button,node):
    displaynode = util.GetDisplayNode(node)
    if displaynode:
      if button in self.color_btn_map:
        if node == self.color_btn_map[button]:
          return
      self.color_btn_map[button] = node
      if node.IsA("vtkMRMLSegmentationNode"):
        segment = util.GetNthSegment(node,0)
        scolor = segment.GetColor()
      else:
        scolor = util.GetDisplayNode(node).GetColor()
      button.setStyleSheet("background-color:rgb("+(scolor[0]*255).__str__()+","+(scolor[1]*255).__str__()+","+(scolor[2]*255).__str__()+");")
      button.clicked.disconnect()
      button.connect('clicked()', lambda:self.on_open_color_pad(button,node))

  def create_labeled_clicked_button2(self,widget,btn,picture_name,tooltip,icon_width=26):
    import qt
    btn.setFixedSize(icon_width+10,icon_width+10)
    picture_name = widget.resourcePath(('Icons/'+picture_name)).replace('\\','/')
    pixelmap = qt.QPixmap(picture_name)
    pixelmap_scaled = pixelmap.scaled(icon_width,icon_width, 0,2)
    labelPic = qt.QLabel()
    labelPic.setPixmap(pixelmap_scaled)
    labelPic.setObjectName("labelPic")
    labelPic.setAlignment(0x0004|0x0080)
    labelPic.setStyleSheet("background-color: transparent; border: 0px")
    layout = qt.QVBoxLayout()
    layout.setAlignment(0x0004|0x0080)
    layout.addWidget(labelPic)
    btn.setLayout(layout)
    btn.toolTip = tooltip

    btn_stylesheet = ""
    btn_stylesheet = btn_stylesheet + "QToolTip { color: #000000; background-color: #ffffff; border: 0px; }"
    btn_stylesheet = btn_stylesheet + "QPushButton{background-color: transparent; border: 0px}"
    btn_stylesheet = btn_stylesheet + "QPushButton:hover{border: 1px solid #009900}"
    btn_stylesheet = btn_stylesheet + "QPushButton:pressed{background-color: #363d4a; border: 0px}"
    btn.setStyleSheet(btn_stylesheet)
    return btn,btn

  def create_labeled_clicked_button(self,widget,btn,picture_name,tooltip,icon_width=26,rlist=None):
    import qt
    if rlist:
      rlist[picture_name] = tooltip
    btn.setFixedSize(icon_width+10,icon_width+10)
    picture_name = util.get_resource(picture_name).replace('\\','/')
    pixelmap = qt.QPixmap(picture_name)
    pixelmap_scaled = pixelmap.scaled(icon_width,icon_width, 0,1)
    labelPic = qt.QLabel()
    labelPic.setPixmap(pixelmap_scaled)
    labelPic.setObjectName("labelPic")
    labelPic.setAlignment(0x0004|0x0080)
    labelPic.setStyleSheet("background-color: transparent; border: 0px")
    layout = qt.QVBoxLayout()
    layout.setAlignment(0x0004|0x0080)
    layout.addWidget(labelPic)
    btn.setLayout(layout)
    btn.toolTip = tooltip

    btn_stylesheet = ""
    btn_stylesheet = btn_stylesheet + "QToolTip { color: #000000; background-color: #ffffff; border: 0px; }"
    btn_stylesheet = btn_stylesheet + "QPushButton{background-color: transparent; border: 0px}"
    btn_stylesheet = btn_stylesheet + "QPushButton:hover{border: 1px solid #009900}"
    btn_stylesheet = btn_stylesheet + "QPushButton:pressed{background-color: #363d4a; border: 0px}"
    btn_stylesheet = btn_stylesheet + "QPushButton:checked{background-color: #004444};"
    btn.setStyleSheet(btn_stylesheet)
    return btn,btn

  def on_open_color_pad(self,button,node):
    if node is None:
      return
    qdialog = qt.QColorDialog()
    qdialog.colorSelected.disconnect()
    qdialog.connect('colorSelected(QColor)',lambda qcolor:self.on_get_color(qcolor,node,button))
    qdialog.exec()
  def on_get_color(self,qcolor,node,btn):
    
    btn.setStyleSheet("background-color:rgb("+qcolor.red().__str__()+","+qcolor.green().__str__()+","+qcolor.blue().__str__()+");")
    if node.IsA("vtkMRMLSegmentationNode"):
      segment = util.GetNthSegment(node,0)
      segment.SetColor([qcolor.red()/255.0,qcolor.green()/255.0,qcolor.blue()/255.0])
    else:
      util.GetDisplayNode(node).SetColor([qcolor.red()/255.0,qcolor.green()/255.0,qcolor.blue()/255.0])
  

  def add_picture_to_widget(self,module_widget,widget,picture_name):
    stylesheet = widget.styleSheet
    btnpic = (module_widget.resourcePath('Icons/%s')%(picture_name)).replace('\\','/')
    stylesheet = stylesheet + "QPushButton{image: url("+btnpic+")}"
    widget.setStyleSheet(stylesheet)

  def add_picture_to_widget2(self,widget,picture_name,resource_list,tooltip):
    resource_list[picture_name] = tooltip
    stylesheet = widget.styleSheet
    btnpic = util.get_resource(picture_name)
    stylesheet = stylesheet + "QPushButton{image: url("+btnpic+")}"
    widget.setStyleSheet(stylesheet)
    
  
  def bind_erase_with_buttons(self,button,slider,volume_node,segment_node):
    def on_apply_erase(is_show):
        segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
        segmentEditorWidget.setSegmentationNode(segment_node)
        segmentEditorWidget.setSourceVolumeNode(volume_node)
        if is_show:
          util.trigger_view_tool("Erase")
          segmentEditorWidget.setActiveEffectByName("Erase")
          effect = segmentEditorWidget.activeEffect()
          effect.setParameter("BrushAbsoluteDiameter", slider.value)
          effect.setParameter("EditIn3DViews", 1)
          self.m_ActiveEffect = effect
        else:
          segmentEditorWidget.setActiveEffectByName("None")
    def on_brush_diameter_changed(value):
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      effect = segmentEditorWidget.activeEffect()
      effect.setParameter("BrushAbsoluteDiameter", slider.value)
      
    button.setCheckable(True)
    button.toggled.disconnect()
    button.connect('toggled(bool)', on_apply_erase)  
    slider.valueChanged.disconnect()
    slider.connect('valueChanged(double)', on_brush_diameter_changed)
    util.registe_view_tool(button,"Erase")
  
  def bind_redo_with_buttons(self,button):
    def on_redo():
      util.trigger_view_tool("")
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.redo()
    button.clicked.disconnect()
    button.connect('clicked()', on_redo) 
    
    
  def bind_undo_with_buttons(self,button):
    def on_undo():
      util.trigger_view_tool("")
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.undo()
    button.clicked.disconnect()
    button.connect('clicked()', on_undo) 
  
  def bind_island_with_buttons(self,button,volume_node,segment_node):
    def on_apply_islands():
      util.trigger_view_tool("")
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setSegmentationNode(segment_node)
      segmentEditorWidget.setSourceVolumeNode(volume_node)
      segmentEditorWidget.setActiveEffectByName("Islands")
      effect = segmentEditorWidget.activeEffect()
      effect.setParameterDefault("Operation", "KEEP_LARGEST_ISLAND")
      effect.self().onApply()
    button.setCheckable(False)
    button.clicked.disconnect()
    button.connect('clicked()', on_apply_islands) 
    util.registe_view_tool(button,"Islands")
    
  def bind_scissors_with_buttons(self,button,volume_node,segment_node):
    def on_apply_scissors(is_show):
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      if is_show:
        util.trigger_view_tool("Scissors")
        segmentEditorWidget.setSegmentationNode(segment_node)
        segmentEditorWidget.setSourceVolumeNode(volume_node)
        segmentEditorWidget.setActiveEffectByName("Scissors")
      else:
        segmentEditorWidget.setActiveEffectByName("None")
    button.setCheckable(True)
    button.toggled.disconnect()
    button.connect('toggled(bool)', on_apply_scissors)  
    util.registe_view_tool(button,"Scissors")
  
  def bind_segmentation_opacity(self,slider,node):
    slider.valueChanged.disconnect()
    displaynode = util.GetDisplayNode(node)
    if displaynode:
      percent = util.GetDisplayNode(node).GetOpacity()
      slider.setValue(percent*100)
      slider.connect('valueChanged(double)',lambda val: util.GetDisplayNode(node).SetOpacity(val/100))
      
  def bind_threshold_with_ui(self,volume_node,segment_node,slider,button,callonconfirm=None):
      def onThresholdValuesChanged(dou1,dou2):
          segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
          segmentEditorWidget.setActiveEffectByName("Threshold")
          effect = segmentEditorWidget.activeEffect()
          effect.setParameter("MinimumThreshold", dou1)
          effect.setParameter("MaximumThreshold", dou2)
          print(dou1,dou2)
      def on_apply_threshold():
          segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
          segmentEditorWidget.setSegmentationNode(segment_node)
          segmentEditorWidget.setSourceVolumeNode(volume_node)
          segmentEditorWidget.setActiveEffectByName("Threshold")
          effect = segmentEditorWidget.activeEffect()
          effect.self().onApply()
          if callonconfirm:
            callonconfirm()
          util.ShowNode(segment_node)
      
      
      button.clicked.disconnect() 
      slider.valuesChanged.disconnect()
      lo, hi = util.GetScalarRange(volume_node)
      slider.setRange(lo, hi)
      slider.singleStep = (hi - lo) / 1000.
      slider.setMinimumValue(-400)
      slider.setMaximumValue(hi)
      slider.connect('valuesChanged(double,double)', onThresholdValuesChanged)
      button.connect('clicked()', on_apply_threshold)  
  
  
  
    
  
  def bind_mpr_with_button(self,btn):
    def on_toggle_mpr(is_show):
        print("on_toggle_mpr",is_show)
        if is_show:
          slicer.app.applicationLogic().SetIntersectingSlicesEnabled(slicer.vtkMRMLApplicationLogic.IntersectingSlicesVisibility, True)
          slicer.app.applicationLogic().SetIntersectingSlicesEnabled(slicer.vtkMRMLApplicationLogic.IntersectingSlicesInteractive,True)
          slicer.app.applicationLogic().SetIntersectingSlicesEnabled(slicer.vtkMRMLApplicationLogic.IntersectingSlicesTranslation,True)
          slicer.app.applicationLogic().SetIntersectingSlicesEnabled(slicer.vtkMRMLApplicationLogic.IntersectingSlicesRotation,True)
        else:
          slicer.app.applicationLogic().SetIntersectingSlicesEnabled(slicer.vtkMRMLApplicationLogic.IntersectingSlicesVisibility, False)
   
    btn.setCheckable(True)
    btn.toggled.disconnect() 
    btn.connect('toggled(bool)',on_toggle_mpr)
  