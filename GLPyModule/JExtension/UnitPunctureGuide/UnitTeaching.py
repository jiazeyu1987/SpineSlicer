import slicer,qt,vtk,ctk
import slicer.util as util
import threading
import os
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from Base.JBaseExtension import JBaseExtensionWidget
import UnitPunctureGuideLib.G_UnitPunctureGuide as G
#
# UnitTeaching
#

class TeacherIntroduce:
  data = {}
  teacher_id = ''
  teacher_name = ''
  module_path = ''
  def __init__(self):
    module_path = os.path.dirname(util.modulePath('UnitTeaching'))
    self.module_path = module_path
    ui_path = os.path.join(module_path, 'Resources', 'UI', 'TeacherIntroduce.ui')
    self.uiWidget = slicer.util.loadUI(ui_path)
    self.ui = slicer.util.childWidgetVariables(self.uiWidget)
    self.ui.btnPatent.connect('clicked()',self.show_patent)
    self.ui.btnThesis.connect('clicked()',self.show_thesis)

  def set_hard(self, hard):
    data = util.teacher_info[str(hard)]
    self.teacher_id = data['doctor_id']
    self.teacher_name = data['doctor_name']
    patent = ""
    index = "patent"
    if util.curr_language == 1:
      index = "patent_en"
    if index in data:
      patent = data["patent"]
    if patent != "":
      self.ui.widget_3.show()
    else:
      self.ui.widget_3.hide()
    self.ui.lblPatent.setText(patent)
    self.ui.lblName.setText(self.teacher_name)
    file_path = os.path.join(self.module_path, 'Resources', 'Icons', f'teacher{self.teacher_id}.png')
    img = qt.QImage()
    img.load(file_path)
    pixelmap = qt.QPixmap.fromImage(img).scaled(100,140)
    self.ui.lblPic.setPixmap(pixelmap)
    
    index = ""
    if util.curr_language == 1:
      index = '_en'
    file_path = os.path.join(self.module_path, 'Resources', 'Text', f'advance{self.teacher_id}{index}.txt')

    content = "empty content"
    with open(file_path, "r",encoding="utf-8") as file:
       content = file.read()
    self.ui.lblAdvantage.setText(content)

    file_path = os.path.join(self.module_path, 'Resources', 'Text', f'thesis{self.teacher_id}.pdf')
    if os.path.exists(file_path):
      self.ui.btnThesis.show()
    else:
      self.ui.btnThesis.hide()

    file_path = os.path.join(self.module_path, 'Resources', 'Text', f'patent{self.teacher_id}.pdf')
    
    if os.path.exists(file_path):
      self.ui.btnPatent.show()
    else:
      self.ui.btnPatent.hide()

  def show_patent(self):
    file_path = os.path.join(self.module_path, 'Resources', 'Text', f'patent{self.teacher_id}.pdf')
    self.open_file(file_path)

  def open_file(self, file_path):
    if os.path.exists(file_path):
      try:
        os.startfile(file_path)
      except Exception as e:
        print(f"Failed to open file: {e}")
    else:
      print('file_path error')

  def show_thesis(self):
    file_path = os.path.join(self.module_path, 'Resources', 'Text', f'thesis{self.teacher_id}.txt')
    self.open_file(file_path)
  
  def get_widget(self):
    return self.ui.UnitTeachingIntro2

class UnitTeaching(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UnitTeaching"  # TODO: make this more human readable by adding spaces
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
# UnitTeachingWidget
#

class UnitTeachingWidget(JBaseExtensionWidget):
  teacher_info = {}
  teacher_id = ''
  teacher_name = ''
  buy_url = ''
  material_list = []
  introduce = None
  def setup(self):
    super().setup()
    self.init_config()
    self.introduce = TeacherIntroduce()
    util.addWidget2(self.ui.info_widget, self.introduce.get_widget())
    self.ui.btnDicom.connect('clicked()',self.on_load_example_data)
    self.ui.btnVideo.connect('clicked()',self.show_video)
    self.ui.btnAnaly.connect('clicked()',self.on_load_analysis)
    self.ui.btnBuy.connect('clicked()',self.on_buy)
    self.ui.btnPatent.connect('clicked()',self.show_patent)
    self.ui.btnThesis.connect('clicked()',self.show_thesis)
    self.TagMaps[util.ResetVersion] = slicer.mrmlScene.AddObserver(util.ResetVersion, self.OnResetVersion)
    self.OnResetVersion(None, None)

  def enter(self):
    auto_enter = util.get_cache_from_PAAA("auto_enter","0")
    print("whm test auto_enter ", auto_enter, util.is_load_from_storge)
    if auto_enter != "1" and auto_enter != 1:
      return
    if util.is_load_from_storge:
      print("whm test util.is_load_from_storge = False")
      util.is_load_from_storge = False
      return
    print("whm test")
    self.on_load_example_data()
    pass

  def show_patent(self):
    file_path = self.resourcePath(f'Text/patent{self.teacher_id}.pdf')
    self.open_file(file_path)
    #threading.Thread(target=self.open_file, args=(file_path,)).start()
    pass

  def open_file(self, file_path):
    if os.path.exists(file_path):
      try:
        os.startfile(file_path)
      except Exception as e:
        print(f"Failed to open file: {e}")
    else:
      print('file_path error')

  def show_thesis(self):
    file_path = self.resourcePath(f'Text/thesis{self.teacher_id}.pdf')
    self.open_file(file_path)
    #threading.Thread(target=self.open_file, args=(file_path,)).start()

  def OnResetVersion(self,_a,_b):
    sub_solution_hard = util.get_cache_from_PAAA("sub_solution_hard","1")
    data = util.teacher_info[str(sub_solution_hard)]
    self.teacher_id = data['doctor_id']
    self.teacher_name = data['doctor_name']
    self.material_list = data['materials'].split(',')
    self.buy_url = data['buy_url']
    file_path = self.resourcePath(f'Text/info{self.teacher_id}.txt')
    content = "empty content"
    with open(file_path, "r",encoding="utf-8") as file:
       content = file.read()
    self.ui.lblContent.setText(content)
    self.introduce.set_hard(str(sub_solution_hard))

    file_path = self.resourcePath(f'Text/thesis{self.teacher_id}.pdf')
    
    if os.path.exists(file_path):
      self.ui.btnThesis.hide()
    else:
      self.ui.btnThesis.hide()
    file_path = self.resourcePath(f'Text/patent{self.teacher_id}.pdf')
  

    if os.path.exists(file_path):
      self.ui.btnPatent.hide()
    else:
      self.ui.btnPatent.hide()

  
  def init_config(self):
    util.send_event_str(util.UpdateTitle)

  def on_load_example_data(self):
    sub_solution_hard = util.get_cache_from_PAAA("sub_solution_hard","1")
    data = util.teacher_info[str(sub_solution_hard)]
    sub_solution_dicom = data['dicom']
    util.close_scene()
    file_path = self.get_file_path(data['project'], sub_solution_dicom)
    self.volume = util.loadVolume(file_path)
    self.volume.SetAttribute("main_node","1")
    util.reinit(self.volume)
    util.send_event_str(G.show_volume_rendering)
    util.send_event_str(G.OnFinishCreateLoadTeachingDICOM)
  

  def show_video(self):
    util.getModuleWidget("UnitTeachingVideo").set_teacher_id(self.teacher_id, self.teacher_name, self.buy_url)
    dialog = util.getModuleWidget("JMessageBox").on_popup_ui_dialog("教学视频",util.getModuleWidget("UnitTeachingVideo").get_widget(), 700, 490)
    util.getModuleWidget("UnitTeachingVideo").set_dialog(dialog)
    dialog.exec_()
    return
    import subprocess,os
    sub_solution_video = util.get_cache_from_PAAA("sub_solution_video","teaching.mp4")
    path = self.resourcePath(f'Data/{sub_solution_video}')
    if os.path.exists(path):
        subprocess.run(['start', path], shell=True, check=True)
    else:
      util.showWarningText(f"当前教学视频不存在")
      
  def on_load_analysis(self):
    sub_solution_hard = util.get_cache_from_PAAA("sub_solution_hard","1")
    data = util.teacher_info[str(sub_solution_hard)]
    util.close_scene()
    self.volume = util.loadVolume(self.resourcePath('Data/ct.nrrd'))
    self.volume.SetAttribute("main_node","1")
    t1node = util.loadVolume(self.resourcePath('Data/t1.nrrd'))
    t1node.SetAttribute("main_node","0")
    util.hideVolumeRendering(t1node)
    util.hideVolumeRendering(self.volume)
    util.reinit(self.volume)
    util.send_event_str(G.show_volume_rendering)
    util.send_event_str(G.OnFinishCreateLoadTeachingDICOM)

  def get_file_path(self, moudlule_name, file_name, fold_name="Data"):
    module_path = os.path.dirname(util.modulePath(moudlule_name))
    file_path = (module_path + f'/Resources/{fold_name}/{file_name}').replace("\\", "/")
    print(file_path)
    return file_path

  def on_display_info(self):
    util.getModuleWidget("UnitTeachingIntro").set_teacher_id(self.teacher_id, self.teacher_name)
    dialog = util.getModuleWidget("JMessageBox").on_popup_ui_dialog("讲师介绍",util.getModuleWidget("UnitTeachingIntro").get_widget(), 700, 600)
    util.getModuleWidget("UnitTeachingIntro").set_dialog(dialog)
    dialog.exec_()
  
  def on_buy(self):
    import webbrowser
    #url = "https://www.bilibili.com/video/BV1Xs411W7T2/?vd_source=5f13e2e3c948a8c9e046a3e04a831d00"
    webbrowser.open(self.buy_url)
    return
    util.getModuleWidget("PurchaseMaterial").set_material(self.material_list)
    print(self.material_list)
    dialog = util.getModuleWidget("JMessageBox").on_popup_ui_dialog("设备采购",util.getModuleWidget("PurchaseMaterial").get_widget(), 700, 600)
    util.getModuleWidget("PurchaseMaterial").set_dialog(dialog)
    dialog.exec_()