import slicer,qt,vtk,ctk
import slicer.util as util
import os
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from Base.JBaseExtension import JBaseExtensionWidget
import UnitPunctureGuideLib.G_UnitPunctureGuide as G
import threading
import numpy as np

class sunHeadExport(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "sunHeadExport"  # TODO: make this more human readable by adding spaces
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
# PurchaseMaterialWidget
#

class sunHeadExportWidget(JBaseExtensionWidget):
  def setup(self):
    super().setup()
    folder_path = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(folder_path, '1.txt')):
        app_style = "1"
    elif os.path.exists(os.path.join(folder_path, '2.txt')):
        app_style = "2"
    else:
        app_style = "3"
    if app_style == "3":
        pass
    elif app_style == "2":
        self.ui.tabWidget_2.setVisible(True)
    elif app_style == "1":
        self.ui.widget_3.setVisible(False)
        self.ui.label_26.setVisible(False)
      
    self.ui.tabWidget_2.tabBar().hide()
    self.ui.pushButton.connect('clicked()',self.on_click_f)
    self.ui.pushButton_4.connect('clicked()',self.on_export)
    # util.singleShot(1000,self.statistics)
    # return
    cached_path = util.get_from_PAAA("cached_path")
    if cached_path!=None and os.path.exists(cached_path):
      self.ui.textEdit.setPlainText(cached_path)
    else:
      folderpath = util.get_project_base_path()
      for i in range(3):
          folderpath = os.path.dirname(folderpath)
      folderpath = os.path.join(folderpath,"PC").replace("\\","/")
      if not os.path.exists(folderpath):
        os.mkdir(folderpath)
      self.ui.textEdit.setPlainText(folderpath)
      
      
    

  def find5Points(self,btn):
    util.RemoveNodeByName("PDS5")
    planeNode1 = util.getFirstNodeByName("axial_a")
    origin1 = [0.0, 0.0, 0.0]
    normal1 = [0.0, 0.0, 0.0]
    planeNode1.GetOriginWorld(origin1)
    planeNode1.GetNormalWorld(normal1)
    normal1_direction = normal1 / np.linalg.norm(normal1)
    if normal1_direction[2] < 0 :
        normal1_direction = -normal1_direction
    np1 = np.array(origin1) + 5*normal1_direction
    asd = util.AddControlPointGlobal(np1)
    asd.SetName("PDS5")
    util.GetDisplayNode(asd).SetPropertiesLabelVisibility(False)
    util.HideNode(asd)
    util.set_button_percent(btn,60)
    self.on_tmp_markups(btn)
    util.set_button_percent(btn,70)
    self.on_interaction_points(btn)
    util.set_button_percent(btn,90)
    
  def show_kedu(self):
    val1 = util.getModuleWidget("sunHeadFrame").ui.slider3.value+5.88
    self.ui.label_26.setText(f"顶部刻度：{format(val1,'.2f')}")
    
    
  def get_panel_size(self):
        import numpy as np
        volume = util.getFirstNodeByClassByAttribute(util.vtkMRMLScalarVolumeNode,"main_node","1")
        bounds = [0]*6
        volume.GetBounds(bounds)
        spacing = volume.GetSpacing()
        extent = ([(bounds[1]-bounds[0])/spacing[0],(bounds[3]-bounds[2])/spacing[1],(bounds[5]-bounds[4])/spacing[2]])
        max_len = np.max([(bounds[1]-bounds[0])/spacing[0],(bounds[3]-bounds[2])/spacing[1],(bounds[5]-bounds[4])/spacing[2]])
        max_len = max_len
        return max_len
    
  def on_tmp_markups(self,btn):
        planenode = util.getFirstNodeByName("axial_a")
        normal = planenode.GetNormal()
        
        p3w = util.get_world_control_point_by_name("PDS5")
        
        plane_name = "axial_tmp"
        planeNode = util.getFirstNodeByName(plane_name)
        if planeNode:
            util.RemoveNode(planeNode)
        planeNode = util.AddNewNodeByNameByClass(plane_name,"vtkMRMLMarkupsPlaneNode")
        util.GetDisplayNode(planeNode).SetNormalVisibility(False)
        util.GetDisplayNode(planeNode).SetPropertiesLabelVisibility(False)
        util.GetDisplayNode(planeNode).SetSelectedColor(vtk.vtkVector3d(1,1,1))
        planeNode.SetSizeWorld([self.get_panel_size(),self.get_panel_size()])
        planeNode.SetCenter(p3w)
        planeNode.SetNormal(normal)
        
        
        planenode = util.getFirstNodeByName("coronal_a")
        normal = planenode.GetNormal()
        plane_name = "coronal_tmp"
        planeNode = util.getFirstNodeByName(plane_name)
        if planeNode:
            util.RemoveNode(planeNode)
        planeNode = util.AddNewNodeByNameByClass(plane_name,"vtkMRMLMarkupsPlaneNode")
        util.GetDisplayNode(planeNode).SetNormalVisibility(False)
        util.GetDisplayNode(planeNode).SetPropertiesLabelVisibility(False)
        util.GetDisplayNode(planeNode).SetSelectedColor(vtk.vtkVector3d(1,1,1))
        planeNode.SetSizeWorld([self.get_panel_size()*2,self.get_panel_size()*2])
        planeNode.SetCenter(p3w)
        planeNode.SetNormal(normal)
        
        
        planenode = util.getFirstNodeByName("saggital_a")
        normal = planenode.GetNormal()
        plane_name = "saggital_tmp"
        planeNode = util.getFirstNodeByName(plane_name)
        if planeNode:
            util.RemoveNode(planeNode)
        planeNode = util.AddNewNodeByNameByClass(plane_name,"vtkMRMLMarkupsPlaneNode")
        util.GetDisplayNode(planeNode).SetNormalVisibility(False)
        util.GetDisplayNode(planeNode).SetPropertiesLabelVisibility(False)
        util.GetDisplayNode(planeNode).SetSelectedColor(vtk.vtkVector3d(1,1,1))
        planeNode.SetSizeWorld([self.get_panel_size()*2,self.get_panel_size()*2])
        planeNode.SetCenter(p3w)
        planeNode.SetNormal(normal)
        
        
  def on_interaction_points(self,btn):
    import numpy as np
    import random
    planeNode1 = util.getFirstNodeByName("axial_tmp")
    skin = util.getFirstNodeByName("皮肤")
    planeNode3 = util.getFirstNodeByName("coronal_tmp")
    linenode = util.getModuleWidget("sunModule").calculate_intersection_line(planeNode1, planeNode3)
    list1 = util.getModuleWidget("sunModule").calculate_segmentation_line_intersections(skin, linenode)
    util.RemoveNode(linenode)
    util.RemoveNodeByName("is_points")
    
    # 定义KMeans的参数
    n_clusters = 2
    max_iters = 100
    tol = 1e-4
    
    # 随机初始化两个聚类中心
    centroids = np.array(random.sample(list1, n_clusters))
    labels = np.zeros(len(list1), dtype=int)

    for _ in range(max_iters):
        # 分配每个点到最近的质心
        new_labels = np.array([np.argmin([np.linalg.norm(point - centroid) for centroid in centroids]) for point in list1])
        
        # 检查是否收敛
        if np.all(labels == new_labels):
            break
        labels = new_labels

        # 更新质心
        new_centroids = np.array([np.mean([point for i, point in enumerate(list1) if labels[i] == j], axis=0) for j in range(n_clusters)])
        
        # 如果质心变化小于容差，则终止
        if np.all(np.linalg.norm(new_centroids - centroids, axis=1) < tol):
            break
        centroids = new_centroids

    # 计算每个聚类到 "TargetPoint" 的最大距离点
    p4w = util.get_world_control_point_by_name("PDS5")
    distance1 = {0: -1, 1: -1}
    pointlist = {0: None, 1: None}
    
    for i, point in enumerate(list1):
        distance = np.linalg.norm(np.array(point) - np.array(p4w))
        if distance > distance1[labels[i]]:
            distance1[labels[i]] = distance
            pointlist[labels[i]] = point

    AINodes = []
    # 创建或更新标记线
    for i, label_name in enumerate(["ltps_left", "ltps_right"]):
        linenode = util.getFirstNodeByName(label_name)
        if linenode:
            util.RemoveNode(linenode)
    for i, label_name in enumerate(["ltps_left", "ltps_right"]):
        linenode = util.AddNewNodeByClass(util.vtkMRMLMarkupsLineNode)
        linenode.SetLineStartPositionWorld(p4w)
        linenode.SetLineEndPositionWorld(pointlist[i])
        AINodes.append(pointlist[i])
        if pointlist[i][0] > p4w[0]:
            linenode.SetName("ltps_left")
        else:
            linenode.SetName("ltps_right")
        util.HideNode(linenode)
        util.GetDisplayNode(linenode).SetSelectedColor(vtk.vtkVector3d(0, 0, 0))

    
    
    
    
    planeNode4 = util.getFirstNodeByName("saggital_tmp")
    linenode = util.getModuleWidget("sunModule").calculate_intersection_line(planeNode1, planeNode4)
    list1 = util.getModuleWidget("sunModule").calculate_segmentation_line_intersections(skin, linenode)
    util.RemoveNode(linenode)
    util.RemoveNodeByName("is_points")
    
    # 定义KMeans的参数
    n_clusters = 2
    max_iters = 100
    tol = 1e-4
    
    # 随机初始化两个聚类中心
    centroids = np.array(random.sample(list1, n_clusters))
    labels = np.zeros(len(list1), dtype=int)
    util.set_button_percent(btn,75)
    for _ in range(max_iters):
        # 分配每个点到最近的质心
        new_labels = np.array([np.argmin([np.linalg.norm(point - centroid) for centroid in centroids]) for point in list1])
        
        # 检查是否收敛
        if np.all(labels == new_labels):
            break
        labels = new_labels

        # 更新质心
        new_centroids = np.array([np.mean([point for i, point in enumerate(list1) if labels[i] == j], axis=0) for j in range(n_clusters)])
        
        # 如果质心变化小于容差，则终止
        if np.all(np.linalg.norm(new_centroids - centroids, axis=1) < tol):
            break
        centroids = new_centroids

    # 计算每个聚类到 "TargetPoint" 的最大距离点
    p4w = util.get_world_control_point_by_name("PDS5")
    distance1 = {0: -1, 1: -1}
    pointlist = {0: None, 1: None}
    
    for i, point in enumerate(list1):
        distance = np.linalg.norm(np.array(point) - np.array(p4w))
        if distance > distance1[labels[i]]:
            distance1[labels[i]] = distance
            pointlist[labels[i]] = point

    AINodes = []
    # 创建或更新标记线
    for i, label_name in enumerate(["ltps_front", "ltps_back"]):
        linenode = util.getFirstNodeByName(label_name)
        if linenode:
            util.RemoveNode(linenode)
    for i, label_name in enumerate(["ltps_front", "ltps_back"]):
        linenode = util.AddNewNodeByClass(util.vtkMRMLMarkupsLineNode)
        linenode.SetLineStartPositionWorld(p4w)
        linenode.SetLineEndPositionWorld(pointlist[i])
        AINodes.append(pointlist[i])
        linenode.SetName(label_name)
        if pointlist[i][1] > p4w[1]:
            linenode.SetName("ltps_front")
        else:
            linenode.SetName("ltps_back")
        util.HideNode(linenode)
        util.GetDisplayNode(linenode).SetSelectedColor(vtk.vtkVector3d(0, 0, 0))

        
    util.set_button_percent(btn,80)
    linenode = util.getModuleWidget("sunModule").calculate_intersection_line(planeNode1, planeNode3)
    list1 = util.getModuleWidget("sunModule").calculate_segmentation_line_intersections(skin, linenode)
    util.RemoveNode(linenode)
    util.RemoveNodeByName("is_points")
    
    # 定义KMeans的参数
    n_clusters = 2
    max_iters = 100
    tol = 1e-4
    
    # 随机初始化两个聚类中心
    centroids = np.array(random.sample(list1, n_clusters))
    labels = np.zeros(len(list1), dtype=int)

    for _ in range(max_iters):
        # 分配每个点到最近的质心
        new_labels = np.array([np.argmin([np.linalg.norm(point - centroid) for centroid in centroids]) for point in list1])
        
        # 检查是否收敛
        if np.all(labels == new_labels):
            break
        labels = new_labels

        # 更新质心
        new_centroids = np.array([np.mean([point for i, point in enumerate(list1) if labels[i] == j], axis=0) for j in range(n_clusters)])
        
        # 如果质心变化小于容差，则终止
        if np.all(np.linalg.norm(new_centroids - centroids, axis=1) < tol):
            break
        centroids = new_centroids


        
    ################jjjjjjjjjjjjjjjjjjj
    util.set_button_percent(btn,85)
    linenode = util.getModuleWidget("sunModule").calculate_intersection_line(planeNode3, planeNode4)
    list1 = util.getModuleWidget("sunModule").calculate_segmentation_line_intersections(skin, linenode)
    util.RemoveNode(linenode)
    util.RemoveNodeByName("is_points")
    
    # 定义KMeans的参数
    n_clusters = 2
    max_iters = 100
    tol = 1e-4
    
    if n_clusters < 0:
        n_clusters = 0
    elif n_clusters > len(list1):
        n_clusters = len(list1)
    
    
    # 随机初始化两个聚类中心
    centroids = np.array(random.sample(list1, n_clusters))
    labels = np.zeros(len(list1), dtype=int)

    for _ in range(max_iters):
        # 分配每个点到最近的质心
        new_labels = np.array([np.argmin([np.linalg.norm(point - centroid) for centroid in centroids]) for point in list1])
        
        # 检查是否收敛
        if np.all(labels == new_labels):
            break
        labels = new_labels

        # 更新质心
        new_centroids = np.array([np.mean([point for i, point in enumerate(list1) if labels[i] == j], axis=0) for j in range(n_clusters)])
        
        # 如果质心变化小于容差，则终止
        if np.all(np.linalg.norm(new_centroids - centroids, axis=1) < tol):
            break
        centroids = new_centroids

    # 计算每个聚类到 "TargetPoint" 的最大距离点
    p4w = util.get_world_control_point_by_name("PDS5")
    distance1 = {0: -1, 1: -1}
    pointlist = {0: None, 1: None}
    
    for i, point in enumerate(list1):
        distance = np.linalg.norm(np.array(point) - np.array(p4w))
        if distance > distance1[labels[i]]:
            distance1[labels[i]] = distance
            pointlist[labels[i]] = point

    AINodes = []
    # 创建或更新标记线
    for i, label_name in enumerate(["ltps_top", "ltps_bottom"]):
        linenode = util.getFirstNodeByName(label_name)
        if linenode:
            util.RemoveNode(linenode)
    for i, label_name in enumerate(["ltps_top", "ltps_bottom"]):
        if not pointlist[i]:
            continue
        linenode = util.AddNewNodeByClass(util.vtkMRMLMarkupsLineNode)
        linenode.SetLineStartPositionWorld(p4w)
        linenode.SetLineEndPositionWorld(pointlist[i])
        AINodes.append(pointlist[i])
        linenode.SetName(label_name)
        if pointlist[i][2] > p4w[2]:
            linenode.SetName("ltps_top")
        else:
            linenode.SetName("ltps_bottom")
        util.HideNode(linenode)
        util.GetDisplayNode(linenode).SetSelectedColor(vtk.vtkVector3d(0, 0, 0))

        
        
    util.RemoveNodeByName("coronal_tmp")
    util.RemoveNodeByName("axial_tmp")
    util.RemoveNodeByName("saggital_tmp")

  def statistics(self,btn):
    util.set_button_percent(btn,59)
    sm = util.getModuleWidget("sunModule")
    
    self.find5Points(btn)
    util.set_button_percent(btn,87)
    v1 = np.linalg.norm(np.array(util.get_world_control_point_by_name("TargetPoint"))-np.array(util.get_world_control_point_by_name("EntryPoint")))
    util.SetGlobalSaveValue("sun_export_2",f"入点到靶点：{format(v1,'.2f')} mm")
    self.ui.label_10.setText(f"入点到靶点：{format(v1,'.2f')} mm")   
    
    segmentationNode = util.getFirstNodeByName("血肿")
    if segmentationNode:
        import SegmentStatistics
        segStatLogic = SegmentStatistics.SegmentStatisticsLogic()
        segStatLogic.getParameterNode().SetParameter("Segmentation", segmentationNode.GetID().__str__())
        segStatLogic.computeStatistics()
        stats = segStatLogic.getStatistics()

        # Display volume of each segment
        for segmentId in stats["SegmentIDs"]:
            volume_cm3 = stats[segmentId,"LabelmapSegmentStatisticsPlugin.volume_cm3"]
            self.volume_cm3 = volume_cm3
            tips =   f"血肿体积：{round(volume_cm3,2)} cm3"
            util.SetGlobalSaveValue("sun_export_1",tips)
            self.ui.label_14.setText(tips)
    util.set_button_percent(btn,91)
    sm.on_red_panel()
    util.set_button_percent(btn,92)
    sm.on_yellow_panel()
    util.set_button_percent(btn,94)
    sm.on_green_panel()
    util.set_button_percent(btn,96)
    red_dis = sm.on_red_distance_any_point(util.get_world_control_point_by_name("EntryPoint"),"a",3)
    green_dis = sm.on_green_distance_any_point(util.get_world_control_point_by_name("EntryPoint"),"a",3)
    yellow_dis = sm.on_yellow_distance_any_point(util.get_world_control_point_by_name("EntryPoint"),"a",3)
    self.ui.label_11.setText(red_dis+" mm")   
    self.ui.label_20.setText(green_dis+" mm")   
    self.ui.label_19.setText(yellow_dis+" mm")   
    util.SetGlobalSaveValue("sun_export_6",red_dis+" mm")
    util.SetGlobalSaveValue("sun_export_7",green_dis+" mm")
    util.SetGlobalSaveValue("sun_export_8",yellow_dis+" mm")
    
    red_dis = sm.on_red_distance_any_point(util.get_world_control_point_by_name("TargetPoint"),"a",3)
    green_dis = sm.on_green_distance_any_point(util.get_world_control_point_by_name("TargetPoint"),"a",3)
    yellow_dis = sm.on_yellow_distance_any_point(util.get_world_control_point_by_name("TargetPoint"),"a",3)
    self.ui.label_3.setText(red_dis+" mm")   
    self.ui.label_5.setText(green_dis+" mm")   
    self.ui.label_7.setText(yellow_dis+" mm")   
    util.SetGlobalSaveValue("sun_export_3",red_dis+" mm")
    util.SetGlobalSaveValue("sun_export_4",green_dis+" mm")
    util.SetGlobalSaveValue("sun_export_5",yellow_dis+" mm")
    util.set_button_percent(btn,98)
    ltps_left = util.getFirstNodeByName("ltps_left")
    if ltps_left:
        m1 = str(format(ltps_left.GetMeasurement('length').GetValue(),".2f"))
        self.ui.label_16.setText(f"右边：{m1} mm")
        util.SetGlobalSaveValue("sun_export_9",f"右边：{m1} mm")
        
    ltps_right = util.getFirstNodeByName("ltps_right")
    if ltps_right:
        m1 = str(format(ltps_right.GetMeasurement('length').GetValue(),".2f"))
        self.ui.label_18.setText(f"左边：{m1} mm")
        util.SetGlobalSaveValue("sun_export_10",f"左边：{m1} mm")
        
    ltps_front = util.getFirstNodeByName("ltps_front")
    if ltps_front:
        m1 = str(format(ltps_front.GetMeasurement('length').GetValue(),".2f"))
        self.ui.label_22.setText(f"前边：{m1} mm")
        util.SetGlobalSaveValue("sun_export_11",f"前边：{m1} mm")
        
    ltps_back = util.getFirstNodeByName("ltps_back")
    if ltps_back:
        m1 = str(format(ltps_back.GetMeasurement('length').GetValue(),".2f"))
        self.ui.label_23.setText(f"后边：{m1} mm")
        util.SetGlobalSaveValue("sun_export_12",f"后边：{m1} mm")
        
    ltps_top = util.getFirstNodeByName("ltps_top")
    if ltps_top:
        m1 = str(format(ltps_top.GetMeasurement('length').GetValue(),".2f"))
        self.ui.label_24.setText(f"顶部：{m1} mm")
        util.SetGlobalSaveValue("sun_export_13",f"顶部：{m1} mm")
  
  
  def OnArchiveLoaded(self,_a,_b):
    sun_export_1 = util.GetGlobalSaveValue("sun_export_1")
    if sun_export_1:
        self.ui.label_14.setText(sun_export_1)
        
    sun_export_2 = util.GetGlobalSaveValue("sun_export_2")
    if sun_export_2:
        self.ui.label_10.setText(sun_export_2)
        
    sun_export_3 = util.GetGlobalSaveValue("sun_export_3")
    if sun_export_3:
        self.ui.label_3.setText(sun_export_3)
        
    sun_export_4 = util.GetGlobalSaveValue("sun_export_4")
    if sun_export_4:
        self.ui.label_5.setText(sun_export_4)
        
    sun_export_5 = util.GetGlobalSaveValue("sun_export_5")
    if sun_export_5:
        self.ui.label_7.setText(sun_export_5)
        
    sun_export_6 = util.GetGlobalSaveValue("sun_export_6")
    if sun_export_6:
        self.ui.label_11.setText(sun_export_6)
        
    sun_export_7 = util.GetGlobalSaveValue("sun_export_7")
    if sun_export_7:
        self.ui.label_20.setText(sun_export_7)
        
    sun_export_8 = util.GetGlobalSaveValue("sun_export_8")
    if sun_export_8:
        self.ui.label_19.setText(sun_export_8)
        
    sun_export_9 = util.GetGlobalSaveValue("sun_export_9")
    if sun_export_9:
        self.ui.label_16.setText(sun_export_9)
        
    sun_export_10 = util.GetGlobalSaveValue("sun_export_10")
    if sun_export_10:
        self.ui.label_18.setText(sun_export_10)
        
    sun_export_11 = util.GetGlobalSaveValue("sun_export_11")
    if sun_export_11:
        self.ui.label_22.setText(sun_export_11)
        
    sun_export_12 = util.GetGlobalSaveValue("sun_export_12")
    if sun_export_12:
        self.ui.label_23.setText(sun_export_12)
        
    sun_export_13 = util.GetGlobalSaveValue("sun_export_13")
    if sun_export_13:
        self.ui.label_24.setText(sun_export_13)
    
    
  def on_click_f(self):
    dir1 = util.get_folder_path()
    if dir1 == "":
      return
    else:
      self.ui.textEdit.setPlainText(dir1)
      util.save_to_PAAA("cached_path",dir1)
  
  def _combine_segments(self,namelist):
        rnode = util.AddNewNodeByClass(util.vtkMRMLSegmentationNode) 
        rnode.CreateDefaultDisplayNodes()
        for name in namelist:
            if name == "通道":
                fibernode = util.getFirstNodeByName("outer_normal_fiber")
                util.ShowNode(fibernode)
                tnode = util.convert_model_to_segment(fibernode,self.get_volume())
                tnode.SetName("NMA")
                tnode.SetAndObserveTransformNodeID(fibernode.GetTransformNodeID())
                tnode.HardenTransform()
                if tnode:
                    segment = util.GetNthSegment(tnode,0)
                    rnode.GetSegmentation().AddSegment(segment)
                #util.RemoveNode(tnode)
            else:
                tnode = util.getFirstNodeByName(name)
                if tnode:
                    segment = util.GetNthSegment(tnode,0)
                    rnode.GetSegmentation().AddSegment(segment)
        return rnode
  
  def vector_angle_and_normal(self,vector1, vector2):
    # 计算向量夹角
    dot_product = np.dot(vector1, vector2)
    norm_vector1 = np.linalg.norm(vector1)
    norm_vector2 = np.linalg.norm(vector2)
    cos_angle = dot_product / (norm_vector1 * norm_vector2)
    angle = np.arccos(cos_angle)
    # 转换为角度制
    angle_degrees = np.rad2deg(angle)

    # 计算法向量（仅适用于三维向量）
    if len(vector1) == 3 and len(vector2) == 3:
        normal = np.cross(vector1, vector2)
    else:
        normal = None

    return angle_degrees, normal
  
  
  def rotate_to_drill1(self,starget,sentry,ttarget,tentry):
    tvector = np.array(tentry) - np.array(ttarget)
    svector = np.array(sentry) - np.array(starget)
    v1 = np.array(ttarget) - np.array(starget)
    angle,normal = self.vector_angle_and_normal(tvector,svector)
    
    transformToParentMatrix = vtk.vtkMatrix4x4()
    transformToParentMatrix.Identity()
    handleToParentMatrix=vtk.vtkTransform()
    handleToParentMatrix.PostMultiply()
    handleToParentMatrix.Concatenate(transformToParentMatrix)
    handleToParentMatrix.Translate(-starget[0], -starget[1], -starget[2])
    handleToParentMatrix.RotateWXYZ(-angle, normal)
    handleToParentMatrix.Translate(starget[0], starget[1], starget[2])
    handleToParentMatrix.Translate(v1[0], v1[1], v1[2])
    transformToParentMatrix.DeepCopy(handleToParentMatrix.GetMatrix())

    util.RemoveNodeByName("transform_node123")
    transform_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
    transform_node.SetMatrixTransformToParent(transformToParentMatrix)
    transform_node.SetName("transform_node123")
    return transform_node


  def rotate_to_drill(self):
      ttarget = [40.500,12.000,311.700]
      tentry = [40.500,12.000,811.700]
    
      sentry = util.get_world_control_point_by_name("EntryPoint")
      starget = util.get_world_control_point_by_name("TargetPoint")
      tn = self.rotate_to_drill1(starget,sentry,ttarget,tentry)
      return tn

  
  def extractLargestConnectedComponent(self,inputModel, outputModel):
    """Extract the largest connected portion of a surface model.
    """
    connect = vtk.vtkPolyDataConnectivityFilter()
    connect.SetInputData(inputModel.GetPolyData())
    connect.SetExtractionModeToLargestRegion()
    connect.Update()
    outputModel.SetAndObservePolyData(connect.GetOutput())
    
    
  def on_export3(self):
    tn = self.rotate_to_drill()

    folderpath = self.ui.textEdit.plainText
    if not os.path.exists(folderpath):
      util.showWarningText("当前的导出文件夹不存在，请重新选择文件夹")
      return
    
    
    util.RemoveNodeByName("headframe_centerball")
    nodes = util.getNodesByAttribute("flag_model_1","1")
    for node in nodes:
        util.RemoveNode(node)
        
    if util.getFirstNodeByName("皮肤") is None:
        util.showWarningText("请先创建皮肤")
        return
    
    if util.getFirstNodeByName("血肿") is None:
        util.showWarningText("请先创建血肿")
        return
    
    util.send_event_str(util.ProgressStart,"正在导出,请稍候...")
    file_names = ['skin.obj', 'mark.obj','skin.mtl', 'mark.mtl', 'name.txt']
    for file_name in file_names:
        file_path = os.path.join(folderpath, file_name)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"已成功删除 {file_path}")
            except Exception as e:
                print(f"删除 {file_path} 时出错: {e}")
    util.send_event_str(util.ProgressValue,30)
    
    
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    exportFolderItemId = shNode.CreateFolderItem(shNode.GetSceneItemID(), "skin")
    slicer.modules.segmentations.logic().ExportAllSegmentsToModels(util.getFirstNodeByClassByName(util.vtkMRMLSegmentationNode,"皮肤"), exportFolderItemId)
    slicer.modules.segmentations.logic().ExportAllSegmentsToModels(util.getFirstNodeByClassByName(util.vtkMRMLSegmentationNode,"血肿"), exportFolderItemId)
    
    plannode = util.getFirstNodeByName("coronal_a")
    skinmodel = util.getFirstNodeByClassByName(util.vtkMRMLModelNode,"皮肤")
    tumormodel = util.getFirstNodeByClassByName(util.vtkMRMLModelNode,"血肿")
    dynamicModelerNode = util.CreateNodeByClass("vtkMRMLDynamicModelerNode")
    dynamicModelerNode.SetToolName("Plane cut")
    dynamicModelerNode.SetNodeReferenceID("PlaneCut.OutputPositiveModel",skinmodel.GetID())
    dynamicModelerNode.SetNodeReferenceID("PlaneCut.InputPlane",plannode.GetID())
    dynamicModelerNode.SetAttribute("CapSurface","0")
    dynamicModelerNode.SetNodeReferenceID("PlaneCut.InputModel",skinmodel.GetID())
    util.AddNode(dynamicModelerNode)
    util.RemoveNode(dynamicModelerNode)
    self.extractLargestConnectedComponent(skinmodel,skinmodel)
    
    widget = util.getModuleWidget("OpenAnatomyExport")
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    if widget:
        skinmodel.SetAndObserveTransformNodeID(tn.GetID())
        tumormodel.SetAndObserveTransformNodeID(tn.GetID())
        skinmodel.HardenTransform()
        tumormodel.HardenTransform()
        widget.logic.exportModel(exportFolderItemId,folderpath,0.9,"OBJ")
        
    util.remove_all_folder("skin")
    
    TargetPoint = util.clone(util.getFirstNodeByName("TargetPoint"))
    TargetPoint.SetName("badian")
    TargetPoint.SetAndObserveTransformNodeID(tn.GetID())
    TargetPoint.HardenTransform()
    SN = self.create_segment_fiducials(["badian"])
    SN.SetName("ASP1")
    segment_node = self._combine_segments(["ASP1"])
    segment_node.SetName("mark")
    
    
    widget = util.getModuleWidget("OpenAnatomyExport")
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    itemIDToClone = shNode.GetItemByDataNode(segment_node)
    util.send_event_str(util.ProgressValue,50)
    if widget:
        widget.logic.exportModel(itemIDToClone,folderpath,0.1,"OBJ")
    util.RemoveNode(segment_node)
    util.RemoveNode(TargetPoint)
    util.RemoveNodeByName("ASP1")
    
    file_path = os.path.join(folderpath,"name.txt")
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            for string in ["皮肤","血肿"]:
                file.write(string + '\n')
        print(f"已成功将字符串写入 {file_path} 文件。")
    except Exception as e:
        print(f"写入文件时出错: {e}")
    
    file_names = ['skin.mtl', 'mark.mtl']
    for file_name in file_names:
        file_path = os.path.join(folderpath, file_name)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"已成功删除 {file_path}")
            except Exception as e:
                print(f"删除 {file_path} 时出错: {e}")
                
    util.send_event_str(util.ProgressValue,100)
    
    import subprocess
    try:
      win_dir = os.path.normpath(folderpath)
      subprocess.Popen('explorer "%s"' %win_dir)
      print(f"成功打开文件夹: {folderpath}")
    except FileNotFoundError:
        print(f"未找到文件夹: {folderpath}")
    except subprocess.CalledProcessError as e:
        print(f"打开文件夹时出现错误: {e}")
        
        
        
        
  def on_export(self):
    folderpath = self.ui.textEdit.plainText
    if not os.path.exists(folderpath):
      util.showWarningText("当前的导出文件夹不存在，请重新选择文件夹")
      return
    
    
    util.RemoveNodeByName("headframe_centerball")
    nodes = util.getNodesByAttribute("flag_model_1","1")
    for node in nodes:
        util.RemoveNode(node)
    
    # keyspoint = ["left_p","right_p","nose","TargetPoint","EntryPoint","frame_needle_left","frame_needle_right"]
    # for kname in keyspoint:
    #     if util.getFirstNodeByName(kname) is None:
    #         util.showWarningText("缺少关键点:"+kname)
    #         return
    if util.getFirstNodeByName("皮肤") is None:
        util.showWarningText("请先创建皮肤")
        return
    
    if util.getFirstNodeByName("血肿") is None:
        util.showWarningText("请先创建血肿")
        return
    
    util.send_event_str(util.ProgressStart,"正在导出,请稍候...")
    file_names = ['skin.obj', 'mark.obj','skin.mtl', 'mark.mtl', 'name.txt']
    for file_name in file_names:
        file_path = os.path.join(folderpath, file_name)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"已成功删除 {file_path}")
            except Exception as e:
                print(f"删除 {file_path} 时出错: {e}")
            
    # for node in util.getNodes("*").values():
    #     if node.IsA("vtkMRMLTransformableNode"):
    #         node.SetAndObserveTransformNodeID(tn.GetID())
    util.send_event_str(util.ProgressValue,30)
    
    SN = self.create_segment_fiducials(["register_point_1"])
    SN.SetName("ASP1")
    SN = self.create_segment_fiducials(["register_point_2"])
    SN.SetName("ASP2")
    SN = self.create_segment_fiducials(["register_point_3"])
    SN.SetName("ASP3")
    SN = self.create_segment_fiducials(["register_point_4"])
    SN.SetName("ASP4")
    segment_node = self._combine_segments(["ASP1","ASP2","ASP3","ASP4"])
    segment_node.SetName("mark")
    
    
    widget = util.getModuleWidget("OpenAnatomyExport")
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    itemIDToClone = shNode.GetItemByDataNode(segment_node)
    util.send_event_str(util.ProgressValue,50)
    if widget:
        widget.logic.exportModel(itemIDToClone,folderpath,0.1,"OBJ")
    util.RemoveNode(segment_node)
    
    if util.getFirstNodeByName("frame_needle_left"):
        util.ShowNodeByName("frame_needle_left")
        util.ShowNodeByName("frame_needle_right")
        util.ShowNodeByName("EntryPoint")
        SN = self.create_segment_fiducials(["frame_needle_left"])
        SN.SetName("DSP1")
        SN = self.create_segment_fiducials(["frame_needle_right"])
        SN.SetName("DSP2")
        segment_node = self._combine_segments(["皮肤","血肿","DSP1","DSP2"])
        segment_node.SetName("skin")
        strings = ["皮肤", "血肿", "DS1", "DS2"]
    else:
        segment_node = self._combine_segments(["皮肤","血肿","通道"])
        segment_node.SetName("skin")
        strings = ["皮肤", "血肿","通道"]
    widget = util.getModuleWidget("OpenAnatomyExport")
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    itemIDToClone = shNode.GetItemByDataNode(segment_node)
    util.send_event_str(util.ProgressValue,50)
    if widget:
        widget.logic.exportModel(itemIDToClone,folderpath,0.9,"OBJ")
    util.RemoveNode(segment_node)
    
    
    file_path = os.path.join(folderpath,"name.txt")
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            for string in strings:
                file.write(string + '\n')
        print(f"已成功将字符串写入 {file_path} 文件。")
    except Exception as e:
        print(f"写入文件时出错: {e}")
    
    file_names = ['skin.mtl', 'mark.mtl']
    for file_name in file_names:
        file_path = os.path.join(folderpath, file_name)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"已成功删除 {file_path}")
            except Exception as e:
                print(f"删除 {file_path} 时出错: {e}")
                
    util.send_event_str(util.ProgressValue,100)
    
    import subprocess
    try:
      win_dir = os.path.normpath(folderpath)
      subprocess.Popen('explorer "%s"' %win_dir)
      print(f"成功打开文件夹: {folderpath}")
    except FileNotFoundError:
        print(f"未找到文件夹: {folderpath}")
    except subprocess.CalledProcessError as e:
        print(f"打开文件夹时出现错误: {e}")
  
  def get_volume(self):
        volume = util.getFirstNodeByClassByAttribute(util.vtkMRMLScalarVolumeNode,"main_node","1")
        return volume
  
  def create_sphere_ball(self,pname,color=[0,0,1]):
        wp = util.get_world_control_point_by_name(pname)
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(wp[0],wp[1],wp[2])
        sphere.SetRadius(3)
        modelNode = slicer.modules.models.logic().AddModel(sphere.GetOutputPort())
        modelNode.SetName(f"model_{pname}")
        modelNode.SetAttribute("flag_model_1","1")
        util.GetDisplayNode(modelNode).SetColor(color)
        return modelNode
      

  def create_segment_fiducials(self,namelist):
      nalie = []
      for pname in namelist:
          ba = self.create_sphere_ball(pname)
          segment = util.convert_model_to_segment(ba,"")
          util.RemoveNode(ba)
          nalie.append(segment)
      
      abc = self.union_segment_node_list(self.get_volume(),nalie,"ooi")
      return abc

  def union_segment_node_list(self,master_node,segment_node_list,segment_name):
      node_fix = util.getFirstNodeByName(segment_name)
      if node_fix:
          util.RemoveNode(node_fix)
      node_fix = util.CreateDefaultSegmentationNode(segment_name)
      for i in range(len(segment_node_list)):
          segmentNode1 = segment_node_list[i]
          segment_move = util.GetNthSegment(segmentNode1,0)
          node_fix.GetSegmentation().AddSegment(segment_move)
          util.RemoveNode(segmentNode1)
          
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
    