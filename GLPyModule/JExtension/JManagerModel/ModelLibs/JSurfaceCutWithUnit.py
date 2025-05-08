from __main__ import vtk, slicer
import slicer.util as util
import qt

class JSurfaceCutWithUnit:
   model_node = None
   master_node = None
   segment_node = None

   main = None
   uiWidget = None
   ui = None

   template = None
   default_segment_name = "JSurfaceCutWithUnitModel"
   def __init__(self,main) -> None:
    self.main = main
    self.uiWidget = slicer.util.loadUI(self.main.resourcePath('UI/Plugin/JSurfaceCutWithUnit.ui'))
    self.ui = slicer.util.childWidgetVariables(self.uiWidget)


    template =  self.main.get_new_widget("normal_manager")
    self.template = template
    self.template.setStyle("surface cut")
    util.addWidget2(self.ui.widget,self.template.widget)

    self.ui.point_place_btn.connect('clicked()', self.on_point_place)
    self.ui.btn_statstics.connect('clicked()', self.on_stastics)
    self.ui.pushButton.connect('clicked()', lambda:util.send_event_str(util.JSurfaceCutWithUnitConfirm))
    self.ui.pushButton_2.connect('clicked()', lambda:util.send_event_str(util.JSurfaceCutWithUnitCancel))

   def init(self,master_node,segment_node,title="未知",image_path=""):
    self.master_node = master_node
    if segment_node is not None:
      util.removeNode(segment_node)
    segment_node = util.CreateDefaultSegmentationNode(self.default_segment_name)
    self.segment_node = segment_node
    util.HideNode(self.segment_node)

    self.template.shrink()
    if segment_node is None:
      raise Exception("segment is None")
    if master_node is None:
      raise Exception("master_node is None")
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(segment_node)
    segmentEditorWidget.setSourceVolumeNode(master_node)
    segmentEditorWidget.setActiveEffectByName("Surface cut")
    model = util.getFirstNodeByClassByName(util.vtkMRMLModelNode,"SegmentEditorSurfaceCutModel")
    util.HideNode(model)
    effect = segmentEditorWidget.activeEffect()
    self.model_node = effect.self().segmentModel
    self.template.init(self.model_node,None,None)
    self.template.shrink()
    self.model_node.SetAttribute("alias_name","病灶模型")
    if image_path!="":
     self.template.set_image(image_path)
    self.template.set_title(title)
    
    self.reset()


   def reset(self):
     segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
     effect = segmentEditorWidget.activeEffect()
     effect.self().onCancel()
     self.model_node = effect.self().segmentModel
     self.model_node.SetAttribute("alias_name","病灶模型")
     util.GetDisplayNode(self.model_node).SetColor(1,0,0)
     self.template.init(self.model_node,None,None)
     self.template.shrink()
     

   '''
    连续选点
   '''
   def on_point_place(self):
    segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
    segmentEditorWidget.setSegmentationNode(self.segment_node)
    segmentEditorWidget.setSourceVolumeNode(self.master_node)
    segmentEditorWidget.setActiveEffectByName("Surface cut")
    effect = segmentEditorWidget.activeEffect()
    self.reset()
    effect.self().fiducialPlacementToggle.placeButton().setChecked(False)
    effect.self().fiducialPlacementToggle.placeButton().setChecked(True)


   def get_pointlist_node(self):
    node = util.getFirstNodeByExactName("C")
    return node




   def on_stastics(self):
    import vtk
    
    # 获取模型节点
    model = util.getFirstNodeByName("SegmentEditorSurfaceCutModel")
    if model is None:
     return
    polyData = model.GetPolyData()

    # 创建vtkMassProperties对象
    massProperties = vtk.vtkMassProperties()
    massProperties.SetInputData(polyData)
    massProperties.Update()

    # 获取模型的表面积和体积
    surfaceArea = massProperties.GetSurfaceArea()
    volume = massProperties.GetVolume()

    self.ui.info.setText(f"病灶模型体积是\t{round(volume/1000,2)}    mm³\n面积是\t\t{round(surfaceArea/100,2)}    mm²")