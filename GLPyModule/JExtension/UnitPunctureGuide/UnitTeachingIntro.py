import slicer,qt,vtk,ctk
import slicer.util as util
import os
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from Base.JBaseExtension import JBaseExtensionWidget
import UnitPunctureGuideLib.G_UnitPunctureGuide as G
import threading
#
# UnitTeachingIntro
#


class UnitTeachingIntro(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UnitTeachingIntro"  # TODO: make this more human readable by adding spaces
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
# UnitTeachingIntroWidget
#

class UnitTeachingIntroWidget(JBaseExtensionWidget):
  id = 0
  dialog = None
  def setup(self):
    super().setup()
    self.ui.btnPatent.connect('clicked()',self.show_patent)
    self.ui.btnThesis.connect('clicked()',self.show_thesis)

  def set_teacher_id(self, id, name):
    self.id = id
    self.ui.lblName.setText(name)
    file_path = self.resourcePath(f'Icons/teacher{id}.png')
    img = qt.QImage()
    img.load(file_path)
    pixelmap = qt.QPixmap.fromImage(img)
    self.ui.lblPic.setPixmap(pixelmap)
    file_path = self.resourcePath(f'Icons/info{id}.txt')
    content = "empty content"
    with open(file_path, "r") as file:
       content = file.read()
    self.ui.lblContent.setText(content)

  def show_patent(self):
    file_path = self.resourcePath(f'Icons/patent{self.id}.pdf')
    threading.Thread(target=self.open_file, args=(file_path,)).start()
    self.dialog.close()
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
    file_path = self.resourcePath(f'Icons/thesis{self.id}.pdf')
    threading.Thread(target=self.open_file, args=(file_path,)).start()
    self.dialog.close()

  def get_widget(self):
    return self.ui.UnitTeachingIntro2

  def set_dialog(self, dialog):
    self.dialog = dialog