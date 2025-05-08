import slicer,os,qt
from slicer.ScriptedLoadableModule import *
class Declaration(qt.QDialog,ScriptedLoadableModuleWidget):
  def __init__(self, parent=None):
    super(Declaration, self).__init__()
    self.setWindowFlag(qt.Qt.FramelessWindowHint)
    self.setAttribute(qt.Qt.WA_TranslucentBackground)  # 使窗口透明
    
    # 设置对话框为全屏
    #self.showFullScreen()
    self.module_path = os.path.dirname(slicer.util.modulePath("UnitCreatePunctureGuide"))
    print(self.module_path)
    uiWidget = slicer.util.loadUI(self.module_path + '/Resources/UI/Declaration.ui')
    slicer.util.addWidget2(self, uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)
    self.ui.btnOK.connect("clicked()",self.accept)
    self.ui.btnCancel.connect("clicked()",self.reject)