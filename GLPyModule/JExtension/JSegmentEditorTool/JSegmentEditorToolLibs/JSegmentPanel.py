from __main__ import vtk, slicer
import slicer.util as util
import qt


class JSegmentPanel:
  title = None
  toollist = None
  button_callback = None
  main = None
  uiWidget = None
  ui = None
  button_txt = None
  effect_button_list = {}
  effect_checkable_button_list = {}
  effect_list_widget = {}
  effect_list_ui = {}
  master_node = None
  segment_node = None
  cancel_callback = None
  segmentationNode = None
  def __init__(self,main,master_node,segment_node,title,toollist,button_callback,cancel_callback,button_txt):
    self.title = "title"
    self.toollist = toollist
    self.button_callback = button_callback
    self.main = main
    self.master_node = master_node
    self.segment_node = segment_node
    self.button_txt = button_txt
    self.cancel_callback = cancel_callback
    #self.segmentationNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLSegmentEditorNode")
    #self.segmentationNode.AddObserver(slicer.vtkMRMLSegmentEditorNode.EffectParameterModified, self.updateGUIFromMRML)
    #print(self.segmentationNode.GetID())
    self.init()

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def updateGUIFromMRML(self,caller, event):
    pass

  def init(self):
    self.init_ui()
    self.init_toollist()

  def init_ui(self):
    self.uiWidget = util.loadUI(self.main.resourcePath('UI/JSegmentPanel.ui'))
    self.ui = slicer.util.childWidgetVariables(self.uiWidget)
    self.ui.label.setText(self.title)
    if self.button_callback == None:
      self.ui.extra_button.setVisible(False)
    else:
      self.ui.extra_button.setVisible(True)
      self.ui.extra_button.connect('clicked()',lambda:self.button_callback())
      self.ui.pushButton.connect('clicked()',self.onCancel)
    
    if self.button_txt:
      self.ui.extra_button.setText(self.button_txt)
      
  def onCancel(self):
    res = util.messageBox("确定放弃修改吗",windowTitle=util.tr("提示"))
    if res == 0:
      return
    self.cancel_callback()
    if self.segment_node:
      util.RemoveNode(self.segment_node)
      self.segment_node = None
    

  def cancel(self):
    util.send_event_str(util.SetPage,"1")

  def on_button_clicked(self,key):
    if key == "undo":
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.undo()
    elif key == "redo":
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.redo()
    elif key == "rotate":
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.rotateSliceViewsToSegmentation()
    elif key == "none":
      util.trigger_view_tool("")


  def on_button_toggled(self,btn,is_show,key):
   con = self.ui.tool_paras_container
   if is_show:
    if key == "Draw":
      res = self.main._on_tool_hide_draw(btn,True,self.master_node,self.segment_node)
      self.ui.info.setText("鼠标左键:添加若干点\n按键x:删除选中的点\n双击左键或者点击右键:绘制平面")
      util.addWidgetOnly(con,None)
    elif key == "Paint":
      res = self.main._on_tool_hide_paint(btn,True,self.master_node,self.segment_node,ui=self.effect_list_ui[key])
      if not res:
        self.ui.info.setText("绘制条件不符合")
        util.addWidgetOnly(con,None)
      else:
        self.ui.info.setText("鼠标左键:画感兴趣的区域")
        util.addWidgetOnly(con,self.effect_list_widget[key])
    elif key == "Threshold":
      res = self.main._on_tool_hide_threshold(btn,True,self.master_node,self.segment_node)
      if not res:
        self.ui.info.setText("绘制条件不符合")
        util.addWidgetOnly(con,None)
      else:
        lo, hi = util.GetScalarRange(self.master_node)
        ui = self.effect_list_ui[key]
        ui.thresholdSlider.setRange(lo, hi)
        ui.thresholdSlider.singleStep = (hi - lo) / 1000.
        ui.thresholdSlider.setMaximumValue(hi)
        ui.thresholdSlider.setMinimumValue((hi - lo)/3+lo)
        self.ui.info.setText("调节滑动条,选择需要的阈值区间\n点击确定按钮,确认阈值区间")
        util.addWidgetOnly(con,ui.threshold_paras)
    elif key == "Scissors":
      res = self.master_node is not None and self.segment_node is not None
      if not res:
        self.ui.info.setText("绘制条件不符合")
        util.addWidgetOnly(con,None)
      else:
        self.ui.info.setText("鼠标左键:选择要删除的区域\nESC:取消选择")
        util.addWidgetOnly(con,self.effect_list_widget[key])
        self.effect_list_ui[key].radioButton_2.setChecked(True)
        self.effect_list_ui[key].radioButton.setChecked(True)
    elif key == "LevelTracing":
      res = self.main._on_tool_hide_leveltracing(btn,True,self.master_node,self.segment_node)
      self.ui.info.setText("鼠标移动:自动吸附像素相同的边框\n鼠标左键:确认选择区域")
      util.addWidgetOnly(con,None)
    elif key == "Hollow":
      res = self.main._on_tool_hide_hollow(btn,True,self.master_node,self.segment_node,ui=self.effect_list_ui[key])
      if not res:
        self.ui.info.setText("绘制条件不符合")
        util.addWidgetOnly(con,None)
      else:
        self.ui.info.setText("鼠标左键:轻触决定要镂空的位置")
        util.addWidgetOnly(con,self.effect_list_widget[key])
    elif key == "IslandMax":
      res = self.main._on_tool_hide_islandmax(btn,True,self.master_node,self.segment_node)
      self.ui.info.setText("鼠标点击:保留最大连通域")
      util.addWidgetOnly(con,None)
    elif key == "FillBetweenSlice":
      res = self.main._on_tool_hide_fill_between_slice(btn,True,self.master_node,self.segment_node)
      if not res:
        self.ui.info.setText("绘制条件不符合")
        util.addWidgetOnly(con,None)
      else:
        self.ui.info.setText("使用任何其他效果创建分割。\n只有没有直接相邻切片被分割时，分割才会扩展\n因此不要使用具有绘制效果的球体笔刷\n并且在分割的切片之间始终保留至少一个空切片。\n所有可见线段都将进行插值，而不仅仅是选定线段\n完整的分割将通过在空切片中插入分割来创建。")
        util.addWidgetOnly(con,self.effect_list_widget[key])
   else:
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setActiveEffectByName("None")
  

  def init_paras(self,key):
    if key == "Paint":
      uiWidget = slicer.util.loadUI(self.main.resourcePath('UI/JSegmentPanelSub/%s.ui')%(key))
      ui = slicer.util.childWidgetVariables(uiWidget)
      self.effect_list_widget[key] = uiWidget 
      self.effect_list_ui[key] = ui
      ui.paint_slider.singleStep = 1
      ui.paint_slider.minimum = 1
      ui.paint_slider.maximum = 100
      ui.paint_slider.value = 3
      ui.paint_slider.connect('valueChanged(double)', self.main.on_paint_slider_changed)
      ui.paint_checkbox.connect('stateChanged(int)', self.main.on_sphere_brush)
      ui.paint_slider.setValue(6)
    elif key == "Threshold":
      uiWidget = slicer.util.loadUI(self.main.resourcePath('UI/JSegmentPanelSub/%s.ui')%(key))
      ui = slicer.util.childWidgetVariables(uiWidget)
      self.effect_list_widget[key] = uiWidget 
      self.effect_list_ui[key] = ui
      ui.thresholdSlider.connect('valuesChanged(double,double)', lambda h,l:self.main.onThresholdValuesChanged2(h,l))
      ui.threshold_apply.connect('clicked()',lambda: self.main.on_apply_threshold2())
    elif key == "FillBetweenSlice":
      uiWidget = slicer.util.loadUI(self.main.resourcePath('UI/JSegmentPanelSub/%s.ui')%(key))
      ui = slicer.util.childWidgetVariables(uiWidget)
      self.effect_list_widget[key] = uiWidget 
      self.effect_list_ui[key] = ui
      ui.fill_between_slice_apply.connect('clicked()',self.main.on_fill_between_slice2)
    elif key == "Hollow":
      uiWidget = slicer.util.loadUI(self.main.resourcePath('UI/JSegmentPanelSub/%s.ui')%(key))
      ui = slicer.util.childWidgetVariables(uiWidget)
      self.effect_list_widget[key] = uiWidget 
      self.effect_list_ui[key] = ui
      ui.paint_slider.singleStep = 1
      ui.paint_slider.minimum = 1
      ui.paint_slider.maximum = 100
      ui.paint_slider.value = 3
      ui.paint_slider.connect('valueChanged(double)', self.main.on_hollow_slider_changed)
      ui.paint_slider.setValue(30)
    elif key == "Scissors":
      uiWidget = slicer.util.loadUI(self.main.resourcePath('UI/JSegmentPanelSub/%s.ui')%(key))
      ui = slicer.util.childWidgetVariables(uiWidget)
      self.effect_list_widget[key] = uiWidget 
      self.effect_list_ui[key] = ui
      ui.paint_slider.singleStep = 1
      ui.paint_slider.minimum = 1
      ui.paint_slider.maximum = 100
      ui.paint_slider.value = 3
      ui.paint_slider.connect('valueChanged(double)', self.on_scissor_paint_slider_changed)
      ui.paint_slider.setValue(30)
      ui.paint_slider.setVisible(False)
      ui.radioButton.connect('toggled(bool)',lambda:self.on_scissor_style(1))
      ui.radioButton_2.connect('toggled(bool)',lambda:self.on_scissor_style(2))
      ui.radioButton_3.connect('toggled(bool)',lambda:self.on_scissor_style(3))
      ui.radioButton_4.connect('toggled(bool)',lambda:self.on_scissor_style(4))
  
  def on_scissor_paint_slider_changed(self,value):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    paintEffect = segmentEditorWidget.activeEffect()
    if paintEffect:
      paintEffect.setParameter("BrushAbsoluteDiameter", value)
  
  def on_scissor_style(self,style):
    import slicer
    ui = self.effect_list_ui["Scissors"]
    if style==3:
      ui.paint_slider.setVisible(True)
    else:
      ui.paint_slider.setVisible(False)
    
    if style==1:
      self.main._on_tool_hide_scissors(self.effect_checkable_button_list["Scissors"],True,self.master_node,self.segment_node)
    elif style == 2:
      self.main._on_tool_hide_scissors_circle(self.effect_checkable_button_list["Scissors"],True,self.master_node,self.segment_node)
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
      
  def set_info(self,master_node,segment_node):
    self.master_node = master_node
    self.segment_node = segment_node

    
    

  def init_toollist(self):
    import slicer.util as util
    self.effect_button_list = {}
    self.effect_checkable_button_list = {}
    layout = qt.QHBoxLayout(self.ui.tool_icon_container)
    layout = self.ui.tool_icon_container.layout()
    for key in self.toollist:
      if key == "Draw":
        widget,button = util.getModuleLogic("JUITool").create_labeled_button2("segment_tool_draw.png","钢笔工具:用鼠标左键在二维视图上画一个闭合曲线,算法将自动填充这个闭合曲线",self.main.resourcelist,"钢笔")
      elif key == "Paint":
        widget,button = util.getModuleLogic("JUITool").create_labeled_button2("segment_tool_paint.png","笔刷工具:类似于刷子,可以选择合适的刷子大小和刷子类型",self.main.resourcelist,"笔刷")
      elif key == "Threshold":
        widget,button = util.getModuleLogic("JUITool").create_labeled_button2("segment_tool_threshold.png","阈值工具:会选择灰度值范围在阈值区间的作为目标区域",self.main.resourcelist,"阈值")
      elif key == "Scissors":
        widget,button = util.getModuleLogic("JUITool").create_labeled_button2("segment_tool_scissors.png","删除工具:可以在二维视图和三维视图上选择不需要的区域删除",self.main.resourcelist,"删除")
      elif key == "LevelTracing":
        widget,button = util.getModuleLogic("JUITool").create_labeled_button2("segment_tool_level_tracing.png","魔术棒工具:类似于PS的魔术棒,会选择颜色相近的区域",self.main.resourcelist,"魔术棒")
      elif key == "FillBetweenSlice":
        widget,button = util.getModuleLogic("JUITool").create_labeled_button2("segment_tool_fill_between_slice.png","填充工具:算法将填充相邻的两片区域,补充其中的差值",self.main.resourcelist,"填充")
      elif key == "Hollow":
        widget,button = util.getModuleLogic("JUITool").create_labeled_button2("segment_tool_draw.png","镂空工具：将镂空模型的表面",self.main.resourcelist,"镂空")
      elif key == "IslandMax":
        widget,button = util.getModuleLogic("JUITool").create_labeled_button2("segment_tool_paint.png","最大岛工具:算法将保留最大连通域",self.main.resourcelist,"最大岛")
      button.setCheckable(True)
      util.registe_view_tool(button,key)
      self.effect_checkable_button_list[key] = button
      layout.addWidget(widget)
      self.init_paras(key)
    layout.addStretch(1)
    layout = qt.QHBoxLayout(self.ui.redo_container)

    widget,button = util.getModuleLogic("JUITool").create_labeled_button2("segment_tool_empty.png","取消工具:取消当前选择的工具",self.main.resourcelist,"无")
    layout.addWidget(widget)
    self.effect_button_list["none"] = button
    button.setShortcut(qt.QKeySequence(qt.Qt.Key_Escape))

    widget,button = util.getModuleLogic("JUITool").create_labeled_button2("btn_undo.png","撤销:快捷键ctrl+Z",self.main.resourcelist,"撤销")
    layout.addWidget(widget)
    self.effect_button_list["undo"] = button
    button.setShortcut(qt.QKeySequence("Ctrl+Z"))

    widget,button = util.getModuleLogic("JUITool").create_labeled_button2("btn_redo.png","反撤销:快捷键ctrl+Y",self.main.resourcelist,"反撤销")
    layout.addWidget(widget)
    self.effect_button_list["redo"] = button
    button.setShortcut(qt.QKeySequence("Ctrl+Y"))

    widget,button = util.getModuleLogic("JUITool").create_labeled_button2("segment_tool_rotate.png","矫正工具:将偏斜的影像矫正到合适的位置",self.main.resourcelist,"矫正")
    layout.addWidget(widget)
    self.effect_button_list["rotate"] = button

    for key in self.effect_button_list:
      button = self.effect_button_list[key]
      button.connect('clicked()', lambda v = key:self.on_button_clicked(v))

    for key in self.effect_checkable_button_list:
      button = self.effect_checkable_button_list[key]
      button.connect('toggled(bool)', lambda value,a=key: self.on_button_toggled(button,value,a))
