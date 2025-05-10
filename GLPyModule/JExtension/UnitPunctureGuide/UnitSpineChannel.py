import imp
import os
from re import A
from tabnanny import check
from time import sleep
import unittest
import logging
import vtk, qt, ctk, slicer,math
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import slicer.util as util
import SlicerWizard.Utilities as su 
import numpy as np
from Base.JBaseExtension import JBaseExtensionWidget
#
# UnitSpineChannel
#

import slicer
import numpy as np
import vtk
from scipy.spatial.transform import Rotation

class PathItem:
    def __init__(self,main,distance,radius,entry_point,target_point,item):
        self.main = main
        self.distance = distance
        self.radius = radius
        self.item = item
        self.entry_point = entry_point
        self.target_point = target_point
        self.visible = False
        self.uiwidget = slicer.util.loadUI(self.main.resourcePath('UI/PathItem.ui'))
        self.ui = slicer.util.childWidgetVariables(self.uiwidget)
        self.ui.l_distance.setText(f"距离: {self.distance:.2f} mm")
        self.ui.l_radius.setText(f"半径: {self.radius:.2f} mm")
        self.ui.visibleButton.connect('clicked()',self.on_switch_model_visible)
        self.ui.deleteButton.connect('clicked()',self.onDelete)
        
    def on_switch_model_visible(self):
        util.getFirstNodeByName("TargetPoint").SetNthControlPointPositionWorld(0,self.target_point)
        util.getFirstNodeByName("EntryPoint").SetNthControlPointPositionWorld(0,self.entry_point)
        
    def onDelete(self):
        self.main.onDeleteItem(self.item)
        

class UnitSpineChannel(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UnitSpineChannel"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["test"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["jia ze yu"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """

"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """

"""


#
# UnitSpineChannelWidget
#

class UnitSpineChannelWidget(JBaseExtensionWidget):
    def setup(self):
        super().setup()
        self.logic = UnitSpineChannelLogic()
        module_path = os.path.dirname(util.modulePath('UnitSpineChannel'))
        file_path1 = (module_path + '/Resources/Icons/btn_entry.png').replace("\\", "/")
        file_path2 = (module_path + '/Resources/Icons/btn_target.png').replace("\\", "/")
        self.bind_point_with_button(self.ui.btn_entry,"EntryPoint","EntryPoint", file_path1)
        self.bind_point_with_button(self.ui.btn_target,"TargetPoint","TargetPoint", file_path2)
        self.path_entries = []
        self.ui.pushButton.connect('clicked()',self.onReload)
        
    
    def onDeleteItem(self,item):
         # 1. 从 QListWidget 中移除
        row = self.ui.listWidget.row(item)
        if row != -1:
            self.ui.listWidget.takeItem(row)

        # 2. 从 path_entries 中去掉对应条目
        self.path_entries = [
            (r, it, pi) for (r, it, pi) in self.path_entries
            if it is not item
        ]
    
    def update_info(self, distance, radius):
        # 1. 获取当前 EntryPoint 世界坐标
        new_entry = util.get_world_control_point_by_name("EntryPoint")
        new_target = util.get_world_control_point_by_name("TargetPoint")

        # 2. 如果新点与已有任何条目的 entry_point 距离 ≤ 3mm，则丢弃
        for _, _, existing_item in self.path_entries:
            existing_entry = existing_item.entry_point
            dx = new_entry[0] - existing_entry[0]
            dy = new_entry[1] - existing_entry[1]
            dz = new_entry[2] - existing_entry[2]
            if math.sqrt(dx*dx + dy*dy + dz*dz) <= 3.0:
                return

        # 3. 半径下限过滤（可选）
        if radius < 1:
            return

        # 4. 创建新 PathItem
        item = qt.QListWidgetItem()
        path_item = PathItem(self, distance, radius, new_entry, new_target,item)
        item.setSizeHint(qt.QSize(160, 90))

        # 5. 按半径降序找到插入索引
        insert_index = 0
        for existing_radius, _, _ in self.path_entries:
            if radius < existing_radius:
                insert_index += 1
            else:
                break

        # 6. 插入到 listWidget 和 path_entries
        self.ui.listWidget.insertItem(insert_index, item)
        self.ui.listWidget.setItemWidget(item, path_item.uiwidget)
        self.path_entries.insert(insert_index, (radius, item, path_item))
        
        
        # 7. 超过 6 条时，删除最后一条
        if len(self.path_entries) > 6:
            _, last_item, _ = self.path_entries.pop()
            row = self.ui.listWidget.row(last_item)
            self.ui.listWidget.takeItem(row)
    
    def fresh_list(self):
        self.ui.listWidget.clear()
        self.path_entries.clear()
        for i in range(6):
            item = qt.QListWidgetItem(self.ui.listWidget)
            path_item = PathItem(self,12,24,[0,0,0],[100,100,100])
            item.setSizeHint(qt.QSize(180,64))
            self.ui.listWidget.setItemWidget(item,path_item.uiwidget)
            self.ui.listWidget.addItem(item)
    
    def set_btn_point_defined(self, btn, file_path):        
        btn.setStyleSheet("background-color: #56AC2B;background-image: url(" + file_path + ");")
        btn.setChecked(False)
        
    def bind_point_with_button(self,btn,point_node_name,label=None,file_path="",archive=False):
      import qt,slicer,vtk
      btn.setStyleSheet("QPushButton:checked{  background-color: #1765AD;background-image: url(" + file_path + ");}")
      def on_add_point(val):
        if val:
          btn.setStyleSheet("background-color: #1765AD;background-image: url(" + file_path + ");")
          point_node = util.getFirstNodeByName(point_node_name)
          if point_node:
            util.RemoveNode(point_node)
          point_node = util.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
          point_node.SetName(point_node_name)
          
          if point_node_name == "EntryPoint":
                pdLesion = self.logic.segmentationToPolyData(util.getFirstNodeByName("血肿"), "血肿")
                pdL5 = self.logic.segmentationToPolyData(util.getFirstNodeByName("Spine"), "vertebrae_L4")
                pdL6 = self.logic.segmentationToPolyData(util.getFirstNodeByName("Spine"), "vertebrae_L5")
                centerOfMassFilter = vtk.vtkCenterOfMass()
                centerOfMassFilter.SetInputData(pdLesion)
                centerOfMassFilter.SetUseScalarsAsWeights(False)
                centerOfMassFilter.Update()
                util.global_data_map["lesionCenter"] = centerOfMassFilter.GetCenter()

                boneAppend = vtk.vtkAppendPolyData()
                boneAppend.AddInputData(pdL5)
                boneAppend.AddInputData(pdL6)
                boneAppend.Update()
                pdBone = boneAppend.GetOutput()
                util.global_data_map["boneDistance"] = vtk.vtkImplicitPolyDataDistance()
                util.global_data_map["boneDistance"].SetInput(pdBone)
                    
          
          display_node = util.GetDisplayNode(point_node)
          display_node.SetPointLabelsVisibility(False)
          point_node.AddObserver(slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent, on_point_defined)
          point_node.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, on_point_modified)
          point_node.AddObserver(slicer.vtkMRMLMarkupsNode.PointStartInteractionEvent, on_start_interaction)
          point_node.AddObserver(slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent, on_stop_interaction)
          point_node.AddObserver(slicer.vtkMRMLMarkupsNode.PointRemovedEvent, on_point_removed)  
          interactionNode = slicer.app.applicationLogic().GetInteractionNode()
          selectionNode = slicer.app.applicationLogic().GetSelectionNode()
          selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
          selectionNode.SetActivePlaceNodeID(point_node.GetID())
          interactionNode.SetCurrentInteractionMode(interactionNode.Place)
        else:
          pass
        
      def on_point_defined(pointnode,event):
        if pointnode is None:
          return
        self.set_btn_point_defined(btn, file_path)
        if label:
          display_node = util.GetDisplayNode(pointnode)
          display_node.SetPointLabelsVisibility(False)
          pointnode.SetNthControlPointLabel(0,label)
      def on_point_modified(point_node,event):
            if point_node.GetName() == "EntryPoint":
                if util.getFirstNodeByName("TargetPoint") is None:
                    return
                util.global_data_map["lesionCenter"] = util.get_world_control_point_by_name("TargetPoint")
                markupsNode = util.getFirstNodeByName("EntryPoint")
                if markupsNode.GetNumberOfControlPoints() == 0:
                        return
                skinPoint = [0, 0, 0]
                markupsNode.GetNthControlPointPosition(0, skinPoint)

                distToLesion = np.linalg.norm(np.array(util.global_data_map["lesionCenter"]) - np.array(skinPoint))

                numSamples = 20
                minDist = float('inf')
                for k in range(numSamples + 1):
                    f = k / numSamples
                    p = [skinPoint[0] * (1 - f) + util.global_data_map["lesionCenter"][0] * f,
                            skinPoint[1] * (1 - f) + util.global_data_map["lesionCenter"][1] * f,
                            skinPoint[2] * (1 - f) + util.global_data_map["lesionCenter"][2] * f]
                    dist = util.global_data_map["boneDistance"].EvaluateFunction(p)
                    if dist < minDist:
                        minDist = dist

                riskText = "\n⚠️ 路径风险: 穿近骨" if minDist < 0.1 else "\n✅ 路径安全"

                self.ui.label_2.setText(f"入点到靶点: {distToLesion:.2f} mm\n最大半径: {minDist:.2f} mm{riskText}")
                lineSource = vtk.vtkLineSource()
                lineSource.SetPoint1(skinPoint)
                lineSource.SetPoint2(util.global_data_map["lesionCenter"])
                lineSource.Update()

                util.RemoveNodeByName("Temp_SkinToTumor_Line")
                modelNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "Temp_SkinToTumor_Line")
                modelNode.SetAndObservePolyData(lineSource.GetOutput())
                displayNode = util.GetDisplayNode(modelNode)
                displayNode.SetColor(1.0, 0.0, 0.0) if minDist < 0.1 else displayNode.SetColor(0.0, 1.0, 0.0)
                displayNode.SetLineWidth(2)
                self.update_info(distToLesion,minDist)
                
                
                
        #print("on_point_modified",point_node.GetID(),event)
      
      def on_start_interaction(point_node,event):
        print("on_start_interaction",point_node.GetID(),event)
        btn.setStyleSheet("background-color: #1765AD;background-image: url(" + file_path + ");")
      def on_stop_interaction(point_node,event):
        print("on_stop_interaction",point_node.GetID(),event)
        btn.setStyleSheet("background-color: #56AC2B;background-image: url(" + file_path + ");")
      def on_point_removed(point_node,event):
        #print("on_point_removed",point_node.GetID(),event)
        btn.setChecked(False)
        btn.setStyleSheet("background-color: #2d3745;background-image: url(" + file_path + ");")
      
      @vtk.calldata_type(vtk.VTK_OBJECT)
      def onNodeRemove(scene,event,calldata):
        if (calldata.GetName() == point_node_name):
          btn.setChecked(False)
          btn.setStyleSheet("background-color: #2d3745;background-image: url(" + file_path + ");")
          
      btn.setCheckable(True)
      btn.setStyleSheet("background-color: #2d3745;background-image: url(" + file_path + ");")
      btn.connect('toggled(bool)', on_add_point)
      slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeRemovedEvent, onNodeRemove)
        
      if archive:
        point_node = util.getFirstNodeByName(point_node_name)
        if not point_node:
          btn.setChecked(False)
          btn.setStyleSheet("background-color: #2d3745;background-image: url(" + file_path + ");")
          return
        point_node.AddObserver(slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent, on_point_defined)
        point_node.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, on_point_modified)
        point_node.AddObserver(slicer.vtkMRMLMarkupsNode.PointStartInteractionEvent, on_start_interaction)
        point_node.AddObserver(slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent, on_stop_interaction)
        point_node.AddObserver(slicer.vtkMRMLMarkupsNode.PointRemovedEvent, on_point_removed)  
        on_point_defined(point_node,"")
  
  
  
  
    def onParaCaculation(self):
        node1 = util.getFirstNodeByName("全分割")
        node2 = util.CreateDefaultSegmentationNode("Spine")
        
        n1 = util.GetSegmentNumber(node1)
        for i in range(n1):
            segment = util.GetNthSegment(node1,i)
            if segment:
                cname = segment.GetName()
                if  cname.startswith("vertebrae"):
                    node2.GetSegmentation().AddSegment(segment)
        util.HideNode(node1)
    
    def onParaCaculation2(self):
        # 计算L2下终板和L3上终板法线向量（通过选取表面上靠近终板的点并平面拟合）
        def fit_plane_normal(points):
            """利用点云PCA拟合平面，返回法线向量（单位向量）"""
            pts = np.array(points)
            centroid = pts.mean(axis=0)
            # 奇异值分解，最小奇异值对应法线方向:contentReference[oaicite:9]{index=9}
            U, S, Vt = np.linalg.svd(pts - centroid)
            normal = Vt[-1]  # 法线方向
            normal_unit = normal / np.linalg.norm(normal)
            return normal_unit

        # 筛选出L2段下表面点和L3段上表面点
        def get_endplate_points(polydata, top=True, fraction=0.1):
            """获取polydata顶部或底部一定比例(fraction)的点用于拟合终板平面"""
            pts = polydata.GetPoints()
            n = pts.GetNumberOfPoints()
            coords = [pts.GetPoint(i) for i in range(n)]
            # 根据Z坐标（RAS坐标中S轴）进行筛选
            zs = [p[2] for p in coords]
            if top:
                z_thresh = max(zs) - (max(zs) - min(zs)) * fraction
                endplate_pts = [p for p in coords if p[2] >= z_thresh]
            else:
                z_thresh = min(zs) + (max(zs) - min(zs)) * fraction
                endplate_pts = [p for p in coords if p[2] <= z_thresh]
            return endplate_pts
        
        skinSeg = util.getFirstNodeByName("skin")
        tumorSeg = util.getFirstNodeByName("tumor")
        spineSeg = util.getFirstNodeByName("spine")
        
        pdSkin = self.logic.segmentationToPolyData(skinSeg, "ROI")
        pdTumor = self.logic.segmentationToPolyData(tumorSeg, "artery")
        pdL5 = self.logic.segmentationToPolyData(spineSeg, "T10 vertebra")
        pdL6 = self.logic.segmentationToPolyData(spineSeg, "T11 vertebra")
        

        # 为加速最近点查找，构建vtkCellLocator用于两段表面
        locator_L3 = vtk.vtkCellLocator()
        locator_L3.SetDataSet(pdL5)  # 注意：这里交换顺序，以计算L3表面到L2表面的距离
        locator_L3.BuildLocator()
        locator_L2 = vtk.vtkCellLocator()
        locator_L2.SetDataSet(pdL6)  # 另一方向
        locator_L2.BuildLocator()

        # 遍历各表面顶点，计算最短距离及对应最近点
        minDist2 = float("inf")
        closestPt_L2 = [0.0, 0.0, 0.0]
        closestPt_L3 = [0.0, 0.0, 0.0]
        tmpPt = [0.0, 0.0, 0.0]
        cellId = vtk.reference(0)
        subId = vtk.reference(0)
        dist2 = vtk.reference(0.0)

        # L2每个顶点到L3表面的最近距离
        pts_L2 = pdL5.GetPoints()
        for i in range(pts_L2.GetNumberOfPoints()):
            pt = pts_L2.GetPoint(i)
            locator_L2.FindClosestPoint(pt, tmpPt, cellId, subId, dist2)
            if dist2.get() < minDist2:
                minDist2 = dist2.get()
                closestPt_L2 = list(pt)
                closestPt_L3 = list(tmpPt)

        # L3每个顶点到L2表面的最近距离
        pts_L3 = pdL6.GetPoints()
        for j in range(pts_L3.GetNumberOfPoints()):
            pt = pts_L3.GetPoint(j)
            locator_L3.FindClosestPoint(pt, tmpPt, cellId, subId, dist2)
            if dist2.get() < minDist2:
                minDist2 = dist2.get()
                closestPt_L3 = list(pt)
                closestPt_L2 = list(tmpPt)

        thickness = np.sqrt(minDist2)  # 最短距离（椎间隙厚度）
        print(f"L5-L6椎间隙最小厚度: {thickness:.2f} mm")
        
        
        L2_inferior_pts = get_endplate_points(pdL5, top=False)   # L2下终板附近点
        L3_superior_pts = get_endplate_points(pdL6, top=True)    # L3上终板附近点

        normal_L2 = fit_plane_normal(L2_inferior_pts)
        normal_L3 = fit_plane_normal(L3_superior_pts)
        # 为保证法线朝向相对（指向椎间隙），若两法线夹角大于90度则翻转一个方向
        if np.dot(normal_L2, normal_L3) < 0:
            normal_L3 = -normal_L3
        # 计算终板夹角（弧度转角度）
        angle_rad = np.arccos(np.clip(np.dot(normal_L2, normal_L3), -1.0, 1.0))
        angle_deg = float(np.degrees(angle_rad))
        print(f"L5-L6终板夹角: {angle_deg:.2f}°")

        # 计算椎间隙中心点（取最近点连线的中点）
        center = [(closestPt_L2[i] + closestPt_L3[i]) / 2.0 for i in range(3)]

        # 创建3D可视化对象：
        # 1. 穿刺路径线段模型（连接最近点的直线）
        lineSource = vtk.vtkLineSource()
        lineSource.SetPoint1(closestPt_L2[0], closestPt_L2[1], closestPt_L2[2])
        lineSource.SetPoint2(closestPt_L3[0], closestPt_L3[1], closestPt_L3[2])
        lineSource.Update()
        util.RemoveNodeByName("L5-L6_PuncturePath")
        util.RemoveNodeByName("sphereModel")
        util.RemoveNodeByName("L5-L6_Angle")
        util.RemoveNodeByName("MinBoneDistPath")
        lineModel = slicer.modules.models.logic().AddModel(lineSource.GetOutput())
        lineModel.SetName("L5-L6_PuncturePath")
        lineModel.GetDisplayNode().SetColor(0.0, 1.0, 0.0)    # 绿色线段
        lineModel.GetDisplayNode().SetLineWidth(2)

        # 2. 椎间隙中心点模型（小球）
        sphereSource = vtk.vtkSphereSource()
        sphereSource.SetCenter(center[0], center[1], center[2])
        sphereSource.SetRadius(2.0)  # 半径可根据需要调整
        sphereSource.Update()
        sphereModel = slicer.modules.models.logic().AddModel(sphereSource.GetOutput())
        sphereModel.SetName("L5-L6_DiscCenter")
        sphereModel.GetDisplayNode().SetColor(1.0, 0.0, 0.0)   # 红色球体标记

        # 3. （可选）终板夹角标记：使用Markups Angle在3D视图显示角度弧线
        angleNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsAngleNode", "L5-L6_Angle")
        # 取中心点，并沿两法线方向各取一定距离的点来定义角度
        pt_center = vtk.vtkVector3d(center[0], center[1], center[2])
        len_mm = 30.0  # 角两侧点离中心的距离
        pt1 = vtk.vtkVector3d(center[0] + normal_L2[0]*len_mm,
                            center[1] + normal_L2[1]*len_mm,
                            center[2] + normal_L2[2]*len_mm)
        pt2 = vtk.vtkVector3d(center[0] + normal_L3[0]*len_mm,
                            center[1] + normal_L3[1]*len_mm,
                            center[2] + normal_L3[2]*len_mm)
        angleNode.AddControlPoint(pt1)        # 终板L2方向点
        angleNode.AddControlPoint(pt_center)  # 顶点（中心）
        angleNode.AddControlPoint(pt2)        # 终板L3方向点
        angleNode.GetDisplayNode().SetTextScale(2)  # 放大文字显示
        
    
    


    
    def onPlanMinBoneDistPath(self):
        skinSeg = util.getFirstNodeByName("skin")
        tumorSeg = util.getFirstNodeByName("tumor")
        spineSeg = util.getFirstNodeByName("spine")

        pdSkin = self.logic.segmentationToPolyData(skinSeg, "ROI")
        pdTumor = self.logic.segmentationToPolyData(tumorSeg, "artery")
        pdL5 = self.logic.segmentationToPolyData(spineSeg, "T10 vertebra")
        pdL6 = self.logic.segmentationToPolyData(spineSeg, "T11 vertebra")

        # Combine L5 and L6 to form full bone model
        boneAppend = vtk.vtkAppendPolyData()
        boneAppend.AddInputData(pdL5)
        boneAppend.AddInputData(pdL6)
        boneAppend.Update()
        pdBone = boneAppend.GetOutput()

        # Collision detector
        obbTree = vtk.vtkOBBTree()
        obbTree.SetDataSet(pdBone)
        obbTree.BuildLocator()

        # Distance field
        boneDistance = vtk.vtkImplicitPolyDataDistance()
        boneDistance.SetInput(pdBone)

        skinPts = self.logic.samplePoints(pdSkin, 50)
        tumorPts = self.logic.samplePoints(pdTumor, 50)

        bestDist = -1
        bestE, bestT = None, None

        for i in range(skinPts.GetNumberOfPoints()):
            e = skinPts.GetPoint(i)
            for j in range(tumorPts.GetNumberOfPoints()):
                t = tumorPts.GetPoint(j)

                # First check: is this path collision-free?
                ptsIntersect = vtk.vtkPoints()
                cellIds = vtk.vtkIdList()
                obbTree.IntersectWithLine(e, t, ptsIntersect, cellIds)
                if ptsIntersect.GetNumberOfPoints() > 0:
                    continue  # Skip this path, it intersects bone

                # If safe, compute minimum distance to bone along path
                numSamples = 50
                minDist = float("inf")
                for k in range(numSamples + 1):
                    f = k / numSamples
                    p = [e[0]*(1-f) + t[0]*f,
                        e[1]*(1-f) + t[1]*f,
                        e[2]*(1-f) + t[2]*f]
                    d = boneDistance.EvaluateFunction(p)
                    if d < minDist:
                        minDist = d

                if minDist > bestDist:
                    bestDist = minDist
                    bestE = e
                    bestT = t

        if bestE is None:
            slicer.util.warningDisplay("未找到有效路径（所有路径与椎体发生碰撞）")
            return

        # Draw result
        line = vtk.vtkLineSource()
        line.SetPoint1(bestE)
        line.SetPoint2(bestT)
        line.Update()
        util.RemoveNodeByName("MaxSafePath")
        modelNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "MaxSafePath")
        modelNode.SetAndObservePolyData(line.GetOutput())
        displayNode = util.GetDisplayNode(modelNode)
        displayNode.SetColor(1.0, 0.0, 0.0)  # Red line
        displayNode.SetLineWidth(3)

        # Add entry and target markers
        def createSphere(point, color, name):
            sphere = vtk.vtkSphereSource()
            sphere.SetCenter(*point)
            sphere.SetRadius(1.5)
            sphere.Update()
            util.RemoveNodeByName(name)
            node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", name)
            node.SetAndObservePolyData(sphere.GetOutput())
            return node

        createSphere(bestE, (0.0, 1.0, 0.0), "EntryPoint")  # green
        createSphere(bestT, (0.0, 0.0, 1.0), "TargetPoint")  # blue

        slicer.util.infoDisplay(f"最安全路径已生成，路径最小骨距: {bestDist:.2f} mm")
    
    def onExtractSkinFromScissors(self):
        skinSeg = util.getFirstNodeByName("skin")
        skinSeg.GetSegmentation().AddEmptySegment("ROI")
        skinSeg.GetSegmentation().GetSegment("ROI").SetColor(1.0, 0.0, 0.0)
        sid = util.GetNthSegmentID(skinSeg,1)
        segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
        segmentEditorWidget.setSegmentationNode(skinSeg)
        segmentEditorWidget.setSourceVolumeNode(util.getFirstNodeByName("CTChest"))
        segmentEditorWidget.setCurrentSegmentID(sid)
        slicer.modules.SegmentEditorWidget.editor.setActiveEffectByName("Scissors")
        effect = segmentEditorWidget.activeEffect()
        effect.setParameter("EditIn3DViews", 1)
        effect.setParameter("Shape", "FreeForm")
        effect.setParameter("Operation", "FillInside")
        segmentEditorWidget.mrmlSegmentEditorNode().SetOverwriteMode(2)
        segmentEditorWidget.mrmlSegmentEditorNode().SetMaskSegmentID(util.GetNthSegmentID(skinSeg,0))
        segmentEditorWidget.mrmlSegmentEditorNode().SetMaskMode(slicer.vtkMRMLSegmentationNode.EditAllowedInsideSingleSegment)
        
    def onFindOptimalTarget(self):
        skinMarkups = slicer.util.getNode("TempSkinPoint")
        if skinMarkups.GetNumberOfControlPoints() == 0:
            slicer.util.warningDisplay("请先在皮肤上放置 TempSkinPoint 标记")
            return
        skinPoint = [0, 0, 0]
        skinMarkups.GetNthFiducialPosition(0, skinPoint)

        spineSeg = util.getFirstNodeByName("spine")
        lesionSeg = util.getFirstNodeByName("tumor")
        self.logic.findBestTargetFromSkinPoint(skinPoint, lesionSeg, spineSeg, "T10 vertebra", "T11 vertebra")
        
        
    def onPickSkinPoint(self):
            skinSeg = util.getFirstNodeByName("skin")
            lesionSeg = util.getFirstNodeByName("tumor")
            spineSeg = util.getFirstNodeByName("spine")
            self.logic.pickSkinPointAndShowPath(skinSeg, lesionSeg, spineSeg, "T10 vertebra", "T11 vertebra")

    def onApplyButton(self):  # noqa: D102
        spineSeg = util.getFirstNodeByName("spine")
        skinSeg = util.getFirstNodeByName("skin")
        lesionSeg = util.getFirstNodeByName("tumor")
        numEntries = int(self.entrySpinBox.value)
        numTargets = int(self.targetSpinBox.value)
        margin = float(self.marginDoubleSpinBox.value)
        self.logic.planNeedlePaths(spineSeg, "T10 vertebra", "T11 vertebra",
                                    skinSeg, lesionSeg,
                                    numEntries, numTargets, margin)
        

class UnitSpineChannelLogic(ScriptedLoadableModuleLogic):  # noqa: D102
    def segmentationToPolyData(self, segNode, segmentName):
        import vtk
        closedSurfacePolyData = vtk.vtkPolyData()
        segment_id = segNode.GetSegmentation().GetSegmentIdBySegmentName(segmentName)
        print(segNode.GetName(),segmentName,segment_id)
        segNode.CreateClosedSurfaceRepresentation()
        segNode.GetClosedSurfaceRepresentation(segment_id, closedSurfacePolyData)
        return closedSurfacePolyData
        import slicer,vtk
        shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        exportFolderItemId = shNode.CreateFolderItem(shNode.GetSceneItemID(), "abc")
        segment_id = segNode.GetSegmentation().GetSegmentIdBySegmentName(segmentName)
        slicer.modules.segmentations.logic().ExportSegmentsToModels(segNode,[segment_id], exportFolderItemId)
        segmentModels = vtk.vtkCollection()
        shNode.GetDataNodesInBranch(exportFolderItemId, segmentModels)
        ModelNode = segmentModels.GetItemAsObject(0)
        return ModelNode.GetPolyData()


    def samplePoints(self, polyData, numberOfPoints):  # noqa: D102
        mask = vtk.vtkMaskPoints()
        mask.SetInputData(polyData)
        nPts = polyData.GetNumberOfPoints()
        if nPts > numberOfPoints:
            mask.SetOnRatio(int(nPts / numberOfPoints))
        mask.RandomModeOn()
        mask.Update()
        return mask.GetOutput().GetPoints()

    
    def findBestTargetFromSkinPoint(self, skinPoint, lesionSeg, spineSeg, l5Name, l6Name):
        pdLesion = self.segmentationToPolyData(lesionSeg, "Segment_1")
        util.remove_folder_single("abc")
        pdL5 = self.segmentationToPolyData(spineSeg, l5Name)
        util.remove_folder_single("abc")
        pdL6 = self.segmentationToPolyData(spineSeg, l6Name)
        util.remove_folder_single("abc")

        boneAppend = vtk.vtkAppendPolyData()
        boneAppend.AddInputData(pdL5)
        boneAppend.AddInputData(pdL6)
        boneAppend.Update()
        pdBone = boneAppend.GetOutput()
        boneDistance = vtk.vtkImplicitPolyDataDistance()
        boneDistance.SetInput(pdBone)

        candidates = self.samplePoints(pdLesion, 200)
        bestDist = -1
        bestTarget = None
        for i in range(candidates.GetNumberOfPoints()):
            tgt = candidates.GetPoint(i)
            minDist = float('inf')
            for k in range(21):
                f = k / 20
                p = [skinPoint[0] * (1 - f) + tgt[0] * f,
                     skinPoint[1] * (1 - f) + tgt[1] * f,
                     skinPoint[2] * (1 - f) + tgt[2] * f]
                d = boneDistance.EvaluateFunction(p)
                if d < minDist:
                    minDist = d
            if minDist > bestDist:
                bestDist = minDist
                bestTarget = tgt

        if bestTarget is None:
            slicer.util.warningDisplay("无法在病灶中找到有效目标点")
            return

        slicer.util.infoDisplay(f"最优目标点路径最小骨距: {bestDist:.2f} mm")

        lineSource = vtk.vtkLineSource()
        lineSource.SetPoint1(skinPoint)
        lineSource.SetPoint2(bestTarget)
        lineSource.Update()

        util.RemoveNodeByName("OptimalTargetPath")
        modelNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "OptimalTargetPath")
        modelNode.SetAndObservePolyData(lineSource.GetOutput())
        displayNode = util.GetDisplayNode(modelNode)
        if bestDist < 3.0:
            displayNode.SetColor(1.0, 0.0, 0.0)
        else:
            displayNode.SetColor(0.0, 1.0, 0.0)
        displayNode.SetLineWidth(3)
        
        
    def pickSkinPointAndShowPath(self, skinSeg, lesionSeg, spineSeg, l5Name, l6Name):
        pdSkin = self.segmentationToPolyData(skinSeg, "Segment_1")
        util.remove_folder_single("abc")
        pdLesion = self.segmentationToPolyData(lesionSeg, "Segment_1")
        util.remove_folder_single("abc")
        pdL5 = self.segmentationToPolyData(spineSeg, l5Name)
        util.remove_folder_single("abc")
        pdL6 = self.segmentationToPolyData(spineSeg, l6Name)
        util.remove_folder_single("abc")

        centerOfMassFilter = vtk.vtkCenterOfMass()
        centerOfMassFilter.SetInputData(pdLesion)
        centerOfMassFilter.SetUseScalarsAsWeights(False)
        centerOfMassFilter.Update()
        lesionCenter = centerOfMassFilter.GetCenter()

        markupsNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", "TempSkinPoint")
        markupsNode.RemoveAllMarkups()

        boneAppend = vtk.vtkAppendPolyData()
        boneAppend.AddInputData(pdL5)
        boneAppend.AddInputData(pdL6)
        boneAppend.Update()
        pdBone = boneAppend.GetOutput()
        boneDistance = vtk.vtkImplicitPolyDataDistance()
        boneDistance.SetInput(pdBone)

        def onPointModified(caller, event):
            if markupsNode.GetNumberOfControlPoints() == 0:
                return
            skinPoint = [0, 0, 0]
            markupsNode.GetNthFiducialPosition(0, skinPoint)

            distToLesion = np.linalg.norm(np.array(lesionCenter) - np.array(skinPoint))

            numSamples = 20
            minDist = float('inf')
            for k in range(numSamples + 1):
                f = k / numSamples
                p = [skinPoint[0] * (1 - f) + lesionCenter[0] * f,
                     skinPoint[1] * (1 - f) + lesionCenter[1] * f,
                     skinPoint[2] * (1 - f) + lesionCenter[2] * f]
                dist = boneDistance.EvaluateFunction(p)
                if dist < minDist:
                    minDist = dist

            riskText = "\n⚠️ 路径风险: 穿近骨" if minDist < 0.1 else "\n✅ 路径安全"

            print(f"皮肤点到病灶中心: {distToLesion:.2f} mm\n路径与椎体最短距离: {minDist:.2f} mm{riskText}")

            lineSource = vtk.vtkLineSource()
            lineSource.SetPoint1(skinPoint)
            lineSource.SetPoint2(lesionCenter)
            lineSource.Update()

            util.RemoveNodeByName("Temp_SkinToTumor_Line")
            modelNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "Temp_SkinToTumor_Line")
            modelNode.SetAndObservePolyData(lineSource.GetOutput())
            displayNode = util.GetDisplayNode(modelNode)
            displayNode.SetColor(1.0, 0.0, 0.0) if minDist < 0.1 else displayNode.SetColor(0.0, 1.0, 0.0)
            displayNode.SetLineWidth(2)


        markupsNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, onPointModified)
        interactionNode = slicer.app.applicationLogic().GetInteractionNode()
        selectionNode = slicer.app.applicationLogic().GetSelectionNode()
        selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
        selectionNode.SetActivePlaceNodeID(markupsNode.GetID())
        interactionNode.SetCurrentInteractionMode(interactionNode.Place)
        
    def planNeedlePaths(self, spineSeg, l5Name, l6Name,
                    skinSeg, lesionSeg,
                    numEntries, numTargets, margin):
        pdL5 = self.segmentationToPolyData(spineSeg, l5Name)
        util.remove_folder_single("abc")
        pdL6 = self.segmentationToPolyData(spineSeg, l6Name)
        util.remove_folder_single("abc")
        pdSkin = self.segmentationToPolyData(skinSeg, "Segment_1")
        util.remove_folder_single("abc")
        pdLesion = self.segmentationToPolyData(lesionSeg, "Segment_1")
        util.remove_folder_single("abc")

        # Combine L5 and L6 for unified collision detection
        append = vtk.vtkAppendPolyData()
        append.AddInputData(pdL5)
        append.AddInputData(pdL6)
        append.Update()
        pdBone = append.GetOutput()

        # Create distance calculator from bone surface
        boneDistance = vtk.vtkImplicitPolyDataDistance()
        boneDistance.SetInput(pdBone)

        # ROI bounds
        b5 = pdL5.GetBounds()
        b6 = pdL6.GetBounds()
        zmin = max(b5[4], b6[4])
        zmax = min(b5[5], b6[5])
        xmin = min(b5[0], b6[0]) - margin
        xmax = max(b5[1], b6[1]) + margin
        ymin = min(b5[2], b6[2]) - margin
        ymax = max(b5[3], b6[3]) + margin
        box = vtk.vtkBox()
        box.SetBounds(xmin, xmax, ymin, ymax, zmin, zmax)

        def clipPolyData(inputPd):
            clipper = vtk.vtkClipPolyData()
            clipper.SetInputData(inputPd)
            clipper.SetClipFunction(box)
            clipper.InsideOutOn()
            clipper.Update()
            return clipper.GetOutput()

        pdLesionROI = clipPolyData(pdLesion)
        pdSkinROI = clipPolyData(pdSkin)

        targets = self.samplePoints(pdLesionROI, numTargets)
        entries = self.samplePoints(pdSkinROI, numEntries)

        # Build bone collision OBBTree
        obb = vtk.vtkOBBTree()
        obb.SetDataSet(pdBone)
        obb.BuildLocator()

        # Clear previous paths
        for n in slicer.util.getNodesByClass('vtkMRMLModelNode'):
            if n.GetName().startswith('NeedlePaths_'):
                slicer.mrmlScene.RemoveNode(n)

        # Store feasible paths: (minBoneDistanceAlongPath, entry, target)
        pathData = []
        for i in range(entries.GetNumberOfPoints()):
            e = entries.GetPoint(i)
            for j in range(targets.GetNumberOfPoints()):
                t = targets.GetPoint(j)
                ptsIntersect = vtk.vtkPoints()
                cellIds = vtk.vtkIdList()
                obb.IntersectWithLine(e, t, ptsIntersect, cellIds)
                if ptsIntersect.GetNumberOfPoints() == 0:
                    # Check minimum distance from line to bone surface
                    numSamples = 20
                    minDist = float('inf')
                    for k in range(numSamples + 1):
                        f = k / numSamples
                        p = [e[0] * (1 - f) + t[0] * f,
                            e[1] * (1 - f) + t[1] * f,
                            e[2] * (1 - f) + t[2] * f]
                        dist = boneDistance.EvaluateFunction(p)
                        if dist < minDist:
                            minDist = dist
                    pathData.append((minDist, e, t))

        if len(pathData) == 0:
            slicer.util.messageBox("未找到可行路径")
            return

        # 保留最“安全”的6条路径（离骨最远）
        pathData.sort(key=lambda x: x[0], reverse=True)
        topPaths = pathData[:6]

        # 显示路径
        append = vtk.vtkAppendPolyData()
        for minDist, e, t in topPaths:
            line = vtk.vtkLineSource()
            line.SetPoint1(e)
            line.SetPoint2(t)
            line.Update()
            append.AddInputData(line.GetOutput())
        append.Update()
        util.RemoveNodeByName("NeedlePaths_Top6Safe")
        modelNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode', 'NeedlePaths_Top6Safe')
        modelNode.SetAndObservePolyData(append.GetOutput())
        displayNode = util.GetDisplayNode(modelNode)
        displayNode.SetColor(0.2, 0.8, 0.2)  # 安全路径：绿色
        displayNode.SetLineWidth(2)

        slicer.util.messageBox(f"已选出离椎体表面最远的6条安全路径。")



    
 