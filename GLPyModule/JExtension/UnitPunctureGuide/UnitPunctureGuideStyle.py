def set_reconstruction_style(module_path, ui):
  file_path = (module_path + '/Resources/Icons/seg_naoshi.png').replace("\\", "/")
  file_style = "background-image: url(" + file_path + ");"
  ui.btnVentricle.setStyleSheet(file_style)
  
  file_path = (module_path + '/Resources/Icons/seg_naoqv.png').replace("\\", "/")
  file_style = "background-image: url(" + file_path + ");"
  ui.btnBrain.setStyleSheet(file_style)
  
  file_path = (module_path + '/Resources/Icons/seg_turmo.png').replace("\\", "/")
  file_style = "background-image: url(" + file_path + ");"
  ui.btnTurmo.setStyleSheet(file_style)
  
  file_path = (module_path + '/Resources/Icons/seg_skin.png').replace("\\", "/")
  file_style = "background-image: url(" + file_path + ");"
  ui.btn_quick_skin.setStyleSheet(file_style)
  
  file_path = (module_path + '/Resources/Icons/seg_bone.png').replace("\\", "/")
  file_style = "background-image: url(" + file_path + ");"
  ui.btn_quick_bone.setStyleSheet(file_style)
  

def set_simple_teacher_data_style(module_path, ui):
  file_path = (module_path + '/Resources/Icons/test_ct_data.png').replace("\\", "/")
  file_style = "QPushButton{background-image: url(" + file_path + ");}"
  ui.btnDicom.setStyleSheet(file_style)

  file_path = (module_path + '/Resources/Icons/load_latest_file.png').replace("\\", "/")
  file_style = "QPushButton{background-image: url(" + file_path + ");}"
  ui.btnDicom_2.setStyleSheet(file_style)

  file_path = (module_path + '/Resources/Icons/load_dicom.png').replace("\\", "/")
  file_style = "QPushButton{background-image: url(" + file_path + ");}"
  ui.btnDicom_3.setStyleSheet(file_style)

def set_sun_style(module_path, ui):
  file_path = (module_path + '/Resources/Icons/mark_auto.png').replace("\\", "/")
  file_style = "QPushButton{background-image: url(" + file_path + ");}"
  ui.pushButton_13.setStyleSheet(file_style)

  file_path = (module_path + '/Resources/Icons/mark_visible.png').replace("\\", "/")
  file_path2 = (module_path + '/Resources/Icons/mark_visible2.png').replace("\\", "/")
  file_style = "QRadioButton::indicator:unchecked {image: url(" + file_path + ");} QRadioButton::indicator:checked {image: url(" + file_path2 + ");}"

  ui.w1.setStyleSheet(file_style)
  ui.m1.setStyleSheet(file_style)
  ui.y1.setStyleSheet(file_style)
  ui.g1.setStyleSheet(file_style)
  ui.a1.setStyleSheet(file_style)

  file_path = (module_path + '/Resources/Icons/mark_visible.png').replace("\\", "/")
  file_path2 = (module_path + '/Resources/Icons/mark_visible2.png').replace("\\", "/")
  file_style = "QRadioButton::indicator:unchecked {image: url(" + file_path + ");} QRadioButton::indicator:checked {image: url(" + file_path2 + ");}"

  ui.w1.setStyleSheet(file_style)
  ui.m1.setStyleSheet(file_style)
  ui.y1.setStyleSheet(file_style)
  ui.g1.setStyleSheet(file_style)
  ui.a1.setStyleSheet(file_style)

  file_path = (module_path + '/Resources/Icons/mark_opacity.png').replace("\\", "/")
  file_path2 = (module_path + '/Resources/Icons/mark_opacity2.png').replace("\\", "/")
  file_style = "QRadioButton::indicator:unchecked {image: url(" + file_path + ");} QRadioButton::indicator:checked {image: url(" + file_path2 + ");}"

  ui.w2.setStyleSheet(file_style)
  ui.m2.setStyleSheet(file_style)
  ui.y2.setStyleSheet(file_style)
  ui.g2.setStyleSheet(file_style)
  ui.a2.setStyleSheet(file_style)

  file_path = (module_path + '/Resources/Icons/mark_invisible.png').replace("\\", "/")
  file_path2 = (module_path + '/Resources/Icons/mark_invisible2.png').replace("\\", "/")
  file_style = "QRadioButton::indicator:unchecked {image: url(" + file_path + ");} QRadioButton::indicator:checked {image: url(" + file_path2 + ");}"

  ui.w3.setStyleSheet(file_style)
  ui.m3.setStyleSheet(file_style)
  ui.y3.setStyleSheet(file_style)
  ui.g3.setStyleSheet(file_style)
  ui.a3.setStyleSheet(file_style)

  
  file_path = (module_path + '/Resources/Icons/mark_mark.png').replace("\\", "/")
  file_style = "background-image: url(" + file_path + ");"
  ui.lblIconMark.setStyleSheet(file_style)

  
  file_path = (module_path + '/Resources/Icons/mark_red.png').replace("\\", "/")
  file_style = "background-image: url(" + file_path + ");"
  ui.lblIconRed.setStyleSheet(file_style)

  
  file_path = (module_path + '/Resources/Icons/mark_yellow.png').replace("\\", "/")
  file_style = "background-image: url(" + file_path + ");"
  ui.blIconYellow.setStyleSheet(file_style)

  
  file_path = (module_path + '/Resources/Icons/mark_green.png').replace("\\", "/")
  file_style = "background-image: url(" + file_path + ");"
  ui.blIconGreen.setStyleSheet(file_style)
  pass