from __main__ import vtk, slicer,qt
import slicer.util as util
import numpy as np

class FiberUnit:
  tag = None
  entry_point = None
  target_point = None
  
  widget = None
  main = None
  qcolor = None

  #每一个导管工具都有一个独一无二的编号
  unit_index_inner = 0
  
  #代表了导管的类型
  style = None
  ui = None
  resourcelist = {}
  def __init__(self,style):
    self.style = style
    self.unit_index_inner = util.global_int_index
    util.global_int_index=util.global_int_index+1
  
  def get_resource_list(self):
    txt = ""
    for key in self.resourcelist:
      value = self.resourcelist[key]
      txt = txt+key+":\t\t"+value+"\n"
    filepath = util.get_resource("fiber_base.txt",use_default_path=False)
    if txt != "":
      with open(filepath, "w") as file:
        file.write(txt)
    return txt

  def set_widget(self,in_widget,main):
    self.widget = in_widget
    self.ui = slicer.util.childWidgetVariables(self.widget)
    self.main = main
    
    self.ui.btnAddEntry.connect('toggled(bool)', self.on_add_entry_point)
    self.ui.btnAddTarget.connect('toggled(bool)', self.on_add_target_point)

    

    rname = "fiber_delete.png"
    self.resourcelist[rname] = "删除当前的导向器"
    
    
    rname = "fiber_reset_camera.png"
    self.resourcelist[rname] = "点击恢复到默认设置"
    btnDirectionNormal_visible = util.get_resource(rname)
    btnDirectionNormal_stylesheet = ""
    btnDirectionNormal_stylesheet = btnDirectionNormal_stylesheet + "QPushButton{image: url("+btnDirectionNormal_visible+")}"
    #self.ui.btnReset.connect('clicked()', self.on_reset)
    #self.ui.btnReset.toolTip = self.resourcelist[rname]
    #self.ui.btnReset.setStyleSheet(btnDirectionNormal_stylesheet)


    rname = "fiber_direction_camera.png"
    self.resourcelist[rname] = "点击切换到导向器视角/再点击恢复默认视角"
    btnDirectionFiber_visible = util.get_resource(rname)
    btnDirectionFiber_stylesheet = ""
    btnDirectionFiber_stylesheet = btnDirectionFiber_stylesheet + "QPushButton{image: url("+btnDirectionFiber_visible+")}"
    self.ui.btnDirectionFiber.connect('toggled(bool)', self.rotate_to_fiber)
    self.ui.btnDirectionFiber.toolTip = self.resourcelist[rname]

    

    

    self.qcolor = qt.QColor()
    self.qcolor.setRed(255)
    self.qcolor.setGreen(255)
    self.qcolor.setBlue(255)

      

  def on_length_slider_changed(self,val):
    raise Exception("virtual method")

  
  
  

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

  
  
  
  def on_stl_depth(self,val):
    pass

  def GetID(self):
    if self.entry_point:
      return self.entry_point.GetAttribute("fiber_unit_id")
    return None

  def on_stl_rotate(self,val):
    pass

  def on_modify(self,is_trigger):
    if is_trigger:
      if self.entry_point:
        pass
        #util.GetDisplayNode(self.entry_point).SetHandlesInteractive(True)
      if self.target_point:
        #util.GetDisplayNode(self.target_point).SetHandlesInteractive(True)
        pass
    else:
      if self.entry_point:
        #util.GetDisplayNode(self.entry_point).SetHandlesInteractive(False)
        pass
      if self.target_point:
        #util.GetDisplayNode(self.target_point).SetHandlesInteractive(False)
        pass
      self.fresh_result()

  def change_visible(self,is_show):
    raise Exception("virtual method")

  def rotate_to_fiber(self,boo):
    scene_view_node_name = f"scene_{self.entry_point.GetID()}_view"
    scene_view_node = util.getFirstNodeByName(scene_view_node_name)
    if boo:
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
      
      
      
      if scene_view_node:
        util.RemoveNode(scene_view_node)
      if True:
        util.getModuleLogic("SceneViews").CreateSceneView(scene_view_node_name,"abc",1,vtk.vtkImageData()) 
      util.singleShot(0,lambda:util.getModuleLogic("JTransformTool").rotate_to_vector(entry_point_world[0],entry_point_world[1],entry_point_world[2],target_point_world[0],target_point_world[1],target_point_world[2]))
      
    else:
      if scene_view_node:
        scene_view_node.AddMissingNodes()
        if True:
          util.getModuleLogic("SceneViews").RestoreSceneView(scene_view_node.GetID(),True)
      else:
        util.reinit()
    

  def on_setting(self):
    raise Exception("virtual method")

  def on_open_color_pad(self):
    raise Exception("virtual method")
  
  def destroy(self):
    raise Exception("need destroy on sub child")
  
  def delete_unit(self):
    res = util.messageBox("确定删除吗",windowTitle=util.tr("提示"))
    if res == 0:
      return
    self.delete_unit_without_warning()

  def delete_unit_without_warning(self):
    if self.main:
      self.main.delete_unit(self)
    print("delete_unit_without_warning",self.unit_index_inner)
    if self.entry_point:
      util.RemoveNode(self.entry_point)
      self.entry_point = None
    if self.target_point:
      util.RemoveNode(self.target_point)
      self.target_point = None
    self.ui.btnAddEntry.disconnect('toggled(bool)', self.on_add_entry_point)
    self.ui.btnAddTarget.disconnect('toggled(bool)', self.on_add_target_point)
    
    

    
    
  
  def get_entry_point(self):
    #开始创建的时候,如果没有place直接点击右键,也会创建一个点,这个点的默认位置是0,0,0,但是不会显示出来
    if not self.entry_point:
      return "",False
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
      # util.RemoveNode(self.entry_point)
      # entry_point = util.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
      # entry_point.SetName("EntryPoint")
      # entry_point.SetAttribute("node_type",self.style.__str__())
      # self.set_component(entry_point,"entry_point")
      self.entry_point.RemoveAllControlPoints()
      
    
    display_node = util.GetDisplayNode(self.entry_point)
    display_node.SetPointLabelsVisibility(False)
    display_node.SetSelectedColor([1,0.3,0.8])
    interactionNode = slicer.app.applicationLogic().GetInteractionNode()
    selectionNode = slicer.app.applicationLogic().GetSelectionNode()
    selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
    selectionNode.SetActivePlaceNodeID(self.entry_point.GetID())
    interactionNode.SetCurrentInteractionMode(interactionNode.Place)
    

  def on_point_hide_3d(self,is_hide):
    raise Exception("virtual method")


  def on_reset(self):
    self.reset_slider()
  
      
  def on_entry_point_placed(self,caller,event):
    self._on_landing_to_model(caller,util.getFirstNodeByName("皮肤"))
    self.reset_slider()
    interactionNode = slicer.app.applicationLogic().GetInteractionNode()
    interactionNode.SetCurrentInteractionMode(interactionNode.ViewTransform)
    self.ui.btnAddEntry.setChecked(False)
    # label = util.findChild(self.ui.btnAddEntry,"labelText")
    # label.setText("定位入点")
    util.send_event_str(util.JAddFiber_EntryPoint_Placed,self.unit_index_inner.__str__())
    self.fresh_result()
    util.singleShot(100,self.check_points_placed)
    #util.GetDisplayNode(self.entry_point).SetHandlesInteractive(True)
    util.GetDisplayNode(self.entry_point).SetInteractionHandleScale(0.99)
    util.send_event_str(1431222,"message")
    self.entry_point.SetNthControlPointLabel(0,"EP")
    display_node = util.GetDisplayNode(self.entry_point)
    display_node.SetPointLabelsVisibility(True)
    

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
      #self.target_point.RemoveAllControlPoints()

    display_node = self.target_point.GetDisplayNode()
    if not display_node:
      self.target_point.CreateDefaultDisplayNodes()
      display_node = self.target_point.GetDisplayNode()
    display_node.SetSelectedColor([0.3,1,0.8])
    display_node.SetPointLabelsVisibility(False)

    interactionNode = slicer.app.applicationLogic().GetInteractionNode()
    selectionNode = slicer.app.applicationLogic().GetSelectionNode()
    selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
    selectionNode.SetActivePlaceNodeID(self.target_point.GetID())
    interactionNode.SetCurrentInteractionMode(interactionNode.Place)
    

  def reset_slider(self):
    pass

  def on_target_point_placed(self,caller,event):
    self.reset_slider()
    print("on place target point","2",self.unit_index_inner)
    interactionNode = slicer.app.applicationLogic().GetInteractionNode()
    interactionNode.SetCurrentInteractionMode(interactionNode.ViewTransform)
    self.ui.btnAddTarget.setChecked(False)
    #label = util.findChild(self.ui.btnAddTarget,"labelText")
    #label.setText("定位靶点")
    util.send_event_str(util.JAddFiber_TargetPoint_Placed,self.unit_index_inner.__str__())
    # util.GetDisplayNode(self.target_point).SetHandlesInteractive(True)
    util.GetDisplayNode(self.target_point).SetInteractionHandleScale(0.99)
    self.fresh_result()
    util.singleShot(100,self.check_points_placed)
    
    self.target_point.SetNthControlPointLabel(0,"TP")
    display_node = util.GetDisplayNode(self.target_point)
    display_node.SetPointLabelsVisibility(True)
    

  def check_points_placed(self):
    raise Exception("virual method")


    
  def on_opacity_changed(self,val):
    raise Exception("virual method")


  def hide_fiber(self):
    raise Exception("virual method")

  def show_fiber(self):
    raise Exception("virual method")
  

  def delete_points(self):
    if self.entry_point:
      util.RemoveNode(self.entry_point)
      self.entry_point = None
    if self.target_point:
      util.RemoveNode(self.target_point)
      self.target_point = None

  def on_btnConfirm(self):
    self.update_archive_flag = False
    #self.reset_slider()
    self.update_archive_flag = True
    slicer.mrmlScene.InvokeEvent(util.JAddFiberReturn,self.entry_point)
    util.send_event_str(util.GotoPrePage,"1")

  def set_component(self,node,type):
    node.SetAttribute("fiber_unit_id",self.unit_index_inner.__str__())
    node.SetAttribute("fiber_unit_type",type.__str__())
    
    if type == "target_point":
      self.target_point = node
      self.target_point.AddObserver(slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent, self.on_target_point_placed)
      self.target_point.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, lambda a,b:self.fresh_result())
      self.target_point.AddObserver(slicer.vtkMRMLMarkupsNode.PointStartInteractionEvent, lambda A,b:self.on_point_hide_3d(True))
      self.target_point.AddObserver(slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent, self.on_PointEndInteractionEvent)
    if type == "entry_point":
      self.entry_point = node
      self.entry_point.AddObserver(slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent, self.on_entry_point_placed)
      self.entry_point.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, lambda a,b:self.fresh_result())
      self.entry_point.AddObserver(slicer.vtkMRMLMarkupsNode.PointStartInteractionEvent, lambda A,b:self.on_point_hide_3d(True))
      self.entry_point.AddObserver(slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent, self.on_PointEndInteractionEvent)
  
  def on_PointEndInteractionEvent(self,_a,_b):
    self._on_landing_to_model(_a,util.getFirstNodeByName("皮肤"))
    self.on_point_hide_3d(False)
    

  def _on_landing_to_model(self,fiducialNode,modelNode):
    if modelNode is None:
      return  
    if fiducialNode is None:
      return
    # 假设我们关注第一个标记点
    point = [0,0,0]
    fiducialNode.GetNthFiducialPosition(0, point)
    
    
    # 从 vtkMRMLModelNode 获取模型的 vtkPolyData
    polyData = modelNode.GetClosedSurfaceInternalRepresentation("皮肤")
    if not polyData:
      return
   
    # 创建一个 vtkPointLocator
    pointLocator = vtk.vtkPointLocator()
    pointLocator.SetDataSet(polyData)
    pointLocator.BuildLocator()

    # 查找最近的点
    closestPointId = pointLocator.FindClosestPoint(point)
    closestPoint = polyData.GetPoint(closestPointId)

    # 计算最近点与标记点之间的距离
    distance = vtk.vtkMath.Distance2BetweenPoints(point, closestPoint)
    fiducialNode.SetNthControlPointPositionWorld(0,closestPoint)
    print("Closest point ID:", closestPointId)
    print("Closest point coordinates:", closestPoint)
    print("Distance to closest point:", distance)
    
    
  
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
    self.style = cloned_node.GetAttribute("node_type")
    if cloned_node.GetAttribute("thick_slider") is not None:
      self.ui.thick_slider.setValue(float(cloned_node.GetAttribute("thick_slider")))
    if cloned_node.GetAttribute("rotate_slider_2") is not None:
      self.ui.rotate_slider_2.setValue(float(cloned_node.GetAttribute("rotate_slider_2")))
    if cloned_node.GetAttribute("rotate_slider") is not None:
      self.ui.rotate_slider.setValue(float(cloned_node.GetAttribute("rotate_slider")))
    if cloned_node.GetAttribute("radius_slider") is not None:
      self.ui.radius_slider.setValue(float(cloned_node.GetAttribute("radius_slider")))
    if cloned_node.GetAttribute("length_slider") is not None:
      self.ui.length_slider.setValue(float(cloned_node.GetAttribute("length_slider")))
    if cloned_node.GetAttribute("depth_slider_2") is not None:
      self.ui.depth_slider_2.setValue(float(cloned_node.GetAttribute("depth_slider_2")))
    if cloned_node.GetAttribute("depth_slider") is not None:
      self.ui.depth_slider.setValue(float(cloned_node.GetAttribute("depth_slider")))
    util.RemoveNode(cloned_node)

  

  


  

  def is_not_empty(self):
    raise Exception("vitual method")

  def generate_final_fiber_model(self):
    return None

  def fresh_result(self):
    self.reset_slider()
    if self.entry_point is None:
      return
    if self.target_point is None:
      return
    if self.entry_point.GetNumberOfControlPoints() == 0:
      return
    if self.target_point.GetNumberOfControlPoints() == 0:
      return
    util.send_event_str(util.JAddFiber_TargetPoint_Placed,self.unit_index_inner.__str__())
    util.send_event_str(util.JAddFiber_EntryPoint_Placed,self.unit_index_inner.__str__())
    entry_point_world,_ = self.get_entry_point()
    target_point_world,_ = self.get_target_point()
    self.ensure_load_stl(entry_point_world,target_point_world)
    self.main.refresh_tab()
    return

    

