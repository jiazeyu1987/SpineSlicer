import slicer,qt,vtk,ctk
import slicer.util as util
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from Base.JBaseExtension import JBaseExtensionWidget

#
# FrameworkBottom
#



class FrameworkBottom(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "FrameworkBottom"  # TODO: make this more human readable by adding spaces
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
# FrameworkBottomWidget
#

class FrameworkBottomWidget(JBaseExtensionWidget):
  button_map = {}
  is_First_Load = True
  def setup(self):
    super().setup()
    
    
    
    self.TagMaps[util.ResetSolution] = slicer.mrmlScene.AddObserver(util.ResetSolution, self.OnResetSolution)
    self.TagMaps[util.BackToSolution] = slicer.mrmlScene.AddObserver(util.BackToSolution, self.OnBackToSolution)
    slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeAddedEvent, self.onNodeAdded)
    
    util.singleShot(0,self.init_later)
    #util.singleShot(2000,self.init_later2)
    # panel = slicer.qSlicerModulePanel()
    # panel.setModuleManager(slicer.app.moduleManager())    
    # slicer.util.addWidget2(self.ui.tools, panel)
    # panel.setModule("JMeasure")   
    slicer.util.addWidget2(self.ui.tools, util.getModuleWidget("JMeasure").get_control_panel())

  
  def init_later(self):
    util.getModuleWidget("FrameworkRouter")   
  
  
  def get_extension(self):
    return "mrb"
    
  #type 1: channel; 2: segment 3:model 4:ScalarVolumeNode 
  def add_color_unit(self, node, unitType):
    if util.color_unit_list:
      util.color_unit_list.add_item(node, unitType)
    if util.tips_unit_list:
      util.tips_unit_list.add_item(node, unitType)
  
  
  def OnArchiveLoaded(self,_a,_b):
    util.singleShot(10,self.__OnArchiveLoaded)
    
  def __OnArchiveLoaded(self):
    util.color_unit_list.clear()
    util.color_unit_list.reinit()
    util.tips_unit_list.clear()
    util.tips_unit_list.reinit()
    
    
  @vtk.calldata_type(vtk.VTK_OBJECT)
  def onNodeAdded(self,caller, event, calldata):
    self._onNodeAdded(calldata)
  def _onNodeAdded(self,calldata):
    node = calldata
    if isinstance(node,slicer.vtkMRMLLabelMapVolumeNode): 
      pass
    elif isinstance(node, slicer.vtkMRMLScalarVolumeNode):
      print("node is slicer.vtkMRMLScalarVolumeNode")
      flag = node.GetAttribute("color_unit")
      self.add_color_unit(node, 4)        
      pass
    return
    print(node.GetName())
    if node.GetAttribute("fiber_unit_type") == "entry_point":
      flag = node.GetAttribute("color_unit")
      if flag == "1":
        self.add_color_unit(node, 1)
    elif isinstance(node, slicer.vtkMRMLSegmentationNode):
      flag = node.GetAttribute("color_unit")
      if flag == "1":
        self.add_color_unit(node, 2)
    elif isinstance(node, slicer.vtkMRMLModelNode):
      flag = node.GetAttribute("color_unit")
      if flag == "1":
        self.add_color_unit(node, 3)
    elif isinstance(node, slicer.vtkMRMLScalarVolumeNode):
      print("node is slicer.vtkMRMLScalarVolumeNode")
      flag = node.GetAttribute("color_unit")
      self.add_color_unit(node, 4)        
      pass
    else:
      pass
  
  
  
  def OnResetSolution(self,_a,_b):    
    if self.is_First_Load:
      util.send_event_str(util.ProgressStart, util.tr("正在切换解决方案"))
      util.send_event_str(util.ProgressValue,30)
      #util.close_scene()
      #util.getModuleWidget("JProgressBar")
      self.reload_project()
      self.is_First_Load = False
      util.send_event_str(util.ProgressValue,100)
      return
    
    util.send_event_str(util.ProgressStart,util.tr("正在切换解决方案"))
    util.send_event_str(util.ProgressValue,30)
    util.close_scene()
    util.send_event_str(util.ProgressValue,70)
    self.reload_project()
    util.singleShot(100,lambda:util.send_event_str(util.ProgressValue,100))
    
  def reload_project(self):
    key = util.get_cache_from_PAAA("solution_name","UnitPunctureGuide")
    button_unit = key+"Bottom"
    fra = util.getModuleWidget(button_unit)
    util.addWidgetOnly(self.ui.menu,fra.get_control_panel())
    hard = util.get_cache_from_PAAA("sub_solution_hard","-1")
    if hard == "-1":
      util.save_cache_to_PAAA("sub_solution_hard",2)
    util.getModuleWidget("FrameworkTop").update_title()
    fra.solution_init()
    
    if hard == "-1":
      util.getModuleWidget("FrameworkTop").on_show_menu()
    return

  def OnBackToSolution(self,_a,_b):
    util.send_event_str(util.ProgressStart,util.tr("正在返回原有方案"))
    key = util.get_cache_from_PAAA("solution_name","UnitPunctureGuide")
    button_unit = key+"Bottom"
    fra = util.getModuleWidget(button_unit)
    util.send_event_str(util.ProgressValue,30)
    if fra.old_select_module == '':
      self.OnResetSolution(None, None)
      util.send_event_str(util.ProgressValue,70)
    fra.back_to_solution()
    util.singleShot(100,lambda:util.send_event_str(util.ProgressValue,100))