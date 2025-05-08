import slicer
import slicer.util as util
import os,vtk,qt
import numpy as np
from AddFiberLib.BaseUnit import FiberUnit
class NormalUnit(FiberUnit):

  infos = {}

  ShrinkHeight = 152
  ShrinkWidth = 100
  ExpandHeight = 400
  ExpandHeight2 = 600
  ExpandWidth = 100
  style = "NormalUnit:1"
  def __init__(self):
    super().__init__(self.style)


  def set_widget(self,in_widget,main):
    super().set_widget(in_widget,main)
    self.update_ui(10)
    self.addEvent(True)
    
    rname = "fiber_delete.png"
    self.resourcelist[rname] = "删除当前的导管"
    btnModify_visible = util.get_resource(rname)
    btnModify_stylesheet = ""
    btnModify_stylesheet = btnModify_stylesheet + "QPushButton{image: url("+btnModify_visible+")}"
    self.ui.btnDelete.toolTip = self.resourcelist[rname]
    self.ui.btnDelete.setStyleSheet(btnModify_stylesheet)
    self.ui.btnDelete.setText("")
    self.ui.btnDelete.setVisible(False)
    
    rname = "model_cover_导向器.png"
    self.resourcelist[rname] = "导管的图标"
    picture_path = util.get_resource(rname)
    util.add_pixelmap_to_label(picture_path,self.ui.lblImage)
    
    rname = "fiber_visible.png"
    self.resourcelist[rname] = "切换当前导管是否可见"
    btnSetting_visible = util.get_resource(rname)
    btnSetting_stylesheet = ""
    btnSetting_stylesheet = btnSetting_stylesheet + "QPushButton{image: url("+btnSetting_visible+")}"
    self.ui.btnVisible.toolTip = self.resourcelist[rname]
    self.ui.btnVisible.setStyleSheet(btnSetting_stylesheet)
    self.ui.tabWidget.tabBar().hide()
    self.ui.tabWidget.setCurrentIndex(0)
    self.ui.tabWidget.setStyleSheet("QTabWidget::pane { border: none; }")
    self.ui.btnInfo.setVisible(False)
    
    tooltip = "点击显示/关闭当前3D"
    tooltip1 = "点击显示当前3D"
    tooltip2 = "点击关闭当前3D"
    self.resourcelist["visible_3D.png"] = tooltip1
    self.resourcelist["invisible_3D.png"] = tooltip2
    self.ui.btn3D.setToolTip(tooltip)
    btn3d_visible = util.get_resource('visible_3D.png')
    btn3d_unvisible = util.get_resource('invisible_3D.png')
    btn3d_stylesheet = ""
    btn3d_stylesheet = btn3d_stylesheet + "QPushButton{image: url("+btn3d_visible+")}"
    btn3d_stylesheet = btn3d_stylesheet + "QPushButton:checked{image: url("+btn3d_unvisible+")}"
    
    self.ui.btn3D.setStyleSheet(btn3d_stylesheet)
    
    tooltip = "点击显示/关闭当前2D"
    tooltip1 = "点击显示当前2D"
    tooltip2 = "点击关闭当前2D"
    self.resourcelist["visible_2D.png"] = tooltip1
    self.resourcelist["invisible_2D.png"] = tooltip2
    self.ui.btn2D.setToolTip(tooltip)
    btn2D_visible = util.get_resource('visible_2D.png')
    btn2D_unvisible = util.get_resource('invisible_2D.png')
    btn2D_stylesheet = ""
    btn2D_stylesheet = btn2D_stylesheet + "QPushButton{image: url("+btn2D_visible+")}"
    btn2D_stylesheet = btn2D_stylesheet + "QPushButton:checked{image: url("+btn2D_unvisible+")}"
    
    self.ui.btn2D.setStyleSheet(btn2D_stylesheet)
    
    rname = "fiber_info.png"
    self.resourcelist[rname] = "修改当前的数据"
    btnModify_visible = util.get_resource(rname)
    btnModify_stylesheet = ""
    btnModify_stylesheet = btnModify_stylesheet + "QPushButton{image: url("+btnModify_visible+")}"
    self.ui.btnInfo_2.toolTip = self.resourcelist[rname]
    self.ui.btnInfo_2.setStyleSheet(btnModify_stylesheet)
    self.ui.btnInfo_2.setText("")
    
    
    rname = "fiber_delete.png"
    self.resourcelist[rname] = "删除当前的导向器"
    btnModify_visible = util.get_resource(rname)
    btnModify_stylesheet = ""
    btnModify_stylesheet = btnModify_stylesheet + "QPushButton{image: url("+btnModify_visible+")}"
    self.ui.btnDelete_3.toolTip = self.resourcelist[rname]
    self.ui.btnDelete_3.setStyleSheet(btnModify_stylesheet)
    self.ui.btnDelete_3.setText("")
    
    self.ui.btnPalette.setStyleSheet("background-color:rgb(255,255,0);")
    
    if util.get_from_PAAA("current_project_selector_project_name")=="SunSlicer":
      self.ui.tmp1.setVisible(False)
      color = util.get_unique_color()
      qcolor = qt.QColor(color[0]*255,color[1]*255,color[2]*255)
      self.on_get_color(qcolor)
    

  def delete_unit_without_warning(self):
    self.delete_normal_fiber()
    super().delete_unit_without_warning()
    

  def on_open_color_pad(self):
      qdialog = qt.QColorDialog()
      qdialog.connect('colorSelected(QColor)', self.on_get_color)
      qdialog.installEventFilter(slicer.util.mainWindow())
      qdialog.exec()
  def on_get_color(self,qcolor):
    self.qcolor = qcolor
    self.ui.btnPalette.setStyleSheet("background-color:rgb("+qcolor.red().__str__()+","+qcolor.green().__str__()+","+qcolor.blue().__str__()+");")
    if self.get_model("fiber_model"):
      self.get_model("fiber_model").GetDisplayNode().SetColor([qcolor.red()/255.0,qcolor.green()/255.0,qcolor.blue()/255.0])

  def shrink(self):
    import qt
    # single_item = self.single_item
    # self.ui.widget.setVisible(False)
    # self.ui.textEdit.setVisible(False)
    # single_item.listitem.setSizeHint(qt.QSize(self.ShrinkWidth , self.ShrinkHeight))
    # single_item.sub_template.widget.setFixedHeight(self.ShrinkHeight)
    self.ui.tabWidget.setCurrentIndex(1)
    pass

  def expand(self):
    import qt
    # single_item = self.single_item
    # self.ui.widget.setVisible(True)
    # self.ui.textEdit.setVisible(True)
    # single_item.listitem.setSizeHint(qt.QSize(self.ExpandWidth , self.ExpandHeight))
    # single_item.sub_template.widget.setFixedHeight(self.ExpandHeight)
    self.ui.tabWidget.setCurrentIndex(0)
    
  def show_fiber(self):
    self.ui.btnVisible.setChecked(True)
    self.ui.btnVisible.setChecked(False)

  def hide_fiber(self):
    self.ui.btnVisible.setChecked(False)
    self.ui.btnVisible.setChecked(True)

  def set_component(self,node,type):
    super().set_component(node,type)
    if type == "fiber_model":
      self.set_model(type,node)
    if type == "fiber_model_inner":
      self.set_model(type,node)

  def on_length_slider_changed(self,val):
    self.on_normal_fiber_modify()


  def destroy(self):
    #util.removeFromParent2(self.widget)
    self.addEvent(False)
    self.delete_model("fiber_model")
    self.delete_model("fiber_model_inner")
    
  def init_from_single(self,widget,entry_point,single_item):
    self.single_item = single_item
    nodelist = []
    key = entry_point.GetAttribute("fiber_unit_id")
    for node in util.get_all_nodes():
      if key == node.GetAttribute("fiber_unit_id"):
        nodelist.append(node)
    entry_point.SetAttribute("is_single","1")
    self.unit_index_inner = key
    self.load_archive(key,nodelist)
    self.shrink()

  def addEvent(self,boolVal):
    if boolVal:
      self.ui.btnVisible.connect('toggled(bool)', self.change_visible)
      self.ui.radius_slider.connect('valueChanged(double)',lambda:self.on_normal_fiber_modify())
      self.ui.thick_slider.connect('valueChanged(double)',lambda:self.on_normal_fiber_modify())
      self.ui.length_slider.connect('valueChanged(double)',lambda:self.on_normal_fiber_modify())
      self.ui.btnPalette.connect('clicked()', self.on_open_color_pad)
      self.ui.btnInfo.connect('clicked()', self.on_info)
      self.ui.btnDelete.connect('clicked()',self.on_delete)
      self.ui.btnConfirm.connect('clicked()',self.on_confirm)
      self.ui.btnDelete_2.connect('clicked()',self.on_delete)
      self.ui.sliderOpacity2D.connect('valueChanged(double)',self.on_opacity_2d)
      self.ui.sliderOpacity.connect('valueChanged(double)',self.on_opacity_3d)
      self.ui.btn3D.connect('toggled(bool)', self.on_show_3D)
      self.ui.btn2D.connect('toggled(bool)', self.on_show_2D)
      self.ui.btnInfo_2.connect('clicked()', self.on_edit_info)
      self.ui.btnDelete_3.connect('clicked()', self.on_delete_info)
      self.ui.entry_lock_cb.connect('toggled(bool)', self.lock_entry)
      self.ui.target_lock_cb.connect('toggled(bool)', self.lock_target)
    else:
      self.ui.btnVisible.disconnect('toggled(bool)', self.change_visible)
      self.ui.radius_slider.disconnect('valueChanged(double)',lambda:self.on_normal_fiber_modify())
      self.ui.thick_slider.disconnect('valueChanged(double)',lambda:self.on_normal_fiber_modify())
      self.ui.length_slider.disconnect('valueChanged(double)',lambda:self.on_normal_fiber_modify())
      self.ui.btnPalette.disconnect('clicked()', self.on_open_color_pad)
      self.ui.btnInfo.disconnect('clicked()', self.on_info)
      self.ui.btnDelete.disconnect('clicked()',self.on_delete)
      self.ui.btnConfirm.disconnect('clicked()',self.on_confirm)
      self.ui.btnDelete_2.disconnect('clicked()',self.on_delete)
      self.ui.sliderOpacity2D.disconnect('valueChanged(double)',self.on_opacity_2d)
      self.ui.sliderOpacity.disconnect('valueChanged(double)',self.on_opacity_3d)
      self.ui.btn3D.disconnect('toggled(bool)', self.on_show_3D)
      self.ui.btn2D.disconnect('toggled(bool)', self.on_show_2D)
      self.ui.btnInfo_2.disconnect('clicked()', self.on_edit_info)
      self.ui.btnDelete_3.disconnect('clicked()', self.on_delete_info)
      self.ui.entry_lock_cb.disconnect('toggled(bool)', self.lock_entry)
      self.ui.target_lock_cb.disconnect('toggled(bool)', self.lock_target)

  def lock_entry(self,val):
    self.entry_point.SetLocked(val)
    # if val:
    #   util.HideNode(self.entry_point)
    # else:
    #   util.ShowNode(self.entry_point)
    
  def lock_target(self,val):
    self.target_point.SetLocked(val)
  
  def on_delete_info(self):
    res = util.messageBox("确定删除导管吗",windowTitle=util.tr("提示"))
    if res == 0:
      return
    slicer.mrmlScene.InvokeEvent(util.JAddFiberNormalUnitRemvoed,self.entry_point)
    self.delete_unit_without_warning()
    
  def on_edit_info(self):
    util.send_event_str(util.SetPage,920)
    util.getModuleWidget("JAddFiber").SetFiber(self.entry_point)
    
  def on_show_2D(self,boolval):
    nodelist = []
    for node in util.get_all_nodes():
      if self.unit_index_inner == node.GetAttribute("fiber_unit_id"):
        nodelist.append(node)
    for node in nodelist:
      util.HideNode2D(node,not boolval)

  def on_show_3D(self,boolval):
    nodelist = []
    for node in util.get_all_nodes():
      if self.unit_index_inner == node.GetAttribute("fiber_unit_id"):
        nodelist.append(node)
    for node in nodelist:
      if not boolval:
        if node.GetAttribute("hide_node") == "True":
          continue
      util.ShowNode3D(node,not boolval)
      
  def on_opacity_2d(self,value):
    nodelist = []
    for node in util.get_all_nodes():
      if self.unit_index_inner == node.GetAttribute("fiber_unit_id"):
        nodelist.append(node)
    for node in nodelist:
      util.GetDisplayNode(node).SetSliceIntersectionOpacity(value/100.0)
  
  def on_opacity_3d(self,value):
    nodelist = []
    for node in util.get_all_nodes():
      if self.unit_index_inner == node.GetAttribute("fiber_unit_id"):
        nodelist.append(node)
    for node in nodelist:
      util.GetDisplayNode(node).SetOpacity(value/100.0)
      
      
  def on_confirm(self):
    if self.entry_point == None and self.target_point == None:
      if util.get_from_PAAA("current_project_selector_project_name")!="SunSlicer":
        util.send_event_str(util.GotoPrePage,"1")
    elif self.entry_point == None or self.target_point == None:
      res = util.messageBox("当前并没有生成导管，继续将遗失当前的信息，是否继续",windowTitle=util.tr("提示"))
      if res == 0:
        return
      self.delete_unit_without_warning()
    else:
      self.ui.entry_lock_cb.setChecked(True)
      self.ui.target_lock_cb.setChecked(True)
      #util.GetDisplayNode(self.entry_point).SetHandlesInteractive(False)
      #util.GetDisplayNode(self.target_point).SetHandlesInteractive(False)
      util.send_event_str(util.JAddFiberNormalReturnSingle,self.entry_point.GetID())
    
  def on_delete(self):
    res = util.messageBox("确定删除吗",windowTitle=util.tr("提示"))
    if res == 0:
      return
    slicer.mrmlScene.InvokeEvent(util.JAddFiberNormalUnitRemvoed,self.entry_point)
    self.delete_unit_without_warning()
    #util.send_event_str(util.GotoPrePage,"1")
    
  def on_info(self):
    if self.single_item is not None:
      if self.ui.textEdit.visible == False:
        self.expand()
      else:
        self.shrink()

  def load_archive(self,id,nodelist):
    print("fiber unit load_archive",id,len(nodelist))
    self.unit_index_inner = id
    cloned_node = None
    self.update_archive_flag = False
    
    for node in nodelist:
      type = node.GetAttribute("fiber_unit_type")
      if type == "entry_point":
        cloned_node = util.clone(node)
    for node in nodelist:
      self.set_component(node,node.GetAttribute("fiber_unit_type"))

    self.style = cloned_node.GetAttribute("node_type")

    if self.get_model("fiber_model"):
      if self.get_model("fiber_model").GetDisplayNode():
        color = self.get_model("fiber_model").GetDisplayNode().GetColor()
        self.qcolor = qt.QColor(color[0]*255,color[1]*255,color[2]*255)
        self.ui.btnPalette.setStyleSheet(f"background-color:rgb({color[0]*255},{color[1]*255},{color[2]*255});")
    
    self.addEvent(False)
    if cloned_node.GetAttribute("length_slider") is not None:
      self.ui.length_slider.setValue(float(cloned_node.GetAttribute("length_slider")))
    if cloned_node.GetAttribute("thick_slider") is not None:
      self.ui.thick_slider.setValue(float(cloned_node.GetAttribute("thick_slider")))
    if cloned_node.GetAttribute("radius_slider") is not None:
      self.ui.radius_slider.setValue(float(cloned_node.GetAttribute("radius_slider")))
    
    
    
    util.RemoveNode(cloned_node)
    self.update_archive_flag = True
    self.ui.btnInfo.setVisible(True)
    
    entry_point_world,_ = self.get_entry_point()
    target_point_world,_ = self.get_target_point()
    self.ensure_load_stl(entry_point_world,target_point_world)
    self.addEvent(True)
    self.ui.btnInfo.setVisible(False)
    
  def reset_slider(self):
    length = 150
    thick = 1.5
    radius = 1.5
    if self.entry_point:
      if self.entry_point.GetAttribute("length_slider") is not None:
        length = float(self.entry_point.GetAttribute("length_slider"))
      if self.entry_point.GetAttribute("thick_slider") is not None:
        thick = float(self.entry_point.GetAttribute("thick_slider"))
      if self.entry_point.GetAttribute("radius_slider") is not None:
        radius = float(self.entry_point.GetAttribute("radius_slider"))
      self.ui.length_slider.setValue(length)
      self.ui.thick_slider.setValue(thick)
      self.ui.radius_slider.setValue(radius)
  
  def update_ui(self,offset):
    self.ui.btnPalette.setStyleSheet("background-color:rgb(255,255,255);")
    btnVisible_visible =  util.get_resource("btnUnvisible.png") 
    btnVisible_unvisible = util.get_resource("btnVisible.png")
    btnVisible_stylesheet = ""
    btnVisible_stylesheet = btnVisible_stylesheet + "QPushButton{image: url("+btnVisible_unvisible+")}"
    btnVisible_stylesheet = btnVisible_stylesheet + "QPushButton:checked{image: url("+btnVisible_visible+")}"
    self.ui.btnVisible.toolTip = "显示/关闭 导管模型"
    self.ui.btnVisible.setStyleSheet(btnVisible_stylesheet)
    

  def on_normal_fiber_modify(self):
    if self.entry_point is None:
      #util.showWarningText("请添加靶点和入点之后再添加导管")
      return
    if self.target_point is None:
      #util.showWarningText("请添加靶点和入点之后再添加导管")
      return
    if self.entry_point.GetNumberOfControlPoints() == 0:
      #util.showWarningText("请添加靶点和入点之后再添加导管")
      return
    if self.target_point.GetNumberOfControlPoints() == 0:
      #util.showWarningText("请添加靶点和入点之后再添加导管")
      return
    util.getModuleWidget("UnitScore").adjust_channel_value = True
    entry_point_world,_ = self.get_entry_point()
    target_point_world,_ = self.get_target_point()
    self.delete_normal_fiber()
    fiber_model,fiber_model_inner = self.on_add_normal_fiber(entry_point_world,target_point_world,self.qcolor,self.ui.length_slider.value,self.ui.radius_slider.value/2,self.ui.thick_slider.value)
    fiber_model.SetSelectable(False)
    fiber_model_inner.SetSelectable(False)
    self.set_component(fiber_model,"fiber_model")
    self.set_component(fiber_model_inner,"fiber_model_inner")
    
    self.update_archive_paras()

  def update_archive_paras(self):
    if self.entry_point:
      self.entry_point.SetAttribute("thick_slider",self.ui.thick_slider.value.__str__())
      self.entry_point.SetAttribute("radius_slider",self.ui.radius_slider.value.__str__())
      self.entry_point.SetAttribute("length_slider",self.ui.length_slider.value.__str__())

  def check_points_placed(self):
    self.on_point_hide_3d(False)

  def set_model(self,type,node):
    if not self.entry_point:
      return None
    self.entry_point.SetAttribute(type,node.GetID())
    
  def get_model(self,type):
    if not self.entry_point:
      return None
    id = self.entry_point.GetAttribute(type)
    if id is None:
      return
    node = util.GetNodeByID(id)
    return node
  
  def delete_model(self,type):
    id = self.entry_point.GetAttribute(type)
    node = util.GetNodeByID(id)
    util.RemoveNode(node)
    self.entry_point.SetAttribute(type,None)
  
  def delete_normal_fiber(self):
    if self.get_model("fiber_model") is not None:
      transform_node = self.get_model("fiber_model").GetParentTransformNode()
      if transform_node is not None:
        util.RemoveNode(transform_node)
    if self.get_model("fiber_model"):
      self.delete_model("fiber_model")
    if self.get_model("fiber_model_inner"):
      self.delete_model("fiber_model_inner")

  def set_info(self,key,value):
    print("set_info",key,value)
    self.infos[key] = value

  def on_point_hide_3d(self,is_hide):
      if is_hide:
        self.set_info("point_3d",util.Visibility3D(self.get_model("fiber_model")))
        util.ShowNode3D(self.get_model("fiber_model"),False)
        util.ShowNode3D(self.get_model("fiber_model_inner"),False)
      else:
        util.ShowNode3D(self.get_model("fiber_model"),True)
        util.ShowNode3D(self.get_model("fiber_model_inner"),True)

  def on_add_normal_fiber(self,entry_point_world,target_point_world,qcolor,length,radius,thick):
    # model_node = self.add_hollow_cylinder(radius,radius+thick,length,qcolor.red()/255.0,qcolor.green()/255.0,qcolor.blue()/255.0,)
    print("on_add_normal_fiber")
    import slicer.util as util
    slicer.app.applicationLogic().PauseRender()
    model_node,modelNode_inner = self.add_cylinder(radius+thick,radius,length,qcolor.red()/255.0,qcolor.green()/255.0,qcolor.blue()/255.0)
    util.getModuleLogic("JTransformTool").rotate_fiber_model_to_vector(model_node,entry_point_world,target_point_world,length)
    transform_node = model_node.GetParentTransformNode()
    modelNode_inner.SetAndObserveTransformNodeID(transform_node.GetID())
    slicer.app.applicationLogic().ResumeRender()
    model_node.SetName("outer_normal_fiber")
    modelNode_inner.SetName("inner_normal_fiber")
    return model_node,modelNode_inner


  def add_cylinder(self,radius,inner_radius,height,red=1,green=1,blue=1):
      print("add_cylinder",radius,inner_radius,height)
      cy_source = vtk.vtkCylinderSource()
      cy_source.SetHeight(height)
      cy_source.SetRadius(radius)
      cy_source.SetResolution(160)
      modelNode = slicer.modules.models.logic().AddModel(cy_source.GetOutputPort())
      modelNode.GetDisplayNode().SetColor([red,green,blue])
      modelNode.GetDisplayNode().SetVisibility2D(True)
      modelNode.GetDisplayNode().SetSliceIntersectionThickness(2)

      cy_source_inner = vtk.vtkCylinderSource()
      cy_source_inner.SetHeight(height+5)
      cy_source_inner.SetRadius(inner_radius)
      cy_source_inner.SetResolution(160)
      modelNode_inner = slicer.modules.models.logic().AddModel(cy_source_inner.GetOutputPort())
      
      modelNode_inner.GetDisplayNode().SetSliceIntersectionThickness(2)
      modelNode.SetAttribute("JAddFiberWidget_Fiber","1")
      modelNode_inner.SetAttribute("JAddFiberWidget_FiberInner","1")
      return modelNode,modelNode_inner

  def is_not_empty(self):
    if self.get_model("fiber_model"):
      return True
    else:
      return False

  def fresh_result(self):
    util.ShowNode3D(self.get_model("fiber_model"),False)
    util.ShowNode3D(self.get_model("fiber_model_inner"),False)
    super().fresh_result()
    

  def change_visible(self,is_show):
    print("on change visible")
    is_show = not is_show
    if self.get_model("fiber_model"):
      util.ShowNode(self.get_model("fiber_model"),is_show)
      util.ShowNode3D(self.get_model("fiber_model"),is_show)
    if self.get_model("fiber_model_inner"):
      util.ShowNode(self.get_model("fiber_model_inner"),is_show)
      util.ShowNode3D(self.get_model("fiber_model_inner"),is_show)

  def add_hollow_cylinder(self,inner_radius,outter_radius,height,red=1,green=1,blue=1):
    cy_source = vtk.vtkCylinderSource()
    cy_source.SetHeight(height)
    cy_source.SetRadius(outter_radius)
    cy_source.SetResolution(960)
    modelNode = slicer.modules.models.logic().AddModel(cy_source.GetOutputPort())
    

    cy_source_inner = vtk.vtkCylinderSource()
    cy_source_inner.SetHeight(height+15)
    cy_source_inner.SetRadius(inner_radius)
    cy_source_inner.SetResolution(960)
    modelNode_inner = slicer.modules.models.logic().AddModel(cy_source_inner.GetOutputPort())

    output_node = util.AddNewNodeByClass('vtkMRMLModelNode')

    CombineModelsLogic = util.getModuleLogic("CombineModels")
    if CombineModelsLogic:
      CombineModelsLogic.process(modelNode,modelNode_inner,output_node,'difference')
    
    util.RemoveNode(modelNode_inner)
    util.RemoveNode(modelNode)

    output_node.GetDisplayNode().SetColor([red,green,blue])
    output_node.GetDisplayNode().SetVisibility2D(True)
    return output_node
    
  def on_add_hollow_fiber(self,entry_point_world,target_point_world,qcolor,length,radius,thick):
    model_node = self.add_hollow_cylinder(radius,radius+thick,length,qcolor.red()/255.0,qcolor.green()/255.0,qcolor.blue()/255.0)
    util.getModuleLogic("JTransformTool").rotate_fiber_model_to_vector(model_node,entry_point_world,target_point_world,length)
    return model_node

  def generate_final_fiber_model(self):
    if not self.get_model("fiber_model") or not self.get_model("fiber_model_inner"):
      return
    entry_point_world = [0,0,0]
    self.entry_point.GetNthControlPointPositionWorld(0, entry_point_world)
    target_point_world = [0,0,0]
    self.target_point.GetNthControlPointPositionWorld(0, target_point_world)
    self.fiber_model_hollow = self.on_add_hollow_fiber(entry_point_world,target_point_world,self.qcolor,self.ui.length_slider.value,self.ui.radius_slider.value/2,self.ui.thick_slider.value)
    
    

    #hollow_copy = util.clone(self.fiber_model_hollow)
    origin_copy = util.clone(self.get_model("fiber_model_inner"))
    #hollow_copy.SetAndObserveTransformNodeID(self.fiber_model_hollow.GetTransformNodeID())
    #hollow_copy.HardenTransform()
    origin_copy.SetAndObserveTransformNodeID(self.get_model("fiber_model").GetTransformNodeID())
    
    origin_copy.SetName("OriginCopy")
    vtkpolydata = vtk.vtkPolyData()
    vtkpolydata.DeepCopy(self.get_model("fiber_model_inner").GetPolyData())
    origin_copy.SetAndObservePolyData(vtkpolydata)
    origin_copy.HardenTransform()
    origin_copy.SetAttribute("TobeDelete","1")
    #hollow_copy.SetAttribute("origin_node_id",origin_copy.GetID())
    self.fiber_model_hollow.SetAttribute("origin_node_id",origin_copy.GetID())
    self.fiber_model_hollow.HardenTransform()
    self.get_model("fiber_model").SetAttribute("final_fiber_model",self.fiber_model_hollow.GetID())
    #self.ui.btnVisible.setChecked(True)
    return self.fiber_model_hollow

  def ensure_load_stl(self,entry_point_world,target_point_world):
      distance = np.sqrt( (entry_point_world[0]-target_point_world[0])*(entry_point_world[0]-target_point_world[0])+
                            (entry_point_world[1]-target_point_world[1])*(entry_point_world[1]-target_point_world[1])+
                            (entry_point_world[2]-target_point_world[2])*(entry_point_world[2]-target_point_world[2])
                            )
      self.ui.textEdit.setText("入点到靶点距离:"+round(distance, 2).__str__()+"mm")
      if self.get_model("fiber_model") and self.get_model("fiber_model_inner"):
        
        util.getModuleLogic("JTransformTool").rotate_fiber_model_to_vector(self.get_model("fiber_model"),entry_point_world,target_point_world,self.ui.length_slider.value)
        old_transform_node = self.get_model("fiber_model_inner").GetParentTransformNode()
        util.RemoveNode(old_transform_node)
        transform_node = self.get_model("fiber_model").GetParentTransformNode()
        self.get_model("fiber_model_inner").SetAndObserveTransformNodeID(transform_node.GetID())
      else:
        
        fiber_model,fiber_model_inner = self.on_add_normal_fiber(entry_point_world,target_point_world,self.qcolor,self.ui.length_slider.value,self.ui.radius_slider.value/2,self.ui.thick_slider.value)
        import re
        style_sheet = self.ui.btnPalette.styleSheet
        # 使用正则表达式查找 background-color 的 RGB 值
        match = re.search(r'background-color:\s*rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', style_sheet)

        if match:
            red, green, blue = match.groups()
            print(f"Red: {red}, Green: {green}, Blue: {blue}")
        else:
            print("Background color not found or not in expected format.")
        fiber_model.GetDisplayNode().SetColor(int(red)/255,int(green)/255,int(blue)/255)
        self.set_component(fiber_model,"fiber_model")
        self.set_component(fiber_model_inner,"fiber_model_inner")
        util.GetDisplayNode(self.get_model("fiber_model")).SetSelectable(False)
        util.GetDisplayNode(self.get_model("fiber_model_inner")).SetSelectable(False)
