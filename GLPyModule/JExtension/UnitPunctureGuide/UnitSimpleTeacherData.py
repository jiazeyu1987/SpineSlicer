import slicer,qt,vtk,ctk,os
import slicer.util as util
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from Base.JBaseExtension import JBaseExtensionWidget
from AddFiberLib.NormalUnit import NormalUnit
import UnitPunctureGuideLib.G_UnitPunctureGuide as G
import UnitPunctureGuideStyle as style
#
# UnitSimpleTeacherData
#

    
    
    

class UnitSimpleTeacherData(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UnitSimpleTeacherData"  # TODO: make this more human readable by adding spaces
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
# UnitSimpleTeacherDataWidget
#

class UnitSimpleTeacherDataWidget(JBaseExtensionWidget):
  
  def init_ui(self):
    self.ui.btnDicom.connect('clicked()',self.on_add_data_1)
    self.ui.btnDicom_2.connect('clicked()',self.on_add_data_2)
    self.ui.btnDicom_3.connect('clicked()',self.on_load_single_folder)

    style1 = "background-image: url(bin/images/CTColor.png);"
    self.ui.btnDicom.setStyleSheet(style1)
    self.ui.btnDicom_2.setStyleSheet(style1)
    self.ui.btnDicom_3.setStyleSheet(style1)
    module_path = os.path.dirname(util.modulePath('UnitPunctureGuide'))
    style.set_simple_teacher_data_style(module_path, self.ui)
  
    
  '''
    读取文件夹
    读取文件夹下的数据,如果文件夹下只有一个序列,那么不提示
    如果有多个序列,那么提示选择一个
  '''
  def on_load_single_folder(self):
      dicomDataDir = "E:/"  # input folder with DICOM files
      res_path,result =util.show_file_dialog(2)
      if result == 0:
        return
      else:
        dicomDataDir = res_path
        
      from DICOMLib import DICOMUtils
      loadedNodeIDs = []
      
      with DICOMUtils.TemporaryDICOMDatabase() as db:
          DICOMUtils.importDicom(dicomDataDir, db)
          patientUIDs = db.patients()
          for patientUID in patientUIDs:
            loadedNodeIDs.extend(DICOMUtils.loadPatientByUID(patientUID))
            
      for loadedNodeID in loadedNodeIDs:
          node = slicer.mrmlScene.GetNodeByID(loadedNodeID)
          if util.isinstance(node,slicer.vtkMRMLScalarVolumeNode):
            self.volume = node
            
            util.set_main_node(self.volume,False)
            print("OOOOOOOOOOOOOOOOO:",self.volume.GetID())
            util.send_event_str(G.show_volume_rendering)
            util.send_event_str(G.OnFinishCreateLoadTeachingDICOM)
            util.reinit(self.volume)
            return node
            
            
            
  def on_add_data_1(self):
    print("on_add_data_1")
    import os
    file_path =  util.getModuleWidget("UnitPunctureGuide").resourcePath("Data/teaching_data.nrrd")
    self.volume = util.loadVolume(file_path)
    util.set_main_node(self.volume,False)
    
    slice_node = slicer.app.layoutManager().sliceWidget("Red").mrmlSliceNode()
    slice_node.SetWidgetOutlineVisible(True)
    util.reinit(self.volume)
    util.send_event_str(G.show_volume_rendering)
    util.send_event_str(G.OnFinishCreateLoadTeachingDICOM)
    
  def on_add_data_2(self):
    print("on_add_data_2")
    import os
    latest_save_path = util.get_from_PAAA("latest_save_path","-1")
    if latest_save_path == "-1":
      util.showWaitText("当前还没有存档")
      return
    
    util.send_event_str(util.ProgressStart,"正在加载分析")
    util.send_event_str(util.ProgressValue,10)
    mrb_path = latest_save_path
    if not qt.QFile(mrb_path).exists():
      util.send_event_str(util.ProgressValue,100)
      util.showWarningText("当前文件不存在: "+mrb_path)
      return
    util.close_scene()
    util.is_load_from_storge = True
    util.send_event_str(util.ProgressValue,30)
    util.getModuleWidget("JMeasure")._onload(mrb_path)
    util.singleShot(1000,lambda:util.send_event_str(util.ArchiveFileLoadedEvent))
    util.singleShot(10,lambda:util.send_event_str(util.ProgressValue,100))
    
  def on_add_data_3(self):
    util.layout_panel("middle_left").setMaximumWidth(10000000)
    util.layout_panel("middle_left").setMinimumWidth(400)
    util.layout_panel("middle_left").setModule("FrameworkPACS")
    slicer.util.findChildren(name="CentralWidget")[0].hide()
    util.send_event_str(util.DoctorAssitButttonResetState)
    util.layout_panel("middle_left").show()