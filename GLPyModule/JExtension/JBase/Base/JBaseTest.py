import vtk, qt, ctk, slicer, os
from slicer.ScriptedLoadableModule import *
import slicer.util as util
import time




class JBaseTest(ScriptedLoadableModuleTest):
  #case index
  index = 0
  #action index
  action_index = 0
  #case information
  info = ""
  #main widget
  widget = None
  #current case list concat from action data info(multi bundle data info)
  current_case_list = None
  #all bundles
  bundle_map = {}
  #all actions
  action_list = []
  
  module_name = ""
  module_path = ""
  module_directory = ""
  paramap = {}
  
  def setUp(self):
    
    
    self.index = 0
    self.action_index = 0
    self.info = ""
    self.widget = None
    self.current_case_list = None
    self.bundle_map ={}
    self.action_list = []
    self.module_name = ""
    self.module_path = ""
    self.classname = self.__class__.__name__
    if self.classname.count("Test") != 1:
      raise Exception("error class name")
    index = self.classname.find("Test")
    if index != -1:
        self.module_name = self.classname[:index]
    else:
      raise Exception("error class name of:",self.classname)
    
    module_path = f"Test.{self.classname}_Bundle"
    import importlib
    module = importlib.import_module(module_path)
    module.init_bundle(self)
    
    module_path = f"Test.{self.classname}_Action"
    import importlib
    module = importlib.import_module(module_path)
    module.init_action(self)
    
    self.widget = util.getModuleWidget(self.module_name)
    
    
          
    slicer.mrmlScene.Clear(0)
    
    # import Test.JManagerScalarVolume_Action as ac
    # import Test.JManagerScalarVolume_Bundle as ab
    # import Test.JManagerScalarVolume_Case as ca
    # self.widget = util.getModuleWidget(self.module_name)
    # ca.init_case(self)
    # ab.init_bundle(self)
    # ac.init_action(self)
    

  def runTest(self):
      self.setUp()
      util.create_log_file(self.module_directory)
      util.write_test_log(f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<{self.module_name} start unit test >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
      self.test_case(0)
  
  def next_index(self):
    self.set_index(self.index+1)
  
  def continue_test(self,time=0):
    self.next_index()
    util.singleShot(time,lambda:self.test_case(self.index))
    
  def finish_test(self):
    self.index = len(self.current_case_list)+1
    self.next_index()
    util.singleShot(time,lambda:self.test_case(self.index))

  def test_error(self):
    self.assertEqual(1, 3)
    self.continue_test()
  
  def finish_test(self):
    import subprocess
    util.singleShot(10,lambda:util.write_test_log(f"\n\n\n{self.index} test Done"))
    # 用notepad打开文本文件
    file_path = util.unit_test['log_file_path']
    subprocess.Popen(['notepad.exe', file_path])
    util.send_event_str(util.UnitTestFinished,"1")
    return
  
  def save_scene(self):
    path = os.path.join(self.module_directory,"save_test.mrb")
    util.write_test_log(f"\n\n\nsave scene to path {path}")
    util.saveScene(path)
  
  def set_index(self,value):
    self.index=value
  
  #加下面两个装饰器会出现测试中途偶尔崩溃的BUG
  #@util.unit_test_timer
  #@util.memory_usage_timer
  def test_case(self,in_value):
    self.index = in_value
    self.set_index(in_value)
    if self.current_case_list is not None and self.index >= len(self.current_case_list):
      util.write_test_log(f"\n\n\n\n\n=========================={self.action_list[self.action_index-1]['name']} complete==========================\n\n\n\n\n")
      self.current_case_list = None
      self.set_index(0)
    if self.current_case_list is None:
      if self.action_index >= len(self.action_list):
        util.write_test_log(f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<{self.module_name} complete unit  test>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        util.singleShot(1000,self.finish_test)
        return
      action = self.action_list[self.action_index]
      list_temp = []
      for bundle_name in action['data']:
        bundle = self.bundle_map[bundle_name]
        list_temp = list_temp + bundle['data']
      self.current_case_list = list_temp
      self.action_index+=1
    
    self.info = "empty info "
    util.write_test_log(f"\n\n\nstart test case {self.index}")
    try:
      row = self.current_case_list[self.index]
      self.info = row[0]
      util.write_test_log(f"-------------------------------------- is running index {self.index} function {row[1].__name__} --------------------------------------")
      util.show_screen_label(f"{self.info}")
      row[1]()
      util.write_test_log(f"the {self.index} passed")
    except Exception as e:
      import traceback
      traceback.print_exc()
      traceback_str = traceback.format_exc()
      str1 = e.__str__()+"\n"+traceback_str
      
      util.write_test_log(f"\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n失败项:{self.index}-{self.info}  \n{str1}\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")
      self.next_index()
      self.test_case(self.index)
      
      
  def delay_test(self,key,success_func,error_message,success_message):
    cout_key = key + "_count"
    timestamp_key = key + "_start_timestamp"
    util.unit_test['delay_test_key'] = key
    util.unit_test['success_func'] = success_func
    util.unit_test['error_message'] = error_message
    util.unit_test['success_message'] = success_message
    self.paramap[cout_key] = 0
    self.paramap[timestamp_key] = time.time()
    util.singleShot(10,self._wait_for_delay_test)
  def _wait_for_delay_test(self):
    key = util.unit_test['delay_test_key']
    cout_key = key + "_count"
    flag_key = key + "_flag"
    timestamp_key = key + "_start_timestamp"
    success_func = util.unit_test['success_func']
    if success_func():
      self.on_delay_test_success()
    else:
      self.paramap[cout_key] += 1
      if key in self.paramap:
        timeline = self.paramap[key]
      else:
        timeline = self.paramap["default"]
      if self.paramap[cout_key] > timeline :
        self.paramap[flag_key] = False
        time1 = time.time() - self.paramap[timestamp_key]
        util.write_test_log(f"[ERROR] {util.unit_test['error_message']} in time {round(time1,2)} second")
        self.finish_test()
        return
      util.singleShot(10,self._wait_for_delay_test)
  def on_delay_test_success(self):
    key = util.unit_test['delay_test_key']
    timestamp_key = key + "_start_timestamp"
    time1 = time.time() - self.paramap[timestamp_key]
    util.write_test_log(f"{util.unit_test['success_message']} use {round(time1,2)} second")
    util.log_screen_shot(self.module_directory,f"{key}.png")
    self.continue_test()