import slicer,qt,vtk,ctk
import slicer.util as util
import os
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from Base.JBaseExtension import JBaseExtensionWidget
import UnitPunctureGuideLib.G_UnitPunctureGuide as G
import threading
import numpy as np

class sunHeadFrame(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "sunHeadFrame"  # TODO: make this more human readable by adding spaces
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

class sunHeadFrameWidget(JBaseExtensionWidget):
  def setup(self):
    super().setup()
    self.ui.tabWidget_2.tabBar().hide()
    self.old_frame_whole_value = 0
    self.old_frame_slider_value = 0
    self.old_frame_right_slider_value = 0
    self.old_frame_rotate_value = 0
    self.old_frame_move1_value = 0
    self.old_puncture_value = 0
    self.old_puncture_value2 = 0
    self.old_left_puncture = 0
    self.old_right_puncture_value = 0
    self.old_left_puncture_value = 0
    
    
    self.ui.slider0.singleStep = 0.1
    self.ui.slider0.minimum = -360
    self.ui.slider0.maximum = 360
    self.ui.slider0.value= 0
    self.ui.slider0.connect('valueChanged(double)', self.on_frame_whole_rotate)
    
    
    self.ui.slider2.singleStep = 0.5
    self.ui.slider2.minimum = -360
    self.ui.slider2.maximum = 360
    self.ui.slider2.value= 0
    self.ui.slider2.connect('valueChanged(double)', self.on_frame_move1)
    
    self.ui.slider3.singleStep = 0.1
    self.ui.slider3.minimum = -130
    self.ui.slider3.maximum = 93
    self.ui.slider3.value= 0
    self.ui.slider3.connect('valueChanged(double)', self.on_frame_rotate2)
    
    self.ui.slider4.singleStep = 0.1
    self.ui.slider4.minimum = -93
    self.ui.slider4.maximum = 93
    self.ui.slider4.value= 0
    self.ui.slider4.connect('valueChanged(double)', self.on_frame_rotate3)
    
    self.ui.slider5.singleStep = 1
    self.ui.slider5.minimum = -80
    self.ui.slider5.maximum = 200
    self.ui.slider5.value= 0
    self.ui.slider5.connect('valueChanged(double)', self.on_puncture2)
    
    
    self.ui.slider6.singleStep = 1
    self.ui.slider6.minimum = -100
    self.ui.slider6.maximum = 130
    self.ui.slider6.value= 0
    self.ui.slider6.connect('valueChanged(double)', self.on_puncture3)
    
    
    self.ui.slider7.singleStep = 1
    self.ui.slider7.minimum = -150
    self.ui.slider7.maximum = 50
    self.ui.slider7.value= 0
    self.ui.slider7.connect('valueChanged(double)', self.on_left_puncture)
    
    self.ui.slider8.singleStep = 1
    self.ui.slider8.minimum = -70
    self.ui.slider8.maximum = 70
    self.ui.slider8.value= 0
    self.ui.slider8.connect('valueChanged(double)', self.on_right_puncture)
    
    self.ui.pushButton.connect('clicked()',self.on_reverse)
    
  def on_reverse(self):
    self.reset()
    modellist = util.getNodesByAttribute("is_head_frame","1")
    modellist = modellist+[util.getFirstNodeByName("frame_right"),util.getFirstNodeByName("frame_needle_right"),util.getFirstNodeByName("frame_needle_left"),util.getFirstNodeByName("frame_left"),util.getFirstNodeByName("toppoint_needle")]
    frame_upnode= util.getFirstNodeByName("frame_up")
    frame_centernode = util.getFirstNodeByName("headframenode_center")
    center=util.get_world_position(frame_centernode)
    n1 = np.array(util.get_world_position(frame_upnode))-np.array(util.get_world_position(frame_centernode))
    
    transformToParentMatrix = vtk.vtkMatrix4x4()
    transformToParentMatrix.Identity()
    handleToParentMatrix=vtk.vtkTransform()
    handleToParentMatrix.PostMultiply()
    handleToParentMatrix.Concatenate(transformToParentMatrix)
    handleToParentMatrix.Translate(-center[0], -center[1], -center[2])
    handleToParentMatrix.RotateWXYZ(180, n1)
    handleToParentMatrix.Translate(center[0], center[1], center[2])
    transformToParentMatrix.DeepCopy(handleToParentMatrix.GetMatrix())

    transform_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
    transform_node.SetMatrixTransformToParent(transformToParentMatrix)
    
    for modelnode in modellist:
      modelnode.SetAndObserveTransformNodeID(transform_node.GetID())
      modelnode.HardenTransform()
    util.RemoveNode(transform_node)
    
    # frame_left = util.getFirstNodeByName("frame_left")
    # frame_right = util.getFirstNodeByName("frame_right")
    # frame_needle_left = util.getFirstNodeByName("frame_needle_left")
    # frame_needle_right = util.getFirstNodeByName("frame_needle_right")
    # frame_left.SetName("aa1")
    # frame_needle_left.SetName("aa2")
    # frame_right.SetName("frame_left")
    # frame_needle_right.SetName("frame_needle_left")
    # frame_left.SetName("frame_right")
    # frame_needle_left.SetName("frame_needle_right")
    
    # left_stick_needle = util.getFirstNodeByName("left_stick_needle")
    # left_stick_pipe = util.getFirstNodeByName("left_stick_pipe")
    # left_kedu = util.getFirstNodeByName("left_kedu")
    # right_stick_needle = util.getFirstNodeByName("right_stick_needle")
    # right_stick_pipe = util.getFirstNodeByName("right_stick_pipe")
    # right_kedu = util.getFirstNodeByName("right_kedu")
    # left_stick_needle.SetName("right_stick_needle")
    # left_stick_pipe.SetName("right_stick_pipe")
    # if left_kedu:
    #   left_kedu.SetName("right_kedu")
    # right_stick_needle.SetName("left_stick_needle")
    # right_stick_pipe.SetName("left_stick_pipe")
    # if right_kedu:
    #   right_kedu.SetName("left_kedu")
    
    # leftpumbs = util.getNodesByAttribute("left_pump_widget","1")
    # rightpumbs = util.getNodesByAttribute("right_pump_widget","1")
    # for node in leftpumbs:
    #   node.SetAttribute("left_pump_widget","0")
    #   node.SetAttribute("right_pump_widget","1")
    # for node in rightpumbs:
    #   node.SetAttribute("left_pump_widget","1")
    #   node.SetAttribute("right_pump_widget","0")

  def set_front_back(self,val):
    self.ui.slider0.setValue(self.ui.slider0.value+val)
  def set_rotate(self,val):
    self.ui.slider3.setValue(self.ui.slider3.value+val)

  def on_frame_rotate3(self,value):
      modellist = [util.getFirstNodeByName("top_right_slider"),util.getFirstNodeByName("top_inner_right_slider"),util.getFirstNodeByName("top_right_needle"),util.getFirstNodeByName("toppointright_needle")]
      differ = value - self.old_frame_right_slider_value
      self.old_frame_right_slider_value = value
      frame_upnode= util.getFirstNodeByName("frame_up")
      frame_centernode = util.getFirstNodeByName("headframenode_center")
      fc = util.get_world_position(frame_centernode)
      frame_left = util.getFirstNodeByName("frame_left")
      n1 = np.array(util.get_world_position(frame_upnode))-np.array(util.get_world_position(frame_centernode))
      n2= np.array(util.get_world_position(frame_left))-np.array(util.get_world_position(frame_centernode))
      cross_product = np.cross(n1, n2)
      
      transformToParentMatrix = vtk.vtkMatrix4x4()
      transformToParentMatrix.Identity()
      handleToParentMatrix=vtk.vtkTransform()
      handleToParentMatrix.PostMultiply()
      handleToParentMatrix.Concatenate(transformToParentMatrix)
      handleToParentMatrix.Translate(-fc[0], -fc[1], -fc[2])
      handleToParentMatrix.RotateWXYZ(differ, cross_product)
      handleToParentMatrix.Translate(fc[0], fc[1], fc[2])
      transformToParentMatrix.DeepCopy(handleToParentMatrix.GetMatrix())

      transform_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
      transform_node.SetMatrixTransformToParent(transformToParentMatrix)
      
      for modelnode in modellist:
        modelnode.SetAndObserveTransformNodeID(transform_node.GetID())
        modelnode.HardenTransform()
      util.RemoveNode(transform_node)

  def reset(self):
    self.ui.slider0.blockSignals(True)
    self.ui.slider2.blockSignals(True)
    self.ui.slider3.blockSignals(True)
    self.ui.slider4.blockSignals(True)
    self.ui.slider5.blockSignals(True)
    self.ui.slider6.blockSignals(True)
    self.ui.slider7.blockSignals(True)
    self.ui.slider8.blockSignals(True)
    self.old_frame_whole_value = 0
    self.old_frame_slider_value = 0
    self.old_frame_right_slider_value = 0
    self.old_frame_rotate_value = 0
    self.old_frame_move1_value = 0
    self.old_puncture_value = 0
    self.old_puncture_value2 = 0
    self.old_left_puncture = 0
    self.old_right_puncture_value = 0
    self.old_left_puncture_value = 0
    
    self.ui.slider0.value= 0
    self.ui.slider2.value= 0
    self.ui.slider3.value= 0
    self.ui.slider4.value= 0
    self.ui.slider5.value= 0
    self.ui.slider6.value= 0
    self.ui.slider7.value= 0
    self.ui.slider8.value= 0
    
    self.ui.slider0.blockSignals(False)
    self.ui.slider2.blockSignals(False)
    self.ui.slider3.blockSignals(False)
    self.ui.slider4.blockSignals(False)
    self.ui.slider5.blockSignals(False)
    self.ui.slider6.blockSignals(False)
    self.ui.slider7.blockSignals(False)
    self.ui.slider8.blockSignals(False)

  def on_frame_whole_rotate(self,value):
      modellist = util.getNodesByAttribute("is_head_frame","1")
      modellist = modellist + [util.getFirstNodeByName("headframenode_center"),util.getFirstNodeByName("frame_up"),util.getFirstNodeByName("frame_left"),util.getFirstNodeByName("frame_right"),util.getFirstNodeByName("frame_needle_right"),util.getFirstNodeByName("toppoint_needle"),util.getFirstNodeByName("toppointright_needle")]
      differ = value - self.old_frame_whole_value
      self.old_frame_whole_value = value
      frame_left = util.getFirstNodeByName("frame_left")
      frame_right = util.getFirstNodeByName("frame_right")
      n1 = np.array(util.get_world_position(frame_left))-np.array(util.get_world_position(frame_right))
      
      center = util.get_world_control_point_by_name("headframenode_center")
      transformToParentMatrix = vtk.vtkMatrix4x4()
      transformToParentMatrix.Identity()
      handleToParentMatrix=vtk.vtkTransform()
      handleToParentMatrix.PostMultiply()
      handleToParentMatrix.Concatenate(transformToParentMatrix)
      handleToParentMatrix.Translate(-center[0], -center[1], -center[2])
      handleToParentMatrix.RotateWXYZ(differ, n1)
      handleToParentMatrix.Translate(center[0], center[1], center[2])
      transformToParentMatrix.DeepCopy(handleToParentMatrix.GetMatrix())

      transform_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
      transform_node.SetMatrixTransformToParent(transformToParentMatrix)
      
      for modelnode in modellist:
        modelnode.SetAndObserveTransformNodeID(transform_node.GetID())
        modelnode.HardenTransform()
      util.RemoveNode(transform_node)

  def on_frame_rotate2(self,value):
      modellist = [util.getFirstNodeByName("top_slider"),util.getFirstNodeByName("top_inner_slider"),util.getFirstNodeByName("top_needle"),util.getFirstNodeByName("toppoint_needle"),util.getFirstNodeByName("G22033 _ G22033_028_5"),util.getFirstNodeByName("G22033 _ G22033_028_6"),util.getFirstNodeByName("top_kedu")]
      modellist = modellist+util.getNodesByAttribute("top_extra_widget","1")
      differ = value - self.old_frame_slider_value
      self.old_frame_slider_value = value
      frame_upnode= util.getFirstNodeByName("frame_up")
      frame_centernode = util.getFirstNodeByName("headframenode_center")
      fc = util.get_world_position(frame_centernode)
      frame_left = util.getFirstNodeByName("frame_left")
      n1 = np.array(util.get_world_position(frame_upnode))-np.array(util.get_world_position(frame_centernode))
      n2= np.array(util.get_world_position(frame_left))-np.array(util.get_world_position(frame_centernode))
      cross_product = np.cross(n1, n2)
      
      transformToParentMatrix = vtk.vtkMatrix4x4()
      transformToParentMatrix.Identity()
      handleToParentMatrix=vtk.vtkTransform()
      handleToParentMatrix.PostMultiply()
      handleToParentMatrix.Concatenate(transformToParentMatrix)
      handleToParentMatrix.Translate(-fc[0], -fc[1], -fc[2])
      handleToParentMatrix.RotateWXYZ(differ, cross_product)
      handleToParentMatrix.Translate(fc[0], fc[1], fc[2])
      transformToParentMatrix.DeepCopy(handleToParentMatrix.GetMatrix())

      transform_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
      transform_node.SetMatrixTransformToParent(transformToParentMatrix)
      
      for modelnode in modellist:
        if modelnode is None:
          continue
        modelnode.SetAndObserveTransformNodeID(transform_node.GetID())
        modelnode.HardenTransform()
      util.RemoveNode(transform_node)
  
  def on_left_puncture(self,value):
    modellist = util.getNodesByAttribute("left_pump_widget","1")
    differ = value - self.old_left_puncture_value
    self.old_left_puncture_value = value
    
    frame_centernode = util.getFirstNodeByName("headframenode_center")
    toppoint_needle = util.getFirstNodeByName("frame_left")
    move_line= np.array(util.get_world_position(toppoint_needle))-np.array(util.get_world_position(frame_centernode))
    norm = np.linalg.norm(move_line)
    unit_vector = move_line / norm
    
    transformToParentMatrix = vtk.vtkMatrix4x4()
    transformToParentMatrix.Identity()
    handleToParentMatrix=vtk.vtkTransform()
    handleToParentMatrix.PostMultiply()
    handleToParentMatrix.Concatenate(transformToParentMatrix)
    handleToParentMatrix.Translate(unit_vector[0]*differ, unit_vector[1]*differ, unit_vector[2]*differ)
    transformToParentMatrix.DeepCopy(handleToParentMatrix.GetMatrix())

    transform_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
    transform_node.SetMatrixTransformToParent(transformToParentMatrix)
    
    for modelnode in modellist:
      if modelnode:
        modelnode.SetAndObserveTransformNodeID(transform_node.GetID())
        modelnode.HardenTransform()
    util.RemoveNode(transform_node)
    
  def on_right_puncture(self,value):
    modellist = util.getNodesByAttribute("right_pump_widget","1")
    differ = value - self.old_right_puncture_value
    self.old_right_puncture_value = value
    
    frame_centernode = util.getFirstNodeByName("top_right2")
    toppoint_needle = util.getFirstNodeByName("top_right1")
    move_line= np.array(util.get_world_position(toppoint_needle))-np.array(util.get_world_position(frame_centernode))
    norm = np.linalg.norm(move_line)
    unit_vector = move_line / norm
    
    transformToParentMatrix = vtk.vtkMatrix4x4()
    transformToParentMatrix.Identity()
    handleToParentMatrix=vtk.vtkTransform()
    handleToParentMatrix.PostMultiply()
    handleToParentMatrix.Concatenate(transformToParentMatrix)
    handleToParentMatrix.Translate(unit_vector[0]*differ, unit_vector[1]*differ, unit_vector[2]*differ)
    transformToParentMatrix.DeepCopy(handleToParentMatrix.GetMatrix())

    transform_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
    transform_node.SetMatrixTransformToParent(transformToParentMatrix)
    
    for modelnode in modellist:
      if modelnode:
        modelnode.SetAndObserveTransformNodeID(transform_node.GetID())
        modelnode.HardenTransform()
    util.RemoveNode(transform_node)
  
  def on_puncture2(self,value):
    modellist = [util.getFirstNodeByName("top_needle")]
    differ = value - self.old_puncture_value
    self.old_puncture_value = value
    
    frame_centernode = util.getFirstNodeByName("headframenode_center")
    toppoint_needle = util.getFirstNodeByName("toppoint_needle")
    move_line= np.array(util.get_world_position(toppoint_needle))-np.array(util.get_world_position(frame_centernode))
    norm = np.linalg.norm(move_line)
    unit_vector = move_line / norm
    
    transformToParentMatrix = vtk.vtkMatrix4x4()
    transformToParentMatrix.Identity()
    handleToParentMatrix=vtk.vtkTransform()
    handleToParentMatrix.PostMultiply()
    handleToParentMatrix.Concatenate(transformToParentMatrix)
    handleToParentMatrix.Translate(unit_vector[0]*differ, unit_vector[1]*differ, unit_vector[2]*differ)
    transformToParentMatrix.DeepCopy(handleToParentMatrix.GetMatrix())

    transform_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
    transform_node.SetMatrixTransformToParent(transformToParentMatrix)
    
    for modelnode in modellist:
      modelnode.SetAndObserveTransformNodeID(transform_node.GetID())
      modelnode.HardenTransform()
    util.RemoveNode(transform_node)
    
  def on_puncture3(self,value):
    modellist = [util.getFirstNodeByName("top_right_needle")]
    differ = value - self.old_puncture_value2
    self.old_puncture_value2 = value
    
    frame_centernode = util.getFirstNodeByName("headframenode_center")
    toppoint_needle = util.getFirstNodeByName("toppointright_needle")
    move_line= np.array(util.get_world_position(toppoint_needle))-np.array(util.get_world_position(frame_centernode))
    norm = np.linalg.norm(move_line)
    unit_vector = move_line / norm
    
    transformToParentMatrix = vtk.vtkMatrix4x4()
    transformToParentMatrix.Identity()
    handleToParentMatrix=vtk.vtkTransform()
    handleToParentMatrix.PostMultiply()
    handleToParentMatrix.Concatenate(transformToParentMatrix)
    handleToParentMatrix.Translate(unit_vector[0]*differ, unit_vector[1]*differ, unit_vector[2]*differ)
    transformToParentMatrix.DeepCopy(handleToParentMatrix.GetMatrix())

    transform_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
    transform_node.SetMatrixTransformToParent(transformToParentMatrix)
    
    for modelnode in modellist:
      if modelnode:
        modelnode.SetAndObserveTransformNodeID(transform_node.GetID())
        modelnode.HardenTransform()
    util.RemoveNode(transform_node)
      
  def on_frame_move1(self,value):
      differ = value - self.old_frame_move1_value
      self.old_frame_move1_value = value
      left_stick_needle = util.getFirstNodeByName("left_stick_needle")
      right_stick_needle = util.getFirstNodeByName("right_stick_needle")
      frame_left = util.getFirstNodeByName("frame_left")
      frame_right = util.getFirstNodeByName("frame_right")
      modellist = util.getNodesByAttribute("is_head_frame","1")
      frame_upnode= util.getFirstNodeByName("frame_up")
      frame_centernode = util.getFirstNodeByName("headframenode_center")
      modellist += [frame_upnode,frame_centernode,util.getFirstNodeByName("toppoint_needle"),util.getFirstNodeByName("toppointright_needle")]
      move_line = np.array(util.get_world_position(frame_left))-np.array(util.get_world_position(frame_right))
      norm = np.linalg.norm(move_line)
      unit_vector = move_line / norm
      
      transformToParentMatrix = vtk.vtkMatrix4x4()
      transformToParentMatrix.Identity()
      handleToParentMatrix=vtk.vtkTransform()
      handleToParentMatrix.PostMultiply()
      handleToParentMatrix.Concatenate(transformToParentMatrix)
      handleToParentMatrix.Translate(unit_vector[0]*differ, unit_vector[1]*differ, unit_vector[2]*differ)
      transformToParentMatrix.DeepCopy(handleToParentMatrix.GetMatrix())

      transform_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
      transform_node.SetMatrixTransformToParent(transformToParentMatrix)
      
      for modelnode in modellist:
        modelnode.SetAndObserveTransformNodeID(transform_node.GetID())
        modelnode.HardenTransform()
      util.RemoveNode(transform_node)
  