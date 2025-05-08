import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from Base.JBaseExtension import JBaseExtensionWidget
import slicer.util as util
import random
#
# JMutiPointPanel
#

class PointItem:
  def __init__(self,main,uiWidget,ui,markupsNode,tag) -> None:
    self.main = main
    self.uiWidget = uiWidget
    self.ui = ui
    self.markupsNode = markupsNode
    self.tag = tag
    
    self.ui.label.setText(tag)
    self.ui.checkBox.setChecked(True)
    self.ui.checkBox.connect('toggled(bool)',self.on_checkbox_toggled)
    
  def on_checkbox_toggled(self,val):
    if val:
      util.ShowNode(self.markupsNode)
    else:
      util.HideNode(self.markupsNode)


class PanelItem:
  def __init__(self,main,uiWidget,ui,panelNode,item) -> None:
    self.main = main
    self.uiWidget = uiWidget
    self.ui = ui
    self.panelNode = panelNode
    self.item = item
    
    color = util.GetDisplayNode(self.panelNode).GetSelectedColor()
    self.ui.label.setStyleSheet(f"background-color: rgb({color[0]*255}, {color[1]*255}, {color[2]*255});")
    
    self.ui.pushButton.connect('clicked()',self.on_export)
    self.ui.pushButton_2.connect('clicked()',self.on_delete)
    
  def on_delete(self):
    self.main.on_delete_panel(self)
    
  def on_export(self):
    fileName = qt.QFileDialog.getSaveFileName(None, ("保存文件"),
                              "/model.vtk",
                              ("模型 (*.vtk)"))
    if fileName == "":
      util.showWarningText("请选择一个文件地址用来存储模型")
      return
    
    if not self.panelNode:
      util.showWarningText("请先创建平面")
      return
    model = self.convert_plane_to_model(self.panelNode)
    slicer.util.saveNode(model,fileName)
    util.RemoveNode(model)
    util.showWarningText(f"模型已经被存储到 {fileName}")
    
  def convert_plane_to_model(self,planeNode):
    ps = vtk.vtkPoints()
    planeNode.GetPlaneCornerPointsWorld(ps)
    
    p1 = [0,0,0]
    ps.GetPoint(0,p1)
    p2 = [0,0,0]
    ps.GetPoint(1,p2)
    p3 = [0,0,0]
    ps.GetPoint(3,p3)
    
    planeSource = vtk.vtkPlaneSource()
    planeSource.SetOrigin(p1)
    planeSource.SetPoint1(p2[0],p2[1],p2[2])
    planeSource.SetPoint2(p3[0],p3[1],p3[2])
    model = slicer.modules.models.logic().AddModel(planeSource.GetOutputPort())
    return model
      

class JMutiPointPanel(ScriptedLoadableModule):
  volume = None
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "JMutiPointPanel"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["JPlugins"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["jia ze yu"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """

"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """

"""


class JMutiPointPanelWidget(JBaseExtensionWidget):
  point_item_list = []
  panel_item_list = []
  def setup(self):
    super().setup()
    pass
  
  def enter(self):
    layoutManager = slicer.app.layoutManager()
    layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUp3DView)
  
  def init_ui(self):
    self.ui.pushButton_4.setVisible(False)
    self.ui.pushButton_3.connect('clicked()',self.on_caculate_10point)
    self.ui.pushButton.connect('clicked()',self.create_panel)
    self.ui.pushButton_2.connect('clicked()',self.on_return)
    self.ui.pushButton_4.connect('clicked()',self.on_reload)
  
  def on_reload(self):
    self.onReload()
  
  def on_return(self):
    util.send_event_str(util.GotoPrePage)
  
  def get_container(self):
    return self.ui.JMeasure
  
  def show_volume(self,volume):
    self.volume = volume
  
  def on_caculate_10point(self):
    import subprocess
    import re
    import shutil

    numOfCoo=17
    script_path = 'script.py'


    # the target path
    targetname = 'example_ct.nii.gz'
    def extract_coordinates(script_path='script.py',numOfCoo=10):
            copy_file(targetname, "example/test_images/image_test_0.nii.gz")
            util.send_event_str(util.ProgressValue,30)

            #run the script.py with default
            result = subprocess.run(['PythonSlicer', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            output = result.stdout
            print(result)
            pattern = r'\(([^)]+)\) --> \(([^)]+)\)'


            matches = re.findall(pattern, output)


            right_side_coordinates = [f"({match[1]})" for match in matches]
            last_coordinates = right_side_coordinates[-numOfCoo:]
            print(last_coordinates)
            return last_coordinates





    def copy_file(source_path, destination_path):

            try:
                shutil.copy2(source_path, destination_path)
            except FileNotFoundError:
                print(f"源文件 '{source_path}' 不存在。")
            except PermissionError:
                print(f"没有权限访问文件 '{source_path}' 或 '{destination_path}'。")
            except Exception as e:
                print(f"复制文件时发生错误: {e}")



    util.send_event_str(util.ProgressStart,"正在计算10个关键点位置")
    util.send_event_str(util.ProgressValue,0)
            
    coordinates = extract_coordinates(script_path,numOfCoo)
    util.send_event_str(util.ProgressValue,90)

    print("coo:")
    for coord in coordinates:
        print(coord)
    
    val = self.get_random_number()
    pixelvals = val.split(",")
    i = 0
    names = ["鼻根点","左眼眶上","左眼眶下缘最低点","左前切迹","左前切迹对应","左前切迹内侧端","左后切迹内侧端","左外耳道上缘中点","左顶颞点","右眼眶上","右眼眶下缘最低点","右前切迹","右前切迹对应","右前切迹内侧端","右后切迹内侧端","右外耳道上缘中点","右顶颞点"]
    
    for coord in coordinates:
      tag = "P"+i.__str__()
      # 去掉括号
      str_without_parentheses = coord.strip('()')
      # 将字符串拆分成列表
      str_list = str_without_parentheses.split(',')
      # 将字符串列表转换为浮点数列表
      float_list = [float(i) for i in str_list]
      x1 = float(float_list[0])
      y1 = float(float_list[1])
      z1 = float(float_list[2])
      markupsNode = util.AddControlPointGlobal([x1,y1,z1])
      util.GetDisplayNode(markupsNode).SetSelectedColor(1,0,0)
      markupsNode.SetNthControlPointLabel(0,tag)
      
      uiWidget = slicer.util.loadUI(self.resourcePath('UI/JPointItem.ui'))
      ui = slicer.util.childWidgetVariables(uiWidget)
      item = qt.QListWidgetItem(self.ui.pointlistWidget)
      point_item = PointItem(self, uiWidget, ui,markupsNode,names[i]+"("+tag+")")
      self.ui.pointlistWidget.setItemWidget(item,uiWidget)
      self.ui.pointlistWidget.addItem(item)
      item.setSizeHint(qt.QSize(300, 30))
      self.point_item_list.append(point_item)
      
      i+=1
      
    util.reinit()
    util.send_event_str(util.ProgressValue,100)
    return
      
  
  def on_point_checkbox_toggled(self,pointitem):
    index = 0
    for point_item in self.point_item_list:
      if point_item != pointitem and point_item.ui.checkBox.isChecked():
        index += 1
    if index > 2:
      for point_item in self.point_item_list:
        if point_item != pointitem and point_item.ui.checkBox.isChecked():
          point_item.ui.checkBox.setChecked(False)
          return
    return False
  
  def get_random_number(self):
    arr1 = []
    for i in range(30):
      num = random.randint(0, 300)
      arr1.append(num.__str__())
    str1 = ",".join(arr1)
    return str1
  
  def create_panel(self):
    pointlist = []
    for point_item in self.point_item_list:
      if point_item.ui.checkBox.isChecked():
        pointlist.append(point_item.markupsNode)
    if len(pointlist) > 2:
      self.do_create_panel(pointlist)
    else:
      print("need three panel")
      return
    
  def do_create_panel(self,pointlist):
    import numpy as np
    p1 = util.get_world_control_point_by_name(pointlist[0].GetName())
    p2 = util.get_world_control_point_by_name(pointlist[1].GetName())
    p3 = util.get_world_control_point_by_name(pointlist[2].GetName())
    list1 = [p1,p2,p3]
        
    self.create_plane_by_three_point(list1,"RedPlane")
  
  
  def on_delete_panel(self,panel_template):
    row = self.ui.panellistWidget.row(panel_template.item)
    self.ui.panellistWidget.takeItem(row)
    if panel_template.panelNode:
      util.RemoveNode(panel_template.panelNode)
    
  
  def create_plane_by_three_point(self,pointlist,plane_name):
    import numpy as np
    if len(pointlist) < 3:
      print("至少需要3个点来创建平面")
      return
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
    util.GetDisplayNode(planeNode).SetSelectedColor(random.randint(0, 255)/255,random.randint(0, 255)/255,random.randint(0, 255)/255)
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/JPanelItem.ui'))
    ui = slicer.util.childWidgetVariables(uiWidget)
    item = qt.QListWidgetItem(self.ui.panellistWidget)
    panel_item = PanelItem(self, uiWidget, ui,planeNode,item)
    self.ui.panellistWidget.setItemWidget(item,uiWidget)
    self.ui.panellistWidget.addItem(item)
    item.setSizeHint(qt.QSize(300, 30))
    self.panel_item_list.append(panel_item)