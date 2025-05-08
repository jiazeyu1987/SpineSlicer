def set_menu_style(module_path, ui):
  file_path = (module_path + '/Resources/Icons/btn_return.png').replace("\\", "/")
  file_style = f"background-image: url({file_path});"
  ui.icon_back.setStyleSheet(file_style)