import slicer,qt,vtk,ctk
import slicer.util as util
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from Base.JBaseExtension import JBaseExtensionWidget
#
# UnitTeachingVideo
#


class UnitTeachingVideo(ScriptedLoadableModule):
  
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UnitTeachingVideo"  # TODO: make this more human readable by adding spaces
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
# UnitTeachingVideoWidget
#

class UnitTeachingVideoWidget(JBaseExtensionWidget):
  id = 0
  dialog = None
  buy_url = ""
  def setup(self):
    super().setup()    
    
  def init_ui(self):
    self.ui.btnBuy.connect('clicked()',self.buyMaterial)
    
  def set_teacher_id(self, teacher_id, teacher_name, buy_url):
    self.id = teacher_id
    file_path = self.resourcePath(f'Icons/qrcode{teacher_id}.png')
    print(file_path)
    img = qt.QImage()
    img.load(file_path)
    pixelmap = qt.QPixmap.fromImage(img).scaled(180,180)
    self.ui.lblQrcode.setPixmap(pixelmap)
    self.buy_url = buy_url

  def buyMaterial(self):
    import threading
    thread = threading.Thread(target=self.open_url)
    thread.start()
    thread.join(0.1)
    
  def open_url(self):
    import webbrowser
    print("buy_url:", self.buy_url)
    success = webbrowser.open(self.buy_url)
    print("URL opened:", success)

  def get_widget(self):
    return self.ui.UnitTeachingVideo2

  def set_dialog(self, dialog):
    self.dialog = dialog