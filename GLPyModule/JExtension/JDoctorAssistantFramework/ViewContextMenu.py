import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import slicer.util as util
    
from SubjectHierarchyPlugins import AbstractScriptedSubjectHierarchyPlugin

class ViewContextMenu(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Context menu example"
    self.parent.categories = ["Examples"]
    self.parent.contributors = ["Steve Pieper (Isomics, Inc.)"]
    util.singleShot(1000,self.onStartupCompleted)

  def onStartupCompleted(self):
    """register subject hierarchy plugin once app is initialized"""
    import SubjectHierarchyPlugins
    from ViewContextMenu import ViewContextMenuSubjectHierarchyPlugin
    scriptedPlugin = slicer.qSlicerSubjectHierarchyScriptedPlugin(None)
    scriptedPlugin.setPythonSource(ViewContextMenuSubjectHierarchyPlugin.filePath)
    pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler.instance()
    pluginHandler.registerPlugin(scriptedPlugin)
    print("ViewContextMenuSubjectHierarchyPlugin loaded")

class ViewContextMenuSubjectHierarchyPlugin(AbstractScriptedSubjectHierarchyPlugin):

  # Necessary static member to be able to set python source to scripted subject hierarchy plugin
  filePath = __file__
  list2D = []
  list3D = []
  list2DAnd3D = []
  viewNode = None
  is_show_label = True
  is_show_corner = False
  is_show_rule = False
  is_show_orimarker = False
  def __init__(self, scriptedPlugin):
    self.viewAction = qt.QAction("取消操作", scriptedPlugin)
    self.viewAction.objectName = "Menu2D"
    slicer.qSlicerSubjectHierarchyAbstractPlugin.setActionPosition(self.viewAction, slicer.qSlicerSubjectHierarchyAbstractPlugin.SectionNode+5)
    self.viewAction.connect("triggered()", self.onViewAction)
    self.list2D.append(self.viewAction)
    
    self.viewAction3D = qt.QAction("取消操作", scriptedPlugin)
    self.viewAction3D.objectName = "Menu3D"
    slicer.qSlicerSubjectHierarchyAbstractPlugin.setActionPosition(self.viewAction3D, slicer.qSlicerSubjectHierarchyAbstractPlugin.SectionNode+5)
    self.viewAction3D.connect("triggered()", self.onViewAction3D)
    self.list3D.append(self.viewAction3D)
    
    self.rotate3DAction = qt.QAction("旋转", scriptedPlugin)
    self.rotate3DAction.objectName = "rotate3DAction"
    slicer.qSlicerSubjectHierarchyAbstractPlugin.setActionPosition(self.viewAction3D, slicer.qSlicerSubjectHierarchyAbstractPlugin.SectionNode+5)
    self.rotate3DAction.connect("triggered()", self.onRotate3DAction)
    self.rotate3DAction.setCheckable(True)
    self.list3D.append(self.rotate3DAction)
    
    self.showLabelAction = qt.QAction("隐藏标签", scriptedPlugin)
    self.showLabelAction.objectName = "showLabelAction"
    slicer.qSlicerSubjectHierarchyAbstractPlugin.setActionPosition(self.viewAction3D, slicer.qSlicerSubjectHierarchyAbstractPlugin.SectionNode+5)
    self.showLabelAction.connect("triggered()", self.onShowLabelAction)
    self.list3D.append(self.showLabelAction)
    
    self.showOriMarkerAction = qt.QAction("显示方向标记", scriptedPlugin)
    self.showOriMarkerAction.objectName = "showOriMarkerAction"
    slicer.qSlicerSubjectHierarchyAbstractPlugin.setActionPosition(self.viewAction3D, slicer.qSlicerSubjectHierarchyAbstractPlugin.SectionNode+5)
    self.showOriMarkerAction.connect("triggered()", self.onShowOriMarkerAction)
    self.list3D.append(self.showOriMarkerAction)
    
    self.showCornerAction = qt.QAction("显示角标", scriptedPlugin)
    self.showCornerAction.objectName = "showCornerAction"
    slicer.qSlicerSubjectHierarchyAbstractPlugin.setActionPosition(self.viewAction, slicer.qSlicerSubjectHierarchyAbstractPlugin.SectionNode+5)
    self.showCornerAction.connect("triggered()", self.onShowCornerAction)
    self.list2D.append(self.showCornerAction)
    
    self.showRuleAction = qt.QAction("显示标尺", scriptedPlugin)
    self.showRuleAction.objectName = "showRuleAction"
    slicer.qSlicerSubjectHierarchyAbstractPlugin.setActionPosition(self.viewAction, slicer.qSlicerSubjectHierarchyAbstractPlugin.SectionNode+5)
    self.showRuleAction.connect("triggered()", self.onShowRuleAction)
    self.list2D.append(self.showRuleAction)
    return
    self.onShowLabelAction()
    self.onShowCornerAction()
    self.onShowOriMarkerAction()
    
    # self.saveVideoAction = qt.QAction("保存视频", scriptedPlugin)
    # self.saveVideoAction.objectName = "rotate3DAction"
    # slicer.qSlicerSubjectHierarchyAbstractPlugin.setActionPosition(self.viewAction3D, slicer.qSlicerSubjectHierarchyAbstractPlugin.SectionNode+5)
    # self.saveVideoAction.connect("triggered()", self.onsaveVideoAction)
    # self.list3D.append(self.saveVideoAction)
    
    
    # self.ScreenShotAction = qt.QAction("截图", scriptedPlugin)
    # self.ScreenShotAction.objectName = "screenshot"
    # slicer.qSlicerSubjectHierarchyAbstractPlugin.setActionPosition(self.viewAction3D, slicer.qSlicerSubjectHierarchyAbstractPlugin.SectionNode+5)
    # self.ScreenShotAction.connect("triggered()", self.OnScreenShotAction)
    # self.list2DAnd3D.append(self.ScreenShotAction)

  def onShowOriMarkerAction(self):
    self.is_show_orimarker = not self.is_show_orimarker
    txt = '显示方向标记'
    if self.is_show_orimarker:
      txt = '隐藏方向标记'
      util.show_3D_Orientation_Marker(2)
    else:
      util.show_3D_Orientation_Marker(0)
    self.showOriMarkerAction.setText(txt)

  def onShowLabelAction(self):
    self.is_show_label = not self.is_show_label
    txt = '显示标签'
    if self.is_show_label:
      txt = '隐藏标签'
      util.send_event_str(util.DisplayModelAlias, '')
    else:
      util.send_event_str(util.HideModelAlias, '')
    self.showLabelAction.setText(txt)
    pass

  def onShowCornerAction(self):
    self.is_show_corner = not self.is_show_corner
    txt = '显示角标'
    if self.is_show_corner:
      txt = '隐藏角标'
      util.getModuleWidget("JAnnotation").show_or_hide_info(True)
    else:
      util.getModuleWidget("JAnnotation").show_or_hide_info(False)
    self.showCornerAction.setText(txt)
    pass

  def onShowRuleAction(self):
    self.is_show_rule = not self.is_show_rule
    txt = '显示标尺'
    if self.is_show_rule:
      txt = '隐藏标尺'
      for sliceNode in slicer.util.getNodesByClass('vtkMRMLSliceNode'):
        sliceNode.SetRulerType(1)
    else:
      for sliceNode in slicer.util.getNodesByClass('vtkMRMLSliceNode'):
        sliceNode.SetRulerType(0)
    self.showRuleAction.setText(txt)
    pass

  def viewContextMenuActions(self):
    return self.list2D+self.list3D+self.list2DAnd3D

  def showViewContextMenuActionsForItem(self, itemID, eventData=None):
    # We can decide here if we want to show this action based on the itemID or eventData (ViewNodeID, ...).
    print(f"itemID: {itemID}")
    print(f"eventData: {eventData}")
    if not "ViewNodeID" in eventData:
        self.viewAction.visible = False
    self.viewNode = util.GetNodeByID(eventData["ViewNodeID"])
    
    interactionNode = self.viewNode.GetInteractionNode()
    if not interactionNode:
        self.viewAction.visible = False
    
    if len(eventData["ViewNodeID"])>len("vtkMRMLSliceNode") and eventData["ViewNodeID"][:len("vtkMRMLSliceNode")]=="vtkMRMLSliceNode":
        for action in self.list2D:
            action.visible = True
        for action in self.list3D:
            action.visible = False
    else:
        for action in self.list2D:
            action.visible = False
        for action in self.list3D:
            action.visible = True
            
    for action in self.list2DAnd3D:
            action.visible = True

  def onViewAction(self):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setActiveEffectByName(None)

  def onViewAction3D(self):
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      segmentEditorWidget.setActiveEffectByName(None)

  def onRotate3DAction(self):
     for viewIndex in range(slicer.app.layoutManager().threeDViewCount):
      slicer.app.layoutManager().threeDWidget(viewIndex).threeDController().spinView(self.rotate3DAction.isChecked())

  def onsaveVideoAction(self):
      from datetime import datetime
      import subprocess
      import os

      now = datetime.now()
      # 将当前日期和时间格式化为年月日时分秒
      timestamp = now.strftime('%Y-%m-%d-%H-%M-%S')
      dialog = qt.QFileDialog(util.mainWindow(), "Save Text File")
      dialog.setAcceptMode(qt.QFileDialog.AcceptSave)
      dialog.setNameFilters(["Video Files (*.mp4)", "All Files (*)"])
      dialog.selectFile(timestamp+".mp4")
      if dialog.exec_() == qt.QFileDialog.Accepted:
          fileName = dialog.selectedFiles()[0]  # 获取选择的文件路径
      else:
        return
        
        
      # 获取当前文件的绝对路径
      current_file_path = os.path.dirname(os.path.abspath(__file__))
      
      sc = util.getModuleWidget("ScreenCapture")
      sc.logic.ffmpegDownload()
      sc.videoLengthSliderWidget.value = 15
      sc.outputTypeWidget.setCurrentIndex(1)
      
      res = util.messageBox(f"确定将视频保存到 [ {fileName} ] 吗？",windowTitle=util.tr("提示"))
      if res == 0:
        return
      folder_path = os.path.dirname(fileName)
      file_name = os.path.basename(fileName)
      sc.outputDirSelector.setCurrentPath(folder_path)
      sc.videoFileNameWidget.setText(file_name)
      ffpath = os.path.join(current_file_path,"Resources/ffmpeg/bin/ffmpeg.exe").replace("\\","/")
      sc.ffmpegPathSelector.setCurrentPath(ffpath)
      sc.onCaptureButton()
      
      #os.startfile(fileName)
      
  def OnScreenShotAction(self):
    if not self.viewNode:
        return 
    fileName = qt.QFileDialog.getSaveFileName(None, ("保存截图"),
                            "/screenshot.png",
                            ("截图 (*.png)"))
    if fileName == "":
      util.messageBox2("请选择一个文件地址")
      return
    
    import ScreenCapture
    cap = ScreenCapture.ScreenCaptureLogic()
    view = cap.viewFromNode(self.viewNode)
    cap.captureImageFromView(view, fileName)