import slicer,qt,os,vtk
import slicer.util as util
from FrameworkLib.ColorUnit import ColorUnit
from FrameworkLib.ColorUnit import TipsUnit
class TipsUnitList:  
  pwidget = None
  m_map = {}
  display_state = True
  def __init__(self,main) -> None:
    self.main = main
    self.uiWidget = slicer.util.loadUI(main.resourcePath('UI/TipsUnitList.ui'))
    self.ui = slicer.util.childWidgetVariables(self.uiWidget)
    
    self.ui.listWidget.setSpacing(0)
    stylesheet = self.ui.listWidget.styleSheet
    stylesheet += "QListWidget::item:selected { border: 0px solid white; }"
    stylesheet += "QListWidget{background-color: transparent;}"
    self.ui.listWidget.setStyleSheet(stylesheet)
    slicer.mrmlScene.AddObserver(util.DisplayModelAlias, self.show_alias)
    slicer.mrmlScene.AddObserver(util.HideModelAlias, self.hide_alias)
    
  @vtk.calldata_type(vtk.VTK_OBJECT)
  def show_alias(self,caller,str_event,calldata):
    print('show_alias')
    self.display_state = True
    for key, value in self.m_map.items():
      key.show_alias()

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def hide_alias(self,caller,str_event,calldata):
    self.display_state = False
    for key, value in self.m_map.items():
      key.hide_alias()
    
  def reinit(self):
    self.m_map={}
    print("color unit list reinit")
    nodes = util.getNodesByClass(util.vtkMRMLMarkupsNode)
    for node in nodes:
      if node.GetAttribute("color_unit") == "1":
        self.add_item(node, 1)
        
    nodes = util.getNodesByClass(util.vtkMRMLModelNode)
    for node in nodes:
      if node.GetAttribute("color_unit") == "1":
        self.add_item(node, 3)
      
    nodes = util.getNodesByClass(util.vtkMRMLSegmentationNode)
    for node in nodes:
      if node.GetAttribute("color_unit") == "1":
        self.add_item(node, 2)
      
    nodes = util.getNodesByClass(util.vtkMRMLScalarVolumeNode)
    for node in nodes:
      self.add_item(node, 4)

  def clear(self):
    self.ui.listWidget.clear()
    
  
  def get_unit_by_node(self,node):
    for template in self.m_map:
      if template.node == node:
        return template
    return None
  
  
    
    
  #type 1: channel; 2: segment 3:model   4:ScalarVolumeNode 
  def add_item(self,node,item_type=1):
    print('add_item list')
    for template in self.m_map:
      if template.node == node:
        return
    node.SetAttribute("color_unit","1")
    template = TipsUnit(self.main, item_type)
    item = qt.QListWidgetItem()
    template.init(self,item)
    template.set_node(node, self.display_state)

    if item_type == 1:
      self.ui.listWidget.insertItem(0, item)
      util.getModuleWidget("UnitScore").create_channel = True
    elif item_type == 4:
      self.ui.listWidget.addItem(item)
      pass
    else:
      self.ui.listWidget.addItem(item)
      alias_name = node.GetAttribute("alias_name")
      if alias_name == "血肿":
        util.getModuleWidget("UnitScore").create_tumor = True
      elif alias_name == "面具":
        util.getModuleWidget("UnitScore").create_mask = True
      elif alias_name == "皮肤":
        util.getModuleWidget("UnitScore").create_skin = True
      elif alias_name == "颅骨":
        util.getModuleWidget("UnitScore").create_bone = True

    self.ui.listWidget.setItemWidget(item,template.uiWidget)
    item.setSizeHint(qt.QSize(540 , 54))
    self.m_map[template] = item
  
  def show(self):
    widget = self.uiWidget
    
    if not self.pwidget:
      self.pwidget = qt.QWidget()
    self.pwidget.setParent(slicer.app.layoutManager().threeDWidget(0).threeDView())
    self.pwidget.setStyleSheet("QWidget{background-color: transparent;}")
    self.pwidget.setAttribute(qt.Qt.WA_TransparentForMouseEvents, True)
    util.addWidget2(self.pwidget,widget)
    
    widget_width = 560
    widget_height = 2000
    geometry = qt.QRect(56,0 ,widget_width,widget_height)
  
    self.pwidget.geometry = geometry
    self.pwidget.show()
    
  def hide(self):
    if self.pwidget:
      self.pwidget.hide()
    
  def remove_by_unit(self,unit):
    for node in self.m_map:
      if node == unit:
        item = self.m_map[node]
        row = self.ui.listWidget.row(item)
        self.ui.listWidget.takeItem(row)
        del self.m_map[node]
        break
    print("remove_by_unit")
    for node in self.m_map:
      print("test remove")

class ColorUnitList:
  status = 0
  m_map = {}
  pwidget = None
  colorlist = []
  display_state = False
  def __init__(self,main) -> None:
    self.main = main
    self.uiWidget = slicer.util.loadUI(main.resourcePath('UI/ColorUnitList.ui'))
    self.ui = slicer.util.childWidgetVariables(self.uiWidget)
    
    self.ui.listWidget.setSpacing(0)
    stylesheet = self.ui.listWidget.styleSheet
    stylesheet += "QListWidget::item:selected { border: 0px solid white; }"
    stylesheet += "QListWidget{background-color: transparent;}"
    self.ui.listWidget.setStyleSheet(stylesheet)

    self.colorlist.append([85,170,255])
    self.colorlist.append([255,170,255])
    self.colorlist.append([85,255,255])
    self.colorlist.append([255,85,255])
    self.colorlist.append([85,85,255])
    self.colorlist.append([255,0,255])
    self.colorlist.append([85,0,255])
    self.colorlist.append([255,255,127])
    self.colorlist.append([85,255,127])
    self.colorlist.append([255,170,127])
    self.colorlist.append([85,170,127])
    self.colorlist.append([255,85,127])
    self.colorlist.append([85,85,127])
    self.colorlist.append([255,0,127])
    self.colorlist.append([85,0,127])
    self.colorlist.append([170,255,255])
    self.colorlist.append([0,255,255])
    self.colorlist.append([170,170,255])
    self.colorlist.append([0,170,255])
    self.colorlist.append([170,85,255])
    self.colorlist.append([0,85,255])
    self.colorlist.append([170,0,255])
    self.colorlist.append([170,255,0])
    self.colorlist.append([170,170,0])
    self.colorlist.append([0,170,0])
    self.colorlist.append([170,85,0])
    self.colorlist.append([0,85,0])
    self.colorlist.append([170,0,0])
  
  def set_node_status(self,node,status):
    for template in self.m_map:
      if template.node == node:
        template.status = status
        template.fresh_status()
        return

  def fresh_node_color(self,node):
    for template in self.m_map:
      if template.node == node:
        template.fresh_display_color()
        return
   
  def get_node_status(self,node):
    for template in self.m_map:
      if template.node == node:
        return template.status
  
  def get_all_units_by_alias_name(self,alias_name):
    arr = []
    for template in self.m_map:
      if template.node:
        if template.node.GetAttribute("alias_name") == alias_name:
          arr.append(template)
    return arr
  
  def get_unit_by_alias_name(self,alias_name):
    for template in self.m_map:
      if template.node:
        if template.node.GetAttribute("alias_name") == alias_name:
          return template
    return None
  
  def get_unique_color(self):
    for color255 in self.colorlist:
      val = False
      for template in self.m_map:
        color = template.color
        if round(color[0]*255) == color255[0] and round(color[1]*255) == color255[1] and round(color[2]*255) == color255[2]:
          val = True
      if not val:
        return [color255[0]/255,color255[1]/255,color255[2]/255]
    return [1,1,1]
  
  def clear(self):
    self.ui.listWidget.clear()
    
  def reinit(self):
    self.m_map={}
    print("color unit list reinit")
    nodes = util.getNodesByClass(util.vtkMRMLMarkupsNode)
    for node in nodes:
      if node.GetAttribute("color_unit") == "1":
        self.add_item(node, 1)
        
    nodes = util.getNodesByClass(util.vtkMRMLModelNode)
    for node in nodes:
      if node.GetAttribute("color_unit") == "1":
        self.add_item(node, 3)
      
    nodes = util.getNodesByClass(util.vtkMRMLSegmentationNode)
    for node in nodes:
      if node.GetAttribute("color_unit") == "1":
        self.add_item(node, 2)
          
    nodes = util.getNodesByClass(util.vtkMRMLScalarVolumeNode)
    for node in nodes:
      self.add_item(node, 4)

  def half_opacity(self):
    for template in self.m_map:
      template.half_opacity()
    
    
  def zero_opacity_by_type(self,type):
    for template in self.m_map:
      if isinstance(template.node,type):
        template.zero_opacity()
  
  def zero_opacity(self):
    for template in self.m_map:
      template.zero_opacity()
      
  def one_opacity(self):
    for template in self.m_map:
      template.one_opacity()
  
  def clear_with_nodes(self):
    for template in self.m_map:
      template._deleteAction()
      
  #type 1: channel; 2: segment 3:model  
  def add_item(self,node,item_type=1):
    for template in self.m_map:
      if template.node == node:
        return
    node.SetAttribute("color_unit","1")
    template = ColorUnit(self.main, item_type)
    item = qt.QListWidgetItem()
    template.init(self,item)
    template.set_node(node, self.display_state)

    if item_type == 1:
      self.ui.listWidget.insertItem(0, item)
    else:
      self.ui.listWidget.addItem(item)
    self.ui.listWidget.setItemWidget(item,template.uiWidget)
    item.setSizeHint(qt.QSize(54 , 54))
    
    self.m_map[template] = item
  
  
  def set_style_to_halfmiddle(self):
    for template in self.m_map:
      template.set_style_to_halfmiddle()
  
  def remove_by_unit(self,unit):
    for node in self.m_map:
      if node == unit:
        item = self.m_map[node]
        row = self.ui.listWidget.row(item)
        self.ui.listWidget.takeItem(row)
        del item
        return
  
  def show(self):
    widget = self.uiWidget
    
    if not self.pwidget:
      self.pwidget = qt.QWidget()
    self.pwidget.setParent(slicer.app.layoutManager().threeDWidget(0).threeDView())
    self.pwidget.setStyleSheet("QWidget{background-color: transparent;}")
    util.addWidget2(self.pwidget,widget)
    
    widget_width = 56
    widget_height = 2000
    geometry = qt.QRect(0,0 ,widget_width,widget_height)
  
    self.pwidget.geometry = geometry
    self.pwidget.show()
    
  def hide(self):
    if self.pwidget:
      self.pwidget.hide()