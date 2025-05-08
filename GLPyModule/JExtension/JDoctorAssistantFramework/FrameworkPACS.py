import imp
import os
import re
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
import SimpleITK as sitk
#
# FrameworkPACS
#

class FrameworkPACS(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "FrameworkPACS"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["JPlugins"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["jia ze yu"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """

"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """

"""
class SerieItem:
  ui = None
  def __init__(self, in_ui, series_id, series_des, cover_path) -> None:
    self.ui = in_ui
    self.ui.lbl_des.setText(series_des)
    self.set_label_cover(cover_path)
    self.series_id = series_id
    
  def set_label_cover(self, cover_path):
    scaled_pixmap = qt.QPixmap(cover_path).scaled(qt.QSize(1145, 145), qt.Qt.KeepAspectRatio, qt.Qt.SmoothTransformation)
    self.ui.lbl_cover.setAlignment(qt.Qt.AlignLeft)
    self.ui.lbl_cover.setPixmap(scaled_pixmap)
  
class Saves_Unit:
  ui = None
  widget =None
  item = None
  datas = None
  def __init__(self, main, in_widget,in_ui) -> None:
    self.main = main
    self.widget = in_widget
    self.ui =in_ui
    self.ui.tabWidget.tabBar().hide()
    
    self.ui.btn_enter.connect('clicked()',self.on_enter)
    self.ui.btn_delete.connect('clicked()',self.on_delete)

  def on_enter(self):
    util.send_event_str(util.ProgressStart,"正在加载分析")
    util.send_event_str(util.ProgressValue,10)
    mrb_path = self.datas[2]
    if not qt.QFile(mrb_path).exists():
      util.send_event_str(util.ProgressValue,100)
      util.showWarningText("当前文件不存在: "+mrb_path)
      return
    util.close_scene()
    util.is_load_from_storge = True
    util.send_event_str(util.ProgressValue,30)
    util.getModuleWidget("JMeasure")._onload(mrb_path)
    util.singleShot(10,lambda:util.send_event_str(util.ProgressValue,100))

  def on_delete(self):
    ID = self.datas[0]
    res = util.messageBox(f"确定删除【{self.datas[2]}】吗",windowTitle="警告")
    if res == 0:
      return
    from FrameworkLib.datas import fdb
    fdb.remove_analyse(ID)
    
    pathlist = self.datas[2]
    if os.path.exists(pathlist):
      os.remove(pathlist)
    row = self.main.ui.listWidget.row(self.item)
    self.main.ui.listWidget.takeItem(row)

  def init(self,item,datas):
    import qt
    solution_name = datas[1]
    pathlist = datas[2]
    cover = datas[3]
    recordtime = datas[4]
    
    img = self.ui.label_2
    
  
  
    self.item = item
    self.datas = datas
    
    pixmap = qt.QPixmap()
    pixmap.loadFromData(cover, "PNG")
    pixelmap_scaled = pixmap.scaled(222,111,0,1)
    img.setPixmap(pixelmap_scaled)
    
    self.ui.label.setText("路径:"+pathlist)
    
    self.ui.label_3.setText("项目:"+solution_name)
    self.ui.label_4.setText("保存时间:"+recordtime.split(".")[0])
#
# FrameworkPACSWidget
#

class FrameworkPACSWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  browserWidget = None
  is_start = False
  timer = None
  init_once_flag = False
  current_selected_uid = -1
  current_patient_id = -1
  selectIds = []
  list_series_item = {}
  gender_list = ["男", "女", "其他"]
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

    uiWidget = slicer.util.loadUI(self.resourcePath('UI/FrameworkPACS.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)
    
    uiWidget.setMRMLScene(slicer.mrmlScene)
    
    self.init_ui()

  
  def get_extension(self):
    return "mrb"
  
  def on_load_saves(self):
    file_dialog = qt.QFileDialog()
    file_dialog.setNameFilter('files (*.%s)'%(self.get_extension())) # 过滤器，只显示后缀名为.mrb的文件
    file_dialog.setFileMode(0) # 设置打开文件模式
    if file_dialog.exec_():
        # 获取所选文件的路径
        fileName = file_dialog.selectedFiles()[0]
        if fileName != "":
          filepath = fileName
        else:
          return
    else:
      return
    util.send_event_str(util.ProgressStart,"正在加载数据")
    util.is_load_from_storge = True
    util.send_event_str(util.ProgressValue,30)
    if not qt.QFile(filepath).exists():
      util.send_event_str(util.ProgressValue,100)
      util.showWarningText("当前文件不存在: "+filepath)
      return
    try:
      util.close_scene()
      util.loadScene(filepath)
      util.send_event_str(util.ArchiveFileLoadedEvent)
    except Exception as e:
      import traceback
      traceback.print_exc()
      print("mrb load with exception:"+e.__str__())
    util.singleShot(10,lambda:util.send_event_str(util.ProgressValue,100))

  
    
  
  def init_ui(self):
    import DICOMLib
    self.browserWidget = slicer.modules.dicom.widgetRepresentation().self().browserWidget
    self.browserWidget.setAutoFillBackground(True)
    self.browserWidget.show()
    util.addWidget2(self.ui.widgett1,self.browserWidget)
    self.browserWidget.setAutoFillBackground(True)
    self.browserWidget.show() 
    self.ui.tabWidget.tabBar().hide()
    self.ui.tabWidget_3.tabBar().hide()
    self.ui.tabWidget_2.tabBar().hide()
    dicomBrowser = slicer.modules.dicom.widgetRepresentation().self().browserWidget.dicomBrowser
    dicomDatabase = dicomBrowser.database()
    fields = ['UID', 'PatientsName', 'PatientID', 'PatientsBirthDate', 'PatientsBirthTime', 'PatientsSex', 'PatientsAge', 'PatientsComments', 'InsertTimestamp', 'DisplayedLastStudyDate', 'DisplayedFieldsUpdatedTimestamp', "DisplayedPatientsName", "DisplayedNumberOfStudies"]
    translate = ['PatientsUID','姓名','ID','出生年月','出生时间','性别','年龄','备注','添加时间','DisplayedLastStudyDate','修改时间', "显示姓名","Study个数"]
    for i in range(len(fields)):
      field = fields[i]
      dicomDatabase.setVisibilityForField("Patients", field, True)
      dicomDatabase.setDisplayedNameForField("Patients", field, translate[i])
    show_items = ['PatientsName','PatientsBirthDate','DisplayedFieldsUpdatedTimestamp']
    for item in fields:
      if item not in show_items:
        dicomDatabase.setVisibilityForField("Patients", item, False)
    fields = [ 'StudyDate','StudyID','StudyDescription',  'StudyInstanceUID', 'PatientsUID', 'StudyTime', 'AccessionNumber', 'ModalitiesInStudy', 'InstitutionName', 'ReferringPhysician', 'PerformingPhysiciansName', 'InsertTimestamp', 'DisplayedNumberOfSeries', 'DisplayedFieldsUpdatedTimestamp']
    translate = ['检查日期','StudyID','检查描述', 'StudyInstanceUID', 'PatientsUID',  '检查时间',  '访问号', '检查中的成像方式', '机构名称', '转诊医师', '检查医师姓名', '插入时间戳', '显示的Series数量', '显示字段更新时间戳']
    for i in range(len(fields)):
      field = fields[i]
      dicomDatabase.setVisibilityForField("Studies", field, True)
      dicomDatabase.setDisplayedNameForField("Studies", field, translate[i])
      dicomDatabase.setWeightForField("Studies", field, i)
    show_items = ['StudyDate','DisplayedNumberOfSeries']
    for item in fields:
      if item not in show_items:
        dicomDatabase.setVisibilityForField("Studies", item, False)
    fields = ['SeriesNumber','SeriesDate','SeriesTime', 'SeriesDescription','SeriesInstanceUID', 'StudyInstanceUID',    'Modality', 'BodyPartExamined', 'FrameOfReferenceUID', 'AcquisitionNumber', 'ContrastAgent', 'ScanningSequence', 'EchoNumber', 'TemporalPosition', 'InsertTimestamp', 'DisplayedCount', 'DisplayedSize', 'DisplayedNumberOfFrames', 'DisplayedFieldsUpdatedTimestamp']
    translate = ['Series编号','Series日期','Series时间', 'Series描述', 'SeriesInstanceUID', 'StudyInstanceUID',   '成像方式', '检查部位', '参考帧唯一标识', '采集编号', '路径', '扫描序列', '回波编号', '时间位置', '插入时间戳', '显示计数', '显示大小', '显示帧数', '显示字段更新时间戳']
    for i in range(len(fields)):
      field = fields[i]
      dicomDatabase.setVisibilityForField("Series", field, True)
      dicomDatabase.setDisplayedNameForField("Series", field, translate[i])
      dicomDatabase.setWeightForField("Series", field, i)
    dicomDatabase.setVisibilityForField("Series", 'SeriesInstanceUID', False)
    dicomDatabase.setVisibilityForField("Series", 'StudyInstanceUID', False)
    dicomDatabase.setVisibilityForField("Series", 'SeriesInstanceUID', False)
    dicomDatabase.setVisibilityForField("Series", 'SeriesTime', False)
    show_items = ['SeriesNumber','SeriesDescription','SeriesTime','Modality','DisplayedCount','DisplayedSize','ContrastAgent']
    for item in fields:
      if item not in show_items:
        dicomDatabase.setVisibilityForField("Series", item, False)
    dicomDatabase.setFormatForField("Series", "ContrastAgent", '{"resizeMode":"resizeToContents"}')
    self.ui.tabWidget_2.tabBar().hide()
    self.ui.tabWidget_3.tabBar().hide()
    self.ui.list_series.setSpacing(10)
    stylesheet = self.ui.list_series.styleSheet
    stylesheet += "QListWidget::item:selected { border: 1px solid white; }"
    stylesheet += "QListWidget{background-color: transparent;}"
    self.ui.list_series.setStyleSheet(stylesheet)
    util.singleShot(10,self.init_later)
  
  
  def on_select_changed(self,data):
    seriesTable=slicer.util.findChildren(name="seriesTable")[0]
    seriesTable.selectFirst()

  def init_once(self):
    if self.init_once_flag == True:
      return
    self.init_once_flag = True
    self.hide_search_bar()
  def enter(self):
    self.init_once()
    self.addEvent(True)
    util.singleShot(100,lambda:self.browserWidget.advancedViewButton.setChecked(True))
    self.fresh_analyse_list()

  def fresh_analyse_list(self):
    self.ui.listWidget.clear()
    from FrameworkLib.datas import fdb
    list1 = fdb.get_all_analyse_info()
    print("fresh_analyse_list:",len(list1))
    for result in list1:
      
      template1 = slicer.util.loadUI(self.resourcePath("UI/Saves_Unit.ui"))
      template1ui = slicer.util.childWidgetVariables(template1)
      template = Saves_Unit(self,template1,template1ui)
      item = qt.QListWidgetItem(self.ui.listWidget)
      template.init(item,result)
      item.setSizeHint(qt.QSize(250 , 300))
      self.ui.listWidget.setItemWidget(item,template.widget)
      self.ui.listWidget.addItem(item)
      
      
  def exit(self):
    self.addEvent(False)

  
  def addEvent(self,bool_val):
    if bool_val:
      self.ui.btn_add_file.connect('clicked()', self.on_load_from_file)
      self.ui.btn_add_dicom.connect('clicked()', self.on_load_from_folder)
      self.ui.btn_add_save.connect('clicked()', self.on_load_saves)
      self.ui.btn_add_file2.connect('clicked()', self.on_load_from_file)
      self.ui.btn_add_dicom2.connect('clicked()', self.on_load_from_folder)
      self.ui.btn_add_save2.connect('clicked()', self.on_load_saves)
      slicer.mrmlScene.AddObserver(util.ClearPatientInfo, self.refresh_list)
      self.ui.list_series.connect('itemDoubleClicked(QListWidgetItem *)', self.on_cover_double_clicked)

    else:
      self.ui.btn_add_file.disconnect('clicked()', self.on_load_from_file)
      self.ui.btn_add_dicom.disconnect('clicked()', self.on_load_from_folder)
      self.ui.btn_add_save.disconnect('clicked()', self.on_load_saves)
      self.ui.btn_add_file2.disconnect('clicked()', self.on_load_from_file)
      self.ui.btn_add_dicom2.disconnect('clicked()', self.on_load_from_folder)
      self.ui.btn_add_save2.disconnect('clicked()', self.on_load_saves)
      slicer.mrmlScene.RemoveObserver(util.ClearPatientInfo)
      self.ui.list_series.disconnect('itemDoubleClicked(QListWidgetItem *)', self.on_cover_double_clicked)
      
      
  def sort_table_by_modify_time(self):    
    sort_coloum = 12
    patientsTable=slicer.util.findChildren(name="patientsTable")[0]
    patientsTable.tableView().horizontalHeader().setSortIndicator(sort_coloum, qt.Qt.DescendingOrder)
    patientsTable.tableView().sortByColumn(sort_coloum, qt.Qt.DescendingOrder)
    util.singleShot(10,lambda:patientsTable.tableView().selectRow(0))
    
  def init_later(self):
    patientsTable = slicer.util.findChildren(name="patientsTable")[0]
    patientsTable.connect('selectionChanged(QStringList)',self.on_selection_changed)
    series_table = slicer.util.findChildren(name="seriesTable")[0]
    series_table.connect('selectionChanged(QStringList)',self.on_series_selection_changed)
    toolbar = util.findChildren(name="ToolBar")[0]
    toolbar.hide()
    self.sort_table_by_modify_time()
  
  def on_cover_double_clicked(self, item):
    series_id = ""
    for key, value in self.list_series_item.items():
      if value == item:
        series_id = key
        break
    if series_id == "":
      return
    file_list = slicer.dicomDatabase.filesForSeries(series_id)
    if len(file_list) == 0:
      return
    file_path = file_list[0]
    if not qt.QFile(file_path).exists():
      util.getModuleWidget("JMessageBox").show_infomation('提示', '文件已被移除', 1)
      return
    util.send_event_str(util.ProgressStart,"正在加载数据")
    util.send_event_str(util.ProgressValue,30)
    util.is_load_from_storge = True
    loadedVolumeNode = util.loadVolume(file_list[0])
    loadedVolumeNode.SetAttribute("filepath",file_list[0])
    slicer.mrmlScene.InvokeEvent(util.NewFileLoadedFromMain,None)
    util.singleShot(10,lambda:util.send_event_str(util.ProgressValue,100))
    pass
  
  def natural_sort_key(self, s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]
  
  def get_series_png(self, series_id):
    tmp_str = series_id.replace('.', '')
    storage_dir = qt.QStandardPaths.writableLocation(qt.QStandardPaths.GenericDataLocation)
    target_path = f'{storage_dir}/paaa'
    if not os.path.exists(target_path):
      os.mkdir(target_path)
    target_path = f'{storage_dir}/paaa/cover'
    if not os.path.exists(target_path):
      os.mkdir(target_path)
    cover_path = f'{storage_dir}/paaa/cover/{tmp_str}.png'
    if qt.QFile(cover_path).exists():
      return cover_path
    fileList = sorted(slicer.dicomDatabase.filesForSeries(series_id), key=self.natural_sort_key)
    # 2. 计算序列长度
    file_numbers = len(fileList)
    file_name = fileList[int(file_numbers/2)]
    self.create_cover(file_name, cover_path)
    return cover_path

  def _on_load_from_folder(self,dicomDataDir):
      from DICOMLib import DICOMUtils
      res = DICOMUtils.importDicom(dicomDataDir, slicer.dicomDatabase)
      
  def refresh_list(self, _a, _b):
    self.fresh_analyse_list()

  def on_load_from_folder(self):
      if True:
        res_path,result =util.show_file_dialog(2)
        if result == 0:
          return
        else:
          dicomDataDir = res_path
      util.send_event_str(util.ProgressStart,"正在加载数据")
      util.send_event_str(util.ProgressValue,30)
      util.is_load_from_storge = True
      self._on_load_from_folder(dicomDataDir)
      util.singleShot(10,lambda:util.send_event_str(util.ProgressValue,100))
      self.sort_table_by_modify_time()   
      
  def create_cover(self, file, path):
    image = sitk.ReadImage(file)
    image_array = sitk.GetArrayFromImage(image)
    # 获取图像信息
    spacing = image.GetSpacing()
    window_center = 0
    window_width = 500
    if not image.GetMetaData("0028|1050"):
      window_center = int(image.GetMetaData("0028|1050").split("\\")[0])
      window_width = int(image.GetMetaData("0028|1051").split("\\")[0])
    # 将像素值缩放到 0-255 范围
    min_pixel_value = window_center - 0.5 * window_width
    max_pixel_value = window_center + 0.5 * window_width
    image_array = 255 * (image_array - min_pixel_value) / (max_pixel_value - min_pixel_value)
    image_array[image_array < 0] = 0
    image_array[image_array > 255] = 255
    image_array = image_array.astype('uint8')
    sitk.WriteImage(sitk.GetImageFromArray(image_array), path)

  def on_load_from_file(self):
    try:
      if True:
        res_path,result =util.show_file_dialog(0)
        if result == 0:
          return
        else:
          NrrdPath = res_path
    except Exception as e:
      util.showWarningText("加载文件失败")
      return
    util.send_event_str(util.ProgressStart,"正在加载数据")
    util.send_event_str(util.ProgressValue,30)
    util.is_load_from_storge = True
    loadedVolumeNode = util.loadVolume(NrrdPath)
    loadedVolumeNode.SetAttribute("filepath",NrrdPath)
    slicer.mrmlScene.InvokeEvent(util.NewFileLoadedFromMain,None)
    util.singleShot(10,lambda:util.send_event_str(util.ProgressValue,100))

  def on_selection_changed(self,list1):
    self.selectIds = list1
    if len(list1) == 0:
      return
    self.current_patient_id = list1[0]
    study_list = slicer.dicomDatabase.studiesForPatient(self.current_patient_id)
    series_list = []
    for study in study_list:
      tmp_list = slicer.dicomDatabase.seriesForStudy(study)
      series_list.extend(tmp_list)
    self.ui.list_series.clear()
    self.list_series_item.clear()
    for series_id in series_list:
      series_des = slicer.dicomDatabase.descriptionForSeries(series_id)
      png_path = self.get_series_png(series_id)
      template1 = slicer.util.loadUI(self.resourcePath("UI/SerieItem.ui"))
      template1ui = slicer.util.childWidgetVariables(template1)
      template = SerieItem(template1ui, series_id, series_des, png_path)
      item = qt.QListWidgetItem(self.ui.list_series)
      item.setSizeHint(qt.QSize(150, 180))
      self.ui.list_series.setItemWidget(item, template1)
      self.ui.list_series.addItem(item)
      self.list_series_item[series_id] = item
    
  def on_series_selection_changed(self, list1):
    if len(list1) == 0:
      return
    current_series_id = list1[0]    
    item = self.list_series_item.get(current_series_id, None)
    if item == None:
      return
    for value in self.list_series_item.values():
      value.setSelected(False)
    item.setSelected(True)
    
    
  def hide_search_bar(self):
    #隐藏搜索栏
    slicer.util.findChildren(name="studiesSearchBox")[0].setVisible(0)
    slicer.util.findChildren(name="patientsSearchBox")[0].setVisible(0)
    slicer.util.findChildren(name="seriesSearchBox")[0].setVisible(0)
    slicer.util.findChildren(name="lblSeries")[0].setVisible(0)
    util.findChildren(name="lblStudies")[0].setVisible(0)
    slicer.util.findChildren(name="lblPatients")[0].setVisible(0)
    patientsTable=slicer.util.findChildren(name="patientsTable")[0]
    #if util.getjson2("FrameworkPACS","FrameworkPACS_only_one_select") == "2":
    #禁用Patients栏位的双击事件
    patientsTable.tableView().setSelectionBehavior(qt.QAbstractItemView.SelectRows)
    patientsTable.tableView().setSelectionMode(qt.QAbstractItemView.SingleSelection)
    patientsTable.tableView().setEditTriggers(qt.QAbstractItemView.NoEditTriggers)
    patientsTable.tableView().horizontalHeader().setDefaultAlignment(qt.Qt.AlignVCenter)
    patientsTable.tableView().setShowGrid(False)
    patientsTable.tableView().horizontalHeader().setHighlightSections(False)
    patientsTable.tableView().setFocusPolicy(qt.Qt.NoFocus)
    patientsTable.tableView().setSizeAdjustPolicy(0)
    studiesTable=slicer.util.findChildren(name="studiesTable")[0]
    #studiesTable.disconnect("doubleClicked( const QModelIndex& )")
    studiesTable.tableView().setSelectionBehavior(qt.QAbstractItemView.SelectRows)
    #studiesTable.tableView().setSelectionMode(qt.QAbstractItemView.SingleSelection)
    studiesTable.tableView().horizontalHeader().setDefaultAlignment(qt.Qt.AlignVCenter)
    studiesTable.tableView().setShowGrid(False)
    studiesTable.tableView().horizontalHeader().setHighlightSections(False)
    studiesTable.tableView().setFocusPolicy(qt.Qt.NoFocus)
    
    seriesTable=slicer.util.findChildren(name="seriesTable")[0]
    #seriesTable.disconnect("doubleClicked( const QModelIndex& )")
    seriesTable.tableView().setSelectionBehavior(qt.QAbstractItemView.SelectRows)
    #seriesTable.tableView().setSelectionMode(qt.QAbstractItemView.SingleSelection)
    seriesTable.tableView().horizontalHeader().setDefaultAlignment(qt.Qt.AlignVCenter)
    seriesTable.tableView().setShowGrid(False)
    seriesTable.tableView().horizontalHeader().setHighlightSections(False)
    seriesTable.tableView().setFocusPolicy(qt.Qt.NoFocus)

    
    patientsTable.tableView().horizontalHeader().setMinimumHeight(30)
    patientsTable.tableView().horizontalHeader().setMaximumHeight(30)
    studiesTable.tableView().horizontalHeader().setMinimumHeight(30)
    studiesTable.tableView().horizontalHeader().setMaximumHeight(30)
    seriesTable.tableView().horizontalHeader().setMinimumHeight(30)
    seriesTable.tableView().horizontalHeader().setMaximumHeight(30)

