import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import slicer.util as util
import SlicerWizard.Utilities as su 
import numpy as np
from JSegmentEditorToolLibs.SegmentManager import *
from JSegmentEditorToolLibs.JSegmentPanel import JSegmentPanel
from JSegmentEditorToolLibs.JSegmentPanelWithUnit import JSegmentPanelWithUnit
#
# JSegmentEditorTool
#



class JSegmentEditorTool(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "JSegmentEditorTool"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["JPlugins"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["jia ze yu"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """

"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """

"""

class SegmentUnit:
  node = None
  ui = None
  widget =None
  main = None
  def __init__(self,main,in_present,in_ui) -> None:
    self.ui = in_ui
    self.main = main
    self.widget = in_present
  
  def init(self,node):
    if self.node:
      self.clear_info("")
      util.RemoveNode(self.node)
    self.node = node
    if node:
      util.GetDisplayNode(node)
      self.ui.lblName.setText(node.GetName())
      path = self.main.resourcePath('Icons/skin.png').replace('\\','/')
      img = qt.QImage()
      img.load(path)
      pixelmap = qt.QPixmap.fromImage(img)
      self.ui.lblImage.setPixmap(pixelmap)
      self.main.create_btn3D(node,self.ui.btn3D)
      self.main.create_btn2D(node,self.ui.btn2D)
      self.main.create_btnPalette(node,self.ui.btnPalette)
      self.main.create_slider3D(node,self.ui.horizontalSlider3D)
  

class JSegmentTool:
  layout = None
  btn = None
  label = None
  para = {}

  
  def __init__(self,layoutin,btnin,labelin):
    self.label = labelin
    self.layout = layoutin
    self.btn = btnin


#
# JSegmentEditorToolWidget
#

class JSegmentEditorToolWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  tool_list = []
  dce_segment_manager = "dce_segment_manager"
  normal_segment_manager = "normal_segment_manager"
  manual_panel = None
  resourcelist = {}
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
    self.logic = JSegmentEditorToolLogic()
    self.logic.setWidget(self)
    
    
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/JSegmentEditorTool.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)
    
   
    uiWidget.setMRMLScene(slicer.mrmlScene)
    
    self.int_manual_segment_panel()
    
    self.get_resource_list()
    if True:
      pass
    else:
      self.init_ui()
    self.ui.reload.connect('clicked()', self.onReload)
    #self.test_add_jsegmentpanel()

  def get_resource_list(self):
    txt = ""
    for key in self.resourcelist:
      value = self.resourcelist[key]
      txt = txt+key+":\t\t"+value+"\n"
    filepath = util.get_resource("segment_list.txt",use_default_path=False)
    if txt != "":
      with open(filepath, "w") as file:
        file.write(txt)
    return txt

  def int_manual_segment_panel(self):
    self.ui.tabWidget.tabBar().hide()
    self.manual_panel = self.create_segment_panel_with_unit(callback=self.on_finish_manual_segment,cancel_callback=lambda:self.on_btnCancel(),buttontxt="确认")
    util.addWidget2(self.ui.widget_5,self.manual_panel.uiWidget)

  def on_btnCancel(self):
    util.send_event_str(util.GotoPrePage)


  def on_finish_manual_segment(self):
    model_node = util.convert_segment_to_model(self.manual_panel.segment_node)
    model_node.SetAttribute("alias_name",self.manual_panel.segment_node.GetAttribute("alias_name"))
    model_node.SetAttribute("bind_segment",self.manual_panel.segment_node.GetID())
    model_node.SetAttribute("jduruofei_name",self.manual_panel.segment_node.GetAttribute("jduruofei_name"))
    slicer.mrmlScene.InvokeEvent(util.JRemoveSkullBoardWidgetResult,model_node)
    util.HideNode(self.manual_panel.segment_node)
    util.send_event_str(util.GotoPrePage)

  
  def onReloadAll(self):
    import os
    file_name = os.path.basename(__file__)
    print(f"Reloading {file_name}")         
    packageName='JSegmentEditorToolLibs'
    submoduleNames=['JSegmentPanel', 'JSegmentPanelWithUnit', 'SegmentManager']
    import imp
    f, filename, description = imp.find_module(packageName)
    package = imp.load_module(packageName, f, filename, description)
    for submoduleName in submoduleNames:
      f, filename, description = imp.find_module(submoduleName, package.__path__)
      try:
          imp.load_module(packageName+'.'+submoduleName, f, filename, description)
      finally:
          f.close()
    util.singleShot(0,lambda:self.onReload())

  def enter(self):
    print("JSegmentEditorTool enter ")

  def exit(self):
    pass

  def test_add_jsegmentpanel(self):
    #panel = self.create_tool_panel("abcd",["Draw","Paint","Threshold","Scissors","LevelTracing","FillBetweenSlice"],None)
    master_node = util.getFirstNodeByName("T1")
    segment_node = util.getFirstNodeByName("S1")
    panel = self.create_tool_panel(master_node,segment_node,"abcd",["Paint","Draw","Scissors","Threshold","LevelTracing","FillBetweenSlice"],None)
    util.addWidget2(self.ui.widget_2,panel.uiWidget)

    master_node = util.getFirstNodeByName("T1")
    segment_node = util.getFirstNodeByName("S2")
    panel = self.create_tool_panel(master_node,segment_node,"vvvv",["Paint","Draw","Threshold","Scissors","LevelTracing","FillBetweenSlice"],lambda:print("123"),lambda:print("234"))
    util.addWidget2(self.ui.widget_4,panel.uiWidget)

  def init_ui(self):
    
    settings = util.mainWindow().GetProjectSettings()
    is_reload = settings.value("General/module_reload")=="2"
    self.ui.reload.setVisible(is_reload)

  def create_tool_panel(self,master_node,segment_node,title,toollist,button_callback=None,cancel_callback=None,button_txt="计算"):
    #from JSegmentEditorToolLibs.JSegmentPanel import JSegmentPanel
    
    panel = JSegmentPanel(self,master_node,segment_node,title,toollist,button_callback,cancel_callback,button_txt)
    return panel


  def create_slider3D(self,node,slider):
    if node:
      util.getModuleLogic("JUITool").registe_model_opacity_3D(slider,node)


  def create_btnPalette(self,node,btn):
    if node:
      util.getModuleLogic("JUITool").registe_color_button(btn,node)


  def create_toollist(self,unit,manager,node,comboBox):
    comboBox.connect("currentIndexChanged(int)",lambda intval: self.on_toollist_changed(unit,comboBox,manager,node,intval))
    unit.ui.panit_slider.setValue(15)
    unit.ui.smooth_slider_kernel.setValue(3)
    unit.ui.smooth_slider_brush.setValue(15)
    unit.ui.margin_out_slider.setValue(3)
    unit.ui.margin_in_slider.setValue(3)
  
  def create_redoundo(self,btnundo,btnredo):
    btnundo.connect('clicked()',lambda:slicer.modules.segmenteditor.widgetRepresentation().self().editor.undo())
    btnredo.connect('clicked()',lambda:slicer.modules.segmenteditor.widgetRepresentation().self().editor.redo())

  def on_toollist_changed(self,unit,comboBox,manager,node,intval):
    txt = comboBox.currentText
    tabWidget = unit.ui.tabWidget
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(unit.node)
    segmentEditorWidget.setSourceVolumeNode(self.logic.master_node)
    if txt == "无":
      tabWidget.setCurrentIndex(0)
      segmentEditorWidget.setActiveEffectByName("None")
    if txt == "笔刷":
      tabWidget.setCurrentIndex(1)
      segmentEditorWidget.setActiveEffectByName("Paint")
      effect = segmentEditorWidget.activeEffect()
      effect.setParameter("BrushSphere", "0")
      effect.setParameter("EditIn3DViews",  "0")
      effect.setParameter("BrushAbsoluteDiameter", "15")
      if "paint" not in unit.paras:
        unit.paras["paint"] = 1 
        unit.ui.panit_slider.connect('valueChanged(double)',lambda douval:effect.setParameter("BrushAbsoluteDiameter", int(douval).__str__()))
        def inner_c(val):
          if val:
            unit.paras["BrushSphere"] = "1"
            effect = segmentEditorWidget.activeEffect()
            effect.setParameter("BrushSphere",  "1")
          else:
            unit.paras["BrushSphere"] = "0"
            effect = segmentEditorWidget.activeEffect()
            effect.setParameter("BrushSphere",  "0")
        unit.ui.checkBox.connect("toggled(bool)",inner_c)
    if txt == "钢笔":
      tabWidget.setCurrentIndex(2)
      segmentEditorWidget.setActiveEffectByName("Draw")
      effect = segmentEditorWidget.activeEffect()
      effect.setParameter("EditIn3DViews",  "0")
    if txt == "删除":  
      tabWidget.setCurrentIndex(3)
      segmentEditorWidget.setActiveEffectByName("Scissors")
      effect = segmentEditorWidget.activeEffect()
      effect.setParameter("EditIn3DViews", 1)
    if txt == "平滑":
      tabWidget.setCurrentIndex(4)
      segmentEditorWidget.setActiveEffectByName("Smoothing")
      effect = segmentEditorWidget.activeEffect()
      effect.setParameter("EditIn3DViews", 1)
      effect.setParameter("KernelSizeMm", "15")
      if "Smoothing" not in unit.paras:
        unit.paras["Smoothing"] = 1 
        unit.ui.smooth_slider_brush.connect('valueChanged(double)',lambda douval:effect.setParameter("BrushAbsoluteDiameter", int(douval).__str__()))
        unit.ui.smooth_slider_kernel.connect('valueChanged(double)',lambda douval:effect.setParameter("KernelSizeMm", int(douval).__str__()))
        def smooth_apply():
          effect.setParameter("EditIn3DViews", 1)
          effect.setParameter("KernelSizeMm", unit.ui.smooth_slider_kernel.value.__str__())
          effect.setParameter("SmoothingMethod", "GAUSSIAN")
          effect.self().onApply()
        unit.ui.smooth_apply.connect('clicked()',smooth_apply)
    if txt == "膨胀":
      tabWidget.setCurrentIndex(5)
      segmentEditorWidget.setActiveEffectByName("Margin")
      effect = segmentEditorWidget.activeEffect()
      effect.setParameter("MarginSizeMm", "3")
      if "MarginOut" not in unit.paras:
        unit.paras["MarginOut"] = 1 
        unit.ui.margin_out_slider.connect('valueChanged(double)',lambda douval:effect.setParameter("MarginSizeMm", int(douval).__str__()))
        
        def margin_apply():
          effect.self().onApply()
        unit.ui.margin_out_apply.connect('clicked()',margin_apply)
    if txt == "缩小":
      tabWidget.setCurrentIndex(6)
      segmentEditorWidget.setActiveEffectByName("Margin")
      effect = segmentEditorWidget.activeEffect()
      effect.setParameter("MarginSizeMm", "-3")
      if "MarginIn" not in unit.paras:
        unit.paras["MarginIn"] = 1 
        unit.ui.margin_in_slider.connect('valueChanged(double)',lambda douval:effect.setParameter("MarginSizeMm", "-%d"%(douval)))
        
        def margin_in_apply():
          effect.self().onApply()
        unit.ui.margin_in_apply.connect('clicked()',margin_in_apply)
    if txt == "阈值":
      tabWidget.setCurrentIndex(7)
      if not self.logic.master_node:
        util.showWarningText("no master node")
        tabWidget.setCurrentIndex(0)
        return
      lo, hi = util.GetScalarRange(self.logic.master_node) 
      unit.ui.thresholdSlider.setRange(lo,hi)
      segmentEditorWidget.setActiveEffectByName("Threshold")
      effect = segmentEditorWidget.activeEffect()
      unit.ui.thresholdSlider.setMaximumValue(hi)
      unit.ui.thresholdSlider.setMinimumValue(200)
      if "Threshold" not in unit.paras:
        unit.paras["Threshold"] = 1 
        def threshold_changed(min,max):
          effect.setParameter("MinimumThreshold", min)
          effect.setParameter("MaximumThreshold", max)
          effect.updateMRMLFromGUI()
        unit.ui.thresholdSlider.connect('valuesChanged(double,double)',threshold_changed)
        
        def threshold_apply():
          effect.self().onApply()
        unit.ui.threshold_apply.connect('clicked()',threshold_apply)
    if txt == "镂空":
      tabWidget.setCurrentIndex(8)
      segmentEditorWidget.setActiveEffectByName("Hollow")
      effect = segmentEditorWidget.activeEffect()
      if "Hollow" not in unit.paras:
        unit.paras["Hollow"] = 1 
        def hollow_changed(val):
          effect.setParameter("ShellThicknessMm", val.__str__())
        unit.ui.hollow_slider.connect('valuesChanged(double)',hollow_changed)
        
        def hollow_apply():
          if unit.ui.hollow_combox.currentText == "内侧镂空":
            effect.setParameter("ShellMode", "INSIDE_SURFACE")
          if unit.ui.hollow_combox.currentText == "中间镂空":
            effect.setParameter("ShellMode", "MEDIAL_SURFACE")
          if unit.ui.hollow_combox.currentText == "外部镂空":
            effect.setParameter("ShellMode", "OUTSIDE_SURFACE")
            
          effect.self().onApply()
        unit.ui.hollow_apply.connect('clicked()',hollow_apply)
    if txt == "岛":
      tabWidget.setCurrentIndex(9)
      segmentEditorWidget.setActiveEffectByName("Islands")
      effect = segmentEditorWidget.activeEffect()
      if "Islands" not in unit.paras:
        unit.paras["Islands"] = 1 
        def on_island_keeplargest():
          print("on_island_keeplargest()")
          effect.setParameter("Operation", "KEEP_LARGEST_ISLAND")
          effect.self().onApply()
        def on_island_removesmall():
          print("on_island_removesmall")
          effect.setParameter("Operation", "REMOVE_SMALL_ISLANDS")
          effect.setParameter("MinimumSize", int(unit.ui.island_sp.value))
          effect.self().onApply()
        unit.ui.island_keeplargest.connect('clicked()',on_island_keeplargest)
        unit.ui.island_removesmall.connect('clicked()',on_island_removesmall)
    if txt == "体素减":
      tabWidget.setCurrentIndex(10)
      
      segmentEditorWidget.setActiveEffectByName("Logical operators")
      effect = segmentEditorWidget.activeEffect()
      effect.setParameter("Operation", "SUBTRACT")
      unit.ui.substract_cb.clear()
      nodes = util.getNodesByClass(util.vtkMRMLSegmentationNode)
      for inner_node in nodes:
        if inner_node == node:
          continue
        alias_name = inner_node.GetAttribute("alias_name")
        unit.ui.substract_cb.addItem(alias_name)
      if "SUBTRACT" not in unit.paras:
        unit.paras["SUBTRACT"] = 1 
        def on_substract_apply():
          cloned_node = util.clone(unit.node)
          cloned_node.SetAttribute("alias_name","相减_"+cloned_node.GetAttribute("alias_name"))
          segmentEditorWidget.setSegmentationNode(cloned_node)
          alias_name = unit.ui.substract_cb.currentText
          node = util.getFirstNodeByClassByAttribute(util.vtkMRMLSegmentationNode,"alias_name",alias_name)
          segment = util.GetNthSegment(node,0)
          segmentid = util.GetNthSegmentID(node,0)
          cloned_node.GetSegmentation().AddSegment(segment,segmentid)
          effect.setParameter("ModifierSegmentID",segmentid)
          effect.self().onApply()
          cloned_node.GetSegmentation().RemoveSegment(segmentid)
          manager.fresh_list()
        unit.ui.substract_apply.connect('clicked()',on_substract_apply)
    if txt == "体素加":
      tabWidget.setCurrentIndex(11)
      segmentEditorWidget.setActiveEffectByName("Logical operators")
      effect = segmentEditorWidget.activeEffect()
      effect.setParameter("Operation", "UNION")
      unit.ui.add_cb.clear()
      nodes = util.getNodesByClass(util.vtkMRMLSegmentationNode)
      for inner_node in nodes:
        if inner_node == node:
          continue
        alias_name = inner_node.GetAttribute("alias_name")
        unit.ui.add_cb.addItem(alias_name)
      if "ADD" not in unit.paras:
        unit.paras["ADD"] = 1 
        def on_add_apply():
          cloned_node = util.clone(unit.node)
          cloned_node.SetAttribute("alias_name","相加_"+cloned_node.GetAttribute("alias_name"))
          segmentEditorWidget.setSegmentationNode(cloned_node)
          alias_name = unit.ui.add_cb.currentText
          node = util.getFirstNodeByClassByAttribute(util.vtkMRMLSegmentationNode,"alias_name",alias_name)
          segment = util.GetNthSegment(node,0)
          segmentid = util.GetNthSegmentID(node,0)
          cloned_node.GetSegmentation().AddSegment(segment,segmentid)
          print("on add ",alias_name)
          effect.setParameter("ModifierSegmentID",segmentid)
          effect.self().onApply()
          cloned_node.GetSegmentation().RemoveSegment(segmentid)
          manager.fresh_list()
        unit.ui.add_apply.connect('clicked()',on_add_apply)
    if txt == "反转":
      tabWidget.setCurrentIndex(12)
      segmentEditorWidget.setActiveEffectByName("Logical operators")
      effect = segmentEditorWidget.activeEffect()
      effect.setParameter("Operation", "INVERT")
      if "INVERT" not in unit.paras:
        unit.paras["INVERT"] = 1 
        def on_invert_apply():
          cloned_node = util.clone(unit.node)
          cloned_node.SetAttribute("alias_name","反转_"+cloned_node.GetAttribute("alias_name"))
          segmentEditorWidget.setSegmentationNode(cloned_node)
          effect.self().onApply()
          manager.fresh_list()
        unit.ui.invert_apply.connect('clicked()',on_invert_apply)
    if txt == "转模型":
      tabWidget.setCurrentIndex(13)
      if "Convert_to_model" not in unit.paras:
        unit.paras["Convert_to_model"] = 1 
        def on_convert_to_model():
          model_node = util.convert_segment_to_model(unit.node)
          model_node.SetAttribute("alias_name",unit.node.GetAttribute("alias_name"))
        unit.ui.convert_model_apply.connect('clicked()',on_convert_to_model)
        util.singleShot(0,lambda:util.send_event_str(util.FreshModelList,"1"))
      

  def create_advance(self,unit,manager,node,btn):
    btn.connect('toggled(bool)', lambda val:self.on_advance(unit,manager,node,val))
    btn.toolTip = "打开高级选项菜单"
  def on_advance(self,unit,manager,node,val):
    if manager:
      if val:
        for node1 in manager.m_TemplateList:
          if node1 == node:
            continue
          template = manager.m_TemplateList[node1]
          template.ui.btnAdvance.setChecked(False)
        

      manager.expand(node,val)
      comboBox = unit.ui.comboBox
      if not val:
        comboBox.setCurrentIndex(0)
    else:
      if val:
        unit.expand()
      else:
        unit.shrink()

  def create_segment_panel_with_unit(self,toollist=["Paint","Draw","Threshold","Scissors","LevelTracing","FillBetweenSlice","Hollow","IslandMax"],callback=None,cancel_callback=None,buttontxt="无"):
    
    panel = JSegmentPanelWithUnit(self,toollist=toollist,callback=callback,cancel_callback=cancel_callback,buttontxt=buttontxt)
    return panel

  def create_btnDelete(self,unit,manager,node,btn):
    self.resourcelist["segment_delete.png"] = "删除当前的分割区域"
    btn_visible = util.get_resource("segment_delete.png")
    btn_stylesheet = ""
    btn_stylesheet = btn_stylesheet + "QToolTip { color: #000000; background-color: #ffffff; border: 0px; }"
    btn_stylesheet = btn_stylesheet + "QPushButton{image: url("+btn_visible+")}"
    btn.connect('clicked()', lambda:self.on_delete_node(unit,manager,node))
    btn.toolTip = self.resourcelist["segment_delete.png"]
    btn.setStyleSheet(btn_stylesheet)

  def on_delete_node(self,unit,manager,node):
    unit.remove_node(node)
    if manager:
      manager.fresh_list()

  def create_btn2D(self,node,btn):
    self.resourcelist["segment_visible_btn2D.png"] = "在2D视图中显示当前的分割区域"
    self.resourcelist["segment_invisible_btn2D.png"] = "在2D视图中隐藏当前的分割区域"
    btn_visible = util.get_resource("segment_visible_btn2D.png")
    btn_unvisible = util.get_resource("segment_invisible_btn2D.png")
    btn_stylesheet = ""
    btn_stylesheet = btn_stylesheet + "QToolTip { color: #000000; background-color: #ffffff; border: 0px; }"
    btn_stylesheet = btn_stylesheet + "QPushButton{image: url("+btn_visible+")}"
    btn_stylesheet = btn_stylesheet + "QPushButton:checked{image: url("+btn_unvisible+")}"
    #btn.connect('toggled(bool)', lambda is_show:util.HideNode2D(node,not is_show))
    btn.toolTip = "在2D视图中显示/隐藏当前的分割区域"
    btn.setStyleSheet(btn_stylesheet)
    if node:
      util.getModuleLogic("JUITool").registe_model_visible2d_button(btn,node)

  def create_btn3D(self,node,btn):
    self.resourcelist["segment_visible_btn3D.png"] = "在3D视图中显示当前的分割区域"
    self.resourcelist["segment_invisible_btn3D.png"] = "在3D视图中隐藏当前的分割区域"
    btn_visible = util.get_resource("segment_visible_btn3D.png")
    btn_unvisible = util.get_resource("segment_invisible_btn3D.png")
    btn_stylesheet = ""
    btn_stylesheet = btn_stylesheet + "QToolTip { color: #000000; background-color: #ffffff; border: 0px; }"
    btn_stylesheet = btn_stylesheet + "QPushButton{image: url("+btn_visible+")}"
    btn_stylesheet = btn_stylesheet + "QPushButton:checked{image: url("+btn_unvisible+")}"
    #btn.connect('toggled(bool)', lambda is_show:util.ShowNode3D(node,not is_show))
    btn.toolTip = "在3D视图中显示/隐藏当前的分割区域"
    btn.setStyleSheet(btn_stylesheet)
    if node:
      util.getModuleLogic("JUITool").registe_model_visible3d_button(btn,node)

  def create_segment_manager(self,name):
    if name == self.dce_segment_manager:
      uiWidget = util.loadUI(self.resourcePath('UI/JDCESegmentManager.ui'))
      m_ui = slicer.util.childWidgetVariables(uiWidget)
      manager=SegmentManager(self,m_ui,0,slicer.mrmlScene)
      return uiWidget,manager
    if name == self.normal_segment_manager:
      uiWidget = util.loadUI(self.resourcePath('UI/JNormalSegmentManager .ui'))
      m_ui = slicer.util.childWidgetVariables(uiWidget)
      manager=SegmentManager(self,m_ui,1,slicer.mrmlScene)
      return uiWidget,manager

      
  def get_new_widget(self,style=1):
    if style == 1:
      # template1 = slicer.util.loadUI(self.resourcePath("UI/SegmentUnit.ui").replace('\\','/'))
      # template1ui = slicer.util.childWidgetVariables(template1)
      # widget = SegmentUnit(self,template1,template1ui)
      # return widget,template1
      template1 = slicer.util.loadUI(self.resourcePath('UI/JNormalROI.ui'))
      template1ui = slicer.util.childWidgetVariables(template1)
      widget = Unit_Normal(self,template1ui,template1)
      
    return widget

  
  def create_labeled_clicked_button(self,btn,picture_name,tooltip,icon_width=30):
    import qt
    btn.setFixedSize(icon_width+10,icon_width+10)
    picture_name = util.get_resource(picture_name)
    
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
    btn_stylesheet = btn_stylesheet + "QPushButton{background-color: transparent; border: 0px}"
    btn_stylesheet = btn_stylesheet + "QPushButton:hover{border: 1px solid #009900}"
    btn_stylesheet = btn_stylesheet + "QPushButton:pressed{background-color: #363d4a; border: 0px}"
    btn.setStyleSheet(btn_stylesheet)
    return btn,btn


  def create_labeled_checkable_button(self,btn,checked_false_name,checked_true_name,tooltip,icon_width=26):
    import qt
    btn.setFixedSize(icon_width+10,icon_width+10)
    btn_checked_true = util.get_resource(checked_true_name)
    btn_checked_false = util.get_resource(checked_false_name)
    
    pixelmap = qt.QPixmap(btn_checked_false)
    pixelmap_scaled = pixelmap.scaled(24,24, 0,1)
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
    btn.setCheckable(True)
    btn_stylesheet = ""
    btn_stylesheet = btn_stylesheet + "QPushButton{background-color: #363d4a; border: 0px}"
    btn_stylesheet = btn_stylesheet + "QPushButton:hover{border: 1px solid #009900}"
    btn_stylesheet = btn_stylesheet + "QPushButton:checked{border: 1px solid #888888}"
    btn_stylesheet = btn_stylesheet + "QPushButton:pressed{background-color: #363d4a; border: 0px}"
    btn.setStyleSheet(btn_stylesheet)
    return btn,btn


  def init_old(self):  
    #normal_spacing = int(settings.value("JSegmentEditorTool/normal_spacing"))
    settings = util.mainWindow().GetProjectSettings()
    toolbars = settings.value("JSegmentEditorTool/tools")
    if toolbars:
      for toolbar in toolbars:
        if toolbar.strip()=="":
          return
        tool_name = toolbar
        tool = self.add_tool_by_name(tool_name,self.ui.widget)  
    
    pos = 0
    for tool in self.tool_list:
      tool.layout.move(pos,10)
      pos =  pos + 85


  def add_tools(self,namelist,parent_widget,spacing=60):
    tools = []
    for name in namelist:
      widget,_ = self.add_tool_by_name(name,parent_widget)
      tools.append(widget)
    for i in range(len(tools)):
      tools[i].layout.move(i*spacing,0)
    self.get_resource_list()

  
  def add_tool_by_name(self,tool_name,parent_widget):
    if tool_name == 'Paint':
      return self.add_paint_tool(parent_widget)
    if tool_name == 'Draw':
      return self.add_draw_tool(parent_widget)
    if tool_name == 'Scissors':
      return self.add_scissors_tool(parent_widget)
    if tool_name == 'ChooseSlices':
      return self.add_choose_slice_tool(parent_widget)

  def add_scissors_tool_with_paras(self,parent_widget,param_widget):
    layout,btn = self.logic.create_checkable_button(parent_widget,"segment_tool_scissors.png","删除工具:可以在二维视图和三维视图上选择不需要的区域删除","删除")
    tool = JSegmentTool(layout,btn,"Scissors_with_paras")
    self.tool_list.append(tool)
    util.registe_view_tool(btn,"Scissors_with_paras")
    
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/JSegmentPanelSub/%s.ui')%("Scissors"))
    btn.setCheckable(False)
    btn.connect('clicked()',lambda:self.on_tool_hide_scissors_with_paras(ui))
    btn.setEnabled(False)
    ui = slicer.util.childWidgetVariables(uiWidget)
    ui.paint_slider.singleStep = 1
    ui.paint_slider.minimum = 1
    ui.paint_slider.maximum = 100
    ui.paint_slider.value = 3
    ui.paint_slider.connect('valueChanged(double)', self.on_scissor_paint_slider_changed)
    ui.paint_slider.setValue(30)
    ui.paint_slider.setVisible(False)
    ui.radioButton.connect('toggled(bool)',lambda:self.on_scissor_style(1,ui))
    ui.radioButton_2.connect('toggled(bool)',lambda:self.on_scissor_style(2,ui))
    ui.radioButton_3.connect('toggled(bool)',lambda:self.on_scissor_style(3,ui))
    ui.radioButton_4.connect('toggled(bool)',lambda:self.on_scissor_style(4,ui))
    util.addWidgetOnly(param_widget,uiWidget)
    return tool,ui
  def on_tool_hide_scissors_with_paras(self,ui):
      ui.radioButton.setChecked(False)
      ui.radioButton_2.setChecked(False)
      ui.radioButton_3.setChecked(False)
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setActiveEffectByName("None")
  
  def on_scissor_paint_slider_changed(self,value):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    paintEffect = segmentEditorWidget.activeEffect()
    if paintEffect:
      paintEffect.setParameter("BrushAbsoluteDiameter", value)
  
  def on_scissor_style(self,style,ui):
    import slicer
    if style==3:
      ui.paint_slider.setVisible(True)
    else:
      ui.paint_slider.setVisible(False)
    
    if style==1:
      self._on_tool_hide_scissors(None,True,self.logic.master_node,self.logic.segment_node)
    elif style == 2:
      self._on_tool_hide_scissors_circle(None,True,self.logic.master_node,self.logic.segment_node)
    elif style == 3:
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setActiveEffectByName("Erase")
      paintEffect = segmentEditorWidget.activeEffect()
      paintEffect.setCommonParameter("BrushAbsoluteDiameter", ui.paint_slider.value)
      paintEffect.setCommonParameter("BrushSphere", "1")
      paintEffect.setCommonParameter("EditIn3DViews", 1)
    elif style == 4:
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setActiveEffectByName("None")
  
  def add_undo(self,parent_widget):
    layout,btn = self.logic.create_checkable_button(parent_widget,"btn_undo.png","撤销:快捷键ctrl+Z","撤销")
    btn.setCheckable(False)
    btn.setShortcut(qt.QKeySequence("Ctrl+Z"))
    btn.connect('clicked()',lambda:slicer.modules.segmenteditor.widgetRepresentation().self().editor.undo())
    return layout,btn
  
  def add_redo(self,parent_widget):
    layout,btn = self.logic.create_checkable_button(parent_widget,"btn_redo.png","反撤销:快捷键ctrl+Y","恢复")
    btn.setCheckable(False)
    btn.setShortcut(qt.QKeySequence("Ctrl+Y"))
    btn.connect('clicked()',lambda:slicer.modules.segmenteditor.widgetRepresentation().self().editor.redo())
    return layout,btn
  
  def add_choose_slice_tool(self,parent_widget):
    layout,btn = self.logic.create_checkable_button(parent_widget,"segment_tool_threshold.png","选择层工具:可以选择多个层","选择层")
    tool = JSegmentTool(layout,btn,"ChooseSlices")
    self.tool_list.append(tool)
    btn.connect('toggled(bool)',lambda is_show: self.on_tool_choose_slices(btn,is_show))
    util.registe_view_tool(btn,"ChooseSlices")
    return tool,None
  def on_tool_choose_slices(self,btn,is_show):
    self._on_tool_choose_slices(btn,is_show,self.logic.master_node,self.logic.segment_node)
  def _on_tool_choose_slices(self,btn,is_show,master_node,segment_node):
    if not master_node:
      if is_show and btn:
        btn.setChecked(False)
      return False
    if not segment_node:
      if is_show and btn:
        btn.setChecked(False)
      return False
    if is_show:
      util.trigger_view_tool("ChooseSlices")
    
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(master_node)
    if is_show:
      segmentEditorWidget.setActiveEffectByName("Scissors")
      effect = segmentEditorWidget.activeEffect()
      effect.setParameter("EditIn3DViews", 1)
      effect.setParameter("Shape", "Rectangle")
      effect.setParameter("Operation", "FillInside")
    else:
      segmentEditorWidget.setActiveEffectByName("None")
    return True
  
  def add_scissors_tool(self,parent_widget):
    layout,btn = self.logic.create_checkable_button(parent_widget,"segment_tool_scissors.png","删除工具:可以在二维视图和三维视图上选择不需要的区域删除","删除")
    tool = JSegmentTool(layout,btn,"Scissors")
    self.tool_list.append(tool)
    btn.connect('toggled(bool)',lambda is_show: self.on_tool_hide_scissors(btn,is_show))
    util.registe_view_tool(btn,"Scissors")
    return tool,None

  def on_tool_hide_scissors(self,btn,is_show):
    self._on_tool_hide_scissors(btn,is_show,self.logic.master_node,self.logic.segment_node)
  def _on_tool_hide_scissors(self,btn,is_show,master_node,segment_node):
    if not master_node:
      if is_show and btn:
        btn.setChecked(False)
      return False
    if not segment_node:
      if is_show and btn:
        btn.setChecked(False)
      return False
    if is_show:
      util.trigger_view_tool("Scissors")
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(master_node)
    if is_show:
      segmentEditorWidget.setActiveEffectByName("Scissors")
      effect = segmentEditorWidget.activeEffect()
      effect.setParameter("EditIn3DViews", 1)
      effect.setParameter("Shape", "FreeForm")
      effect.setParameter("Operation", "EraseInside")
    else:
      segmentEditorWidget.setActiveEffectByName("None")
    return True
  
  def _on_tool_hide_scissors_circle(self,btn,is_show,master_node,segment_node):
    if not master_node:
      if is_show and btn:
        btn.setChecked(False)
      return False
    if not segment_node:
      if is_show and btn:
        btn.setChecked(False)
      return False
    if is_show:
      util.trigger_view_tool("Scissors")
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(master_node)
    if is_show:
      segmentEditorWidget.setActiveEffectByName("Scissors")
      effect = segmentEditorWidget.activeEffect()
      effect.setParameter("EditIn3DViews", 1)
      effect.setParameter("Shape", "Circle")
    else:
      segmentEditorWidget.setActiveEffectByName("None")
    return True

  def on_tool_hide_fill_between_slice(self,btn,is_show):
    self._on_tool_hide_fill_between_slice(btn,is_show,self.logic.master_node,self.logic.segment_node)
  def _on_tool_hide_fill_between_slice(self,btn,is_show,master_node,segment_node):
    if not master_node:
      if is_show:
        btn.setChecked(False)
      return False
    if not segment_node:
      if is_show:
        btn.setChecked(False)
      return False
    if is_show:
      util.trigger_view_tool("FillBetweenSlice")
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(master_node)
    if is_show:
      segmentEditorWidget.setActiveEffectByName("Fill between slices")
    else:
      segmentEditorWidget.setActiveEffectByName("None")
    return True

  def on_tool_hide_leveltracing(self,btn,is_show):
    self._on_tool_hide_leveltracing(btn,is_show,self.logic.master_node,self.logic.segment_node)
  def _on_tool_hide_leveltracing(self,btn,is_show,master_node,segment_node):
    
    if not master_node:
      if is_show:
        btn.setChecked(False)
      return False
    if not segment_node:
      if is_show:
        btn.setChecked(False)
      return False
    if is_show:
      util.trigger_view_tool("LevelTracing")
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(master_node)
    if is_show:
      segmentEditorWidget.setActiveEffectByName("Level tracing")
    else:
      segmentEditorWidget.setActiveEffectByName("None")
    return True
  
  def _on_tool_hide_islandmax(self,btn,is_show,master_node,segment_node):
    
    if not master_node:
      if is_show:
        btn.setChecked(False)
      return False
    if not segment_node:
      if is_show:
        btn.setChecked(False)
      return False
    if is_show:
      util.trigger_view_tool("LevelTracing")
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(master_node)
    if is_show:
      segmentEditorWidget.setActiveEffectByName("Islands")
      effect = segmentEditorWidget.activeEffect()
      effect.setParameterDefault("Operation", "KEEP_LARGEST_ISLAND")
      effect.self().onApply()
      util.showWarningText("已保留最大连通域")
    else:
      segmentEditorWidget.setActiveEffectByName("None")
    return True
 

  def add_paint_tool(self,parent_widget):
    layout,btn = self.logic.create_checkable_button(parent_widget,"segment_tool_paint.png","笔刷工具:类似于刷子,可以选择合适的刷子大小和刷子类型","笔刷")
    tool = JSegmentTool(layout,btn,"Paint")
    self.tool_list.append(tool)
    btn.connect('toggled(bool)', lambda is_show:self.on_tool_hide_paint(btn,is_show))
    util.registe_view_tool(btn,"Paint")
    self.ui.paint_slider.singleStep = 1
    self.ui.paint_slider.minimum = 1
    self.ui.paint_slider.maximum = 100
    self.ui.paint_slider.value = 3
    self.ui.paint_slider.connect('valueChanged(double)', self.on_paint_slider_changed)
    self.ui.paint_checkbox.connect('stateChanged(int)', self.on_sphere_brush)
    return tool,self.ui.paint_layout

  def on_sphere_brush(self,val):
    if val:
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      paintEffect = segmentEditorWidget.effectByName("Paint")
      paintEffect.setParameter("BrushSphere", "1")
    else:
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      paintEffect = segmentEditorWidget.effectByName("Paint")
      paintEffect.setParameter("BrushSphere", "0")

  def on_paint_slider_changed(self,value):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    paintEffect = segmentEditorWidget.effectByName("Paint")
    paintEffect.setParameter("EditIn3DViews", "1")
    paintEffect.setParameter("BrushSphere", "1")
    paintEffect.setCommonParameter("BrushAbsoluteDiameter", value)

  def on_tool_hide_paint(self,btn,is_show):
    self._on_tool_hide_paint(btn,is_show,self.logic.master_node,self.logic.segment_node)
  def _on_tool_hide_paint(self,btn,is_show,master_node,segment_node,ui=None):
    if not master_node:
      if is_show:
        btn.setChecked(False)
      print("master_node is None")
      return False
    if not segment_node:
      if is_show:
        btn.setChecked(False)
      print("segment_node is None")
      return False
    if is_show:
      util.trigger_view_tool("Paint")
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(master_node)
    if ui is None:
      targetui = self.ui
    else:
      targetui = self.ui
    if is_show:
      segmentEditorWidget.setActiveEffectByName("Paint")
      effect = segmentEditorWidget.activeEffect()
      effect.setParameter("EditIn3DViews", 1)
      if targetui.paint_checkbox.isChecked():
        effect.setParameter("BrushSphere", "1")
      else:
        effect.setParameter("BrushSphere", "0")
    else:
      segmentEditorWidget.setActiveEffectByName("None")
    return True
  
  def on_hollow_slider_changed(self,value):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    paintEffect = segmentEditorWidget.effectByName("Erase")
    paintEffect.setCommonParameter("BrushAbsoluteDiameter", value)
    
  def _on_tool_hide_hollow(self,btn,is_show,master_node,segment_node,ui=None):
    if not master_node:
      if is_show:
        btn.setChecked(False)
      print("master_node is None")
      return False
    if not segment_node:
      if is_show:
        btn.setChecked(False)
      print("segment_node is None")
      return False
    if is_show:
      util.trigger_view_tool("Paint")
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(master_node)
    if is_show:
      segmentEditorWidget.setActiveEffectByName("Erase")
      effect = segmentEditorWidget.activeEffect()
      effect.setCommonParameter("EditIn3DViews", 1)
      effect.setCommonParameter("BrushSphere", "1")
    else:
      segmentEditorWidget.setActiveEffectByName("None")
    return True
  
  def on_tool_hide_threshold(self,btn,is_show):
    self._on_tool_hide_threshold(btn,is_show,self.logic.master_node,self.logic.segment_node)
  def _on_tool_hide_threshold(self,btn,is_show,master_node,segment_node):
    if not master_node:
      if is_show:
        btn.setChecked(False)
      return False
    if not segment_node:
      if is_show:
        btn.setChecked(False)
      return False
    if is_show:
      util.trigger_view_tool("Threshold")
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(master_node)
    if is_show:
      segmentEditorWidget.setActiveEffectByName("Threshold")
    else:
      segmentEditorWidget.setActiveEffectByName("None")
    return True

  

  def add_threshold_tool(self,parent_widget,master_node_name=None,segment_node_name = None):
    layout,btn = self.logic.create_checkable_button(parent_widget,"threshold.png","阈值工具:会选择灰度值范围在阈值区间的作为目标区域","阈值")
    btn.clicked.disconnect()
    btn.move(0,0)
    tool = JSegmentTool(layout,btn,"Threshold")
    tool.para["master_node_name"] = master_node_name
    tool.para["segment_node_name"] = segment_node_name
    self.tool_list.append(tool)
    btn.connect('toggled(bool)', lambda is_show:self.on_tool_Threshold(tool,is_show))
    util.registe_view_tool(btn,"Threshold")
    threshold_uiwidget = slicer.util.loadUI(self.resourcePath('UI/JSegmentPanelSub/Threshold.ui'))
    threshold_ui = slicer.util.childWidgetVariables(threshold_uiwidget)
    threshold_ui.thresholdSlider.connect('valuesChanged(double,double)', lambda h,l:self.onThresholdValuesChanged(tool,h,l))
    threshold_ui.threshold_apply.connect('clicked()',lambda: self.on_apply_threshold(tool))
    tool.para["layout"] = self.ui
    return tool,threshold_uiwidget,threshold_ui.threshold_apply

  
  
  def on_tool_Threshold(self,tool,is_show):
    if "master_node_name" not in tool.para:
      return
    if "segment_node_name" not in tool.para:
      return
    segment_node = util.EnsureFirstNodeByNameByClass(tool.para["segment_node_name"],util.vtkMRMLSegmentationNode)
    master_node = util.getFirstNodeByName(tool.para["master_node_name"])
    if not master_node:
      return

    if is_show:
      util.trigger_view_tool("Threshold")
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(master_node)
    if is_show:
      segmentEditorWidget.setActiveEffectByName("Threshold")
    else:
      segmentEditorWidget.setActiveEffectByName("None")
    
    lo, hi = util.GetScalarRange(master_node)
    self.ui.thresholdSlider.setRange(lo, hi)
    self.ui.thresholdSlider.singleStep = (hi - lo) / 1000.
    self.ui.thresholdSlider.setMaximumValue(hi)
    if "min" in tool.para:
      self.ui.thresholdSlider.setMinimumValue(tool.para["min"])
    else:
      self.ui.thresholdSlider.setMinimumValue(lo)

  def onThresholdValuesChanged(self,tool,dou1,dou2):
    if "master_node_name" not in tool.para:
      return
    if "segment_node_name" not in tool.para:
      return
    master_node = util.getFirstNodeByName(tool.para["master_node_name"])
    if not master_node:
      return
  def onThresholdValuesChanged2(self,dou1,dou2):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("MinimumThreshold", dou1)
    effect.setParameter("MaximumThreshold", dou2)
    effect.updateMRMLFromGUI()
  
  def on_fill_between_slice(self,master_node,segment_node):
    if master_node is None:
      return
    if segment_node is None:
      return
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(master_node)
    segmentEditorWidget.setActiveEffectByName("Fill between slices")
    effect = segmentEditorWidget.activeEffect()
    print("on_fill_between_slice",segment_node.GetName(),master_node.GetName())
    effect.self().onPreview()
    util.singleShot(0,lambda:effect.self().onApply())
  def on_fill_between_slice2(self):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setActiveEffectByName("Fill between slices")
    effect = segmentEditorWidget.activeEffect()
    effect.self().onPreview()
    util.singleShot(0,lambda:effect.self().onApply())
    

  def on_apply_threshold2(self):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    effect = segmentEditorWidget.activeEffect()
    if effect:
      effect.self().onApply()
  def on_apply_threshold(self,tool):
    self.on_apply_threshold2()
    util.send_event_str(util.ThresholdApplyed,tool.para["segment_node_name"])


  def add_leveltracing_tool(self,parent_widget):
    layout,btn = self.logic.create_checkable_button(parent_widget,"leveltracing.png","魔术棒工具:类似于PS的魔术棒,会选择颜色相近的区域","魔术棒")
    tool = JSegmentTool(layout,btn,"LevelTracing")
    self.tool_list.append(tool)
    btn.connect('toggled(bool)', lambda is_show:self.on_tool_leveltracing(btn,is_show))
    util.registe_view_tool(btn,"LevelTracing")
    return tool,None
  def on_tool_leveltracing(self,btn,is_show):
    if not self.logic.master_node:
      if is_show:
        btn.setChecked(False)
      return
    if not  self.logic.segment_node:
      if is_show:
        btn.setChecked(False)
      return
    if is_show:
      util.trigger_view_tool("LevelTracing")
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(self.logic.segment_node)
    segmentEditorWidget.setSourceVolumeNode(self.logic.master_node)
    if is_show:
      segmentEditorWidget.setActiveEffectByName("Level tracing")
    else:
      segmentEditorWidget.setActiveEffectByName("None")


  def add_draw_tool(self,parent_widget):
    layout,btn = self.logic.create_checkable_button(parent_widget,"segment_tool_draw.png","绘制工具:用鼠标左键在二维视图上画一个闭合曲线,算法将自动填充这个闭合曲线","绘制")
    tool = JSegmentTool(layout,btn,"Draw")
    self.tool_list.append(tool)
    btn.connect('toggled(bool)', lambda is_show:self.on_tool_hide_draw(btn,is_show))
    util.registe_view_tool(btn,"Draw")
    return tool,None

  def on_tool_hide_draw(self,btn,is_show):
    self._on_tool_hide_draw(btn,is_show,self.logic.master_node,self.logic.segment_node)
  def _on_tool_hide_draw(self,btn,is_show,master_node,segment_node):
    if not master_node:
      if is_show:
        btn.setChecked(False)
      return False
    if not  segment_node:
      if is_show:
        btn.setChecked(False)
      return False
    if is_show:
      util.trigger_view_tool("Draw")
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(master_node)
    if is_show:
      segmentEditorWidget.setActiveEffectByName("Draw")
    else:
      segmentEditorWidget.setActiveEffectByName("None")
    return True
  
  

class JSegmentEditorToolLogic(ScriptedLoadableModuleLogic):
  segment_node = None
  master_node = None
  def __init__(self):
    """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
    ScriptedLoadableModuleLogic.__init__(self)

  def set_nodes(self,master_node,segment_node):
    self.master_node = master_node
    self.segment_node = segment_node

  def setWidget(self,widget):
    self.m_Widget = widget

  def threhold(self,master_node,segment_node,lower_threhold,higher_threhold,nth_segment_id = 0):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(master_node)
    segmentEditorWidget.setActiveEffectByName("Threshold")
    selectedSegmentID = util.GetNthSegmentID(segment_node,nth_segment_id)
    segmentEditorWidget.setCurrentSegmentID(selectedSegmentID)
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("MinimumThreshold", lower_threhold)
    effect.setParameter("MaximumThreshold", higher_threhold)
    effect.self().onApply()

  def smoothing(self,master_node,segment_node,method="GAUSSIAN",kernel_size=1):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(master_node)
    segmentEditorWidget.setActiveEffectByName("Smoothing")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("SmoothingMethod",method)
    effect.setParameter("KernelSizeMm",str(kernel_size))
    effect.self().onApply()

  # result = segment_node1 - segment_node2
  def substract(self,master_node,segment_node1,segment_node2):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSourceVolumeNode(master_node)
    segmentEditorWidget.setSegmentationNode(segment_node1)

    segmentEditorWidget.setActiveEffectByName("Logical operators")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("Operation", "SUBTRACT")

    segment = util.GetNthSegment(segment_node2,0)
    segmentid = util.GetNthSegmentID(segment_node2,0)
    segment_node1.GetSegmentation().AddSegment(segment,segmentid+"cop")

    effect.setParameter("ModifierSegmentID",segmentid+"cop")
    effect.self().onApply()
    segment_node1.GetSegmentation().RemoveSegment(segmentid+"cop")

  def hollow_like_skin(self,master_node,segment_node,thick="3"):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(master_node)
    segmentEditorWidget.setActiveEffectByName("Hollow")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("ShellMode", 'OUTSIDE_SURFACE')
    effect.setParameter("ShellThicknessMm", thick)
    effect.self().onApply()
  
  def hollow_like_mask(self,master_node,segment_node,thick="3",skin_distance="0"):
    if skin_distance != "0":
      cloned_node = util.clone(segment_node)
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setSegmentationNode(cloned_node)
      segmentEditorWidget.setSourceVolumeNode(master_node)
      segmentEditorWidget.setActiveEffectByName("Hollow")
      effect = segmentEditorWidget.activeEffect()
      effect.setParameter("ShellMode", 'INSIDE_SURFACE')
      effect.setParameter("ShellThicknessMm", skin_distance)
      effect.self().onApply()
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(master_node)
    segmentEditorWidget.setActiveEffectByName("Hollow")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("ShellMode", 'INSIDE_SURFACE')
    effect.setParameter("ShellThicknessMm", (float(thick)+float(skin_distance)).__str__())
    effect.self().onApply()
    if skin_distance != "0":
      self.substract(master_node,segment_node,cloned_node)
      util.RemoveNode(cloned_node)

  def islands_max(self,master_node,segment_node):
    print("on island max",master_node.GetID(),segment_node.GetID())
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(master_node)
    segmentEditorWidget.setActiveEffectByName("Islands")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameterDefault("Operation", "KEEP_LARGEST_ISLAND")
    effect.self().onApply()

  def remove_island_smaller_than(self,master_node,segment_node,threshold=100000):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(master_node)
    segmentEditorWidget.setActiveEffectByName("Islands")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("Operation", "REMOVE_SMALL_ISLANDS")
    effect.setParameter("MinimumSize", threshold)
    effect.self().onApply()


  def margin_out(self,master_node,segment_node,value=2):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(master_node)
    segmentEditorWidget.setActiveEffectByName("Margin")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("MarginSizeMm", "%s"%(value))
    effect.self().onApply()

  def mask_volume(self,master_node,segment_node,input_node,output_node):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(master_node)
    segmentEditorWidget.setActiveEffectByName("Mask volume")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("FillValue", "%s"%(-1000))
    effect.setParameter("Operation", "FILL_INSIDE")
    effect.self().inputVolumeSelector.setCurrentNode(input_node)
    effect.self().outputVolumeSelector.setCurrentNode(output_node)
    effect.self().onApply()

  def fill_slice(self,master_node,segment_node):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(master_node)
    segmentEditorWidget.setActiveEffectByName("Fill between slices")
    effect = segmentEditorWidget.activeEffect()
    effect.self().onPreview()
    effect.self().onApply()

  def add_segment(self,master_node,segment_node):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(master_node)
    segmentEditorWidget.onAddSegment()

  def grow_from_seeds(self,master_node,segment_node):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(master_node)
    segmentEditorWidget.setActiveEffectByName("Grow from seeds")
    effect = segmentEditorWidget.activeEffect()
    effect.self().onApply()

  '''
    用途
    用户在三个方向画感兴趣的区域
    最后生成一个包含这三个方向感兴趣区域的方块Segment
  '''
  def fill_segment_with_extent(self,segment_node):
    segmentId = util.GetNthSegmentID(segment_node,0)
    seg=util.arrayFromSegmentInternalBinaryLabelmap(segment_node, segmentId).T
    seg[:] = 1
    segment_node.GetSegmentation().GetSegment(segmentId).Modified()

  '''
    获取到一个SegmentationNode的world中心点
  '''
  def get_segmentation_center_point(self,segment_node):
    
    seg_id = util.GetNthSegmentID(segment_node,0)
    segImage = slicer.vtkOrientedImageData()
    segment_node.GetBinaryLabelmapRepresentation(seg_id,segImage)
    segImageExtent = segImage.GetExtent()
    ijkToWorld = vtk.vtkMatrix4x4()
    segImage.GetImageToWorldMatrix(ijkToWorld)

    binary_volume = util.arrayFromSegment(segment_node,seg_id).T

    # 获取该Segment所有非零点的坐标
    nonzero_idxs = np.argwhere(binary_volume != 0 )
    center = np.mean(nonzero_idxs, axis=0)

    return center

  def create_checkable_button(self,parent,filename,tooltip,label):
    widget = qt.QWidget(parent)
    label_width = 60
    btn_width = 32
    spacing = 0
    btn = qt.QPushButton(widget)
    btn.setGeometry((label_width-btn_width)/2-2,0,btn_width,btn_width)
    btn.setCheckable(True)
    util.getModuleLogic("JUITool").add_picture_to_widget2(btn,filename,self.m_Widget.resourcelist,tooltip)

    labelText = qt.QLabel(widget)
    labelText.setText(label)
    labelText.setFixedSize(label_width,btn_width)
    labelText.setAlignment(0x0084)
    labelText.setStyleSheet("font: 12px 'Source Han Sans CN-Regular, Source Han Sans CN';")
    labelText.move(0,btn_width+spacing)
    return widget,btn
 
  