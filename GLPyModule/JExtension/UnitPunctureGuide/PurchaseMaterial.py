import slicer,qt,vtk,ctk
import slicer.util as util
import os
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from Base.JBaseExtension import JBaseExtensionWidget
import UnitPunctureGuideLib.G_UnitPunctureGuide as G
import threading
#
# PurchaseMaterial
#
class MaterialItem:
  ui = None
  widget =None
  item = None
  data = None
  def __init__(self, main, in_widget,in_ui, data) -> None:
    self.main = main
    self.widget = in_widget
    self.ui = in_ui
    self.data = data
    self.init_info()
    self.ui.btnBuy.connect('clicked()',self.on_buy)

  #{'id':'1', 'name':'大道发生的撒旦法1', 'price':'￥9.99', 'icon':'material1.png'}
  def init_info(self):
    self.ui.lblName.setText(self.data['name'])
    self.ui.lblPrice.setText(self.data['price'])
    file_path = self.data['icon']
    img = qt.QImage()
    img.load(file_path)
    pixelmap = qt.QPixmap.fromImage(img)
    self.ui.lblIcon.setPixmap(pixelmap)

  def on_buy(self):
    pass

class PurchaseMaterial(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "PurchaseMaterial"  # TODO: make this more human readable by adding spaces
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
# PurchaseMaterialWidget
#

class PurchaseMaterialWidget(JBaseExtensionWidget):
  id = 0
  dialog = None
  display_id_list = {}
  material_list = {}
  def setup(self):
    super().setup()
    self.init_config_data()

  def init_config_data(self):
    import json
    file_path = self.resourcePath(f'Text/materials.json')
    with open(file_path, 'r') as file:
      self.material_list = json.load(file)   
    for material in self.material_list:
      icon = material['icon']
      file_path = self.resourcePath(f'Icons/{icon}')
      material['icon'] = file_path

  def init_list(self):
    self.ui.listWidget.clear()
    for material_id in self.display_id_list:
      print(self.material_list, 'test')
      material = self.material_list[material_id]
      if material == None:
        continue
      icon = material['icon']
      file_path = self.resourcePath(f'Icons/{icon}')
      material['icon'] = file_path
      template1 = slicer.util.loadUI(self.resourcePath("UI/MaterialItem.ui"))
      template1ui = slicer.util.childWidgetVariables(template1)
      template = MaterialItem(self,template1,template1ui,material)
      item = qt.QListWidgetItem(self.ui.listWidget)
      item.setSizeHint(qt.QSize(600 , 64))
      self.ui.listWidget.setItemWidget(item,template.widget)
      self.ui.listWidget.addItem(item)
      
  def set_material(self, id_list):
    self.display_id_list = id_list
    self.init_list()
    self.ui.listWidget.setSpacing(12)

  def get_widget(self):
    return self.ui.PurchaseMaterial2

  def set_dialog(self, dialog):
    self.dialog = dialog