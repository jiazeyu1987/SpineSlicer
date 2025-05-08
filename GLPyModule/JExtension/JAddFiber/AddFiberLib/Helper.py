from __main__ import vtk, slicer,qt
import slicer.util as util
import numpy as np

class FiberUnit():
  entry_point = None
  target_point = None
  fiber_model = None
  fiber_model_inner = None
  widget = None
  main = None
  qcolor = None

  '''
    模型控制
  '''
  stl_stick = None
  stl_holder = None
  stl_fiber = None
  stl_bushinglist = []
  stl_rotate_angle = -50
  stl_rotate_angle_du = 0
  stl_depth = 0
  stl_depth_du = 0
  infos = {}

  '''
    度若飞模型
  '''
  stl_du_axis = None
  stl_du_tube = None
  stl_du_board = None
  stl_du_bar = None
  stl_du_needle = None
  du_map = {}

  stl_robot_arm = None

  #代表了导管的类型
  style = None
  style_normal = 0
  style_stl_1 = 1
  style_stl_2 = 2
  style_stl_3 = 3
  style_stl_duruofei = 11
  style_robot_arm = 21
  #每一个导管工具都有一个独一无二的编号
  unit_index_inner = 0
  
  emap = {}
  def __init__(self,style):
    self.style = style
    self.unit_index_inner = util.global_int_index
    util.global_int_index=util.global_int_index+1
    

  def set_widget(self,in_widget,main):
    self.widget = in_widget
    self.main = main
    
    
    
    picPath = main.resourcePath('Icons/fiberEntryIcon.png').replace('\\','/')
    util.add_pixel_label(picPath,"添加入点",self.widget.btnAddEntry)
    self.widget.btnAddEntry.connect('toggled(bool)', self.on_add_entry_point)

    picPath = main.resourcePath('Icons/fiberTargetIcon.png').replace('\\','/')
    util.add_pixel_label(picPath,"添加靶点",self.widget.btnAddTarget)
    self.widget.btnAddTarget.connect('toggled(bool)', self.on_add_target_point)

    

    btnDelete_visible = self.main.resourcePath('Icons/btnDelete.png').replace('\\','/')
    btnDelete_stylesheet = ""
    btnDelete_stylesheet = btnDelete_stylesheet + "QPushButton{image: url("+btnDelete_visible+")}"
    self.widget.btnDelete.connect('clicked()', self.delete_unit)
    self.widget.btnDelete.toolTip = "删除当前导管"
    self.widget.btnDelete.setStyleSheet(btnDelete_stylesheet)

    self.widget.btnPalette.setStyleSheet("background-color:rgb(255,255,255);")
    self.widget.btnPalette.connect('clicked()', self.on_open_color_pad)
    

    btnDirectionNormal_visible = self.main.resourcePath('Icons/btnDirectionNormal.png').replace('\\','/')
    btnDirectionNormal_stylesheet = ""
    btnDirectionNormal_stylesheet = btnDirectionNormal_stylesheet + "QPushButton{image: url("+btnDirectionNormal_visible+")}"
    self.widget.btnDirectionNormal.connect('clicked()', lambda:util.reinit())
    self.widget.btnDirectionNormal.toolTip = "恢复到默认视角"
    self.widget.btnDirectionNormal.setStyleSheet(btnDirectionNormal_stylesheet)


    btnDirectionFiber_visible = self.main.resourcePath('Icons/btnDirectionFiber.png').replace('\\','/')
    btnDirectionFiber_stylesheet = ""
    btnDirectionFiber_stylesheet = btnDirectionFiber_stylesheet + "QPushButton{image: url("+btnDirectionFiber_visible+")}"
    self.widget.btnDirectionFiber.connect('clicked()', self.rotate_to_fiber)
    self.widget.btnDirectionFiber.toolTip = "设置到导管视角"
    self.widget.btnDirectionFiber.setStyleSheet(btnDirectionFiber_stylesheet)

    btnSetting_visible = self.main.resourcePath('Icons/btnVisible.png').replace('\\','/')
    btnSetting_stylesheet = ""
    btnSetting_stylesheet = btnSetting_stylesheet + "QPushButton{image: url("+btnSetting_visible+")}"
    self.widget.btnSetting.connect('clicked()', self.on_setting)
    self.widget.btnSetting.toolTip = "设置模型的透明度和颜色"
    self.widget.btnSetting.setStyleSheet(btnSetting_stylesheet)

    self.widget.btnAuto.connect('toggled(bool)', self.on_duruofei_auto)

    self.widget.btnBushing.setToolButtonStyle(3)
    self.widget.btnBushing.setPopupMode(1)
    btnReset_stylesheet = ""
    btnReset_stylesheet = btnReset_stylesheet + "QToolTip { color: #000000; background-color: #ffffff; border: 0px; }"
    

    menu = qt.QMenu(self.widget.btnBushing)
    self.widget.btnBushing.setMenu(menu)
    self.widget.btnBushing.connect('clicked()', lambda:self.add_bushing(5))
    menu.addAction("5mm套管",lambda:self.add_bushing(5))
    menu.addAction("8mm套管",lambda:self.add_bushing(8))
    self.widget.btnBushing.toolTip = ""
    self.widget.btnBushing.setStyleSheet(btnReset_stylesheet)


    

    btnVisible_visible = self.main.resourcePath('Icons/btnUnvisible.png').replace('\\','/')
    btnVisible_unvisible = self.main.resourcePath('Icons/btnVisible.png').replace('\\','/')
    btnVisible_stylesheet = ""
    btnVisible_stylesheet = btnVisible_stylesheet + "QPushButton{image: url("+btnVisible_unvisible+")}"
    btnVisible_stylesheet = btnVisible_stylesheet + "QPushButton:checked{image: url("+btnVisible_visible+")}"
    self.widget.btnVisible.connect('toggled(bool)', self.change_visible)
    self.widget.btnVisible.toolTip = "显示/关闭 导管模型"
    self.widget.btnVisible.setStyleSheet(btnVisible_stylesheet)


    btnModify_visible = self.main.resourcePath('Icons/btnModify.png').replace('\\','/')
    btnModify_stylesheet = ""
    btnModify_stylesheet = btnModify_stylesheet + "QPushButton{image: url("+btnModify_visible+")}"
    self.widget.btnModify.connect('toggled(bool)', self.on_modify)
    self.widget.btnModify.toolTip = "修改靶点入点位置"
    self.widget.btnModify.setStyleSheet(btnModify_stylesheet)

    self.widget.radius_slider.connect('valueChanged(double)',lambda:self.on_normal_fiber_modify())
    self.widget.thick_slider.connect('valueChanged(double)',lambda:self.on_normal_fiber_modify())
    self.widget.length_slider.connect('valueChanged(double)',self.on_length_slider_changed)
    self.widget.rotate_slider.connect('valueChanged(double)',self.on_stl_rotate)
    self.widget.depth_slider.connect('valueChanged(double)',self.on_stl_depth)
    self.widget.rotate_slider_2.connect('valueChanged(double)',self.on_stl_rotate2)
    self.widget.depth_slider_2.connect('valueChanged(double)',self.on_stl_depth2)
    self.widget.opacity_slider.connect('valueChanged(double)',self.on_opacity_changed)

    self.qcolor = qt.QColor()
    self.qcolor.setRed(255)
    self.qcolor.setGreen(255)
    self.qcolor.setBlue(255)
    offset = 10
    self.widget.depth_label.move(1110,170+offset)
    self.widget.depth_slider.move(1110,170+offset)
    self.widget.rotate_label.move(1110,120+offset)
    self.widget.rotate_slider.move(1110,120+offset)
    self.widget.thick_label.move(1110,105+offset)
    self.widget.thick_slider.move(1110,105+offset)
    self.widget.radius_label.move(1110,165+offset)
    self.widget.radius_slider.move(1110,165+offset)
    self.widget.length_label.move(1110,135+offset)
    self.widget.length_slider.move(1110,135+offset)
    self.widget.rotate_slider_2.move(1110,135+offset)
    self.widget.depth_slider_2.move(1110,135+offset)
    self.widget.depth_label_2.move(1110,135+offset)
    self.widget.rotate_label_2.move(1110,135+offset)
    self.widget.opacity_label.move(1110,170+offset)
    self.widget.opacity_slider.move(1110,170+offset)
    if(self.style == self.style_normal):
      self.widget.thick_label.move(10,105+offset)
      self.widget.thick_slider.move(110,105+offset)
      self.widget.radius_label.move(10,165+offset)
      self.widget.radius_slider.move(110,165+offset)
      self.widget.length_label.move(10,135+offset)
      self.widget.length_slider.move(110,135+offset)
      self.widget.btnPalette.setVisible(True)
      self.widget.btnVisible.setVisible(True)
      self.widget.btnSetting.setVisible(False)
      self.widget.btnBushing.setVisible(False)  
    elif(self.style == self.style_stl_1 or self.style == self.style_stl_2 or self.style == self.style_stl_3 ):
      

      self.widget.depth_label.move(10,165+offset)
      self.widget.depth_slider.move(110,165+offset)
      self.widget.rotate_label.move(10,120+offset)
      self.widget.rotate_slider.move(110,120+offset)

      self.widget.btnSetting.move(430,22)
      self.widget.btnBushing.move(350,68)
      self.widget.btnPalette.setVisible(False)
      self.widget.btnVisible.setVisible(False)
      self.widget.btnSetting.setVisible(True)
      self.widget.btnBushing.setVisible(True)
    elif(self.style == self.style_stl_duruofei):
      self.widget.depth_label.move(10,165+offset)
      self.widget.depth_slider.move(110,165+offset)
      self.widget.rotate_label.move(10,120+offset)
      self.widget.rotate_slider.move(110,120+offset)
      self.widget.depth_label_2.move(10,210+offset)
      self.widget.depth_slider_2.move(110,210+offset)
      self.widget.rotate_label_2.move(10,255+offset)
      self.widget.rotate_slider_2.move(110,255+offset)
      self.widget.btnSetting.move(430,22)
      self.widget.btnAuto.move(350,68)
      self.widget.btnBushing.setVisible(False)
      self.widget.btnPalette.setVisible(False)
      self.widget.btnVisible.setVisible(False)
      self.widget.btnSetting.setVisible(True)
    elif(self.style == self.style_robot_arm):
      self.widget.length_label.move(10,105+offset)
      self.widget.length_label.setText("机械距离:")
      self.widget.length_slider.move(110,105+offset)
      self.widget.thick_label.move(10,135+offset)
      self.widget.thick_slider.move(110,135+offset)
      self.widget.thick_label.setText("保护区:")
      self.widget.opacity_label.move(10,165+offset)
      self.widget.opacity_slider.move(110,165+offset)
      self.widget.opacity_label.setText("透明度:")
      self.widget.btnPalette.setVisible(True)
      self.widget.btnVisible.setVisible(True)
      self.widget.btnSetting.setVisible(False)
      self.widget.btnBushing.setVisible(False)  
      self.widget.radius_slider.setValue(0.2)

  def on_length_slider_changed(self,val):
    if self.style == self.style_normal:
      self.on_normal_fiber_modify()
    if self.style == self.style_robot_arm:
      self.fresh_result()
      self.on_normal_fiber_modify()

  def on_duruofei_auto(self,is_trigger):
    self.du_map["is_trigger"] = is_trigger
    if not is_trigger:
      return
    util.singleShot(0,self.on_duruofei_auto_timer)
    
  def on_duruofei_auto_timer(self):
    if not self.du_map["is_trigger"]:
      return
    pui = util.getModuleWidget("PDuruofei").setting_panel_ui

    speed = 0.05
    speed = float(pui.le_speed.text)
    angle = 1
    angle = float(pui.le_degree.text)
    counts = 100
    counts = int(pui.le_couts.text)
    show_duruofei_animate = True
    show_duruofei_animate = pui.cb_show_animation.isChecked()
    print("speed:",speed)
    print("angle:",angle)
    print("counts:",counts)
    index = 0
    while True:
      index+=1
      if show_duruofei_animate:
        if index>1:
          break
      else:
        if index > counts:
          break
      
      stls = [self.stl_du_axis,self.stl_du_bar,self.stl_du_board,self.stl_du_tube]
      
      p1 = [40,0,0]
      p2 = [-40,0,0]
      p3 = [-0.3,-86,-5.3]
      p1_world = util.getModuleLogic("JTransformTool").get_global_point_from_ijk(p1,self.stl_du_board)
      p2_world = util.getModuleLogic("JTransformTool").get_global_point_from_ijk(p2,self.stl_du_board)
      p3_world = util.getModuleLogic("JTransformTool").get_global_point_from_ijk(p3,self.stl_du_bar)
      segmentationNode = util.getModuleLogic("JPuncturePlan").m_HeadSegmentationNode
      util.ShowNode3D(segmentationNode,True)
      if segmentationNode is None:
        util.showWarningText("请先创建头部的皮肤")
        self.du_map["is_trigger"] = False
        return
      sliceViewWidget = slicer.app.layoutManager().sliceWidget('Red')
      segmentationsDisplayableManager = sliceViewWidget.sliceView().displayableManagerByClassName("vtkMRMLSegmentationsDisplayableManager2D")
      segmentIds1 = vtk.vtkStringArray()
      segmentIds2 = vtk.vtkStringArray()
      segmentIds3 = vtk.vtkStringArray()
      segmentationsDisplayableManager.GetVisibleSegmentsForPosition(p1_world, segmentationNode.GetDisplayNode(), segmentIds1)
      segmentationsDisplayableManager.GetVisibleSegmentsForPosition(p2_world, segmentationNode.GetDisplayNode(), segmentIds2)
      segmentationsDisplayableManager.GetVisibleSegmentsForPosition(p3_world, segmentationNode.GetDisplayNode(), segmentIds3)
      delta_angle = -angle
      if segmentIds1.GetNumberOfValues()>0 and segmentIds2.GetNumberOfValues()>0 and segmentIds3.GetNumberOfValues()>0 :
        print("success moved")
        self.du_map["is_trigger"] = False
        return
      elif segmentIds1.GetNumberOfValues()>0 and segmentIds2.GetNumberOfValues()>0:
        if "depth_bar" not in self.du_map:
          self.du_map["depth_bar"] = 0
        self.du_map["depth_bar"]-=speed
        self.on_stl_depth2(self.du_map["depth_bar"])
      elif segmentIds1.GetNumberOfValues()>0:
        self.on_stl_rotate2(self.stl_rotate_angle_du+delta_angle)
      elif segmentIds2.GetNumberOfValues()>0:
        self.on_stl_rotate2(self.stl_rotate_angle_du-delta_angle)
      else:
        entry_point_world,_ = self.get_entry_point()
        target_point_world,_ = self.get_target_point()
        ne = np.array(entry_point_world)
        nt = np.array(target_point_world)
        norm1 = (ne-nt )/ np.linalg.norm(ne-nt)

        if "depth" not in self.du_map:
          self.du_map["depth"] = 0
        self.du_map["depth"]-=speed

        for stl in stls:
          util.getModuleLogic("JTransformTool").move_depth_along_vector(stl,self.du_map["depth"],norm1)
    
    if show_duruofei_animate:
      util.singleShot(0,self.on_duruofei_auto_timer)

  def add_bushing(self,int_type):
    if int_type == 5:
        stl_path = self.main.resourcePath('STL/5mm.lts').replace('\\','/')
    if int_type == 8:
        stl_path = self.main.resourcePath('STL/8mm.lts').replace('\\','/')
    model = util.loadModelSecret(stl_path)
    model.SetAttribute("model_list_id",self.unit_index_inner.__str__())
    model.SetAttribute("model_name","套管")
    model.GetDisplayNode().SetColor(115/255.0,115/255.0,255/255.0)
    self.set_component(model,"bushing")
    transform_node = self.stl_holder.GetParentTransformNode()
    new_transform_node = util.clone(transform_node)
    if new_transform_node:
      model.SetAndObserveTransformNodeID(new_transform_node.GetID())
    util.showWarningText(int_type.__str__()+"mm套管已添加")
  

  def ras_to_ijk_relative_to_model(self,world_point,node):
    ijkpoint = [0,0,0,1]
    volumeIjkToRas = vtk.vtkMatrix4x4()
    ras_to_ijk = vtk.vtkMatrix4x4()
    transformNode=node.GetParentTransformNode()
    transformNode.GetMatrixTransformToParent(volumeIjkToRas)
    vtk.vtkMatrix4x4.Invert(volumeIjkToRas, ras_to_ijk)
    ras_to_ijk.MultiplyPoint(np.append(world_point,1.0), ijkpoint)
    return ijkpoint[0:3]
  
  def ijk_to_ras_relative_to_model(self,ijk_point,node):
    world_point = [0,0,0,1]
    volumeIjkToRas = vtk.vtkMatrix4x4()
    transformNode=node.GetParentTransformNode()
    transformNode.GetMatrixTransformToParent(volumeIjkToRas)
    volumeIjkToRas.MultiplyPoint(np.append(ijk_point,1.0), world_point)
    return world_point[0:3]

  def multipoint(self,matrix,point):
    point1 = [0,0,0,1]
    matrix.MultiplyPoint(np.append(point,1.0), point1)
    return point1[0:3]

  
  def on_stl_depth2(self,val):
    stls=[]
    if self.style == self.style_stl_duruofei:
      stls = [self.stl_du_bar]


    entry_point_world,_ = self.get_entry_point()
    target_point_world,_ = self.get_target_point()

    volumeIjkToRas = vtk.vtkMatrix4x4()
    volumeIjkToRas.Identity()
    volumeIjkToRas.SetElement(1,1,0.71)
    volumeIjkToRas.SetElement(2,2,0.71)
    volumeIjkToRas.SetElement(1,2,-0.71)
    volumeIjkToRas.SetElement(2,1,-0.71)
    

   
    entry_point_ijk=self.ras_to_ijk_relative_to_model(entry_point_world,self.stl_du_needle)
    target_point_ijk=self.ras_to_ijk_relative_to_model(target_point_world,self.stl_du_needle)

    entry_point_ijk=self.multipoint(volumeIjkToRas,entry_point_ijk)
    target_point_ijk=self.multipoint(volumeIjkToRas,target_point_ijk)

    entry_point_world = self.ijk_to_ras_relative_to_model(entry_point_ijk,self.stl_du_board)
    target_point_world = self.ijk_to_ras_relative_to_model(target_point_ijk,self.stl_du_board)

    

    ne = np.array(entry_point_world)
    nt = np.array(target_point_world)
    norm1 = (ne-nt )/ np.linalg.norm(ne-nt)
    depth = val-self.stl_depth_du


    for stl in stls:
      util.getModuleLogic("JTransformTool").move_depth_along_vector(stl,depth,norm1)
    self.stl_depth_du = val
    self.widget.l1_info1.setText("穿刺深度:"+round((self.widget.depth_slider.value+120)/10,2).__str__()+"cm")
    self.update_archive_paras()
  
  def on_stl_depth(self,val):
    stls=[]
    if self.style == self.style_stl_1 or self.style == self.style_stl_2 or self.style == self.style_stl_3:
      stls = [self.stl_holder,self.stl_stick]
      stls.extend(self.stl_bushinglist)
    elif self.style == self.style_stl_duruofei:
      stls = [self.stl_du_board,self.stl_du_bar,self.stl_du_axis,self.stl_du_tube]

    entry_point_world,_ = self.get_entry_point()
    target_point_world,_ = self.get_target_point()
    ne = np.array(entry_point_world)
    nt = np.array(target_point_world)
    norm1 = (ne-nt )/ np.linalg.norm(ne-nt)
    depth = val-self.stl_depth

    for stl in stls:
      util.getModuleLogic("JTransformTool").move_depth_along_vector(stl,depth,norm1)
    self.stl_depth = val
    self.widget.l1_info1.setText("穿刺深度:"+round((self.widget.depth_slider.value+120)/10,2).__str__()+"cm")
    self.update_archive_paras()

  def on_stl_rotate2(self,val):
    stls=[]
    if self.style == self.style_stl_duruofei:
      stls = [self.stl_du_board,self.stl_du_bar]
    point_target = [0,100,30]
    point_input  = [0,-100,30]
    point_center = [0,0,30]
    point_target_word = [0,100,30,1]
    point_input_word  = [0,-100,30,1]
    point_center_word = [0,0,30,1]
    volumeIjkToRas = vtk.vtkMatrix4x4()
    transformNode=self.stl_du_axis.GetParentTransformNode()
    transformNode.GetMatrixTransformToParent(volumeIjkToRas)
    volumeIjkToRas.MultiplyPoint(np.append(point_target,1.0), point_target_word)
    volumeIjkToRas.MultiplyPoint(np.append(point_input,1.0), point_input_word)
    volumeIjkToRas.MultiplyPoint(np.append(point_center,1.0), point_center_word)
    point_target_word = point_target_word[0:3]
    point_input_word = point_input_word[0:3]
    point_center_word = point_center_word[0:3]
    ne = np.array(point_target_word)
    nt = np.array(point_input_word)
    norm1 = (ne-nt )/ np.linalg.norm(ne-nt)

    angle = val-self.stl_rotate_angle_du
    for stl in stls:
      util.getModuleLogic("JTransformTool").rotate_angle_along_vector(stl,(angle),point_center_word,norm1)
    self.stl_rotate_angle_du = val
    self.update_archive_paras()

  def on_stl_rotate(self,val):
    stls=[]
    if self.style == self.style_stl_1 or self.style == self.style_stl_2 or self.style == self.style_stl_3:
      stls = [self.stl_holder,self.stl_stick]
    elif self.style == self.style_stl_duruofei:
      stls = [self.stl_du_board,self.stl_du_bar,self.stl_du_axis,self.stl_du_tube]

    
    entry_point_world,_ = self.get_entry_point()
    target_point_world,_ = self.get_target_point()
    ne = np.array(entry_point_world)
    nt = np.array(target_point_world)
    focus_point = (ne+nt)/2
    norm1 = (ne-nt )/ np.linalg.norm(ne-nt)
    angle = val-self.stl_rotate_angle
    for stl in stls:
      util.getModuleLogic("JTransformTool").rotate_angle_along_vector(stl,(angle),focus_point,norm1)
    self.stl_rotate_angle = val
    self.update_archive_paras()

  def on_modify(self,is_trigger):
    if is_trigger:
      if self.entry_point:
        util.GetDisplayNode(self.entry_point).SetHandlesInteractive(True)
      if self.target_point:
        util.GetDisplayNode(self.target_point).SetHandlesInteractive(True)
    else:
      if self.entry_point:
        util.GetDisplayNode(self.entry_point).SetHandlesInteractive(False)
      if self.target_point:
        util.GetDisplayNode(self.target_point).SetHandlesInteractive(False)
      self.fresh_result()

  def change_visible(self,is_show):
    is_show = not is_show
    if self.style == self.style_normal or self.style == self.style_robot_arm:
      if self.fiber_model:
        util.ShowNode(self.fiber_model,is_show)
        util.ShowNode3D(self.fiber_model,is_show)
      if self.fiber_model_inner:
        util.ShowNode(self.fiber_model_inner,is_show)
        util.ShowNode3D(self.fiber_model_inner,is_show)

  def rotate_to_fiber(self):
    if self.entry_point is None:
      util.showWarningText("请添加靶点和入点之后再添加导管")
      return
    if self.target_point is None:
      util.showWarningText("请添加靶点和入点之后再添加导管")
      return
    if self.entry_point.GetNumberOfControlPoints() == 0:
      util.showWarningText("请添加靶点和入点之后再添加导管")
      return
    if self.target_point.GetNumberOfControlPoints() == 0:
      util.showWarningText("请添加靶点和入点之后再添加导管")
      return
    entry_point_world,_ = self.get_entry_point()
    target_point_world,_ = self.get_target_point()
    util.getModuleLogic("JTransformTool").rotate_to_vector(entry_point_world[0],entry_point_world[1],entry_point_world[2],target_point_world[0],target_point_world[1],target_point_world[2])
    

  def on_setting(self):
    widget = util.getModuleWidget("JManagerModel")
    
    if self.style == self.style_stl_1 or self.style == self.style_stl_2 or self.style == self.style_stl_3:
      index = self.stl_fiber.GetAttribute("model_list_id")
      model_id = self.stl_fiber.GetID()
    elif self.style == self.style_stl_duruofei:
      index = self.stl_du_needle.GetAttribute("model_list_id")
      model_id = self.stl_du_needle.GetID()
    else:
      index = 0
      model_id = self.stl_fiber.GetID()
    widget.show_list_with_index(index)
    util.send_event_str(util.Start_ModelList,model_id)
    util.reinit(background_node=self.main.logic.m_Node)

  def on_open_color_pad(self):
    if self.style == self.style_normal or self.style == self.style_robot_arm:
      qdialog = qt.QColorDialog()
      qdialog.connect('colorSelected(QColor)', self.on_get_color)
      qdialog.installEventFilter(slicer.util.mainWindow())
      qdialog.exec()
  
  def on_get_color(self,qcolor):
    self.qcolor = qcolor
    self.widget.btnPalette.setStyleSheet("background-color:rgb("+qcolor.red().__str__()+","+qcolor.green().__str__()+","+qcolor.blue().__str__()+");")
    if self.fiber_model:
      self.fiber_model.GetDisplayNode().SetColor([qcolor.red()/255.0,qcolor.green()/255.0,qcolor.blue()/255.0])

  def delete_unit(self):
    res = util.messageBox("确定删除当前导管吗",windowTitle=util.tr("提示"))
    if res == 0:
      return
    self.delete_unit_without_warning()

  def delete_unit_without_warning(self):
    print("delete_unit_without_warning",self.unit_index_inner)
    self.delete_normal_fiber()
    if self.entry_point:
      util.RemoveNode(self.entry_point)
      self.entry_point = None
    if self.target_point:
      util.RemoveNode(self.target_point)
      self.target_point = None
    
    self.widget.btnAddEntry.disconnect('toggled(bool)', self.on_add_entry_point)
    self.widget.btnAddTarget.disconnect('toggled(bool)', self.on_add_target_point)
    '''
      删除stl
    '''
    if self.stl_du_axis:
      transform_node = self.stl_du_axis.GetParentTransformNode()
      if transform_node is not None:
        util.RemoveNode(transform_node)
      util.RemoveNode(self.stl_du_axis)
      self.stl_du_axis = None
    if self.stl_du_needle:
      transform_node = self.stl_du_needle.GetParentTransformNode()
      if transform_node is not None:
        util.RemoveNode(transform_node)
      util.RemoveNode(self.stl_du_needle)
      self.stl_du_needle = None
    if self.stl_du_bar:
      transform_node = self.stl_du_bar.GetParentTransformNode()
      if transform_node is not None:
        util.RemoveNode(transform_node)
      util.RemoveNode(self.stl_du_bar)
      self.stl_du_bar = None
    if self.stl_du_needle:
      transform_node = self.stl_du_needle.GetParentTransformNode()
      if transform_node is not None:
        util.RemoveNode(transform_node)
      util.RemoveNode(self.stl_du_needle)
      self.stl_du_needle = None
    if self.stl_du_tube:
      transform_node = self.stl_du_tube.GetParentTransformNode()
      if transform_node is not None:
        util.RemoveNode(transform_node)
      util.RemoveNode(self.stl_du_tube)
      self.stl_du_tube = None

    if self.stl_stick:
      transform_node = self.stl_stick.GetParentTransformNode()
      if transform_node is not None:
        util.RemoveNode(transform_node)
      util.RemoveNode(self.stl_stick)
      self.stl_stick = None
    if self.stl_fiber:
      transform_node = self.stl_fiber.GetParentTransformNode()
      if transform_node is not None:
        util.RemoveNode(transform_node)
      util.RemoveNode(self.stl_fiber)
      self.stl_fiber = None
    if self.stl_holder:
      transform_node = self.stl_holder.GetParentTransformNode()
      if transform_node is not None:
        util.RemoveNode(transform_node)
      util.RemoveNode(self.stl_holder)
      self.stl_holder = None
    for stl in self.stl_bushinglist:
      transform_node = stl.GetParentTransformNode()
      if transform_node is not None:
        util.RemoveNode(transform_node)
      util.RemoveNode(stl)
    self.stl_bushinglist = []
    if self.main:
      self.main.delete_unit(self)
    
  
  def get_entry_point(self):
    #开始创建的时候,如果没有place直接点击右键,也会创建一个点,这个点的默认位置是0,0,0,但是不会显示出来
    entry_point_world = [0,0,0]
    self.entry_point.GetNthControlPointPositionWorld(0, entry_point_world)
    flag = False
    if entry_point_world != [0,0,0]:
      flag = True
    return entry_point_world,flag

  def get_target_point(self):
    #开始创建的时候,如果没有place直接点击右键,也会创建一个点,这个点的默认位置是0,0,0,但是不会显示出来
    target_point_world = [0,0,0]
    self.target_point.GetNthControlPointPositionWorld(0, target_point_world)
    flag = False
    if target_point_world != [0,0,0]:
      flag = True
    return target_point_world,flag

  def on_add_entry_point(self,is_trigger):
    if not is_trigger:
      return
    #如果没有创建,开始创建
    if self.entry_point is None:
      entry_point = util.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
      entry_point.SetName("EntryPoint")
      entry_point.SetAttribute("node_type",self.style.__str__())
      self.set_component(entry_point,"entry_point")
    else:
      util.RemoveNode(self.entry_point)
      entry_point = util.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
      entry_point.SetName("EntryPoint")
      entry_point.SetAttribute("node_type",self.style.__str__())
      self.set_component(entry_point,"entry_point")
      # #开始创建的时候,如果没有place直接点击右键,也会创建一个点,这个点的默认位置是0,0,0,但是不会显示出来
      # entry_point_world,flag = self.get_entry_point()
      # #所以上一步如果右键取消了,那么我们重新创建一个点
      # #如果存在一个不是[0,0,0]的点,那么我们认为这个点已经在前面的步骤创建成功了
      # if flag:
      #   slicer.vtkMRMLSliceNode.JumpAllSlices(slicer.mrmlScene, entry_point_world[0],entry_point_world[1],entry_point_world[2], 0)
      #   self.widget.btnAddEntry.setChecked(False)
      #   return
      # else:
      #   util.RemoveNode(self.entry_point)
      #   self.entry_point = util.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
      
    
    display_node = util.GetDisplayNode(self.entry_point)
    display_node.SetPointLabelsVisibility(False)
    interactionNode = slicer.app.applicationLogic().GetInteractionNode()
    selectionNode = slicer.app.applicationLogic().GetSelectionNode()
    selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
    selectionNode.SetActivePlaceNodeID(self.entry_point.GetID())
    interactionNode.SetCurrentInteractionMode(interactionNode.Place)
    

  def on_point_hide_3d(self,is_hide):
    if self.style == self.style_normal or self.style == self.style_robot_arm:
      if is_hide:
        self.set_info("point_3d",util.Visibility3D(self.fiber_model))
        util.ShowNode3D(self.fiber_model,False)
        util.ShowNode3D(self.fiber_model_inner,False)
      else:
        util.ShowNode3D(self.fiber_model,self.infos["point_3d"])
        util.ShowNode3D(self.fiber_model_inner,self.infos["point_3d"])
    else:
      if is_hide:
        util.ShowNode3D(self.stl_fiber,False)
        util.ShowNode3D(self.stl_holder,False)
        util.ShowNode3D(self.stl_stick,False)
        for stl in self.stl_bushinglist:
          util.ShowNode3D(stl,False)
      else:
        util.ShowNode3D(self.stl_fiber,True)
        util.ShowNode3D(self.stl_holder,True)
        util.ShowNode3D(self.stl_stick,True)
        for stl in self.stl_bushinglist:
          util.ShowNode3D(stl,True)

  def set_info(self,key,value):
    print("set_info",key,value)
    self.infos[key] = value
      
  def on_entry_point_placed(self,caller,event):
    interactionNode = slicer.app.applicationLogic().GetInteractionNode()
    interactionNode.SetCurrentInteractionMode(interactionNode.ViewTransform)
    self.widget.btnAddEntry.setChecked(False)
    label = util.findChild(self.widget.btnAddEntry,"labelText")
    label.setText("定位入点")
    util.send_event_str(util.JAddFiber_EntryPoint_Placed,self.unit_index_inner.__str__())
    self.fresh_result()
    if self.style == self.style_normal:
      self.widget.btnVisible.setChecked(True)
      self.widget.btnVisible.setChecked(False)
    else:
      util.ShowNode(self.stl_stick,True)
      util.ShowNode(self.stl_fiber,True)
      util.ShowNode(self.stl_holder,True)
      util.ShowNode3D(self.stl_stick,True)
      util.ShowNode3D(self.stl_fiber,True)
      util.ShowNode3D(self.stl_holder,True)
      for stl in self.stl_bushinglist:
        util.ShowNode(stl,True)

  def on_add_target_point(self,is_trigger):
    print("on_add_target_point:",is_trigger,self.unit_index_inner)
    if not is_trigger:
      return
    if self.target_point is None:
      target_point = util.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
      target_point.SetName("TargetPoint")
      self.set_component(target_point,"target_point")
    else:
      util.RemoveNode(self.target_point)
      target_point = util.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
      target_point.SetName("TargetPoint")
      self.set_component(target_point,"target_point")
      # target_point_world,flag = self.get_target_point()
      # if flag:
      #   slicer.vtkMRMLSliceNode.JumpAllSlices(slicer.mrmlScene, target_point_world[0],target_point_world[1],target_point_world[2], 0)
      #   self.widget.btnAddTarget.setChecked(False)
      #   return
      # else:
      #   util.RemoveNode(self.target_point)
      #   self.target_point = util.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
      

    display_node = self.target_point.GetDisplayNode()
    if not display_node:
      self.target_point.CreateDefaultDisplayNodes()
      display_node = self.target_point.GetDisplayNode()
    display_node.SetPointLabelsVisibility(False)

    interactionNode = slicer.app.applicationLogic().GetInteractionNode()
    selectionNode = slicer.app.applicationLogic().GetSelectionNode()
    selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
    selectionNode.SetActivePlaceNodeID(self.target_point.GetID())
    interactionNode.SetCurrentInteractionMode(interactionNode.Place)
    


  def on_target_point_placed(self,caller,event):
    print("on place target point","1",self.unit_index_inner)
    interactionNode = slicer.app.applicationLogic().GetInteractionNode()
    interactionNode.SetCurrentInteractionMode(interactionNode.ViewTransform)
    self.widget.btnAddTarget.setChecked(False)
    label = util.findChild(self.widget.btnAddTarget,"labelText")
    label.setText("定位靶点")
    util.send_event_str(util.JAddFiber_TargetPoint_Placed,self.unit_index_inner.__str__())
    self.fresh_result()
    if self.style == self.style_normal:
      self.widget.btnVisible.setChecked(True)
      self.widget.btnVisible.setChecked(False)
    else:
      util.ShowNode(self.stl_stick,True)
      util.ShowNode(self.stl_fiber,True)
      util.ShowNode(self.stl_holder,True)
      util.ShowNode3D(self.stl_stick,True)
      util.ShowNode3D(self.stl_fiber,True)
      util.ShowNode3D(self.stl_holder,True)
      for stl in self.stl_bushinglist:
        util.ShowNode(stl,True)

  def ensure_load_robot_arm_stl(self,entry_point_world,target_point_world):
    len1 = self.widget.length_slider.value
    if self.stl_robot_arm is None:
      stl_path = self.main.resourcePath('STL/huannengqi.stl').replace('\\','/')
      self.stl_robot_arm = util.loadModel(stl_path)
      self.stl_robot_arm.SetAttribute("model_list_id",self.unit_index_inner.__str__())
      self.stl_robot_arm.SetAttribute("model_name","robot_arm")
      util.ShowModel2D(self.stl_robot_arm,2)
      self.stl_robot_arm.GetDisplayNode().SetColor(255/255.0,238/255.0,0/255.0)
      util.AddNode(self.stl_robot_arm)
      util.GetDisplayNode(self.stl_robot_arm).SetOpacity(0.5)

    old_fiber_transform_node = self.stl_robot_arm.GetParentTransformNode()
    util.RemoveNode((old_fiber_transform_node))
    self.stl_robot_arm.SetAndObserveTransformNodeID(None)
    bounds = [0]*6
    self.stl_robot_arm.GetRASBounds(bounds)
    util.getModuleLogic("JTransformTool").rotate_stl_model_to_vector_full(self.stl_robot_arm,entry_point_world,target_point_world,len1)

  def ensure_load_DuRuoFei_stl(self,entry_point_world,target_point_world):
    if self.stl_du_axis is None:
      stl_path = self.main.resourcePath('STL/duruofei/hAxis.stl').replace('\\','/')
      self.stl_du_axis = util.loadModel(stl_path)
      self.stl_du_axis.SetAttribute("model_list_id",self.unit_index_inner.__str__())
      self.stl_du_axis.SetAttribute("model_name","axis")
      util.ShowModel2D(self.stl_du_axis,2)
      self.stl_du_axis.GetDisplayNode().SetColor(46/255.0,156/255.0,34/255.0)
      util.AddNode(self.stl_du_axis)
    if self.stl_du_tube is None:
      stl_path = self.main.resourcePath('STL/duruofei/pTube.stl').replace('\\','/')
      self.stl_du_tube = util.loadModel(stl_path)
      self.stl_du_tube.SetAttribute("model_list_id",self.unit_index_inner.__str__())
      self.stl_du_tube.SetAttribute("model_name","tube")
      util.ShowModel2D(self.stl_du_tube,2)
      self.stl_du_tube.GetDisplayNode().SetColor(255/255.0,238/255.0,0/255.0)
      util.AddNode(self.stl_du_tube)
    if self.stl_du_board is None:
      stl_path = self.main.resourcePath('STL/duruofei/rBoard.stl').replace('\\','/')
      self.stl_du_board = util.loadModel(stl_path)
      self.stl_du_board.SetAttribute("model_list_id",self.unit_index_inner.__str__())
      self.stl_du_board.SetAttribute("model_name","board")
      util.ShowModel2D(self.stl_du_board,2)
      self.stl_du_board.GetDisplayNode().SetColor(115/255.0,255/255.0,255/255.0)
      util.AddNode(self.stl_du_board)
    if self.stl_du_bar is None:
      stl_path = self.main.resourcePath('STL/duruofei/sBar.stl').replace('\\','/')
      self.stl_du_bar = util.loadModel(stl_path)
      self.stl_du_bar.SetAttribute("model_list_id",self.unit_index_inner.__str__())
      self.stl_du_bar.SetAttribute("model_name","bar")
      util.ShowModel2D(self.stl_du_bar,2)
      self.stl_du_bar.GetDisplayNode().SetColor(115/255.0,115/255.0,255/255.0)
      util.AddNode(self.stl_du_bar)
    if self.stl_du_needle is None:
      stl_path = self.main.resourcePath('STL/duruofei/vNeedle.stl').replace('\\','/')
      self.stl_du_needle = util.loadModel(stl_path)
      self.stl_du_needle.SetAttribute("model_list_id",self.unit_index_inner.__str__())
      self.stl_du_needle.SetAttribute("model_name","needle")
      util.ShowModel2D(self.stl_du_needle,2)
      self.stl_du_needle.GetDisplayNode().SetColor(115/255.0,225/255.0,155/255.0)
      util.AddNode(self.stl_du_needle)
    
    old_fiber_transform_node = self.stl_du_needle.GetParentTransformNode()
    util.RemoveNode((old_fiber_transform_node))
    self.stl_du_needle.SetAndObserveTransformNodeID(None)
    bounds = [0]*6
    self.stl_du_needle.GetRASBounds(bounds)
    util.getModuleLogic("JTransformTool").rotate_stl_model_to_vector(self.stl_du_needle,entry_point_world,target_point_world,bounds[5]-bounds[4])
    transform_node = self.stl_du_needle.GetParentTransformNode()

    stllist = [self.stl_du_axis,self.stl_du_tube,self.stl_du_board,self.stl_du_bar]
    for stl in stllist:
      old_stick_transform_node = stl.GetParentTransformNode()
      util.RemoveNode((old_stick_transform_node))
      cloned_node = util.clone(transform_node)
      stl.SetAndObserveTransformNodeID(cloned_node.GetID())
  
  def ensure_load_DrShi_stl(self,entry_point_world,target_point_world):
    import os
    if self.stl_fiber is None:
      stl_path = self.main.resourcePath('STL/t1_fiber.lts').replace('\\','/')
      if self.style == self.style_stl_1:
        stl_path = self.main.resourcePath('STL/0/t1_fiber.lts').replace('\\','/')
      if self.style == self.style_stl_2:
        stl_path = self.main.resourcePath('STL/1/t1_fiber.lts').replace('\\','/')
      if self.style == self.style_stl_3:
        stl_path = self.main.resourcePath('STL/2/t1_fiber.lts').replace('\\','/')
      stl_fiber = util.loadModelSecret(stl_path)
      stl_fiber.SetAttribute("model_list_id",self.unit_index_inner.__str__())
      stl_fiber.SetAttribute("model_name","导针")
      stl_fiber.GetDisplayNode().SetColor(46/255.0,156/255.0,34/255.0)
      self.set_component(stl_fiber,"stl_fiber")
      util.ShowModel2D(self.stl_fiber,2)
    if self.stl_stick is None:
      if self.style == self.style_stl_1:
        stl_path = self.main.resourcePath('STL/0/t1_stick.lts').replace('\\','/')
      if self.style == self.style_stl_2:
        stl_path = self.main.resourcePath('STL/1/t1_stick.lts').replace('\\','/')
      if self.style == self.style_stl_3:
        stl_path = self.main.resourcePath('STL/2/t1_stick.lts').replace('\\','/')
      stl_stick = util.loadModelSecret(stl_path)
      stl_stick.SetAttribute("model_list_id",self.unit_index_inner.__str__())
      stl_stick.SetAttribute("model_name","直柱")
      stl_stick.GetDisplayNode().SetColor(255/255.0,238/255.0,0/255.0)
      self.set_component(stl_stick,"stl_stick")
    if self.stl_holder is None:
      if self.style == self.style_stl_1:
        stl_path = self.main.resourcePath('STL/0/t1_holder.lts').replace('\\','/')
      if self.style == self.style_stl_2:
        stl_path = self.main.resourcePath('STL/1/t1_holder.lts').replace('\\','/')
      if self.style == self.style_stl_3:
        stl_path = self.main.resourcePath('STL/2/t1_holder.lts').replace('\\','/')
      stl_holder = util.loadModelSecret(stl_path)
      stl_holder.SetAttribute("model_list_id",self.unit_index_inner.__str__())
      stl_holder.SetAttribute("model_name","弯柱")
      stl_holder.GetDisplayNode().SetColor(115/255.0,255/255.0,255/255.0)
      self.set_component(stl_holder,"stl_holder")


    old_fiber_transform_node = self.stl_fiber.GetParentTransformNode()
    util.RemoveNode((old_fiber_transform_node))
    self.stl_fiber.SetAndObserveTransformNodeID(None)
    bounds = [0]*6
    self.stl_fiber.GetRASBounds(bounds)
    util.getModuleLogic("JTransformTool").rotate_stl_model_to_vector(self.stl_fiber,entry_point_world,target_point_world,bounds[5]-bounds[4])
    transform_node = self.stl_fiber.GetParentTransformNode()

    old_stick_transform_node = self.stl_stick.GetParentTransformNode()
    util.RemoveNode((old_stick_transform_node))
    old_holder_transform_node = self.stl_holder.GetParentTransformNode()
    util.RemoveNode((old_holder_transform_node))
    self.stl_stick.SetAndObserveTransformNodeID( util.clone(transform_node).GetID())
    self.stl_holder.SetAndObserveTransformNodeID(util.clone(transform_node).GetID())

    for stl in self.stl_bushinglist:
      clonedItemID3 = slicer.modules.subjecthierarchy.logic().CloneSubjectHierarchyItem(shNode, itemIDToClone)
      new_transform_node = shNode.GetItemDataNode(clonedItemID3)
      transform_node = stl.GetParentTransformNode()
      util.RemoveNode((transform_node))
      if new_transform_node:
        stl.SetAndObserveTransformNodeID(new_transform_node.GetID())
    
    
  def on_opacity_changed(self,val):
    if self.style == self.style_robot_arm:
      if self.fiber_model:
        util.GetDisplayNode(self.fiber_model).SetSliceIntersectionOpacity(val/100)
        util.GetDisplayNode(self.fiber_model).SetOpacity(val/100)

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
    
    entry_point_world,_ = self.get_entry_point()
    target_point_world,_ = self.get_target_point()
    self.delete_normal_fiber()
    fiber_model,fiber_model_inner = self.on_add_normal_fiber(entry_point_world,target_point_world,self.qcolor,self.widget.length_slider.value,self.widget.radius_slider.value/2,self.widget.thick_slider.value)
    self.set_component(fiber_model,"fiber_model")
    self.set_component(fiber_model_inner,"fiber_model_inner")
    
    self.update_archive_paras()

  def delete_points(self):
    if self.entry_point:
      util.RemoveNode(self.entry_point)
      self.entry_point = None
    if self.target_point:
      util.RemoveNode(self.target_point)
      self.target_point = None

  def update_archive_paras(self):
    if self.entry_point:
      self.entry_point.SetAttribute("thick_slider",self.widget.thick_slider.value.__str__())
      self.entry_point.SetAttribute("rotate_slider_2",self.widget.rotate_slider_2.value.__str__())
      self.entry_point.SetAttribute("rotate_slider",self.widget.rotate_slider.value.__str__())
      self.entry_point.SetAttribute("radius_slider",self.widget.radius_slider.value.__str__())
      self.entry_point.SetAttribute("length_slider",self.widget.length_slider.value.__str__())
      self.entry_point.SetAttribute("depth_slider_2",self.widget.depth_slider_2.value.__str__())
      self.entry_point.SetAttribute("depth_slider",self.widget.depth_slider.value.__str__())

  def set_component(self,node,type):
    print("set_component",type)
    node.SetAttribute("fiber_unit_id",self.unit_index_inner.__str__())
    node.SetAttribute("fiber_unit_type",type.__str__())
    if type == "fiber_model":
      self.fiber_model = node
    if type == "fiber_model_inner":
      self.fiber_model_inner = node
    if type == "target_point":
      self.target_point = node
      self.target_point.AddObserver(slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent, self.on_target_point_placed)
      self.target_point.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, lambda a,b:self.fresh_result())
      self.target_point.AddObserver(slicer.vtkMRMLMarkupsNode.PointStartInteractionEvent, lambda A,b:self.on_point_hide_3d(True))
      self.target_point.AddObserver(slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent, lambda A,b:self.on_point_hide_3d(False))
    if type == "entry_point":
      self.entry_point = node
      self.entry_point.AddObserver(slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent, self.on_entry_point_placed)
      self.entry_point.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, lambda a,b:self.fresh_result())
      self.entry_point.AddObserver(slicer.vtkMRMLMarkupsNode.PointStartInteractionEvent, lambda A,b:self.on_point_hide_3d(True))
      self.entry_point.AddObserver(slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent, lambda A,b:self.on_point_hide_3d(False))
    if type == "stl_fiber":
      self.stl_fiber = node
    if type == "stl_holder":
      self.stl_holder = node
    if type == "stl_stick":
      self.stl_stick = node
    if type == "bushing":
      while len(self.stl_bushinglist) > 0 :
        node = self.stl_bushinglist[0]
        util.RemoveNode(node)
        self.stl_bushinglist.pop(0)
      self.stl_bushinglist=[]
      self.stl_bushinglist.append(node)

  
  def load_archive(self,id,nodelist):
    print("fiber unit load_archive",id,len(nodelist))
    self.unit_index_inner = id
    cloned_node = None
    for node in nodelist:
      type = node.GetAttribute("fiber_unit_type")
      if type == "entry_point":
        cloned_node = util.clone(node)
    for node in nodelist:
      self.set_component(node,node.GetAttribute("fiber_unit_type"))

    if cloned_node.GetAttribute("thick_slider") is not None:
      self.widget.thick_slider.setValue(float(cloned_node.GetAttribute("thick_slider")))
    if cloned_node.GetAttribute("rotate_slider_2") is not None:
      self.widget.rotate_slider_2.setValue(float(cloned_node.GetAttribute("rotate_slider_2")))
    if cloned_node.GetAttribute("rotate_slider") is not None:
      self.widget.rotate_slider.setValue(float(cloned_node.GetAttribute("rotate_slider")))
    if cloned_node.GetAttribute("radius_slider") is not None:
      self.widget.radius_slider.setValue(float(cloned_node.GetAttribute("radius_slider")))
    if cloned_node.GetAttribute("length_slider") is not None:
      self.widget.length_slider.setValue(float(cloned_node.GetAttribute("length_slider")))
    if cloned_node.GetAttribute("depth_slider_2") is not None:
      self.widget.depth_slider_2.setValue(float(cloned_node.GetAttribute("depth_slider_2")))
    if cloned_node.GetAttribute("depth_slider") is not None:
      self.widget.depth_slider.setValue(float(cloned_node.GetAttribute("depth_slider")))
    util.RemoveNode(cloned_node)

  def delete_normal_fiber(self):
    if self.fiber_model is not None:
      transform_node = self.fiber_model.GetParentTransformNode()
      if transform_node is not None:
        util.RemoveNode(transform_node)
    if self.fiber_model:
      util.RemoveNode(self.fiber_model)
      self.fiber_model = None
    if self.fiber_model_inner:
      util.RemoveNode(self.fiber_model_inner)
      self.fiber_model_inner = None

  def on_add_normal_fiber(self,entry_point_world,target_point_world,qcolor,length,radius,thick):
    # model_node = self.add_hollow_cylinder(radius,radius+thick,length,qcolor.red()/255.0,qcolor.green()/255.0,qcolor.blue()/255.0,)
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
    cy_source = vtk.vtkCylinderSource()
    cy_source.SetHeight(height)
    cy_source.SetRadius(radius)
    cy_source.SetResolution(160)
    modelNode = slicer.modules.models.logic().AddModel(cy_source.GetOutputPort())
    modelNode.GetDisplayNode().SetColor([red,green,blue])
    modelNode.GetDisplayNode().SetVisibility2D(True)
    modelNode.GetDisplayNode().SetSliceIntersectionThickness(2)

    cy_source_inner = vtk.vtkCylinderSource()
    cy_source_inner.SetHeight(height)
    cy_source_inner.SetRadius(inner_radius)
    cy_source_inner.SetResolution(160)
    modelNode_inner = slicer.modules.models.logic().AddModel(cy_source_inner.GetOutputPort())
    
    modelNode_inner.GetDisplayNode().SetSliceIntersectionThickness(2)
    modelNode.SetAttribute("JAddFiberWidget_Fiber","1")
    modelNode_inner.SetAttribute("JAddFiberWidget_FiberInner","1")
    return modelNode,modelNode_inner

  

  def fresh_result(self):
    if self.entry_point is None:
      #print("a1")
      return
    if self.target_point is None:
      #print("a2")
      return
    if self.entry_point.GetNumberOfControlPoints() == 0:
      #print("a3")
      return
    if self.target_point.GetNumberOfControlPoints() == 0:
      #print("a4")
      return
    util.send_event_str(util.JAddFiber_TargetPoint_Placed,self.unit_index_inner.__str__())
    util.send_event_str(util.JAddFiber_EntryPoint_Placed,self.unit_index_inner.__str__())
    util.ShowNode3D(self.fiber_model,False)
    util.ShowNode3D(self.fiber_model_inner,False)
    util.ShowNode3D(self.stl_fiber,False)
    util.ShowNode3D(self.stl_holder,False)
    util.ShowNode3D(self.stl_stick,False)
    for stl in self.stl_bushinglist:
      util.ShowNode3D(stl,False)

    entry_point_world,_ = self.get_entry_point()
    target_point_world,_ = self.get_target_point()
    
    

    if self.style == self.style_normal or self.style == self.style_robot_arm:
      distance = np.sqrt( (entry_point_world[0]-target_point_world[0])*(entry_point_world[0]-target_point_world[0])+
                          (entry_point_world[1]-target_point_world[1])*(entry_point_world[1]-target_point_world[1])+
                          (entry_point_world[2]-target_point_world[2])*(entry_point_world[2]-target_point_world[2])
                          )
      self.widget.l1_info1.setText("入点到靶点距离:"+round(distance, 2).__str__()+"mm")
      if self.fiber_model and self.fiber_model_inner:
        
        util.getModuleLogic("JTransformTool").rotate_fiber_model_to_vector(self.fiber_model,entry_point_world,target_point_world,self.widget.length_slider.value)
        old_transform_node = self.fiber_model_inner.GetParentTransformNode()
        util.RemoveNode(old_transform_node)
        transform_node = self.fiber_model.GetParentTransformNode()
        self.fiber_model_inner.SetAndObserveTransformNodeID(transform_node.GetID())
      else:
        fiber_model,fiber_model_inner = self.on_add_normal_fiber(entry_point_world,target_point_world,self.qcolor,self.widget.length_slider.value,self.widget.radius_slider.value/2,self.widget.thick_slider.value)
        self.set_component(fiber_model,"fiber_model")
        self.set_component(fiber_model_inner,"fiber_model_inner")
        util.GetDisplayNode(self.fiber_model).SetSelectable(False)
        util.GetDisplayNode(self.fiber_model_inner).SetSelectable(False)
      if self.style == self.style_robot_arm:
        self.ensure_load_robot_arm_stl(entry_point_world,target_point_world)
    elif self.style == self.style_stl_1 or self.style == self.style_stl_2 or self.style == self.style_stl_3:
      self.widget.l1_info1.setText("穿刺深度:"+round((self.widget.depth_slider.value+120)/10,2).__str__()+"cm")
      self.ensure_load_DrShi_stl(entry_point_world,target_point_world)
      old_depth = self.stl_depth
      old_angle = self.stl_rotate_angle
      self.stl_depth = 0
      self.stl_rotate_angle = -50
      self.widget.rotate_slider.setValue(old_angle)
      self.widget.depth_slider.setValue(old_depth)
      self.on_stl_depth(old_depth)
      self.on_stl_rotate(old_angle)
    elif self.style == self.style_stl_duruofei:
      self.ensure_load_DuRuoFei_stl(entry_point_world,target_point_world)
    self.main.refresh_tab()

    

