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
from ModelLibs.ModelManagerUnit.JMC_PunctureGuide import JMC_PunctureGuide
from ModelLibs.ModelManagerUnit.JMC_AddFiber import JMC_AddFiber
from ModelLibs.ModelManagerUnit.JMC_Normal import JMC_Normal
from ModelLibs.JSurfaceCutWithUnit import JSurfaceCutWithUnit

   
      
from Base.JBaseExtension import JBaseExtensionWidget

  

class ModelManager:
  #ModelManager 对应的 UI
  m_ui = None
  logic = None
  main = None
  m_TemplateList = {}
  m_Index = -1
  m_Scene = None
  def __init__(self,in_main,in_ui,scene):
    self.main = in_main
    self.m_ui = in_ui
    self.m_Scene = scene
    self.logic = self.main.logic
    #self.main.create_labeled_clicked_button(self.m_ui.btnClose2D,"close_2D.png","关闭2D显示")
    util.getModuleLogic("JUITool").create_labeled_clicked_button(self.main,self.m_ui.btnClose3D,"close_3D.png","关闭3D显示",rlist=self.main.resourcelist)
    util.getModuleLogic("JUITool").create_labeled_clicked_button(self.main,self.m_ui.btnClose2D,"model_invisible_2d.png","关闭2D显示",rlist=self.main.resourcelist)
    util.getModuleLogic("JUITool").create_labeled_clicked_button(self.main,self.m_ui.btnRemove,"volume_remove.png","删除当前序列组",rlist=self.main.resourcelist)
    util.getModuleLogic("JUITool").create_labeled_clicked_button(self.main,self.m_ui.btn_export,"tool_topmenu_save.png","保存所有模型数据",rlist=self.main.resourcelist)
    
    menu = qt.QMenu(self.m_ui.widget)
    self.m_ui.btnAdd.setMenu(menu)
    menu.addAction("添加颅骨",lambda:self.add_node_by_type("skull"))
    menu.addAction("添加皮质",lambda:self.add_node_by_type("brain_tissue"))
    menu.addAction("添加静脉血管",lambda:self.add_node_by_type("vessel_jing"))
    menu.addAction("添加动脉血管",lambda:self.add_node_by_type("artery"))
    menu.addAction("添加肿瘤",lambda:self.add_node_by_type("tumor"))
    menu.addAction("添加脑区",lambda:self.add_node_by_type("cortex"))
    menu.addAction("神经束",lambda:self.add_node_by_type("fibers"))
    self.m_ui.btnAdd.setLayoutDirection(qt.Qt.LeftToRight)
    self.m_ui.btnAdd.setToolButtonStyle(qt.Qt.ToolButtonTextBesideIcon)
    self.m_ui.btnAdd.setPopupMode(1)
    path = util.get_resource("add.png")
    pixmap = qt.QPixmap(path)
    pixelmap_scaled = pixmap.scaled(24,24, 0,1)
    buttonIcon = qt.QIcon(pixelmap_scaled)
    self.m_ui.btnAdd.setIcon(buttonIcon)
      
    #util.getModuleLogic("JMeasure").create_toolbutton(self.main,self.m_ui.btnClose2D,"model_invisible_2d.png","关闭2D显示",rlist=self.main.resourcelist)#self.m_ui.btnClose2D.connect('clicked()', self.close_all_2d)
    self.m_ui.btnClose3D.setCheckable(True)
    self.m_ui.btnClose2D.setCheckable(True)
    self.m_ui.btnClose3D.connect('toggled(bool)', self.close_all_3d)
    self.m_ui.btnClose2D.connect('toggled(bool)', self.close_all_2d)
    self.m_ui.btnRemove.connect('clicked()', self.on_remove_series)
    self.m_ui.horizontalSlider2D.connect('valueChanged(int)', self.onSlicer2DChanged)
    self.m_ui.horizontalSlider3D.connect('valueChanged(int)', self.onSlicer3DChanged)
    self.m_ui.btn_pre.connect('clicked()', self.goto_preveiw_page)
    self.m_ui.btn_next.connect('clicked()', self.goto_next_page)
    self.m_ui.comboBox.connect("currentIndexChanged(int)",self.on_filter_condition_changed)
    self.m_ui.ListWidget.connect('currentItemChanged(QListWidgetItem*,QListWidgetItem*)', self.on_change)
    self.m_ui.btn_export.connect('clicked()', self.on_btn_export)
    self.m_ui.ListWidget.setSpacing(0)
    self.m_ui.tabWidget.tabBar().hide()
    slicer.mrmlScene.AddObserver(util.FreshModelList, self.onevent1)

  def on_btn_export(self):
    folders_path = util.get_folder_path()
    if folders_path == "":
      return
    nodes_with_slice = util.getNodesByClass(util.vtkMRMLModelNode)
    nodes = []
    for node in nodes_with_slice:
      if node.GetName().find("Volume Slice") != -1:
        continue
      nodes.append(node)
    util.send_event_str(util.ProgressStart,"正在保存模型数据")
    len1=len(nodes)
    step = int(100/len1)
    num = 0
    util.send_event_str(util.ProgressValue,num)
    for node in nodes:
      name = node.GetName()
      naemvtk = name+".vtk"
      namepath = os.path.join(folders_path,naemvtk).replace("\\","/")
      util.saveNode(node,namepath)
      num+=step
      util.send_event_str(util.ProgressValue,num)
    util.send_event_str(util.ProgressValue,100)

  def on_filter_condition_changed(self):
    txt = self.m_ui.comboBox.currentText
    self._fresh_list(txt)
  
  def _fresh_list(self,type):
    if type == "显示全部模型":
      for node in self.m_TemplateList:
        template = self.m_TemplateList[node]
        template.item.setHidden(False)
    elif type in ["脑区(左)"]:
      for node in self.m_TemplateList:
        template = self.m_TemplateList[node]
        if node.GetAttribute("model_type") == "脑区":
          alias_name = node.GetAttribute("alias_name")
          if alias_name.find("左") != -1:
            template.item.setHidden(False)
          else:
            template.item.setHidden(True)
        else:
          template.item.setHidden(True)
    elif type in ["脑区(右)"]:
      for node in self.m_TemplateList:
        template = self.m_TemplateList[node]
        if node.GetAttribute("model_type") == "脑区":
          alias_name = node.GetAttribute("alias_name")
          if alias_name.find("右") != -1:
            template.item.setHidden(False)
          else:
            template.item.setHidden(True)
        else:
          template.item.setHidden(True)
    else:
      for node in self.m_TemplateList:
        template = self.m_TemplateList[node]
        if node.GetAttribute("model_type") == type:
          template.item.setHidden(False)
        else:
          template.item.setHidden(True)
          
  def get_folder_path(self):
    res_path,result = util.show_file_dialog(2)
    if result == 0:
      return ""
    else:
      return res_path
  
  def add_node_by_type(self,type,find_path=True):
    project_name = util.getjson("project_name")
    print("add_node_by_type")
    if not find_path:
      folder_path = os.path.join(util.mainWindow().GetProjectBasePath(),"ProjectCache",project_name,"patient_data",util.get_patient_id(),type).replace('\\','/')
    else:
      folder_path = self.get_folder_path()
      if folder_path=="":
        return
    print("add from file path:",folder_path)
    data_map = {}
    data_map['skull'] = {}
    data_map['skull']['folder_path'] = folder_path
    data_map['skull']['alias_name'] = "颅骨"
    data_map['skull']['model_type'] = "颅骨"
    data_map['skull']['SetOpacity'] = 50
    data_map['skull']['SetColor'] = [1,1,1]
    data_map['skull']['FileType'] = 'ModelFile'
    
    data_map['brain_tissue'] = {}
    data_map['brain_tissue']['folder_path'] = folder_path
    data_map['brain_tissue']['alias_name'] = "皮质"
    data_map['brain_tissue']['model_type'] = "皮质"
    data_map['brain_tissue']['SetOpacity'] = 50
    data_map['brain_tissue']['SetColor'] = [0.5,0.5,0.5]
    data_map['brain_tissue']['FileType'] = 'ModelFile'
    
    data_map['vessel_jing'] = {}
    data_map['vessel_jing']['folder_path'] = folder_path
    data_map['vessel_jing']['alias_name'] = "静脉"
    data_map['vessel_jing']['model_type'] = "血管"
    data_map['vessel_jing']['SetOpacity'] = 100
    data_map['vessel_jing']['SetColor'] = [0,151/255.0,206/255.0]
    data_map['vessel_jing']['FileType'] = 'ModelFile'
    
    data_map['artery'] = {}
    data_map['artery']['folder_path'] = folder_path
    data_map['artery']['alias_name'] = "动脉"
    data_map['artery']['model_type'] = "血管"
    data_map['artery']['SetOpacity'] = 100
    data_map['artery']['SetColor'] = [1,0,0]
    data_map['artery']['FileType'] = 'ModelFile'
    
    data_map['tumor'] = {}
    data_map['tumor']['folder_path'] = folder_path
    data_map['tumor']['alias_name'] = "肿瘤"
    data_map['tumor']['model_type'] = "肿瘤"
    data_map['tumor']['SetOpacity'] = 100
    data_map['tumor']['SetColor'] = [145/255.0,60/255.0,66/255.0]
    data_map['tumor']['FileType'] = 'ModelFile'
    
    data_map['cortex'] = {}
    data_map['cortex']['folder_path'] = folder_path
    data_map['cortex']['alias_name'] = "脑区"
    data_map['cortex']['model_type'] = "脑区"
    data_map['cortex']['SetOpacity'] = 100
    data_map['cortex']['SetColor'] = 'cortex'
    data_map['cortex']['FileType'] = 'ModelFile'
    
    # data_map['cortexL'] = {}
    # data_map['cortexL']['folder_path'] = folder_path
    # data_map['cortexL']['alias_name'] = "脑区左"
    # data_map['cortexL']['model_type'] = "脑区左"
    # data_map['cortexL']['SetOpacity'] = 100
    # data_map['cortexL']['SetColor'] = 'cortex'
    # data_map['cortexL']['FileType'] = 'ModelFile'
    
    # data_map['cortexR'] = {}
    # data_map['cortexR']['folder_path'] = folder_path
    # data_map['cortexR']['alias_name'] = "脑区右"
    # data_map['cortexR']['model_type'] = "脑区右"
    # data_map['cortexR']['SetOpacity'] = 100
    # data_map['cortexR']['SetColor'] = 'cortex'
    # data_map['cortexR']['FileType'] = 'ModelFile'
    
    data_map['fibers'] = {}
    data_map['fibers']['folder_path'] = folder_path
    data_map['fibers']['alias_name'] = "神经束"
    data_map['fibers']['model_type'] = "神经束"
    data_map['fibers']['SetOpacity'] = 100
    data_map['fibers']['SetColor'] = [145/255.0,60/255.0,66/255.0]
    data_map['fibers']['FileType'] = 'FiberBundleFile'
    print(data_map,type)
    folder_path  = data_map[type]['folder_path']
    # folder_path,result  = util.show_file_dialog(2)
    # if result is False or folder_path == "":
    #   return
    alias_name  = data_map[type]['alias_name']
    model_type  = data_map[type]['model_type']
    SetOpacity  = data_map[type]['SetOpacity']
    SetColor  = data_map[type]['SetColor']
    FileType = data_map[type]['FileType']
    
    util.send_event_str(util.ProgressStart,"正在加载数据")
    util.send_event_str(util.ProgressValue,0)
    vtk_files = []
    print("load data from model:",folder_path)
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.vtk') or file.endswith('.vtp'):
                print("load data from vtk:",os.path.join(root, file))
                vtk_files.append(os.path.join(root, file))
    length = len(vtk_files)
    index=0
    for file_path in vtk_files:
      model = util.loadNodeFromFile(file_path, FileType, {}, False)
      model.SetAttribute("alias_name",alias_name)
      model.SetAttribute("model_type",model_type)
      util.GetDisplayNode(model).SetOpacity(SetOpacity)
      util.GetDisplayNode(model).SetScalarVisibility(False)
      file_name = os.path.basename(file_path)
      if isinstance(SetColor,list):
        util.GetDisplayNode(model).SetColor(SetColor)
      elif SetColor == 'cortex':
        file_name = os.path.basename(file_path)
        file_name_without_extension = os.path.splitext(file_name)[0]
        if  file_name_without_extension in self.main.cortex_config:
          try:
            value = self.main.cortex_config[file_name_without_extension]
            eng_name = value['英文']
            chinese_name = value['中文']
            R1 = int(value['R'])
            G1 = int(value['G'])
            B1= int(value['B'])
            util.GetDisplayNode(model).SetColor([R1/255.0,G1/255.0,B1/255.0])
            model.SetAttribute("alias_name",chinese_name)
          except Exception as e:
            print(e.__str__())
        else:
          pass
      index+=1
      util.send_event_str(util.ProgressValue,int(90/length*index))
    
    util.getModuleWidget("JDTI").ui.btn_all_paint.setChecked(False)
    util.getModuleWidget("JDTI").ui.btn_all_paint.setChecked(True)
          
    util.singleShot(0,lambda:util.send_event_str(util.ProgressValue,100))
    util.reinit()
    self.update_model_type_combox(model_type)
    if model_type == "神经束":
      util.send_event_str(util.SetPage,"8")
    
  def update_model_type_combox(self,model_type):
    if model_type == "神经束":
      return
    if (self.m_ui.comboBox.findText(model_type) == -1):
      if model_type == "脑区":
        if self.m_ui.comboBox.findText("脑区(左)") == -1:
          self.m_ui.comboBox.addItem("脑区(左)")
        if self.m_ui.comboBox.findText("脑区(右)") == -1:
          self.m_ui.comboBox.addItem("脑区(右)")
      else:
        self.m_ui.comboBox.addItem(model_type)
    

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def onevent1(self,caller,str_event,calldata):
    self.fresh_list()

  def on_return(self):
    #util.send_event_str(util.GotoCurrentPage,self.m_Index.__str__())
    #util.send_event_str(util.Return_ModelList,self.m_Index.__str__())
    util.send_event_str(util.GotoPrePage,self.m_Index.__str__())

  def shrink_all(self,keeped_node = None):
    if self.m_TemplateList:
      for node in self.m_TemplateList:
        if node == keeped_node:
          continue
        else:
          self.m_TemplateList[node].ui.comboBox.setCurrentIndex(0)

  def goto_next_page(self):
    util.send_event_str(util.GotoNextPage)
    
  def goto_preveiw_page(self):
    util.send_event_str(util.GotoPrePage)
  
  def on_remove_series(self):
    res = util.messageBox("确定删除当前的所有序列吗",windowTitle=util.tr("提示"))
    if res == 0:
      return
    txt = self.m_ui.comboBox.currentText
    nodes = []
    if txt == "显示全部模型":
      for node in self.m_TemplateList:
            nodes.append(node)
    elif txt == "脑区(左)":
      for node in self.m_TemplateList:
        if node.GetAttribute("model_type") == "脑区":
          alias_name = node.GetAttribute("alias_name")
          if alias_name.find("左") != -1:
            nodes.append(node)
    elif txt == "脑区(右)":
      for node in self.m_TemplateList:
        if node.GetAttribute("model_type") == "脑区":
          alias_name = node.GetAttribute("alias_name")
          if alias_name.find("右") != -1:
            nodes.append(node)
    else:
      for node in self.m_TemplateList:
          if node.GetAttribute("model_type") == txt:
            nodes.append(node)
    
    util.send_event_str(util.ProgressStart,"正在删除数据")
    util.send_event_str(util.ProgressValue,0)
    i = 0
    print("delete nodes:",len(nodes))
    for node in nodes:
      i+=1
      template = self.m_TemplateList[node]
      if not template:
        continue
      util.RemoveNode(node)
      row = self.m_ui.ListWidget.row(template.item)
      self.m_ui.ListWidget.takeItem(row)
      pv = int(98/len(nodes))*i
      util.send_event_str(util.ProgressValue,pv)
      del template
      
    util.send_event_str(util.ProgressValue,100)
    
  def close_all_2d(self,val):
    print("close all 2d in JManagerModel")
    for key in self.m_TemplateList:
        template = self.m_TemplateList[key]
        if not template.item.isHidden():
          template.ui.btn2D.setChecked(val)

  def close_all_3d(self,val):
    print("close all 3d in JManagerModel")
    for key in self.m_TemplateList:
        template = self.m_TemplateList[key]
        if not template.item.isHidden():
          template.ui.btn3D.setChecked(val)

  def onSlicer2DChanged(self,val):
    for key in self.m_TemplateList:
        template = self.m_TemplateList[key]
        if not template.item.isHidden():
          template.ui.sliderOpacity2D.setValue(val)
          
  def onSlicer3DChanged(self,val):
    for key in self.m_TemplateList:
        template = self.m_TemplateList[key]
        if not template.item.isHidden():
          template.ui.sliderOpacity.setValue(val)
  
  def on_change(self,item,_):
    pass

  def fresh_list(self):
    self.m_ui.ListWidget.clear()
    self.m_TemplateList = {}
    model_list = util.getNodesByClass(util.vtkMRMLModelNode)
    for model in model_list:
      alias_name = model.GetAttribute("alias_name")
      if not alias_name:
        continue
      template = self.main.get_new_widget('normal_manager')
      

      item = qt.QListWidgetItem(self.m_ui.ListWidget)
      template.init(model,self,item)
      self.m_ui.ListWidget.setItemWidget(item,template.widget)
      self.m_ui.ListWidget.addItem(item)
      template.set_title(alias_name)
      template.set_image(self.main.get_image_path(model))
      self.m_TemplateList[model] = template
      template.shrink()

  
  
  
 
 
  
  def on_node_added(self,node):
    if node in self.m_TemplateList:
      return
    if node.GetAttribute("hide_in_manager") == "1":
      return
    if len(node.GetName())>12 and node.GetName()[-12:] == "Volume Slice":
      return
    if node.GetAttribute("alias_name") is None:
      node.SetAttribute("model_type","其他")
    template = self.main.get_new_widget("normal_manager")
    functionlist = util.getjson2("JManagerModel","function_list","")
    template.init_function_list(functionlist)
    
    
    item = qt.QListWidgetItem(self.m_ui.ListWidget)
    self.m_ui.ListWidget.setItemWidget(item,template.widget)
    self.m_ui.ListWidget.addItem(item)
    #这里不用singleShot会布局错误
    #必须要在这里用singhleShot
    #这里的时候node还没有被添加进Scene里
    #因此很多属性是有误导的，比如现在displaynode是空的，因为还没有添加进scene，但是使用singleshot之后displaynode就不为空了
    template.init(node,self,item)
    template.shrink()
    self.m_TemplateList[node] = template
    util.singleShot(10,lambda:template.ui.btn2D.setChecked(False))
  
  
  def on_node_removed(self,node):
    if node.GetAttribute("hide_in_manager") == "1":
      return
    if node not in self.m_TemplateList:
      return
    template = self.m_TemplateList[node]
    self.m_ui.ListWidget.takeItem(self.m_ui.ListWidget.row(template.item))
    del self.m_TemplateList[node]
  


class JManagerModel(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "JManagerModel"  # TODO: make this more human readable by adding spaces
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
# JManagerModelWidget
#

class JManagerModelWidget(JBaseExtensionWidget):
  uis = {}
  name_puncture_guide = "name_puncture_guide"
  name_addfiber = "name_addfiber"
  addfiber_manager = "addfiber_manager"
  inner_manager = None
  model_list_id = 0
  resourcelist = {}
  cortex_config = {}
  def __init__(self, parent=None):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)  # needed for parameter node observation
    self.logic = None

  def setup(self):
    super().setup()
    self.logic = JManagerModelLogic()
    self.logic.setWidget(self)
    self.uis[self.name_puncture_guide] = 'UI/JMC_PunctureGuide.ui'
    self.uis[self.name_addfiber] = 'UI/JMC_AddFiber.UI'
    
    if util.get_from_PAAA("current_project_selector_project_name") == "PBrainPlatform":
      self.cortex_config = self.load_config()
    self.ensure_manager_loaded()
    #util.singleShot(10,self.test_add_stls)
    
  
  def load_config(self):
    import pandas as pd
    excel_file = util.get_resource("brain_segment.xlsx",False)
    if not os.path.exists(excel_file):
      return {}
    if excel_file is None:
      return {}
    data = pd.read_excel(excel_file,engine="openpyxl")

    # 创建一个空字典
    result = {}

    # 将每行的第一列的值作为键，剩下的列的值作为对应键的值
    for index, row in data.iterrows():
        # 获取第一列的值作为键
        try:
          key = int(row[0])
        except Exception as e:
          key = 0
        key = key.__str__()
        # 获取剩下的列的值，将它们放入一个字典
        values = {data.columns[i]: row[i] for i in range(1, len(data.columns))}

        # 将键值对添加到字典中
        result[key] = values
    return result
  
  def test_add_stls(self):
    def test_add_model(list1,index):
      if index == len(list1):
        return
      util.loadModel(list1[index])
      util.singleShot(300,lambda:test_add_model(list1,index+1))
    test_folder = r"D:\S521\GLPyModule\JExtension\JAddFiber\Resources\STL\duruofei\side\1"
    stl_files = []
    for root, dirs, files in os.walk(test_folder):
        for file in files:
            if file.endswith('.stl'):
                stl_files.append(os.path.join(root, file))
    test_add_model(stl_files,0)
    

  
  def get_resource_list(self):
    txt = ""
    for key in self.resourcelist:
      value = self.resourcelist[key]
      txt = txt+key+":\t\t"+value+"\n"
    filepath = util.get_resource("model_list.txt",use_default_path=False)
    if txt != "":
      with open(filepath, "w") as file:
        file.write(txt)
    return txt

  def get_image_path(self,node):
    #image_path = node.GetAttribute("image_path")
    #if not image_path:
    #  return
    #path = os.path.join(util.mainWindow().GetProjectBasePath(),"Resources","Icons",image_path+".png").replace('\\','/')
    #print("model icon path:",path)
    path = util.get_resource(f"model_cover_{node.GetName()}.png")
    self.resourcelist[f"model_cover_{node.GetName()}.png"] = "用来描述这个名字的模型的简单的图标"
    self.get_resource_list()
    return path
  
  
  def ensure_manager_loaded(self):
    if self.inner_manager is None:
      uiwidget,manager = self.create_model_manager("normal_manager")
      util.addWidget2(self.ui.widget,uiwidget)
      self.inner_manager = manager
  

  def show_list_with_index(self,index=-100):
    self.ensure_manager_loaded()
    goodlist = []
    if index == -100:
      goodlist = util.getNodesByClass(util.vtkMRMLModelNode)
    else:
      for node in util.getNodes("*").values():
        if node.GetAttribute("model_list_id") :
          if node.GetAttribute("model_list_id") == index:
            if util.GetDisplayNode(node) is not None:
              goodlist.append(node) 
    self.model_list_id = index
  

  def show_list(self):
    self.show_list_with_index(self.model_list_id)

  def create_model_manager(self,name):
    
    if name == self.addfiber_manager:
      uiWidget = util.loadUI(self.resourcePath('UI/JMC_Manager.ui'))
      m_ui = slicer.util.childWidgetVariables(uiWidget)
      manager = ModelManager(self,m_ui,slicer.mrmlScene)
      return uiWidget,manager
    if name == "normal_manager":
      uiWidget = util.loadUI(self.resourcePath('UI/Normal_Manager.ui'))
      m_ui = slicer.util.childWidgetVariables(uiWidget)
      manager = ModelManager(self,m_ui,slicer.mrmlScene)
      return uiWidget,manager

  def get_single_model(self,sigle_item,model_id=None):
    widget = slicer.util.loadUI(self.resourcePath("UI/JMC_Normal.ui"))
    template1ui = slicer.util.childWidgetVariables(widget)
    template = JMC_Normal(self,widget,template1ui)
    if model_id is not None:
      node = util.GetNodeByID(model_id)
      if node is not None:
        template.init(node,None,sigle_item)
        template.set_image(self.get_image_path(node))
    else:
      return None
    self.get_resource_list()
    return template

  def get_new_widget(self,name):
    
    if name == self.name_puncture_guide:
      key = self.uis['name_puncture_guide']
      template1 = slicer.util.loadUI(self.resourcePath(key))
      template1ui = slicer.util.childWidgetVariables(template1)
      widget = JMC_PunctureGuide(self,template1,template1ui)
      return widget
    if name == self.name_addfiber:
      key = self.uis['name_addfiber']
      template1 = slicer.util.loadUI(self.resourcePath(key))
      template1ui = slicer.util.childWidgetVariables(template1)
      widget = JMC_AddFiber(self,template1,template1ui)
      return widget
    if name == "normal_manager":
      template1 = slicer.util.loadUI(self.resourcePath('UI/JMC_Normal.ui'))
      template1ui = slicer.util.childWidgetVariables(template1)
      widget = JMC_Normal(self,template1,template1ui)
      return widget
      


  def create_btnVisible(self,node,btn):
    self.resourcelist["model_visible_2d.png"] = "让模型在2D视图上显示"
    self.resourcelist["model_invisible_2d.png"] = "让模型在2D视图上隐藏"
    btn_visible = util.get_resource("model_visible_2d.png")
    btn_unvisible = util.get_resource("model_invisible_2d.png")
    btn_stylesheet = btn.styleSheet
    btn_stylesheet = btn_stylesheet + "QToolTip { color: #000000; background-color: #ffffff; border: 0px; }"
    btn_stylesheet = btn_stylesheet + "QPushButton{image: url("+btn_visible+")}"
    btn_stylesheet = btn_stylesheet + "QPushButton:checked{image: url("+btn_unvisible+")}"
    btn.connect('toggled(bool)', lambda is_show:self.on_visible(node,is_show))
    btn.toolTip = "让模型在2D视图上显示/隐藏"
    btn.setStyleSheet(btn_stylesheet)

  
  def create_btnExport(self,node,btn):
    self.resourcelist["tool_topmenu_save.png"] = "让模型在3D视图上显示"
    btn_visible = util.get_resource("tool_topmenu_save.png")
    btn_stylesheet = btn.styleSheet
    btn_stylesheet = btn_stylesheet + "QToolTip { color: #000000; background-color: #ffffff; border: 0px; }"
    btn_stylesheet = btn_stylesheet + "QPushButton{image: url("+btn_visible+")}"
    btn.toolTip = "导出模型"
    btn.setStyleSheet(btn_stylesheet)
    btn.connect('clicked()', lambda:self.on_export(node))
  
  def on_export(self,node):
    fileName = qt.QFileDialog.getSaveFileName(None, ("保存文件"),
                              "/model.stl",
                              ("模型 (*.stl)"))
    if fileName == "":
      util.showWarningText("请选择一个文件地址用来存储模型")
      return
    slicer.util.saveNode(node,fileName)
    util.send_event_str(util.ProgressValue,"100")
    util.showWarningText("模型导出成功")
    
  def create_btn2D(self,node,btn):
    self.resourcelist["model_visible_2d.png"] = "让模型在2D视图上显示"
    self.resourcelist["model_invisible_2d.png"] = "让模型在2D视图上隐藏"
    btn_visible = util.get_resource("model_visible_2d.png")
    btn_unvisible = util.get_resource("model_invisible_2d.png")
    btn_stylesheet = btn.styleSheet
    btn_stylesheet = btn_stylesheet + "QToolTip { color: #000000; background-color: #ffffff; border: 0px; }"
    btn_stylesheet = btn_stylesheet + "QPushButton{image: url("+btn_unvisible+")}"
    btn_stylesheet = btn_stylesheet + "QPushButton:checked{image: url("+btn_visible+")}"
    btn.toolTip = "让模型在2D视图上显示/隐藏"
    btn.setStyleSheet(btn_stylesheet)
    util.getModuleLogic("JUITool").registe_model_visible2d_button(btn,node)

  
  def create_btn3D(self,node,btn):
    self.resourcelist["model_visible_3d.png"] = "让模型在3D视图上显示"
    self.resourcelist["model_invisible_3d.png"] = "让模型在3D视图上隐藏"
    btn_visible = util.get_resource("model_visible_3d.png")
    btn_unvisible = util.get_resource("model_invisible_3d.png")
    btn_stylesheet = btn.styleSheet
    btn_stylesheet = btn_stylesheet + "QToolTip { color: #000000; background-color: #ffffff; border: 0px; }"
    btn_stylesheet = btn_stylesheet + "QPushButton{image: url("+btn_unvisible+")}"
    btn_stylesheet = btn_stylesheet + "QPushButton:checked{image: url("+btn_visible+")}"
    btn.toolTip = "让模型在3D视图上显示/隐藏"
    btn.setStyleSheet(btn_stylesheet)
    util.getModuleLogic("JUITool").registe_model_visible3d_button(btn,node)

  def create_toollist(self,unit,manager,node,comboBox):
    comboBox.connect("currentIndexChanged(int)",lambda intval: self.on_toollist_changed(unit,comboBox,manager,node,intval))
  
  def on_toollist_changed(self,unit,comboBox,manager,node,intval):
    txt = comboBox.currentText
    tabWidget = unit.ui.tabWidget
    if txt == "无":
      tabWidget.setCurrentIndex(0)
      unit.shrink()
      pass
    if txt == "平面切割":
      tabWidget.setCurrentIndex(1)
      unit.expand()
      unit.ui.plane_cut_cb.clear()
      nodes = util.getNodesByClass(util.vtkMRMLMarkupsPlaneNode)
      for inner_node in nodes:
        unit.ui.plane_cut_cb.addItem(inner_node.GetName())
      if "plane_cut" not in unit.paras:
        unit.paras["plane_cut"] = 1 
        def on_planecut_apply():
          if len(nodes) == 0:
            util.showWarningText("您需要先创建一个平面")
            return
          currentText = unit.ui.plane_cut_cb.currentText
          planenode = util.getFirstNodeByName(currentText)
          a_node = util.AddNewNodeByClass(util.vtkMRMLModelNode)
          b_node = util.AddNewNodeByClass(util.vtkMRMLModelNode)
          dynamicModelerNode = util.CreateNodeByClass("vtkMRMLDynamicModelerNode")
          dynamicModelerNode.SetToolName("Plane cut")
          dynamicModelerNode.SetNodeReferenceID("PlaneCut.OutputPositiveModel",a_node.GetID())
          dynamicModelerNode.SetNodeReferenceID("PlaneCut.OutputNegativeModel",b_node.GetID())
          dynamicModelerNode.SetNodeReferenceID("PlaneCut.InputPlane",planenode.GetID())
          dynamicModelerNode.SetNodeReferenceID("PlaneCut.InputModel",unit.node.GetID())

          a_node.SetAttribute("alias_name",unit.node.GetAttribute("alias_name")+"L")
          b_node.SetAttribute("alias_name",unit.node.GetAttribute("alias_name")+"R")
          util.AddNode(dynamicModelerNode)
          manager.fresh_list()
        unit.ui.plane_cut_apply.connect('clicked()',on_planecut_apply)
    if txt == "膨胀":
      tabWidget.setCurrentIndex(2)
      unit.expand()
      if "margin_out" not in unit.paras:
        unit.paras["margin_out"] = 1 
        def margin_apply():
          dynamicModelerNode = util.CreateNodeByClass("vtkMRMLDynamicModelerNode")
          dynamicModelerNode.SetToolName("Margin")
          dynamicModelerNode.SetAttribute("Margin",unit.ui.margin_out_slider.value.__str__())
          dynamicModelerNode.SetNodeReferenceID("Margin.InputModel",unit.node.GetID())
          dynamicModelerNode.SetNodeReferenceID("Margin.OutputModel",unit.node.GetID())
          util.AddNode(dynamicModelerNode)
        unit.ui.margin_out_apply.connect('clicked()',margin_apply)
    if txt == "缩小":
      tabWidget.setCurrentIndex(3)
      unit.expand()
      if "margin_in" not in unit.paras:
        unit.paras["margin_in"] = 1 
        
        def margin_in_apply():
          dynamicModelerNode = util.CreateNodeByClass("vtkMRMLDynamicModelerNode")
          dynamicModelerNode.SetToolName("Margin")
          dynamicModelerNode.SetAttribute("Margin","%d"%(-unit.ui.margin_out_slider.value))
          dynamicModelerNode.SetNodeReferenceID("Margin.InputModel",unit.node.GetID())
          dynamicModelerNode.SetNodeReferenceID("Margin.OutputModel",unit.node.GetID())
          util.AddNode(dynamicModelerNode)
        unit.ui.margin_in_apply.connect('clicked()',margin_in_apply)
    if txt == "镜像":
      tabWidget.setCurrentIndex(4)
      unit.expand()
      unit.ui.mirror_cb.clear()
      nodes = util.getNodesByClass(util.vtkMRMLMarkupsPlaneNode)
      for inner_node in nodes:
        unit.ui.mirror_cb.addItem(inner_node.GetName())
      if "mirror" not in unit.paras:
        unit.paras["mirror"] = 1 
        if len(nodes) == 0:
          util.showWarningText("您需要先创建一个平面")
          return
        currentText = unit.ui.mirror_cb.currentText
        planenode = util.getFirstNodeByName(currentText)
        a_node = util.AddNewNodeByClass(util.vtkMRMLModelNode)
        def on_mirror():
          dynamicModelerNode = util.CreateNodeByClass("vtkMRMLDynamicModelerNode")
          dynamicModelerNode.SetToolName("Mirror")
          dynamicModelerNode.SetNodeReferenceID("Mirror.InputModel",unit.node.GetID())
          dynamicModelerNode.SetNodeReferenceID("Mirror.InputPlane",planenode.GetID())
          dynamicModelerNode.SetNodeReferenceID("Mirror.OutputModel",a_node.GetID())
          a_node.SetAttribute("alias_name",unit.node.GetAttribute("alias_name")+"镜像")
          util.AddNode(dynamicModelerNode)
          manager.fresh_list()
        unit.ui.mirror_apply.connect('clicked()',on_mirror)
    if txt == "合成":
      tabWidget.setCurrentIndex(5)
      unit.expand()
      unit.ui.combine_cb.clear()
      nodes = util.getNodesByClass(util.vtkMRMLModelNode)
      for inner_node in nodes:
        if inner_node == node:
          continue
        alias_name = inner_node.GetAttribute("alias_name")
        if alias_name:
          unit.ui.combine_cb.addItem(alias_name)
      if "combine" not in unit.paras:
        unit.paras["combine"] = 1 
        currentText = unit.ui.combine_cb.currentText
        model_node = util.getFirstNodeByClassByAttribute(util.vtkMRMLModelNode,"alias_name",currentText)
        a_node = util.AddNewNodeByClass(util.vtkMRMLModelNode)
        def on_combine_apply():
          dynamicModelerNode = util.CreateNodeByClass("vtkMRMLDynamicModelerNode")
          dynamicModelerNode.SetToolName("Append")
          dynamicModelerNode.AddNodeReferenceID("Append.InputModel",unit.node.GetID())
          dynamicModelerNode.AddNodeReferenceID("Append.InputModel",model_node.GetID())
          dynamicModelerNode.SetNodeReferenceID("Append.OutputModel",a_node.GetID())
          a_node.SetAttribute("alias_name",unit.node.GetAttribute("alias_name")+"合并")
          util.AddNode(dynamicModelerNode)
          manager.fresh_list()
        unit.ui.combine_apply.connect('clicked()',on_combine_apply)
    if txt == "镂空":
      tabWidget.setCurrentIndex(6)
      unit.expand()
      if "hollow" not in unit.paras:
        unit.paras["hollow"] = 1 
        
        def on_hollow_apply():
          dynamicModelerNode = util.CreateNodeByClass("vtkMRMLDynamicModelerNode")
          dynamicModelerNode.SetToolName("Hollow")
          dynamicModelerNode.SetAttribute("ShellThickness","%d"%(unit.ui.hollow_slider.value))
          dynamicModelerNode.SetNodeReferenceID("Hollow.InputModel",unit.node.GetID())
          dynamicModelerNode.SetNodeReferenceID("Hollow.OutputModel",unit.node.GetID())
          util.AddNode(dynamicModelerNode)
        unit.ui.hollow_apply.connect('clicked()',on_hollow_apply)
    if txt == "转分割":
      tabWidget.setCurrentIndex(7)
      unit.expand()
      if "convert_segment" not in unit.paras:
        unit.paras["convert_segment"] = 1 
        def on_convert_segment_apply():
          seg = util.convert_model_to_segment(unit.node,util.getModuleLogic("JSegmentEditorTool").master_node)
          seg.SetAttribute("alias_name",unit.node.GetAttribute("alias_name"))
        unit.ui.convert_segment_apply.connect('clicked()',on_convert_segment_apply)
    if txt == "详细信息":
      tabWidget.setCurrentIndex(9)
      unit.expand()
      polyData = unit.node.GetPolyData()
      # 创建vtkMassProperties对象
      massProperties = vtk.vtkMassProperties()
      massProperties.SetInputData(polyData)
      massProperties.Update()
      # 获取模型的表面积和体积
      surfaceArea = massProperties.GetSurfaceArea()
      volume = massProperties.GetVolume()
      cell_number = unit.node.GetMesh().GetNumberOfCells()
      point_number = unit.node.GetMesh().GetNumberOfPoints()
      txt = "模型信息\n"
      txt += f"模型体积:\t{round(volume/1000,0)}  mm³\n面积:\t{round(surfaceArea/100,0)}  mm²\n"
      #txt += f"模型面数:\t{cell_number}  \n模型点数:\t{point_number}  "
      unit.ui.textEdit.append(txt)
    if txt == "普通导板":
      tabWidget.setCurrentIndex(10)
      unit.expand()
  
  

  def create_btnModify(self,node,btn):
    btn.clicked.disconnect()
    self.resourcelist["model_modify.png"] = "修改当前的模型"
    btnReset_visible = util.get_resource('model_modify.png')
    btnReset_stylesheet = ""
    btnReset_stylesheet = btnReset_stylesheet + "QToolTip { color: #000000; background-color: #ffffff; border: 0px; }"
    btnReset_stylesheet = btnReset_stylesheet + "QPushButton{image: url("+btnReset_visible+")}"
    btn.connect('clicked()', lambda:self.on_modify(node))
    btn.toolTip = self.resourcelist["model_modify.png"]
    btn.setStyleSheet(btnReset_stylesheet)

  def create_btnDelete(self,widget,node,btn):
    btn.clicked.disconnect()
    self.resourcelist["model_delete.png"] = "删除当前的模型"
    btnReset_visible = util.get_resource('model_delete.png')
    btnReset_stylesheet = ""
    btnReset_stylesheet = btnReset_stylesheet + "QToolTip { color: #000000; background-color: #ffffff; border: 0px; }"
    btnReset_stylesheet = btnReset_stylesheet + "QPushButton{image: url("+btnReset_visible+")}"
    btn.connect('clicked()', lambda:widget.on_delete(node))
    btn.toolTip = self.resourcelist["model_delete.png"]
    btn.setStyleSheet(btnReset_stylesheet)

  def create_JSurfaceCutWithUnit(self):
    
    panel = JSurfaceCutWithUnit(self)
    return panel

  def OnArchiveLoaded(self,_a,_b):
    nodes = util.getNodesByClass(util.vtkMRMLModelNode)
    for node in nodes:
      model_type = node.GetAttribute("model_type")
      if model_type:
        self.inner_manager.update_model_type_combox(model_type)

  def create_sliderOpacity2D(self,model_node,opacity_slider):
    util.getModuleLogic("JUITool").registe_model_opacity_2D(opacity_slider,model_node)

  def create_sliderOpacity(self,model_node,opacity_slider):
    util.getModuleLogic("JUITool").registe_model_opacity_3D(opacity_slider,model_node)

  


  def create_btnColor(self,model_node,btn):
    util.getModuleLogic("JUITool").registe_color_button(btn,model_node)


  def on_open_color_pad(self,btn,model_node):
    qdialog = qt.QColorDialog()
    qdialog.connect('colorSelected(QColor)',lambda qcolor:self.on_get_color(qcolor,model_node,btn))
    qdialog.exec()

  def on_get_color(self,qcolor,model_node,btn):
    btn.setStyleSheet("background-color:rgb("+qcolor.red().__str__()+","+qcolor.green().__str__()+","+qcolor.blue().__str__()+");")
    model_node.GetDisplayNode().SetColor([qcolor.red()/255.0,qcolor.green()/255.0,qcolor.blue()/255.0])
  
  def on_modify(self,node):
    bind_segment_id = node.GetAttribute("bind_segment")
    bind_segment = util.GetNodeByID(bind_segment_id)
    if not bind_segment:
      util.showWarningText("当前模型不支持修改，请删除后重建")
      return
    slicer.mrmlScene.InvokeEvent(util.JManagerModel_Modify,node)
  
  

  def on_visible(self,node,is_show):
    print(node.GetID(),is_show)
    if is_show:
      util.ShowNode(node,True)
      node.GetDisplayNode().SetVisibility2D(True)
    else:
      util.HideNode(node)
      node.GetDisplayNode().SetVisibility2D(False)
  

  

class JManagerModelLogic(ScriptedLoadableModuleLogic):
  m_Node = None
  def __init__(self):
    """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
    ScriptedLoadableModuleLogic.__init__(self)
    slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeAddedEvent, self.onNodeAdded)
    slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeRemovedEvent, self.onNodeRemove)

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def onNodeRemoveOuter(self,caller, event, calldata):
    id = calldata.GetAttribute("value")
    node = util.GetNodeByID(id)
    self.onNodeRemove(caller,event,node)

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def onNodeAddedOuter(self,caller, event, calldata):
    self.onNodeAdded(caller,event,calldata)

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def onNodeAdded(self,caller, event, calldata):
    node = calldata
    if isinstance(node, slicer.vtkMRMLModelNode):
      try:
        if isinstance(node, slicer.vtkMRMLFiberBundleNode):
          return
      except Exception as e:
        pass
      util.singleShot(0,lambda:self.m_Widget.inner_manager.on_node_added(node))
      
  @vtk.calldata_type(vtk.VTK_OBJECT)
  def onNodeRemove(self,caller, event, calldata):
    node = calldata
    if isinstance(node, slicer.vtkMRMLModelNode):
      try:
        if isinstance(node, slicer.vtkMRMLFiberBundleNode):
          return
      except Exception as e:
        pass
      self.m_Widget.inner_manager.on_node_removed(node)
      
  def setWidget(self,widget):
    self.m_Widget = widget


  def dynamic_split_model(self,plane_node,source_model_node,OutputPositiveModel,OutputNegativeModel):
    no_name = source_model_node.GetID()+plane_node.GetID()
    old_node =  util.getFirstNodeByName(no_name)
    if old_node:
      util.RemoveNode(old_node)
    dynamicModelerNode = util.CreateNodeByClass("vtkMRMLDynamicModelerNode")
    dynamicModelerNode.SetName(no_name)
    dynamicModelerNode.SetToolName("Plane cut")
    dynamicModelerNode.SetNodeReferenceID("PlaneCut.OutputPositiveModel",OutputPositiveModel.GetID())
    dynamicModelerNode.SetNodeReferenceID("PlaneCut.OutputNegativeModel",OutputNegativeModel.GetID())
    dynamicModelerNode.SetNodeReferenceID("PlaneCut.InputPlane",plane_node.GetID())
    dynamicModelerNode.SetNodeReferenceID("PlaneCut.InputModel",source_model_node.GetID())
    util.AddNode(dynamicModelerNode)

  def dynamic_mirror_model(self,plane_node,source_model_node,OutputModel):
    no_name = source_model_node.GetID()+plane_node.GetID()
    old_node =  util.getFirstNodeByName(no_name)
    if old_node:
      util.RemoveNode(old_node)
    dynamicModelerNode = util.CreateNodeByClass("vtkMRMLDynamicModelerNode")
    dynamicModelerNode.SetName(no_name)
    dynamicModelerNode.SetToolName("Mirror")
    dynamicModelerNode.SetNodeReferenceID("Mirror.InputModel",source_model_node.GetID())
    dynamicModelerNode.SetNodeReferenceID("Mirror.InputPlane",plane_node.GetID())
    dynamicModelerNode.SetNodeReferenceID("Mirror.OutputModel",OutputModel.GetID())
    util.AddNode(dynamicModelerNode)


  def dynamic_append_model(self,source_model_node1,source_model_node2,OutputModel):
    no_name = source_model_node1.GetID()+source_model_node2.GetID()
    old_node =  util.getFirstNodeByName(no_name)
    if old_node:
      util.RemoveNode(old_node)
    dynamicModelerNode = util.CreateNodeByClass("vtkMRMLDynamicModelerNode")
    dynamicModelerNode.SetName(no_name)
    dynamicModelerNode.SetToolName("Append")
    dynamicModelerNode.AddNodeReferenceID("Append.InputModel",source_model_node1.GetID())
    dynamicModelerNode.AddNodeReferenceID("Append.InputModel",source_model_node2.GetID())
    dynamicModelerNode.SetNodeReferenceID("Append.OutputModel",OutputModel.GetID())
    util.AddNode(dynamicModelerNode)

  '''
    将一个模型拆分成多个模型节点
  '''
  def split_model_node(self,model_node):
    import slicer.util as util
    poly = vtk.vtkPolyData()
    poly.DeepCopy(model_node.GetPolyData())
    # 计算连通域
    connectivityFilter = vtk.vtkPolyDataConnectivityFilter()
    connectivityFilter.SetInputData(poly)
    connectivityFilter.SetExtractionModeToSpecifiedRegions()
    connectivityFilter.InitializeSpecifiedRegionList()
    connectivityFilter.Update()
    # 获取连通域数量
    numRegions = connectivityFilter.GetNumberOfExtractedRegions()
    
    # 初始化区域列表
    connectivityFilter.SetExtractionModeToSpecifiedRegions()
    connectivityFilter.InitializeSpecifiedRegionList()

    layoutManager = slicer.app.layoutManager()
    # 对于每个连通域，创建一个 Actor，并使用不同的颜色来渲染
    nodelist = []
    for i in range(numRegions):
      # 获取当前连通域
      connectivityFilter.AddSpecifiedRegion(i)
      connectivityFilter.Update()

      # 将连通域作为 Mapper 的输入
      regionPolyData = vtk.vtkPolyData()
      regionPolyData.DeepCopy(connectivityFilter.GetOutput())

      
      numCells = regionPolyData.GetNumberOfCells()
      if numCells > 100:
        referenceVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode")
        model_node = referenceVolumeNode
        model_node.SetName("Region#:"+numCells.__str__())
        model_node.SetAndObserveMesh(regionPolyData)
        color = np.random.rand(3)
        displayNode = model_node.GetDisplayNode()
        if displayNode is None:
          model_node.CreateDefaultDisplayNodes()
          displayNode = model_node.GetDisplayNode()
        displayNode.SetColor(color[0], color[1], color[2])
        nodelist.append(model_node)
      connectivityFilter.DeleteSpecifiedRegion(i)

    return nodelist