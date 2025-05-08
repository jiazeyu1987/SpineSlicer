import slicer,qt,vtk,ctk
import slicer.util as util
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from Base.JBaseExtension import JBaseExtensionWidget
from AddFiberLib.NormalUnit import NormalUnit
import UnitPunctureGuideLib.G_UnitPunctureGuide as G
#
# UnitCreateChannel
#

    
    
    

class UnitCreateChannel(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UnitCreateChannel"  # TODO: make this more human readable by adding spaces
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
# UnitCreateChannelWidget
#

class UnitCreateChannelWidget(JBaseExtensionWidget):
  normal_unit = None
  TagMaps = {}
  unitlist = []
  fu = None
    
  def init_ui(self):
    self.ui.tabWidget.tabBar().hide()
    util.addWidget2Stretch(self.ui.widget)
    unit = util.create_unit_button("TargetPoint.png","靶点","测量",buttonsize=64,iconsize=48  )
    unit.set_style_to_toggled(self.on_add_target_point)
    util.addWidget2(self.ui.widget,unit.uiWidget)
    
    util.addWidget2Stretch(self.ui.widget)
    unit = util.create_unit_button("EntryPoint.png","入点","测量",buttonsize=64,iconsize=48)
    unit.set_style_to_toggled(self.on_add_entry_point)
    util.addWidget2(self.ui.widget,unit.uiWidget)
    util.addWidget2Stretch(self.ui.widget)
    
    self.TagMaps[util.JAddFiberNormalReturnSingle] = slicer.mrmlScene.AddObserver(util.JAddFiberNormalReturnSingle, self.OnJAddFiberNormalReturnSingle)
    
    
    self.ui.tabWidget.setCurrentIndex(0)
    self.ui.pushButton_4.connect('clicked()',self.on_add)
    self.ui.pushButton.connect('clicked()',self.on_confirm)
    self.ui.pushButton_3.connect('clicked()',self.on_cancel)
    
    self.ui.slider_opacity.singleStep = 1
    self.ui.slider_opacity.minimum = 0
    self.ui.slider_opacity.maximum = 100
    self.ui.slider_opacity.value = 100
    self.ui.slider_opacity.decimals = 1
    self.ui.slider_opacity.connect("valueChanged(double)", self.on_opacity_changed)
    
    self.ui.slider_inner.singleStep = 0.1
    self.ui.slider_inner.minimum = 0.1
    self.ui.slider_inner.maximum = 10
    self.ui.slider_inner.value = 3
    self.ui.slider_inner.decimals = 1
    self.ui.slider_inner.connect("valueChanged(double)", self.on_inner_changed)
    
    self.ui.slider_outer.singleStep = 0.1
    self.ui.slider_outer.minimum = 0.1
    self.ui.slider_outer.maximum = 10
    self.ui.slider_outer.value = 3
    self.ui.slider_outer.decimals = 1
    self.ui.slider_outer.connect("valueChanged(double)", self.on_outer_changed)
    
    self.ui.slider_length.singleStep = 0.1
    self.ui.slider_length.minimum = 0.1
    self.ui.slider_length.maximum = 30
    self.ui.slider_length.value = 10
    self.ui.slider_length.decimals = 1
    self.ui.slider_length.connect("valueChanged(double)", self.on_length_changed)
  
  
  def refresh_tab(self):
    pass
  
  @vtk.calldata_type(vtk.VTK_OBJECT)
  def OnJAddFiberNormalReturnSingle(self,a,b,calldata):
    id1 = calldata.GetAttribute("value")
    print("OnJAddFiberNormalReturnSingle",id1)
    self._OnJAddFiberNormalReturnSingle(id1)
  
  def _OnJAddFiberNormalReturnSingle(self,id1):
    if id1 is None:
      return
    entry_point = util.GetNodeByID(id1)
    self.fu.update_archive_paras()
    #self.ui.tabWidget.setCurrentIndex(1)
    util.color_unit_list.add_item(entry_point, 1)
    util.tips_unit_list.add_item(entry_point, 1)
    util.send_event_str(G.FinishCreateChannel)
  
  
  
  def delete_unit(self,unit):
    pass
    
  def on_add_target_point(self,val):
    if self.normal_unit:
      self.normal_unit.ui.btnAddTarget.setChecked(val)
      
  def on_add_entry_point(self,is_trigger): 
    if not is_trigger:
      return
    if self.entry_point is None:
      entry_point = util.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
      entry_point.SetName("EntryPoint")
      entry_point.SetAttribute("node_type",self.style.__str__())
      self.set_component(entry_point,"entry_point")
    else:
      # util.RemoveNode(self.entry_point)
      # entry_point = util.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
      # entry_point.SetName("EntryPoint")
      # entry_point.SetAttribute("node_type",self.style.__str__())
      # self.set_component(entry_point,"entry_point")
      self.entry_point.RemoveAllControlPoints()
      
    
    display_node = util.GetDisplayNode(self.entry_point)
    display_node.SetPointLabelsVisibility(False)
    interactionNode = slicer.app.applicationLogic().GetInteractionNode()
    selectionNode = slicer.app.applicationLogic().GetSelectionNode()
    selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
    selectionNode.SetActivePlaceNodeID(self.entry_point.GetID())
    interactionNode.SetCurrentInteractionMode(interactionNode.Place)
  
  def on_length_changed(self,val):
    print("on_length_changed")
    
    self.normal_unit.ui.length_slider.setValue(val)
  def on_outer_changed(self,val):
    self.normal_unit.ui.thick_slider.setValue(val)
    util.getModuleWidget("UnitScore").adjust_channel_value = True
  def on_inner_changed(self,val):
    self.normal_unit.ui.radius_slider.setValue(val)
    util.getModuleWidget("UnitScore").adjust_channel_value = True
  def on_opacity_changed(self,val):
    self.normal_unit.on_opacity_2d(val)
    self.normal_unit.on_opacity_3d(val)
    util.getModuleWidget("UnitScore").adjust_channel_value = True

  def on_confirm(self):
    #self.ui.tabWidget.setCurrentIndex(1)
    pass
  def on_cancel(self):
    #self.ui.tabWidget.setCurrentIndex(1)
    pass
  
  def enter(self):
    self.on_add()
    
  def exit(self):
    if not self.fu:
      return
    if self.fu.entry_point != None and self.fu.target_point != None:
      self.fu.update_archive_paras()
      util.color_unit_list.add_item(self.fu.entry_point, 1)
      util.tips_unit_list.add_item(self.fu.entry_point, 1) 
    else:
      util.RemoveNode(self.fu.entry_point)
      util.RemoveNode(self.fu.target_point)
  
  
  def get_unit_by_node(self,node):
    for unit in self.unitlist:
      if unit.entry_point == node:
        return unit
    return None
  
  def set_unit_length(self,node,length):
    unit = self.get_unit_by_node(node)
    unit.ui.length_slider.setValue(length)
  
  def set_unit_radius(self,node,val):
    unit = self.get_unit_by_node(node)
    unit.ui.radius_slider.setValue(val)
    
  def set_unit_thick(self,node,val):
    unit = self.get_unit_by_node(node)
    unit.ui.thick_slider.setValue(val)
  
  def on_delete(self):
    self.unitlist = []
  
  def on_add(self):
    print("on_add NormalUnit")
    if len(self.unitlist) == 0:
      fu = NormalUnit()
      fu.style = "NormalUnit"+":1"
      uiwidget = slicer.util.loadUI(util.getModuleWidget("JAddFiber").resourcePath('UI/JNormalUnitAssist.ui'))
      fu.set_widget(uiwidget,self) 
      self.fu = fu
      util.addWidgetOnly(self.ui.JNormalUnitAssist,uiwidget)
      self.ui.tabWidget.setCurrentIndex(2)
      self.unitlist.append(fu)
    else:
      self.ui.tabWidget.setCurrentIndex(2)
  
  def generate_final_fiber_model(self):
    fibers = []
    for unit in self.unitlist:
      node = unit.generate_final_fiber_model()
      if node is not None:
        fibers.append(node)
    return fibers
  
  def get_volume(self):
    volume = util.getFirstNodeByClassByAttribute(util.vtkMRMLScalarVolumeNode,"main_node","1")
    return volume
  
  
  def OnArchiveLoaded(self,_a,_b):
    self._OnArchiveLoaded()
    
  def _OnArchiveLoaded(self):
    vals = {}
    for node in util.get_all_nodes():
      key = node.GetAttribute("fiber_unit_id")
      if key != None:
        if key in vals:
          vals[key].append(node)
        else:
          vals[key] = [node]
    for key in vals: 
      self.add_archive_uint(key,vals[key])
  
  def add_archive_uint(self,id,nodelist):
    node_type = 0
    for node in nodelist:
      if node.GetAttribute("fiber_unit_type")=="entry_point":
        node_type1 = node.GetAttribute("node_type")
        if node_type1 != None:
          node_type = node_type1
        break
    print('on load node type of %s'%(node_type),len(nodelist),id)
    fu = NormalUnit()
    fu.update_archive_flag = False
    fu.style = "NormalUnit"+":1"
    uiwidget = slicer.util.loadUI(util.getModuleWidget("JAddFiber").resourcePath('UI/JNormalUnitAssist.ui'))
    fu.set_widget(uiwidget,self) 
    self.unitlist.append(fu)
    fu.load_archive(id,nodelist)
    fu.update_archive_flag = True
    
    
  def on_step1(self):
    print("on_step1")
    
  def on_step2(self):
    print("on_step2")
 