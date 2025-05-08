import slicer,qt,vtk,ctk,os
import slicer.util as util
import FrameworkStyle as style
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from Base.JBaseExtension import JBaseExtensionWidget
from FrameworkLib.datas import fdb
from qt import QCoreApplication
from UnitTeaching import TeacherIntroduce
#
# FrameworkMenu
#

class MenuMain:
  item_map = {}
  module_path = ''
  project_type = 1
  is_default = 0
  def __init__(self,uiwidget,ui,main,item,json_val):
    self.uiwidget = uiwidget
    self.ui = ui
    self.main = main
    self.item = item
    self.json_val = json_val
    self.project_type = int(json_val["ptype"])
    name1 = json_val["info_name"]
    des = json_val["des"]
    icon = json_val["icon"]
    is_open = json_val["open"]
    if is_open == 1:
      self.ui.lblUnOpen.hide()
    default = json_val.get("default")
    if default != None and (default == "1" or default == 1):
      self.is_default = 1
    self.ui.lbl_cover.setText(util.tr('项目：')+name1)
    self.ui.lbl_des.setText(util.tr('简介：')+des)
    self.module_path = os.path.dirname(util.modulePath('FrameworkMenu'))
    icon_path = os.path.join(self.module_path, 'Resources', 'Icons', icon)
    img = qt.QImage()
    img.load(icon_path)
    pixelmap = qt.QPixmap.fromImage(img).scaled(100,100)
    self.ui.lbl_icon.setPixmap(pixelmap)
    self.ui.pushButton.connect('clicked()', self.on_friend)

  def on_friend(self):
    uiWidget = slicer.util.loadUI(os.path.join(self.module_path, 'Resources', 'UI/Contact.ui'))
    ui = slicer.util.childWidgetVariables(uiWidget)
    
    contact_path = os.path.join(self.module_path, 'Resources', 'Icons/contact.png')
    slicer.util.addPictureFromFile(contact_path,ui.label_2,size_width=381,size_height=381)
    util.getModuleWidget("JMessageBox").on_popup_ui_dialog("合作拿证",uiWidget, 400, 510).exec_()
    
class MenuBar:
  def __init__(self, uiwidget, ui, des):
    self.uiwidget = uiwidget
    self.ui = ui
    self.ui.lbl_des.setText(des)
 
    
class MenuSub:
  def __init__(self,uiwidget,ui,main,item,json_val):
    self.uiwidget = uiwidget
    self.ui = ui
    self.main = main
    self.item = item
    self.json_val = json_val
    name1 = json_val["name"]
    self.ui.lbl_cover.setText(name1)
    extension_base = json_val["extension_base"]
    hard = json_val["hard"]
    movie = None
    self.ui.bg.tabBar().hide()
    default = json_val.get("default")
    if default != None and (default == "1" or default == 1):
      self.ui.bg.setCurrentIndex(1)
      gif_name = json_val.get("gif")
      if gif_name == None:
        return
      module_path = os.path.dirname(util.modulePath('FrameworkMenu'))
      icon_path = os.path.join(module_path, 'Resources', 'Icons', gif_name).replace("\\", "/")
      self.movie = qt.QMovie(icon_path)
      self.movie.setScaledSize(qt.QSize(80, 80))
      self.ui.lblGif.setMovie(self.movie)
      self.movie.start()
      return
    self.ui.bg.setCurrentIndex(0)
    score = fdb.get_score(util.username,extension_base,hard)
    if score > 0:
      stylesheet = "QLabel{color: rgb(0, 255, 0);}"
      self.ui.label.setStyleSheet(stylesheet)
    else:
      stylesheet = "QLabel{color: rgb(111, 111, 111);}"
      self.ui.label.setStyleSheet(stylesheet)
    des = util.tr('使用次数')
    self.ui.label.setText(f"{des}:{score}")
        
    if "powerby" in json_val:
      self.ui.lbl_info.setText(" "+json_val["powerby"])
      hard = 0

    if int(json_val["auth"]) > 1:
      self.ui.lbl_cover.setText(name1+"(VIP)")

  def setSelect(self, state):
    if state:
      self.ui.bgPage1.setStyleSheet("#bgPage1{border:1px solid #2B649A;}")
      self.ui.tab.setStyleSheet("#tab{border:1px solid #2B649A;}")
    else:
      self.ui.bgPage1.setStyleSheet("#bgPage1{border:0px solid #2B649A;}")
      self.ui.tab.setStyleSheet("#tab{border:0px solid #2B649A;}")

  def setItem(self,item):
    self.item = item
  
  def enter(self):
    
    if int(self.json_val["auth"]) > 1:
      util.showWarningText("该功能仅限VIP")
      return
    res = util.messageBox("确定要进入这个解决方案吗？",windowTitle=util.tr("提示"))
    if res == 0:
      return
    auto_enter = self.json_val.get('auto_enter')
    if auto_enter is None:
      auto_enter = 0
    display_score = self.json_val.get('display_score')
    if display_score is None:
      display_score = 0
    util.save_cache_to_PAAA("auto_enter",auto_enter)
    util.save_cache_to_PAAA("display_score",display_score)
    util.save_cache_to_PAAA("sub_solution",self.json_val["extension_base"])
    util.save_cache_to_PAAA("sub_solution_version",self.json_val["name"])
    util.save_cache_to_PAAA("sub_solution_hard",self.json_val["hard"])
    util.save_cache_to_PAAA("solution_name",self.json_val["extension_base"])
    util.save_cache_to_PAAA("sub_project_alias_name",self.main.selected_main.json_val["info_name"])
    util.send_event_str(util.ResetSolution)
    
    
class FrameworkMenu(ScriptedLoadableModule):

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "FrameworkMenu"  # TODO: make this more human readable by adding spaces
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
# FrameworkMenuWidget
#

class FrameworkMenuWidget(JBaseExtensionWidget):
  logindlg = None
  config = {}
  item_map = {}
  selected_main = None
  selected_sub = None
  introduce = None
  star_list = {}
  player = None
  is_init = False
  type_btn_list = []
  is_use_event = True
  hard_list = []
  def setup(self):
    super().setup()
    self.ui.tabWidget.tabBar().hide()
    self.ui.tabWidget.setCurrentIndex(1)
    self.introduce = TeacherIntroduce()
    util.addWidget2(self.ui.info_widget, self.introduce.get_widget())
    self.star_list = [self.ui.star1, self.ui.star2, self.ui.star3, self.ui.star4, self.ui.star5, self.ui.star6, self.ui.star7, self.ui.star8]
    
    self.ui.btn_open.connect('clicked()',self.on_enter_solution)
    self.ui.btn_back.connect('clicked()',self.on_back_to_solution)
    self.ui.treeWidget.header().hide()
    self.ui.treeWidget.setIndentation(13)
    self.ui.treeWidget.setStyleSheet('''QTreeWidget::item:selected, QTreeWidget::branch:selected{background-color:#1c1d1d;}''')
    self.ui.tabWidget_2.tabBar().hide()
    
    self.player = qt.QMediaPlayer()
    container = qt.QVideoWidget()
    self.player.setVideoOutput(container)
    container.show()
    util.addWidget2(self.ui.widget_video, container)
    container.setAspectRatioMode(qt.Qt.IgnoreAspectRatio)
    #util.getModuleWidget("SVideoPlayer").AddVideoPlayer(video_path, self.ui.tabVideo)
    module_path = os.path.dirname(util.modulePath('FrameworkMenu'))
    style.set_menu_style(module_path, self.ui)
    self.player.connect("videoAvailableChanged(bool)", self.on_vedio_available)
    self.ui.btnType1.connect("toggled(bool)", self.on_select_type1)
    self.ui.btnType2.connect("toggled(bool)", self.on_select_type2)
    self.ui.btnType3.connect("toggled(bool)", self.on_select_type3)
    self.type_btn_list.append(self.ui.btnType1)
    self.type_btn_list.append(self.ui.btnType2)
    self.type_btn_list.append(self.ui.btnType3)
    self.ui.btnType1.hide()
    self.ui.btnType2.hide()
    self.ui.btnType3.hide()
    
    util.singleShot(500, lambda:self.init_once())
  
  def on_select_type1(self, state):
    if state == False:
      return
    if not self.is_use_event:
      return
    self.on_select_type(1)
    pass

  def on_select_type2(self, state):
    if state == False:
      return
    if not self.is_use_event:
      return
    self.on_select_type(2)
    pass

  def on_select_type3(self, state):
    if state == False:
      return
    if not self.is_use_event:
      return
    self.ui.btnType1.setChecked(False)
    self.on_select_type(3)
    pass

  def on_select_type(self, select_type):
    for index in range(len(self.type_btn_list)):
      if index == select_type - 1:
        continue
      self.type_btn_list[index].setChecked(False)
    for key in self.item_map:
      is_hide = True
      item = self.item_map[key]
      if item.project_type == select_type:
        is_hide = False
      key.setHidden(is_hide)
      if is_hide == False and item.is_default == 1:
        self.ui.listWidget.setCurrentItem(key)
        self.on_main_selected(key)
    pass

  def on_vedio_available(self, state):
    if state == False:
      return
    self.player.play()
    qt.QTimer.singleShot(200, lambda:self.ui.tabWidget_2.setCurrentIndex(1))
    pass

  def exit(self):
    util.layout_panel("middle_top").show()
    util.layout_dock("top").show()
    util.getModuleWidget("FrameworkTop").set_style("whole")
    
  def enter(self):
    if not self.is_init:
      return    
    util.layout_panel("middle_top").hide()
    util.layout_dock("top").hide()
    util.singleShot(0,self._enter)

  def init_once(self):   
    if self.is_init:
      return
    self.is_init = True
    self.ui.tabWidget.setCurrentIndex(0)
    self.config_data = self.init_config_data()
    self.reinit_from_config_data()
    self._enter()
    pass
  def show_ui(self):
    pass
  def _enter(self):
    sub_solution = util.get_cache_from_PAAA("sub_solution",default="UnitPunctureGuide")
    sub_solution_hard = int(util.get_cache_from_PAAA("sub_solution_hard",3))
    selected = False
    for key in self.item_map:
      template = self.item_map[key]
      for item in template.item_map:
        sub_template = template.item_map[item]
        if int(sub_template.json_val["hard"]) == sub_solution_hard :  
          stylesheet = "QLabel{color: rgb(0, 255, 0);}"
          sub_template.ui.lbl_cover.setStyleSheet(stylesheet)
          cover_info = sub_template.ui.lbl_cover.text
          curr_des = util.tr('当前方案')
          sub_template.ui.lbl_cover.setText(f"{cover_info}({curr_des})")
          
          self.selected_main = template
          self.is_use_event = False
          self.ui.listWidget.setCurrentItem(key)
          self.ui.treeWidget.setCurrentItem(item)
          self.is_use_event = True
        else:
          stylesheet = "QLabel{color: rgb(255, 255, 255);}"
          sub_template.ui.lbl_cover.setStyleSheet(stylesheet)    
    
  def on_enter_solution(self):
    self.selected_sub.enter()

  def on_back_to_solution(self):
    util.send_event_str(util.BackToSolution)
  
  def init_config_data(self):
    import json
    file_name = 'text/project.json'
    if util.curr_language == 1:
      file_name = 'text/project_en.json'

    file_path = self.resourcePath(file_name)
    with open(file_path, 'r', encoding='utf-8') as file:
      data = json.load(file)    
      return data
    return None
  

  def reinit_from_config_data(self):
    self.ui.listWidget.clear()
    self.ui.treeWidget.clear()
    self.ui.listWidget.setSpacing(6)
    
    self.item_map = {}
    item_list = []
    sub_solution_hard = int(util.get_cache_from_PAAA("sub_solution_hard",3))
    select_project_type = 1
    select_project = "UnitPunctureGuide"
    for main_val in self.config_data:
      for key in main_val["versions"]:
        sub_val = main_val["versions"][key]
        if sub_solution_hard == int(sub_val["hard"]):
          select_project_type = int(main_val["ptype"])
          select_project = sub_val["extension_base"]
          print("whm test", select_project_type, select_project)
    self.is_use_event = False
    if select_project_type == 1:
      self.ui.btnType1.setChecked(True)
    else:
      self.ui.btnType2.setChecked(True)
    self.is_use_event = True
    des_list = [util.tr('项目介绍：'), util.tr('科研教学：')]
    for i in range(2):
      uiWidget = slicer.util.loadUI(self.resourcePath('UI/MenuBar.ui'))
      ui = slicer.util.childWidgetVariables(uiWidget)
      item = qt.QTreeWidgetItem(self.ui.treeWidget)
      item.setSizeHint(0, qt.QSize(253 , 40))
      templatesub = MenuBar(uiWidget, ui, des_list[i])
      self.ui.treeWidget.setItemWidget(item, 0, templatesub.uiwidget)
      item_list.append(item)
      item.setExpanded(True)

    for val in self.config_data:
      if val['display'] == 0:
        continue
      tmp_ptype = int(val["ptype"])
      if tmp_ptype >= len(self.type_btn_list):
        continue
      self.type_btn_list[tmp_ptype-1].show()
      uiWidget = slicer.util.loadUI(self.resourcePath('UI/FrameworkMenuItemMain.ui'))
      ui = slicer.util.childWidgetVariables(uiWidget)
      ui.pushButton.setVisible(False)
      item = qt.QListWidgetItem()
      if val['open'] == 0:
        item.setFlags(item.flags() & ~qt.Qt.ItemIsEnabled)
      template = MenuMain(uiWidget,ui,self,item,val)
      self.ui.listWidget.addItem(item)
      self.ui.listWidget.setItemWidget(item,template.uiwidget)
      item.setSizeHint(qt.QSize(492 , 135))
      self.item_map[item] = template
      mainmenu = template
      mainmenu.item_map = {}
      is_hide = True
      
      if select_project_type == tmp_ptype:
        is_hide = False
      item.setHidden(is_hide)
      for key in mainmenu.json_val["versions"]:
        val = mainmenu.json_val["versions"][key]
        default =  val.get("default")
        parent = item_list[1]
        hard = int(val.get("hard"))
        if hard in self.hard_list:
          util.showWarningText(f"配置错误，难度字段值{hard}重复")
          pass
        else:
          self.hard_list.append(hard)
        if default != None and (default == "1" or default == 1):
          parent = item_list[0]
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/FrameworkMenuItemSub.ui'))
        ui = slicer.util.childWidgetVariables(uiWidget)
        tree_item = qt.QTreeWidgetItem(parent)
        tree_item.setSizeHint(0, qt.QSize(253 , 95))
        templatesub = MenuSub(uiWidget,ui,self,tree_item,val)
        self.ui.treeWidget.setItemWidget(tree_item, 0, templatesub.uiwidget)
        mainmenu.item_map[tree_item] = templatesub
        is_tree_item_hide = True
        if select_project == val["extension_base"]:
          is_tree_item_hide = False
        tree_item.setHidden(is_tree_item_hide)
    
    self.ui.listWidget.disconnect('currentRowChanged(int)',self.on_main_item_clicked)
    self.ui.treeWidget.disconnect('currentItemChanged(QTreeWidgetItem *, QTreeWidgetItem *)',self.on_sub_item_clicked)
    self.ui.listWidget.connect('currentRowChanged(int)',self.on_main_item_clicked)
    self.ui.treeWidget.connect('currentItemChanged(QTreeWidgetItem *, QTreeWidgetItem *)',self.on_sub_item_clicked)
      
  def on_main_item_clicked(self,row):
    if not self.is_use_event:
      return
    curr_item = self.ui.listWidget.item(row)
    if curr_item == None:
      return
    self.on_main_selected(curr_item)

  def on_main_selected(self, curr_item):
    mainmenu = self.item_map[curr_item]
    self.selected_main = mainmenu
    solution_name = util.get_cache_from_PAAA("solution_name", "")
    hard = int(util.get_cache_from_PAAA("sub_solution_hard","-1"))
    for key in self.item_map:
      hide_state = True
      if key == curr_item:
        hide_state = False
      menu = self.item_map[key]
      for item in menu.item_map:
        item.setHidden(hide_state)
        if hide_state == False:          
          template = menu.item_map[item]
          if solution_name == template.json_val["extension_base"]:
            if hard == int(template.json_val["hard"]):
              self.ui.treeWidget.setCurrentItem(item)
            pass
          else:
            default =  template.json_val.get("default")
            if default == 1:
              self.ui.treeWidget.setCurrentItem(item)

  def on_sub_item_clicked(self, current, previous):
    if self.selected_sub:
      self.selected_sub.setSelect(False)
    if current == None:
      return
    submenu = self.selected_main.item_map[current]
    self.selected_sub = submenu
    submenu.setSelect(True)
    self.ui.label.setText(self.selected_sub.json_val["name"])
    self.ui.label_2.setText(self.selected_sub.json_val["info"])
    hard = self.selected_sub.json_val["hard"]
    display_type = self.selected_sub.json_val.get('display_type')
    self.ui.widget_5.hide()
    if display_type is None:
      display_type = 0
    self.ui.tabWidget_2.setCurrentIndex(display_type)
    if display_type == 1:
      value = self.selected_sub.json_val.get("video")
      if value is None:
        self.ui.tabWidget_2.setCurrentIndex(0)
        #util.getModuleWidget("SVideoPlayer").VideoPlay(False)
        self.player.stop()        
      else:
        self.ui.tabWidget_2.setCurrentIndex(3)
        video_path = self.resourcePath(f'Video/{value}').replace("\\", "/")
        content = qt.QMediaContent(qt.QUrl.fromLocalFile(video_path))
        print(video_path)
        self.player.setMedia(content)
        if self.player.isAudioAvailable():
          self.player.play()
          qt.QTimer.singleShot(200, lambda:self.ui.tabWidget_2.setCurrentIndex(1))
    hide_open = self.selected_sub.json_val.get('hide_open')
    if hide_open is None:
      hide_open = 0
    if hide_open != 0:
      self.ui.openContainer.hide()
    else:
      self.ui.openContainer.show()
    self.introduce.set_hard(hard)
    extension_base = self.selected_sub.json_val["extension_base"]
    module_path = os.path.dirname(util.modulePath(extension_base))
    pic = self.selected_sub.json_val["pic"]
    pic_path = os.path.join(module_path,"Resources","Data",pic)
    print("OOOOOOOOOOOOOOOOOAAAAAAAAAAAAAAAAAAAA:",pic_path)
    if os.path.exists(pic_path):
      util.addPictureFromFile2(pic_path,self.ui.label_3,self.ui.label_3.width,self.ui.label_3.height)
      if display_type == 2:
        util.addPictureFromFile2(pic_path,self.ui.lblPic,self.ui.lblPic.width,self.ui.lblPic.height)
    else:
      pic_path = self.resourcePath('Data/version_default.png')
      util.addPictureFromFile2(pic_path,self.ui.label_3,self.ui.label_3.width,self.ui.label_3.height)
      