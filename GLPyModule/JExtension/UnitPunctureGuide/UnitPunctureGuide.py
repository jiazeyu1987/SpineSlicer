import slicer,qt,vtk,ctk
import slicer.util as util
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from Base.JBaseExtension import JBaseExtensionWidget
#
# UnitPunctureGuide
#


class UnitPunctureGuide(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "UnitPunctureGuide"  # TODO: make this more human readable by adding spaces
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
# UnitPunctureGuideWidget
#

class UnitPunctureGuideWidget(JBaseExtensionWidget):
  def setup(self):
    super().setup()
    self.ui.tabWidget.tabBar().hide()
    
    # unit = BottomUnit("add_file.png","步骤1","测量")
    # util.addWidget2(self.ui.widget_3,unit.uiWidget)
    # self.ui.widget_3.layout().addSpacing(30)
    # unit = BottomUnit("add_file.png","步骤2","测量")
    # util.addWidget2(self.ui.widget_3,unit.uiWidget)
    # self.ui.widget_3.layout().addSpacing(30)
    # unit = BottomUnit("add_file.png","步骤3","测量")
    # util.addWidget2(self.ui.widget_3,unit.uiWidget)
    # unit.setEnabled(False)
    # self.ui.widget_3.layout().addSpacing(30)
    # unit = BottomUnit("add_file.png","步骤4","测量")
    # unit.setEnabled(False)
    # util.addWidget2(self.ui.widget_3,unit.uiWidget)
    # self.ui.widget_3.layout().addSpacing(30)
    # unit = BottomUnit("add_file.png","步骤5","测量")
    # util.addWidget2(self.ui.widget_3,unit.uiWidget)
    # self.ui.widget_3.layout().addSpacing(30)
    # unit = BottomUnit("add_file.png","步骤6","测量")
    # util.addWidget2(self.ui.widget_3,unit.uiWidget)