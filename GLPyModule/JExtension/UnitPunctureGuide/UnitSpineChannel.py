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
        self.ui.btn_area.connect('clicked()',self.onExtractSkinFromScissors)
        self.ui.btn_recommand.connect('clicked()',self.onApplyButton)
    
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
    
    def update_path_info(self):
        util.RemoveNodeByName("Temp_SkinToTumor_Line")
                
        lesionCenter = util.get_world_control_point_by_name("TargetPoint")
        markupsNode = util.getFirstNodeByName("EntryPoint")
        if markupsNode.GetNumberOfControlPoints() == 0:
                return
        if "boneDistance" not in util.global_data_map:
            return
        skinPoint = [0, 0, 0]
        markupsNode.GetNthControlPointPosition(0, skinPoint)

        distToLesion = np.linalg.norm(np.array(lesionCenter) - np.array(skinPoint))

        numSamples = 20
        minDist = float('inf')
        for k in range(numSamples + 1):
            f = k / numSamples
            p = [skinPoint[0] * (1 - f) + lesionCenter[0] * f,
                    skinPoint[1] * (1 - f) + lesionCenter[1] * f,
                    skinPoint[2] * (1 - f) + lesionCenter[2] * f]
            dist = util.global_data_map["boneDistance"].EvaluateFunction(p)
            if dist < minDist:
                minDist = dist

        riskText = "\n⚠️ 路径风险: 穿近骨" if minDist < 0.1 else "\n✅ 路径安全"

        self.ui.label_2.setText(f"入点到靶点: {distToLesion:.2f} mm\n最大半径: {minDist:.2f} mm{riskText}")
        lineSource = vtk.vtkLineSource()
        lineSource.SetPoint1(skinPoint)
        lineSource.SetPoint2(lesionCenter)
        lineSource.Update()

        modelNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "Temp_SkinToTumor_Line")
        modelNode.SetAndObservePolyData(lineSource.GetOutput())
        displayNode = util.GetDisplayNode(modelNode)
        displayNode.SetColor(1.0, 0.0, 0.0) if minDist < 0.1 else displayNode.SetColor(0.0, 1.0, 0.0)
        displayNode.SetLineWidth(2)
        self.update_info(distToLesion,minDist)
    
    
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
              
                spineSeg  = slicer.util.getFirstNodeByName("Spine")
                if util.getFirstNodeByName('TargetPoint'):
                    closest2 = self.findClosestSpineSegments(spineSeg, "TargetPoint", topN=2)
                    names = []
                    if closest2:
                        names = [f"{name}" for name, dist in closest2]
                    if len(names)!=2:
                        return
                    pdL5 = self.logic.segmentationToPolyData(util.getFirstNodeByName("Spine"), names[0])
                    pdL6 = self.logic.segmentationToPolyData(util.getFirstNodeByName("Spine"), names[1])
                

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
                util.RemoveNodeByName("Temp_SkinToTumor_Line")
                if util.getFirstNodeByName("TargetPoint") is None:
                    return
                self.update_path_info()
                
                
                
                
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
  

    def get_volume(self):
        volume = util.getFirstNodeByClassByAttribute(util.vtkMRMLScalarVolumeNode,"main_node","1")
        return volume


    def onExtractSkinFromScissors(self):
        skinSeg = util.getFirstNodeByName("皮肤")
        util.removeSegmentByName(skinSeg,"ROI")
        skinSeg.GetSegmentation().AddEmptySegment("ROI")
        skinSeg.GetSegmentation().GetSegment("ROI").SetColor(0.0, 1.0, 0.0)
        sid = util.GetNthSegmentID(skinSeg,1)
        segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
        segmentEditorWidget.setSegmentationNode(skinSeg)
        segmentEditorWidget.setSourceVolumeNode(self.get_volume())
        segmentEditorWidget.setCurrentSegmentID(sid)
        slicer.modules.SegmentEditorWidget.editor.setActiveEffectByName("Scissors")
        effect = segmentEditorWidget.activeEffect()
        effect.setParameter("EditIn3DViews", 1)
        effect.setParameter("Shape", "FreeForm")
        effect.setParameter("Operation", "FillInside")
        segmentEditorWidget.mrmlSegmentEditorNode().SetOverwriteMode(2)
        segmentEditorWidget.mrmlSegmentEditorNode().SetMaskSegmentID(util.GetNthSegmentID(skinSeg,0))
        segmentEditorWidget.mrmlSegmentEditorNode().SetMaskMode(slicer.vtkMRMLSegmentationNode.EditAllowedInsideSingleSegment)
        
        

    def onApplyButton(self):  # noqa: D102
        if util.getFirstNodeByName("TargetPoint") is None:
            util.showWarningText("请先创建靶点")
            return
        spineSeg  = slicer.util.getFirstNodeByName("Spine")
        closest2 = self.findClosestSpineSegments(spineSeg, "TargetPoint", topN=2)
        names = []
        if closest2:
            names = [f"{name}" for name, dist in closest2]
        if len(names)!=2:
            util.showWarningText("脊柱的分割数量小于2")
            return
    
        # 获取场景中的分割
        spineSeg  = util.getFirstNodeByName("Spine")
        skinSeg   = util.getFirstNodeByName("皮肤")
        numEntries = 1000   # 入口点采样数
        margin     = 10   # margin 仍可用于骨面范围扩展
        # 调用新的单路径规划函数
        EntryPoint = util.getFirstNodeByName("EntryPoint")
        TargetPoint = util.getFirstNodeByName("TargetPoint")
        if TargetPoint is None:
            util.showWarningText("请创建靶点")
            return
        if EntryPoint is None:
            util.showWarningText("请创建入点")
            return
        self.planSingleBestPath(
            spineSeg, names[0],  names[1],
            skinSeg,
            numEntries, margin
        )

    def findClosestSpineSegments(self, spineSegNode, controlPointName, topN=2):
        """
        返回距离控制点最近的 topN 个子分割名称及对应距离（mm）。
        """

        # 1. 获取控制点坐标
        ctrl = slicer.util.getFirstNodeByName(controlPointName)
        if not ctrl:
            slicer.util.errorDisplay(f"找不到控制点「{controlPointName}」")
            return []
        point = [0.0, 0.0, 0.0]
        ctrl.GetNthControlPointPositionWorld(0, point)

        # 2. 枚举所有子分割 ID
        segmentation = spineSegNode.GetSegmentation()
        idsArray = vtk.vtkStringArray()
        segmentation.GetSegmentIDs(idsArray)

        # 3. 对每个子分割，生成 PolyData 并计算距离
        distances = []
        for i in range(idsArray.GetNumberOfValues()):
            segID = idsArray.GetValue(i)
            seg = segmentation.GetSegment(segID)
            segName = seg.GetName()
            # 把该子分割转成 Closed Surface PolyData
            pd = self.logic.segmentationToPolyData(spineSegNode, segName)
            # 用 ImplicitDistance 来测点到表面的最短距离
            imp = vtk.vtkImplicitPolyDataDistance()
            imp.SetInput(pd)
            d = abs(imp.EvaluateFunction(point))
            distances.append((segName, d))

        # 4. 按距离升序排序，取前 topN
        distances.sort(key=lambda x: x[1])
        return distances[:topN]


    def samplePoints(self, polyData, numberOfPoints):  # noqa: D102
        mask = vtk.vtkMaskPoints()
        mask.SetInputData(polyData)
        nPts = polyData.GetNumberOfPoints()
        if nPts > numberOfPoints:
            mask.SetOnRatio(int(nPts / numberOfPoints))
        mask.RandomModeOn()
        mask.Update()
        return mask.GetOutput().GetPoints()  # 一定会返回 vtkPoints 对象

    def planSingleBestPath(self, spineSeg, l3Name, l4Name,
                        skinSeg,
                        numEntries, margin):
        """
        在全皮肤表面上寻找一个入口点，与血肿中心连线能在 L3/L4 上
        保持最大最小骨距（即安全半径最大）。
        """

        # ——— 1. 分割转 PolyData ———
        pdL3     = self.logic.segmentationToPolyData(spineSeg, l3Name)
        pdL4     = self.logic.segmentationToPolyData(spineSeg, l4Name)
        pdSkin   = self.logic.segmentationToPolyData(skinSeg,   "ROI")
        if pdSkin.GetNumberOfPoints() == 0:
            pdSkin   = self.logic.segmentationToPolyData(skinSeg,   "皮肤")
        lesionCenter = util.get_world_control_point_by_name("TargetPoint")

        # ——— 3. 合并 L3/L4，构建隐式距离场 & OBBTree ———
        appendBone = vtk.vtkAppendPolyData()
        appendBone.AddInputData(pdL3)
        appendBone.AddInputData(pdL4)
        appendBone.Update()
        pdBone = appendBone.GetOutput()

        boneDistance = vtk.vtkImplicitPolyDataDistance()
        boneDistance.SetInput(pdBone)

        obb = vtk.vtkOBBTree()
        obb.SetDataSet(pdBone)
        obb.BuildLocator()

        # ——— 4. 直接在全皮肤上采样入口点 ———
        entries = self.samplePoints(pdSkin, numEntries)
        if entries is None or entries.GetNumberOfPoints() == 0:
            slicer.util.messageBox("未能在皮肤上采样到入口点，请检查皮肤分割或增大 numEntries。")
            return

        # ——— 5. 遍历入口点，计算“入口→lesionCenter”路径的最小骨距，选最大者 ———
        bestEntry = None
        bestDist  = -1.0
        numSamples = 100

        for i in range(entries.GetNumberOfPoints()):
            e = entries.GetPoint(i)
            # 碰撞检测：若与骨相交，则跳过
            ptsIntersect = vtk.vtkPoints()
            ids          = vtk.vtkIdList()
            obb.IntersectWithLine(e, lesionCenter, ptsIntersect, ids)
            if ptsIntersect.GetNumberOfPoints() > 0:
                continue

            # 沿线等距采样，求最小距离
            minDist = float('inf')
            for k in range(numSamples + 1):
                f = k / numSamples
                p = [
                    e[0] * (1 - f) + lesionCenter[0] * f,
                    e[1] * (1 - f) + lesionCenter[1] * f,
                    e[2] * (1 - f) + lesionCenter[2] * f
                ]
                d = boneDistance.EvaluateFunction(p)
                if d < minDist:
                    minDist = d

            if minDist > bestDist:
                bestDist  = minDist
                bestEntry = e

        # ——— 6. 无可行路径时提示 ———
        if bestEntry is None:
            slicer.util.messageBox("未找到不穿透骨且满足安全距离的入口点。")
            return


        EntryPoint = util.getFirstNodeByName("EntryPoint")
        if EntryPoint:
            EntryPoint.SetNthControlPointPositionWorld(0,bestEntry)
            self.update_path_info()
        

class UnitSpineChannelLogic(ScriptedLoadableModuleLogic):  # noqa: D102
    def segmentationToPolyData(self, segNode, segmentName):
        import vtk
        closedSurfacePolyData = vtk.vtkPolyData()
        segment_id = segNode.GetSegmentation().GetSegmentIdBySegmentName(segmentName)
        segNode.CreateClosedSurfaceRepresentation()
        segNode.GetClosedSurfaceRepresentation(segment_id, closedSurfacePolyData)
        return closedSurfacePolyData


    

    
 