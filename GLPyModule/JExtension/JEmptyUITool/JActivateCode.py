import imp
import os
from re import A
from tabnanny import check
from time import sleep
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import slicer.util as util
import SlicerWizard.Utilities as su 
import numpy as np


#
# JActivateCode
#

class JActivateCode(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "JActivateCode"  # TODO: make this more human readable by adding spaces
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
# JActivateCodeWidget
#

class JActivateCodeWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  def __init__(self, parent=None):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)  # needed for parameter node observation
    self.logic = None

  def setup(self):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    self.logic = JActivateCodeLogic()
    self.logic.setWidget(self)
    

class JActivateCodeLogic(ScriptedLoadableModuleLogic):
  def __init__(self):
    """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
    ScriptedLoadableModuleLogic.__init__(self)
    slicer.mrmlScene.AddObserver(slicer.vtkMRMLScene.NodeAddedEvent, self.onNodeAdded)
  

  def setWidget(self,widget):
    self.m_Widget = widget

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def onNodeAdded(self,caller, event, calldata):
    node = calldata
    #if isinstance(node, slicer.vtkMRMLMarkupsFiducialNode):
      #self.m_Widget.on_node_added(node)


  # 获取当前系统的 CPU ID
  def get_cpu_id(self):
    import platform
    cpu_id = platform.processor()
    return cpu_id


  def get_volume_id(self):
    str = util.mainWindow().GetVolumeID()
    return str

  def get_mac_id(self):
    str = util.mainWindow().GetMac()
    return str

  # 如果文件不存在，则创建并写入 CPU ID，否则读取已有的 CPU ID
  def create_or_read_file(self,file_name):
    #if not os.path.exists(file_name):
        with open(file_name, 'w') as f:
            id = self.get_mac_id()
            hashed_id = self.hash_id(id)
            hashed_id = hashed_id[-6:]
            f.write(hashed_id)
            return hashed_id
    #


  # 对 CPU ID 进行哈希
  def hash_id(self,id):
    import hashlib
    return hashlib.sha256(id.encode()).hexdigest()


  # md5加密
  def md5_string(self,in_str):
      import hashlib
      md5 = hashlib.md5()
      md5.update(in_str.encode("utf8"))
      result = md5.hexdigest()
      return result
  
  #识别cpu id,并将识别的ID存储到一个文件中,如果文件不存在就创建这个文件
  def makesure_key_file(self):
    key_path = slicer.app.slicerHome+"/key.txt"
    print("key_path:",key_path)
    return self.create_or_read_file(key_path)
  
  def makesure_lock_file(self):
    key_path = slicer.app.slicerHome+"/lock.txt"
    print("lock_path:",key_path)
    
    return self.create_or_read_file(key_path)
  
  def save_lock_file(self,info):
    key_path = slicer.app.slicerHome+"/lock.txt"
    with open(key_path, 'w') as f:
            f.write(info)
            return info

  def mac_md5_str(self):
    return self.md5_string(util.mainWindow().GetMac())

  def made(self): #生成激活码
    import random
    fo = open("E:/test.txt", "w")
    str1 = ""
    for i in range(1000):
      activation_code = ''.join(random.sample('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',32)).replace(" ","")#python3语法
      str1 = str1 + activation_code
      str1 = str1 + "&"
      str1 = str1 + "\n"
    fo.write(str1)

   
  # PS. verify_activate_code('UY5Q13697SE0XKIPTOJBR4LMCFAHGZ8V')
  def verify_activate_code(self,activate_code):
    return False
    