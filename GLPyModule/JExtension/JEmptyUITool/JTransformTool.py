import imp
import os
from re import A
from tabnanny import check
from time import sleep
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import slicer.util as util
import SlicerWizard.Utilities as su 
import numpy as np
#
# JTransformTool
#

class JTransformTool(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "JTransformTool"  # TODO: make this more human readable by adding spaces
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
# JTransformToolWidget
#

class JTransformToolWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  def __init__(self, parent=None):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)  # needed for parameter node observation
    self.logic = None

  def setup(self):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.setup(self)

    self.logic = JTransformToolLogic()

    


  def enter(self):
    pass

  def exit(self):
    pass

 

class JTransformToolLogic(ScriptedLoadableModuleLogic):
  def __init__(self):
    """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
    ScriptedLoadableModuleLogic.__init__(self)
  
  '''
    摄像机在3D视图中聚焦一个点,围绕一个轴旋转一个角度
  '''
  def rotate_camera(self,camera_node,val,focus_point,cemera_vector_normalized):
    transform_node = util.AddNewNodeByNameByClass("vtkMRMLLinearTransformNode")
    camera_node.SetAndObserveTransformNodeID(transform_node.GetID())

    modelToParentTransform = vtk.vtkMatrix4x4()
    handleToWorldMatrix = vtk.vtkTransform()
    handleToWorldMatrix.PostMultiply()
    handleToWorldMatrix.Translate(-focus_point[0], -focus_point[1], -focus_point[2])
    handleToWorldMatrix.RotateWXYZ(val,cemera_vector_normalized)
    handleToWorldMatrix.Translate(focus_point)
    modelToParentTransform.DeepCopy(handleToWorldMatrix.GetMatrix())

    transform_node.SetMatrixTransformToParent(modelToParentTransform)


  def rotate_stl_model_to_vector_full(self,model_node,m_PointInput,m_PointTarget,length):
    length = length
    half_vector = (np.array(m_PointInput) - np.array(m_PointTarget))
    half_vector_len = np.sqrt(half_vector[0]*half_vector[0]+half_vector[1]*half_vector[1]+half_vector[2]*half_vector[2]).astype(np.float64)

    transformToParentMatrix = vtk.vtkMatrix4x4()
    transformToParentMatrix.Identity()
    transformToParentMatrix.SetElement(0, 3, m_PointTarget[0])
    transformToParentMatrix.SetElement(1, 3, m_PointTarget[1])
    transformToParentMatrix.SetElement(2, 3, m_PointTarget[2])

    rotationVector_Local = np.array([0,0,0]).astype(np.float64)
    vector1 = np.array(m_PointInput).astype(np.float64) - np.array(m_PointTarget).astype(np.float64)
    vector0 = np.array([0,0,1]).astype(np.float64)

    angle = vtk.vtkMath.DegreesFromRadians(vtk.vtkMath.AngleBetweenVectors(vector0,vector1))
    vtk.vtkMath.Cross(vector0, vector1, rotationVector_Local)
    handleToParentMatrix=vtk.vtkTransform()
    handleToParentMatrix.PostMultiply()
    handleToParentMatrix.Concatenate(transformToParentMatrix)
    handleToParentMatrix.Translate(-m_PointTarget[0], -m_PointTarget[1], -m_PointTarget[2])
    handleToParentMatrix.RotateWXYZ(angle, rotationVector_Local)
    handleToParentMatrix.Translate(m_PointTarget[0]+half_vector[0]*length/half_vector_len,m_PointTarget[1]+half_vector[1]*length/half_vector_len,m_PointTarget[2]+half_vector[2]*length/half_vector_len)
    transformToParentMatrix.DeepCopy(handleToParentMatrix.GetMatrix())

    transform_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
    transform_node.SetMatrixTransformToParent(transformToParentMatrix)
    model_node.SetAndObserveTransformNodeID(transform_node.GetID())

  '''
    将一个0,0,0点在模型z轴中心点的模型z轴移动到指定的vector位置,模型的z轴长度为length
    @model_node     模型节点
    @m_PointInput   入点
    @m_PointTarget  靶点
    @length         模型长度
  '''
  def rotate_stl_model_to_vector(self,model_node,m_PointInput,m_PointTarget,length):
    
    length = length/2
    half_vector = (np.array(m_PointInput) - np.array(m_PointTarget))/2
    half_vector_len = np.sqrt(half_vector[0]*half_vector[0]+half_vector[1]*half_vector[1]+half_vector[2]*half_vector[2]).astype(np.float64)

    transformToParentMatrix = vtk.vtkMatrix4x4()
    transformToParentMatrix.Identity()
    transformToParentMatrix.SetElement(0, 3, m_PointTarget[0])
    transformToParentMatrix.SetElement(1, 3, m_PointTarget[1])
    transformToParentMatrix.SetElement(2, 3, m_PointTarget[2])

    rotationVector_Local = np.array([0,0,0]).astype(np.float64)
    vector1 = np.array(m_PointInput).astype(np.float64) - np.array(m_PointTarget).astype(np.float64)
    vector0 = np.array([0,0,1]).astype(np.float64)

    angle = vtk.vtkMath.DegreesFromRadians(vtk.vtkMath.AngleBetweenVectors(vector0,vector1))
    vtk.vtkMath.Cross(vector0, vector1, rotationVector_Local)
    handleToParentMatrix=vtk.vtkTransform()
    handleToParentMatrix.PostMultiply()
    handleToParentMatrix.Concatenate(transformToParentMatrix)
    handleToParentMatrix.Translate(-m_PointTarget[0], -m_PointTarget[1], -m_PointTarget[2])
    handleToParentMatrix.RotateWXYZ(angle, rotationVector_Local)
    handleToParentMatrix.Translate(m_PointTarget[0]+half_vector[0]*length/half_vector_len,m_PointTarget[1]+half_vector[1]*length/half_vector_len,m_PointTarget[2]+half_vector[2]*length/half_vector_len)
    transformToParentMatrix.DeepCopy(handleToParentMatrix.GetMatrix())

    transform_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
    transform_node.SetMatrixTransformToParent(transformToParentMatrix)
    model_node.SetAndObserveTransformNodeID(transform_node.GetID())


  def rotate_to_vector(self,entry_point_world0,entry_point_world1,entry_point_world2,target_point_world0,target_point_world1,target_point_world2):
    util.mainWindow().rotate_to_vector(entry_point_world0,entry_point_world1,entry_point_world2,target_point_world0,target_point_world1,target_point_world2)
    slicer.vtkMRMLSliceNode.JumpAllSlices(slicer.mrmlScene, target_point_world0,target_point_world1,target_point_world2, 0)
    layoutManager = slicer.app.layoutManager()
    view = layoutManager.threeDWidget(0).threeDView()
    threeDViewNode = view.mrmlViewNode()
    cameraNode = slicer.modules.cameras.logic().GetViewActiveCameraNode(threeDViewNode)
    camera = cameraNode.GetCamera()

    entry_point_world = np.array([entry_point_world0,entry_point_world1,entry_point_world2])
    target_point_world = np.array([target_point_world0,target_point_world1,target_point_world2])
    ne = np.array(entry_point_world)
    nt = np.array(target_point_world)
    focus_point = (ne+nt)/2
    norm1 = (ne-nt )/ np.linalg.norm(ne-nt)
    camera_point = norm1*500+nt
    camera.SetPosition(camera_point)
    camera.SetFocalPoint(focus_point)
    for threeDViewIndex in range(layoutManager.threeDViewCount) :
        controller = layoutManager.threeDWidget(threeDViewIndex).threeDController()
        controller.resetFocalPoint()


  def rotate_angle_along_vector(self,model_node,angle,focus_point,vector):
    matrix_old = vtk.vtkMatrix4x4()
    transform_old = model_node.GetParentTransformNode()
    transform_old.GetMatrixTransformToParent(matrix_old)

    modelToParentTransform = vtk.vtkMatrix4x4()
    handleToWorldMatrix = vtk.vtkTransform()
    handleToWorldMatrix.Concatenate(matrix_old)
    handleToWorldMatrix.PostMultiply()
    handleToWorldMatrix.Translate(-focus_point[0], -focus_point[1], -focus_point[2])
    handleToWorldMatrix.RotateWXYZ(angle,vector)
    handleToWorldMatrix.Translate(focus_point)
    modelToParentTransform.DeepCopy(handleToWorldMatrix.GetMatrix())
    transform_old.SetMatrixTransformToParent(modelToParentTransform)

  def move_depth_along_vector(self,model_node,depth,vector):
    matrix_old = vtk.vtkMatrix4x4()
    transform_old = model_node.GetParentTransformNode()
    if transform_old:
      transform_old.GetMatrixTransformToParent(matrix_old)
      modelToParentTransform = vtk.vtkMatrix4x4()
      handleToWorldMatrix = vtk.vtkTransform()
      handleToWorldMatrix.Concatenate(matrix_old)
      handleToWorldMatrix.PostMultiply()
      handleToWorldMatrix.Translate(depth*vector)
      modelToParentTransform.DeepCopy(handleToWorldMatrix.GetMatrix())
      transform_old.SetMatrixTransformToParent(modelToParentTransform)
    else:
      modelToParentTransform = vtk.vtkMatrix4x4()
      handleToWorldMatrix = vtk.vtkTransform()
      handleToWorldMatrix.Translate(depth*vector)
      modelToParentTransform.DeepCopy(handleToWorldMatrix.GetMatrix())
      transform_node = util.AddNewNodeByClass("vtkMRMLTransformNode")
      transform_node.SetMatrixTransformToParent(modelToParentTransform)
      model_node.SetAndObserveTransformNodeID(transform_node.GetID())

  def rotate_fiber_model_to_vector(self,model_node,m_PointInput,m_PointTarget,length):
    length = length/2
    half_vector = (np.array(m_PointInput) - np.array(m_PointTarget))/2
    half_vector_len = np.sqrt(half_vector[0]*half_vector[0]+half_vector[1]*half_vector[1]+half_vector[2]*half_vector[2])

    transformToParentMatrix = vtk.vtkMatrix4x4()
    transformToParentMatrix.Identity()
    transformToParentMatrix.SetElement(0, 3, m_PointTarget[0])
    transformToParentMatrix.SetElement(1, 3, m_PointTarget[1])
    transformToParentMatrix.SetElement(2, 3, m_PointTarget[2])

    rotationVector_Local = np.array([0,0,0])
    vector1 = np.array(m_PointInput) - np.array(m_PointTarget)
    vector0 = np.array([0,1,0])
    angle = vtk.vtkMath.DegreesFromRadians(vtk.vtkMath.AngleBetweenVectors(vector0,vector1))
    vtk.vtkMath.Cross(vector0, vector1, rotationVector_Local)
    handleToParentMatrix=vtk.vtkTransform()
    handleToParentMatrix.PostMultiply()
    handleToParentMatrix.Concatenate(transformToParentMatrix)
    handleToParentMatrix.Translate(-m_PointTarget[0], -m_PointTarget[1], -m_PointTarget[2])
    handleToParentMatrix.RotateWXYZ(angle, rotationVector_Local)
    handleToParentMatrix.Translate(m_PointTarget[0]+half_vector[0]*length/half_vector_len,m_PointTarget[1]+half_vector[1]*length/half_vector_len,m_PointTarget[2]+half_vector[2]*length/half_vector_len)
    transformToParentMatrix.DeepCopy(handleToParentMatrix.GetMatrix())

    transform_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
    transform_node.SetMatrixTransformToParent(transformToParentMatrix)
    model_node.SetAndObserveTransformNodeID(transform_node.GetID())
    
  '''
    local_point:  类似格式[10,2,2]
    node       :  局部点所在的节点,local_point就是该节点下的ijk坐标
  '''
  def get_global_point_from_ijk(self,local_point,node):
    if len(local_point) == 3:
      local_point = [local_point[0],local_point[1],local_point[2],1]
    matrix_old = vtk.vtkMatrix4x4()
    transform_old = node.GetParentTransformNode()
    transform_old.GetMatrixTransformToParent(matrix_old)
    p1_world = matrix_old.MultiplyPoint(local_point)
    return p1_world[0:3]

  '''
    point:      类似格式[10,2,2]
    model_node: point所绑定的点
  '''
  def transform_point_by_model(self,point,model_node):
    transform_node_id = model_node.GetTransformNodeID()
    if transform_node_id is not None:
      transform_node = util.GetNodeByID(transform_node_id)
      transformMatrix = vtk.vtkMatrix4x4()
      transform_node.GetMatrixTransformToParent(transformMatrix)
      p5 = transformMatrix.MultiplyPoint([point[0],point[1],point[2],1])
      p5 = [p5[0],p5[1],p5[2]]
      return p5


 