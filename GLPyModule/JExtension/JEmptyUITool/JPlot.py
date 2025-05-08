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
# JPlot
#

class JPlot(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "JPlot"  # TODO: make this more human readable by adding spaces
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
# JPlotWidget
#

class JPlotWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
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

    self.logic = JPlotLogic()
    self.logic.setWidget(self)

    


  def enter(self):
    pass

  def exit(self):
    pass

 

class JPlotLogic(ScriptedLoadableModuleLogic):
  table_map = {}
  chart_map = {}
  def __init__(self):
    """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
    ScriptedLoadableModuleLogic.__init__(self)
    slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeAddedEvent, self.onNodeAdded)
  

  def setWidget(self,widget):
    self.m_Widget = widget

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def onNodeAdded(self,caller, event, calldata):
    node = calldata
    #if isinstance(node, slicer.vtkMRMLMarkupsFiducialNode):
      #self.m_Widget.on_node_added(node)

  def registe_plot(self,plot_name,table_node,chart_node):
    self.table_map[plot_name] = table_node
    self.chart_map[plot_name] = chart_node

  
  def change_plot_color(self,backgroundcolor,axisColor,line_color,xrange=10):
    title=""
    tag="tag1"
    is_unique_color=False
    list1=[]
    for i in range(xrange):
      list1.append(0)
    datas = [list1]
    if len(datas)==0:
      return
    array2D = []
    array1DIndex = []
    for i in range(len(datas[0])):
      array1DIndex.append(i)
    array2D.append(array1DIndex)

    for i in range(len(datas)):
      array2D.append(datas[i])
    
    viewWidget = None
    nodes1 = util.getNodesByClass("vtkMRMLPlotViewNode")
    for i in range(len(nodes1)):
      viewWidget1 = slicer.app.layoutManager().plotWidget(i)
      plot_view_node = viewWidget1.mrmlPlotViewNode()
      if "vtkMRMLPlotViewNodePlotView1" == plot_view_node.GetID():
          viewWidget = viewWidget1
    if viewWidget == None:
      util.showWarningText("空的表格")
      return
    plot_view_node = viewWidget.mrmlPlotViewNode()
    plotChartNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotChartNode")
    plot_view_node.SetPlotChartNodeID(plotChartNode.GetID())
    pv = viewWidget.plotView()
    ch = pv.chart()
    bb = ch.GetBackgroundBrush()
    bb.SetColor([int(backgroundcolor[0]*255.0),int(backgroundcolor[1]*255.0),int(backgroundcolor[2]*255.0)])
    ch.SetBackgroundBrush(bb)
    pv = viewWidget.plotView()
    # 更改X轴颜色
    xAxis = ch.GetAxis(vtk.vtkAxis.BOTTOM)
    xAxis.GetPen().SetColorF(axisColor)
    # 更改Y轴颜色
    yAxis = ch.GetAxis(vtk.vtkAxis.LEFT)
    yAxis.GetPen().SetColorF(axisColor)
    # 更改X轴文字颜色
    xAxis = ch.GetAxis(vtk.vtkAxis.BOTTOM)
    xAxis.GetLabelProperties().SetColor(axisColor)
    # 更改Y轴文字颜色
    yAxis = ch.GetAxis(vtk.vtkAxis.LEFT)
    yAxis.GetLabelProperties().SetColor(axisColor)
    plotChartNode.SetLegendVisibility(False)
    plotChartNode.SetGridVisibility(False)
    ch.GetTitleProperties().SetColor(axisColor)
    
    table_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode")
    util.easyPlot(array2D,None,title,tag,table_node=table_node,chatnode=plotChartNode,is_unique_color=is_unique_color,color=line_color)
    return table_node,plotChartNode

  def show_plot_in_multiwidget(self,datas,title="",tag="tag1",is_unique_color=True,line_color=[0.5,0.5,0.5],backgroundcolor=[0,0,0],axisColor=[1,1,1]):
    if len(datas)==0:
      return
    array2D = []
    array1DIndex = []
    for i in range(len(datas[0])):
      array1DIndex.append(i)
    array2D.append(array1DIndex)

    for i in range(len(datas)):
      array2D.append(datas[i])
    
    viewWidget = None
    nodes1 = util.getNodesByClass("vtkMRMLPlotViewNode")
    for i in range(len(nodes1)):
      viewWidget1 = slicer.app.layoutManager().plotWidget(i)
      plot_view_node = viewWidget1.mrmlPlotViewNode()
      if "vtkMRMLPlotViewNodePlotView1" == plot_view_node.GetID():
          viewWidget = viewWidget1
    if viewWidget == None:
      util.showWarningText("空的表格")
      return
    plot_view_node = viewWidget.mrmlPlotViewNode()
    plotChartNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotChartNode")
    plot_view_node.SetPlotChartNodeID(plotChartNode.GetID())
    pv = viewWidget.plotView()
    ch = pv.chart()
    bb = ch.GetBackgroundBrush()
    bb.SetColor(backgroundcolor)
    ch.SetBackgroundBrush(bb)
    pv = viewWidget.plotView()
    # 更改X轴颜色
    xAxis = ch.GetAxis(vtk.vtkAxis.BOTTOM)
    xAxis.GetPen().SetColorF(axisColor)
    # 更改Y轴颜色
    yAxis = ch.GetAxis(vtk.vtkAxis.LEFT)
    yAxis.GetPen().SetColorF(axisColor)
    # 更改X轴文字颜色
    xAxis = ch.GetAxis(vtk.vtkAxis.BOTTOM)
    xAxis.GetLabelProperties().SetColor(axisColor)
    # 更改Y轴文字颜色
    yAxis = ch.GetAxis(vtk.vtkAxis.LEFT)
    yAxis.GetLabelProperties().SetColor(axisColor)
    plotChartNode.SetLegendVisibility(False)
    plotChartNode.SetGridVisibility(False)
    ch.GetTitleProperties().SetColor(axisColor)
    util.easyPlot(array2D,None,title,tag,chatnode=plotChartNode,is_unique_color=is_unique_color,color=line_color)


  #在一个uiwidget里创建一个图表
  def add_table_widget_in_widget(self,parent_widget,table_name,old_view_widget=None,width=618,height=320):
    viewName = table_name+"View"
    viewNode = util.getFirstNodeByName(table_name)
    tableview = util.getFirstNodeByName(viewName)
    util.RemoveNode(viewNode)
    util.RemoveNode(tableview)
    if True:
      print("create new table and tableview")
      viewNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode")
      viewNode.SetName(table_name)
      tableview = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLTableViewNode')
      tableview.SetTableNodeID(viewNode.GetID())
      tableview.SetName(viewName)
    else:
      print("exist table and tableview")
      tableview.SetTableNodeID(viewNode.GetID())
    # Create widget
    if old_view_widget is None:
      viewWidget = slicer.qMRMLTableWidget(parent_widget)
      viewWidget.setMRMLScene(slicer.mrmlScene)
      viewWidget.setMRMLTableViewNode(tableview)
      viewWidget.show()
      viewWidget.setFixedSize(width,height)
      viewWidget.tableController().setVisible(False)
    else:
      viewWidget = old_view_widget
    return viewNode,viewWidget

  '''
    目的:在一个QWidget中创建一个图表
    @parent_widget  在哪一个父容器里放入这个图表,一般是一个QWidget,长度是@width,高度是@height
    @plot_name      图表的名字,可以通过图表的名字获取到这个容器里的图标的引用
    @red @green @blue 图表的背景色
    @axisColor  坐标系的颜色
  '''
  #在一个uiwidget里创建一个图表
  def add_plot_widget_in_widget(self,parent_widget,plot_name,width=598,height=320,red=54,green=61,blue=74,axisColor=[1,1,1]):
    viewNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotViewNode")
    viewOwnerNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScriptedModuleNode")
    viewNode.SetAndObserveParentLayoutNodeID(viewOwnerNode.GetID())
    
    # Create widget
    viewWidget = slicer.qMRMLPlotWidget(parent_widget)
    viewWidget.setMRMLScene(slicer.mrmlScene)
    viewWidget.setMRMLPlotViewNode(viewNode)
    viewWidget.show()
    viewWidget.plotController().setVisible(False)
    viewWidget.setFixedSize(width,height)

    pv = viewWidget.plotView()
    ch = pv.chart()
    bb = ch.GetBackgroundBrush()
    bb.SetColor(0,0,0)
    ch.SetBackgroundBrush(bb)

    pv = viewWidget.plotView()

    # 更改X轴颜色
    xAxis = ch.GetAxis(vtk.vtkAxis.BOTTOM)
    xAxis.GetPen().SetColorF(axisColor)

    # 更改Y轴颜色
    yAxis = ch.GetAxis(vtk.vtkAxis.LEFT)
    yAxis.GetPen().SetColorF(axisColor)

    # 更改X轴文字颜色
    xAxis = ch.GetAxis(vtk.vtkAxis.BOTTOM)
    xAxis.GetLabelProperties().SetColor(axisColor)

    # 更改Y轴文字颜色
    yAxis = ch.GetAxis(vtk.vtkAxis.LEFT)
    yAxis.GetLabelProperties().SetColor(axisColor)
    # 更改标题颜色
    ch.GetTitleProperties().SetColor(axisColor)
    plotChartNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotChartNode")
    viewNode.SetPlotChartNodeID(plotChartNode.GetID())
    tableNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode", "ECGTable")
    title = 'table'
    plotChartNode.SetName(title + ' chart')
    plotChartNode.SetTitle(title)
    plotChartNode.SetLegendVisibility(False)
    plotChartNode.SetGridVisibility(False)
    self.registe_plot(plot_name,tableNode,plotChartNode)
    return tableNode,plotChartNode,viewWidget

  #画一条直线
  def plot_single_line(self,plot_name,char_name,plot_data):
    columeX = []
    for i in range(len(plot_data)):
      columeX.append(i+1)
    
    datas = []
    datas.append(columeX)
    datas.append(plot_data)

    table_node = self.table_map[plot_name]
    chart_node = self.chart_map[plot_name]
    chart_node.SetTitle(char_name)
    util.updateTableFromArray(table_node, np.array(datas).T)
    table_node.GetTable().GetColumn(0).SetName("Time")
    table_node.GetTable().GetColumn(1).SetName("Intensity")

    plotSeriesNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotSeriesNode", "PlotSeriesNode")
    plotSeriesNode.SetAndObserveTableNodeID(table_node.GetID())
    plotSeriesNode.SetXColumnName("Time")
    plotSeriesNode.SetYColumnName("Intensity")
    plotSeriesNode.SetPlotType(plotSeriesNode.PlotTypeScatter)
    plotSeriesNode.SetAttribute("exclude","1")
    chart_node.AddAndObservePlotSeriesNodeID(plotSeriesNode.GetID())
    plotSeriesNode.SetColor(0, 1, 1.0)
    return chart_node
  
  def test_dynamic_plot(self,plotChartNode,range1=1):
    import math
    max_size = 100
    for ris in range(0,range1):
      array2D = []
      array1DIndex = []
      for i in range(max_size):
        array1DIndex.append(i)
      array2D.append(array1DIndex)

      array1D = []
      for i in range(ris):
        array1D.append(math.sin(i*180/3.1415926))
      if len(array1D)<max_size:
        array1D.extend([0] * (100 - len(array1D)))
      else:
        array1D = array1D[-100:]
      array2D.append(array1D)


      columnNames = []
      for i in range(len(array2D)):
        columnNames.append("I"+i.__str__())

      util.easyPlot(array2D,columnNames,"Table","t1",chatnode=plotChartNode)
      plotChartNode.Modified()
      slicer.app.processEvents()
      sleep(0.01)

  def add_test_plot(self):
    datas = []
    datas.append([1,2,3,4,5])
    datas.append([11,21,31,41,51])
    datas.append([12,22,32,42,52])
    datas.append([13,23,33,43,53])
    
    
    
    tableNode,plotChartNode,_ = util.getModuleLogic("JPlot").add_plot_widget_in_widget(self.ui.chart_widget)
    util.updateTableFromArray(tableNode, np.array(datas).T)
    tableNode.GetTable().GetColumn(0).SetName("Time")
    tableNode.GetTable().GetColumn(1).SetName("Voltage")
    tableNode.GetTable().GetColumn(2).SetName("Voltage2")
    tableNode.GetTable().GetColumn(3).SetName("Voltage3")

    plotSeriesNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotSeriesNode", "PlotSeriesNode")
    plotSeriesNode.SetAndObserveTableNodeID(tableNode.GetID())
    plotSeriesNode.SetXColumnName("Time")
    plotSeriesNode.SetYColumnName("Voltage")
    plotSeriesNode.SetPlotType(plotSeriesNode.PlotTypeScatter)
    plotChartNode.AddAndObservePlotSeriesNodeID(plotSeriesNode.GetID())

    plotSeriesNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotSeriesNode", "PlotSeriesNode")
    plotSeriesNode.SetAndObserveTableNodeID(tableNode.GetID())
    plotSeriesNode.SetXColumnName("Time")
    plotSeriesNode.SetYColumnName("Voltage2")
    plotSeriesNode.SetPlotType(plotSeriesNode.PlotTypeScatter)
    plotChartNode.AddAndObservePlotSeriesNodeID(plotSeriesNode.GetID())

    plotSeriesNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotSeriesNode", "PlotSeriesNode")
    plotSeriesNode.SetAndObserveTableNodeID(tableNode.GetID())
    plotSeriesNode.SetXColumnName("Time")
    plotSeriesNode.SetYColumnName("Voltage3")
    plotSeriesNode.SetPlotType(plotSeriesNode.PlotTypeScatter)
    plotChartNode.AddAndObservePlotSeriesNodeID(plotSeriesNode.GetID())
    return
 