from __main__ import vtk, slicer
import slicer.util as util
import qt

class Unit_Template:
  node = None
  ui = None
  main = None
  widget = None
  def __init__(self,main,in_ui,widget) -> None:
    self.ui = in_ui
    self.main = main
    self.widget = widget

class Unit_Normal(Unit_Template):
  manager = None
  item = None
  paras = {}
  soft_delete = None
  def __init__(self, main,in_ui,widget) -> None:
    super().__init__(main,in_ui,widget)

  def init(self,node,manager,item):
    self.manager = manager
    self.shrink()
    if node == self.node:
      return
    self.node = node
    self.item = item
    self.main.create_btn2D(node,self.ui.btn2D)
    self.main.create_btn3D(node,self.ui.btn3D)
    self.main.create_btnPalette(node,self.ui.btnPalette)
    self.main.create_slider3D(node,self.ui.horizontalSlider3D)
    self.main.create_btnDelete(self,self.manager,node,self.ui.btnDelete)
    self.main.create_advance(self,self.manager,node,self.ui.btnAdvance)
    self.main.create_toollist(self,self.manager,node,self.ui.comboBox)
    #self.main.create_redoundo(self.ui.btnUndo,self.ui.btnRedo)
    self.ui.tabWidget.tabBar().hide()
    self.ui.tabWidget.setCurrentIndex(0)
    self.ui.lineEdit.disconnect('textChanged(QString)')
    self.ui.lineEdit.connect('textChanged(QString)',self.on_textchanged)
  
  def remove_node(self,node):
    util.trigger_view_tool("")
    if self.soft_delete is None:
      util.RemoveNode(node)
    else:
      util.RemoveNthSegmentIDSoft(node,0)

  def on_textchanged(self,val):
    if self.node:
      self.node.SetAttribute("alias_name",val)

  def setTitle(self,title):
    self.ui.lineEdit.setText(title)

  def shrink(self):
    self.ui.widget_2.setVisible(False)
    self.ui.Main.setFixedHeight(111)

  def expand(self):
    self.ui.widget_2.setVisible(True)
    self.ui.Main.setFixedHeight(340)

  '''
    隐藏高级功能,防止重复的功能
  '''
  def hide_advance(self):
    self.ui.btnAdvance.setVisible(False)

  '''
    软删除:只清除内容,不删除节点
  '''
  def set_soft_delete(self):
    self.soft_delete = 1

class SegmentManager:
  #SegmentManager 对应的 UI
  m_ui = None
  #ROI相关参数
  m_SegmentationList = []
  m_SegmentationMax = 10
  m_SegmentColorList = [[255,10,10],[10,255,255],[255,255,10],[10,255,10],[10,10,255],[10,255,255],[10,122,122],[122,122,10],[10,122,10],[10,10,122]]
  m_CurrentSegmentationNode = None
  m_ROIWidgetList = []
  m_ROIItemList = []

  name_index = 0
  m_TemplateList = {}
  logic = None
  main = None

  m_Scene = None
  #style 0 简单的
  #
  style = 0
  def __init__(self,in_main,in_ui,style=0,scene=None):
    self.main = in_main
    self.m_ui = in_ui
    self.m_Scene = scene
    self.logic = self.main.logic
    self.main.create_labeled_clicked_button(self.m_ui.btnClose2D,"segment_invisible_btn2D.png","关闭2D显示")
    self.main.create_labeled_clicked_button(self.m_ui.btnClose3D,"segment_invisible_btn3D.png","关闭3D显示")
    self.main.create_labeled_clicked_button(self.m_ui.btnAddROI,"add.png","添加一个新的遮罩")
    self.main.create_labeled_clicked_button(self.m_ui.btnUndo,"btn_undo.png","撤销(ctrl+Z)")
    self.main.create_labeled_clicked_button(self.m_ui.btnRedo,"btn_redo.png","反撤销(ctrl+Y)")
    self.main.create_labeled_clicked_button(self.m_ui.btnFresh,"fresh.png","刷新")
    self.main.create_labeled_clicked_button(self.m_ui.btnImport,"add_file.png","加载")
    self.m_ui.btnAddROI.connect('clicked()', self.add_roi)
    self.m_ui.btnClose2D.connect('clicked()', self.close_all_2d)
    self.m_ui.btnClose3D.connect('clicked()', self.close_all_3d)
    self.m_ui.btnFresh.connect('clicked()', self.fresh_list)
    self.m_ui.btnImport.connect('clicked()', self.on_import)
    self.main.create_redoundo(self.m_ui.btnUndo,self.m_ui.btnRedo)
    self.m_ui.btnFresh.setVisible(False)
    self.m_ui.roiListWidget.connect('currentItemChanged(QListWidgetItem*,QListWidgetItem*)', self.on_change_segment)
    
    self.style = style
    if style == 0:
      self.main.add_tools(["Paint","Draw","Scissors","ChooseSlices"],self.m_ui.roi_parent_2,spacing=60)
    if style == 1:
      self.m_ui.roiListWidget.setSpacing(25)

  def close_all_2d(self):
    for i in range(len(self.m_ROIWidgetList)):
      widget = self.m_ROIWidgetList[i]
      widget.btn2D.setChecked(True)
    util.trigger_view_tool("")

  def close_all_3d(self):
    for i in range(len(self.m_ROIWidgetList)):
      widget = self.m_ROIWidgetList[i]
      widget.btn3D.setChecked(True)
    util.trigger_view_tool("")

  def on_change_segment(self,item,_):
    for i in range(len(self.m_ROIWidgetList)):
      widget = self.m_ROIWidgetList[i]
      if widget == self.m_ui.roiListWidget.itemWidget(item):
        segmentNode = self.m_SegmentationList[i]
        self.m_CurrentSegmentationNode = segmentNode
        self.logic.segment_node = segmentNode
        util.trigger_view_tool("")
        break

  def update_segment_node(self):
    item = self.m_ui.roiListWidget.currentItem()
    if item is None:
      return None
    self.on_change_segment(item,"")
  
  def get_all_segment_names(self):
    list1 = []
    for i in range(len(self.m_ROIWidgetList)):
      widget = self.m_ROIWidgetList[i]
      list1.append(widget.lineEdit)
    return list1

  def get_segment_node_by_title(self,title):
    print("get_segment_node_by_title",":",title)
    if title=="All" or title == "全部":
      segmentlist = []
      for i in range(len(self.m_ROIWidgetList)):
          segmentNodeSub = self.m_SegmentationList[i]
          if segmentNodeSub.GetAttribute("alias_name") == "脑脊液":
            continue
          print("get_segment_node_by_title2:",segmentNodeSub.GetName(),segmentNodeSub.GetAttribute("alias_name"))
          segmentlist.append(segmentNodeSub)
      print("get_segment_node_by_title:",len(segmentlist))
      segmentNodeAll=self.union_segment_node_list(self.main.logic.master_node,segmentlist,"get_segment_node_by_title_all")
      np1 = util.arrayFromSegmentInternalBinaryLabelmap(segmentNodeAll,util.GetNthSegmentID(segmentNodeAll,0))
      print(type(np1))
      return segmentNodeAll
    for i in range(len(self.m_ROIWidgetList)):
      widget = self.m_ROIWidgetList[i]
      if widget.lineEdit.text == title:
        segmentNode = self.m_SegmentationList[i]
        return segmentNode
    return None

  def union_segment_node_list(self,master_node,segment_node_list,segment_name):
    node_fix = util.getFirstNodeByName(segment_name)
    if node_fix:
      util.RemoveNode(node_fix)
    node_fix = util.CreateDefaultSegmentationNode(segment_name)
    for i in range(len(segment_node_list)):
        segmentNode1 = segment_node_list[i]
        segment_move = util.GetNthSegment(segmentNode1,0)
        segmentid_move = util.GetNthSegmentID(segmentNode1,0)
        print("Add Segment ID:",segmentid_move)
        node_fix.GetSegmentation().AddSegment(segment_move)
        
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(node_fix)
    segmentEditorWidget.setSourceVolumeNode(master_node)
    segmentEditorWidget.setActiveEffectByName("Logical operators")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("Operation", "UNION")
    segment_id_0 = util.GetNthSegmentID(node_fix,0)

    for i in range(1,util.GetSegmentNumber(node_fix)):
      segment_id_i = util.GetNthSegmentID(node_fix,i)
      effect.setParameter("SelectedSegmentID", segment_id_0) 
      effect.setParameter("ModifierSegmentID",segment_id_i)
      effect.self().onApply()

    while util.GetSegmentNumber(node_fix) > 1:
      segment_id_i = util.GetNthSegmentID(node_fix,1)
      node_fix.GetSegmentation().RemoveSegment(segment_id_i)
    return node_fix

  def union_segment_node(self,node_fix,node_move):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(node_fix)
    segmentEditorWidget.setSourceVolumeNode(self.main.logic.master_node)
    segmentEditorWidget.setActiveEffectByName("Logical operators")
    effect = segmentEditorWidget.activeEffect()
    cloned_node = node_move
    segment_move = util.GetNthSegment(cloned_node,0)
    segmentid_move = util.GetNthSegmentID(cloned_node,0)
    segmentid_fix = util.GetNthSegmentID(node_fix,0)
    node_fix.GetSegmentation().AddSegment(segment_move,segmentid_move)
    effect.setParameter("Operation", "UNION")
    effect.setParameter("SelectedSegmentID", segmentid_move) 
    effect.setParameter("ModifierSegmentID",segmentid_fix)
    effect.self().onApply()
    node_fix.GetSegmentation().RemoveSegment(segmentid_fix)
    return node_fix
    

  def add_segment_node(self,segment_node):
    color_3 = self.m_SegmentColorList[self.name_index%self.m_SegmentationMax]
    segment_node.SetAttribute("segment_manager","1")
    segment = util.GetNthSegment(segment_node,0)
    segment.SetName("dce_tool")
    segment.SetColor(color_3[0]/255.0,color_3[1]/255.0,color_3[2]/255.0)
    self.m_CurrentSegmentationNode = segment_node
    self.m_SegmentationList.append(segment_node)
    ui_roi_unit = slicer.util.loadUI(self.main.resourcePath('UI/JDCEROIUnit.ui'))
    item = qt.QListWidgetItem(self.m_ui.roiListWidget)

    self.main.create_labeled_clicked_button(ui_roi_unit.btnDelete,"volume_remove.png","删除这个ROI",icon_width=26)
    self.main.create_labeled_checkable_button(ui_roi_unit.btn3D,"segment_visible_btn3D.png","segment_invisible_btn3D.png","显示/隐藏 3D",icon_width=26)
    self.main.create_labeled_checkable_button(ui_roi_unit.btn2D,"segment_visible_btn2D.png","segment_invisible_btn2D.png","显示/隐藏 2D",icon_width=26)

    ui_roi_unit.lineEdit.setText("ROI_"+(self.name_index+1).__str__())
    self.name_index+=1

    self.m_ui.roiListWidget.setItemWidget(item,ui_roi_unit)
    self.m_ui.roiListWidget.addItem(item)
    width = self.m_ui.roiListWidget.width
    item.setSizeHint(qt.QSize(width, 85))
    self.m_ROIWidgetList.append(ui_roi_unit)
    self.m_ROIItemList.append(item)
    ui_roi_unit.btnDelete.connect('clicked()', lambda:self.delete_roi(ui_roi_unit.btnDelete))
    ui_roi_unit.btn2D.connect('toggled(bool)', lambda is_show:util.HideNode2D(segment_node,not is_show))
    ui_roi_unit.btn3D.connect('toggled(bool)', lambda is_show:util.ShowNode3D(segment_node,not is_show))
    util.getModuleLogic("JUITool").registe_color_button(ui_roi_unit.pad,segment_node)
    ui_roi_unit.pad.setStyleSheet("background-color: rgb("+color_3[0].__str__()+","+ color_3[1].__str__()+","+color_3[2].__str__()+");")
    util.trigger_view_tool("")
    self.m_ui.roiListWidget.setCurrentItem(item)


  

  def fresh_list(self):
    print("fresh segment list")
    self.m_ui.roiListWidget.clear()
    self.m_TemplateList = {}
    nodes = util.getNodesByClass(util.vtkMRMLSegmentationNode)
    nodes1 = []
    for n1 in nodes:
      if n1.GetAttribute("alias_name") is not None:
        nodes1.append(n1)
    nodes = nodes1
    for node in nodes:
      template = self.main.get_new_widget(self.style)
      item = qt.QListWidgetItem(self.m_ui.roiListWidget)
      template.init(node,self,item)
      self.m_ui.roiListWidget.setItemWidget(item,template.widget)
      self.m_ui.roiListWidget.addItem(item)
      width = self.m_ui.roiListWidget.width
      item.setSizeHint(qt.QSize(width, 116))
      alias_name = node.GetAttribute("alias_name")
      template.setTitle(alias_name)
      self.m_TemplateList[node] = template
      

  def expand(self,node,val):
    template = None
    if node in self.m_TemplateList:
      template = self.m_TemplateList[node]
    if template is None:
      return
    item = template.item
    width = self.m_ui.roiListWidget.width
    if val:
      item.setSizeHint(qt.QSize(width, 340))
    else:
      item.setSizeHint(qt.QSize(width, 116))

    
  def on_import(self):
    NrrdPath = "F:/dce_segment.nii"
    if util.isPackage():
      res_path,result =util.show_file_dialog(0)
      if result == 0:
        return
      else:
        NrrdPath = res_path
    segment_node = util.loadSegmentation(NrrdPath)
    util.AddNode(segment_node)
    self._add_roi(segment_node)

  def add_roi(self):
    segment_node = util.AddNewNodeByClass("vtkMRMLSegmentationNode")
    segment = slicer.vtkSegment()
    segment.SetName("segment"+len(self.m_SegmentationList).__str__())
    segment_node.SetAttribute("segment_manager","1")
    segment_node.GetSegmentation().AddSegment(segment)
    segment_node.CreateDefaultDisplayNodes()
    segment_node.CreateClosedSurfaceRepresentation()
    self._add_roi(segment_node)

  '''
    添加一个新的ROI,颜色内定,最多10个
  '''
  def _add_roi(self,segment_node):
    # if self.main.logic.master_node is None:
    #   util.showWarningText("还没有加载主节点")
    #   return
    # print("on add roi")
    # if len(self.m_SegmentationList) > self.m_SegmentationMax-1:
    #   return False,None
    if segment_node in self.m_SegmentationList:
      return
    color_3 = self.m_SegmentColorList[self.name_index%self.m_SegmentationMax]
    segment = util.GetNthSegment(segment_node,0)
    
    segment.SetColor(color_3[0]/255.0,color_3[1]/255.0,color_3[2]/255.0)
    self.m_CurrentSegmentationNode = segment_node
    self.m_SegmentationList.append(segment_node)

    if self.style == 0:
      ui_roi_unit = slicer.util.loadUI(self.main.resourcePath('UI/JDCEROIUnit.ui'))
      item = qt.QListWidgetItem(self.m_ui.roiListWidget)
      self.main.create_labeled_clicked_button(ui_roi_unit.btnDelete,"volume_remove.png","删除这个ROI",icon_width=26)
      self.main.create_labeled_checkable_button(ui_roi_unit.btn3D,"segment_visible_btn3D.png","segment_invisible_btn3D.png","显示/隐藏 3D",icon_width=26)
      self.main.create_labeled_checkable_button(ui_roi_unit.btn2D,"segment_visible_btn2D.png","segment_invisible_btn2D.png","显示/隐藏 2D",icon_width=26)
      if segment_node.GetAttribute("alias_name") == None:
        ui_roi_unit.lineEdit.setText("ROI_"+(self.name_index+1).__str__())
      else:
        ui_roi_unit.lineEdit.setText(segment_node.GetAttribute("alias_name"))
      self.name_index+=1
      self.m_ui.roiListWidget.setItemWidget(item,ui_roi_unit)
      self.m_ui.roiListWidget.addItem(item)
      width = self.m_ui.roiListWidget.width
      item.setSizeHint(qt.QSize(width, 85))
      self.m_ROIWidgetList.append(ui_roi_unit)
      self.m_ROIItemList.append(item)
      ui_roi_unit.btnDelete.connect('clicked()', lambda:self.delete_roi(ui_roi_unit.btnDelete))
      ui_roi_unit.btn2D.connect('toggled(bool)', lambda is_show:util.HideNode2D(segment_node,not is_show))
      ui_roi_unit.btn3D.connect('toggled(bool)', lambda is_show:util.ShowNode3D(segment_node,not is_show))
      util.getModuleLogic("JUITool").registe_color_button(ui_roi_unit.pad,segment_node)
      ui_roi_unit.pad.setStyleSheet("background-color: rgb("+color_3[0].__str__()+","+ color_3[1].__str__()+","+color_3[2].__str__()+");")
    if self.style == 1:
      ui_roi_unit = slicer.util.loadUI(self.main.resourcePath('UI/JNormalROI.ui'))
      item = qt.QListWidgetItem(self.m_ui.roiListWidget)
      self.main.create_labeled_clicked_button(ui_roi_unit.btnDelete,"Delete.png","删除这个ROI",icon_width=26)
      ui_roi_unit.lineEdit.setText("重命名_"+(self.name_index+1).__str__())
      self.name_index+=1
      self.m_ui.roiListWidget.setItemWidget(item,ui_roi_unit)
      self.m_ui.roiListWidget.addItem(item)
      item.setSizeHint(qt.QSize(item.sizeHint().width(), 114))
      self.m_ROIWidgetList.append(ui_roi_unit)
      self.m_ROIItemList.append(item)
      ui_roi_unit.btnDelete.connect('clicked()', lambda:self.delete_roi(ui_roi_unit.btnDelete))
      util.getModuleLogic("JUITool").registe_color_button(ui_roi_unit.pad,segment_node)
      ui_roi_unit.pad.setStyleSheet("background-color: rgb("+color_3[0].__str__()+","+ color_3[1].__str__()+","+color_3[2].__str__()+");")
    util.trigger_view_tool("")
    self.m_ui.roiListWidget.setCurrentItem(item)


  def delete_roi(self,btn):
    for i in range(len(self.m_ROIWidgetList)):
      widget = self.m_ROIWidgetList[i]
      if widget.btnDelete == btn:
        item = self.m_ROIItemList[i]
        segmentNode = self.m_SegmentationList[i]

        self.m_ui.roiListWidget.takeItem(i)
        self.m_ROIItemList.remove(item)
        self.m_ROIWidgetList.remove(widget)
        self.m_SegmentationList.remove(segmentNode)
        util.RemoveNode(segmentNode)
        break

