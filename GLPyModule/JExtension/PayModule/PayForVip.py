import slicer,qt
import slicer.util as util
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from Base.JBaseExtension import JBaseExtensionWidget


class PayForVip(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "PayForVip"  # TODO: make this more human readable by adding spaces
        self.parent.categories = [
            "Examples"]  # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["sun qing wen"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """

    """
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """

    """


#
# LineIntensityProfileWidget
#


class PayForVipWidget(JBaseExtensionWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """
    dialog = None
    def __init__(self, parent=None) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation

    def setup(self) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        super().setup()

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        # self.uiWidget = slicer.util.loadUI(self.resourcePath("UI/PayForVip.ui"))
        # self.layout.addWidget(self.uiWidget)
        # self.ui = slicer.util.childWidgetVariables(self.uiWidget)
        # self.uiWidget.setMRMLScene(slicer.mrmlScene)
        #self.init_ui()

    def init_ui(self):
        self.ui.btnVip.connect('clicked()', self.become_vip)
        pass

    def become_vip(self):
        code = self.ui.lblCode.text
        if code == "":
            util.showWarningText("请先输入激活码")
        
        val = self.ui.lblCode.text.strip()
        if len(val)!=60:
            util.showWarningText("激活码格式错误："+len(val).__str__())
            return
        
        data = {
          "code": val
        }
        url = "/system/passport/validate_code"
        val = util.httplib.asyncTask(url,data)
        if  val["success"] == True:
            print(val['msg'])
            
            from datetime import datetime
            info_list = val['msg'].split('到')
            time_list = info_list[1].strip().split('.')
            input_format = "%Y-%m-%d %H:%M:%S"
            dt = datetime.strptime(time_list[0], input_format)
            output_format = "%a, %d %b %Y %H:%M:%S GMT"
            out_str = dt.strftime(output_format)
            out_str1 = dt.strftime("您的VIP权限将在%Y年%m月%d日到期")
            print(out_str, out_str1)
            util.send_event_str(util.UpdateVIPTime, out_str)
            util.getModuleWidget("PayVipTips").set_info(out_str1)
            dialog = util.getModuleWidget("JMessageBox").on_popup_ui_dialog("VIP用户",util.getModuleWidget("PayVipTips").get_widget(), 700, 600)
            util.getModuleWidget("PayVipTips").set_dialog(dialog)
            dialog.exec_()
            self.dialog.close()
        else:
            util.showWarningText(val["msg"])

    def set_error_info(self, error):
        self.ui.setText(error)

    def set_dialog(self, dialog):
        self.dialog = dialog

    def get_widget(self):
        return self.ui.PayForVip2