import slicer,qt
import slicer.util as util
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin


class PayModule(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "PayModule"  # TODO: make this more human readable by adding spaces
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


class PayModuleWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
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
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        self.uiWidget = slicer.util.loadUI(self.resourcePath("UI/PayDialog.ui"))
        self.layout.addWidget(self.uiWidget)
        self.ui = slicer.util.childWidgetVariables(self.uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        self.uiWidget.setMRMLScene(slicer.mrmlScene)
        self.init_ui()

    def init_ui(self):
        self.ui.label_3.setAttribute(qt.Qt.WA_TransparentForMouseEvents, True)
        self.ui.label_5.setAttribute(qt.Qt.WA_TransparentForMouseEvents, True)
        self.ui.label_6.setAttribute(qt.Qt.WA_TransparentForMouseEvents, True)
        self.ui.label_7.setAttribute(qt.Qt.WA_TransparentForMouseEvents, True)
        self.ui.label_8.setAttribute(qt.Qt.WA_TransparentForMouseEvents, True)
        self.ui.label_9.setAttribute(qt.Qt.WA_TransparentForMouseEvents, True)
        self.ui.label_10.setAttribute(qt.Qt.WA_TransparentForMouseEvents, True)
        self.ui.label_11.setAttribute(qt.Qt.WA_TransparentForMouseEvents, True)
        self.ui.label_12.setAttribute(qt.Qt.WA_TransparentForMouseEvents, True)
        # btnGroup = qt.QButtonGroup()
        # btnGroup.addButton(self.ui.btnPayLife)
        # btnGroup.addButton(self.ui.btnPayYear)
        # btnGroup.addButton(self.ui.btnPayMonth)
        # btnGroup.setExclusive(True)
        self.ui.btnPayLife.connect('toggled(bool)', self.on_pay_life)
        self.ui.btnPayYear.connect('toggled(bool)', self.on_pay_year)
        self.ui.btnPayMonth.connect('toggled(bool)', self.on_pay_month)
        self.ui.btnPay.connect('clicked()', self.on_pay_click)
        path = util.get_resource("alipay.svg")
        icon = qt.QPixmap(path).scaled(qt.QSize(32, 32), qt.Qt.KeepAspectRatio, qt.Qt.SmoothTransformation)
        icon = qt.QIcon(icon)
        self.ui.alipay.setIcon(icon)
        path = util.get_resource("wechat.svg")
        icon = qt.QPixmap(path).scaled(qt.QSize(32, 32), qt.Qt.KeepAspectRatio, qt.Qt.SmoothTransformation)
        icon = qt.QIcon(icon)
        self.ui.wechat.setIcon(icon)
        self.ui.btnPayLife.setChecked(True)
        self.ui.alipay.setChecked(True)

    def on_pay_life(self, state):
        if state:
            self.ui.btnPayYear.setChecked(False)
            self.ui.btnPayMonth.setChecked(False)
        pass

    def on_pay_year(self, state):
        if state:
            self.ui.btnPayLife.setChecked(False)
            self.ui.btnPayMonth.setChecked(False)
        pass

    def on_pay_month(self, state):
        if state:
            self.ui.btnPayYear.setChecked(False)
            self.ui.btnPayLife.setChecked(False)
        pass

    def on_pay_click(self):
        pay_type = 0
        if self.ui.btnPayLife.isChecked():
            pay_type = 1
        elif self.ui.btnPayYear.isChecked():
            pay_type = 2
        elif self.ui.btnPayMonth.isChecked():
            pay_type = 3
        if pay_type == 0:
            util.showWarningText('请选择一个套餐')

    def set_dialog(self, dialog):
        self.dialog = dialog

    def get_widget(self):
        return self.ui.PayDialog2