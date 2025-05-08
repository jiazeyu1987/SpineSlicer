import vtk, qt, ctk, slicer,os
import slicer.util as util
from ModelLibs.ModelManagerUnit.JMC_Template import JMC_Template
class JMC_Normal(JMC_Template):
  manager  = None
  item = None
  paras = {}
  ShrinkHeight = 160
  ShrinkWidth = 100
  ExpandHeight = 300
  ExpandHeight2 = 600
  ExpandWidth = 100
  style = "normal"
  def __init__(self, main, in_present,in_ui) -> None:
    super().__init__(main,in_present,in_ui)
    
  
  def init(self,node,manager,item):
    print("jmc init with node:",node.GetID())
    if node is None:
      return
    if node == self.node:
      return
    self.manager = manager
    self.item = item
    if self.node:
      self.clear_info("")
      util.RemoveNode(self.node)
    self.node = node
    displaynode = util.GetDisplayNode(node)
    if displaynode:
      displaynode.SetVisibility(True)
      displaynode.SetSliceIntersectionThickness(3)
    #self.main.create_advance(self,self.manager,node,self.ui.btnAdvance)
    self.main.create_btn2D(node,self.ui.btn2D)
    self.main.create_btnModify(node,self.ui.btnModify)
    self.main.create_btn3D(node,self.ui.btn3D)
    self.main.create_btnDelete(self,node,self.ui.btnDelete)
    self.main.create_btnColor(node,self.ui.btnColor)
    self.main.create_sliderOpacity(node,self.ui.sliderOpacity)
    self.main.create_sliderOpacity2D(node,self.ui.sliderOpacity2D)
    self.main.create_btnExport(node,self.ui.btn_export)
    self.main.create_toollist(self,self.manager,node,self.ui.comboBox)
    self.ui.lblName.connect('textChanged(QString)', self.on_text_changed)
    self.ui.tabWidget.tabBar().hide()
    self.ui.tabWidget.setCurrentIndex(0)
    self.ui.lblImage.setVisible(False)
    self.ui.btn_puncture_combine.connect('clicked()', self.on_puncture_combine)
    self.ui.btn_puncture_export.connect('clicked()', self.on_puncture_export)
    
    alias_name =  node.GetAttribute("alias_name")
    if alias_name:
      self.set_title(alias_name)
    else:
      self.set_title(node.GetName())
    self.ui.comboBox.setVisible(False)
  def hide_model(self):
    self.ui.btn2D.setChecked(True)
    self.ui.btn3D.setChecked(True)
  
  def on_effect_substract(self,volume_node,segment_node,segid_src):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(volume_node)
    segmentEditorWidget.setActiveEffectByName("Logical operators")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("Operation", "SUBTRACT")
    effect.setParameter("ModifierSegmentID",segid_src)
    effect.self().onApply()
  
    
  
  def on_puncture_export(self):
    res = util.messageBoxReject("我们提供的服务和模型并非用于医学诊断或治疗。任何对于模型结果的解释、解读和应用都应该由医生或其他具有相关专业资质和知识背景的人员进行。我们的模型只能作为医生或其他医疗专业人员的参考，而不应该作为医学诊断和治疗的标准。使用我们的服务和模型所产生的结果和结论仅供参考，不具有法律约束力。在任何情况下，我们不承担由于使用或依赖我们的服务和模型而产生的任何直接或间接的损失、伤害或责任。最终的医学决策应该由医生或其他专业人员根据自己的专业判断和经验作出，并对其决策承担完全的责任。如果您使用我们的服务和模型，即表示您已经完全理解并接受了以上免责声明，同时您也同意自行承担任何由于使用我们的服务和模型而产生的任何责任和风险。",windowTitle=util.tr("提示"))
    if res == 0:
      return

    fileName = qt.QFileDialog.getSaveFileName(None, ("保存文件"),
                              "/model.stl",
                              ("模型 (*.stl)"))
    if fileName == "":
      util.showWarningText("请选择一个文件地址用来存储穿刺导板")
      return
    slicer.util.saveNode(self.node,fileName)
    util.send_event_str(util.ProgressValue,"100")
    util.showWarningText("模型导出成功")
    
  
  #原始的连接导管的函数
  def on_puncture_combine(self):
    duruofei_mask_model = util.getFirstNodeByClassByAttribute(util.vtkMRMLModelNode,"duruofei_mask_model","1")
    duruofei_head_volume = util.getFirstNodeByClassByAttribute(util.vtkMRMLScalarVolumeNode,"duruofei_head_volume","1")
    bind_segment_id = duruofei_mask_model.GetAttribute("bind_segment")
    bind_segment = util.GetNodeByID(bind_segment_id)
    full_head_segment_id = duruofei_mask_model.GetAttribute("full_head_segment")
    full_head_segment = util.GetNodeByID(full_head_segment_id)
    if not duruofei_head_volume:
      util.showWarningText("请加载Dicom数据")
      return
    if not duruofei_mask_model:
      util.showWarningText("请先创建一个面具")
      return
    if not bind_segment:
      util.showWarningText("数据出现了问题，请重新创建一个面具")
      return
    if not full_head_segment:
      util.showWarningText("数据出现了问题，请重新创建一个面具...")
      return
    '''
      将光纤模型,STL模型进行裁剪,与头部皮肤符合
    '''
    res = util.messageBox("合并之后将无法修改模型\n请确认当前的面具已经经过正确的裁剪和镂空",windowTitle=util.tr("提示"))
    if res == 0:
      return
    util.send_event_str(util.ProgressStart,"正在生成连接导管")
    util.send_event_str(util.ProgressValue,"10")
    
    full_head_model = util.convert_segment_to_model(full_head_segment)
    
    util.send_event_str(util.ProgressValue,"20")
    fibers = util.getModuleWidget("JDuruofei").generate_final_fiber_model()
    CombineModelsLogic = util.getModuleLogic("CombineModels")
    for modelNode in fibers:
      if CombineModelsLogic:
        CombineModelsLogic.process(modelNode,full_head_model,modelNode,'difference')
    util.RemoveNode(full_head_model)
    util.send_event_str(util.ProgressValue,"60")

    hollowed_copy = util.clone(bind_segment)
    '''
      如果是普通光纤,那么要在皮肤上给光纤打洞
    '''
    for modelNode in fibers:
      origin_node_id = modelNode.GetAttribute("origin_node_id")
      if origin_node_id:
        util.GetDisplayNode(modelNode).SetColor([1,1,0])
        origin_node = util.GetNodeByID(origin_node_id)
        segment_id = hollowed_copy.AddSegmentFromClosedSurfaceRepresentation(origin_node.GetPolyData(), "SegmentFiber", [1.0,0.0,0.0])
        self.on_effect_substract(duruofei_head_volume,hollowed_copy,segment_id)
        hollowed_copy.RemoveSegment(segment_id)
    util.send_event_str(util.ProgressValue,"65")


    '''
      复制HollowedSegmentationNode转换成模型,用来连接打过洞的导管或者不需要打孔的模型
    '''
    FinalModel = util.convert_segment_to_model(hollowed_copy)
    FinalModel.SetName("TempFinalModel")
    util.send_event_str(util.ProgressValue,"70")


   
    #self.set_final_model(FinalModel)
    final_model = FinalModel
    '''
      仅仅显示最终模型
    '''
    util.send_event_str(util.ProgressValue,"80")
    '''
      设置最终模型的显示参数
    '''
    
    final_model.SetName("FinalModel")
    final_model.SetAttribute("jpunctureplan_finalmodel","1")
    display_node = util.GetDisplayNode(final_model)
    display_node.SetAndObserveColorNodeID("Tissue")
    display_node.SetColor(1,1,0)
    display_node.SetVisibility2D(True)
    display_node.SetScalarVisibility(False)

    if fibers!=[]:

      '''
        因为普通导管用的是克隆体,所以用完之后要删掉
      '''
      for modelNode in fibers:
        origin_node_id = modelNode.GetAttribute("origin_node_id")
        if origin_node_id:
          origin_node = util.GetNodeByID(origin_node_id)
          util.RemoveNode(origin_node)
        util.RemoveNode(modelNode)
      
      '''
        连接导管和头部模型
      '''
      modellist = fibers
      modellist.append(final_model)
      util.combineModelList(modellist,final_model)

    #self.on_cancel()
    util.send_event_str(util.ProgressValue,"95")
    #self.fresh_state()
    
    
    
    '''
      去除碎片
    '''
    util.send_event_str(util.ProgressValue,"100")
    util.send_event_str(util.CombinePunctureGuidComplete,"1")
    
    if self.node:
      util.cloneAttributes(self.node,final_model)
      slicer.mrmlScene.InvokeEvent(util.JMC_NormalRemoved,self.node)
    slicer.mrmlScene.InvokeEvent(util.JRemoveSkullBoardWidgetResult,final_model)
    
  def destroy(self):
    #util.removeFromParent2(self.widget)
    
    if self.node:
      util.RemoveNode(self.node)
    


  def on_text_changed(self,val):
    self.node.SetAttribute("alias_name",val)

  def setStyle(self,style):
    self.style = style

  def shrink(self):
    self.ui.tabWidget.setCurrentIndex(0)
    self.ui.tabWidget.hide()
    if self.item is None:
      self.widget.setFixedHeight(self.ShrinkHeight)
    else:
      classname = type(self.item).__name__
      if classname == "QListWidgetItem":
        self.item.setSizeHint(qt.QSize(self.ShrinkWidth , self.ShrinkHeight))
        pass
      else:
        single_item = self.item
        single_item.listitem.setSizeHint(qt.QSize(self.ShrinkWidth , self.ShrinkHeight))
        single_item.sub_template.widget.setFixedHeight(self.ShrinkHeight)

  def setFunctionSelection(self,val):
    self.ui.comboBox.setCurrentText(val)
    if val != "无":
      self.expand()

  def init_function_list(self,func_list):
    self.ui.comboBox.clear()
    if func_list is None:
      self.ui.comboBox.addItem("无")
      self.ui.comboBox.addItem("平面切割")
      self.ui.comboBox.addItem("膨胀")
      self.ui.comboBox.addItem("缩小")
      self.ui.comboBox.addItem("镜像")
      self.ui.comboBox.addItem("合成")
      self.ui.comboBox.addItem("镂空")
      self.ui.comboBox.addItem("转分割")
      self.ui.comboBox.addItem("详细信息")
    else:
      func_list = func_list.split(", ")
      self.ui.comboBox.addItem("无")
      for key in func_list:
        if key !="无":
          self.ui.comboBox.addItem(key)

  def is_single(self):
    return self.manager is None

  def expand(self,intval=1):
    if self.manager:
      self.manager.shrink_all(self.node)
    self.ui.tabWidget.show()
    classname = type(self.item).__name__
    if classname == "QListWidgetItem":
      self.item.setSizeHint(qt.QSize(self.ExpandWidth , self.ExpandHeight))
    else:
      single_item = self.item
      if intval==1:
        single_item.listitem.setSizeHint(qt.QSize(self.ExpandWidth , self.ExpandHeight))
        single_item.sub_template.widget.setFixedHeight(self.ExpandHeight)
      else:
        single_item.listitem.setSizeHint(qt.QSize(self.ShrinkWidth , self.ExpandHeight2))
        single_item.sub_template.widget.setFixedHeight(self.ExpandHeight2)

  def on_delete(self,node):
    res = util.messageBox("确定删除吗",windowTitle=util.tr("提示"))
    if res == 0:
      return
    if self.style == "surface cut":
      segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
      effect = segmentEditorWidget.activeEffect()
      effect.self().onCancel()
      return
    transform_node = node.GetParentTransformNode()
    if transform_node:
      util.RemoveNode(transform_node)
    bind_segment = node.GetAttribute("bind_segment")
    if bind_segment:
      seg = util.GetNodeByID(bind_segment)
      util.RemoveNode(seg)
    util.RemoveNode(node)

    #for duruofei
    if self.is_single():
      util.removeFromParent2(self.widget)
      slicer.mrmlScene.InvokeEvent(util.JMC_NormalRemoved,self.node)
      
    #   return
    # else:
    #   if node.GetAttribute("model_name"):
    #     if node.GetAttribute("model_name") in ["直柱","弯柱","导针"]:
    #       util.showWarningText("该模型不允许在这里删除")
    #       return
    #   self.main.show_list()
   
    

  def set_title(self,title):
    self.ui.lblName.setText(title)

  
  def set_image(self,img_path):
    if img_path is None or not os.path.exists(img_path):
      return
    util.add_pixelmap_to_label(img_path,self.ui.lblImage)
    
  
  def add_default_info(self,type):
    if type == "":
      pass
  
  def clear_info(self,type):
    if type == "":
      pass
