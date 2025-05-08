import slicer,qt,os
import slicer.util as util

class BottomUnit:
  def __init__(self,pic_path,label,tooltip,buttonsize=64,iconsize=48) -> None:
    absolute_file_path = os.path.abspath(__file__)
    uipath = os.path.join(os.path.dirname(os.path.dirname(absolute_file_path)),"Resources",'UI/BottomUnit.ui')
    self.uiWidget = slicer.util.loadUI(uipath)
    self.uiWidget.setMaximumWidth(buttonsize)
    self.ui = slicer.util.childWidgetVariables(self.uiWidget)
    icon_path = util.get_resource(pic_path)
    util.add_pixel_middle(icon_path,self.ui.pushButton,tooltip,size=iconsize)
    
    self.ui.pushButton.setMaximumWidth(buttonsize)
    self.ui.pushButton.setMinimumWidth(buttonsize)
    self.ui.pushButton.setMaximumHeight(buttonsize)
    self.ui.pushButton.setMinimumHeight(buttonsize)
    self.ui.label_6.setMaximumWidth(buttonsize)
    self.ui.label_6.setMinimumWidth(buttonsize)
    self.ui.label_6.setMaximumHeight(21)
    self.ui.label_6.setMinimumHeight(21)
    
    self.ui.label_6.setText(label)
  
  def set_style_to_toggled(self,func1):
    self.ui.pushButton.setCheckable(True)
    self.ui.pushButton.connect('toggled(bool)',func1)
    self.ui.pushButton.connect('toggled(bool)',self.func_style)
  
  def set_style_to_clicked(self,func1):
    self.ui.pushButton.setCheckable(False)
    self.ui.pushButton.connect('clicked()',func1)
  
  def func_style(self,boolval):
    if boolval:
      stylesheet = "QLabel{color: rgb(0, 255, 0);}"
      self.ui.label_6.setStyleSheet(stylesheet)
    else:
      stylesheet = "QLabel{color: rgb(255, 255, 255);}"
      self.ui.label_6.setStyleSheet(stylesheet)
  
  def get_button(self):
    return self.ui.pushButton
  
  def setChecked(self,boolval):
    self.ui.pushButton.setChecked(boolval)
    
  def isChecked(self):
    return self.ui.pushButton.isChecked()
  
  def isEnabled(self):
    return self.ui.pushButton.isEnabled()
  
  def setEnabled(self,val):
    self.ui.pushButton.setEnabled(val)
    self.ui.label_6.setEnabled(val)
    if val:
      if self.ui.pushButton.isChecked():
        stylesheet = "QLabel{color: rgb(0, 255, 0);}"
        self.ui.label_6.setStyleSheet(stylesheet)
      else:
        stylesheet = "QLabel{color: rgb(255, 255, 255);}"
        self.ui.label_6.setStyleSheet(stylesheet)
    else:
      stylesheet = "QLabel{color: rgb(111, 111, 111);}"
      self.ui.label_6.setStyleSheet(stylesheet)
    
  def setVisible(self,val):
    self.uiWidget.setVisible(val)
    
  def isVisible(self):
    return self.uiWidget.visible