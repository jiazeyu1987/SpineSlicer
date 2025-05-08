import slicer,qt,os
import slicer.util as util
import threading
import numpy as np
import copy
from accuracy.main import AccuracyTest
import time
class JChooseMultiPointPanelButton:
  widget = None
  btn = None
  qfunctionbtn = None
  style = 1
  def __init__(self,btn,radius,id,style) -> None:
    qwidget = qt.QWidget()
    self.widget = qwidget
    layout = qt.QHBoxLayout(qwidget)
    layout.addWidget(btn)
    layout.setSpacing(0)
    layout.setContentsMargins(0, 0, 0, 0)
    self.btn = btn
    self.style = style
    
    qfunctionbtn = qt.QPushButton(qwidget)
    if self.style == 1:
      qfunctionbtn.setText("删除")
      qfunctionbtn.setStyleSheet("color: red;")
    elif self.style == 2:
      qfunctionbtn.setText("导航")
      qfunctionbtn.setStyleSheet("color: yellow;")
    qfunctionbtn.setFixedWidth(radius*3)
    self.qfunctionbtn = qfunctionbtn
    layout.addWidget(qfunctionbtn)
    
    self.btn = btn
    self.btn.setObjectName(f"{id}")
    self.btn.setFixedSize(radius*2,radius*2)
    self.point_node = None
    self.radius = radius
    self.id = id
    self.btn.connect('clicked()',self.on_click)
    qfunctionbtn.connect('clicked()',self.on_function)
    
    
  
  def on_function(self):
    if self.style == 1:
      if self.point_node :
        util.RemoveNode(self.point_node)
      self.point_node = None
      self.set_red()
    elif self.style == 2:
      if not self.point_node:
        return
      point_world = [0,0,0]
      self.point_node.GetNthControlPointPositionWorld(0, point_world)
      util.showWarningText(f"Now navigating to ct point :{point_world[0]},{point_world[1]},{point_world[2]}")
      
      trans_ct_in_camera = np.linalg.inv(util.getModuleWidget('RDNTreat').camera_in_ct)
      point_ct = np.array(point_world)
      point_ct = np.append(point_ct,1)
      point_camera = np.dot(trans_ct_in_camera,point_ct)
      
      trans_camera_in_base = util.getModuleWidget('JRobotNDI').camera_in_base
      point_base = np.dot(trans_camera_in_base,point_camera)
      point_base[2] += 10 # to avoid collision with the marker
      entry_base = copy.deepcopy(point_base)
      entry_base[2] += 40 # create an entry point just above the target point
      
      # trans_tip_in_hand = np.matmul(util.getModuleWidget('JRobotNDI').marker_in_hand,util.getModuleWidget('JRobotNDI').trans_tip_in_marker_frame)

      DO_PID = False
      self.on_navigation(entry_base, point_base, point_camera, DO_PID)
      # self.th_accuracy_test = threading.Thread(target = self.on_navigation, args=(entry_base, point_base, point_camera, DO_PID))
      # self.th_accuracy_test.start()

  def on_navigation(self, target_entry_in_base, target_point_in_base, target_point_in_cam, DO_PID):
    print("[navigation test]: thread id : ", threading.get_ident())

    # target_point_in_base, target_entry_in_base, target_point_in_cam, _ = self.target_to_base() # (x,y,z,1)
    print('target point in base:', target_point_in_base)
    print('target entry in base:', target_entry_in_base)

    trans_tip_in_marker_frame = util.getModuleWidget('JRobotNDI').trans_tip_in_marker_frame
    print('Tip in Marker frame:', trans_tip_in_marker_frame)

    trans_tip_in_hand_frame = np.matmul(util.getModuleWidget('JRobotNDI').marker_in_hand,trans_tip_in_marker_frame)
    print('Tip in Hand frame:', trans_tip_in_hand_frame)

    target_entry_in_base_copy = copy.deepcopy(target_entry_in_base)
    target_point_in_base_copy = copy.deepcopy(target_point_in_base)
    trans_cam_in_base_frame = copy.deepcopy(util.getModuleWidget('JRobotNDI').camera_in_base)
    trans_mar_in_hand_frame = copy.deepcopy(util.getModuleWidget('JRobotNDI').marker_in_hand)

    accTestInst = AccuracyTest(trans_cam_in_base_frame, trans_mar_in_hand_frame, target_entry_in_base_copy.reshape((4,1)), target_point_in_base_copy.reshape((4,1)), trans_tip_in_hand_frame, trans_tip_in_marker_frame)
    acc_pose = accTestInst.pose # angles are in degrees

    print('Navigation test final pose : ', acc_pose)
    # acc_pose_j = self.reg_wiget.inverseKinematic(acc_pose.tolist())
    # print('Accracy test final joint position  : ', acc_pose_j)
    # self.move2target(acc_pose, 'pose')
    acc_pose = util.getModuleWidget('JRobotNDI').convertNonStandardPoseToUrStandardPose(acc_pose)
    
    acc_pose_str = np.array2string(acc_pose, separator=',')[1:-1] # for negative numbers space after , is ommited
    acc_pose_str = ', '.join(acc_pose_str.split(',')) 
    # acc_pose_str = acc_pose_str.replace(', ', ',')
    print('Navigation test pose str:', acc_pose_str)

    # # self.reg_wiget.move_robot_to_random_position(acc_pose_str, 'pose')
    # self.reg_wiget.move_robot_to_pose(acc_pose_str)
    print("calling movebytcp")
    print(f"UR, MoveByTCP, {acc_pose_str}, True")
    #util.getModuleWidget("RequestStatus").send_cmd(f"UR, MoveByTCP, {acc_pose_str}, True")
    util.move_robot_to(acc_pose_str)
    print('[move cmd begins]')

    # # wait for the robot to start moving
    # # while self.reg_wiget.rbt_state != 3:
    # while util.getModuleWidget("RequestStatus").send_synchronize_cmd(f"UR, IsRobotSteady") == "True":
    #   time.sleep(0.5)
    # flag_wait = True
    # # wait for the robot to stop moving
    # # while self.reg_wiget.rbt_state != 0:
    # while util.getModuleWidget("RequestStatus").send_synchronize_cmd(f"UR, IsRobotSteady") == "False":  
    #   if(flag_wait):
    #     print('[waiting for robot to finish the movement]')
    #     flag_wait = False
    #   time.sleep(0.05)

    # print('[move cmd over]')

    # if not DO_PID:
    #   return
    # # pid parameters
    # error_threshold = 0.5 # in mm
    # # new parameters 
    # # Kp = np.array([0.35,0.45,0.3]) 
    # # Ki = np.array([0.0000035,0.000006,0.000005]); #np.array([0.000005,0.000005,0.000005])
    # # Kd = np.array([7.5,8.5,2.5])

    # # old parameters (used for elite)
    # Kp = np.array([0.6,0.45,0.7])
    # Ki = np.array([0.000005,0.000005,0.000005])
    # Kd = np.array([1.5,4.0,2.0])

    # accTestInst.pidControl(Kp,Ki,Kd,error_threshold,target_point_in_base,target_point_in_cam)
    # print('PID Control Done!')

    # accTestInst.plotDataAll()
    # print('Data Plotted')    
    
  
  def on_click(self):
    node_name = f"cmppb_{self.id}"
    node = util.getFirstNodeByName(node_name)
    if util.GetControlPointNumber(node) == 0:
      util.RemoveNode(node)
      node = None
      
    if node:
      util.navigation_to_node(node)
      return
    
    if self.style==2:
      util.showWarningText("请在准备阶段添加点")
      return
    entry_point = util.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
    display_node = util.GetDisplayNode(entry_point)
    entry_point.SetName(node_name)
    entry_point.SetAttribute("cmppd",self.id.__str__())
    
    display_node.SetPointLabelsVisibility(False)
    interactionNode = slicer.app.applicationLogic().GetInteractionNode()
    selectionNode = slicer.app.applicationLogic().GetSelectionNode()
    selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
    selectionNode.SetActivePlaceNodeID(entry_point.GetID())
    interactionNode.SetCurrentInteractionMode(interactionNode.Place)
    entry_point.AddObserver(slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent, self.on_define)
    entry_point.AddObserver(slicer.vtkMRMLMarkupsNode.PointRemovedEvent, self.on_remove)
  
  
  def is_green(self):
    return self.point_node != None
    
  
  def on_remove(self,point_node,event):
    self.point_node = None
    self.set_red()
    
    
  def on_define(self,point_node,event):
    self.point_node = point_node
    self.set_green()
    util.GetDisplayNode(self.point_node).SetPointLabelsVisibility(True)
    self.point_node.SetNthControlPointLabel(0,f"R{self.id+1}")
    
  
  def set_red(self):
    self.btn.setStyleSheet(
            "QPushButton {"
            f"   border-radius: {self.radius}px;"  # 设置圆角半径，使按钮呈现圆形
            "   background-color: red;"  # 设置按钮背景颜色
            "   color: white;"  # 设置按钮文本颜色
            "}"
            "QPushButton:hover {"
            "   background-color: #aa0000;"  # 设置鼠标悬停时的背景颜色
            "}"
            "QPushButton:pressed {"
            "   background-color: #ff0000;"  # 设置鼠标悬停时的背景颜色
            "}"
        )
    self.qfunctionbtn.setVisible(False)
    
  def set_green(self):
    self.btn.setStyleSheet(
            "QPushButton {"
            f"   border-radius: {self.radius}px;"  # 设置圆角半径，使按钮呈现圆形
            "   background-color: green;"  # 设置按钮背景颜色
            "   color: white;"  # 设置按钮文本颜色
            "}"
            "QPushButton:hover {"
            "   background-color: #00aa00;"  # 设置鼠标悬停时的背景颜色
            "}"
            "QPushButton:pressed {"
            "   background-color: green;"  # 设置鼠标悬停时的背景颜色
            "}"
        )
    self.qfunctionbtn.setVisible(True)
  
class JChooseMultiPointPanel:
  style = 1
  def __init__(self,parent,radius,style=1) -> None:
    self.parent = parent
    self.radius = radius
    self.button_map = {}
    self.current_btn = None
    self.style = style
  
  def get_node(self,index):
    return self.button_map[index].point_node
  
  def create(self,total,row):
    import math
    vlayout = qt.QVBoxLayout(self.parent)
    vlayout.setSpacing(30)
    vlayout.setContentsMargins(0, 0, 0, 0)
    
    for i in range(math.ceil(total/row)):
      layout = qt.QHBoxLayout()  
      layout.setSpacing(0)
      layout.setContentsMargins(10, 0, 0, 0)
      vlayout.addLayout(layout)
      for j in range(row):
        if i*row+j < total:
          ppt = self.create_round_button(self.parent,i*row+j,self.radius*2)
          
          layout.addWidget(ppt.widget)
  
  def get_empty_points(self):
    empty_index = 0
    for id in self.button_map:
      button = self.button_map[id]
      if not button.is_green():
        empty_index += 1
    return empty_index
  
  def create_round_button(self,parent,id,width=30):
    button = qt.QPushButton(parent)
    ppt = JChooseMultiPointPanelButton(button,width/2,id,self.style)
    ppt.set_red()
    self.button_map[id] = ppt
    return ppt
  
  def OnArchiveLoaded(self):
    nodes = self.get_all_nodes()
    print("get cmppd nodes length:",len(nodes))
    for node in nodes:
      id = int(node.GetAttribute("cmppd"))
      button = self.button_map[id]
      node.AddObserver(slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent, self.button_map[id].on_define)
      node.AddObserver(slicer.vtkMRMLMarkupsNode.PointRemovedEvent, self.button_map[id].on_remove)
      button.on_define(node,None)
      
  def get_all_nodes(self):
    nodes = []
    for node in util.getNodes("*").values():
      if node.GetAttribute("cmppd") != None:
        nodes.append(node)
    return nodes
  
  
  def fresh_status(self):
    for id in self.button_map:
      ppt = self.button_map[id]
      if ppt.point_node and util.GetControlPointNumber(ppt.point_node) > 0 and util.GetNodeByID(ppt.point_node.GetID()) is not None:
        ppt.set_green()
      else:
        ppt.set_red()
  
