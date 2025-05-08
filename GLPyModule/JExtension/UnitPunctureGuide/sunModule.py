import logging
import os

import vtk

import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import slicer.util as util
import UnitPunctureGuideStyle as style
import numpy as np
#
# sunModule
#

class sunModule(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "sunModule"  # TODO: make this more human readable by adding spaces
        self.parent.categories = ["Examples"]  # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["John Doe (AnyWare Corp.)"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
See more information in <a href="https://github.com/organization/projectname#sunModule">module documentation</a>.
"""
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
"""




#
# sunModuleWidget
#

class sunModuleWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """
    btn_list = {}
    btn_list_red = []
    btn_list_green = []
    btn_list_yellow = []
    btn_list_mark = []
    btn_list_whole = []
    is_use_event = True
    reversed = False
    def __init__(self, parent=None):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._updatingGUIFromParameterNode = False

    def setup(self):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/sunModule.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)
        
        self.ui.pushButton_9.connect('clicked()',self.on_whole)
        self.ui.pushButton_13.connect('clicked()',self.on_blood_center)
        
        self.ui.a1.connect('toggled(bool)',self.on_change_red_visible1)
        self.ui.a2.connect('toggled(bool)',self.on_change_red_visible2)
        self.ui.a3.connect('toggled(bool)',self.on_change_red_visible3)
        self.ui.g1.connect('toggled(bool)',self.on_change_green_visible1)
        self.ui.g2.connect('toggled(bool)',self.on_change_green_visible2)
        self.ui.g3.connect('toggled(bool)',self.on_change_green_visible3)
        self.ui.y1.connect('toggled(bool)',self.on_change_yellow_visible1)
        self.ui.y2.connect('toggled(bool)',self.on_change_yellow_visible2)
        self.ui.y3.connect('toggled(bool)',self.on_change_yellow_visible3)
        self.ui.m1.connect('toggled(bool)',self.on_change_markups_visible1)
        self.ui.m2.connect('toggled(bool)',self.on_change_markups_visible2)
        self.ui.m3.connect('toggled(bool)',self.on_change_markups_visible3)
        self.ui.w1.connect('toggled(bool)',self.on_whole_visible1)
        self.ui.w2.connect('toggled(bool)',self.on_whole_visible2)
        self.ui.w3.connect('toggled(bool)',self.on_whole_visible3)
        
        self.ui.pushButton_2.connect('clicked()',self.on_place_head_frame)
        self.ui.pushButton.connect('toggled(bool)',self.on_open_headframe_module)
        
        self.ui.pushButton_15.connect('toggled(bool)',self.on_export_module)
        
        module_path = os.path.dirname(util.modulePath('sunModule'))

        file_path1 = (module_path + '/Resources/Icons/mark_earl.png').replace("\\", "/")
        self.bind_point_with_button(self.ui.pushButton_10,"left_p","LP", file_path1)
        file_path2 = (module_path + '/Resources/Icons/mark_earr.png').replace("\\", "/")
        self.bind_point_with_button(self.ui.pushButton_11,"right_p","RP", file_path2)
        file_path3 = (module_path + '/Resources/Icons/mark_nose.png').replace("\\", "/")
        self.bind_point_with_button(self.ui.pushButton_12,"nose","NP", file_path3)
        
        file_path5 = ""
        self.bind_point_with_button(self.ui.pushButton_16,"register_point_1","RG1")
        file_path6 = ""
        self.bind_point_with_button(self.ui.pushButton_17,"register_point_2","RG2")
        file_path7 = ""
        self.bind_point_with_button(self.ui.pushButton_18,"register_point_3","RG3")
        file_path8 = ""
        self.bind_point_with_button(self.ui.pushButton_19,"register_point_4","RG4")
        
        file_path4 = (module_path + '/Resources/Icons/mark_mananal.png').replace("\\", "/")
        self.bind_point_with_button(self.ui.pushButton_14,"blood_center","BP", file_path4)
        style.set_sun_style(module_path, self.ui)
        self.btn_list_red = [self.ui.a1, self.ui.a2, self.ui.a3]
        self.btn_list_green = [self.ui.g1, self.ui.g2, self.ui.g3]
        self.btn_list_yellow = [self.ui.y1, self.ui.y2, self.ui.y3]
        self.btn_list_mark = [self.ui.m1, self.ui.m2, self.ui.m3]
        self.btn_list_whole = [self.ui.w1, self.ui.w2, self.ui.w3]
        self.btn_list = {"left_p":(file_path1, self.ui.pushButton_10), "right_p":(file_path2, self.ui.pushButton_11), "nose":(file_path3, self.ui.pushButton_12), "blood_center":(file_path4, self.ui.pushButton_14), "register_point_1":(file_path5, self.ui.pushButton_16), "register_point_2":(file_path6, self.ui.pushButton_17), "register_point_3":(file_path6, self.ui.pushButton_18), "register_point_4":(file_path6, self.ui.pushButton_19)}
        #self.ui.pushButton.setEnabled(False)
        self.ui.pushButton_2.setEnabled(False)
        
        # self.ui.pushButton_10.connect('toggled(bool)',self.on_left_choosed)
        # self.ui.pushButton_11.connect('toggled(bool)',self.on_right_choosed)
        # self.ui.pushButton_12.connect('toggled(bool)',self.on_nose_choosed)
        self.ui.pushButton_3.connect('toggled(bool)',self.on_rotate_plane)
        
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
            self.ui.pushButton_2.setVisible(False)
            self.ui.pushButton.setVisible(False)
            self.ui.widget_2.setVisible(False)
        elif app_style == "1":
            self.ui.widget_2.setVisible(False)
            self.ui.pushButton_2.setVisible(False)
            self.ui.pushButton.setVisible(False)
            self.ui.label_13.setVisible(False)
            self.ui.pushButton_16.setVisible(False)
            self.ui.pushButton_17.setVisible(False)
            self.ui.pushButton_19.setVisible(False)
            self.ui.pushButton_18.setVisible(False)
    
    def on_end_1(self,a,b):
        return
        ori_node = util.getFirstNodeByName("ori_node")
        if not ori_node:
            return
        util.GetDisplayNode(ori_node).SetVisibility(False)
        util.singleShot(1100,lambda:util.GetDisplayNode(ori_node).SetVisibility(True))
    
    def on_rotate_1(self,a,b):
        ori_node = util.getFirstNodeByName("ori_node")
        if not ori_node:
            return
        orientationMatrix = ori_node.GetInteractionHandleToWorldMatrix()
        orientationMatrix.SetElement(0,3,0)
        orientationMatrix.SetElement(1,3,0)
        orientationMatrix.SetElement(2,3,0)
        orientationMatrix.SetElement(3,3,0)
        planeNode1 = util.getFirstNodeByName("axial_a")
        saggital_a = util.getFirstNodeByName("saggital_a")
        coronal_a = util.getFirstNodeByName("coronal_a")
        nose = util.getFirstNodeByName("nose")
        tranid = planeNode1.GetTransformNodeID()
        if tranid is  None:
            TNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLinearTransformNode")
            TNode.SetAndObserveMatrixTransformToParent(
                orientationMatrix
            )
            planeNode1.SetAndObserveTransformNodeID(TNode.GetID())
            saggital_a.SetAndObserveTransformNodeID(TNode.GetID())
            coronal_a.SetAndObserveTransformNodeID(TNode.GetID())
            nose.SetAndObserveTransformNodeID(TNode.GetID())
        else:
            TNode = util.GetNodeByID(tranid)
            TNode.SetAndObserveMatrixTransformToParent(
                orientationMatrix
            )
            
            
    def on_rotate_plane(self,val):
        ori_node = util.getFirstNodeByName("ori_node")
        if not ori_node:
            planeNode1 = util.getFirstNodeByName("axial_a")
            origin1 = [0.0, 0.0, 0.0]
            planeNode1.GetOriginWorld(origin1)
            ori_node = util.AddControlPointGlobal(origin1)
            ori_node.SetName("ori_node")
            util.GetDisplayNode(ori_node).SetPointLabelsVisibility(False)
            ori_node.AddObserver(slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent, self.on_end_1)
            ori_node.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, self.on_rotate_1)
        if val:
           util.GetDisplayNode(ori_node).SetVisibility(True)
           util.GetDisplayNode(ori_node).SetHandlesInteractive(True)
        else:
           util.GetDisplayNode(ori_node).SetVisibility(False)
           util.GetDisplayNode(ori_node).SetHandlesInteractive(False)
            
    
    
    def on_left_choosed(self,val):
        if val:
            util.on_camera_direction("L")
            util.reinit3D()
            self.translateAlong()
    def on_right_choosed(self,val):
        if val:
            util.on_camera_direction("R")
            util.reinit3D()
            self.translateAlong()
    def on_nose_choosed(self,val):
        if val:
            util.on_camera_direction("A")
            util.reinit3D()
            self.translateAlong()
    
    def _combine_segments(self,namelist):
        rnode = util.AddNewNodeByClass(util.vtkMRMLSegmentationNode) 
        rnode.CreateDefaultDisplayNodes()
        for name in namelist:
            tnode = util.getFirstNodeByName(name)
            if tnode:
                segment = util.GetNthSegment(tnode,0)
                rnode.GetSegmentation().AddSegment(segment)
        return rnode

    
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
    
    def get_volume(self):
        volume = util.getFirstNodeByClassByAttribute(util.vtkMRMLScalarVolumeNode,"main_node","1")
        return volume
    
    def on_export(self):
        util.RemoveNodeByName("headframe_centerball")
        nodes = util.getNodesByAttribute("flag_model_1","1")
        for node in nodes:
            util.RemoveNode(node)
        
        keyspoint = ["left_p","right_p","left_eye","right_eye","nose","TargetPoint","EntryPoint","frame_needle_left","frame_needle_right"]
        for kname in keyspoint:
            if util.getFirstNodeByName(kname) is None:
                util.showWarningText("缺少关键点:"+kname)
                return
        if util.getFirstNodeByName("皮肤") is None:
            util.showWarningText("请先创建皮肤")
            return
        
        if util.getFirstNodeByName("血肿") is None:
            util.showWarningText("请先创建血肿")
            return
        
        util.send_event_str(util.ProgressStart,"正在导出,请稍候...")
        util.send_event_str(util.ProgressValue,30)
        
        SN = self.create_segment_fiducials(["left_p"])
        SN.SetName("ASP1")
        SN = self.create_segment_fiducials(["right_p"])
        SN.SetName("ASP2")
        SN = self.create_segment_fiducials(["left_eye"])
        SN.SetName("ASP3")
        SN = self.create_segment_fiducials(["right_eye"])
        SN.SetName("ASP4")
        SN = self.create_segment_fiducials(["nose"])
        SN.SetName("ASP5")
        segment_node = self._combine_segments(["ASP1","ASP2","ASP3","ASP4","ASP5"])
        segment_node.SetName("KeyPoint")
        folderpath = util.get_project_base_path()
        for i in range(3):
            folderpath = os.path.dirname(folderpath)
        folderpath = os.path.join(folderpath,"PC").replace("\\","/")
        
        widget = util.getModuleWidget("OpenAnatomyExport")
        shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        itemIDToClone = shNode.GetItemByDataNode(segment_node)
        util.send_event_str(util.ProgressValue,50)
        if widget:
            widget.logic.exportModel(itemIDToClone,folderpath,0.1,"OBJ")
        util.RemoveNode(segment_node)
        
        SN = self.create_segment_fiducials(["frame_needle_left"])
        SN.SetName("DSP1")
        SN = self.create_segment_fiducials(["frame_needle_right"])
        SN.SetName("DSP2")
        segment_node = self._combine_segments(["皮肤","血肿","DS1","DS2"])
        segment_node.SetName("Skin")
        widget = util.getModuleWidget("OpenAnatomyExport")
        shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        itemIDToClone = shNode.GetItemByDataNode(segment_node)
        util.send_event_str(util.ProgressValue,50)
        if widget:
            widget.logic.exportModel(itemIDToClone,folderpath,0.9,"OBJ")
        util.RemoveNode(segment_node)
        util.send_event_str(util.ProgressValue,100)
        util.showWarningText("数据已经导出到:"+folderpath)
        
    def on_export2(self):
        util.RemoveNodeByName("headframe_centerball")
        nodes = util.getNodesByAttribute("flag_model_1","1")
        for node in nodes:
            util.RemoveNode(node)
        
        keyspoint = ["left_p","right_p","left_eye","right_eye","nose","TargetPoint","EntryPoint","frame_needle_left","frame_needle_right"]
        for kname in keyspoint:
            if util.getFirstNodeByName(kname) is None:
                util.showWarningText("缺少关键点:"+kname)
                return
        
        SN = self.create_segment_fiducials(["left_p","right_p","left_eye","right_eye","nose"])
        SN.SetName("关键点")
        SN = self.create_segment_fiducials(["TargetPoint","EntryPoint"])
        SN.SetName("靶点入点")
        SN = self.create_segment_fiducials(["frame_needle_left","frame_needle_right"])
        SN.SetName("头架点")
        folderpath = util.get_project_base_path()
        for i in range(3):
            folderpath = os.path.dirname(folderpath)
        folderpath = os.path.join(folderpath,"PC").replace("\\","/")
        
        if util.getFirstNodeByName("皮肤") is None:
            util.showWarningText("请先创建皮肤")
            return
        
        if util.getFirstNodeByName("血肿") is None:
            util.showWarningText("请先创建血肿")
            return
        
        models = util.global_data_map['frame_model_list']
        if len(models) > 0:
            a_node = util.AddNewNodeByClass(util.vtkMRMLModelNode)
            dynamicModelerNode = util.CreateNodeByClass("vtkMRMLDynamicModelerNode")
            dynamicModelerNode.SetToolName("Append")
            for model in models:
                if model.GetAttribute("fball_extra_widget")=="1":
                    continue
                dynamicModelerNode.AddNodeReferenceID("Append.InputModel",model.GetID())
            dynamicModelerNode.SetNodeReferenceID("Append.OutputModel",a_node.GetID())
            a_node.SetName("whole_frame")
            util.AddNode(dynamicModelerNode)
            util.RemoveNode(dynamicModelerNode)
        
        util.send_event_str(util.ProgressStart,"正在导出,请稍候...")
        util.send_event_str(util.ProgressValue,30)
        
        if len(models) > 0:
            segment_node = self._combine_segments(["皮肤","血肿","头架"])
        else:
            segment_node = self._combine_segments(["皮肤","血肿"])
        segment_node.SetName("skin")
        widget = util.getModuleWidget("OpenAnatomyExport")
        shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        itemIDToClone = shNode.GetItemByDataNode(segment_node)
        util.send_event_str(util.ProgressValue,50)
        if widget:
            widget.logic.exportModel(itemIDToClone,folderpath,0.97,"OBJ")
        util.RemoveNode(segment_node)
        
        segment_node = self._combine_segments(["关键点","靶点入点","头架点"])
        segment_node.SetName("markers")
        widget = util.getModuleWidget("OpenAnatomyExport")
        shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        itemIDToClone = shNode.GetItemByDataNode(segment_node)
        if widget:
            widget.logic.exportModel(itemIDToClone,folderpath,0.1,"OBJ")
        util.RemoveNode(segment_node)
        fm = util.getFirstNodeByName("whole_frame")
        util.getModuleLogic("SurfaceToolbox").decimate(fm,fm,0.6)
        util.saveNode(fm,folderpath+"/headframe.obj")
        util.send_event_str(util.ProgressValue,100)
        util.HideNodeByName("whole_frame")
        util.showWarningText("数据已经导出到:"+folderpath)
        
        
    def after_process(self):
        axial_a = util.getFirstNodeByName("axial_a")
        saggital_a = util.getFirstNodeByName("saggital_a")
        coronal_a = util.getFirstNodeByName("coronal_a")
        
        p1w = util.get_world_control_point_by_name("left_p")
        p2w = util.get_world_control_point_by_name("right_p")
        p3w = util.get_world_control_point_by_name("nose")
        
        
        axial_a_x = [0,0,0]
        axial_a_y = [0,0,0]
        axial_a_z = [0,0,0]
        axial_a_origin = [0,0,0]
        axial_a.GetAxesWorld(axial_a_x,axial_a_y,axial_a_z)
        axial_a.GetOrigin(axial_a_origin)
        
        # saggital_a_x = [0,0,0]
        # saggital_a_y = [0,0,0]
        # saggital_a_z = [0,0,0]
        # saggital_a_origin = [0,0,0]
        # saggital_a.GetAxesWorld(saggital_a_x,saggital_a_y,saggital_a_z)
        # saggital_a.GetOrigin(saggital_a_origin)
        
        # coronal_a_x = [0,0,0]
        # coronal_a_y = [0,0,0]
        # coronal_a_z = [0,0,0]
        # coronal_a_origin = [0,0,0]
        # coronal_a.GetAxesWorld(coronal_a_x,coronal_a_y,coronal_a_z)
        # coronal_a.GetOrigin(coronal_a_origin)
        
    
         
        # tp = np.array(saggital_a_origin)+np.array(axial_a_z)
        # vp = [0,0,0]
        # saggital_a.GetClosestPointOnPlaneWorld(tp,vp)
        # vec = np.array(vp)-np.array(saggital_a_origin)
        # angleAS = vtk.vtkMath.DegreesFromRadians(vtk.vtkMath.AngleBetweenVectors(saggital_a_x,vec))
        # transformToParentMatrix = vtk.vtkMatrix4x4()
        # transformToParentMatrix.Identity()
        # handleToParentMatrix=vtk.vtkTransform()
        # handleToParentMatrix.PostMultiply()
        # handleToParentMatrix.Concatenate(transformToParentMatrix)
        # handleToParentMatrix.Translate(-saggital_a_origin[0], -saggital_a_origin[1], -saggital_a_origin[2])
        # handleToParentMatrix.RotateWXYZ(-angleAS, saggital_a_z)
        # handleToParentMatrix.Translate(saggital_a_origin[0], saggital_a_origin[1], saggital_a_origin[2])
        # transformToParentMatrix.DeepCopy(handleToParentMatrix.GetMatrix())
        # transform_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
        # transform_node.SetMatrixTransformToParent(transformToParentMatrix)
        # saggital_a.SetAndObserveTransformNodeID(transform_node.GetID())
        # saggital_a.HardenTransform()
        # util.RemoveNode(transform_node)
        
        # tp = np.array(coronal_a_origin)+np.array(saggital_a_z)
        # vp = [0,0,0]
        # coronal_a.GetClosestPointOnPlaneWorld(tp,vp)
        # vec = np.array(vp)-np.array(coronal_a_origin)
        # angleSC = vtk.vtkMath.DegreesFromRadians(vtk.vtkMath.AngleBetweenVectors(coronal_a_x,vec))
        # transformToParentMatrix = vtk.vtkMatrix4x4()
        # transformToParentMatrix.Identity()
        # handleToParentMatrix=vtk.vtkTransform()
        # handleToParentMatrix.PostMultiply()
        # handleToParentMatrix.Concatenate(transformToParentMatrix)
        # handleToParentMatrix.Translate(-coronal_a_origin[0], -coronal_a_origin[1], -coronal_a_origin[2])
        # handleToParentMatrix.RotateWXYZ(-angleSC, coronal_a_z)
        # handleToParentMatrix.Translate(coronal_a_origin[0], coronal_a_origin[1], coronal_a_origin[2])
        # transformToParentMatrix.DeepCopy(handleToParentMatrix.GetMatrix())
        # transform_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
        # transform_node.SetMatrixTransformToParent(transformToParentMatrix)
        # coronal_a.SetAndObserveTransformNodeID(transform_node.GetID())
        # coronal_a.HardenTransform()
        # util.RemoveNode(transform_node)
        
        tp = np.array(axial_a_origin)+np.array(coronal_a_z)
        vp = [0,0,0]
        axial_a.GetClosestPointOnPlaneWorld(tp,vp)
        vec = np.array(vp)-np.array(axial_a_origin)
        angleCA = vtk.vtkMath.DegreesFromRadians(vtk.vtkMath.AngleBetweenVectors(axial_a_x,vec))
        transformToParentMatrix = vtk.vtkMatrix4x4()
        transformToParentMatrix.Identity()
        handleToParentMatrix=vtk.vtkTransform()
        handleToParentMatrix.PostMultiply()
        handleToParentMatrix.Concatenate(transformToParentMatrix)
        handleToParentMatrix.Translate(-axial_a_origin[0], -axial_a_origin[1], -axial_a_origin[2])
        handleToParentMatrix.RotateWXYZ(-angleCA, axial_a_z)
        handleToParentMatrix.Translate(axial_a_origin[0], axial_a_origin[1], axial_a_origin[2])
        transformToParentMatrix.DeepCopy(handleToParentMatrix.GetMatrix())
        transform_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
        transform_node.SetMatrixTransformToParent(transformToParentMatrix)
        axial_a.SetAndObserveTransformNodeID(transform_node.GetID())
        axial_a.HardenTransform()
        util.RemoveNode(transform_node)
    
    def enter_widget(self):
        print("enter")
        for key, (file_path, btn) in self.btn_list.items():
            print(f"Key: {key}, Value: {file_path}")
            
            point_node2 = util.getFirstNodeByName(key)
            if point_node2:
                numberOfFiducials = point_node2.GetNumberOfFiducials()
                print(numberOfFiducials, "numberOfFiducials")
                # 判断是否已经有点
                if numberOfFiducials > 0:
                    self.set_btn_point_defined(btn, file_path)
            else:
                print("test is none")
        self.is_use_event = False
        num = 0
        type1 = util.GetGlobalSaveValue("num_whole")
        if type1 != None:
            num = int(type1) - 1
        self.btn_list_whole[num].setChecked(True)
        
        num = 0
        type1 = util.GetGlobalSaveValue("num_red")
        if type1 != None:
            num = int(type1) - 1
        self.btn_list_red[num].setChecked(True)

        num = 0
        type1 = util.GetGlobalSaveValue("num_green")
        if type1 != None:
            num = int(type1) - 1
        self.btn_list_green[num].setChecked(True)

        num = 0
        type1 = util.GetGlobalSaveValue("num_yellow")
        if type1 != None:
            num = int(type1) - 1
        self.btn_list_yellow[num].setChecked(True)

        num = 0
        type1 = util.GetGlobalSaveValue("num_mark")
        if type1 != None:
            num = int(type1) - 1
        self.btn_list_mark[num].setChecked(True)
        self.is_use_event = True
    def on_whole_visible1(self,val):
        if not self.is_use_event:
            return
        if val:
            self.ui.a1.setChecked(True)
            self.ui.g1.setChecked(True)
            self.ui.y1.setChecked(True)
            self.ui.m1.setChecked(True)
            util.SetGlobalSaveValue("num_whole","1")

    
    def on_whole_visible2(self,val):
        if not self.is_use_event:
            return
        if val:
            self.ui.a2.setChecked(True)
            self.ui.g2.setChecked(True)
            self.ui.y2.setChecked(True)
            self.ui.m2.setChecked(True)
            util.SetGlobalSaveValue("num_whole","2")
    
    
      
    
    def on_place_head_frame(self):
        util.set_button_percent(self.ui.pushButton_2,0)
        modellist = util.getNodesByAttribute("is_head_frame","1")
        modellist = modellist + [util.getFirstNodeByName("headframenode_center"),util.getFirstNodeByName("frame_up"),util.getFirstNodeByName("frame_left"),util.getFirstNodeByName("frame_right"),util.getFirstNodeByName("frame_needle_right"),util.getFirstNodeByName("frame_needle_left"),util.getFirstNodeByName("toppoint_needle"),util.getFirstNodeByName("toppointright_needle")]
        for node in modellist:
            if node:
                util.RemoveNode(node)
                util.processEvents()
        util.set_button_percent(self.ui.pushButton_2,5)
        util.getModuleWidget("sunHeadFrame").reset()
        util.set_button_percent(self.ui.pushButton_2,10)
        if self.ui.comboBox.currentIndex == 0:
            self.load_head_frame()
        else:
            self.load_head_frame2()
        util.set_button_percent(self.ui.pushButton_2,90)
        util.color_unit_list.get_unit_by_alias_name("头架").one_opacity()
        util.set_button_percent(self.ui.pushButton_2,95)
        self.ui.pushButton.setEnabled(True)
        util.set_button_percent(self.ui.pushButton_2,100)
    
    def  on_open_headframe_module(self,val):
        if val:
            self.ui.pushButton_15.setChecked(False)
            util.trigger_view_tool("")
            util.layout_panel("middle_right").setMaximumWidth(300)
            util.layout_panel("middle_right").setMinimumWidth(300)
            util.layout_panel("middle_right").setModule("sunHeadFrame")
            util.layout_panel("middle_right").show()
        else:
            util.layout_panel("middle_right").setModule("")
            util.layout_panel("middle_right").hide()
        pass
    
    
    def  on_export_module(self,val):
        val1 = self._on_export_module(val)
        if val1 == -1:
            self.ui.pushButton_15.blockSignals(True)
            self.ui.pushButton_15.setChecked(False)
            self.ui.pushButton_15.blockSignals(False)
    
    def _on_export_module(self,val):
        if val:
            self.ui.pushButton.setChecked(False)
            util.trigger_view_tool("")
            util.layout_panel("middle_right").setMaximumWidth(300)
            util.layout_panel("middle_right").setMinimumWidth(300)
            util.layout_panel("middle_right").setModule("sunHeadExport")
            util.layout_panel("middle_right").show()
        else:
            util.layout_panel("middle_right").setModule("")
            util.layout_panel("middle_right").hide()
        pass
    
    def on_whole_visible3(self,val):
        if not self.is_use_event:
            return
        if val:
            self.ui.a3.setChecked(True)
            self.ui.g3.setChecked(True)
            self.ui.y3.setChecked(True)
            self.ui.m3.setChecked(True)
            util.SetGlobalSaveValue("num_whole","3")
    
    def on_change_red_visible1(self,val):
        markups = util.getFirstNodeByName("axial_a")
        if not markups:
            print("not axial_a")
            return
        if val:
            util.GetDisplayNode(markups).SetOpacity(1)
            util.GetDisplayNode(markups).SetVisibility(True)            
            util.SetGlobalSaveValue("num_red","1")
            return
    def on_change_red_visible2(self,val):
        markups = util.getFirstNodeByName("axial_a")
        if not markups:
            print("not axial_a")
            return
        if val:
            util.SetGlobalSaveValue("num_red","2")
            util.GetDisplayNode(markups).SetOpacity(0.3)
            util.GetDisplayNode(markups).SetVisibility(True)
            return
    def on_change_red_visible3(self,val):
        markups = util.getFirstNodeByName("axial_a")
        if not markups:
            print("not axial_a")
            return
        if val:
            util.SetGlobalSaveValue("num_red","3")
            util.GetDisplayNode(markups).SetOpacity(1)
            util.GetDisplayNode(markups).SetVisibility(False)
            return

    def on_change_green_visible1(self,val):
        markups = util.getFirstNodeByName("coronal_a")
        if not markups:
            print("not coronal_a")
            return
        if val:
            util.SetGlobalSaveValue("num_green","1")
            util.GetDisplayNode(markups).SetOpacity(1)
            util.GetDisplayNode(markups).SetVisibility(True)
            return
    def on_change_green_visible2(self,val):
        markups = util.getFirstNodeByName("coronal_a")
        if not markups:
            print("not coronal_a")
            return
        if val:
            util.SetGlobalSaveValue("num_green","2")
            util.GetDisplayNode(markups).SetOpacity(0.3)
            util.GetDisplayNode(markups).SetVisibility(True)
            return
    def on_change_green_visible3(self,val):
        markups = util.getFirstNodeByName("coronal_a")
        if not markups:
            print("not coronal_a")
            return
        if val:
            util.SetGlobalSaveValue("num_green","3")
            util.GetDisplayNode(markups).SetOpacity(1)
            util.GetDisplayNode(markups).SetVisibility(False)
            return
        
    
    def on_change_yellow_visible1(self,val):
        markups = util.getFirstNodeByName("saggital_a")
        if not markups:
            print("not saggital_a")
            return
        if val:
            util.SetGlobalSaveValue("num_yellow","1")
            util.GetDisplayNode(markups).SetOpacity(1)
            util.GetDisplayNode(markups).SetVisibility(True)
            return
    def on_change_yellow_visible2(self,val):
        markups = util.getFirstNodeByName("saggital_a")
        if not markups:
            print("not saggital_a")
            return
        if val:
            util.SetGlobalSaveValue("num_yellow","2")
            util.GetDisplayNode(markups).SetOpacity(0.3)
            util.GetDisplayNode(markups).SetVisibility(True)
            return
    def on_change_yellow_visible3(self,val):
        markups = util.getFirstNodeByName("saggital_a")
        if not markups:
            print("not saggital_a")
            return
        if val:
            util.SetGlobalSaveValue("num_yellow","3")
            util.GetDisplayNode(markups).SetOpacity(1)
            util.GetDisplayNode(markups).SetVisibility(False)
            return
     
    def on_change_markups_visible1(self,val):
        if val:
            markups = ["ls1","ls2","left_p","right_p","left_eye","right_eye","nose","blood_center","bs1","bs2"]
            util.SetGlobalSaveValue("num_mark","1")
            for markupname in markups:
                markup = util.getFirstNodeByName(markupname)
                if markup:
                    util.GetDisplayNode(markup).SetOpacity(1)
                    util.GetDisplayNode(markup).SetVisibility(True)  
            
            markups = self.get_lines()
            for markup in markups:
                if markup:
                    util.GetDisplayNode(markup).SetOpacity(1)
                    util.GetDisplayNode(markup).SetVisibility(True)  
                    
    def on_change_markups_visible2(self,val):
        if val:
            markups = ["ls1","ls2","left_p","right_p","left_eye","right_eye","nose","blood_center","bs1","bs2"]
            util.SetGlobalSaveValue("num_mark","2")
            for markupname in markups:
                markup = util.getFirstNodeByName(markupname)
                if markup:
                    util.GetDisplayNode(markup).SetOpacity(0.3)
                    util.GetDisplayNode(markup).SetVisibility(True)
                    
            markups = self.get_lines()
            for markup in markups:
                if markup:
                    util.GetDisplayNode(markup).SetOpacity(0.3)
                    util.GetDisplayNode(markup).SetVisibility(True) 
    
    def on_change_markups_visible3(self,val):
        if val:
            markups = ["ls1","ls2","left_p","right_p","nose","left_eye","right_eye","blood_center","bs1","bs2"]
            util.SetGlobalSaveValue("num_mark","3")

            for markupname in markups:
                markup = util.getFirstNodeByName(markupname)
                if markup:
                    util.GetDisplayNode(markup).SetOpacity(1)
                    util.GetDisplayNode(markup).SetVisibility(False) 
                    
            markups = self.get_lines()
            for markup in markups:
                if markup:
                    print("GGGGGGGGGGGGGGGGGAAAAAAAAAAA:",markup.GetName(),len(markups))
                    util.GetDisplayNode(markup).SetOpacity(1)
                    util.GetDisplayNode(markup).SetVisibility(False) 
        
    
    def get_lines(self):
        markups = []
        node = util.getFirstNodeByClassByAttribute(util.vtkMRMLMarkupsLineNode,"line_style","left_red")
        if node:
            markups.append(node)
        node = util.getFirstNodeByClassByAttribute(util.vtkMRMLMarkupsLineNode,"line_style","left_green")
        if node:
            markups.append(node)
        node = util.getFirstNodeByClassByAttribute(util.vtkMRMLMarkupsLineNode,"line_style","left_yellow")
        if node:
            markups.append(node)
        node = util.getFirstNodeByClassByAttribute(util.vtkMRMLMarkupsLineNode,"line_style","right_red")
        if node:
            markups.append(node)
        node = util.getFirstNodeByClassByAttribute(util.vtkMRMLMarkupsLineNode,"line_style","right_green")
        if node:
            markups.append(node)
        node = util.getFirstNodeByClassByAttribute(util.vtkMRMLMarkupsLineNode,"line_style","right_yellow")
        if node:
            markups.append(node)
        node = util.getFirstNodeByClassByAttribute(util.vtkMRMLMarkupsLineNode,"line_style","front_red")
        if node:
            markups.append(node)
        node = util.getFirstNodeByClassByAttribute(util.vtkMRMLMarkupsLineNode,"line_style","front_green")
        if node:
            markups.append(node)
        node = util.getFirstNodeByClassByAttribute(util.vtkMRMLMarkupsLineNode,"line_style","front_yellow")
        if node:
            markups.append(node)
        node = util.getFirstNodeByClassByAttribute(util.vtkMRMLMarkupsLineNode,"line_style","back_red")
        if node:
            markups.append(node)
        node = util.getFirstNodeByClassByAttribute(util.vtkMRMLMarkupsLineNode,"line_style","back_green")
        if node:
            markups.append(node)
        node = util.getFirstNodeByClassByAttribute(util.vtkMRMLMarkupsLineNode,"line_style","back_yellow")
        if node:
            markups.append(node)
        return markups
   
    def on_blood_center(self):
      import numpy as np
      util.RemoveNodeByName("blood_center")
      segmentation_node = util.getFirstNodeByName("血肿")
      if not segmentation_node:
        util.showWarningText("请先在[三维重建]中创建血肿")
        return
      
      segment_id = segmentation_node.GetSegmentation().GetNthSegmentID(0)  # 获取第一个segment的ID

      # 获取Segment的闭包曲面(polydata)
      segmentation = segmentation_node.GetSegmentation()
      segment = segmentation.GetSegment(segment_id)
      representation = segment.GetRepresentation(slicer.vtkSegmentationConverter.GetSegmentationClosedSurfaceRepresentationName())

      # 计算几何中心
      centroid = np.mean(representation.GetPoints().GetData(), axis=0)

      # 创建一个新的FiducialNode并添加点
      fiducial_node = util.CreateNodeByClass("vtkMRMLMarkupsFiducialNode")
      fiducial_node.SetName("blood_center")
      fiducial_node.AddFiducial(centroid[0], centroid[1], centroid[2])
      util.AddNode(fiducial_node)
      fiducial_node.SetNthControlPointLabel(0,"BP")
      
      self.ui.pushButton_14.setStyleSheet("background-color: #56AC2B;")
      self.ui.pushButton_14.setChecked(False)
      return fiducial_node


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
          display_node.SetPointLabelsVisibility(True)
          pointnode.SetNthControlPointLabel(0,label)
      def on_point_modified(point_node,event):
        #print("on_point_modified",point_node.GetID(),event)
        nv = util.get_world_control_point_by_name(point_node.GetName())
        fn = 2
      def on_start_interaction(point_node,event):
        print("on_start_interaction",point_node.GetID(),event)
        btn.setStyleSheet("background-color: #1765AD;background-image: url(" + file_path + ");")
      def on_stop_interaction(point_node,event):
        print("on_stop_interaction",point_node.GetID(),event)
        btn.setStyleSheet("background-color: #56AC2B;background-image: url(" + file_path + ");")
      def on_point_removed(point_node,event):
        #print("on_point_removed",point_node.GetID(),event)
        btn.setChecked(False)
        btn.setStyleSheet("background-color: #15395B;background-image: url(" + file_path + ");")
      
      @vtk.calldata_type(vtk.VTK_OBJECT)
      def onNodeRemove(scene,event,calldata):
        if (calldata.GetName() == point_node_name):
          btn.setChecked(False)
          btn.setStyleSheet("background-color: #15395B;background-image: url(" + file_path + ");")
          
      btn.setCheckable(True)
      btn.setStyleSheet("background-color: #15395B;background-image: url(" + file_path + ");")
      btn.connect('toggled(bool)', on_add_point)
      slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeRemovedEvent, onNodeRemove)
        
      if archive:
        point_node = util.getFirstNodeByName(point_node_name)
        if not point_node:
          btn.setChecked(False)
          btn.setStyleSheet("background-color: #15395B;background-image: url(" + file_path + ");")
          return
        point_node.AddObserver(slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent, on_point_defined)
        point_node.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, on_point_modified)
        point_node.AddObserver(slicer.vtkMRMLMarkupsNode.PointStartInteractionEvent, on_start_interaction)
        point_node.AddObserver(slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent, on_stop_interaction)
        point_node.AddObserver(slicer.vtkMRMLMarkupsNode.PointRemovedEvent, on_point_removed)  
        on_point_defined(point_node,"")
      
    def set_btn_point_defined(self, btn, file_path):        
        btn.setStyleSheet("background-color: #56AC2B;background-image: url(" + file_path + ");")
        btn.setChecked(False)
    
    
    def translateAlong(self):
        layoutManager = slicer.app.layoutManager()
        view = layoutManager.threeDWidget(0).threeDView()
        threeDViewNode = view.mrmlViewNode()
        cameraNode = slicer.modules.cameras.logic().GetViewActiveCameraNode(threeDViewNode)
        cameraNode.TranslateAlong(slicer.vtkMRMLCameraNode.Z,True)
        cameraNode.TranslateAlong(slicer.vtkMRMLCameraNode.Z,True)
        cameraNode.TranslateAlong(slicer.vtkMRMLCameraNode.Z,True)
        cameraNode.TranslateAlong(slicer.vtkMRMLCameraNode.Z,True)
        # cameraNode.TranslateAlong(slicer.vtkMRMLCameraNode.Z,True)
        # cameraNode.TranslateAlong(slicer.vtkMRMLCameraNode.Z,True)
        # cameraNode.TranslateAlong(slicer.vtkMRMLCameraNode.Z,True)
        # cameraNode.TranslateAlong(slicer.vtkMRMLCameraNode.Z,True)
        util.reinit3DLight()
    
    
    def load_frame_stl(self):
        modellist = []
        if self.ui.comboBox.currentIndex == 0:
            folder_path = self.resourcePath('STL/model_1').replace("\\","/")
        else:
            folder_path = self.resourcePath('STL/model_2').replace("\\","/")
        util.global_data_map['frame_model_list'] = []
        progress = 10
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(".stl"):
                file_path = os.path.join(folder_path, filename)
                nd = slicer.util.loadModel(file_path)
                util.GetDisplayNode(nd).SetColor([1,1,1])
                nd.SetAttribute("is_head_frame","1")
                progress+=0.5
                util.set_button_percent(self.ui.pushButton_2,int(progress))
                util.global_data_map['frame_model_list'].append(nd)
                if nd.GetName().split(".")[0] == "G22033 - G22033-001a-1":
                    nd.SetName("headframe_main")
                    nd.SetAttribute("alias_name","头架")
                if nd.GetName().split(".")[0] == "G22033 - G22032-006-1":
                    nd.SetName("left_stick_needle")
                if nd.GetName().split(".")[0] == "G22033 - G22036-006-1":
                    nd.SetName("right_stick_needle")
                if nd.GetName().split(".")[0] == "G22033 - G22033-006a-1":
                    nd.SetName("top_slider")  
                if nd.GetName().split(".")[0] == "G22033 - G22030-108-1":
                    nd.SetName("top_inner_slider")  
                if nd.GetName().split(".")[0] == "G22033 - G22033-108-2":
                    nd.SetName("top_inner_right_slider")  
                if nd.GetName().split(".")[0] == "G22033 - G22033-003-2":
                    nd.SetName("top_right_slider") 
                if nd.GetName().split(".")[0] == "G22033 - G22030-CCC-1":
                    nd.SetName("headframe_centerball")
                if nd.GetName().split(".")[0] == "G22033 - 2MM-1":
                    nd.SetName("top_needle")
                if nd.GetName().split(".")[0] == "G22033 - G22032-001-1":
                    nd.SetName("left_stick_pipe")   
                if nd.GetName().split(".")[0] == "G22033 - G22033-014a-1":
                    nd.SetName("right_stick_pipe")   
                if nd.GetName().split(".")[0] == "G22033 - 2MM-2":
                    nd.SetName("top_right_needle")
                if nd.GetName().split(".")[0] == "G22033 - G22033-001aCC-1":
                    nd.SetName("kedu1")
                    util.GetDisplayNode(nd).SetColor([0,0,0])
                if nd.GetName().split(".")[0] == "G22033 - G22033-017axxx2-1":
                    nd.SetName("kedu2")
                    util.GetDisplayNode(nd).SetColor([0,0,0])
                if nd.GetName().split(".")[0].find("G22033 - G22033-001aCCazx-1")!=-1:
                    nd.SetName("kedu4")
                    util.GetDisplayNode(nd).SetColor([0,0,0])
                if nd.GetName().split(".")[0] == "G22033 - G22033-017axxx-1":
                    nd.SetName("kedu3")
                    util.GetDisplayNode(nd).SetColor([0,0,0])
                if nd.GetName().split(".")[0] == "G22033 - G22033_001aCCazx-1":
                    nd.SetName("kedu6")
                    util.GetDisplayNode(nd).SetColor([0,0,0])
                if nd.GetName().split(".")[0] == "G22033 - G22033-001-1":
                    nd.SetName("left_kedu")
                    util.GetDisplayNode(nd).SetColor([0,0,0])
                if nd.GetName().split(".")[0] == "G22033 - G22033-002-1":
                    nd.SetName("down_kedu")
                    util.GetDisplayNode(nd).SetColor([0,0,0])
                if nd.GetName().split(".")[0] == "G22033 - G22033-001aCCxa-1":
                    nd.SetName("right_kedu")
                    util.GetDisplayNode(nd).SetColor([0,0,0])
                if nd.GetName().split(".")[0] == "G22033 - G22033-006akd-1":
                    nd.SetName("top_kedu")
                    util.GetDisplayNode(nd).SetColor([0,0,0])
                if nd.GetName().split(".")[0] == "G22033 _ G22033_006akd_2":
                    nd.SetName("top_kedu")
                    util.GetDisplayNode(nd).SetColor([0,0,0])
                if "G22033 _ G22033_028_1" in nd.GetName():
                    util.GetDisplayNode(nd).SetColor([1,0,0])
                if "G22033 _ G22033_028_2" in nd.GetName():
                    util.GetDisplayNode(nd).SetColor([1,0,0])
                if "G22033 _ G22033_028_3" in nd.GetName():
                    util.GetDisplayNode(nd).SetColor([1,0,0])
                if "G22033 _ G22033_028_4" in nd.GetName():
                    util.GetDisplayNode(nd).SetColor([1,0,0])
                if "G22033 _ G22033_028_5" in nd.GetName():
                    util.GetDisplayNode(nd).SetColor([1,0,0])
                if "G22033 _ G22033_028_6" in nd.GetName():
                    util.GetDisplayNode(nd).SetColor([1,0,0])
                modellist.append(nd)
                util.processEvents()
        
        
            
        util.HideNodeByName("headframe_centerball")
        util.HideNodeByName("right_stick_needle")
        util.HideNodeByName("top_right_needle")
        util.HideNodeByName("top_right_slider")
        util.HideNodeByName("top_inner_right_slider")
        util.HideNodeByName("down_kedu")
        util.HideNodeByName("G22033 - G22024-008-3.STL")
        util.HideNodeByName("G22033 - G22024-010-3.STL")
        util.getModuleWidget("sunHeadFrame").ui.label_7.setVisible(False)
        util.getModuleWidget("sunHeadFrame").ui.slider4.setVisible(False)
        util.getModuleWidget("sunHeadFrame").ui.label_9.setVisible(False)
        util.getModuleWidget("sunHeadFrame").ui.slider6.setVisible(False)
        
        headframe_main = util.getFirstNodeByName("headframe_main")
        util.color_unit_list.add_item(headframe_main, 3)
        util.tips_unit_list.add_item(headframe_main, 3)
        return modellist
    
    def on_whole(self):
        
        p1 = util.getFirstNodeByName("left_p")
        p2 = util.getFirstNodeByName("right_p")
        p3 = util.getFirstNodeByName("nose")
        blood_center = util.getFirstNodeByName("TargetPoint")
        if not p1:
            util.messageBox("请先选择左耳关键点")
            return
        if not p2:
            util.messageBox("请先选择右耳关键点")
            return
        if not p3:
            util.messageBox("请先选择鼻根关键点")
            return
        if not blood_center:
            util.messageBox("请先选择血肿中心点")
            return
        util.set_button_percent(self.ui.pushButton_9,0)
        self.on_red_panel()
        util.set_button_percent(self.ui.pushButton_9,10)
        util.processEvents()
        self.on_yellow_panel()
        util.set_button_percent(self.ui.pushButton_9,20)
        util.processEvents()
        self.on_green_panel()
        util.set_button_percent(self.ui.pushButton_9,30)
        self.on_tmp_markups()
        util.set_button_percent(self.ui.pushButton_9,40)
        self.on_interaction_points()
        
        util.getModuleWidget("sunHeadExport").statistics(self.ui.pushButton_9)
        
        volume = util.getFirstNodeByClassByAttribute(util.vtkMRMLScalarVolumeNode,"main_node","1")
        util.hideVolumeRendering(volume)
        util.color_unit_list.half_opacity()
        self.ui.pushButton_2.setEnabled(True)
        self.ui.pushButton_3.setEnabled(True)
        util.set_button_percent(self.ui.pushButton_9,100)
        
        
    
    def get_target_vector(self):
        if self.ui.radioButton_2.isChecked():
            nodes = util.getNodesByAttribute("is_ia_node","1")
            if  util.get_world_position(nodes[0])[0] - util.get_world_position(nodes[1])[0]<0:
                left_ear1 = util.get_world_position(nodes[0])
                right_ear1 = util.get_world_position(nodes[1])
            else:
                left_ear1 = util.get_world_position(nodes[1])
                right_ear1 = util.get_world_position(nodes[0])
            lp2 = np.array(left_ear1) - np.array(right_ear1)
        else:
            nodes = util.getNodesByAttribute("is_ap_node","1")
            if  util.get_world_position(nodes[0])[1] - util.get_world_position(nodes[1])[1]<0:
                left_ear1 = util.get_world_position(nodes[0])
                right_ear1 = util.get_world_position(nodes[1])
            else:
                left_ear1 = util.get_world_position(nodes[1])
                right_ear1 = util.get_world_position(nodes[0])
            lp2 = np.array(left_ear1) - np.array(right_ear1)
        
        
        return lp2
        
    
    def rotate_to_axial(self,modellist,normal_frame):
        planenode = util.getFirstNodeByName("axial_a")
        normal = planenode.GetNormal()
        if self.calculate_angle(normal,[0,0,1]) < 90 :
            normal = [-normal[0],-normal[1],-normal[2]]
            
        rotationVector_Local = np.array([0,0,0]).astype(np.float64)
        vtk.vtkMath.Cross(normal, normal_frame, rotationVector_Local)
        angle2 = vtk.vtkMath.DegreesFromRadians(vtk.vtkMath.AngleBetweenVectors(normal,normal_frame))
        
        transformToParentMatrix = vtk.vtkMatrix4x4()
        transformToParentMatrix.Identity()
        handleToParentMatrix=vtk.vtkTransform()
        handleToParentMatrix.PostMultiply()
        handleToParentMatrix.Concatenate(transformToParentMatrix)
        handleToParentMatrix.RotateWXYZ(-angle2, rotationVector_Local)
        transformToParentMatrix.DeepCopy(handleToParentMatrix.GetMatrix())

        transform_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
        transform_node.SetMatrixTransformToParent(transformToParentMatrix)
        
        for modelnode in modellist:
            if modelnode:
                modelnode.SetAndObserveTransformNodeID(transform_node.GetID())
                modelnode.HardenTransform()
        util.RemoveNode(transform_node)
        
        
        #将头架旋转到左右耳平面
        lp1 = np.array(util.get_world_control_point_by_name("frame_left")) - np.array(util.get_world_control_point_by_name("frame_right"))
        lp2 = self.get_target_vector()
                
        rotationVector_Local = np.array([0,0,0]).astype(np.float64)
        vtk.vtkMath.Cross(lp1, lp2, rotationVector_Local)
        angle2 = vtk.vtkMath.DegreesFromRadians(vtk.vtkMath.AngleBetweenVectors(lp1,lp2))
        transformToParentMatrix = vtk.vtkMatrix4x4()
        transformToParentMatrix.Identity()
        handleToParentMatrix=vtk.vtkTransform()
        handleToParentMatrix.PostMultiply()
        handleToParentMatrix.Concatenate(transformToParentMatrix)
        handleToParentMatrix.RotateWXYZ(angle2, rotationVector_Local)
        transformToParentMatrix.DeepCopy(handleToParentMatrix.GetMatrix())

        transform_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
        transform_node.SetMatrixTransformToParent(transformToParentMatrix)
        
        for modelnode in modellist:
            if modelnode:
                modelnode.SetAndObserveTransformNodeID(transform_node.GetID())
                modelnode.HardenTransform()
        util.RemoveNode(transform_node)
    
    def clear_info(self):
        util.getModuleWidget("sunHeadFrame").ui.textEdit.clear()
    
    def set_info(self,info):
        util.getModuleWidget("sunHeadFrame").ui.textEdit.append(info+"\n")
    
    def move_frame_to_targetpoint(self,modellist):
        blood_centernode = util.getFirstNodeByName("TargetPoint")
        kd = util.get_world_control_point_by_name("headframenode_center") - np.array(util.get_world_position(blood_centernode))
        transformToParentMatrix = vtk.vtkMatrix4x4()
        transformToParentMatrix.Identity()
        handleToParentMatrix=vtk.vtkTransform()
        handleToParentMatrix.PostMultiply()
        handleToParentMatrix.Concatenate(transformToParentMatrix)
        handleToParentMatrix.Translate(-kd[0], -kd[1], -kd[2])
        transformToParentMatrix.DeepCopy(handleToParentMatrix.GetMatrix())

        transform_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
        transform_node.SetMatrixTransformToParent(transformToParentMatrix)
        
        for modelnode in modellist:
            if modelnode:
                modelnode.SetAndObserveTransformNodeID(transform_node.GetID())
                modelnode.HardenTransform()
        util.RemoveNode(transform_node)
    
    #左右调整
    def rotate_to_fiber_y(self):
        rotationVector_Local = self.get_target_vector()
        center_centernode1 = util.get_world_control_point_by_name("headframenode_center")
        bp_centernode = util.get_world_control_point_by_name("TargetPoint")
        distance = self.distance_difference_along_vector(center_centernode1,bp_centernode,rotationVector_Local)
        util.getModuleWidget("sunHeadFrame").ui.slider2.setValue(distance)
        
    #前后调整
    def rotate_to_fiber_x(self):
        #旋转到导管的位置4
        p4w = util.get_world_control_point_by_name("EntryPoint")
        pg = [0,0,0]
        if self.ui.radioButton_2.isChecked():
            planenode = util.getFirstNodeByName("coronal_a")
            planenode.GetClosestPointOnPlaneWorld(p4w,pg)
        else:
            planenode = util.getFirstNodeByName("saggital_a")
            planenode.GetClosestPointOnPlaneWorld(p4w,pg)
        normal1 = planenode.GetNormal()
        if not self.reversed:
            planenode2 = self.create_plane_by_three_point([util.get_world_control_point_by_name("frame_left"),util.get_world_control_point_by_name("frame_right"),util.get_world_control_point_by_name("EntryPoint")],"abc")
        else:
            planenode2 = self.create_plane_by_three_point([util.get_world_control_point_by_name("frame_right"),util.get_world_control_point_by_name("frame_left"),util.get_world_control_point_by_name("EntryPoint")],"abc")
        normal12 = planenode2.GetNormal()
        angle2 = self.calculate_angle(normal1,normal12)
        util.getModuleWidget("sunHeadFrame").ui.slider0.setValue(angle2)
        val1 = self.get_distance("EntryPoint","toppoint_needle")
        util.getModuleWidget("sunHeadFrame").ui.slider0.setValue(-angle2)
        val2 = self.get_distance("EntryPoint","toppoint_needle")
        if val1 < val2:
            util.getModuleWidget("sunHeadFrame").ui.slider0.setValue(angle2)
        else:
            util.getModuleWidget("sunHeadFrame").ui.slider0.setValue(-angle2)
        util.RemoveNode(planenode2)
        tp1 = np.array(util.get_world_control_point_by_name("EntryPoint"))-np.array(util.get_world_control_point_by_name("TargetPoint"))
        tp2 = np.array(util.get_world_control_point_by_name("frame_up"))-np.array(util.get_world_control_point_by_name("headframenode_center"))
        angle3 = self.calculate_angle(tp1,tp2)
        if angle3 > 90:
            val1 = 180-angle2
            if val1 > 360:
                val1 = val1-360
            util.getModuleWidget("sunHeadFrame").ui.slider0.setValue(val1)
        
    def set_top_slider(self):
        tp1 = np.array(util.get_world_control_point_by_name("EntryPoint"))-np.array(util.get_world_control_point_by_name("headframenode_center"))
        tp2 = np.array(util.get_world_control_point_by_name("toppoint_needle"))-np.array(util.get_world_control_point_by_name("headframenode_center"))
        
        if self.ui.radioButton_2.isChecked():
            if util.get_world_control_point_by_name("EntryPoint")[0] - util.get_world_control_point_by_name("TargetPoint")[0] >0:
                degree = -self.calculate_angle(tp1,tp2)
            else:
                degree = self.calculate_angle(tp1,tp2)
        else:
            if util.get_world_control_point_by_name("EntryPoint")[1] - util.get_world_control_point_by_name("TargetPoint")[1] >0:
                degree = -self.calculate_angle(tp1,tp2)
            else:
                degree = self.calculate_angle(tp1,tp2)
        
        val1 = self.get_distance("EntryPoint","toppoint_needle")
        val2 = self.get_distance("EntryPoint","toppoint_needle")
        if val1 < val2:
            util.getModuleWidget("sunHeadFrame").ui.slider3.setValue(degree)
        else:
            util.getModuleWidget("sunHeadFrame").ui.slider3.setValue(-degree)
            
    
    def get_distance(self,nodename1,nodename2):
        p1 = util.get_world_control_point_by_name(nodename1)
        p2 = util.get_world_control_point_by_name(nodename2)
        distance = np.linalg.norm(np.array(p1)-np.array(p2))
        return distance
    
    def fine_tuning(self):
        f1 = np.array(util.get_world_control_point_by_name("EntryPoint")) - np.array(util.get_world_control_point_by_name("TargetPoint"))
        len1 = np.linalg.norm(f1)
        len2 = np.array(util.get_world_control_point_by_name("toppoint_needle")) - np.array(util.get_world_control_point_by_name("TargetPoint"))
        len2 = np.linalg.norm(len2)
        CorePoint = np.array(util.get_world_control_point_by_name("TargetPoint")) + f1/len1*len2
        CoreControlPoint = util.AddControlPointGlobal(CorePoint)
        front_back_direction = True
        rotate_direction = True
        front_back_value = 8
        rotate_value = 8
        
        
        old_distance = np.linalg.norm(np.array(util.get_world_control_point_by_name("toppoint_needle")) - CorePoint)
        for j in range(20):
            for i in range(5):
                if front_back_direction:
                    util.getModuleWidget("sunHeadFrame").set_front_back(front_back_value)
                else:
                    util.getModuleWidget("sunHeadFrame").set_front_back(-front_back_value)
                distance = np.linalg.norm(np.array(util.get_world_control_point_by_name("toppoint_needle")) - CorePoint)
                if distance > old_distance:
                    front_back_direction = not front_back_direction
                    front_back_value = front_back_value/2
                old_distance = distance
                if old_distance < 0.01:
                    util.RemoveNode(CoreControlPoint)
                    return
                util.processEvents()
            
            for i in range(5):
                if rotate_direction:
                    util.getModuleWidget("sunHeadFrame").set_rotate(rotate_value)
                else:
                    util.getModuleWidget("sunHeadFrame").set_rotate(-rotate_value)
                distance = np.linalg.norm(np.array(util.get_world_control_point_by_name("toppoint_needle")) - CorePoint)
                if distance > old_distance:
                    rotate_direction = not rotate_direction
                    rotate_value = rotate_value/2
                old_distance = distance
                if old_distance < 0.01:
                    util.RemoveNode(CoreControlPoint)
                    return
                util.processEvents()
        util.RemoveNode(CoreControlPoint)
    
    def move_three_plane_to_targetpoint(self):
        p1w = util.get_world_control_point_by_name("left_p")
        p2w = util.get_world_control_point_by_name("right_p")
        center = np.array(p1w)/2+np.array(p2w)/2
        blood_center_point = np.array(util.get_world_control_point_by_name("TargetPoint"))
        distance1 = blood_center_point - center
        transformToParentMatrix = vtk.vtkMatrix4x4()
        transformToParentMatrix.Identity()
        handleToParentMatrix=vtk.vtkTransform()
        handleToParentMatrix.PostMultiply()
        handleToParentMatrix.Concatenate(transformToParentMatrix)
        handleToParentMatrix.Translate(distance1[0], distance1[1], distance1[2])
        transformToParentMatrix.DeepCopy(handleToParentMatrix.GetMatrix())

        transform_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
        transform_node.SetMatrixTransformToParent(transformToParentMatrix)
        
        for modelnodenames in ["axial_a","coronal_a","saggital_a"]:
            modelnode = util.getFirstNodeByName(modelnodenames)
            if modelnode:
                modelnode.SetAndObserveTransformNodeID(transform_node.GetID())
                modelnode.HardenTransform()
        util.RemoveNode(transform_node)
    
    def get_info(self):
            self.clear_info()
            linenodes = self.get_lines()
            for node in linenodes:
                util.RemoveNode(node)
            if self.ui.radioButton_2.isChecked():
                nodes = util.getNodesByAttribute("is_ia_node","1")
                if  util.get_world_position(nodes[0])[0] - util.get_world_position(nodes[1])[0]<0:
                    left_ear1 = util.get_world_position(nodes[0])
                    right_ear1 = util.get_world_position(nodes[1])
                else:
                    left_ear1 = util.get_world_position(nodes[1])
                    right_ear1 = util.get_world_position(nodes[0])
                lp2 = np.array(left_ear1) - np.array(right_ear1)
                
                self.set_info("\n左边控制点")
                self.on_red_distance_any_point(left_ear1,"left_red")
                self.on_green_distance_any_point(left_ear1,"left_green",style=2)
                self.on_yellow_distance_any_point(left_ear1,"left_yellow")
                self.set_info("\n右边控制点")
                self.on_red_distance_any_point(right_ear1,"right_red")
                self.on_green_distance_any_point(right_ear1,"right_green",style=2)
                self.on_yellow_distance_any_point(right_ear1,"right_yellow")
            else:
                nodes = util.getNodesByAttribute("is_ap_node","1")
                if  util.get_world_position(nodes[0])[1] - util.get_world_position(nodes[1])[1]<0:
                    left_ear1 = util.get_world_position(nodes[0])
                    right_ear1 = util.get_world_position(nodes[1])
                else:
                    left_ear1 = util.get_world_position(nodes[1])
                    right_ear1 = util.get_world_position(nodes[0])
                lp2 = np.array(left_ear1) - np.array(right_ear1)
                
                self.set_info("\n后边控制点")
                self.on_red_distance_any_point(left_ear1,"front_red")
                self.on_green_distance_any_point(left_ear1,"front_green")
                self.on_yellow_distance_any_point(left_ear1,"front_yellow",style=2)
                self.set_info("\n前边控制点")
                self.on_red_distance_any_point(right_ear1,"back_red")
                self.on_green_distance_any_point(right_ear1,"back_green")
                self.on_yellow_distance_any_point(right_ear1,"back_yellow",style=2)
            return lp2
     
    def landing(self):
        seg1 = util.getFirstNodeByName("皮肤")
        max = 12
        for i in range(230):
            sliceViewWidget = slicer.app.layoutManager().sliceWidget('Red')
            left_center_needlenodepoint = util.get_world_control_point_by_name("frame_needle_left")
            segmentationsDisplayableManager = sliceViewWidget.sliceView().displayableManagerByClassName("vtkMRMLSegmentationsDisplayableManager2D")
            segmentIds1 = vtk.vtkStringArray()
            segmentationsDisplayableManager.GetVisibleSegmentsForPosition(left_center_needlenodepoint, seg1.GetDisplayNode(), segmentIds1)
            if segmentIds1.GetNumberOfValues()>0:
                break
            max -= 1
            util.getModuleWidget("sunHeadFrame").ui.slider7.setValue(max)
            if max < -150:
                break
            util.processEvents()

        
        if not self.reversed:
            max = 70
            for i in range(200):
                sliceViewWidget = slicer.app.layoutManager().sliceWidget('Red')
                right_center_needlenodepoint = util.get_world_control_point_by_name("frame_needle_right")
                segmentationsDisplayableManager = sliceViewWidget.sliceView().displayableManagerByClassName("vtkMRMLSegmentationsDisplayableManager2D")
                segmentIds1 = vtk.vtkStringArray()
                segmentationsDisplayableManager.GetVisibleSegmentsForPosition(right_center_needlenodepoint, seg1.GetDisplayNode(), segmentIds1)
                if segmentIds1.GetNumberOfValues()>0:
                    break
                max -= 1
                util.getModuleWidget("sunHeadFrame").ui.slider8.setValue(max)
                if max < -70:
                    break
                util.processEvents()   
        else:
            max = -70
            for i in range(200):
                sliceViewWidget = slicer.app.layoutManager().sliceWidget('Red')
                right_center_needlenodepoint = util.get_world_control_point_by_name("frame_needle_right")
                segmentationsDisplayableManager = sliceViewWidget.sliceView().displayableManagerByClassName("vtkMRMLSegmentationsDisplayableManager2D")
                segmentIds1 = vtk.vtkStringArray()
                segmentationsDisplayableManager.GetVisibleSegmentsForPosition(right_center_needlenodepoint, seg1.GetDisplayNode(), segmentIds1)
                if segmentIds1.GetNumberOfValues()>0:
                    break
                max += 1
                util.getModuleWidget("sunHeadFrame").ui.slider8.setValue(max)
                if max > 70:
                    break
                util.processEvents()     
    
    def check_reverse(self):
        self.reversed = False
        if self.ui.radioButton_2.isChecked():
            nodes = util.getNodesByAttribute("is_ia_node","1")
            if  util.get_world_position(nodes[0])[0] - util.get_world_position(nodes[1])[0]<0:
                left_ear1 = util.get_world_position(nodes[0])
                right_ear1 = util.get_world_position(nodes[1])
            else:
                left_ear1 = util.get_world_position(nodes[1])
                right_ear1 = util.get_world_position(nodes[0])
        
            target_point = util.get_world_control_point_by_name("TargetPoint")
            l1 = np.linalg.norm(np.array(target_point)-np.array(left_ear1))
            l2 = np.linalg.norm(np.array(target_point)-np.array(right_ear1))
            if l1 > l2:
                if not self.ui.checkBox.checked:
                    util.getModuleWidget("sunHeadFrame").on_reverse()
                    self.reversed = True
            else:
                if self.ui.checkBox.checked:
                    util.getModuleWidget("sunHeadFrame").on_reverse()
                    self.reversed = True
        else:
            nodes = util.getNodesByAttribute("is_ap_node","1")
            if  util.get_world_position(nodes[0])[1] - util.get_world_position(nodes[1])[1]<0:
                left_ear1 = util.get_world_position(nodes[0])
                right_ear1 = util.get_world_position(nodes[1])
            else:
                left_ear1 = util.get_world_position(nodes[1])
                right_ear1 = util.get_world_position(nodes[0])
                
            target_point = util.get_world_control_point_by_name("TargetPoint")
            l1 = np.linalg.norm(np.array(target_point)-np.array(left_ear1))
            l2 = np.linalg.norm(np.array(target_point)-np.array(right_ear1))
            if l1 > l2:
                if not self.ui.checkBox.checked:
                    util.getModuleWidget("sunHeadFrame").on_reverse()
                    self.reversed = True
            else:
                if self.ui.checkBox.checked:
                    util.getModuleWidget("sunHeadFrame").on_reverse()
                    self.reversed = True
    
    
    def test(self):
        def inner_test():
            TP = util.getFirstNodeByName("TargetPoint")
            EP = util.getFirstNodeByName("EntryPoint")
            map1 = util.global_data_map["stmap"]
            if len(map1[0])==1:
                util.global_data_map["stmap"] = util.global_data_map["stmap"][1:]
                map1 = util.global_data_map["stmap"]
            if len(map1) == 0:
                if self.ui.radioButton.isChecked():
                    self.ui.radioButton_2.setChecked(True)
                    util.on_camera_direction("A")
                    util.singleShot(3000,self.test)
                    return
                else:
                    return
            pn = map1[0].pop()
            tn = map1[0][0]
            TP.SetNthControlPointPositionWorld(0,tn)
            EP.SetNthControlPointPositionWorld(0,pn)
            util.getModuleWidget("UnitCreateChannel").fu.fresh_result()
            self.ui.pushButton_9.animateClick(0)
            self.ui.pushButton_2.animateClick(1000)
            import ScreenCapture
            cap = ScreenCapture.ScreenCaptureLogic()
            view = cap.viewFromNode(slicer.app.layoutManager().threeDWidget(0).mrmlViewNode())
            cap.captureImageFromView(view, f"D:/2/ssc/{len(map1[0])}_{len(map1)}_{self.ui.radioButton.isChecked()}.png")
            len2 = np.array(util.get_world_control_point_by_name("toppoint_needle")) - np.array(util.get_world_control_point_by_name("TargetPoint"))
            len1 = np.array(util.get_world_control_point_by_name("EntryPoint")) - np.array(util.get_world_control_point_by_name("TargetPoint"))
            angle = angle_between_vectors(len1,len2)
            print(f"angle_between_vectors: of TargetPoint {tn}  EntryPoint {pn} , angle is {angle}")
            
            util.singleShot(10,inner_test)
            
        def angle_between_vectors(v1, v2):
            # 计算向量的模
            v1_norm = np.linalg.norm(v1)
            v2_norm = np.linalg.norm(v2)
            
            # 计算向量的点积
            dot_product = np.dot(v1, v2)
            
            # 计算夹角的余弦值
            cos_angle = dot_product / (v1_norm * v2_norm)
            
            # 计算夹角（弧度制）
            angle = np.arccos(cos_angle)
            
            return angle
        # 获取布局管理器
        layoutManager = slicer.app.layoutManager()

        # 设置布局为单 3D 视图布局，以实现 3D 窗口最大化
        layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUp3DView)
        layoutManager = slicer.app.layoutManager()
        for threeDViewIndex in range(layoutManager.threeDViewCount) :
            view = layoutManager.threeDWidget(threeDViewIndex).threeDView()
            threeDViewNode = view.mrmlViewNode()
            cameraNode = slicer.modules.cameras.logic().GetViewActiveCameraNode(threeDViewNode)
            camera = cameraNode.GetCamera()
            #camera.Dolly(1.1)
            camera.Dolly(1.9)
            layoutManager.threeDWidget(threeDViewIndex).threeDView().forceRender()
        util.processEvents()
        controller = layoutManager.threeDWidget(0).threeDController()
        controller.resetFocalPoint()
        layoutManager.threeDWidget(0).threeDView().forceRender()
        map1 = []
        
        ecs = []
        t1 = [20,-30,30]
        ecs.append(t1)
        t1 = [20,60,30]
        ecs.append(t1)
        t1 = [-70,60,30]
        ecs.append(t1)
        t1 = [-70,-30,30]
        ecs.append(t1)
        t1 = [20,-30,-20]
        ecs.append(t1)
        t1 = [20,60,-20]
        ecs.append(t1)
        t1 = [-70,60,-20]
        ecs.append(t1)
        t1 = [-70,-30,-20]
        ecs.append(t1)
        
        for t1 in ecs:
            datas = []
            datas.append(t1)
            datas.append([t1[0]-90,t1[1]-90,t1[2]-90])
            datas.append([t1[0]-90,t1[1]-90,t1[2]+90])
            datas.append([t1[0]-90,t1[1]+90,t1[2]-90])
            datas.append([t1[0]-90,t1[1]+90,t1[2]+90])
            datas.append([t1[0]+90,t1[1]-90,t1[2]-90])
            datas.append([t1[0]+90,t1[1]-90,t1[2]+90])
            datas.append([t1[0]+90,t1[1]+90,t1[2]-90])
            datas.append([t1[0]+90,t1[1]+90,t1[2]+90])
            map1.append(datas)
            
                
        
        util.global_data_map["stmap"] = map1
        util.singleShot(0,inner_test)
        
        
        
    def load_head_frame(self):
        util.getModuleWidget("sunHeadFrame").reset()
        nodes = util.getNodesByAttribute("is_head_frame","1")
        for node in nodes:
            util.RemoveNode(node)
        modellist = self.load_frame_stl()
        util.set_button_percent(self.ui.pushButton_2,50)
        self.on_red_panel()
        util.set_button_percent(self.ui.pushButton_2,52)
        self.on_yellow_panel()
        util.set_button_percent(self.ui.pushButton_2,54)
        self.on_green_panel()
        util.set_button_percent(self.ui.pushButton_2,56)
        key_point_list,normal_frame = self.on_find_key_point()
        util.set_button_percent(self.ui.pushButton_2,58)
        extra_tp1list = [util.getFirstNodeByName("G22033 - G22024-014-2.STL"),util.getFirstNodeByName("G22033 - G22024-014-3.STL"),util.getFirstNodeByName("G22033 - G22033-005a-1"),util.getFirstNodeByName("G22033 - G22033-007a-1"),util.getFirstNodeByName("G22033 - G22033-0083a-1"),util.getFirstNodeByName("G22033 - G22036-003-1")]
        for i in range(len(extra_tp1list)):
            extra_tp1list[i].SetName(f"top_extra_{i}")
            extra_tp1list[i].SetAttribute("top_extra_widget","1")
            
        extra_tp1list = [util.getFirstNodeByName("G22033 - S1.STL"),util.getFirstNodeByName("G22033 - S2.STL"),util.getFirstNodeByName("G22033 - S3.STL"),util.getFirstNodeByName("G22033 - S4.STL"),util.getFirstNodeByName("G22033 - S5.STL"),util.getFirstNodeByName("G22033 - BZ-1 BZ1-1.STL"),util.getFirstNodeByName("G22033 - BZ-1 BZ2-2.STL"),util.getFirstNodeByName("G22033 - BZ-1 BZ3-2.STL"),util.getFirstNodeByName("G22033 - BZ-1 BZ4-1.STL"),util.getFirstNodeByName("G22033 - BZ-1 BZ5-1.STL")]
        for i in range(len(extra_tp1list)):
            if extra_tp1list[i]:
                extra_tp1list[i].SetName(f"fball_extra_{i}")
                extra_tp1list[i].SetAttribute("fball_extra_widget","1")
                util.HideNode(extra_tp1list[i])
                
        extra_tp1list = [util.getFirstNodeByName("right_stick_needle"),util.getFirstNodeByName("frame_needle_right"),util.getFirstNodeByName("right_stick_pipe"),util.getFirstNodeByName("G22033 - ZS92002-005-1.STL"),util.getFirstNodeByName("G22033 - G22033-022a-1.STL"),util.getFirstNodeByName("G22033 - G22033-01B-1.STL"),util.getFirstNodeByName("G22033 - G22033-018a-1.STL"),util.getFirstNodeByName("G22033 - G22033-011a-1.STL"),util.getFirstNodeByName("G22033 - G22033-002B-1.STL"),util.getFirstNodeByName("G22033 - G22024-014-1.STL"),util.getFirstNodeByName("G22033 - ZS92002-005-1.STL"),util.getFirstNodeByName("G22033 - G22033-021a-1.STL"),util.getFirstNodeByName("G22033 - G22033-015aD2-1.STL"),util.getFirstNodeByName("G22033 - G22036-005-1.STL"),util.getFirstNodeByName("va1"),util.getFirstNodeByName("va2"),util.getFirstNodeByName("va3"),util.getFirstNodeByName("va4"),util.getFirstNodeByName("G22033 _ G22033_028_3"),util.getFirstNodeByName("G22033 _ G22033_028_4"),util.getFirstNodeByName("G22033 - G22033-018a-1")]
        for i in range(len(extra_tp1list)):
            if extra_tp1list[i]:
                extra_tp1list[i].SetAttribute("right_pump_widget","1")
                
        extra_tp1list = [util.getFirstNodeByName("left_stick_needle"),util.getFirstNodeByName("kedu3"),util.getFirstNodeByName("kedu2"),util.getFirstNodeByName("frame_needle_left"),util.getFirstNodeByName("left_stick_pipe"),util.getFirstNodeByName("G22033 _ G22033-017a-1.STL"),util.getFirstNodeByName("G22033 - G22033-017axxx-1.STL")]
        for i in range(len(extra_tp1list)):
            if extra_tp1list[i]:
                extra_tp1list[i].SetAttribute("left_pump_widget","1")
                
             
        modellist += key_point_list
        util.set_button_percent(self.ui.pushButton_2,60)
        self.rotate_to_axial(modellist,normal_frame)
        util.set_button_percent(self.ui.pushButton_2,65)
        self.move_frame_to_targetpoint(modellist)
        util.set_button_percent(self.ui.pushButton_2,70)
        self.get_info()   
        util.set_button_percent(self.ui.pushButton_2,75)
        self.ui.w1.setChecked(True)
        self.ui.w3.setChecked(True)
        self.move_three_plane_to_targetpoint()
        util.set_button_percent(self.ui.pushButton_2,78)
        self.check_reverse()
        util.set_button_percent(self.ui.pushButton_2,80)
        self.rotate_to_fiber_x()
        util.set_button_percent(self.ui.pushButton_2,82)
        self.rotate_to_fiber_y()
        util.set_button_percent(self.ui.pushButton_2,85)
        self.set_top_slider()
        util.set_button_percent(self.ui.pushButton_2,87)
        self.fine_tuning()
        util.set_button_percent(self.ui.pushButton_2,90)
        self.landing()
        util.set_button_percent(self.ui.pushButton_2,99)
        self.draw_line()
        
        #self.statistics()
        util.getModuleWidget("sunHeadExport").show_kedu()
        util.set_button_percent(self.ui.pushButton_2,100)
    
    
    def load_head_frame2(self):
        util.getModuleWidget("sunHeadFrame").reset()
        nodes = util.getNodesByAttribute("is_head_frame","1")
        for node in nodes:
            util.RemoveNode(node)
        modellist = self.load_frame_stl()
        util.set_button_percent(self.ui.pushButton_2,50)
        self.on_red_panel()
        util.set_button_percent(self.ui.pushButton_2,52)
        self.on_yellow_panel()
        util.set_button_percent(self.ui.pushButton_2,54)
        self.on_green_panel()
        util.set_button_percent(self.ui.pushButton_2,56)
        key_point_list,normal_frame = self.on_find_key_point()
        util.set_button_percent(self.ui.pushButton_2,58)
        extra_tp1list = [util.getFirstNodeByName("G22033 _ 2MM_2"),util.getFirstNodeByName("G22033 _ G22024_014_7"),util.getFirstNodeByName("G22033 _ G22024_014_8"),util.getFirstNodeByName("G22033 _ G22024_014_9"),util.getFirstNodeByName("G22033 _ G22030_108_2"),util.getFirstNodeByName("G22033 _ G22033_005a_2"),util.getFirstNodeByName("G22033 _ G22033_006a_2"),util.getFirstNodeByName("G22033 _ G22033_006akd_2"),util.getFirstNodeByName("G22033 _ G22033_007a_2"),util.getFirstNodeByName("G22033 _ G22033_027a_2"),util.getFirstNodeByName("G22033 _ G22033_028_7"),util.getFirstNodeByName("G22033 _ G22033_028_8"),util.getFirstNodeByName("G22033 _ G22036_003_2")]
        for i in range(len(extra_tp1list)):
            if extra_tp1list[i]:
                extra_tp1list[i].SetName(f"top_extra_{i}")
                extra_tp1list[i].SetAttribute("top_extra_widget","1")
            
        extra_tp1list = [util.getFirstNodeByName("G22033 - S1.STL"),util.getFirstNodeByName("G22033 - S2.STL"),util.getFirstNodeByName("G22033 - S3.STL"),util.getFirstNodeByName("G22033 - S4.STL"),util.getFirstNodeByName("G22033 - S5.STL"),util.getFirstNodeByName("G22033 - BZ-1 BZ1-1.STL"),util.getFirstNodeByName("G22033 - BZ-1 BZ2-2.STL"),util.getFirstNodeByName("G22033 - BZ-1 BZ3-2.STL"),util.getFirstNodeByName("G22033 - BZ-1 BZ4-1.STL"),util.getFirstNodeByName("G22033 - BZ-1 BZ5-1.STL")]
        for i in range(len(extra_tp1list)):
            if extra_tp1list[i]:
                extra_tp1list[i].SetName(f"fball_extra_{i}")
                extra_tp1list[i].SetAttribute("fball_extra_widget","1")
                util.HideNode(extra_tp1list[i])
                
        extra_tp1list = [util.getFirstNodeByName("right_stick_needle"),util.getFirstNodeByName("frame_needle_right"),util.getFirstNodeByName("right_stick_pipe"),util.getFirstNodeByName("G22033 - ZS92002-005-1.STL"),util.getFirstNodeByName("G22033 - G22033-022a-1.STL"),util.getFirstNodeByName("G22033 - G22033-01B-1.STL"),util.getFirstNodeByName("G22033 - G22033-018a-1.STL"),util.getFirstNodeByName("G22033 - G22033-011a-1.STL"),util.getFirstNodeByName("G22033 - G22033-002B-1.STL"),util.getFirstNodeByName("G22033 - G22024-014-1.STL"),util.getFirstNodeByName("G22033 - ZS92002-005-1.STL"),util.getFirstNodeByName("G22033 - G22033-021a-1.STL"),util.getFirstNodeByName("G22033 - G22033-015aD2-1.STL"),util.getFirstNodeByName("G22033 - G22036-005-1.STL"),util.getFirstNodeByName("va1"),util.getFirstNodeByName("va2"),util.getFirstNodeByName("va3"),util.getFirstNodeByName("va4"),util.getFirstNodeByName("G22033 _ G22033_028_3"),util.getFirstNodeByName("G22033 _ G22033_028_4"),util.getFirstNodeByName("G22033 - G22033-018a-1")]
        for i in range(len(extra_tp1list)):
            if extra_tp1list[i]:
                extra_tp1list[i].SetAttribute("right_pump_widget","1")
                
        extra_tp1list = [util.getFirstNodeByName("left_stick_needle"),util.getFirstNodeByName("kedu3"),util.getFirstNodeByName("kedu2"),util.getFirstNodeByName("frame_needle_left"),util.getFirstNodeByName("left_stick_pipe"),util.getFirstNodeByName("G22033 _ G22033-017a-1.STL"),util.getFirstNodeByName("G22033 - G22033-017axxx-1.STL")]
        for i in range(len(extra_tp1list)):
            if extra_tp1list[i]:
                extra_tp1list[i].SetAttribute("left_pump_widget","1")
                
             
        modellist += key_point_list
        util.set_button_percent(self.ui.pushButton_2,60)
        self.rotate_to_axial(modellist,normal_frame)
        util.set_button_percent(self.ui.pushButton_2,65)
        self.move_frame_to_targetpoint(modellist)
        util.set_button_percent(self.ui.pushButton_2,70)
        self.get_info()   
        util.set_button_percent(self.ui.pushButton_2,75)
        self.ui.w1.setChecked(True)
        self.ui.w3.setChecked(True)
        self.move_three_plane_to_targetpoint()
        util.set_button_percent(self.ui.pushButton_2,78)
        self.check_reverse()
        util.set_button_percent(self.ui.pushButton_2,80)
        self.rotate_to_fiber_x()
        util.set_button_percent(self.ui.pushButton_2,82)
        self.rotate_to_fiber_y()
        util.set_button_percent(self.ui.pushButton_2,85)
        self.set_top_slider()
        util.set_button_percent(self.ui.pushButton_2,87)
        self.fine_tuning()
        util.set_button_percent(self.ui.pushButton_2,90)
        self.landing()
        util.set_button_percent(self.ui.pushButton_2,99)
        self.draw_line()
        
        #self.statistics()
        util.getModuleWidget("sunHeadExport").show_kedu()
        util.set_button_percent(self.ui.pushButton_2,100)
    
    def statistics(self):
        tw = util.getModuleWidget("sunHeadExport")
          
        
        
    def draw_line(self):
        util.RemoveNodeByName("testing_line")
        linenode = util.AddNewNodeByClass(util.vtkMRMLMarkupsLineNode)
        linenode.SetLineStartPositionWorld(util.get_world_control_point_by_name("frame_needle_left"))
        linenode.SetLineEndPositionWorld(util.get_world_control_point_by_name("frame_needle_right"))
        util.GetDisplayNode(linenode).SetPropertiesLabelVisibility(False)
        linenode.SetLocked(True)
        util.GetDisplayNode(linenode).SetSelectedColor(vtk.vtkVector3d(1,0,0))
        util.GetDisplayNode(linenode).SetSelectedColor(vtk.vtkVector3d(0,1,0))
        util.GetDisplayNode(linenode).SetLineThickness(0.5)
        linenode.SetName("testing_line")
            

    
    def land_point_on_model(self,point,model):
        nOfFiducialPoints = point.GetNumberOfFiducials()
        if nOfFiducialPoints!= 1:
            raise Exception("only support fiducai number of 1")

        logic = util.getModuleLogic("FiducialsToModelDistance")
        pointDistances, labels, closest_points1 = logic.pointDistancesLabelsFromSurface(point, model)
        point.SetNthControlPointPositionWorld(0,closest_points1[0])
    
    def distance_difference_along_vector(self,P, Q, v):
            """
            计算两个点 P 和 Q 在向量 v 方向上的距离差值。
            
            参数：
            P (array_like): 点 P 的坐标，例如 [Px, Py, Pz]
            Q (array_like): 点 Q 的坐标，例如 [Qx, Qy, Qz]
            v (array_like): 向量 v，例如 [vx, vy, vz]
            
            返回：
            float: 点 Q 相对于点 P 在向量 v 方向上的距离差值
            """
            P = np.array(P)
            Q = np.array(Q)
            v = np.array(v)
            
            # 计算向量 PQ
            PQ = Q - P
            
            # 计算向量 v 的范数
            norm_v = np.linalg.norm(v)
            if norm_v == 0:
                raise ValueError("向量 v 的长度不能为零。")
            
            # 计算单位向量 v_hat
            v_hat = v / norm_v
            
            # 计算距离差值
            d = np.dot(PQ, v_hat)
            
            return d

    
    def calculate_angle(self,u, v, in_degrees=True):
        """
        计算两个三维向量之间的夹角。
        
        参数：
        u (array_like): 第一个向量。
        v (array_like): 第二个向量。
        in_degrees (bool): 是否将结果转换为度。默认为 True。
        
        返回：
        float: 两个向量之间的夹角（默认以度为单位）。
        """
        u = np.array(u)
        v = np.array(v)
        
        # 计算点积
        dot_product = np.dot(u, v)
        
        # 计算范数
        norm_u = np.linalg.norm(u)
        norm_v = np.linalg.norm(v)
        
        if norm_u == 0 or norm_v == 0:
            raise ValueError("输入的向量不能为零向量。")
        
        # 计算余弦值并限制在 [-1, 1] 之间
        cos_theta = dot_product / (norm_u * norm_v)
        cos_theta = np.clip(cos_theta, -1.0, 1.0)
        
        # 计算夹角
        theta_rad = np.arccos(cos_theta)
        
        if in_degrees:
            return np.degrees(theta_rad)
        else:
            return theta_rad
    
    def on_find_key_point(self):
        modelNode = util.getFirstNodeByName("headframe_centerball")

        # 获取模型的所有点
        polyData = modelNode.GetPolyData()
        points = polyData.GetPoints()

        # 计算质心
        import numpy as np
        numPoints = points.GetNumberOfPoints()
        coords = np.array([points.GetPoint(i) for i in range(numPoints)])
        centroid = coords.mean(axis=0)
        cn = util.AddControlPointGlobal(centroid)
        cn.SetName("headframenode_center")
        
        left_center = np.array([-476.404,-41.647,280.657])
        left_center_needle = np.array([-166.198-67.945,276.509])
        left_center_piple = np.array([-442,-41.647,280.657])
        right_center = np.array([-196.425,-41.647,280.657])
        right_center_needle = np.array([-324.241,-67.945,276.509])
        right_center_piple = np.array([-258.000,-41.647,280.657])
        up_center = np.array([-336.414,-41.647,140.657])
        center_center = np.array([-336.414,-41.647,280.657])
        if self.ui.comboBox.currentIndex == 0:
            toppoint_needle = util.AddControlPointGlobal([-364.267,-154.560,3.180])
        else:
            toppoint_needle = util.AddControlPointGlobal([-534.311,65.136,103.958]) 
        toppointright_needle = util.AddControlPointGlobal([-220.000,-41.0900,164.681])
        top_right1 = util.AddControlPointGlobal([-130.000,-41.0900,164.681])
        top_right2 = util.AddControlPointGlobal([-260.000,-41.0900,164.681])
        
        up_centernode = util.AddControlPointGlobal(up_center)
        up_centernode.SetName("frame_up")
        center_centernode = util.getFirstNodeByName("headframenode_center")
        left_centernode = util.AddControlPointGlobal(left_center)
        left_centernode.SetName("frame_left")
        left_center_needlenode = util.AddControlPointGlobal(left_center_piple)
        left_center_needlenode.SetName("frame_needle_left")
        right_centernode = util.AddControlPointGlobal(right_center)
        right_centernode.SetName("frame_right")
        right_center_needlenode = util.AddControlPointGlobal(right_center_piple)
        right_center_needlenode.SetName("frame_needle_right")
        util.RemoveNodeByName("toppoint_needle")
        toppoint_needle.SetName("toppoint_needle")
        
        
        util.RemoveNodeByName("toppointright_needle")
        toppointright_needle.SetName("toppointright_needle")
        util.RemoveNodeByName("top_right1")
        top_right1.SetName("top_right1")
        util.RemoveNodeByName("top_right2")
        top_right2.SetName("top_right2")
        
        util.HideNode(center_centernode)
        util.HideNode(up_centernode)
        util.HideNode(left_centernode)
        util.HideNode(right_centernode)
        util.HideNode(toppoint_needle)
        util.HideNode(toppointright_needle)
        util.HideNode(left_center_needlenode)
        util.HideNode(right_center_needlenode)
        util.HideNode(top_right1)
        util.HideNode(top_right2)
        
        return [center_centernode,left_centernode,right_centernode,up_centernode,toppoint_needle,toppointright_needle,left_center_needlenode,right_center_needlenode,top_right1,top_right2],center_center-up_center
        
    def create_plane_by_three_point(self,pointlist,plane_name):
        import numpy as np
        if len(pointlist) < 3:
            print("至少需要3个点来创建平面")
            return
        planeNode = util.getFirstNodeByName(plane_name)
        if planeNode:
            util.RemoveNode(planeNode)
        planeNode = util.AddNewNodeByNameByClass(plane_name,"vtkMRMLMarkupsPlaneNode")
        util.GetDisplayNode(planeNode).SetNormalVisibility(False)
        util.GetDisplayNode(planeNode).SetPropertiesLabelVisibility(False)
        p1 = pointlist[0]
        p2 = pointlist[1]
        p3 = pointlist[2]
        origin = [0,0,0]
        for i in range(3):
            total = 0
            for j in range(len(pointlist)):
                total = total + pointlist[j][i]
            origin[i] = total/len(pointlist)
        
        axis1 = np.array(p1) -  np.array(p2)
        axis2 = np.array(p1) -  np.array(p3)
        normal = np.cross(axis1,axis2)
        # 使用三个标记点设置平面的位置和方向
        planeNode.SetOrigin(origin[0],origin[1],origin[2])
        planeNode.SetNormal(normal[0],normal[1],normal[2])
        planeNode.SetNthControlPointVisibility(0,False)
        planeNode.SetSizeWorld([self.get_panel_size(),self.get_panel_size()])
        util.GetDisplayNode(planeNode).SetHandlesInteractive(False)
        return planeNode
    
    def get_volume_center(self,volume_node):
        import numpy as np
        # 获取 volume 的配准矩阵
        ras_to_ijk_matrix = vtk.vtkMatrix4x4()
        volume_node.GetRASToIJKMatrix(ras_to_ijk_matrix)

        # 获取 volume 的尺寸
        dimensions = volume_node.GetImageData().GetDimensions()
        
        # 计算体素中心的 IJK 坐标
        center_ijk = np.array(dimensions) / 2.0

        # 将 IJK 坐标转换为 RAS 坐标
        ijk_to_ras_matrix = vtk.vtkMatrix4x4()
        volume_node.GetIJKToRASMatrix(ijk_to_ras_matrix)
        center_ras = np.array(ijk_to_ras_matrix.MultiplyPoint(np.append(center_ijk, 1.0)))[:3]

        return center_ras
    def on_volume_center(self):
        volume = util.getFirstNodeByClassByAttribute(util.vtkMRMLScalarVolumeNode,"main_node","1")
        center = self.get_volume_center(volume)
        return center
    
    def set_panel_node_center(self,panel):
        closestPosWorld = [0,0,0]
        panel.GetClosestPointOnPlaneWorld(self.on_volume_center(),closestPosWorld)
        panel.SetCenter(closestPosWorld)
    
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
    
    def check_three_point(self):
        p1 = util.getFirstNodeByName("left_p")
        p2 = util.getFirstNodeByName("right_p")
        p3 = util.getFirstNodeByName("nose")
        if p1 is not None and p2 is not None and p3 is not None:
            return True
        else:
            print("you need add three point ")
            return False
        

    def on_red_panel(self):
        if not self.check_three_point():
            return
        p1w = util.get_world_control_point_by_name("left_p")
        p2w = util.get_world_control_point_by_name("right_p")
        p3w = util.get_world_control_point_by_name("nose")
        center = np.array(p1w)/2+np.array(p2w)/2
        planenode = self.create_plane_by_three_point([p1w,p2w,p3w],"axial_a")
        planenode.SetCenterWorld(np.array(p1w)/2+np.array(p2w)/2)
        util.GetDisplayNode(planenode).SetSelectedColor(vtk.vtkVector3d(1,0,0))
        planenode.SetAxes(np.array(p1w)-np.array(p2w),np.array(p3w)-center,[0,0,1])
        
    def on_green_panel(self):
        if not self.check_three_point():
            return
        red_panel = util.getFirstNodeByName("axial_a")
        if not red_panel:
            print("not red panel")
            return
        util.RemoveNodeByName("saggital_a")
        normal = red_panel.GetNormal()
        p1w = util.get_world_control_point_by_name("left_p")
        p2w = util.get_world_control_point_by_name("right_p")
        p1w = [p1w[0]/2+p2w[0]/2,p1w[1]/2+p2w[1]/2,p1w[2]/2+p2w[2]/2]
        p2w = [p1w[0]+normal[0],p1w[1]+normal[1],p1w[2]+normal[2]]
        p3w = util.get_world_control_point_by_name("nose")
        
        center = red_panel.GetCenter()
        green_panel = util.clone(red_panel)
        green_panel.SetSizeWorld([self.get_panel_size(),self.get_panel_size()])
        green_panel.SetCenter(center)
        
        vec = np.array(p3w)-np.array(center)
        vec  = util.getFirstNodeByName("coronal_a").GetNormal()
        
        transformToParentMatrix = vtk.vtkMatrix4x4()
        transformToParentMatrix.Identity()
        handleToParentMatrix=vtk.vtkTransform()
        handleToParentMatrix.PostMultiply()
        handleToParentMatrix.Concatenate(transformToParentMatrix)
        handleToParentMatrix.Translate(-center[0], -center[1], -center[2])
        handleToParentMatrix.RotateWXYZ(-90, vec)
        handleToParentMatrix.Translate(center[0], center[1], center[2])
        transformToParentMatrix.DeepCopy(handleToParentMatrix.GetMatrix())
        transform_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
        transform_node.SetMatrixTransformToParent(transformToParentMatrix)
        green_panel.SetAndObserveTransformNodeID(transform_node.GetID())
        green_panel.HardenTransform()
        util.RemoveNode(transform_node)
        
        green_panel.SetName("saggital_a")
        util.GetDisplayNode(green_panel).SetSelectedColor(vtk.vtkVector3d(0,1,0))
    
    def on_yellow_panel(self):
        # if not self.check_three_point():
        #     return
        # p3w = util.get_world_control_point_by_name("nose")
        # plane_name = "coronal_a"
        # planeNode = util.getFirstNodeByName(plane_name)
        # if planeNode:
        #     util.RemoveNode(planeNode)
        # planeNode = util.AddNewNodeByNameByClass(plane_name,"vtkMRMLMarkupsPlaneNode")
        # util.GetDisplayNode(planeNode).SetNormalVisibility(False)
        # util.GetDisplayNode(planeNode).SetPropertiesLabelVisibility(False)
        # util.GetDisplayNode(planeNode).SetSelectedColor(vtk.vtkVector3d(1,1,0))
        # planeNode.SetCenter(p3w)
        # planeNode.SetNormal([1,0,0])
        # planeNode.SetSizeWorld([self.get_panel_size(),self.get_panel_size()])
        # util.GetDisplayNode(planeNode).SetHandlesInteractive(False)
        if not self.check_three_point():
            return
        red_panel = util.getFirstNodeByName("axial_a")
        if not red_panel:
            print("not red panel")
            return
        util.RemoveNodeByName("coronal_a")
        normal = red_panel.GetNormal()
        p1w = util.get_world_control_point_by_name("left_p")
        p2w = util.get_world_control_point_by_name("right_p")
        p3w = [p1w[0]+normal[0],p1w[1]+normal[1],p1w[2]+normal[2]]
        
        
        center = red_panel.GetCenter()
        yellow_panel = util.clone(red_panel)
        yellow_panel.SetSizeWorld([self.get_panel_size(),self.get_panel_size()])
        yellow_panel.SetCenter(center)
        
        vec = np.array(p1w)-np.array(p2w)
        transformToParentMatrix = vtk.vtkMatrix4x4()
        transformToParentMatrix.Identity()
        handleToParentMatrix=vtk.vtkTransform()
        handleToParentMatrix.PostMultiply()
        handleToParentMatrix.Concatenate(transformToParentMatrix)
        handleToParentMatrix.Translate(-center[0], -center[1], -center[2])
        handleToParentMatrix.RotateWXYZ(90, vec)
        handleToParentMatrix.Translate(center[0], center[1], center[2])
        transformToParentMatrix.DeepCopy(handleToParentMatrix.GetMatrix())
        transform_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
        transform_node.SetMatrixTransformToParent(transformToParentMatrix)
        yellow_panel.SetAndObserveTransformNodeID(transform_node.GetID())
        yellow_panel.HardenTransform()
        util.RemoveNode(transform_node)
        
        yellow_panel.SetName("coronal_a")
        util.GetDisplayNode(yellow_panel).SetSelectedColor(vtk.vtkVector3d(1,1,0))
    
    def on_red_distance(self):
        p4w = util.get_world_control_point_by_name("TargetPoint")
        planenode = util.getFirstNodeByName("axial_a")
        pg = [0,0,0]
        planenode.GetClosestPointOnPlaneWorld(p4w,pg)
        linenode = util.getFirstNodeByClassByAttribute(util.vtkMRMLMarkupsLineNode,"line_style","red_line")
        if linenode:
            util.RemoveNode(linenode)
        linenode = util.AddNewNodeByClass(util.vtkMRMLMarkupsLineNode)
        linenode.SetLineStartPositionWorld(p4w)
        linenode.SetLineEndPositionWorld(pg)
        util.GetDisplayNode(linenode).SetPropertiesLabelVisibility(True)
        linenode.SetAttribute("line_style","red_line")
        normal = [0,0,1]
        tline = np.array(p4w) - np.array(pg)
        if self.is_same_direction(normal,tline):
            linenode.SetName("H")
        else:
            linenode.SetName("D")
        linenode.SetLocked(True)
        util.GetDisplayNode(linenode).SetSelectedColor(vtk.vtkVector3d(1,0,0))
        self.set_info("红色平面 "+linenode.GetName()+" "+str(format(linenode.GetMeasurement('length').GetValue(),".2f")))
        
    def on_red_distance_entry(self):
        p4w = util.get_world_control_point_by_name("EntryPoint")
        if not p4w:
            return
        planenode = util.getFirstNodeByName("axial_a")
        pg = [0,0,0]
        planenode.GetClosestPointOnPlaneWorld(p4w,pg)
        linenode = util.getFirstNodeByClassByAttribute(util.vtkMRMLMarkupsLineNode,"line_style","red_entry_line")
        if linenode:
            util.RemoveNode(linenode)
        linenode = util.AddNewNodeByClass(util.vtkMRMLMarkupsLineNode)
        linenode.SetLineStartPositionWorld(p4w)
        linenode.SetLineEndPositionWorld(pg)
        util.GetDisplayNode(linenode).SetPropertiesLabelVisibility(True)
        linenode.SetAttribute("line_style","red_entry_line")
        normal = [0,0,1]
        tline = np.array(p4w) - np.array(pg)
        if self.is_same_direction(normal,tline):
            linenode.SetName("H")
        else:
            linenode.SetName("D")
        linenode.SetLocked(True)
        util.GetDisplayNode(linenode).SetSelectedColor(vtk.vtkVector3d(1,0,0))
        self.set_info("红色平面 "+linenode.GetName()+" "+str(format(linenode.GetMeasurement('length').GetValue(),".2f")))
        
    
    def on_red_distance_any_point(self,p4w,red_line_name,style=1):
        planenode = util.getFirstNodeByName("axial_a")
        pg = [0,0,0]
        planenode.GetClosestPointOnPlaneWorld(p4w,pg)
        if style==2:
            pg = util.get_world_control_point_by_name("TargetPoint")
        if  np.linalg.norm(np.array(p4w) - np.array(pg)) < 0.01:
            return
        linenode = util.getFirstNodeByClassByAttribute(util.vtkMRMLMarkupsLineNode,"line_style",red_line_name)
        if linenode:
            util.RemoveNode(linenode)
        linenode = util.AddNewNodeByClass(util.vtkMRMLMarkupsLineNode)
        linenode.SetLineStartPositionWorld(p4w)
        linenode.SetLineEndPositionWorld(pg)
        util.GetDisplayNode(linenode).SetPropertiesLabelVisibility(True)
        linenode.SetAttribute("line_style",red_line_name)
        normal = [0,0,1]
        tline = np.array(p4w) - np.array(pg)
        if style == 1 or style == 2:
            if self.is_same_direction(normal,tline):
                linenode.SetName("H")
            else:
                linenode.SetName("D")
            linenode.SetLocked(True)
            util.GetDisplayNode(linenode).SetSelectedColor(vtk.vtkVector3d(1,0,0))
            self.set_info("红色平面 "+linenode.GetName()+" "+str(format(linenode.GetMeasurement('length').GetValue(),".2f")))
        if style == 3:
            prefix = "H："
            if self.is_same_direction(normal,tline):
                prefix = "H："
            else:
                prefix = "D："
            util.RemoveNode(linenode)
            str1 = "红色平面 "+prefix+str(format(linenode.GetMeasurement('length').GetValue(),".2f"))
            return str1
            
    def on_green_distance_any_point(self,p4w,green_line_name,style=1):
        planenode = util.getFirstNodeByName("saggital_a")
        pg = [0,0,0]
        planenode.GetClosestPointOnPlaneWorld(p4w,pg)
        if style==2:
            pg = util.get_world_control_point_by_name("TargetPoint")
        if  np.linalg.norm(np.array(p4w) - np.array(pg)) < 0.01:
            return
        
        linenode = util.getFirstNodeByClassByAttribute(util.vtkMRMLMarkupsLineNode,"line_style",green_line_name)
        if linenode:
            util.RemoveNode(linenode)
        linenode = util.AddNewNodeByClass(util.vtkMRMLMarkupsLineNode)
        linenode.SetLineStartPositionWorld(p4w)
        linenode.SetLineEndPositionWorld(pg)
        util.GetDisplayNode(linenode).SetPropertiesLabelVisibility(True)
        linenode.SetAttribute("line_style",green_line_name)
        normal = [1,0,0]
        tline = np.array(p4w) - np.array(pg)
        if style == 1 or style == 2:
            if self.is_same_direction(normal,tline):
                linenode.SetName("R")
            else:
                linenode.SetName("L")
            linenode.SetLocked(True)
            util.GetDisplayNode(linenode).SetSelectedColor(vtk.vtkVector3d(1,0,0))
            util.GetDisplayNode(linenode).SetSelectedColor(vtk.vtkVector3d(0,1,0))
            self.set_info("绿色平面 "+linenode.GetName()+" "+str(format(linenode.GetMeasurement('length').GetValue(),".2f")))  
        if style == 3:
            prefix = "L："
            if self.is_same_direction(normal,tline):
                prefix = "R："
            else:
                prefix = "L："
            util.RemoveNode(linenode)
            str1 = "绿色平面 "+prefix+str(format(linenode.GetMeasurement('length').GetValue(),".2f"))
            return str1
              
    def on_yellow_distance_any_point(self,p4w,yellow_line_name,style=1):
        planenode = util.getFirstNodeByName("coronal_a")
        pg = [0,0,0]
        planenode.GetClosestPointOnPlaneWorld(p4w,pg)
        if style==2:
            pg = util.get_world_control_point_by_name("TargetPoint")
        if  np.linalg.norm(np.array(p4w) - np.array(pg)) < 0.01:
            return
        linenode = util.getFirstNodeByClassByAttribute(util.vtkMRMLMarkupsLineNode,"line_style",yellow_line_name)
        if linenode:
            util.RemoveNode(linenode)
        linenode = util.AddNewNodeByClass(util.vtkMRMLMarkupsLineNode)
        linenode.SetLineStartPositionWorld(p4w)
        linenode.SetLineEndPositionWorld(pg)
        linenode.SetAttribute("line_style",yellow_line_name)
        util.GetDisplayNode(linenode).SetPropertiesLabelVisibility(True)
        normal = [0,1,0]
        tline = np.array(p4w) - np.array(pg)
        
        if style == 1 or style == 2:
            if self.is_same_direction(normal,tline):
                linenode.SetName("A")
            else:
                linenode.SetName("P")
            linenode.SetLocked(True)
            util.GetDisplayNode(linenode).SetSelectedColor(vtk.vtkVector3d(1,1,0))
            self.set_info("黄色平面 "+linenode.GetName()+" "+str(format(linenode.GetMeasurement('length').GetValue(),".2f")))
        if style == 3:
            prefix = "A："
            if self.is_same_direction(normal,tline):
                prefix = "A："
            else:
                prefix = "P："
            util.RemoveNode(linenode)
            str1 = "黄色平面 "+prefix+str(format(linenode.GetMeasurement('length').GetValue(),".2f"))
            return str1
        
    
    def is_same_direction(self,a, b, tol=1e-7):
        # 将输入向量转换为numpy数组
        a = np.array(a, dtype=float)
        b = np.array(b, dtype=float)
        
        # 检查零向量
        if np.allclose(a, 0, atol=tol) or np.allclose(b, 0, atol=tol):
            raise ValueError("其中至少有一个向量为零向量，无法定义方向一致性。")
        
        # 归一化两个向量
        a_norm = a / np.linalg.norm(a)
        b_norm = b / np.linalg.norm(b)
        
        # 计算点积
        dot_product = np.dot(a_norm, b_norm)
        
        # dot_product 接近1说明方向基本一致
        # 可以根据实际需要设置一个阈值，比如判断dot_product > 0.9999来认为方向一致
        return dot_product > 0

    def on_green_distance(self):
        p4w = util.get_world_control_point_by_name("TargetPoint")
        planenode = util.getFirstNodeByName("saggital_a")
        pg = [0,0,0]
        planenode.GetClosestPointOnPlaneWorld(p4w,pg)
        linenode = util.getFirstNodeByClassByAttribute(util.vtkMRMLMarkupsLineNode,"line_style","green_line")
        if linenode:
            util.RemoveNode(linenode)
        linenode = util.AddNewNodeByClass(util.vtkMRMLMarkupsLineNode)
        linenode.SetLineStartPositionWorld(p4w)
        linenode.SetLineEndPositionWorld(pg)
        util.GetDisplayNode(linenode).SetPropertiesLabelVisibility(True)
        linenode.SetAttribute("line_style","green_line")
        normal = [1,0,0]
        tline = np.array(p4w) - np.array(pg)
        if self.is_same_direction(normal,tline):
            linenode.SetName("R")
        else:
            linenode.SetName("L")
        linenode.SetLocked(True)
        util.GetDisplayNode(linenode).SetSelectedColor(vtk.vtkVector3d(1,0,0))
        util.GetDisplayNode(linenode).SetSelectedColor(vtk.vtkVector3d(0,1,0))
        self.set_info("绿色平面 "+linenode.GetName()+" "+str(format(linenode.GetMeasurement('length').GetValue(),".2f")))
        
    def on_green_distance_entry(self):
        p4w = util.get_world_control_point_by_name("EntryPoint")
        if not p4w:
            return
        planenode = util.getFirstNodeByName("saggital_a")
        pg = [0,0,0]
        planenode.GetClosestPointOnPlaneWorld(p4w,pg)
        linenode = util.getFirstNodeByClassByAttribute(util.vtkMRMLMarkupsLineNode,"line_style","green_entry_line")
        if linenode:
            util.RemoveNode(linenode)
        linenode = util.AddNewNodeByClass(util.vtkMRMLMarkupsLineNode)
        linenode.SetLineStartPositionWorld(p4w)
        linenode.SetLineEndPositionWorld(pg)
        util.GetDisplayNode(linenode).SetPropertiesLabelVisibility(True)
        linenode.SetAttribute("line_style","green_entry_line")
        normal = [1,0,0]
        tline = np.array(p4w) - np.array(pg)
        if self.is_same_direction(normal,tline):
            linenode.SetName("R")
        else:
            linenode.SetName("L")
        linenode.SetLocked(True)
        util.GetDisplayNode(linenode).SetSelectedColor(vtk.vtkVector3d(1,0,0))
        util.GetDisplayNode(linenode).SetSelectedColor(vtk.vtkVector3d(0,1,0))
        self.set_info("绿色平面 "+linenode.GetName()+" "+str(format(linenode.GetMeasurement('length').GetValue(),".2f")))
    
    def on_yellow_distancce(self):
        p4w = util.get_world_control_point_by_name("TargetPoint")
        planenode = util.getFirstNodeByName("coronal_a")
        pg = [0,0,0]
        planenode.GetClosestPointOnPlaneWorld(p4w,pg)
        linenode = util.getFirstNodeByClassByAttribute(util.vtkMRMLMarkupsLineNode,"line_style","yellow_line")
        if linenode:
            util.RemoveNode(linenode)
        linenode = util.AddNewNodeByClass(util.vtkMRMLMarkupsLineNode)
        linenode.SetLineStartPositionWorld(p4w)
        linenode.SetLineEndPositionWorld(pg)
        linenode.SetAttribute("line_style","yellow_line")
        util.GetDisplayNode(linenode).SetPropertiesLabelVisibility(True)
        normal = [0,1,0]
        tline = np.array(p4w) - np.array(pg)
        if self.is_same_direction(normal,tline):
            linenode.SetName("A")
        else:
            linenode.SetName("P")
        linenode.SetLocked(True)
        util.GetDisplayNode(linenode).SetSelectedColor(vtk.vtkVector3d(1,1,0))
        self.set_info("红色平面 "+linenode.GetName()+" "+str(format(linenode.GetMeasurement('length').GetValue(),".2f")))
        
    def on_yellow_distancce_entry(self):
        p4w = util.get_world_control_point_by_name("EntryPoint")
        if not p4w:
            return
        planenode = util.getFirstNodeByName("coronal_a")
        pg = [0,0,0]
        planenode.GetClosestPointOnPlaneWorld(p4w,pg)
        linenode = util.getFirstNodeByClassByAttribute(util.vtkMRMLMarkupsLineNode,"line_style","yellow_entry_line")
        if linenode:
            util.RemoveNode(linenode)
        linenode = util.AddNewNodeByClass(util.vtkMRMLMarkupsLineNode)
        linenode.SetLineStartPositionWorld(p4w)
        linenode.SetLineEndPositionWorld(pg)
        linenode.SetAttribute("line_style","yellow_entry_line")
        util.GetDisplayNode(linenode).SetPropertiesLabelVisibility(True)
        normal = [0,1,0]
        tline = np.array(p4w) - np.array(pg)
        if self.is_same_direction(normal,tline):
            linenode.SetName("A")
        else:
            linenode.SetName("P")
        linenode.SetLocked(True)
        util.GetDisplayNode(linenode).SetSelectedColor(vtk.vtkVector3d(1,1,0))
        self.set_info("黄色平面 "+linenode.GetName()+" "+str(format(linenode.GetMeasurement('length').GetValue(),".2f")))
    
    def on_tmp_markups(self):
        planenode = util.getFirstNodeByName("axial_a")
        normal = planenode.GetNormal()
        
        p3w = util.get_world_control_point_by_name("TargetPoint")
        
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
        util.set_button_percent(self.ui.pushButton_9,35)
        
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
        util.set_button_percent(self.ui.pushButton_9,40)
        
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
        

    def on_interaction_points(self):
        import numpy as np
        import random
        planeNode1 = util.getFirstNodeByName("axial_tmp")
        skin = util.getFirstNodeByName("皮肤")
        planeNode3 = util.getFirstNodeByName("coronal_tmp")
        linenode = self.calculate_intersection_line(planeNode1, planeNode3)
        list1 = self.calculate_segmentation_line_intersections(skin, linenode)
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
        p4w = util.get_world_control_point_by_name("TargetPoint")
        distance1 = {0: -1, 1: -1}
        pointlist = {0: None, 1: None}
        
        for i, point in enumerate(list1):
            distance = np.linalg.norm(np.array(point) - np.array(p4w))
            if distance > distance1[labels[i]]:
                distance1[labels[i]] = distance
                pointlist[labels[i]] = point

        AINodes = []
        # 创建或更新标记线
        for i, label_name in enumerate(["ls1", "ls2"]):
            linenode = util.getFirstNodeByName(label_name)
            if linenode:
                util.RemoveNode(linenode)
            linenode = util.AddNewNodeByClass(util.vtkMRMLMarkupsLineNode)
            linenode.SetLineStartPositionWorld(p4w)
            linenode.SetLineEndPositionWorld(pointlist[i])
            AINodes.append(pointlist[i])
            linenode.SetName(label_name)
            util.HideNode(linenode)
            util.GetDisplayNode(linenode).SetSelectedColor(vtk.vtkVector3d(0, 0, 0))
        oldnodes = util.getNodesByAttribute("is_ia_node","1")
        for node in oldnodes:
            util.RemoveNode(node)
        for nodeworld in AINodes:
            node = util.AddControlPointGlobal(nodeworld)
            node.SetAttribute("is_ia_node","1")
            util.HideNode(node)
            
            
            
            
        
        
        
        
        planeNode4 = util.getFirstNodeByName("saggital_tmp")
        linenode = self.calculate_intersection_line(planeNode1, planeNode4)
        list1 = self.calculate_segmentation_line_intersections(skin, linenode)
        util.RemoveNode(linenode)
        util.RemoveNodeByName("is_points")
        
        # 定义KMeans的参数
        n_clusters = 2
        max_iters = 100
        tol = 1e-4
        
        # 随机初始化两个聚类中心
        centroids = np.array(random.sample(list1, n_clusters))
        labels = np.zeros(len(list1), dtype=int)
        util.set_button_percent(self.ui.pushButton_9,50)
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
        p4w = util.get_world_control_point_by_name("TargetPoint")
        distance1 = {0: -1, 1: -1}
        pointlist = {0: None, 1: None}
        
        for i, point in enumerate(list1):
            distance = np.linalg.norm(np.array(point) - np.array(p4w))
            if distance > distance1[labels[i]]:
                distance1[labels[i]] = distance
                pointlist[labels[i]] = point 
        AINodes = []
        # 创建或更新标记线
        for i, label_name in enumerate(["bs1", "bs2"]):
            linenode = util.getFirstNodeByName(label_name)
            if linenode:
                util.RemoveNode(linenode)
            linenode = util.AddNewNodeByClass(util.vtkMRMLMarkupsLineNode)
            linenode.SetLineStartPositionWorld(p4w)
            linenode.SetLineEndPositionWorld(pointlist[i])
            AINodes.append(pointlist[i])
            linenode.SetName(label_name)
            util.HideNode(linenode)
            util.GetDisplayNode(linenode).SetSelectedColor(vtk.vtkVector3d(0, 0, 0))
        oldnodes = util.getNodesByAttribute("is_ap_node","1")
        for node in oldnodes:
            util.RemoveNode(node)
        for nodeworld in AINodes:
            node = util.AddControlPointGlobal(nodeworld)
            node.SetAttribute("is_ap_node","1")
            util.HideNode(node)
        util.RemoveNodeByName("coronal_tmp")
        util.RemoveNodeByName("axial_tmp")
        util.RemoveNodeByName("saggital_tmp")
    

    def calculate_segmentation_line_intersections(self,segmentationNode, lineNode):
        # 将整个分割导出为PolyData（闭合表面表示）
        polyData = segmentationNode.GetClosedSurfaceInternalRepresentation("皮肤")

        # 获取直线的两个端点
        startPoint = [0.0, 0.0, 0.0]
        endPoint = [0.0, 0.0, 0.0]
        lineNode.GetNthControlPointPositionWorld(0, startPoint)
        lineNode.GetNthControlPointPositionWorld(1, endPoint)

        # 使用 vtkOBBTree 计算交点
        obbTree = vtk.vtkOBBTree()
        obbTree.SetDataSet(polyData)
        obbTree.BuildLocator()

        # 查找直线和模型的所有交点
        points = vtk.vtkPoints()
        obbTree.IntersectWithLine(startPoint, endPoint, points, None)

        # 提取交点坐标
        intersections = []
        for i in range(points.GetNumberOfPoints()):
            point = [0.0, 0.0, 0.0]
            points.GetPoint(i, point)
            intersections.append(point)

        return intersections

    def calculate_intersection_line(self,planeNode1, planeNode2):
        import numpy as np
        # 获取第一个平面的原点和法向量
        origin1 = [0.0, 0.0, 0.0]
        normal1 = [0.0, 0.0, 0.0]
        planeNode1.GetOriginWorld(origin1)
        planeNode1.GetNormalWorld(normal1)

        # 获取第二个平面的原点和法向量
        origin2 = [0.0, 0.0, 0.0]
        normal2 = [0.0, 0.0, 0.0]
        planeNode2.GetOriginWorld(origin2)
        planeNode2.GetNormalWorld(normal2)

        # 将法向量转换为 numpy 数组以便计算
        normal1 = np.array(normal1)
        normal2 = np.array(normal2)

        # 计算交线的方向：交线方向是两个法向量的叉积
        line_direction = np.cross(normal1, normal2)

        # 检查两个平面是否平行（叉积为零向量意味着法向量平行）
        if np.allclose(line_direction, [0.0, 0.0, 0.0]):
            print("两个平面平行或重合，没有唯一交线")
            return None  # 返回 None 表示无交线

        # 规范化交线方向向量
        line_direction = line_direction / np.linalg.norm(line_direction)

        # 计算交线上的一点：找到平面1上的一个点和交线方向的向量组合
        # 方法：通过设置平面方程组来求解一个满足两个平面方程的点
        A = np.array([normal1, normal2, line_direction])
        b = np.array([np.dot(normal1, origin1), np.dot(normal2, origin2), 0.0])

        try:
            # 求解线性方程组来找到交线上的一个点
            point_on_line = np.linalg.solve(A, b)
            util.RemoveNodeByName("tmp_line")
            linenode = util.AddNewNodeByClass(util.vtkMRMLMarkupsLineNode)
            linenode.SetLineStartPositionWorld([point_on_line[0]-line_direction[0]*500,point_on_line[1]-line_direction[1]*500,point_on_line[2]-line_direction[2]*500])
            linenode.SetLineEndPositionWorld([point_on_line[0]+line_direction[0]*500,point_on_line[1]+line_direction[1]*500,point_on_line[2]+line_direction[2]*500])
            linenode.SetName("tmp_line")
            util.GetDisplayNode(linenode).SetSelectedColor(vtk.vtkVector3d(1,1,1))
            return linenode
        except np.linalg.LinAlgError:
            print("无法找到交线上的点")
            return None  # 返回 None 表示无交线
    
    def enter(self):
        pass

   