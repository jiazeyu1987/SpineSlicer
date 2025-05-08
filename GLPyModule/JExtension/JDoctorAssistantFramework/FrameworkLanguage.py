import slicer,qt,vtk,ctk,os,requests,json,pickle
import slicer.util as util
import re
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from Base.JBaseExtension import JBaseExtensionWidget
#
# FrameworkLanguage
#


class FrameworkLanguage(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "FrameworkLanguage"  # TODO: make this more human readable by adding spaces
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
# FrameworkLanguageWidget
#

class FrameworkLanguageWidget(JBaseExtensionWidget):
  dialog = None
  def setup(self):
    super().setup()
    self.ui.btnCancel.connect("clicked()", self.on_cancel)
    self.ui.btnConfirm.connect("clicked()", self.on_confirm)
    self.ui.widget.setStyleSheet("#widget{background-color: #1C1D1D}")
    listView = qt.QListView()
    self.ui.cmbLanguage.setView(listView)
    language = int(util.get_from_PAAA("qm_type", "0"))
    self.ui.cmbLanguage.setCurrentIndex(language)

  def on_cancel(self):
    self.dialog.close()
    pass

  def on_confirm(self):
    index = self.ui.cmbLanguage.currentIndex
    util.save_to_PAAA("qm_type", index)
    info = util.tr("语言切换为中文，重启后生效")
    if index == 1:
      info = util.tr("语言切换为英文，重启后生效")
    util.showWarningText(info)
    self.dialog.close()
    pass

  def set_dialog(self, dialog):
    self.dialog = dialog
  
  def get_widget(self):
    return self.ui.widget
  