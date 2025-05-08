import slicer,qt,vtk,ctk
import slicer.util as util
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from Base.JBaseExtension import JBaseExtensionWidget
import numpy as np
#
# UnitAutoHollow
#


class UnitAutoHollow(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UnitAutoHollow"  # TODO: make this more human readable by adding spaces
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
# UnitAutoHollowWidget
#

class UnitAutoHollowWidget(JBaseExtensionWidget):
  volume_node = None
  segment_node = None
  title = None
  trigger_button = None
  cloned_segment = None
  def setup(self):
    super().setup()
    self.ui.tabWidget.tabBar().hide()
    
  def init(self,volume_node,segment_node,title,trigger_button):
    self.volume_node = volume_node
    self.segment_node = segment_node
    self.title = title
    self.trigger_button = trigger_button
    self.cloned_segment = util.clone(self.segment_node)
    self.cloned_segment.SetName(self.segment_node.GetName()+"_copy")
    util.HideNode(self.cloned_segment)
  
  def init_ui(self):
    self.ui.btn_generate_point.connect('clicked()',self.on_generate_point)
    self.ui.btn_hollow.connect('clicked()',self.on_hollow)
    self.ui.btn_revert.connect('clicked()',self.on_revert)
    self.ui.btn_return.connect('clicked()',self.on_return)
    
    validator = qt.QIntValidator(1, 999, self.ui.tabWidget)
    self.ui.lineEdit.setValidator(validator)
    
    validator = qt.QIntValidator(1, 999, self.ui.tabWidget)
    self.ui.lineEdit_2.setValidator(validator)
    
    slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeRemovedEvent, self.OnNodeRemovedEvent)
    
  
  @vtk.calldata_type(vtk.VTK_OBJECT)
  def OnNodeRemovedEvent(self,caller,str_event,calldata):
    if self.volume_node is None:
      return
    if calldata == self.volume_node :
      if self.trigger_button:
        self.trigger_button.setChecked(False)
  
  
  def on_return(self):
    self.trigger_button.setChecked(False)
  
  def on_revert(self):
    name1 = self.segment_node.GetName()
    util.RemoveNode(self.segment_node)
    self.cloned_segment.SetName(name1)
    util.ShowNode(self.cloned_segment)
    self.segment_node = self.cloned_segment
    self.cloned_segment = util.clone(self.segment_node)
    self.cloned_segment.SetName(self.segment_node.GetName()+"_copy")
    util.HideNode(self.cloned_segment)
    util.ShowNodeByName("crop_hole_point")
    util.GetDisplayNode(self.segment_node).SetOpacity(0.3)
  
  def on_hollow(self):
    volume_node = self.volume_node
    pointnode = util.getFirstNodeByName("crop_hole_point")
    segmentnode = self.segment_node
    if  not segmentnode:
      util.showWarningText("请先创建一个面具")
      return
    nc = util.GetControlPointNumber(pointnode)
    
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segmentnode)
    segmentEditorWidget.setSourceVolumeNode(volume_node)
    segmentEditorWidget.setActiveEffectByName("Logical operators")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("Operation", "SUBTRACT")
    
    try:
      radius = int(self.ui.lineEdit_2.text)
    except Exception as e:
      util.showWarningText("请在镂空半径出入一个数字")
      return
    for i in range(nc):
      control_point = util.GetNthControlPointPosition(pointnode,i)
      tumorSeed = vtk.vtkSphereSource()
      tumorSeed.SetCenter(control_point[0], control_point[1], control_point[2])
      tumorSeed.SetRadius(radius)
      tumorSeed.Update()
      segmentId = segmentnode.AddSegmentFromClosedSurfaceRepresentation(tumorSeed.GetOutput(), "Segment A", [1.0,0.0,0.0])
      effect.setParameter("ModifierSegmentID",segmentId)
      effect.self().onApply()
      segmentnode.RemoveSegment(segmentId)
    
    util.HideNodeByName("crop_hole_point")
  
  def on_generate_point(self):
    def sample_points_on_segment(surfacePolyData, min_distance, max_attempts=10000):
        points = vtk.vtkPoints()
        locator = vtk.vtkPointLocator()
        locator.SetDataSet(surfacePolyData)
        locator.BuildLocator()

        added_points = []
        attempts = 0

        # 初始随机放置点
        while len(added_points) < max_attempts:
            random_point_id = np.random.randint(0, surfacePolyData.GetNumberOfPoints())
            point = surfacePolyData.GetPoint(random_point_id)
            
            # 检查新点与所有已添加点之间的距离
            too_close = any(np.linalg.norm(np.array(point) - np.array(added)) < min_distance for added in added_points)
            
            if not too_close:
                added_points.append(point)
                if len(added_points) == 500:  # 假设我们尝试放置最多500个点
                    break
            attempts += 1
            if attempts >= max_attempts:
                break

        # 迭代优化点位置
        for _ in range(20):  # 迭代次数可以根据需要增加
            for i in range(len(added_points)):
                current_point = added_points[i]
                for j in range(10):  # 每个点尝试10次移动
                    random_shift = np.random.normal(0, 0.1, 3)  # 微小移动
                    new_point = current_point + random_shift
                    closestPointId = locator.FindClosestPoint(new_point)
                    new_point_closest = surfacePolyData.GetPoint(closestPointId)
                    # 检查移动后的点是否更优
                    if not any(np.linalg.norm(np.array(new_point_closest) - np.array(other)) < min_distance for other in added_points if other is not current_point):
                        added_points[i] = new_point_closest

        # 添加点到vtkPoints对象
        for pt in added_points:
            points.InsertNextPoint(pt)

        return points

    # 获取Segmentation节点和Segment
    segmentationNode = self.segment_node
    if  not segmentationNode:
      util.showWarningText("请先创建一个面具")
      return
    segmentId = segmentationNode.GetSegmentation().GetNthSegmentID(0)

    # 获取表面模型
    surfacePolyData = vtk.vtkPolyData()
    segmentationNode.GetClosedSurfaceRepresentation(segmentId, surfacePolyData)

    try:
      # 调用函数
      sampled_points = sample_points_on_segment(surfacePolyData, int(self.ui.lineEdit.text))  # 最小距离50mm
    except Exception as e:
      util.showWarningText("请在点之间的距离输入一个数字")
      return

    # 创建Markup点
    pointNode = util.EnsureFirstNodeByNameByClass("crop_hole_point",util.vtkMRMLMarkupsFiducialNode,delete=True)
    util.GetDisplayNode(pointNode).SetPointLabelsVisibility(False)
    for i in range(sampled_points.GetNumberOfPoints()):
        pointNode.AddControlPointWorld(vtk.vtkVector3d(sampled_points.GetPoint(i)))
    
    util.GetDisplayNode(self.segment_node).SetOpacity(0.3)
        
        
  def exit(self):
    util.RemoveNode(self.cloned_segment)
    self.cloned_segment = None