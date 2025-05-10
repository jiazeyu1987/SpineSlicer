import slicer,qt,vtk
import slicer.util as util

class TipsUnit:
  main = None
  list = None
  item = None
  item_type = 1
  
  def __init__(self,main, item_type) -> None:
    self.uiWidget = slicer.util.loadUI(main.resourcePath('UI/TipsUnit.ui'))
    self.ui = slicer.util.childWidgetVariables(self.uiWidget)
    self.ui.lblInfo.setText("")
    self.item_type = item_type

  def __del__(self):    
    if self.item_type == 4:
      self.node.AddObserver(vtk.vtkCommand.ModifiedEvent, self.on_display_changed)

  def init(self,list1,item):
    self.list = list1
    self.item = item

  def update_fiber_tags(self):
    tips = self.get_fiber_tips(self.node)
    self.ui.lblInfo.setText(tips)

  def set_node(self,node,dispay_state):
    self.node = node
    if self.node.GetAttribute("fiber_unit_type") == "entry_point":
      fiber_model_id = self.node.GetAttribute("fiber_model")
      fiber_model_inner_id = self.node.GetAttribute("fiber_model_inner")
      fiber_model = util.GetNodeByID(fiber_model_id)
      fiber_model_inner = util.GetNodeByID(fiber_model_inner_id)
      if util.GetDisplayNode(fiber_model_inner):
        util.GetDisplayNode(fiber_model_inner).SetVisibility2D(True)
      tips = self.get_fiber_tips(self.node)
      self.ui.lblInfo.setText(tips)
    elif isinstance(self.node,slicer.vtkMRMLSegmentationNode):
      alias_name = self.node.GetAttribute("alias_name")
      self.ui.lblInfo.setText(alias_name)
      if dispay_state:
        self.ui.lblInfo.show()
      else:
        self.ui.lblInfo.hide()
    elif self.item_type == 3:
      alias_name = self.node.GetAttribute("alias_name")
      if alias_name:
        self.ui.lblInfo.setText(alias_name)
      else:
        self.ui.lblInfo.setText('导板')
      if dispay_state:
        self.ui.lblInfo.show()
      else:
        self.ui.lblInfo.hide()
    elif self.item_type == 4:
      self.ui.lblInfo.setText(self.node.GetName())
      self.node.AddObserver(vtk.vtkCommand.ModifiedEvent, self.on_display_changed)
    slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeRemovedEvent, self.on_node_removed)

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def on_display_changed(self, caller, event):
    self.ui.lblInfo.setText(self.node.GetName())
    pass

  def show_alias(self):
    self.ui.lblInfo.show()

  def hide_alias(self):
    if self.item_type != 1:
      self.ui.lblInfo.hide()

  def get_fiber_tips(self,entry_node):
    if entry_node is None or entry_node.GetAttribute("radius_slider") is None :
      return
    radius_slider = int(float(entry_node.GetAttribute("radius_slider"))*10)/10
    thick_slider = int(float(entry_node.GetAttribute("thick_slider"))*10)/10
    length_slider = int(float(entry_node.GetAttribute("length_slider"))*10)/10
    nodelist = []
    key = entry_node.GetAttribute("fiber_unit_id")
    for node in util.get_all_nodes():
      if key == entry_node.GetAttribute("fiber_unit_id"): 
        nodelist.append(node)
    
    target_point = None
    for node in nodelist:
      if node.GetAttribute("fiber_unit_type") == "target_point":
        target_point = node
        break
    
    if not target_point:
      return ""
    
    p1 = util.get_world_position(entry_node)
    p2 = util.get_world_position(target_point)
    import math
    distance = (p1[0] - p2[0])*(p1[0] - p2[0]) + (p1[1] - p2[1])*(p1[1] - p2[1]) + (p1[2] - p2[2])*(p1[2] - p2[2])
    distance = round(math.sqrt(distance),2)
    if float(radius_slider) == float(radius_slider+thick_slider):
      tips = f"入点到靶点距离：{distance} mm"
    else:
      tips = f"入点到靶点距离：{distance} mm"
    
    return tips
    
  @vtk.calldata_type(vtk.VTK_OBJECT)
  def on_node_removed(self, caller, event,calldata):
    if calldata == self.node:
      self.list.remove_by_unit(self)
class ColorUnit:
  status = 0
  list = None
  item = None
  node = None
  #item_type 1: channel; 2: segment 3:model  4：scalevolume
  item_type = 0
  color = [1,1,1]
  volume_cm3 = 0
  main = None
  is_brain_region = False
  blocked = False
  lbl_name = None
  def __init__(self,main, item_type) -> None:
    self.uiWidget = slicer.util.loadUI(main.resourcePath('UI/ColorUnit.ui'))
    self.ui = slicer.util.childWidgetVariables(self.uiWidget)
    self.ui.pushButton.connect('clicked()',self.on_click)
    self.ui.pushButton.setContextMenuPolicy(qt.Qt.CustomContextMenu)
    self.ui.pushButton.customContextMenuRequested.connect(self.showContextMenu)
    self.ui.pushButton.setToolTip("-")
    self.item_type = item_type
    self.main = main
    self.ui.pushButton.setStyleSheet("QToolTip { color: #000000; background-color: #ffffff; border: 0px; }")

  def set_fiber_opacity(self,opacity):
    self.blocked = True
    fiber_model_id = self.node.GetAttribute("fiber_model")
    fiber_model_inner_id = self.node.GetAttribute("fiber_model_inner")
    fiber_unit_id =self.node.GetAttribute("fiber_unit_id")
    fiber_model = util.GetNodeByID(fiber_model_id)
    fiber_model_inner = util.GetNodeByID(fiber_model_inner_id)
    target_point = None
    for nod in util.getNodesByClass(util.vtkMRMLMarkupsNode):
      if nod.GetAttribute("fiber_unit_id") == fiber_unit_id and nod.GetAttribute("fiber_unit_type") == "target_point":
        target_point = nod
        break
    if util.GetDisplayNode(fiber_model_inner):
      util.GetDisplayNode(fiber_model_inner).SetOpacity(opacity)
      util.GetDisplayNode(fiber_model_inner).SetSliceIntersectionOpacity(opacity)
    if util.GetDisplayNode(fiber_model):
      util.GetDisplayNode(fiber_model).SetOpacity(opacity)
      util.GetDisplayNode(fiber_model).SetSliceIntersectionOpacity(opacity)
    if util.GetDisplayNode(self.node):
      util.GetDisplayNode(self.node).SetOpacity(opacity)
    if util.GetDisplayNode(target_point):
      util.GetDisplayNode(target_point).SetOpacity(opacity)
    self.blocked = False

  def set_headframe_opacity(self,val):
    pass

  def set_node_opacity(self,val):
    self.blocked = True
    if isinstance(self.node,slicer.vtkMRMLModelNode):
      util.GetDisplayNode(self.node).SetOpacity(val/100)
      util.GetDisplayNode(self.node).SetSliceIntersectionOpacity(val/100)
    elif isinstance(self.node,slicer.vtkMRMLSegmentationNode):
      util.GetDisplayNode(self.node).SetOpacity3D(val/100)
      util.GetDisplayNode(self.node).SetOpacity2DFill(val/100)
      util.GetDisplayNode(self.node).SetOpacity2DOutline(val/100)
    self.blocked = False

  def set_fiber_length(self,val):
    util.getModuleWidget("UnitCreateChannel").set_unit_length(self.node,val)
    tipunit = util.tips_unit_list.get_unit_by_node(self.node)
    if tipunit:
      tipunit.update_fiber_tags()
      
  def set_fiber_length2(self,val):
    util.getModuleWidget("UnitCreateSingleChannel").set_unit_length(self.node,val)
    tipunit = util.tips_unit_list.get_unit_by_node(self.node)
    if tipunit:
      tipunit.update_fiber_tags()
      
  def set_fiber_thick(self,val):
    util.getModuleWidget("UnitCreateChannel").set_unit_thick(self.node,val)
    tipunit = util.tips_unit_list.get_unit_by_node(self.node)
    if tipunit:
      tipunit.update_fiber_tags()
      
  def set_fiber_radius(self,val):
    util.getModuleWidget("UnitCreateChannel").set_unit_radius(self.node,val)
    tipunit = util.tips_unit_list.get_unit_by_node(self.node)
    if tipunit:
      tipunit.update_fiber_tags()
      
  def set_fiber_radius2(self,val):
    util.getModuleWidget("UnitCreateSingleChannel").set_unit_radius(self.node,val)
    tipunit = util.tips_unit_list.get_unit_by_node(self.node)
    if tipunit:
      tipunit.update_fiber_tags()

  def get_volume(self):
    volume = util.getFirstNodeByClassByAttribute(util.vtkMRMLScalarVolumeNode,"main_node","1")
    return volume
  
  def on_scissors(self):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(self.node)
    segmentEditorWidget.setSourceVolumeNode(self.get_volume())
    
    sid = util.GetNthSegmentID(self.node,0)
    segmentEditorWidget.setCurrentSegmentID(sid)
        
    segmentEditorWidget.setActiveEffectByName("Scissors")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("EditIn3DViews", 1)
    effect.setParameter("Shape", "FreeForm")
    effect.setParameter("Operation", "EraseInside")
  
  def on_smooth(self):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(self.node)
    segmentEditorWidget.setSourceVolumeNode(self.get_volume())
    sid = util.GetNthSegmentID(self.node,0)
    segmentEditorWidget.setCurrentSegmentID(sid)
    segmentEditorWidget.setActiveEffectByName("Smoothing")
    effect = segmentEditorWidget.activeEffect()
    effect.self().onApply()
  
  def showContextMenu(self,position):
    
    util.trigger_view_tool("")
    contextMenu = qt.QMenu(self.uiWidget)
    deleteAct =  qt.QAction('删除', self.uiWidget)
    
    
    sliderAction = qt.QWidgetAction(contextMenu)
    uiWidget = slicer.util.loadUI(self.main.resourcePath('UI/ContextSlider.ui'))     
    ui = slicer.util.childWidgetVariables(uiWidget)
    ui.SliderWidget.singleStep = 1
    ui.SliderWidget.minimum = 0
    ui.SliderWidget.maximum = 100
    opacity = util.GetDisplayNode(self.node).GetOpacity()
    ui.SliderWidget.value = int(opacity*100)
    
    # if self.node.GetAttribute("fiber_unit_type") == "entry_point":
    #   ui.SliderWidget.connect("valueChanged(double)", self.set_fiber_opacity)
    # elif self.node.GetAttribute("is_head_frame") == "1":
    #   ui.SliderWidget.connect("valueChanged(double)", self.set_headframe_opacity)
    # else:
    #   ui.SliderWidget.connect("valueChanged(double)", self.set_node_opacity)
    #ui.SliderWidget.decimals = 0
    #ui.label.setText("透明度：")
    #sliderAction.setDefaultWidget(uiWidget)
      
        
    
    if self.item_type == 4:      
      modifyNameAct =  qt.QWidgetAction(contextMenu)
      uiWidget2 = slicer.util.loadUI(self.main.resourcePath('UI/ContextLineEditor.ui'))     
      ui2 = slicer.util.childWidgetVariables(uiWidget2)
      ui2.lblName.setText(self.node.GetName())
      self.lbl_name = ui2.lblName
      ui2.lblName.connect("editingFinished()", self.set_node_name)
      modifyNameAct.setDefaultWidget(uiWidget2)
      contextMenu.addAction(modifyNameAct)
      pass
    else:
      colorAct =  qt.QAction('颜色', self.uiWidget)      
      colorAct.triggered.connect(self.colorAction)
      #contextMenu.addAction(sliderAction)
      contextMenu.addAction(colorAct)
      
      colorAct =  qt.QAction('修剪', self.uiWidget)      
      colorAct.triggered.connect(self.on_scissors)
      contextMenu.addAction(colorAct)
      
      colorAct =  qt.QAction('平滑', self.uiWidget)      
      colorAct.triggered.connect(self.on_smooth)
      contextMenu.addAction(colorAct)
    
    
    if self.node.GetAttribute("fiber_unit_type") == "entry_point":
      contextMenu.addSeparator()
      directionAct1 =  qt.QAction('导管视角', self.uiWidget)
      contextMenu.addAction(directionAct1)
      directionAct2 =  qt.QAction('普通视角', self.uiWidget)
      contextMenu.addAction(directionAct2)
      # directionAct3 =  qt.QAction('显示参数', self.uiWidget)
      # contextMenu.addAction(directionAct3)
      # directionAct4 =  qt.QAction('关闭参数', self.uiWidget)
      # contextMenu.addAction(directionAct4)
      modifyAction =  qt.QAction('修改位置', self.uiWidget)
      modifyAction.setCheckable(True)
      contextMenu.addAction(modifyAction)
      directionAct1.triggered.connect(self.directionAct1)
      directionAct2.triggered.connect(self.directionAct2)
      modifyAction.triggered.connect(self.directionAct5)
      #directionAct3.triggered.connect(self.directionAct3)
      #directionAct4.triggered.connect(self.directionAct4)
      entry_node = self.node
      dd = util.GetDisplayNode(entry_node).GetHandlesInteractive()
      if dd:
        modifyAction.setChecked(True)
      else:
        modifyAction.setChecked(False)

      if float(self.node.GetAttribute("thick_slider"))!=0:
      
        #设置长度
        sliderAction = qt.QWidgetAction(contextMenu)
        uiWidget = slicer.util.loadUI(self.main.resourcePath('UI/ContextSlider.ui'))     
        ui = slicer.util.childWidgetVariables(uiWidget)
        ui.SliderWidget.singleStep = 0.1
        ui.SliderWidget.minimum = 0
        ui.SliderWidget.maximum = 300
        val = self.node.GetAttribute("length_slider")
        if val:
          ui.SliderWidget.value = int(float(val))
        ui.SliderWidget.connect("valueChanged(double)", self.set_fiber_length)
        ui.SliderWidget.decimals = 1
        ui.label.setText("长度:")
        sliderAction.setDefaultWidget(uiWidget)
        #contextMenu.addAction(sliderAction)
        
        #设置厚度
        sliderAction = qt.QWidgetAction(contextMenu)
        uiWidget = slicer.util.loadUI(self.main.resourcePath('UI/ContextSlider.ui'))     
        ui = slicer.util.childWidgetVariables(uiWidget)
        ui.SliderWidget.singleStep = 0.1
        ui.SliderWidget.minimum = 0
        ui.SliderWidget.maximum = 10
        val = self.node.GetAttribute("thick_slider")
        if val:
          ui.SliderWidget.value = int(float(val))
        ui.SliderWidget.connect("valueChanged(double)", self.set_fiber_thick)
        ui.SliderWidget.decimals = 1
        ui.label.setText("厚度:")
        sliderAction.setDefaultWidget(uiWidget)
        #contextMenu.addAction(sliderAction)
        
        #设置直径
        sliderAction = qt.QWidgetAction(contextMenu)
        uiWidget = slicer.util.loadUI(self.main.resourcePath('UI/ContextSlider.ui'))     
        ui = slicer.util.childWidgetVariables(uiWidget)
        ui.SliderWidget.singleStep = 0.1
        ui.SliderWidget.minimum = 0
        ui.SliderWidget.maximum = 10
        val = self.node.GetAttribute("radius_slider")
        if val:
          ui.SliderWidget.value = int(float(val))
        ui.SliderWidget.connect("valueChanged(double)", self.set_fiber_radius)
        ui.SliderWidget.decimals = 1
        ui.label.setText("直径:")
        sliderAction.setDefaultWidget(uiWidget)
        #contextMenu.addAction(sliderAction)
        
      else:
        
        #设置长度
        sliderAction = qt.QWidgetAction(contextMenu)
        uiWidget = slicer.util.loadUI(self.main.resourcePath('UI/ContextSlider.ui'))     
        ui = slicer.util.childWidgetVariables(uiWidget)
        ui.SliderWidget.singleStep = 0.1
        ui.SliderWidget.minimum = 0
        ui.SliderWidget.maximum = 300
        val = self.node.GetAttribute("length_slider")
        if val:
          ui.SliderWidget.value = int(float(val))
        ui.SliderWidget.connect("valueChanged(double)", self.set_fiber_length2)
        ui.SliderWidget.decimals = 1
        ui.label.setText("长度:")
        sliderAction.setDefaultWidget(uiWidget)
        #contextMenu.addAction(sliderAction)
        
        
        #设置直径
        sliderAction = qt.QWidgetAction(contextMenu)
        uiWidget = slicer.util.loadUI(self.main.resourcePath('UI/ContextSlider.ui'))     
        ui = slicer.util.childWidgetVariables(uiWidget)
        ui.SliderWidget.singleStep = 0.1
        ui.SliderWidget.minimum = 0
        ui.SliderWidget.maximum = 100
        val = self.node.GetAttribute("radius_slider")
        if val:
          ui.SliderWidget.value = int(float(val))
        ui.SliderWidget.connect("valueChanged(double)", self.set_fiber_radius2)
        ui.SliderWidget.decimals = 1
        ui.label.setText("直径:")
        sliderAction.setDefaultWidget(uiWidget)
        #contextMenu.addAction(sliderAction)
    elif self.node.GetAttribute("is_head_frame") == "1":
      ui.widget_2.setVisible(False)    
      

    deleteAct.triggered.connect(self.deleteAction)
    contextMenu.addAction(deleteAct)
    contextMenu.exec_(self.ui.pushButton.mapToGlobal(position))

  def set_node_name(self):
    tmp_name = self.lbl_name.text
    print("whm test set_node_name",tmp_name, self.node.GetName())
    if tmp_name == "" or tmp_name == self.node.GetName():
      return
    self.node.SetName(tmp_name)
    pass

  def directionAct1(self):
    target_point = None
    fiber_unit_id =self.node.GetAttribute("fiber_unit_id")
    for nod in util.getNodesByClass(util.vtkMRMLMarkupsNode):
      if nod.GetAttribute("fiber_unit_id") == fiber_unit_id and nod.GetAttribute("fiber_unit_type") == "target_point":
        target_point = nod
        break
    entry_point_world = [0,0,0]
    self.node.GetNthControlPointPositionWorld(0, entry_point_world)
    target_point_world = [0,0,0]
    target_point.GetNthControlPointPositionWorld(0, target_point_world)
    util.singleShot(0,lambda:util.getModuleLogic("JTransformTool").rotate_to_vector(entry_point_world[0],entry_point_world[1],entry_point_world[2],target_point_world[0],target_point_world[1],target_point_world[2]))
  
  def directionAct5(self):
    entry_node = self.node
    target_node = self.get_target_node(entry_node)
    dd = util.GetDisplayNode(entry_node).GetHandlesInteractive()
    if dd:
      #util.GetDisplayNode(entry_node).SetHandlesInteractive(False)
      entry_node.SetLocked(True)
      util.HideNode(entry_node)
      
      if target_node:
        #util.GetDisplayNode(target_node).SetHandlesInteractive(False)
        target_node.SetLocked(True)
        util.HideNode(target_node)
    else:
      
      #util.GetDisplayNode(entry_node).SetHandlesInteractive(True)
      entry_node.SetLocked(False)
      util.ShowNode(entry_node)
      
      if target_node:
        #util.GetDisplayNode(target_node).SetHandlesInteractive(True)
        target_node.SetLocked(False)
        util.ShowNode(target_node)
      self.half_opacity()
  
  def get_target_node(self,entry_node):
    nodelist = []
    key = entry_node.GetAttribute("fiber_unit_id")
    for node in util.get_all_nodes():
      if key == node.GetAttribute("fiber_unit_id"): 
        nodelist.append(node)
    
    target_point = None
    for node in nodelist:
      if node.GetAttribute("fiber_unit_type") == "target_point":
        target_point = node
        break
    return target_point
  
  def directionAct2(self):
    util.reinitForce()

  def directionAct4(self):
    entry_node = self.node
    util.GetDisplayNode(entry_node).SetPointLabelsVisibility(False)
    
  def directionAct3(self):
    entry_node = self.node
    entry_node.SetNthFiducialLabel(0,"a")
    util.GetDisplayNode(entry_node).SetPointLabelsVisibility(True)

  def deleteAction(self):
    res = util.messageBox("确定删除吗",windowTitle=util.tr("提示"))
    if res == 0:
      return
    self._deleteAction()
    
  def _deleteAction(self):
    if self.node.GetAttribute("fiber_unit_type") == "entry_point":
      fiber_model_id = self.node.GetAttribute("fiber_model")
      fiber_model_inner_id = self.node.GetAttribute("fiber_model_inner")
      fiber_unit_id =self.node.GetAttribute("fiber_unit_id")
      fiber_model = util.GetNodeByID(fiber_model_id)
      fiber_model_inner = util.GetNodeByID(fiber_model_inner_id)
      target_point = None
      for nod in util.getNodesByClass(util.vtkMRMLMarkupsNode):
        if nod.GetAttribute("fiber_unit_id") == fiber_unit_id and nod.GetAttribute("fiber_unit_type") == "target_point":
          target_point = nod
          break
      if fiber_model:
        transform_node_id = fiber_model.GetTransformNodeID()
        transform_node = util.GetNodeByID(transform_node_id)
      util.getModuleWidget("UnitCreateChannel").on_delete()
      util.RemoveNode(fiber_model)
      util.RemoveNode(fiber_model_inner)
      util.RemoveNode(target_point)
      util.RemoveNode(self.node)
      util.RemoveNode(transform_node)
    elif self.node.GetAttribute("is_head_frame") == "1":
      nodes = util.getNodeByAttribute("is_head_frame","1")
      for node in nodes:
        util.RemoveNode(node)
    else:
      util.RemoveNode(self.node)
    self.list.remove_by_unit(self)
    
    
  def colorAction(self):
      qdialog = qt.QColorDialog()
      qdialog.connect('colorSelected(QColor)', self.on_get_color)
      qdialog.installEventFilter(slicer.util.mainWindow())
      qdialog.exec()
  def on_get_color(self,qcolor):
    self.color = [qcolor.red()/255.0,qcolor.green()/255.0,qcolor.blue()/255.0]

    if self.node.GetAttribute("fiber_unit_type") == "entry_point":
      fiber_model_id = self.node.GetAttribute("fiber_model")
      fiber_model = util.GetNodeByID(fiber_model_id)
      util.GetDisplayNode(fiber_model).SetColor([qcolor.red()/255.0,qcolor.green()/255.0,qcolor.blue()/255.0])
    elif isinstance(self.node,slicer.vtkMRMLModelNode):
      display_node = util.GetDisplayNode(self.node)
      display_node.SetColor([qcolor.red()/255.0,qcolor.green()/255.0,qcolor.blue()/255.0])
    elif isinstance(self.node,slicer.vtkMRMLSegmentationNode):
      segment = util.GetNthSegment(self.node,0)
      segment.SetColor([qcolor.red()/255.0,qcolor.green()/255.0,qcolor.blue()/255.0])
    self.fresh_status()

  def on_click(self):
    print("On Click Color Unit:",self.node.GetID())
    self.status+=1
    if self.status == 1 and isinstance(self.node,slicer.vtkMRMLScalarVolumeNode):
      self.status = 2
    self.node.SetAttribute("color_unit_status",f"{self.status}")
    if self.status > 2:
      self.status = 0
    self.fresh_status()
    
  def fresh_status(self):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setActiveEffectByName(None)
    segmentEditorWidget.setSegmentationNode(None)
    tmp_display_node = util.GetDisplayNode(self.node)
    if tmp_display_node == None:
      return
    self.ui.pushButton.setText("")
    if self.status < 0 or self.status > 2:
      self.status = 1
    
    if self.node.GetAttribute("alias_name") == "皮肤":
      svg_path = f"Icons/color_skin_{self.status+1}.svg"
    elif self.node.GetAttribute("alias_name") == "颅骨":
      svg_path = f"Icons/color_bone_{self.status+1}.svg"
    elif self.node.GetAttribute("alias_name") == "血肿":
      svg_path = f"Icons/color_tumor_{self.status+1}.svg"
    elif self.node.GetAttribute("alias_name") == "头架":
      svg_path = f"Icons/color_frame_{self.status+1}.svg"
    else:
      svg_path = f"Icons/color_fiber_{self.status+1}.svg"
      
      
    # if self.item_type == 2:
    #   svg_path = f"Icons/color_seg_{self.status+1}.svg"
    #   if self.is_brain_region:
    #     svg_path = f"Icons/color_brain_{self.status+1}.svg"

    # if self.item_type == 3:
    #   svg_path = f"Icons/color_model_{self.status+1}.svg"
    if self.item_type == 4:
      svg_path = f"Icons/color_volume_{self.status+1}.svg"
    svg_full_path = self.main.resourcePath(svg_path)
    save_path = "bin/tmp/color.png"
    util.getModuleWidget("SVGT").ChangeColor(svg_full_path,self.ui.pushButton,qt.QColor(self.color[0]*255,self.color[1]*255,self.color[2]*255))
    #self.ui.pushButton.setIcon(qt.QIcon(save_path))
    self.ui.pushButton.setIconSize(qt.QSize(24, 24))
    if self.node.GetAttribute("fiber_unit_type") == "entry_point":
      opacity = 0
      if self.status == 2:
        opacity = 0
      if self.status == 1:
        opacity = 0.3
      if self.status == 0:
        opacity = 1
        
      fiber_model_id = self.node.GetAttribute("fiber_model")
      fiber_model_inner_id = self.node.GetAttribute("fiber_model_inner")
      fiber_unit_id =self.node.GetAttribute("fiber_unit_id")
      fiber_model = util.GetNodeByID(fiber_model_id)
      fiber_model_inner = util.GetNodeByID(fiber_model_inner_id)
      target_point = None
      for nod in util.getNodesByClass(util.vtkMRMLMarkupsNode):
        if nod.GetAttribute("fiber_unit_id") == fiber_unit_id and nod.GetAttribute("fiber_unit_type") == "target_point":
          target_point = nod
          break
        
      
      if util.GetDisplayNode(fiber_model_inner):
        util.GetDisplayNode(fiber_model_inner).SetOpacity(opacity)
        util.GetDisplayNode(fiber_model_inner).SetSliceIntersectionOpacity(opacity)
      if util.GetDisplayNode(fiber_model):
        util.GetDisplayNode(fiber_model).SetOpacity(opacity)
        util.GetDisplayNode(fiber_model).SetSliceIntersectionOpacity(opacity)
      if util.GetDisplayNode(self.node):
        util.GetDisplayNode(self.node).SetOpacity(1)
      if util.GetDisplayNode(target_point):
        util.GetDisplayNode(target_point).SetOpacity(1)
    elif self.node.GetAttribute("is_head_frame") == "1":
      modelist = util.getNodeByAttribute("is_head_frame","1")
      for model in modelist:
              if self.status == 2:
                opacity = 0
                util.GetDisplayNode(model).SetOpacity(opacity)
                util.GetDisplayNode(model).SetSliceIntersectionOpacity(opacity)
              if self.status == 1:
                opacity = 0.3
                util.GetDisplayNode(model).SetOpacity(opacity)
                util.GetDisplayNode(model).SetSliceIntersectionOpacity(opacity)
              if self.status == 0:
                util.GetDisplayNode(model).SetOpacity(1)
                util.GetDisplayNode(model).SetSliceIntersectionOpacity(1)
    elif isinstance(self.node,slicer.vtkMRMLModelNode):
      if self.status == 2:
        opacity = 0
        util.GetDisplayNode(self.node).SetOpacity(opacity)
        util.GetDisplayNode(self.node).SetSliceIntersectionOpacity(opacity)
      if self.status == 1:
        opacity = 0.3
        util.GetDisplayNode(self.node).SetOpacity(opacity)
        util.GetDisplayNode(self.node).SetSliceIntersectionOpacity(opacity)
      if self.status == 0:
        util.GetDisplayNode(self.node).SetOpacity(1)
        util.GetDisplayNode(self.node).SetSliceIntersectionOpacity(1)
    elif isinstance(self.node,slicer.vtkMRMLSegmentationNode):
      if self.status == 2:        
        opacity = 0
        if self.is_brain_region:
          opacity = 0.01
        util.GetDisplayNode(self.node).SetOpacity3D(0)
        util.GetDisplayNode(self.node).SetOpacity2DFill(opacity)
        util.GetDisplayNode(self.node).SetOpacity2DOutline(opacity)
      if self.status == 1:
        opacity = 0.3
        if self.is_brain_region:
          opacity = 0.3
        util.GetDisplayNode(self.node).SetOpacity3D(opacity)
        util.GetDisplayNode(self.node).SetOpacity2DFill(opacity)
        util.GetDisplayNode(self.node).SetOpacity2DOutline(opacity)
      if self.status == 0:
        util.GetDisplayNode(self.node).SetOpacity3D(1)
        util.GetDisplayNode(self.node).SetOpacity2DFill(1)
        util.GetDisplayNode(self.node).SetOpacity2DOutline(1)
    elif isinstance(self.node,slicer.vtkMRMLScalarVolumeNode):
      if self.status == 0:
        self.showVolumeRendering(self.node, True)
        pass
      else:
        self.showVolumeRendering(self.node, False)
        pass
      if self.status == 1:
        self.status = 2
        pass
      pass
    else:
      raise Exception("unsupport sdfsdfsdfsdf")

  def showVolumeRendering(self,volumeNode,boolval):
    print("Show volume rendering of node " + volumeNode.GetName())
    volRenLogic = slicer.modules.volumerendering.logic()
    displayNode = volRenLogic.CreateDefaultVolumeRenderingNodes(volumeNode)
    displayNode.SetVisibility(boolval)
    util.reinit3D()

  def set_size(self,size):
    pass
  
  def get_model_tips(self,node):
    polyData = node.GetPolyData()
    # 创建vtkMassProperties对象
    massProperties = vtk.vtkMassProperties()
    massProperties.SetInputData(polyData)
    massProperties.Update()
    # 获取模型的表面积和体积
    surfaceArea = massProperties.GetSurfaceArea()
    self.volume_cm3 = massProperties.GetVolume()
    tips =   f"体积 = {round(self.volume_cm3/1000,2)} cm3\n表面积 = {round(surfaceArea/100,2)} cm2"
    return tips
  
  def get_segment_tips(self,segmentationNode):
    import SegmentStatistics
    segStatLogic = SegmentStatistics.SegmentStatisticsLogic()
    segStatLogic.getParameterNode().SetParameter("Segmentation", segmentationNode.GetID().__str__())
    segStatLogic.computeStatistics()
    stats = segStatLogic.getStatistics()

    # Display volume of each segment
    for segmentId in stats["SegmentIDs"]:
      volume_cm3 = stats[segmentId,"LabelmapSegmentStatisticsPlugin.volume_cm3"]
      self.volume_cm3 = volume_cm3
      tips =   f"体积 = {round(volume_cm3,2)} cm3"
      return tips
  
  def half_opacity(self):
    if isinstance(self.node, slicer.vtkMRMLScalarVolumeNode):
      return
    if self.status == 0:
      self.status = 1
    self.fresh_status()
    
  def zero_opacity(self):
    self.status = 2
    self.fresh_status()
    
  def one_opacity(self):
    self.status = 0
    self.fresh_status()
  
  def get_fiber_tips(self,entry_node):
    if entry_node is None or entry_node.GetAttribute("radius_slider") is None :
      return "通道1"
    radius_slider = float(entry_node.GetAttribute("radius_slider"))
    thick_slider = float(entry_node.GetAttribute("thick_slider"))
    length_slider = float(entry_node.GetAttribute("length_slider"))
    nodelist = []
    key = entry_node.GetAttribute("fiber_unit_id")
    for node in util.get_all_nodes():
      if key == entry_node.GetAttribute("fiber_unit_id"): 
        nodelist.append(node)
    
    target_point = None
    for node in nodelist:
      if node.GetAttribute("fiber_unit_type") == "target_point":
        target_point = node
        break
    
    if not target_point:
      return "通道2"
    
    p1 = util.get_world_position(entry_node)
    p2 = util.get_world_position(target_point)
    import math
    distance = (p1[0] - p2[0])*(p1[0] - p2[0]) + (p1[1] - p2[1])*(p1[1] - p2[1]) + (p1[2] - p2[2])*(p1[2] - p2[2])
    distance = round(math.sqrt(distance),2)
    if float(radius_slider) == float(radius_slider+thick_slider):
      tips = f"入点到靶点距离：{distance} mm"
    else:
      tips = f"入点到靶点距离：{distance} mm"
    
    return tips
  
  def set_style_to_halfmiddle(self):
    if isinstance(self.node,slicer.vtkMRMLScalarVolumeNode): 
      return
    if self.status == 0:
      self.status = 1
      self.fresh_status()
  
  def set_node(self,node,dispay_state):
    self.alias_display_state = dispay_state
    self.node = node
    if self.node.GetAttribute("fiber_unit_type") == "entry_point":
      fiber_model_id = self.node.GetAttribute("fiber_model")
      fiber_model_inner_id = self.node.GetAttribute("fiber_model_inner")
      fiber_model = util.GetNodeByID(fiber_model_id)
      fiber_model_inner = util.GetNodeByID(fiber_model_inner_id)
      if util.GetDisplayNode(fiber_model_inner):
        util.GetDisplayNode(fiber_model_inner).SetVisibility2D(True)
      tips = self.get_fiber_tips(self.node)
      self.ui.pushButton.setToolTip(tips)
    elif isinstance(self.node,slicer.vtkMRMLModelNode):
      util.GetDisplayNode(node).AddObserver(vtk.vtkCommand.ModifiedEvent, self.on_node_modfied)
      tips = self.get_model_tips(self.node)
      self.ui.pushButton.setToolTip(tips)
    elif isinstance(self.node,slicer.vtkMRMLSegmentationNode):
      segment = util.GetNthSegment(self.node,0)
      if segment:
        segment.AddObserver(vtk.vtkCommand.ModifiedEvent, self.on_node_modfied)
      tips = self.get_segment_tips(self.node)
      self.ui.pushButton.setToolTip(tips)
      alias_name = self.node.GetAttribute("alias_name")
      if alias_name == "脑功能区":
        self.is_brain_region = True
      else:
        node.AddObserver(vtk.vtkCommand.AnyEvent, self.on_node_event_change)
    elif self.node.GetAttribute("is_head_frame") == "1":
      pass
    elif isinstance(self.node,slicer.vtkMRMLScalarVolumeNode):
      tips = self.node.GetName()
      self.ui.pushButton.setToolTip(tips)
      self.get_display_state()
      self.fresh_status()
      volRenLogic = slicer.modules.volumerendering.logic()
      display_node = volRenLogic.CreateDefaultVolumeRenderingNodes(self.node)
      display_node.AddObserver(vtk.vtkCommand.ModifiedEvent, self.on_node_modfied)
      pass
    else:
      raise Exception("unsupport lsdkfjlskdjflsdkjfslkdjf")
    
    slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeRemovedEvent, self.on_node_removed)
    self.on_node_modfied("","")
    
    color_unit_status = self.node.GetAttribute("color_unit_status")
    if color_unit_status:
      self.status = int(color_unit_status)
      self.fresh_status()

  def onSegmentationNodeEvent(self, caller, eventId):
    print(f"Event ID: {eventId}")  
      
  def set_value(self,value):
    self.ui.label_6.setText(value)
    
  def init(self,list1,item):
    self.list = list1
    self.item = item
  
  def fresh_display_color(self):
    self.on_node_modfied(None, None)

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def on_node_removed(self, caller, event,calldata):
    if calldata == self.node:
      self.list.remove_by_unit(self)
    
    
  def on_node_event_change(self, caller=None, event=None):
    if event == "NoEvent":
      return
    print(f"Event ID: {event}")
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    if segmentEditorWidget == None:
      return
    referenceID = segmentEditorWidget.segmentationNodeID()
    if referenceID != self.node.GetID():
      return
    tips = self.get_segment_tips(self.node)
    self.ui.pushButton.setToolTip(tips)
    pass

  def on_node_modfied(self, caller=None, event=None):
    print("on_node_modified", event)
    if self.blocked:
      return
    if self.node.GetAttribute("fiber_unit_type") == "entry_point":
      fiber_model_id = self.node.GetAttribute("fiber_model")
      fiber_model = util.GetNodeByID(fiber_model_id)
      display_node = util.GetDisplayNode(fiber_model)
      if display_node:
        self.color = display_node.GetColor()
        self.fresh_status()
    elif isinstance(self.node,slicer.vtkMRMLModelNode):
      display_node = util.GetDisplayNode(self.node)
      self.color = display_node.GetColor()
      self.fresh_status()
    elif isinstance(self.node,slicer.vtkMRMLSegmentationNode):      
      segment = util.GetNthSegment(self.node,0)
      if segment:
        self.color = segment.GetColor()
        self.fresh_status()
      tips = self.get_segment_tips(self.node)
      self.ui.pushButton.setToolTip(tips)
    elif isinstance(self.node,slicer.vtkMRMLLabelMapVolumeNode): 
      pass
    elif isinstance(self.node,slicer.vtkMRMLScalarVolumeNode):   
      self.get_display_state()
      self.fresh_status()
      pass
    else:
      raise Exception("unsupport asdgagsdfsdfsdfsdf")

  def get_display_state(self):
    display_node1 = util.GetDisplayNode(self.node)
    volRenLogic = slicer.modules.volumerendering.logic()
    display_node = volRenLogic.CreateDefaultVolumeRenderingNodes(self.node)
    vis = display_node.GetVisibility()
    vis1 = display_node1.GetVisibility()
    self.status = 2
    if vis and vis1:
      self.status = 0
