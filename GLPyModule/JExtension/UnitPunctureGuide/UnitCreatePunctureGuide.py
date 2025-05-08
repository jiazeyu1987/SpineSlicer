import slicer,qt,vtk,ctk
import os
import slicer.util as util
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from Base.JBaseExtension import JBaseExtensionWidget
import UnitPunctureGuideLib.G_UnitPunctureGuide as G
from FrameworkLib.Declaration import Declaration
#
# UnitCreatePunctureGuide
#

class NoteDialog(qt.QDialog,ScriptedLoadableModuleWidget):
  info_list = []
  def __init__(self, parent=None):
    super(NoteDialog, self).__init__()
    self.setWindowFlag(qt.Qt.FramelessWindowHint)
    self.setAttribute(qt.Qt.WA_TranslucentBackground)  # 使窗口透明
    
    # 设置对话框为全屏
    #self.showFullScreen()
    self.module_path = os.path.dirname(slicer.util.modulePath("UnitCreatePunctureGuide"))
    print(self.module_path)
    uiWidget = slicer.util.loadUI(self.module_path + '/Resources/UI/NoteDialog.ui')
    slicer.util.addWidget2(self, uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)
    self.ui.btnClose.connect("clicked()",self.reject)
    self.ui.btnCanfirm.connect("clicked()",self.on_confirm)

  def set_info(self, info_list):
    self.info_list = info_list

  def on_confirm(self):
    info = self.ui.lblInfo.text
    if info == "":
      util.showWarningText(util.tr("请输入一个用于上传图片的标签"))
      return
    self.info_list.append(info)
    self.accept()
    pass

class Remote3DPrinter(qt.QDialog,ScriptedLoadableModuleWidget):
  volume = 0
  def __init__(self, parent=None):
    super(Remote3DPrinter, self).__init__()
    self.setWindowFlag(qt.Qt.FramelessWindowHint)
    self.setAttribute(qt.Qt.WA_TranslucentBackground)  # 使窗口透明
    self.module_path = os.path.dirname(slicer.util.modulePath("UnitCreatePunctureGuide"))
    print(self.module_path)
    uiWidget = slicer.util.loadUI(self.module_path + '/Resources/UI/Remote3DPrinter.ui')
    slicer.util.addWidget2(self, uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)
    self.ui.btnClose.connect("clicked()",self.accept)

  def setInfo(self, volume):
    self.volume = volume
    self.ui.lblCover.hide()
    regex = qt.QRegExp("^1[3-9]\d{9}$")
    validator = qt.QRegExpValidator(regex, self.ui.lineEdit_2)
    self.ui.lineEdit_2.setValidator(validator)
    
    regex = qt.QRegExp("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    validator = qt.QRegExpValidator(regex, self.ui.lineEdit_3)
    self.ui.lineEdit_3.setValidator(validator)
    
    regex = qt.QRegExp("^[a-zA-Z0-9\u4e00-\u9fa5]+$")
    validator = qt.QRegExpValidator(regex, self.ui.lineEdit)
    self.ui.lineEdit.setValidator(validator)
    
    qt.QWidget.setTabOrder(self.ui.lineEdit, self.ui.lineEdit_2)
    qt.QWidget.setTabOrder(self.ui.lineEdit_2, self.ui.lineEdit_3)
    qt.QWidget.setTabOrder(self.ui.lineEdit_3, self.ui.textEdit)
    qt.QWidget.setTabOrder(self.ui.textEdit, self.ui.comboBox)
    qt.QWidget.setTabOrder(self.ui.comboBox, self.ui.pushButton)
    qt.QWidget.setTabOrder(self.ui.pushButton, self.ui.lineEdit)
    
    
      
      
    self.ui.comboBox.connect("currentIndexChanged(int)",self.on_ma_changed)
    if self.ui.comboBox.currentIndex == 0:
      x = 1.3
    elif  self.ui.comboBox.currentIndex == 1:
      x = 2.5
    self.module_path = os.path.dirname(slicer.util.modulePath("UnitCreatePunctureGuide"))  
    contact_path = self.module_path + '/Resources/UI/tmp_screenshot.png'
    slicer.util.addPictureFromFile(contact_path,self.ui.lbl_img,size_width=300,size_height=300)

    self.ui.label_6.setText(f"导板体积：{volume} cm³")
    self.ui.label_9.setText(f"{round(x*volume,1)}元")
    
    user_real_name = util.get_cache_from_PAAA("user_real_name","")
    user_telephone = util.get_cache_from_PAAA("user_telephone","")
    user_email = util.get_from_PAAA("user_email","")
    user_address = util.get_cache_from_PAAA("user_address","")
    self.ui.lineEdit.setText(user_real_name)
    self.ui.lineEdit_2.setText(user_telephone)
    self.ui.lineEdit_3.setText(user_email)
    self.ui.textEdit.setPlainText(user_address)
    
    self.ui.lineEdit.connect('textChanged(QString)', lambda val:util.save_cache_to_PAAA("user_real_name",val))
    self.ui.lineEdit_2.connect('textChanged(QString)', lambda val:util.save_cache_to_PAAA("user_telephone",val))
    self.ui.lineEdit_3.connect('textChanged(QString)', lambda val:util.save_cache_to_PAAA("user_email",val))
    self.ui.textEdit.connect('textChanged()', lambda :util.save_cache_to_PAAA("user_address",self.ui.textEdit.toPlainText()))
    self.ui.pushButton.connect('clicked()', lambda:self.on_apply(volume,round(x*volume,1)))
    
    
  

  def on_ma_changed(self, index):
    if index == 0:
      x = 1.3
    elif  index == 1:
      x = 2.5
    self.ui.label_9.setText(f"{round(x*self.volume,1)}元")
    
    

    
  def on_apply(self, volume, price):
    user_real_name = self.ui.lineEdit.text
    user_telephone = self.ui.lineEdit_2.text
    user_email = self.ui.lineEdit_3.text
    user_address = self.ui.textEdit.toPlainText()
    material = self.ui.comboBox.currentText
    if not self.is_valid_chinese_mobile(user_telephone):
      util.showWarningText(f"当前电话号码 {user_telephone} 不符合要求")
      return
    if not self.is_valid_email(user_email):
      util.showWarningText(f"当前邮箱格式 {user_email} 不符合要求")
      return
    #str1 = user_real_name+"\n"+user_telephone+"\n"+user_email+"\n"+user_address+"\n"+material+"\n"+volume.__str__()+"\n"+price.__str__()
    #util.showWarningText(str1)
    json1 = {}
    json1['user_real_name'] = user_real_name
    json1['user_telephone'] = user_telephone
    json1['user_email'] = user_email
    json1['user_address'] = user_address
    json1['material'] = material
    json1['volume'] = volume
    json1['price'] = price
    
    tmp_path = self.resourcePath('UI/tmp.stl')
    util.saveNode(util.getFirstNodeByName("导板"),tmp_path)
    self.ui.lblCover.show()
    util.processEvents()
    flag,val=util.httplib.httppost("/system/dept/printer3d_order",json1,timeout=3,silent=False,file_path=tmp_path)
    if flag:
      dlg.accept()
      util.showWarningText("请求已提交，可以联系售后来查看当前进度")
      self.ui.lblCover.hide()
    else:
      if val == 413:
        util.showWarningText("模型太大，请单独联系售后人员")
      else:
        util.showWarningText("请求失败,请查看网络连接:"+val.__str__())
      self.ui.lblCover.hide()

class UnitCreatePunctureGuide(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UnitCreatePunctureGuide"  # TODO: make this more human readable by adding spaces
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
# UnitCreatePunctureGuideWidget
#

class UnitCreatePunctureGuideWidget(JBaseExtensionWidget):
  printer_x = 122
  printer_y = 122
  printer_z = 161
  max_export_times = 5
  max_png_export_times = 5
  def setup(self):
    super().setup()
    
  def init_ui(self):
    self.ui.btnMake.connect('clicked()',self.create_puncture)
    self.ui.btnExport.connect('clicked()',self.export_puncture)
    
    
    self.ui.btnChoosePlane.connect('toggled(bool)',self.on_choose_plane)
    self.ui.btnStartCut.connect('clicked()',self.on_start_cut)
    self.ui.btnRedExport.connect('clicked()',self.on_red_export)
    self.ui.btnGreenExport.connect('clicked()',self.on_blue_export)
    self.ui.btnExportPng.connect('clicked()',self.on_png_export)
    self.ui.brain_segment_button.connect('clicked()', self.on_brain_segment_analyse)
    
    self.ui.btnPrint.connect('clicked()',self.on_remote)
    self.TagMaps[util.ResetVersion] = slicer.mrmlScene.AddObserver(util.ResetVersion, self.OnResetVersion)
    self.TagMaps[321] = slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeRemovedEvent, self.OnMainNodeRemoved2)
    
    self.ui.btnRedExport.setEnabled(False)
    self.ui.btnGreenExport.setEnabled(False)
    self.ui.btnStartCut.setEnabled(False)
    self.ui.label_2.hide()
    self.ui.btnPrint.hide()
  
  def on_brain_segment_analyse(self):
    print("brain_segment_button")
    # brain_segment = util.getFirstNodeByName("脑功能区")
    # if not brain_segment:
    #   util.showWaitText("请先通过【加载数据】导入T1数据然后在【三维重建】中分割脑区")
    #   return
    util.getModuleWidget("BrainSegmentAnalysis").show()
    
    
  def on_png_export(self):
    import time
    export_times = self.check_png_export_times()
    if export_times == -1:
      return
    info_list = []
    dialog = NoteDialog(slicer.util.mainWindow())
    dialog.set_info(info_list)  
    result = dialog.exec_()
    if result == 0:
      return
    print(info_list)
    #改变3D窗口背景颜色为黑色
    view = slicer.app.layoutManager().threeDWidget(0).threeDView()
    view.mrmlViewNode().SetBackgroundColor(0,0,0)
    view.mrmlViewNode().SetBackgroundColor2(0,0,0)
    view.forceRender()
    # Capture RGBA image

    #重置窗口
    util.reinit(ori=True)
    util.trigger_view_tool("")
    util.forceRenderAllViews()
    renderWindow = view.renderWindow()

    viewNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLViewNode")
    cameraNode = slicer.modules.cameras.logic().GetViewActiveCameraNode(viewNode)
    camera = cameraNode.GetCamera()

    # 设置新的相机位置
    camera.Dolly(2)

    # 通知 Slicer 相机已经更新
    cameraNode.Modified()
    view.renderWindow().Render()
    slicer.app.layoutManager().threeDWidget(0).threeDView().resetFocalPoint()
    
    slicerhome = util.mainWindow().slicerhome()
    for index in [1,3,5]:
      view.lookFromAxis(index)
      path = f"{slicerhome}/bin/tmp/screenshot{index}.jpg"
      # renderWindow.SetAlphaBitPlanes(1)
      # wti = vtk.vtkWindowToImageFilter()
      # wti.SetInputBufferTypeToRGBA()
      # wti.SetInput(renderWindow)
      # writer = vtk.vtkPNGWriter()
      # print(path)
      # writer.SetFileName(path)
      # writer.SetInputConnection(wti.GetOutputPort())
      # writer.Write()
      # 官方提供的方法截图后为透明背景，使用下面方法
      view.renderWindow().Render()    
      # 保存当前3D窗口截图
      screenshotWidth = 800
      screenshot = view.grab()  # 获取当前窗口的截图
      originalWidth = screenshot.width()
      originalHeight = screenshot.height()
      aspectRatio = originalHeight / originalWidth
      screenshotHeight = int(screenshotWidth * aspectRatio)    
      # 调整截图大小，保持宽度为400并保持等比缩放
      resizedScreenshot = screenshot.scaled(screenshotWidth, screenshotHeight, qt.Qt.KeepAspectRatio)

      resizedScreenshot.save(path)  # 保存截图文件
    
    # 准备多个文件和数据
    files = [
        ('images', ('image1.jpg', open(f"{slicerhome}/bin/tmp/screenshot{1}.jpg", 'rb'), 'image/jpeg')),
        ('images', ('image2.jpg', open(f"{slicerhome}/bin/tmp/screenshot{3}.jpg", 'rb'), 'image/jpeg')),
        ('images', ('image3.jpg', open(f"{slicerhome}/bin/tmp/screenshot{5}.jpg", 'rb'), 'image/jpeg')),
        # 添加更多图片如果需要
    ]
    data = {
        'names': ['image1.jpg',' image2.jpg',' image3.jpg'] , # 发送图片名称列表，与文件顺序对应
        'notes': info_list[0]
    }
    isSucceed,val = util.httplib.httpuploads("/system/user/upload_picture_list",files=files,data=data)
    if isSucceed:
      util.save_cache_to_PAAA("puncture_png_export_time",export_times+1)
      util.showWarningText("上传成功")
    else:
      util.showWarningText("上传失败")

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def OnMainNodeRemoved2(self, caller, event,calldata):
    if calldata.GetAttribute("alias_name") == "红色导板":
      self.ui.btnRedExport.setEnabled(False)
    if calldata.GetAttribute("alias_name") == "绿色导板":
      self.ui.btnGreenExport.setEnabled(False)
    if calldata.GetName() == "CutPuncturePlane":
      self.ui.btnStartCut.setEnabled(False)
      
  
  
        
  def on_red_export(self):
    node = util.getFirstNodeByName("RedPunctureMask")
    if not node:
      util.showWarningText("请先创建红色导板")
      return
    dialog = Declaration(slicer.util.mainWindow())
    result = dialog.exec_()
    if result == 0:
      return
    save_path = util.get_common_save_path("stl")
    fileName = qt.QFileDialog.getSaveFileName(None, ("保存文件"),
                              f"{save_path}/red_model.stl",
                              ("模型 (*.stl)"))
    if fileName == "":
      util.showWarningText("请选择一个文件地址用来存储穿刺导板")
      return
    slicer.util.saveNode(node,fileName)
    util.send_event_str(util.ProgressValue,"100")
    util.showWarningText("模型导出成功")

  

  def on_blue_export(self):
    node = util.getFirstNodeByName("GreenPunctureMask")
    if not node:
      util.showWarningText("请先创建绿色导板")
      return
    dialog = Declaration(slicer.util.mainWindow())
    result = dialog.exec_()
    if result == 0:
      return
    save_path = util.get_common_save_path("stl")
    fileName = qt.QFileDialog.getSaveFileName(None, ("保存文件"),
                              f"{save_path}/green_model.stl",
                              ("模型 (*.stl)"))
    if fileName == "":
      util.showWarningText("请选择一个文件地址用来存储穿刺导板")
      return
    slicer.util.saveNode(node,fileName)
    util.send_event_str(util.ProgressValue,"100")
    util.showWarningText("模型导出成功")
  
  def on_start_cut(self):
    mask_node = util.getFirstNodeByName("导板")
    if mask_node is None:
      util.showWaitText("请先创建导板")
      return
    util.color_unit_list.half_opacity()
    planenode = util.getFirstNodeByName("CutPuncturePlane")
    util.RemoveNodeByName("RedPunctureMask")
    util.RemoveNodeByName("GreenPunctureMask")
    a_node = util.AddNewNodeByClass(util.vtkMRMLModelNode)
    b_node = util.AddNewNodeByClass(util.vtkMRMLModelNode)
    a_node.SetName("RedPunctureMask")
    a_node.SetAttribute("alias_name","红色导板")
    b_node.SetName("GreenPunctureMask")
    b_node.SetAttribute("alias_name","绿色导板")
    dynamicModelerNode = util.CreateNodeByClass("vtkMRMLDynamicModelerNode")
    dynamicModelerNode.SetToolName("Plane cut")
    dynamicModelerNode.SetNodeReferenceID("PlaneCut.OutputPositiveModel",a_node.GetID())
    dynamicModelerNode.SetNodeReferenceID("PlaneCut.OutputNegativeModel",b_node.GetID())
    dynamicModelerNode.SetNodeReferenceID("PlaneCut.InputPlane",planenode.GetID())
    dynamicModelerNode.SetNodeReferenceID("PlaneCut.InputModel",mask_node.GetID())
    util.GetDisplayNode(a_node).SetColor([1,0,0])
    util.GetDisplayNode(b_node).SetColor([0,1,0])
    util.AddNode(dynamicModelerNode)
    util.color_unit_list.add_item(a_node, 3)
    util.color_unit_list.add_item(b_node, 3)
    util.tips_unit_list.add_item(a_node, 3)
    util.tips_unit_list.add_item(b_node, 3)
    self.ui.btnRedExport.setEnabled(True)
    self.ui.btnGreenExport.setEnabled(True)
    util.HideNode(planenode)

  def on_choose_plane(self,val):
    
    if val:
      entry_node = util.getFirstNodeByName("EntryPoint")
      if not entry_node:
        util.showWarningText("请先创建一个通道")
        self.ui.btnChoosePlane.setChecked(False)
        return
      util.RemoveNodeByName("PlanePointX12321")
      plane_point = util.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
      plane_point.SetName("PlanePointX12321")
      
      display_node = util.GetDisplayNode(plane_point)
      display_node.SetPointLabelsVisibility(False)
      util.HideNode(plane_point)
      interactionNode = slicer.app.applicationLogic().GetInteractionNode()
      selectionNode = slicer.app.applicationLogic().GetSelectionNode()
      selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
      selectionNode.SetActivePlaceNodeID(plane_point.GetID())
      interactionNode.SetCurrentInteractionMode(interactionNode.Place)
      plane_point.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, self.on_plane_point_modified)
      plane_point.AddObserver(slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent, self.on_plane_point_defined)
  
  def on_plane_point_defined(self,a,b):
    self.ui.btnStartCut.setEnabled(True)
  
  def on_plane_point_modified(self,caller,event):
    entry_node = util.getFirstNodeByName("EntryPoint")
    if not entry_node:
      return
    fiber_unit_id = entry_node.GetAttribute("fiber_unit_id")
    target_node = util.getFirstNodeByNameByAttribute("TargetPoint","fiber_unit_id",fiber_unit_id.__str__())
    target_point_world = util.get_world_position(target_node)
    entry_point_world = util.get_world_position(entry_node)
    place_point_world = util.get_world_position(caller)
    self.ui.btnChoosePlane.setChecked(False)
    self.create_plane_by_three_point(caller,[target_point_world,entry_point_world,place_point_world],"CutPuncturePlane")
    
  
  def create_plane_by_three_point(self,node,pointlist,plane_name):
    
    import numpy as np
    if len(pointlist) < 3:
      print("至少需要3个点来创建平面")
      return
    
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
    
    planeNode = util.EnsureFirstNodeByNameByClass(plane_name,"vtkMRMLMarkupsPlaneNode")
    util.ShowNode(planeNode)
    selectionNode = slicer.app.applicationLogic().GetSelectionNode()
    selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
    selectionNode.SetActivePlaceNodeID(node.GetID())
    planeNode.SetSize(300,300)
    util.GetDisplayNode(planeNode).SetNormalVisibility(False)
    util.GetDisplayNode(planeNode).SetPropertiesLabelVisibility(False)
    planeNode.SetOrigin(origin[0],origin[1],origin[2])
    planeNode.SetNormal(normal[0],normal[1],normal[2])
    
    planeNode.SetNthControlPointVisibility(0,False)

  def OnResetVersion(self,_a,_b):
    pass

  def rotate_fiber_model_to_vector(self,model_node,m_PointInput,m_PointTarget,length):
    import numpy as np
    length = length/2
    half_vector = (np.array(m_PointInput) - np.array(m_PointTarget))/2
    half_vector_len = np.sqrt(half_vector[0]*half_vector[0]+half_vector[1]*half_vector[1]+half_vector[2]*half_vector[2])

    transformToParentMatrix = vtk.vtkMatrix4x4()

    rotationVector_Local = np.array([0,0,0])
    vector1 = np.array(m_PointInput) - np.array(m_PointTarget)
    vector0 = np.array([0,-1,0])
    angle = vtk.vtkMath.DegreesFromRadians(vtk.vtkMath.AngleBetweenVectors(vector0,vector1))
    vtk.vtkMath.Cross(vector0, vector1, rotationVector_Local)
    handleToParentMatrix=vtk.vtkTransform()
    handleToParentMatrix.PostMultiply()
    handleToParentMatrix.Translate(-m_PointTarget[0], -m_PointTarget[1], -m_PointTarget[2])
    handleToParentMatrix.RotateWXYZ(angle, rotationVector_Local)
    handleToParentMatrix.Translate(m_PointTarget[0]+half_vector[0]*length/half_vector_len,m_PointTarget[1]+half_vector[1]*length/half_vector_len,m_PointTarget[2]+half_vector[2]*length/half_vector_len)
    transformToParentMatrix.DeepCopy(handleToParentMatrix.GetMatrix())

    transform_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
    transform_node.SetMatrixTransformToParent(transformToParentMatrix)
    model_node.SetAndObserveTransformNodeID(transform_node.GetID())
    model_node.HardenTransform()
    
    
  def only_show(self):
    modelnode = util.getFirstNodeByName("导板")
    nodes = util.getNodesByClass(util.vtkMRMLScalarVolumeNode)+util.getNodesByClass(util.vtkMRMLModelNode)+util.getNodesByClass(util.vtkMRMLMarkupsNode)+util.getNodesByClass(util.vtkMRMLSegmentationNode)
    list1 = {}
    for node in nodes:
      if node.IsA("vtkMRMLSegmentationNode"):
        displayNode = util.GetDisplayNode(node)
        if displayNode:
          sid = util.GetNthSegmentID(node,0)
          vis = displayNode.GetSegmentVisibility(sid)
      else:
        displayNode = util.GetDisplayNode(node)
        if displayNode:
          vis = displayNode.GetVisibility()
      
      if vis:
        list1[node.GetID()] = vis
      util.HideNode(node)
    util.ShowNode(modelnode)
    
    status = util.color_unit_list.get_node_status(modelnode)
    util.color_unit_list.set_node_status(modelnode,0)
    
    layoutManager = slicer.app.layoutManager()
    threeDWidget = layoutManager.threeDWidget(0)
    threeDView = threeDWidget.threeDView()
    threeDView.resetFocalPoint()  # reset the 3D view cube size and center it
    threeDView.resetCamera()  # reset camera zoom
    threeDView.rotateToViewAxis(3)  # look from anterior direction
    
    image_path = self.resourcePath('UI/tmp_screenshot.png')
    threeDView = layoutManager.threeDWidget(0).threeDView()
    import ScreenCapture
    cap = ScreenCapture.ScreenCaptureLogic()
    cap.captureImageFromView(threeDView, image_path)
    
    
    util.singleShot(0,lambda:self.revert_show(list1,modelnode,status))
  
  def revert_show(self,list1,modelnode,status):
    for id in list1:
      node = util.GetNodeByID(id)
      util.ShowNode(node)
      layoutManager = slicer.app.layoutManager()
      threeDWidget = layoutManager.threeDWidget(0)
      threeDView = threeDWidget.threeDView()
      threeDView.resetFocalPoint()  # reset the 3D view cube size and center it
      threeDView.resetCamera()  # reset camera zoom
      threeDView.rotateToViewAxis(3)  # look from anterior direction
    
    util.color_unit_list.set_node_status(modelnode,status)
  
  def get_model_volume(self,node):
    polyData = node.GetPolyData()
    # 创建vtkMassProperties对象
    massProperties = vtk.vtkMassProperties()
    massProperties.SetInputData(polyData)
    massProperties.Update()
    # 获取模型的表面积和体积
    volume_cm3 = massProperties.GetVolume()
    volume_cm3 = round(volume_cm3/1000,2)
    return volume_cm3
  
  def is_valid_email(self,email):
    import re
    """检测是否是有效的电子邮箱地址"""
    pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    return pattern.match(email) is not None
  
  
  def is_valid_chinese_mobile(self,phone_number):
        import re
        """检测是否是有效的中国移动电话号码"""
        pattern = re.compile(r"^1[3456789]\d{9}$")
        return pattern.match(phone_number) is not None
      
  def set_validator(self,uiwidget,ui,volume,dlg):
    ui.tabWidget.tabBar().hide()
    ui.tabWidget.setCurrentIndex(0)
    regex = qt.QRegExp("^1[3-9]\d{9}$")
    validator = qt.QRegExpValidator(regex, ui.lineEdit_2)
    ui.lineEdit_2.setValidator(validator)
    
    regex = qt.QRegExp("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    validator = qt.QRegExpValidator(regex, ui.lineEdit_3)
    ui.lineEdit_3.setValidator(validator)
    
    regex = qt.QRegExp("^[a-zA-Z0-9\u4e00-\u9fa5]+$")
    validator = qt.QRegExpValidator(regex, ui.lineEdit)
    ui.lineEdit.setValidator(validator)
    
    qt.QWidget.setTabOrder(ui.lineEdit, ui.lineEdit_2)
    qt.QWidget.setTabOrder(ui.lineEdit_2, ui.lineEdit_3)
    qt.QWidget.setTabOrder(ui.lineEdit_3, ui.textEdit)
    qt.QWidget.setTabOrder(ui.textEdit, ui.comboBox)
    qt.QWidget.setTabOrder(ui.comboBox, ui.pushButton)
    qt.QWidget.setTabOrder(ui.pushButton, ui.lineEdit)
    
    
      
    if ui.comboBox.currentIndex == 0:
      x = 1.3
    elif  ui.comboBox.currentIndex == 1:
      x = 2.5
      
    
    ui.label_6.setText(f"导板体积：{volume} cm³")
    ui.label_9.setText(f"{round(x*volume,1)}元")
    
    contact_path = self.resourcePath('UI/tmp_screenshot.png')
    slicer.util.addPictureFromFile(contact_path,ui.label_5,size_width=400,size_height=400)
    
    user_real_name = util.get_cache_from_PAAA("user_real_name","")
    user_telephone = util.get_cache_from_PAAA("user_telephone","")
    user_email = util.get_from_PAAA("user_email","")
    user_address = util.get_cache_from_PAAA("user_address","")
    ui.lineEdit.setText(user_real_name)
    ui.lineEdit_2.setText(user_telephone)
    ui.lineEdit_3.setText(user_email)
    ui.textEdit.setPlainText(user_address)
    
    ui.lineEdit.connect('textChanged(QString)', lambda val:util.save_cache_to_PAAA("user_real_name",val))
    ui.lineEdit_2.connect('textChanged(QString)', lambda val:util.save_cache_to_PAAA("user_telephone",val))
    ui.lineEdit_3.connect('textChanged(QString)', lambda val:util.save_cache_to_PAAA("user_email",val))
    ui.textEdit.connect('textChanged()', lambda :util.save_cache_to_PAAA("user_address",ui.textEdit.toPlainText()))
    ui.pushButton.connect('clicked()', lambda:on_apply(volume,round(x*volume,1),dlg))
  
  def on_printer_changed(self, index):
    print(self.ui.comboBox.currentText)
    if self.ui.comboBox.currentText == "小鲁班":
      self.printer_x = 122
      self.printer_y = 122
      self.printer_z = 161
    if self.ui.comboBox.currentText == "拓竹2000":
      self.printer_x = 300
      self.printer_y = 300
      self.printer_z = 400
    if self.ui.comboBox.currentText == "土星":
      self.printer_x = 400
      self.printer_y = 400
      self.printer_z = 600
  
  def on_remote(self):
    modelnode = util.getFirstNodeByName("导板")
    if not modelnode:
      return
    volume = self.get_model_volume(modelnode)
    if not modelnode:
      util.showWarningText("请先创建导板")
      return
    self.only_show()
    dialog = Remote3DPrinter(slicer.util.mainWindow())
    dialog.setInfo(volume)    
    dialog.exec_()
  
  def on_purchase_3dprinter(self):
    print("on_purchase_3dprinter")
    dlg = qt.QDialog()
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/Purchase.ui'))
    ui = slicer.util.childWidgetVariables(uiWidget)
    
    contact_path = self.resourcePath('Data/purchase1.png')
    slicer.util.addPictureFromFile(contact_path,ui.label_2,size_width=381,size_height=381)
    util.getModuleWidget("JMessageBox").on_popup_ui_dialog("购买打印机",uiWidget, 400, 510)
  def on_purchase_head_model(self):
    dlg = qt.QDialog()
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/Purchase.ui'))
    ui = slicer.util.childWidgetVariables(uiWidget)
    
    contact_path = self.resourcePath('Data/purchase2.png')
    slicer.util.addPictureFromFile(contact_path,ui.label_2,size_width=381,size_height=381)
    util.getModuleWidget("JMessageBox").on_popup_ui_dialog("购买头模",uiWidget, 400, 510)
  
  def export_puncture(self):
    node = util.getFirstNodeByName("导板")
    if not node:
      util.showWarningText("请先创建导板")
      return
    export_times = self.check_export_times()
    if export_times == -1:
      return
    dialog = Declaration(slicer.util.mainWindow())
    result = dialog.exec_()
    if result == 0:
      return
    save_path = util.get_common_save_path("stl")
    fileName = qt.QFileDialog.getSaveFileName(None, ("保存文件"),
                              f"{save_path}/model.stl",
                              ("模型 (*.stl)"))
    if fileName == "":
      util.showWarningText("请选择一个文件地址用来存储穿刺导板")
      return
    slicer.util.saveNode(node,fileName)
    util.send_event_str(util.ProgressValue,"100")
    util.getModuleWidget("UnitScore").do_export_stl = True

    util.save_cache_to_PAAA("puncture_export_time",export_times+1)

    res = util.messageBox("模型导出成功, 是否保存此次分析？")
    if res == 0:
      return
    util.send_event_str(util.SaveSolution)

  def check_export_times(self):
    from FrameworkLib.datas import fdb
    export_times = int(util.get_cache_from_PAAA("puncture_export_time","0"))
    if export_times < self.max_export_times:
      return export_times
    viplevel = fdb.get_user_viplevel(util.username)
    if viplevel != 1:
      util.showWarningText("当前功能需要VIP")
      is_guest = (util.username == "游客")
      util.vip_jump(is_guest)
      return -1
    pass

  def check_png_export_times(self):
    from FrameworkLib.datas import fdb
    export_times = int(util.get_cache_from_PAAA("puncture_png_export_time","0"))
    if export_times < self.max_png_export_times:
      return export_times
    viplevel = fdb.get_user_viplevel(util.username)
    if viplevel != 1:
      util.showWarningText("当前功能需要VIP")
      is_guest = (util.username == "游客")
      util.vip_jump(is_guest)
      return -1
    pass

  def get_volume(self):
    volume = util.getFirstNodeByClassByAttribute(util.vtkMRMLScalarVolumeNode,"main_node","1")
    return volume
  
  def create_puncture(self):
    volume_node = self.get_volume()
    MaskSegmentation = util.getFirstNodeByName("面具")
    self.on_bind(volume_node,MaskSegmentation)
    
  def on_bind(self,volume_node,MaskSegmentation):
    util.RemoveNodeByName("导板")
    full_head_segment = util.getFirstNodeByName("FullHeadSegmentationNode")
    if not full_head_segment:
      util.messageBox2("请先分割面具")
      return
    util.send_event_str(util.ProgressStart,"正在生成导板")
    util.send_event_str(util.ProgressValue,5)
    
    logic = util.getModuleWidget("UnitCreateChannel")
    fibers = []
    if logic:
      fibers = logic.generate_final_fiber_model()
    
    
    # if len(fibers)==0:
    #   print("请创建至少一个通道")
    #   util.send_event_str(util.ProgressValue,100)
    #   return
    util.send_event_str(util.ProgressValue,25)
    full_head_model = util.convert_segment_to_model(full_head_segment)
    full_head_model.SetName("FullHeadModel")
    CombineModelsLogic = util.getModuleLogic("CombineModels")
    for modelNode in fibers:
      if CombineModelsLogic:
        CombineModelsLogic.process(modelNode,full_head_model,modelNode,'difference')
    util.send_event_str(util.ProgressValue,35)
    
    '''
      如果是普通光纤,那么要在皮肤上给光纤打洞
    '''
    for modelNode in fibers:
      origin_node_id = modelNode.GetAttribute("origin_node_id")
      if origin_node_id:
        util.GetDisplayNode(modelNode).SetColor([230/255,230/255,77/255])
        origin_node = util.GetNodeByID(origin_node_id)
        inner_normal_fiber = origin_node
        inner_normal_fiber2 = util.convert_model_to_segment(inner_normal_fiber,volume_node)
        inner_normal_fiber2.SetName("LSKDjfk")
        inner_normal_fiber2.SetAndObserveTransformNodeID(inner_normal_fiber.GetTransformNodeID())
        inner_normal_fiber2.HardenTransform()
        inner_normal_fiber2.SetAndObserveTransformNodeID(None)
        util.getModuleLogic("JSegmentEditorTool").substract(volume_node,MaskSegmentation,inner_normal_fiber2)
        util.RemoveNode(inner_normal_fiber2)
    
    MaskModel = util.convert_segment_to_model(MaskSegmentation)
    FinalModel = MaskModel
    
    util.send_event_str(util.ProgressValue,60)
    
    tmp = []
    for aaa in fibers:
      tmp.append(aaa)
    
    if fibers!=[]:
      '''
        连接导管和头部模型
      '''
      modellist = fibers
      modellist.append(FinalModel)
      util.combineModelList(modellist,FinalModel)
      
      
    # for fiber in fibers:
    #   util.RemoveNode(fiber)
    # util.HideNode(full_head_model)
    util.send_event_str(util.ProgressValue,100)
    FinalModel.SetAttribute("alias_name","导板")
    FinalModel.SetName("导板")
    util.GetDisplayNode(FinalModel).SetColor(1,1,1)
    util.ShowNode(FinalModel)
    #用来钻孔
    origin_copy = util.getFirstNodeByName("OriginCopy")
    if origin_copy:
      nodes = util.getNodesByClass(util.vtkMRMLModelNode)
      for node in nodes:
        if node.GetAttribute("origin_node_id") == origin_copy.GetID():
          util.RemoveNode(node)
      util.RemoveNode(origin_copy)
    
    node = util.getFirstNodeByName("inner_normal_fiber")
    util.ShowNode(node)
    util.ShowNode3D(node)
    node = util.getFirstNodeByName("outer_normal_fiber")
    util.ShowNode(node)
    util.ShowNode3D(node)
    #垃圾
    util.RemoveNodeByName("m_MaskMarginedNode")
    util.RemoveNodeByName("m_MaskBoardSegmentationNode")
    #头骨的分割
    util.RemoveNodeByName("skull_mask_segmentation_node")
    #去除背板的头部Volume
    util.RemoveNodeByName("stripeed_mask_basic")
    #测量旁开辅助模型
    util.RemoveNodeByName("YellowCircleModel")
    
    #删除文件夹
    #util.remove_all_folder("面具")
    util.remove_all_folder("FullHeadSegmentationNode")
    
    #删除分割
    #util.RemoveNodeByName("FullHeadSegmentationNode")
    #util.RemoveNodeByName("面具")
    #util.HideNodeByName("面具")
    #全脑模型，用来切除导管
    util.RemoveNodeByName("FullHeadModel")
    util.RemoveNodeByName("OriginCopy")
    # nodes = util.getNodesByName("outer_normal_fiber")
    # for node in nodes:
    #   util.HideNode(node)
      
    # nodes = util.getNodesByName("inner_normal_fiber")
    # for node in nodes:
    #   util.HideNode(node)
    
    #删除空的Segment
    segmentationNodes = util.getNodesByClass(util.vtkMRMLSegmentationNode)
    for node in segmentationNodes:
      if util.GetSegmentNumber(node) == 0:
        util.RemoveNode(node)
        
        
    for aaa in tmp:
      util.RemoveNode(aaa)
    # for model in fibers:
    #   util.RemoveNode(model)
    if self.get_volume().GetAttribute("final_puncture") is None:
      util.send_event_str(util.AddSolutionScore)
      self.get_volume().SetAttribute("final_puncture",FinalModel.GetID())
    
    util.color_unit_list.set_style_to_halfmiddle()
    
    util.color_unit_list.add_item(FinalModel, 3)
    util.tips_unit_list.add_item(FinalModel, 3)
    