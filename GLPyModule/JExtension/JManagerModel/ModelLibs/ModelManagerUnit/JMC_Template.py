#
# JManagerModel
#
class JMC_Template:
  node = None
  ui = None
  widget =None
  main = None
  def __init__(self,main,widget,in_ui) -> None:
    self.ui = in_ui
    self.main = main
    self.widget = widget
  
  def setTitle(self,title):
    pass

  def clear_info(self,key):
    pass
  def add_default_info(self,key):
    pass
