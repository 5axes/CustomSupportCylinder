# Initial Copyright (c) 2018 Lokster <http://lokspace.eu>
# Based on the SupportBlocker plugin by Ultimaker B.V., and licensed under LGPLv3 or higher.
# All modification 5@xes
# First release 05-18-2020  to change the initial plugin into cylinder support
# Modif 0.01 : Cylinder length -> Pick Point to base plate height
# Modif 0.02 : Using  support_tower_diameter as variable to define the cylinder
# Modif 0.03 : Using a special parameter  support_tower_diameter as variable to define the cylinder
# Modif 0.04 : Add a text field to define the diameter
# Modif 0.05 : Add checkbox and option to swaitch between Cube / Cylinder
# Modif 0.06 : Symplify code and store defaut size support in Preference "customsupportcylinder/s_size" default 5

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication

from cura.CuraApplication import CuraApplication

from UM.Logger import Logger
from UM.Math.Vector import Vector
from UM.Tool import Tool
from UM.Event import Event, MouseEvent
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Scene.Selection import Selection

from cura.PickingPass import PickingPass

from UM.Operations.GroupedOperation import GroupedOperation
from UM.Operations.AddSceneNodeOperation import AddSceneNodeOperation
from UM.Operations.RemoveSceneNodeOperation import RemoveSceneNodeOperation
from cura.Operations.SetParentOperation import SetParentOperation

from UM.Settings.SettingInstance import SettingInstance

from cura.Scene.SliceableObjectDecorator import SliceableObjectDecorator
from cura.Scene.BuildPlateDecorator import BuildPlateDecorator
from cura.Scene.CuraSceneNode import CuraSceneNode
from UM.Scene.ToolHandle import ToolHandle
from UM.Tool import Tool

import math
import numpy

class CustomSupportsCylinder(Tool):
    def __init__(self):
        super().__init__()
        
        self._UseSize = 0.0
        self._UseCube = False
        
        self._shortcut_key = Qt.Key_F
        self._controller = self.getController()

        self._selection_pass = None

        self._i18n_catalog = None
        
        self.setExposedProperties("SSize", "LockCube")
        
        CuraApplication.getInstance().globalContainerStackChanged.connect(self._updateEnabled)

        # Note: if the selection is cleared with this tool active, there is no way to switch to
        # another tool than to reselect an object (by clicking it) because the tool buttons in the
        # toolbar will have been disabled. That is why we need to ignore the first press event
        # after the selection has been cleared.
        Selection.selectionChanged.connect(self._onSelectionChanged)
        self._had_selection = False
        self._skip_press = False

        self._had_selection_timer = QTimer()
        self._had_selection_timer.setInterval(0)
        self._had_selection_timer.setSingleShot(True)
        self._had_selection_timer.timeout.connect(self._selectionChangeDelay)


        self._preferences = CuraApplication.getInstance().getPreferences()
        self._preferences.addPreference("customsupportcylinder/s_size", 5)
        # rajout du float pour etre sure sinon sur valeur ronde pense que c'est un INT
        self._UseSize = float(self._preferences.getValue("customsupportcylinder/s_size"))
        
        
        
    def _onContainerLoadComplete(self, container_id):
        if not ContainerRegistry.getInstance().isLoaded(container_id):
            # skip containers that could not be loaded, or subsequent findContainers() will cause an infinite loop
            return

        try:
            container = ContainerRegistry.getInstance().findContainers(id = container_id)[0]
        except IndexError:
            # the container no longer exists
            return

        if not isinstance(container, DefinitionContainer):
            # skip containers that are not definitions
            return
        if container.getMetaDataEntry("type") == "extruder":
            # skip extruder definitions
            return

        support_category = container.findDefinitions(key="support")
        customsupport_setting = container.findDefinitions(key=list(self._settings_dict.keys())[0])
        if support_category and not customsupport_setting:
            # this machine doesn't have a zoffset setting yet
            support_category = support_category[0]
            for setting_key, setting_dict in self._settings_dict.items():

                definition = SettingDefinition(setting_key, container, support_category, self._i18n_catalog)
                definition.deserialize(setting_dict)

                # add the setting to the already existing platform adhesion settingdefinition
                # private member access is naughty, but the alternative is to serialise, nix and deserialise the whole thing,
                # which breaks stuff
                support_category._children.append(definition)
                container._definition_cache[setting_key] = definition
                container._updateRelations(definition)
                
    def event(self, event):
        super().event(event)
        modifiers = QApplication.keyboardModifiers()
        ctrl_is_active = modifiers & Qt.ControlModifier

        if event.type == Event.MousePressEvent and MouseEvent.LeftButton in event.buttons and self._controller.getToolsEnabled():
            if ctrl_is_active:
                self._controller.setActiveTool("TranslateTool")
                return

            if self._skip_press:
                # The selection was previously cleared, do not add/remove an support mesh but
                # use this click for selection and reactivating this tool only.
                self._skip_press = False
                return

            if self._selection_pass is None:
                # The selection renderpass is used to identify objects in the current view
                self._selection_pass = CuraApplication.getInstance().getRenderer().getRenderPass("selection")
            picked_node = self._controller.getScene().findObject(self._selection_pass.getIdAtPosition(event.x, event.y))
            if not picked_node:
                # There is no slicable object at the picked location
                return

            node_stack = picked_node.callDecoration("getStack")
            if node_stack:
                if node_stack.getProperty("support_mesh", "value"):
                    self._removeSupportMesh(picked_node)
                    return

                elif node_stack.getProperty("anti_overhang_mesh", "value") or node_stack.getProperty("infill_mesh", "value") or node_stack.getProperty("cutting_mesh", "value"):
                    # Only "normal" meshes can have support_mesh added to them
                    return

            # Create a pass for picking a world-space location from the mouse location
            active_camera = self._controller.getScene().getActiveCamera()
            picking_pass = PickingPass(active_camera.getViewportWidth(), active_camera.getViewportHeight())
            picking_pass.render()

            picked_position = picking_pass.getPickedPosition(event.x, event.y)

            # Add the support_mesh cube at the picked location
            self._createSupportMesh(picked_node, picked_position)

    def _createSupportMesh(self, parent: CuraSceneNode, position: Vector):
        node = CuraSceneNode()

        if self._UseCube:
            node.setName("CustomSupportCube")
        else:
            node.setName("CustomSupportCylinder")
            
        node.setSelectable(True)
        
        # long=Support Height
        long=position.y

        if self._UseCube :
            # Cube creation Size , length
            mesh =  self._createCube(self._UseSize,long)
        else:
            # Cylinder creation Diameter , Increment angle 2°, length
            mesh = self._createCylinder(self._UseSize,2,long)
        
        node.setMeshData(mesh.build())

        active_build_plate = CuraApplication.getInstance().getMultiBuildPlateModel().activeBuildPlate
        node.addDecorator(BuildPlateDecorator(active_build_plate))
        node.addDecorator(SliceableObjectDecorator())

        stack = node.callDecoration("getStack") # created by SettingOverrideDecorator that is automatically added to CuraSceneNode
        settings = stack.getTop()

        for key in ["support_mesh", "support_mesh_drop_down"]:
            definition = stack.getSettingDefinition(key)
            new_instance = SettingInstance(definition, settings)
            new_instance.setProperty("value", True)
            new_instance.resetState()  # Ensure that the state is not seen as a user state.
            settings.addInstance(new_instance)

        op = GroupedOperation()
        # First add node to the scene at the correct position/scale, before parenting, so the support mesh does not get scaled with the parent
        op.addOperation(AddSceneNodeOperation(node, self._controller.getScene().getRoot()))
        op.addOperation(SetParentOperation(node, parent))
        op.push()
        node.setPosition(position, CuraSceneNode.TransformSpace.World)

        CuraApplication.getInstance().getController().getScene().sceneChanged.emit(node)

    def _removeSupportMesh(self, node: CuraSceneNode):
        parent = node.getParent()
        if parent == self._controller.getScene().getRoot():
            parent = None

        op = RemoveSceneNodeOperation(node)
        op.push()

        if parent and not Selection.isSelected(parent):
            Selection.add(parent)

        CuraApplication.getInstance().getController().getScene().sceneChanged.emit(node)

    def _updateEnabled(self):
        plugin_enabled = False

        global_container_stack = CuraApplication.getInstance().getGlobalContainerStack()
        if global_container_stack:
            plugin_enabled = global_container_stack.getProperty("support_mesh", "enabled")

        CuraApplication.getInstance().getController().toolEnabledChanged.emit(self._plugin_id, plugin_enabled)
    
    def _onSelectionChanged(self):
        # When selection is passed from one object to another object, first the selection is cleared
        # and then it is set to the new object. We are only interested in the change from no selection
        # to a selection or vice-versa, not in a change from one object to another. A timer is used to
        # "merge" a possible clear/select action in a single frame
        if Selection.hasSelection() != self._had_selection:
            self._had_selection_timer.start()

    def _selectionChangeDelay(self):
        has_selection = Selection.hasSelection()
        if not has_selection and self._had_selection:
            self._skip_press = True
        else:
            self._skip_press = False

        self._had_selection = has_selection
    
    # Cube creation
    def _createCube(self, size, height):
        mesh = MeshBuilder()

        # Can't use MeshBuilder.addCube() because that does not get per-vertex normals
        # Per-vertex normals require duplication of vertices
        s = size / 2
        l = height 
        verts = [ # 6 faces with 4 corners each
            [-s, -l,  s], [-s,  s,  s], [ s,  s,  s], [ s, -l,  s],
            [-s,  s, -s], [-s, -l, -s], [ s, -l, -s], [ s,  s, -s],
            [ s, -l, -s], [-s, -l, -s], [-s, -l,  s], [ s, -l,  s],
            [-s,  s, -s], [ s,  s, -s], [ s,  s,  s], [-s,  s,  s],
            [-s, -l,  s], [-s, -l, -s], [-s,  s, -s], [-s,  s,  s],
            [ s, -l, -s], [ s, -l,  s], [ s,  s,  s], [ s,  s, -s]
        ]
        mesh.setVertices(numpy.asarray(verts, dtype=numpy.float32))

        indices = []
        for i in range(0, 24, 4): # All 6 quads (12 triangles)
            indices.append([i, i+2, i+1])
            indices.append([i, i+3, i+2])
        mesh.setIndices(numpy.asarray(indices, dtype=numpy.int32))

        mesh.calculateNormals()
        return mesh
    
    # Cylinder creation
    def _createCylinder(self, size, nb , lg):
        mesh = MeshBuilder()
        # Per-vertex normals require duplication of vertices
        r = size / 2
        # additionale length
        sup = size * 0.1
        l = -lg
        rng = int(360 / nb)
        ang = math.radians(nb)
        
        verts = []
        for i in range(0, rng):
            # Top
            verts.append([0, sup, 0])
            verts.append([r*math.cos((i+1)*ang), sup, r*math.sin((i+1)*ang)])
            verts.append([r*math.cos(i*ang), sup, r*math.sin(i*ang)])
            #Side 1a
            verts.append([r*math.cos(i*ang), sup, r*math.sin(i*ang)])
            verts.append([r*math.cos((i+1)*ang), sup, r*math.sin((i+1)*ang)])
            verts.append([r*math.cos((i+1)*ang), l, r*math.sin((i+1)*ang)])
            #Side 1b
            verts.append([r*math.cos((i+1)*ang), l, r*math.sin((i+1)*ang)])
            verts.append([r*math.cos(i*ang), l, r*math.sin(i*ang)])
            verts.append([r*math.cos(i*ang), sup, r*math.sin(i*ang)])
            #Bottom 
            verts.append([0, l, 0])
            verts.append([r*math.cos((i+1)*ang), l, r*math.sin((i+1)*ang)]) 
            verts.append([r*math.cos(i*ang), l, r*math.sin(i*ang)])
            
        mesh.setVertices(numpy.asarray(verts, dtype=numpy.float32))

        indices = []
        # for every angle increment 12 Vertices
        tot = rng * 12
        for i in range(0, tot, 3): # 
            indices.append([i, i+1, i+2])
        mesh.setIndices(numpy.asarray(indices, dtype=numpy.int32))

        mesh.calculateNormals()
        return mesh
    
    def getSSize(self) -> float:
        """ 
            return: SSize  in mm.
        """           
        return self._UseSize
  
    def setSSize(self, SSize: str) -> None:
        """
        param SSize: Size in mm.
        """
 
        try:
            s_value = float(SSize)
        except ValueError:
            return

        if s_value <= 0:
            return
        
        #Logger.log('d', 's_value : ' + str(s_value))        
        self._UseSize = s_value
        self._preferences.setValue("customsupportcylinder/s_size", s_value)
 
    def getLockCube(self) -> bool:
        """
        Usecube
        """        
        # Logger.log('d', 'getLockCube : ' + str(self._UseCube))
        return self._UseCube
  
    def setLockCube(self, LockCube: bool) -> None:
        """
         Param lock for cube
        """
        #Logger.log('d', 'getLockCube : ' + str(LockCube))
        self._UseCube = LockCube

