from __main__ import vtk, slicer
import slicer.util as util
import qt

class JSegmentPanelWithUnit:
 master_node = None
 segment_node = None
 main = None
 uiWidget = None
 ui = None

 editor_panel = None
 editor_template = None
 def __init__(self,main,toollist=["Paint","Draw","Threshold","Scissors","LevelTracing","FillBetweenSlice","Hollow","IslandMax"],callback=None,cancel_callback = None,buttontxt="无") -> None:
  self.main = main
  self.uiWidget = slicer.util.loadUI(self.main.resourcePath('UI/Plugin/JSegmentPanelWithUnit.ui'))
  self.ui = slicer.util.childWidgetVariables(self.uiWidget)
  
  self.editor_panel = self.main.create_tool_panel(None,None,"分割工具",toollist,callback,cancel_callback,buttontxt)
  util.addWidget2(self.ui.container,self.editor_panel.uiWidget)
  
  template =  self.main.get_new_widget()
  template.hide_advance()
  template.set_soft_delete()
  self.editor_template = template
  util.addWidget2(self.ui.widget_3,self.editor_template.widget)
  
  
 def remove_segment_node(self):
  util.RemoveNode(self.segment_node)
  self.segment_node = None

 def init(self,master_node,segment_node):
  self.master_node = master_node
  self.segment_node = segment_node
  self.editor_template.init(segment_node,None,None)
  self.editor_panel.set_info(master_node,segment_node)
  alias_name = segment_node.GetAttribute("alias_name")
  if alias_name:
   self.editor_template.setTitle(alias_name)
  self.main.get_resource_list()