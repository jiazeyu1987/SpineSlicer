import slicer,qt,vtk,ctk,time
import slicer.util as util
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from Base.JBaseExtension import JBaseExtensionWidget
from FrameworkLib.datas import fdb
import numpy as np
#
# UnitScore
#
class ScoreItem:
  ui = None
  widget =None
  item = None
  data = None
  def __init__(self, main, in_widget,in_ui, time, score) -> None:
    self.main = main
    self.widget = in_widget
    self.ui = in_ui
    self.ui.lblScore.setText(score)
    self.ui.lblTime.setText(time)

class UnitScore(ScriptedLoadableModule):
  
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UnitScore"  # TODO: make this more human readable by adding spaces
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
# UnitScoreWidget
#

class UnitScoreWidget(JBaseExtensionWidget):
  button_map = {}
  #穿刺导板----是否创建了血肿（没有扣5分）
  create_tumor = False
  #穿刺导板----是否创建了通道（没有扣5分）
  create_channel = False
  #穿刺导板----创建通道的时候是否调整了参数（没有任何调整扣1分）
  adjust_channel_value = False
  #穿刺导板----是否创建了面具（没有扣5分）
  create_mask = False
  #穿刺导板----是否创建了皮肤（没有扣2分）
  create_skin = False
  #穿刺导板----是否创建了颅骨（没有扣1分）
  create_bone = False
  #穿刺导板----是否进行了灰度调整（没有扣1分）
  do_gray_scale = False
  #穿刺导板----是否进行了MPR调整（没有扣1分）
  do_mpr = False
  #通用----从导入第一个数据到创建导板的时间(每过2分钟扣1分）
  start_time = -1000000
  #通用----是否导出了stl文件（没有扣2分）
  do_export_stl = False

  create_bone_before_segment = False
  do_opacity_adjust = False
  do_register_before_click_bone_segment = False
  do_generate_point_set_before_generate_segment = False
  do_smooth = False
  do_expend = False
  do_shrink = False

  auto_select_red_after_segment = 0
  total_score = 100
  score_list = []
  def setup(self):
    super().setup()
    
    
  def init_ui(self):    
    self.TagMaps[util.ResetVersion] = slicer.mrmlScene.AddObserver(util.ResetVersion, self.OnResetVersion)
    self.ui.btnScore.connect('clicked()', self.on_score)
    self.ui.btnUpload.connect('clicked()',self.on_upload_score)
    self.ui.btnFresh.connect('clicked()',self.on_fresh_list)
    self.ui.btnUpload.setEnabled(False)
    data = fdb.get_score_list()
    if data != None:
      self.score_list = []
      for item in data:
        self.score_list.append(item[0])
      self.display_score_list()

  
  def on_fresh_list(self):
    isSucceed,val = util.httplib.httppost("/system/passport/score_list",None)
    if isSucceed:
      print("get score list:",val)
      info = val['msg']
      self.score_list = info.split("&$&")
      fdb.refresh_local_score(self.score_list)
      self.display_score_list()

  def display_score_list(self):
    self.ui.listScore.clear()
    solution_name = util.get_cache_from_PAAA("solution_name")
    for score_str in reversed(self.score_list):
      print(score_str)
      tmp_list = score_str.split("&*&")
      if len(tmp_list) < 3:
        continue
      if tmp_list[0] != solution_name:
        continue
      self.add_item_to_list(tmp_list[1], tmp_list[2])

  def add_item_to_list(self, score, time):
    list_width = self.ui.listScore.width - 10
    template1 = slicer.util.loadUI(self.resourcePath("UI/ScoreItem.ui"))
    template1ui = slicer.util.childWidgetVariables(template1)
    template = ScoreItem(self,template1,template1ui,time,score)
    item = qt.QListWidgetItem(self.ui.listScore)
    item.setSizeHint(qt.QSize(list_width , 36))
    self.ui.listScore.setItemWidget(item,template.widget)
    print(time)
    self.ui.listScore.addItem(item)

  def on_upload_score(self):
    json1 = {}
    json1['score'] = self.total_score
    json1['project'] = util.get_cache_from_PAAA("solution_name")
    isSucceed,val = util.httplib.httppost("/system/passport/add_score",json1)
    if isSucceed:
      self.ui.btnUpload.setEnabled(False)
      qt.QTimer.singleShot(1000, self.on_fresh_list)
      print("upload score succeed", val)
    else:
      print("upload score fail",val)

  def on_score(self):
    solution_name = util.get_cache_from_PAAA("solution_name")
    if solution_name == "UnitPunctureGuide":
      self.on_puncture_guide_score()
    elif solution_name == "UnitProtectionHat":
      self.on_protection_hat_score()
    elif solution_name == "UnitRepairSkull":
      self.on_repair_skull_score()
    pass

  #此方法放到计分的最前面，因为要初始化总分
  def init_score_and_overtime_score(self):
    self.total_score = 100
    curr_time = time.perf_counter()
    inter_time = curr_time - self.start_time
    print('score on_score ', inter_time, curr_time, self.start_time)
    minus_score = int(inter_time/120)
    self.total_score = self.total_score - minus_score

  def deal_ui_after_score(self):    
    print(self.total_score)
    self.ui.lblScore.setText(f"您本次得分为{self.total_score}")
    self.ui.btnUpload.setEnabled(True)

  def on_protection_hat_score(self):
    model_node = util.getFirstNodeByName("SkullHatModel")
    if not model_node:
      util.showWarningText("请先在【自动镂空】里【生成保护帽】")
      return
    self.init_score_and_overtime_score()
    if not self.create_bone_before_segment:
      self.total_score = self.total_score - 1
    self.total_score = self.total_score - self.auto_select_red_after_segment
    if not self.do_opacity_adjust:
      self.total_score = self.total_score - 1
    if not self.do_generate_point_set_before_generate_segment:
      self.total_score = self.total_score - 1
    if not self.do_smooth:
      self.total_score = self.total_score - 1
    if not self.do_expend:
      self.total_score = self.total_score - 1
    if not self.do_shrink:
      self.total_score = self.total_score - 1
    if not self.do_export_stl:
      self.total_score = self.total_score - 1
    self.deal_ui_after_score()
    pass

  def on_repair_skull_score(self):
    node = util.getFirstNodeByName("SkullModel")
    if not node:
      util.showWarningText("请先创建颅骨碎片")
      return
    self.init_score_and_overtime_score()
    if not self.create_bone_before_segment:
      self.total_score = self.total_score - 1
    self.total_score = self.total_score - self.auto_select_red_after_segment
    if not self.do_opacity_adjust:
      self.total_score = self.total_score - 1
    if not self.do_register_before_click_bone_segment:
      self.total_score = self.total_score - 1
    if not self.do_generate_point_set_before_generate_segment:
      self.total_score = self.total_score - 1
    if not self.do_smooth:
      self.total_score = self.total_score - 1
    if not self.do_expend:
      self.total_score = self.total_score - 1
    if not self.do_shrink:
      self.total_score = self.total_score - 1
    if not self.do_export_stl:
      self.total_score = self.total_score - 1
    self.deal_ui_after_score()
    pass

  def on_puncture_guide_score(self):
    node = util.getFirstNodeByName("导板")
    if not node:
      util.showWarningText("请先创建导板")
      return
    self.init_score_and_overtime_score()
    if not self.create_tumor:
      self.total_score = self.total_score - 5
    if not self.create_channel:
      self.total_score = self.total_score - 5
    if not self.adjust_channel_value:
      print("test not adjust channel value")
      self.total_score = self.total_score - 1
    if not self.create_mask:
      self.total_score = self.total_score - 5
    if not self.create_skin:
      self.total_score = self.total_score - 2
    if not self.create_bone:
      self.total_score = self.total_score - 1
    if not self.do_gray_scale:
      self.total_score = self.total_score - 1
    if not self.do_mpr:
      self.total_score = self.total_score - 1
    if not self.do_export_stl:
      self.total_score = self.total_score - 2
    self.deal_ui_after_score()
    pass

  def exit(self):
    pass
  
  def OnResetVersion(self,_a,_b):
    self.display_score_list()
    
  def set_project_start(self):
    self.start_time = time.perf_counter()
    print('score start_time = ', self.start_time)
    self.create_tumor = False
    self.create_channel = False
    self.adjust_channel_value = False
    self.create_mask = False
    self.create_skin = False
    self.create_bone = False
    self.do_gray_scale = False
    self.do_mpr = False
    self.do_export_stl = False

    self.create_bone_before_segment = True
    self.do_opacity_adjust = False
    self.do_register_before_click_bone_segment = True
    self.do_generate_point_set_before_generate_segment = True
    self.do_smooth = False
    self.do_expend = False
    self.do_shrink = False
    self.auto_select_red_after_segment = 0
    self.total_score = 100
    self.ui.lblScore.setText("")

  def auto_select_red(self):
    self.auto_select_red_after_segment = self.auto_select_red_after_segment + 1
    if self.auto_select_red_after_segment > 5:
      self.auto_select_red_after_segment = 5