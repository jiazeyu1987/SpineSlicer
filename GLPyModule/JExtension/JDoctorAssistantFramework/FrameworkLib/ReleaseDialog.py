import slicer,qt,os
import slicer.util as util
from slicer.ScriptedLoadableModule import *
class ReleaseDialog(qt.QDialog,ScriptedLoadableModuleWidget):
  version = ""
  def __init__(self, parent=None):
    super(ReleaseDialog, self).__init__()
    self.setWindowFlag(qt.Qt.FramelessWindowHint)
    self.setAttribute(qt.Qt.WA_TranslucentBackground)  # 使窗口透明
    self.module_path = os.path.dirname(slicer.util.modulePath("FrameworkTop"))
    uiWidget = slicer.util.loadUI(self.module_path + '/Resources/UI/ReleaseDialog.ui')
    slicer.util.addWidget2(self, uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)
    self.ui.btnOK.connect("clicked()",self.on_confirm)
    self.ui.btnCancel.connect("clicked()",self.on_no_more_reminder)
    self.ui.btnClose.connect("clicked()",self.reject)

  def on_confirm(self):
    self.accept()
    util.getModuleWidget("FrameworkTop").on_update_version()

  def set_info(self, version, version_file_path):
    self.version = version
    time_str, data = self.load_json(version_file_path)
    timeInfo = f'<B>{time_str}    {version}版本更新</B>'
    self.ui.lblTime.setText(timeInfo)
    self.ui.lblMainMsg.setText(data)

  def on_no_more_reminder(self):
    util.save_cache_to_PAAA(f"version_{self.version}_no_more_reminder", 1)
    self.reject()
    pass

  def on_update(self):
    self.accept()
    pass

  def load_json(self,file_path):
    import json
    with open(file_path, 'r', encoding='utf-8') as file: 
      first_line = file.readline().strip()    
      # 读取剩余内容
      remaining_content = file.read()
      return first_line,remaining_content
    return "", ""