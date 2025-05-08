
import qt,vtk
import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import numpy,logging



class LMJ(ScriptedLoadableModule):
  
    def __init__(self, parent):
        super().__init__(parent)
        ScriptedLoadableModule.__init__(self,parent)
        self.parent.title = "LMJ"  
        self.parent.categories = ["个人模块"]  
        self.parent.dependencies = [] 
        self.parent.contributors = ["SZJ/JZY"] 
        self.parent.helpText = """000"""
        self.parent.acknowledgementText = """000"""

class LMJWidget(ScriptedLoadableModuleWidget,VTKObservationMixin):
  
    def __init__(self, parent=None,cornerEpsilon=1e-3, zeroEpsilon=1e-6):
        ScriptedLoadableModuleWidget.__init__(self, parent)
        self.cornerEpsilon = cornerEpsilon
        self.zeroEpsilon = zeroEpsilon

    def setup(self):
        
        ScriptedLoadableModuleWidget.setup(self)
        uiWidget=slicer.util.loadUI(self.resourcePath("UI/LMJ.ui"))
        self.layout.addWidget(uiWidget)
        self.ui=slicer.util.childWidgetVariables(uiWidget)
        uiWidget.setMRMLScene(slicer.mrmlScene)
        
        self.ui.volumeSelector.setMRMLScene(slicer.mrmlScene)
        self.ui.PushButton.connect('clicked()',self.createAcquisitionTransform)


    
    
    def gridTransformFromCorners(self, volumeNode, sourceCorners, targetCorners):####
     
                columns, rows, slices = volumeNode.GetImageData().GetDimensions()
                cornerShape = (slices, 2, 2, 3)
                if not (sourceCorners.shape == cornerShape and targetCorners.shape == cornerShape):
                    raise Exception("Corner shapes do not match volume dimensions %s, %s, %s" %
                                    (sourceCorners.shape, targetCorners.shape, cornerShape))

                # create the grid transform node
                gridTransform = slicer.vtkMRMLGridTransformNode()
                gridTransform.SetName(slicer.mrmlScene.GenerateUniqueName('LMJTransform'))
                slicer.mrmlScene.AddNode(gridTransform)

                # place grid transform in the same subject hierarchy folder as the volume node
                shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
                volumeParentItemId = shNode.GetItemParent(shNode.GetItemByDataNode(volumeNode))
                shNode.SetItemParent(shNode.GetItemByDataNode(gridTransform), volumeParentItemId)

                # create a grid transform with one vector at the corner of each slice
                # the transform is in the same space and orientation as the volume node
                gridImage = vtk.vtkImageData()
                gridImage.SetOrigin(*volumeNode.GetOrigin())
                gridImage.SetDimensions(2, 2, slices)
                sourceSpacing = volumeNode.GetSpacing()
                gridImage.SetSpacing(sourceSpacing[0] * columns, sourceSpacing[1] * rows, sourceSpacing[2])
                gridImage.AllocateScalars(vtk.VTK_DOUBLE, 3)
                transform = slicer.vtkOrientedGridTransform()
                directionMatrix = vtk.vtkMatrix4x4()
                volumeNode.GetIJKToRASDirectionMatrix(directionMatrix)
                transform.SetGridDirectionMatrix(directionMatrix)
                transform.SetDisplacementGridData(gridImage)
                gridTransform.SetAndObserveTransformToParent(transform)
                volumeNode.SetAndObserveTransformNodeID(gridTransform.GetID())

                # populate the grid so that each corner of each slice
                # is mapped from the source corner to the target corner
                displacements = slicer.util.arrayFromGridTransform(gridTransform)
                for sliceIndex in range(slices):
                    for row in range(2):
                        for column in range(2):
                            displacements[sliceIndex][row][column] = targetCorners[sliceIndex][row][column] - sourceCorners[sliceIndex][row][column]

    def sliceCornersFromDICOM(self, volumeNode):
     
            spacingTag = "0028,0030"
            positionTag = "0020,0032"
            orientationTag = "0020,0037"

            columns, rows, slices = volumeNode.GetImageData().GetDimensions()
            corners = numpy.zeros(shape=[slices, 2, 2, 3])
            instanceUIDsAttribute = volumeNode.GetAttribute('DICOM.instanceUIDs')
            uids = instanceUIDsAttribute.split() if instanceUIDsAttribute else []
            if len(uids) != slices:
                # There is no uid for each slice, so most likely all frames are in a single file
                # or maybe there is a problem with the sequence
                logging.warning("Cannot get DICOM slice positions for volume " + volumeNode.GetName())
                return None
            for sliceIndex in range(slices):
                uid = uids[sliceIndex]
                # get slice geometry from instance
                positionString = slicer.dicomDatabase.instanceValue(uid, positionTag)
                orientationString = slicer.dicomDatabase.instanceValue(uid, orientationTag)
                spacingString = slicer.dicomDatabase.instanceValue(uid, spacingTag)
                if positionString == "" or orientationString == "" or spacingString == "":
                    logging.warning('No geometry information available for DICOM data, skipping corner calculations')
                    return None

                position = numpy.array(list(map(float, positionString.split('\\'))))
                orientation = list(map(float, orientationString.split('\\')))
                rowOrientation = numpy.array(orientation[:3])
                columnOrientation = numpy.array(orientation[3:])
                spacing = numpy.array(list(map(float, spacingString.split('\\'))))
                # map from LPS to RAS
                lpsToRAS = numpy.array([-1, -1, 1])
                position *= lpsToRAS
                rowOrientation *= lpsToRAS
                columnOrientation *= lpsToRAS
                rowVector = columns * spacing[1] * rowOrientation  # dicom PixelSpacing is between rows first, then columns
                columnVector = rows * spacing[0] * columnOrientation
                # apply the transform to the four corners
                for column in range(2):
                    for row in range(2):
                        corners[sliceIndex][row][column] = position
                        corners[sliceIndex][row][column] += column * rowVector
                        corners[sliceIndex][row][column] += row * columnVector
            return corners

    def sliceCornersFromIJKToRAS(self, volumeNode):
            """Calculate the RAS position of each of the four corners of each
            slice of a volume node based on the ijkToRAS matrix of the volume node
            """
            ijkToRAS = vtk.vtkMatrix4x4()
            volumeNode.GetIJKToRASMatrix(ijkToRAS)
            columns, rows, slices = volumeNode.GetImageData().GetDimensions()
            corners = numpy.zeros(shape=[slices, 2, 2, 3])
            for sliceIndex in range(slices):
                for column in range(2):
                    for row in range(2):
                        corners[sliceIndex][row][column] = numpy.array(ijkToRAS.MultiplyPoint([column * columns, row * rows, sliceIndex, 1])[:3])
            return corners

    def cornersToWorld(self, volumeNode, corners):
            """Map corners through the volumeNodes transform to world
            This can be used to confirm that an acquisition transform has correctly
            mapped the slice corners to match the dicom acquisition.
            """
            columns, rows, slices = volumeNode.GetImageData().GetDimensions()
            worldCorners = numpy.zeros(shape=[slices, 2, 2, 3])
            for slice in range(slices):
                for row in range(2):
                    for column in range(2):
                        volumeNode.TransformPointToWorld(corners[slice, row, column], worldCorners[slice, row, column])
            return worldCorners

    def is_error(self,volumeNode):
        self.originalCorners = self.sliceCornersFromIJKToRAS(volumeNode)
        self.targetCorners = self.sliceCornersFromDICOM(volumeNode)
        if self.originalCorners is None or self.targetCorners is None:
            # can't create transform without corner information
            return False
        maxError = (abs(self.originalCorners - self.targetCorners)).max()
        
        if maxError > self.cornerEpsilon:
            return True
        else:
            return False
        

    def createAcquisitionTransform(self, volumeNode=None, addAcquisitionTransformIfNeeded=True):####

            volumeNode=self.ui.volumeSelector.currentNode()
            self.originalCorners = self.sliceCornersFromIJKToRAS(volumeNode)
            self.targetCorners = self.sliceCornersFromDICOM(volumeNode)
            if self.originalCorners is None or self.targetCorners is None:
                # can't create transform without corner information
                return
            maxError = (abs(self.originalCorners - self.targetCorners)).max()

            if maxError > self.cornerEpsilon:
                warningText = f"Irregular volume geometry detected (maximum error of {maxError:g} mm is above tolerance threshold of {self.cornerEpsilon:g} mm)."
                if addAcquisitionTransformIfNeeded:
                    logging.warning(warningText + "  Adding acquisition transform to regularize geometry.")
                    self.gridTransformFromCorners(volumeNode, self.originalCorners, self.targetCorners)
                    self.fixedCorners = self.cornersToWorld(volumeNode, self.originalCorners)
                    if not numpy.allclose(self.fixedCorners, self.targetCorners):
                        raise Exception("Acquisition transform didn't fix slice corners!")
                else:
                    logging.warning(warningText + "  Regularization transform is not added, as the option is disabled.")
            elif maxError > 0 and maxError > self.zeroEpsilon:
                logging.debug("Irregular volume geometry detected, but maximum error is within tolerance" +
                              f" (maximum error of {maxError:g} mm, tolerance threshold is {self.cornerEpsilon:g} mm).")
    

  