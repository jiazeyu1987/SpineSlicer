import slicer,vtk,ctk,qt
import slicer.util as util


class SubProject:
  main = None
  TagMaps = {}
  def __init__(self,main):
    self.main = main

  def init_sub_project(self):
    print("init_sub_project")