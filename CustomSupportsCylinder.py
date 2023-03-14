#--------------------------------------------------------------------------------------------
# Initial Copyright(c) 2018 Ultimaker B.V.
# Copyright (c) 2022 5axes
#--------------------------------------------------------------------------------------------
# Based on the SupportBlocker plugin by Ultimaker B.V., and licensed under LGPLv3 or higher.
#
#  https://github.com/Ultimaker/Cura/tree/master/plugins/SupportEraser
#
#--------------------------------------------------------------------------------------------
# All modifications After 05-15-2020 Copyright(c) 5@xes 
#--------------------------------------------------------------------------------------------
# First release 05-18-2020  to change the initial plugin into cylindric support
# Modif 0.01 : Cylinder length -> Pick Point to base plate height
# Modif 0.02 : Using  support_tower_diameter as variable to define the cylinder
# Modif 0.03 : Using a special parameter  diameter_custom_support as variable to define the cylinder
# Modif 0.04 : Add a text field to define the diameter
# Modif 0.05 : Add checkbox and option to switch between Cube / Cylinder
# Modif 0.06 : Symplify code and store defaut size support in Preference "customsupportcylinder/s_size" default value 5
# V0.9.0 05-20-2020
# V1.0.0 06-01-2020 catalog.i18nc("@label","Size") on QML
# V1.0.1 06-20-2020 Add Angle for conical support
# V2.0.0 07-04-2020 Add Button and custom support type
# V2.0.1 
# V2.1.0 10-04-2020 Add Abutment support type
# V2.2.0 10-05-2020 Add Tube support type
# V2.3.0 10-18-2020 Add Y direction and Equalize heights for Abutment support type
# V2.4.0 01-21-2021 New option Max size to limit the size of the base
# V2.4.1 01-24-2021 By default support are not define with the property support_mesh_drop_down = True
# V2.5.0 03-07-2021 Freeform (Cross/Section/Pillar/Custom)
# V2.5.1 03-08-2021 Mirror & Rotate freeform support
# V2.5.2 03-09-2021 Bridge freeform support Bridge and rename Pillar
# V2.5.3 03-10-2021 Add "arch-buttress" type
# V2.5.5 03-11-2021 Minor modification on freeform design
#
# V2.6.0 03-05-2022 Update for Cura 5.0
# V2.6.1 18-05-2022 Update for Cura 5.0 QML with UM.ToolbarButton
# V2.6.2 19-05-2022 Scale Also in Main direction
# V2.6.3 25-05-2022 Temporary ? solution for the Toolbar height in QT6
# V2.6.4 31-05-2022 Add Button Remove All
#                   Increase the Increment angle for Cylinder and Tube from 2° to 10°
# V2.6.5 11-07-2022 Change Style of Button for Cura 5.0  5.1
# V2.6.6 07-08-2022 Internal modification for Maximum Z height
# V2.7.0 18-01-2023 Prepare translation
# V2.7.1 02-02-2023 Replace Rotation 180° / Auto Orientation for FreeForm Model
#
# V2.8.0 09-02-2023 Add Define As Model For Cylindrical Model
# V2.8.1 20-02-2023 Change Code for automatic orientation
# V2.8.2 13-03-2023 Change Location for qml & i18n
#--------------------------------------------------------------------------------------------

VERSION_QT5 = False
try:
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtWidgets import QApplication
except ImportError:
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtWidgets import QApplication
    VERSION_QT5 = True

import math
import numpy
import os.path
import trimesh

from typing import Optional, List

from cura.CuraApplication import CuraApplication
from cura.PickingPass import PickingPass
from cura.Operations.SetParentOperation import SetParentOperation
from cura.Scene.SliceableObjectDecorator import SliceableObjectDecorator
from cura.Scene.BuildPlateDecorator import BuildPlateDecorator
from cura.Scene.CuraSceneNode import CuraSceneNode

from UM.Logger import Logger
from UM.Message import Message
from UM.Math.Matrix import Matrix
from UM.Math.Vector import Vector
from UM.Tool import Tool
from UM.Event import Event, MouseEvent
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Mesh.MeshData import MeshData, calculateNormalsFromIndexedVertices
from UM.Operations.GroupedOperation import GroupedOperation
from UM.Operations.AddSceneNodeOperation import AddSceneNodeOperation
from UM.Operations.RemoveSceneNodeOperation import RemoveSceneNodeOperation
from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator
from UM.Scene.Selection import Selection
from UM.Scene.SceneNode import SceneNode
from UM.Tool import Tool
from UM.Settings.SettingInstance import SettingInstance
from UM.Resources import Resources
from UM.i18n import i18nCatalog

i18n_cura_catalog = i18nCatalog("cura")
i18n_catalog = i18nCatalog("fdmprinter.def.json")
i18n_extrud_catalog = i18nCatalog("fdmextruder.def.json")

Resources.addSearchPath(
    os.path.join(os.path.abspath(os.path.dirname(__file__)),'resources')
)  # Plugin translation file import

catalog = i18nCatalog("customsupport")

if catalog.hasTranslationLoaded():
    Logger.log("i", "Custom Support Cylinder Plugin translation loaded!")

class CustomSupportsCylinder(Tool):
    def __init__(self):
       
        super().__init__()
        
        self._all_picked_node = []
        
        self._Nb_Point = 0  
        self._SHeights = 0
        
        # variable for menu dialog        
        self._UseSize = 2.0
        self._MaxSize = 10.0
        self._UseISize = 0.0
        self._UseAngle = 0.0
        self._UseYDirection = False
        self._EqualizeHeights = True
        self._ScaleMainDirection = True
        self._OrientSupport = False
        self._MirrorSupport = False
        self._DefineAsModel = False
        self._SType = 'cylinder'
        self._SubType = 'cross'
        self._Mesg = False # To avoid message 
        self._SMsg = catalog.i18nc("@label", "Remove All") 
        
        # Shortcut
        if not VERSION_QT5:
            self._shortcut_key = Qt.Key.Key_F
        else:
            self._shortcut_key = Qt.Key_F
            
        self._controller = self.getController()

        self._Svg_Position = Vector
        self._selection_pass = None
        
        self._application = CuraApplication.getInstance()
        
        self.setExposedProperties("SSize", "MSize", "ISize", "AAngle", "SType" , "AsModel", "YDirection" , "EHeights" , "SMain" , "SubType" , "SOrient", "SMirror", "SMsg")
        
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
        
        # set the preferences to store the default value
        self._preferences = CuraApplication.getInstance().getPreferences()
        self._preferences.addPreference("customsupportcylinder/s_size", 5)
        self._preferences.addPreference("customsupportcylinder/m_size", 10)
        self._preferences.addPreference("customsupportcylinder/i_size", 2)
        self._preferences.addPreference("customsupportcylinder/a_angle", 0)
        self._preferences.addPreference("customsupportcylinder/d_model", False)
        self._preferences.addPreference("customsupportcylinder/y_direction", False)
        self._preferences.addPreference("customsupportcylinder/e_heights", True)
        self._preferences.addPreference("customsupportcylinder/scale_main_direction", True)
        self._preferences.addPreference("customsupportcylinder/s_orient", False)
        self._preferences.addPreference("customsupportcylinder/s_mirror", False)
        self._preferences.addPreference("customsupportcylinder/t_type", "cylinder")
        self._preferences.addPreference("customsupportcylinder/s_type", "cross")
        
        # convert as float to avoid further issue
        self._UseSize = float(self._preferences.getValue("customsupportcylinder/s_size"))
        self._MaxSize = float(self._preferences.getValue("customsupportcylinder/m_size"))
        self._UseISize = float(self._preferences.getValue("customsupportcylinder/i_size"))
        self._UseAngle = float(self._preferences.getValue("customsupportcylinder/a_angle"))
        # convert as boolean to avoid further issue
        
        self._DefineAsModel = bool(self._preferences.getValue("customsupportcylinder/d_model"))
        self._UseYDirection = bool(self._preferences.getValue("customsupportcylinder/y_direction"))
        self._EqualizeHeights = bool(self._preferences.getValue("customsupportcylinder/e_heights"))
        self._ScaleMainDirection = bool(self._preferences.getValue("customsupportcylinder/scale_main_direction"))
        self._OrientSupport = bool(self._preferences.getValue("customsupportcylinder/s_orient"))
        self._MirrorSupport = bool(self._preferences.getValue("customsupportcylinder/s_mirror"))
        # convert as string to avoid further issue
        self._SType = str(self._preferences.getValue("customsupportcylinder/t_type"))
        # Sub type for Free Form support
        self._SubType = str(self._preferences.getValue("customsupportcylinder/s_type"))       
                
    def event(self, event):
        super().event(event)
        modifiers = QApplication.keyboardModifiers()
        if not VERSION_QT5:
            ctrl_is_active = modifiers & Qt.KeyboardModifier.ControlModifier
            shift_is_active = modifiers & Qt.KeyboardModifier.ShiftModifier
            alt_is_active = modifiers & Qt.KeyboardModifier.AltModifier
        else:
            ctrl_is_active = modifiers & Qt.ControlModifier
            shift_is_active = modifiers & Qt.ShiftModifier
            alt_is_active = modifiers & Qt.AltModifier

        
        if event.type == Event.MousePressEvent and MouseEvent.LeftButton in event.buttons and self._controller.getToolsEnabled():
            if ctrl_is_active:
                self._controller.setActiveTool("TranslateTool")
                return

            if alt_is_active:
                self._controller.setActiveTool("RotateTool")
                return
                
            if self._skip_press:
                # The selection was previously cleared, do not add/remove an support mesh but
                # use this click for selection and reactivating this tool only.
                self._skip_press = False
                self._SHeights=0
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
                if (node_stack.getProperty("support_mesh", "value")  or  node_stack.getProperty("infill_mesh_order", "value") == 50 ) and not alt_is_active:
                    self._removeSupportMesh(picked_node)
                    self._SHeights=0
                    return

                elif node_stack.getProperty("anti_overhang_mesh", "value") or node_stack.getProperty("infill_mesh", "value") or node_stack.getProperty("cutting_mesh", "value"):
                    # Only "normal" meshes can have support_mesh added to them
                    return

            # Create a pass for picking a world-space location from the mouse location
            active_camera = self._controller.getScene().getActiveCamera()
            picking_pass = PickingPass(active_camera.getViewportWidth(), active_camera.getViewportHeight())
            picking_pass.render()
            
            
            if self._SType == 'custom': 
                self._Nb_Point += 1
                if self._Nb_Point == 2 :
                    picked_position =  self._Svg_Position 
                    picked_position_b = picking_pass.getPickedPosition(event.x, event.y)
                    self._Svg_Position = picked_position_b
                    self._Nb_Point = 0
                    # Add the support_mesh cube at the picked location
                    self._createSupportMesh(picked_node, picked_position,picked_position_b)
                else:
                    self._Svg_Position = picking_pass.getPickedPosition(event.x, event.y)
            
            else:
                self._Nb_Point = 0
                picked_position =  picking_pass.getPickedPosition(event.x, event.y)
                picked_position_b = picking_pass.getPickedPosition(event.x, event.y)
                self._Svg_Position = picked_position_b
                    
                # Add the support_mesh cube at the picked location
                self._createSupportMesh(picked_node, picked_position,picked_position_b)
                
    def _createSupportMesh(self, parent: CuraSceneNode, position: Vector , position2: Vector):
        node = CuraSceneNode()
        EName = parent.getName()

        node_bounds = parent.getBoundingBox()
        self._nodeHeight = node_bounds.height
        
        # Logger.log("d", "Height Model= %s", str(node_bounds.height))
        
        if self._SType == 'cylinder':
            node.setName("CustomSupportCylinder")
        elif self._SType == 'tube':
            node.setName("CustomSupportTube")
        elif self._SType == 'cube':
            node.setName("CustomSupportCube")
        elif self._SType == 'abutment':
            node.setName("CustomSupportAbutment")
        elif self._SType == 'freeform':
            node.setName("CustomSupportFreeForm")            
        else:
            node.setName("CustomSupportCustom")
            
        node.setSelectable(True)
        
        # long=Support Height
        self._long=position.y
        # Logger.log("d", "Long Support= %s", str(self._long))
        
        # Limitation for support height to Node Height
        # For Cube/Cylinder/Tube
        # Test with 0.5 because the precision on the clic poisition is not very thight 
        if self._long >= (self._nodeHeight-0.5) :
            # additionale length
            self._Sup = 0
        else :
            if self._SType == 'cube' :
                self._Sup = self._UseSize*0.5
            elif self._SType == 'abutment':
                self._Sup = self._UseSize
            else :
                self._Sup = self._UseSize*0.1
                
        # Logger.log("d", "Additional Long Support = %s", str(self._long+self._Sup))    
            
        if self._SType == 'cylinder':
            # Cylinder creation Diameter , Maximum diameter , Increment angle 10°, length , top Additional Height, Angle of the support
            mesh = self._createCylinder(self._UseSize,self._MaxSize,10,self._long,self._Sup,self._UseAngle)
        elif self._SType == 'tube':
            # Tube creation Diameter ,Maximum diameter , Diameter Int, Increment angle 10°, length, top Additional Height , Angle of the support
            mesh =  self._createTube(self._UseSize,self._MaxSize,self._UseISize,10,self._long,self._Sup,self._UseAngle)
        elif self._SType == 'cube':
            # Cube creation Size,Maximum Size , length , top Additional Height, Angle of the support
            mesh =  self._createCube(self._UseSize,self._MaxSize,self._long,self._Sup,self._UseAngle)
        elif self._SType == 'freeform':
            # Cube creation Size , length
            mesh = MeshBuilder()  
            MName = self._SubType + ".stl"
            model_definition_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", MName)
            # Logger.log('d', 'Model_definition_path : ' + str(model_definition_path)) 
            load_mesh = trimesh.load(model_definition_path)
            origin = [0, 0, 0]
            DirX = [1, 0, 0]
            DirY = [0, 1, 0]
            DirZ = [0, 0, 1]
            
            # Solution must be tested ( other solution just on the X Axis)
            if self._ScaleMainDirection :
                if (self._long * 0.5 ) < self._UseSize :
                    Scale = self._UseSize
                else :
                    Scale = self._long * 0.5
                load_mesh.apply_transform(trimesh.transformations.scale_matrix(Scale, origin, DirX))
                load_mesh.apply_transform(trimesh.transformations.scale_matrix(Scale, origin, DirY))
            else :
                load_mesh.apply_transform(trimesh.transformations.scale_matrix(self._UseSize, origin, DirX))
                load_mesh.apply_transform(trimesh.transformations.scale_matrix(self._UseSize, origin, DirY))
                
            # load_mesh.apply_transform(trimesh.transformations.scale_matrix(self._UseSize, origin, DirY))
 
            load_mesh.apply_transform(trimesh.transformations.scale_matrix(self._long, origin, DirZ)) 
            
            # Logger.log('d', "Info Orient Support --> " + str(self._OrientSupport))
            if self._OrientSupport == True :
                key = "adhesion_type"
                # This function can be triggered in the middle of a machine change, so do not proceed if the machine change has not done yet.
                global_container_stack = CuraApplication.getInstance().getGlobalContainerStack()
                #extruder = global_container_stack.extruderList[int(_id_ex)] 
                extruder_stack = CuraApplication.getInstance().getExtruderManager().getActiveExtruderStacks()[0]                
                adhesion=global_container_stack.getProperty(key, "value") 
                   
                if adhesion ==  'none' :
                    if not self._Mesg :
                        definition_key=key + " label"
                        untranslated_label=extruder_stack.getProperty(key,"label")
                        translated_label=i18n_catalog.i18nc(definition_key, untranslated_label) 
                        Format_String = catalog.i18nc("@info:label", "Info modification current profile '") + translated_label  + catalog.i18nc("@info:label", "' parameter\nNew value : ") + catalog.i18nc("@info:label", "Skirt")                
                        Message(text = Format_String, title = catalog.i18nc("@info:title", "Warning ! Custom Supports Cylinder")).show()
                        self._Mesg = True
                    # Define temporary adhesion_type=skirt to force boundary calculation ?
                    global_container_stack.setProperty(key, "value", 'skirt')
                    Logger.log('d', "Info adhesion_type --> " + str(adhesion)) 
                _angle = self._defineAngle(EName,position)
                if self._UseYDirection == True :
                    _angle = self.mainAngle(_angle)
                Logger.log('d', 'Angle : ' + str(_angle))
                load_mesh.apply_transform(trimesh.transformations.rotation_matrix(_angle, [0, 0, 1]))
            
            elif self._UseYDirection == True :
                load_mesh.apply_transform(trimesh.transformations.rotation_matrix(math.radians(90), [0, 0, 1]))

            if self._MirrorSupport == True and self._OrientSupport == False :   
                load_mesh.apply_transform(trimesh.transformations.rotation_matrix(math.radians(180), [0, 0, 1]))
                
            mesh =  self._toMeshData(load_mesh)
            
        elif self._SType == 'abutment':
            # Abutement creation Size , length , top
            if self._EqualizeHeights == True :
                # Logger.log('d', 'SHeights : ' + str(self._SHeights)) 
                if self._SHeights==0 :
                    self._SHeights=position.y
                    self._SSup=self._Sup

                self._top=self._SSup+(self._SHeights-position.y)
                
            else:
                self._top=self._Sup
                self._SHeights=0
            
            # 
            Logger.log('d', 'top : ' + str(self._top))
            # Logger.log('d', 'MaxSize : ' + str(self._MaxSize))
            
            mesh =  self._createAbutment(self._UseSize,self._MaxSize,self._long,self._top,self._UseAngle,self._UseYDirection)
        else:           
            # Custom creation Size , P1 as vector P2 as vector
            # Get support_interface_height as extra distance 
            extruder_stack = self._application.getExtruderManager().getActiveExtruderStacks()[0]
            if self._Sup == 0 :
                extra_top = 0
            else :
                extra_top=extruder_stack.getProperty("support_interface_height", "value")            
            mesh =  self._createCustom(self._UseSize,self._MaxSize,position,position2,self._UseAngle,extra_top)

        # Mesh Freeform are loaded via trimesh doesn't aheve the Build method
        if self._SType != 'freeform':
            node.setMeshData(mesh.build())
        else:
            node.setMeshData(mesh)

        # test for init position
        node_transform = Matrix()
        node_transform.setToIdentity()
        node.setTransformation(node_transform)
        
        active_build_plate = CuraApplication.getInstance().getMultiBuildPlateModel().activeBuildPlate
        node.addDecorator(BuildPlateDecorator(active_build_plate))
        node.addDecorator(SliceableObjectDecorator())
              
        stack = node.callDecoration("getStack") # created by SettingOverrideDecorator that is automatically added to CuraSceneNode

        settings = stack.getTop()

        # Define the new mesh as "support_mesh" or "support_mesh_drop_down"
        # Must be set for this 2 types
        # for key in ["support_mesh", "support_mesh_drop_down"]:
        # Don't fix
        
        if self._DefineAsModel and self._SType == 'cylinder' :   
            
            definition = stack.getSettingDefinition("meshfix_union_all")
            new_instance = SettingInstance(definition, settings)
            new_instance.setProperty("value", False)
            new_instance.resetState()  # Ensure that the state is not seen as a user state.
            settings.addInstance(new_instance)
            
            definition = stack.getSettingDefinition("infill_mesh_order")
            new_instance = SettingInstance(definition, settings)
            new_instance.setProperty("value", 50) #50 "maximum_value_warning": "50"
            new_instance.resetState()  # Ensure that the state is not seen as a user state.
            settings.addInstance(new_instance)               

            definition = stack.getSettingDefinition("infill_sparse_density")
            new_instance = SettingInstance(definition, settings)
            new_instance.setProperty("value", 0) # set infill density to 0
            new_instance.resetState()  # Ensure that the state is not seen as a user state.
            settings.addInstance(new_instance)

            definition = stack.getSettingDefinition("wall_line_count")
            new_instance = SettingInstance(definition, settings)
            new_instance.setProperty("value", 1) # Set wall_line_count to 1
            new_instance.resetState()  # Ensure that the state is not seen as a user state.
            settings.addInstance(new_instance)
            
        else:
            definition = stack.getSettingDefinition("support_mesh")
            new_instance = SettingInstance(definition, settings)
            new_instance.setProperty("value", True)
            new_instance.resetState()  # Ensure that the state is not seen as a user state.
            settings.addInstance(new_instance)

            definition = stack.getSettingDefinition("support_mesh_drop_down")
            new_instance = SettingInstance(definition, settings)
            new_instance.setProperty("value", False)
            new_instance.resetState()  # Ensure that the state is not seen as a user state.
            settings.addInstance(new_instance)

        global_container_stack = CuraApplication.getInstance().getGlobalContainerStack()    
        
        s_p = global_container_stack.getProperty("support_type", "value")
        if s_p ==  'buildplate' :
            Message(text = catalog.i18nc("@info:label", "Info modification support_type new value : Everywhere"), title = catalog.i18nc("@info:title", "Warning ! Custom Supports Cylinder")).show()
            Logger.log('d', 'Support_type different from everywhere : ' + str(s_p))
            # Define support_type=everywhere
            global_container_stack.setProperty("support_type", "value", 'everywhere')
            
        op = GroupedOperation()
        # First add node to the scene at the correct position/scale, before parenting, so the support mesh does not get scaled with the parent
        op.addOperation(AddSceneNodeOperation(node, self._controller.getScene().getRoot()))
        op.addOperation(SetParentOperation(node, parent))
        op.push()
        node.setPosition(position, CuraSceneNode.TransformSpace.World)
        self._all_picked_node.append(node)
        self._SMsg = catalog.i18nc("@label", "Remove Last") 
        self.propertyChanged.emit()
        
        CuraApplication.getInstance().getController().getScene().sceneChanged.emit(node)

    # Source code from MeshTools Plugin 
    # Copyright (c) 2020 Aldo Hoeben / fieldOfView
    def _getAllSelectedNodes(self) -> List[SceneNode]:
        selection = Selection.getAllSelectedObjects()[:]
        if selection:
            deep_selection = []  # type: List[SceneNode]
            for selected_node in selection:
                if selected_node.hasChildren():
                    deep_selection = deep_selection + selected_node.getAllChildren()
                if selected_node.getMeshData() != None:
                    deep_selection.append(selected_node)
            if deep_selection:
                return deep_selection

        # Message(catalog.i18nc("@info:status", "Please select one or more models first"))

        return []
 

    def mainAngle(self, radian : float) -> float:
        degree = math.degrees(radian)
        degree = round(degree / 90) * 90
        return math.radians(degree)   

    def _distance(self,p1, p2):
        """Calculates the distance between two points."""
        x1, y1 = p1
        x2, y2 = p2
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def _closest_point_on_segment(self, segment, point):
        """Find the closest point between a segment and a given point."""
        p, q = segment
        pq_distance = self._distance(p, q)
        if pq_distance == 0:
            return p
        u = ((point[0] - p[0]) * (q[0] - p[0]) + (point[1] - p[1]) * (q[1] - p[1])) / pq_distance ** 2
        if u < 0:
            return p
        elif u > 1:
            return q
        else:
            return (p[0] + u * (q[0] - p[0]), p[1] + u * (q[1] - p[1]))
            
    def _defineAngle(self, Cname : str, act_position: Vector) -> float:
        Angle = 0
        min_lght = 9999999.999
        # Set on the build plate for distance
        calc_position = Vector(act_position.x, 0, act_position.z)
        # Logger.log('d', "Mesh : {}".format(Cname))
        # Logger.log('d', "Position : {}".format(calc_position))

        nodes_list = self._getAllSelectedNodes()
        if not nodes_list:
            nodes_list = DepthFirstIterator(self._application.getController().getScene().getRoot())
         
        for node in nodes_list:
            if node.callDecoration("isSliceable"):
                # Logger.log('d', "isSliceable : {}".format(node.getName()))
                node_stack=node.callDecoration("getStack")           
                if node_stack:                    
                    if node.getName()==Cname :
                        # Logger.log('d', "Mesh : {}".format(node.getName()))
                        
                        hull_polygon = node.callDecoration("getAdhesionArea")
                        # hull_polygon = node.callDecoration("getConvexHull")
                        # hull_polygon = node.callDecoration("getConvexHullBoundary")
                        # hull_polygon = node.callDecoration("_compute2DConvexHull")
                                   
                        if not hull_polygon or hull_polygon.getPoints is None:
                            Logger.log("w", "Object {} cannot be calculated because it has no convex hull.".format(node.getName()))
                            return 0
                            
                        points=hull_polygon.getPoints()
                        # nb_pt = point[0] / point[1] must be divided by 2
                        Id=0
                        Start_Id=0
                        End_Id=0
                        for point in points:                               
                            # Logger.log('d', "X : {}".format(point[0]))
                            # Logger.log('d', "Point : {}".format(point))
                            new_position = Vector(point[0], 0, point[1])
                            lg=calc_position-new_position
                            # Logger.log('d', "Lg : {}".format(lg))
                            # lght = lg.length()
                            lght = round(lg.length(),0)

                            if lght<min_lght and lght>0 :
                                min_lght=lght
                                Start_Id=Id
                                Select_position = new_position                                   
                                    
                            if lght==min_lght and lght>0 :
                                if Id > End_Id+1 :
                                    Start_Id=Id
                                    End_Id=Id
                                else :
                                    End_Id=Id
                                    
                            Id+=1
                        
                        # Could be the case in pickpoint 
                        # Logger.log('d', "Start_Id : {}".format(Start_Id))
                        # Logger.log('d', "End_Id : {}".format(End_Id))
                        if Start_Id == End_Id :
                            # Add First point at the end for Segment Analyse
                            if Start_Id < len(points)-1 :
                                p1 = points[Start_Id]
                                p2 = points[Start_Id+1]
                            else :
                                p1 = points[Start_Id]
                                p2 = points[0]
                                
                            segment = ((p1[0], p1[1]), (p2[0], p2[1]))
                            # Logger.log('d', "Segment : {}".format(segment))
                            pt = (calc_position.x, calc_position.z)
                            # Logger.log('d', "Point : {}".format(pt))
                            pt_r=self._closest_point_on_segment(segment,pt)
                            # Logger.log('d', "Closest_point_on_segment : {}".format(pt_r))
                            new_position = Vector(pt_r[0], 0, pt_r[1]) 
                            lg=calc_position-new_position
                            lght = round(lg.length(),0)
                            
                            if lght<min_lght and lght>0 :                                
                                # Logger.log('d', "New_position : {}".format(new_position))
                                Select_position = new_position
 
                            if Start_Id > 0 :
                                p1 = points[Start_Id-1]
                                p2 = points[Start_Id]
                            else :
                                p1 = points[len(points)-1]
                                p2 = points[0]
                                
                            segment = ((p1[0], p1[1]), (p2[0], p2[1]))
                            # Logger.log('d', "Segment : {}".format(segment))
                            pt = (calc_position.x, calc_position.z)
                            # Logger.log('d', "Point : {}".format(pt))
                            pt_r=self._closest_point_on_segment(segment,pt)
                            # Logger.log('d', "Closest_point_on_segment : {}".format(pt_r))
                            new_position = Vector(pt_r[0], 0, pt_r[1]) 
                            lg=calc_position-new_position
                            lght = round(lg.length(),0)
                            
                            if lght<min_lght and lght>0 :                                
                                # Logger.log('d', "New_position : {}".format(new_position))
                                Select_position = new_position
                                
                        else : # Could be the case with automatic .. rarely in pickpoint 
                            Id=int(Start_Id+0.5*(End_Id-Start_Id))
                            # Logger.log('d', "Id : {}".format(Id))
                            Select_position = Vector(points[Id][0], 0, points[Id][1])
                            
                            
                        lg=calc_position-Select_position                            
                        unit_vector2 = lg.normalized()
                        LeSin = math.asin(ref.dot(unit_vector2))
                        # LeCos = math.acos(ref.dot(unit_vector2))
                        
                        if unit_vector2.x >=0 :
                            Angle = math.pi-LeSin  #angle in radian                              
                        else :
                            Angle = LeSin
                                
                        # Logger.log('d', "Pick_position   : {}".format(calc_position))
                        # Logger.log('d', "Close_position  : {}".format(Select_position))
                        # Logger.log('d', "Unit_vector2    : {}".format(unit_vector2))
                        # Logger.log('d', "Angle Sinus     : {}".format(math.degrees(LeSin)))
                        # Logger.log('d', "Angle Cosinus   : {}".format(math.degrees(LeCos)))
                        # Logger.log('d', "Chose Angle     : {}".format(math.degrees(Angle)))
        return Angle
        
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
 
    # Initial Source code from fieldOfView
    def _toMeshData(self, tri_node: trimesh.base.Trimesh) -> MeshData:
        # Rotate the part to laydown on the build plate
        # Modification from 5@xes
        tri_node.apply_transform(trimesh.transformations.rotation_matrix(math.radians(90), [-1, 0, 0]))
        tri_faces = tri_node.faces
        tri_vertices = tri_node.vertices
        # Following code from fieldOfView
        # https://github.com/fieldOfView/Cura-SimpleShapes/blob/bac9133a2ddfbf1ca6a3c27aca1cfdd26e847221/SimpleShapes.py#L45

        indices = []
        vertices = []

        index_count = 0
        face_count = 0
        for tri_face in tri_faces:
            face = []
            for tri_index in tri_face:
                vertices.append(tri_vertices[tri_index])
                face.append(index_count)
                index_count += 1
            indices.append(face)
            face_count += 1

        vertices = numpy.asarray(vertices, dtype=numpy.float32)
        indices = numpy.asarray(indices, dtype=numpy.int32)
        normals = calculateNormalsFromIndexedVertices(vertices, indices, face_count)

        mesh_data = MeshData(vertices=vertices, indices=indices, normals=normals)

        return mesh_data
        
    # Cube Creation
    def _createCube(self, size, maxs, height, top, dep):
        mesh = MeshBuilder()

        # Intial Comment from Ultimaker B.V. I have never try to verify this point
        # Can't use MeshBuilder.addCube() because that does not get per-vertex normals
        # Per-vertex normals require duplication of vertices
        s = size / 2
        sm = maxs / 2
        l = height 
        s_inf=s+math.tan(math.radians(dep))*(l+top)
        
        if sm>s and dep!=0:
            l_max=(sm-s) / math.tan(math.radians(dep))
        else :
            l_max=l
        
        # Difference between Cone and Cone + max base size
        if l_max<l and l_max>0:
            nbv=40        
            verts = [ # 10 faces with 4 corners each
                [-sm, -l_max,  sm], [-s,  top,  s], [ s,  top,  s], [ sm, -l_max,  sm],
                [-s,  top, -s], [-sm, -l_max, -sm], [ sm, -l_max, -sm], [ s,  top, -s],
                [-sm, -l,  sm], [-sm,  -l_max,  sm], [ sm,  -l_max,  sm], [ sm, -l,  sm],
                [-sm,  -l_max, -sm], [-sm, -l, -sm], [ sm, -l, -sm], [ sm,  -l_max, -sm],
                [ sm, -l, -sm], [-sm, -l, -sm], [-sm, -l,  sm], [ sm, -l,  sm],
                [-s,  top, -s], [ s,  top, -s], [ s,  top,  s], [-s,  top,  s],
                [-sm, -l,  sm], [-sm, -l, -sm], [-sm,  -l_max, -sm], [-sm,  -l_max,  sm],
                [ sm, -l, -sm], [ sm, -l,  sm], [ sm,  -l_max,  sm], [ sm,  -l_max, -sm],  
                [-sm, -l_max,  sm], [-sm, -l_max, -sm], [-s,  top, -s], [-s,  top,  s],
                [ sm, -l_max, -sm], [ sm, -l_max,  sm], [ s,  top,  s], [ s,  top, -s]
            ]       
        else:
            nbv=24        
            verts = [ # 6 faces with 4 corners each
                [-s_inf, -l,  s_inf], [-s,  top,  s], [ s,  top,  s], [ s_inf, -l,  s_inf],
                [-s,  top, -s], [-s_inf, -l, -s_inf], [ s_inf, -l, -s_inf], [ s,  top, -s],
                [ s_inf, -l, -s_inf], [-s_inf, -l, -s_inf], [-s_inf, -l,  s_inf], [ s_inf, -l,  s_inf],
                [-s,  top, -s], [ s,  top, -s], [ s,  top,  s], [-s,  top,  s],
                [-s_inf, -l,  s_inf], [-s_inf, -l, -s_inf], [-s,  top, -s], [-s,  top,  s],
                [ s_inf, -l, -s_inf], [ s_inf, -l,  s_inf], [ s,  top,  s], [ s,  top, -s]
            ]
        mesh.setVertices(numpy.asarray(verts, dtype=numpy.float32))

        indices = []
        for i in range(0, nbv, 4): # All 6 quads (12 triangles)
            indices.append([i, i+2, i+1])
            indices.append([i, i+3, i+2])
        mesh.setIndices(numpy.asarray(indices, dtype=numpy.int32))

        mesh.calculateNormals()
        return mesh
        
    # Abutment Creation
    def _createAbutment(self, size, maxs, height, top, dep, ydir):
    
        # Logger.log('d', 'Ydir : ' + str(ydir)) 
        mesh = MeshBuilder()

        s = size / 2
        sm = maxs / 2
        l = height 
        s_inf=math.tan(math.radians(dep))*(l+top)+(2*s)
        
        if sm>s and dep!=0:
            l_max=(sm-s) / math.tan(math.radians(dep))
        else :
            l_max=l
        
        # Debug Log Lines
        # Logger.log('d', 's_inf : ' + str(s_inf))
        # Logger.log('d', 'l_max : ' + str(l_max)) 
        # Logger.log('d', 'l : ' + str(l))
        
        # Difference between Standart Abutment and Abutment + max base size
        if l_max<l and l_max>0:
            nbv=40  
            if ydir == False :
                verts = [ # 10 faces with 4 corners each
                    [-s, -l_max,  sm], [-s,  top,  2*s], [ s,  top,  2*s], [ s, -l_max,  sm],
                    [-s,  top, -2*s], [-s, -l_max, -sm], [ s, -l_max, -sm], [ s,  top, -2*s],
                    [-s, -l,  sm], [-s,  -l_max,  sm], [ s,  -l_max,  sm], [ s, -l,  sm],
                    [-s,  -l_max, -sm], [-s, -l, -sm], [ s, -l, -sm], [ s,  -l_max, -sm],                  
                    [ s, -l, -sm], [-s, -l, -sm], [-s, -l,  sm], [ s, -l,  sm],
                    [-s,  top, -2*s], [ s,  top, -2*s], [ s,  top,  2*s], [-s,  top,  2*s],
                    [-s, -l_max,  sm], [-s, -l_max, -sm], [-s,  top, -2*s], [-s,  top,  2*s],
                    [ s, -l_max, -sm], [ s, -l_max,  sm], [ s,  top,  2*s], [ s,  top, -2*s],                   
                    [-s, -l,  sm], [-s, -l, -sm], [-s,  -l_max, -sm], [-s,  -l_max,  sm],
                    [ s, -l, -sm], [ s, -l,  sm], [ s,  -l_max,  sm], [ s,  -l_max, -sm]
                ]
            else:
                verts = [ # 10 faces with 4 corners each
                    [-sm, -l_max,  s], [-2*s,  top,  s], [ 2*s,  top,  s], [ sm, -l_max,  s],
                    [-2*s,  top, -s], [-sm, -l_max, -s], [ sm, -l_max, -s], [ 2*s,  top, -s],                
                    [-sm, -l,  s], [-sm,  -l_max,  s], [ sm,  -l_max,  s], [ sm, -l,  s],
                    [-sm,  -l_max, -s], [-sm, -l, -s], [ sm, -l, -s], [ sm,  -l_max, -s],                         
                    [ sm, -l, -s], [-sm, -l, -s], [-sm, -l,  s], [ sm, -l,  s],
                    [-2*s,  top, -s], [ 2*s,  top, -s], [ 2*s,  top,  s], [-2*s,  top,  s],             
                    [-sm, -l_max,  s], [-sm, -l_max, -s], [-2*s,  top, -s], [-2*s,  top,  s],
                    [ sm, -l_max, -s], [ sm, -l_max,  s], [ 2*s,  top,  s], [ 2*s,  top, -s],                                  
                    [-sm, -l,  s], [-sm, -l, -s], [-sm,  -l_max, -s], [-sm,  -l_max,  s],
                    [ sm, -l, -s], [ sm, -l,  s], [ sm,  -l_max,  s], [ sm,  -l_max, -s]
                ]             
        else:
            nbv=24        
            if ydir == False :
                verts = [ # 6 faces with 4 corners each
                    [-s, -l,  s_inf], [-s,  top,  2*s], [ s,  top,  2*s], [ s, -l,  s_inf],
                    [-s,  top, -2*s], [-s, -l, -s_inf], [ s, -l, -s_inf], [ s,  top, -2*s],
                    [ s, -l, -s_inf], [-s, -l, -s_inf], [-s, -l,  s_inf], [ s, -l,  s_inf],
                    [-s,  top, -2*s], [ s,  top, -2*s], [ s,  top,  2*s], [-s,  top,  2*s],
                    [-s, -l,  s_inf], [-s, -l, -s_inf], [-s,  top, -2*s], [-s,  top,  2*s],
                    [ s, -l, -s_inf], [ s, -l,  s_inf], [ s,  top,  2*s], [ s,  top, -2*s]
                ]
            else:
                verts = [ # 6 faces with 4 corners each
                    [-s_inf, -l,  s], [-2*s,  top,  s], [ 2*s,  top,  s], [ s_inf, -l,  s],
                    [-2*s,  top, -s], [-s_inf, -l, -s], [ s_inf, -l, -s], [ 2*s,  top, -s],
                    [ s_inf, -l, -s], [-s_inf, -l, -s], [-s_inf, -l,  s], [ s_inf, -l,  s],
                    [-2*s,  top, -s], [ 2*s,  top, -s], [ 2*s,  top,  s], [-2*s,  top,  s],
                    [-s_inf, -l,  s], [-s_inf, -l, -s], [-2*s,  top, -s], [-2*s,  top,  s],
                    [ s_inf, -l, -s], [ s_inf, -l,  s], [ 2*s,  top,  s], [ 2*s,  top, -s]
                ]        
        mesh.setVertices(numpy.asarray(verts, dtype=numpy.float32))

        indices = []
        for i in range(0, nbv, 4): # All 6 quads (12 triangles)
            indices.append([i, i+2, i+1])
            indices.append([i, i+3, i+2])
        mesh.setIndices(numpy.asarray(indices, dtype=numpy.int32))

        mesh.calculateNormals()
        return mesh
        
    # Cylinder creation
    def _createCylinder(self, size, maxs, nb , lg , sup ,dep):
        mesh = MeshBuilder()
        # Per-vertex normals require duplication of vertices
        r = size / 2
        rm = maxs / 2

        l = -lg
        rng = int(360 / nb)
        ang = math.radians(nb)
        r_inf=math.tan(math.radians(dep))*lg+r
        if rm>r and dep!=0 :
            l_max=(rm-r) / math.tan(math.radians(dep))
        else :
            l_max=l
            
        #Logger.log('d', 'lg : ' + str(lg))
        #Logger.log('d', 'l_max : ' + str(l_max)) 
        
        verts = []
        if l_max<lg and l_max>0:
            nbv=18
            for i in range(0, rng):
                # Top
                verts.append([0, sup, 0])
                verts.append([r*math.cos((i+1)*ang), sup, r*math.sin((i+1)*ang)])
                verts.append([r*math.cos(i*ang), sup, r*math.sin(i*ang)])
                #Side 1a
                verts.append([r*math.cos(i*ang), sup, r*math.sin(i*ang)])
                verts.append([r*math.cos((i+1)*ang), sup, r*math.sin((i+1)*ang)])
                verts.append([rm*math.cos((i+1)*ang), -l_max, rm*math.sin((i+1)*ang)])
                #Side 1b
                verts.append([rm*math.cos((i+1)*ang), -l_max, rm*math.sin((i+1)*ang)])
                verts.append([rm*math.cos(i*ang), -l_max, rm*math.sin(i*ang)])
                verts.append([r*math.cos(i*ang), sup, r*math.sin(i*ang)])
                #Side 2a
                verts.append([rm*math.cos(i*ang), -l_max, rm*math.sin(i*ang)])
                verts.append([rm*math.cos((i+1)*ang), -l_max, rm*math.sin((i+1)*ang)])
                verts.append([rm*math.cos((i+1)*ang), l, rm*math.sin((i+1)*ang)])
                #Side 2b
                verts.append([rm*math.cos((i+1)*ang), l, rm*math.sin((i+1)*ang)])
                verts.append([rm*math.cos(i*ang), l, rm*math.sin(i*ang)])
                verts.append([rm*math.cos(i*ang), -l_max, rm*math.sin(i*ang)])
                #Bottom 
                verts.append([0, l, 0])
                verts.append([rm*math.cos(i*ang), l, rm*math.sin(i*ang)])
                verts.append([rm*math.cos((i+1)*ang), l, rm*math.sin((i+1)*ang)]) 
                
        else:
            nbv=12
            for i in range(0, rng):
                # Top
                verts.append([0, sup, 0])
                verts.append([r*math.cos((i+1)*ang), sup, r*math.sin((i+1)*ang)])
                verts.append([r*math.cos(i*ang), sup, r*math.sin(i*ang)])
                #Side 1a
                verts.append([r*math.cos(i*ang), sup, r*math.sin(i*ang)])
                verts.append([r*math.cos((i+1)*ang), sup, r*math.sin((i+1)*ang)])
                verts.append([r_inf*math.cos((i+1)*ang), l, r_inf*math.sin((i+1)*ang)])
                #Side 1b
                verts.append([r_inf*math.cos((i+1)*ang), l, r_inf*math.sin((i+1)*ang)])
                verts.append([r_inf*math.cos(i*ang), l, r_inf*math.sin(i*ang)])
                verts.append([r*math.cos(i*ang), sup, r*math.sin(i*ang)])
                #Bottom 
                verts.append([0, l, 0])
                verts.append([r_inf*math.cos(i*ang), l, r_inf*math.sin(i*ang)])
                verts.append([r_inf*math.cos((i+1)*ang), l, r_inf*math.sin((i+1)*ang)])
        
        mesh.setVertices(numpy.asarray(verts, dtype=numpy.float32))

        indices = []
        # for every angle increment nbv (12 or 18) Vertices
        tot = rng * nbv
        for i in range(0, tot, 3): # 
            indices.append([i, i+1, i+2])
        mesh.setIndices(numpy.asarray(indices, dtype=numpy.int32))

        mesh.calculateNormals()
        return mesh
 
   # Tube creation
    def _createTube(self, size, maxs, isize, nb , lg, sup ,dep):
        # Logger.log('d', 'isize : ' + str(isize)) 
        mesh = MeshBuilder()
        # Per-vertex normals require duplication of vertices
        r = size / 2
        ri = isize / 2
        rm = maxs / 2
        l = -lg
        rng = int(360 / nb)
        ang = math.radians(nb)
        r_inf=math.tan(math.radians(dep))*lg+r
        if rm>r and dep!=0:
            l_max=(rm-r) / math.tan(math.radians(dep))
        else :
            l_max=l
            
        verts = []
        if l_max<lg and l_max>0:
            nbv=30
            for i in range(0, rng):
                # Top
                verts.append([ri*math.cos(i*ang), sup, ri*math.sin(i*ang)])
                verts.append([r*math.cos((i+1)*ang), sup, r*math.sin((i+1)*ang)])
                verts.append([r*math.cos(i*ang), sup, r*math.sin(i*ang)])
                
                verts.append([ri*math.cos((i+1)*ang), sup, ri*math.sin((i+1)*ang)])
                verts.append([r*math.cos((i+1)*ang), sup, r*math.sin((i+1)*ang)])
                verts.append([ri*math.cos(i*ang), sup, ri*math.sin(i*ang)])

                #Side 1a
                verts.append([r*math.cos(i*ang), sup, r*math.sin(i*ang)])
                verts.append([r*math.cos((i+1)*ang), sup, r*math.sin((i+1)*ang)])
                verts.append([rm*math.cos((i+1)*ang), -l_max, rm*math.sin((i+1)*ang)])
                
                #Side 1b
                verts.append([rm*math.cos((i+1)*ang), -l_max, rm*math.sin((i+1)*ang)])
                verts.append([rm*math.cos(i*ang), -l_max, rm*math.sin(i*ang)])
                verts.append([r*math.cos(i*ang), sup, r*math.sin(i*ang)])
                
                #Side 2a
                verts.append([rm*math.cos(i*ang), -l_max, rm*math.sin(i*ang)])
                verts.append([rm*math.cos((i+1)*ang), -l_max, rm*math.sin((i+1)*ang)])
                verts.append([rm*math.cos((i+1)*ang), l, rm*math.sin((i+1)*ang)])
                
                #Side 2b
                verts.append([rm*math.cos((i+1)*ang), l, rm*math.sin((i+1)*ang)])
                verts.append([rm*math.cos(i*ang), l, rm*math.sin(i*ang)])
                verts.append([rm*math.cos(i*ang), -l_max, rm*math.sin(i*ang)])
                
                #Bottom 
                verts.append([ri*math.cos(i*ang), l, ri*math.sin(i*ang)])
                verts.append([rm*math.cos(i*ang), l, rm*math.sin(i*ang)])
                verts.append([rm*math.cos((i+1)*ang), l, rm*math.sin((i+1)*ang)]) 
                
                verts.append([ri*math.cos((i+1)*ang), l, ri*math.sin((i+1)*ang)])
                verts.append([ri*math.cos(i*ang), l, ri*math.sin(i*ang)])
                verts.append([rm*math.cos((i+1)*ang), l, rm*math.sin((i+1)*ang)]) 
                
                #Side Inta
                verts.append([ri*math.cos(i*ang), sup, ri*math.sin(i*ang)])
                verts.append([ri*math.cos((i+1)*ang), l, ri*math.sin((i+1)*ang)])
                verts.append([ri*math.cos((i+1)*ang), sup, ri*math.sin((i+1)*ang)])
                
                #Side Intb
                verts.append([ri*math.cos((i+1)*ang), l, ri*math.sin((i+1)*ang)])
                verts.append([ri*math.cos(i*ang), sup, ri*math.sin(i*ang)])
                verts.append([ri*math.cos(i*ang), l, ri*math.sin(i*ang)])
                
        else:
            nbv=24
            for i in range(0, rng):
                # Top
                verts.append([ri*math.cos(i*ang), sup, ri*math.sin(i*ang)])
                verts.append([r*math.cos((i+1)*ang), sup, r*math.sin((i+1)*ang)])
                verts.append([r*math.cos(i*ang), sup, r*math.sin(i*ang)])
                
                verts.append([ri*math.cos((i+1)*ang), sup, ri*math.sin((i+1)*ang)])
                verts.append([r*math.cos((i+1)*ang), sup, r*math.sin((i+1)*ang)])
                verts.append([ri*math.cos(i*ang), sup, ri*math.sin(i*ang)])
                
                #Side 1a
                verts.append([r*math.cos(i*ang), sup, r*math.sin(i*ang)])
                verts.append([r*math.cos((i+1)*ang), sup, r*math.sin((i+1)*ang)])
                verts.append([r_inf*math.cos((i+1)*ang), l, r_inf*math.sin((i+1)*ang)])
                
                #Side 1b
                verts.append([r_inf*math.cos((i+1)*ang), l, r_inf*math.sin((i+1)*ang)])
                verts.append([r_inf*math.cos(i*ang), l, r_inf*math.sin(i*ang)])
                verts.append([r*math.cos(i*ang), sup, r*math.sin(i*ang)])
                
                #Bottom 
                verts.append([ri*math.cos(i*ang), l, ri*math.sin(i*ang)])
                verts.append([r_inf*math.cos(i*ang), l, r_inf*math.sin(i*ang)])
                verts.append([r_inf*math.cos((i+1)*ang), l, r_inf*math.sin((i+1)*ang)]) 
                
                verts.append([ri*math.cos((i+1)*ang), l, ri*math.sin((i+1)*ang)])
                verts.append([ri*math.cos(i*ang), l, ri*math.sin(i*ang)])
                verts.append([r_inf*math.cos((i+1)*ang), l, r_inf*math.sin((i+1)*ang)]) 
                
                #Side Inta
                verts.append([ri*math.cos(i*ang), sup, ri*math.sin(i*ang)])
                verts.append([ri*math.cos((i+1)*ang), l, ri*math.sin((i+1)*ang)])
                verts.append([ri*math.cos((i+1)*ang), sup, ri*math.sin((i+1)*ang)])
                
                #Side Intb
                verts.append([ri*math.cos((i+1)*ang), l, ri*math.sin((i+1)*ang)])
                verts.append([ri*math.cos(i*ang), sup, ri*math.sin(i*ang)])
                verts.append([ri*math.cos(i*ang), l, ri*math.sin(i*ang)])

        mesh.setVertices(numpy.asarray(verts, dtype=numpy.float32))

        indices = []
        # for every angle increment ( 24  or 30 ) Vertices
        tot = rng * nbv
        for i in range(0, tot, 3): # 
            indices.append([i, i+1, i+2])
        mesh.setIndices(numpy.asarray(indices, dtype=numpy.int32))

        mesh.calculateNormals()
        return mesh
        
    # Custom Support Creation
    def _createCustom(self, size, maxs, pos1 , pos2, dep, ztop):
        mesh = MeshBuilder()
        # Init point
        Pt1 = Vector(pos1.x,pos1.z,pos1.y)
        Pt2 = Vector(pos2.x,pos2.z,pos2.y)

        V_Dir = Pt2 - Pt1

        # Calcul vecteur
        s = size / 2
        sm = maxs / 2
        l_a = pos1.y 
        s_infa=math.tan(math.radians(dep))*l_a+s
        l_b = pos2.y 
        s_infb=math.tan(math.radians(dep))*l_b+s
 
        if sm>s and dep!=0:
            l_max_a=(sm-s) / math.tan(math.radians(dep))
            l_max_b=(sm-s) / math.tan(math.radians(dep))
        else :
            l_max_a=l_a
            l_max_b=l_b
 
        Vtop = Vector(0,0,ztop)
        VZ = Vector(0,0,s)
        VZa = Vector(0,0,-l_a)
        VZb = Vector(0,0,-l_b)
        
        Norm=Vector.cross(V_Dir,VZ).normalized()
        Dec = Vector(Norm.x*s,Norm.y*s,Norm.z*s)
            
        if l_max_a<l_a and l_max_b<l_b and l_max_a>0 and l_max_b>0: 
            nbv=40
            
            Deca = Vector(Norm.x*sm,Norm.y*sm,Norm.z*sm)
            Decb = Vector(Norm.x*sm,Norm.y*sm,Norm.z*sm)

            VZam = Vector(0,0,-l_max_a)
            VZbm = Vector(0,0,-l_max_b)
        
            # X Z Y
            P_1t = Vtop+Dec
            P_2t = Vtop-Dec
            P_3t = V_Dir+Vtop+Dec
            P_4t = V_Dir+Vtop-Dec
 
            P_1m = VZam+Deca
            P_2m = VZam-Deca
            P_3m = VZbm+V_Dir+Decb
            P_4m = VZbm+V_Dir-Decb
            
            P_1i = VZa+Deca
            P_2i = VZa-Deca
            P_3i = VZb+V_Dir+Decb
            P_4i = VZb+V_Dir-Decb
             
            """
            1) Top
            2) Front
            3) Left
            4) Right
            5) Back 
            6) Front inf
            7) Left inf
            8) Right inf
            9) Back inf
            10) Bottom
            """
            verts = [ # 10 faces with 4 corners each
                [P_1t.x, P_1t.z, P_1t.y], [P_2t.x, P_2t.z, P_2t.y], [P_4t.x, P_4t.z, P_4t.y], [P_3t.x, P_3t.z, P_3t.y],              
                [P_1t.x, P_1t.z, P_1t.y], [P_3t.x, P_3t.z, P_3t.y], [P_3m.x, P_3m.z, P_3m.y], [P_1m.x, P_1m.z, P_1m.y],
                [P_2t.x, P_2t.z, P_2t.y], [P_1t.x, P_1t.z, P_1t.y], [P_1m.x, P_1m.z, P_1m.y], [P_2m.x, P_2m.z, P_2m.y],
                [P_3t.x, P_3t.z, P_3t.y], [P_4t.x, P_4t.z, P_4t.y], [P_4m.x, P_4m.z, P_4m.y], [P_3m.x, P_3m.z, P_3m.y],
                [P_4t.x, P_4t.z, P_4t.y], [P_2t.x, P_2t.z, P_2t.y], [P_2m.x, P_2m.z, P_2m.y], [P_4m.x, P_4m.z, P_4m.y],
                [P_1m.x, P_1m.z, P_1m.y], [P_3m.x, P_3m.z, P_3m.y], [P_3i.x, P_3i.z, P_3i.y], [P_1i.x, P_1i.z, P_1i.y],
                [P_2m.x, P_2m.z, P_2m.y], [P_1m.x, P_1m.z, P_1m.y], [P_1i.x, P_1i.z, P_1i.y], [P_2i.x, P_2i.z, P_2i.y],
                [P_3m.x, P_3m.z, P_3m.y], [P_4m.x, P_4m.z, P_4m.y], [P_4i.x, P_4i.z, P_4i.y], [P_3i.x, P_3i.z, P_3i.y],
                [P_4m.x, P_4m.z, P_4m.y], [P_2m.x, P_2m.z, P_2m.y], [P_2i.x, P_2i.z, P_2i.y], [P_4i.x, P_4i.z, P_4i.y],
                [P_1i.x, P_1i.z, P_1i.y], [P_2i.x, P_2i.z, P_2i.y], [P_4i.x, P_4i.z, P_4i.y], [P_3i.x, P_3i.z, P_3i.y]
            ]
            
        else:
            nbv=24

            Deca = Vector(Norm.x*s_infa,Norm.y*s_infa,Norm.z*s_infa)
            Decb = Vector(Norm.x*s_infb,Norm.y*s_infb,Norm.z*s_infb)

            # X Z Y
            P_1t = Vtop+Dec
            P_2t = Vtop-Dec
            P_3t = V_Dir+Vtop+Dec
            P_4t = V_Dir+Vtop-Dec
     
            P_1i = VZa+Deca
            P_2i = VZa-Deca
            P_3i = VZb+V_Dir+Decb
            P_4i = VZb+V_Dir-Decb
             
            """
            1) Top
            2) Front
            3) Left
            4) Right
            5) Back 
            6) Bottom
            """
            verts = [ # 6 faces with 4 corners each
                [P_1t.x, P_1t.z, P_1t.y], [P_2t.x, P_2t.z, P_2t.y], [P_4t.x, P_4t.z, P_4t.y], [P_3t.x, P_3t.z, P_3t.y],
                [P_1t.x, P_1t.z, P_1t.y], [P_3t.x, P_3t.z, P_3t.y], [P_3i.x, P_3i.z, P_3i.y], [P_1i.x, P_1i.z, P_1i.y],
                [P_2t.x, P_2t.z, P_2t.y], [P_1t.x, P_1t.z, P_1t.y], [P_1i.x, P_1i.z, P_1i.y], [P_2i.x, P_2i.z, P_2i.y],
                [P_3t.x, P_3t.z, P_3t.y], [P_4t.x, P_4t.z, P_4t.y], [P_4i.x, P_4i.z, P_4i.y], [P_3i.x, P_3i.z, P_3i.y],
                [P_4t.x, P_4t.z, P_4t.y], [P_2t.x, P_2t.z, P_2t.y], [P_2i.x, P_2i.z, P_2i.y], [P_4i.x, P_4i.z, P_4i.y],
                [P_1i.x, P_1i.z, P_1i.y], [P_2i.x, P_2i.z, P_2i.y], [P_4i.x, P_4i.z, P_4i.y], [P_3i.x, P_3i.z, P_3i.y]
            ]
        
        mesh.setVertices(numpy.asarray(verts, dtype=numpy.float32))

        indices = []
        for i in range(0, nbv, 4): # All 6 quads (12 triangles)
            indices.append([i, i+2, i+1])
            indices.append([i, i+3, i+2])
        mesh.setIndices(numpy.asarray(indices, dtype=numpy.int32))

        mesh.calculateNormals()
        return mesh

    def removeAllSupportMesh(self):
        if self._all_picked_node:
            for node in self._all_picked_node:
                node_stack = node.callDecoration("getStack")
                if node_stack.getProperty("support_mesh", "value") or  node_stack.getProperty("infill_mesh_order", "value") == 50 :
                    self._removeSupportMesh(node)
            self._all_picked_node = []
            self._SMsg = catalog.i18nc("@label", "Remove All") 
            self.propertyChanged.emit()
        else:        
            for node in DepthFirstIterator(self._application.getController().getScene().getRoot()):
                if node.callDecoration("isSliceable"):
                    # N_Name=node.getName()
                    # Logger.log('d', 'isSliceable : ' + str(N_Name))
                    node_stack=node.callDecoration("getStack")           
                    if node_stack:        
                        if node_stack.getProperty("support_mesh", "value") or  node_stack.getProperty("infill_mesh_order", "value") == 50 :
                            # N_Name=node.getName()
                            # Logger.log('d', 'support_mesh : ' + str(N_Name)) 
                            self._removeSupportMesh(node)
        
    def getSSize(self) -> float:
        """ 
            return: global _UseSize  in mm.
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

    def getMSize(self) -> float:
        """ 
            return: global _MaxSize  in mm.
        """           
        return self._MaxSize
  
    def setMSize(self, MSize: str) -> None:
        """
        param MSize: MaxSize in mm.
        """
 
        try:
            s_value = float(MSize)
        except ValueError:
            return

        if s_value < 0:
            return
        
        #Logger.log('d', 's_value : ' + str(s_value))        
        self._MaxSize = s_value
        self._preferences.setValue("customsupportcylinder/m_size", s_value)
        
    def getISize(self) -> float:
        """ 
            return: global _UseISize  in mm.
        """           
        return self._UseISize
  
    def setISize(self, ISize: str) -> None:
        """
        param ISize: interior Size in mm.
        """
 
        try:
            s_value = float(ISize)
        except ValueError:
            return

        if s_value <= 0:
            return
        
        #Logger.log('d', 's_value : ' + str(s_value))        
        self._UseISize = s_value
        self._preferences.setValue("customsupportcylinder/i_size", s_value)
        
    def getAAngle(self) -> float:
        """ 
            return: global _UseAngle  in °.
        """           
        return self._UseAngle
  
    def setAAngle(self, AAngle: str) -> None:
        """
        param AAngle: Angle in °.
        """
 
        try:
            s_value = float(AAngle)
        except ValueError:
            return

        if s_value < 0:
            return
        
        # Logger.log('d', 's_value : ' + str(s_value))        
        self._UseAngle = s_value
        self._preferences.setValue("customsupportcylinder/a_angle", s_value)
 
    def getSMsg(self) -> bool:
        """ 
            return: global _SMsg  as text paramater.
        """ 
        return self._SMsg
    
    def setSMsg(self, SMsg: str) -> None:
        """
        param SType: SMsg as text paramater.
        """
        self._SMsg = SMsg

        
    def getSType(self) -> bool:
        """ 
            return: global _SType  as text paramater.
        """ 
        return self._SType
    
    def setSType(self, SType: str) -> None:
        """
        param SType: SType as text paramater.
        """
        self._SType = SType
        # Logger.log('d', 'SType : ' + str(SType))   
        self._preferences.setValue("customsupportcylinder/t_type", SType)
 
    def getSubType(self) -> bool:
        """ 
            return: global _SubType  as text paramater.
        """ 
        # Logger.log('d', 'Set SubType : ' + str(self._SubType))  
        return self._SubType
    
    def setSubType(self, SubType: str) -> None:
        """
        param SubType: SubType as text paramater.
        """
        self._SubType = SubType
        # Logger.log('d', 'Get SubType : ' + str(SubType))   
        self._preferences.setValue("customsupportcylinder/s_type", SubType)

    def getAsModel(self) -> bool:
        """ 
            return: global _AsModel  as boolean.
        """ 
        return self._DefineAsModel
    
    def setAsModel(self, AsModel: bool) -> None:
        """
        param AsModel: as boolean.
        """
        self._DefineAsModel = AsModel
        self._preferences.setValue("customsupportcylinder/d_model", AsModel)
 
    def getYDirection(self) -> bool:
        """ 
            return: global _UseYDirection  as boolean.
        """ 
        return self._UseYDirection
    
    def setYDirection(self, YDirection: bool) -> None:
        """
        param YDirection: as boolean.
        """
        self._UseYDirection = YDirection
        self._preferences.setValue("customsupportcylinder/y_direction", YDirection)
 
    def getEHeights(self) -> bool:
        """ 
            return: global _EqualizeHeights  as boolean.
        """ 
        return self._EqualizeHeights
  
    def setEHeights(self, EHeights: bool) -> None:
        """
        param EHeights: as boolean.
        """
        self._EqualizeHeights = EHeights
        self._preferences.setValue("customsupportcylinder/e_heights", EHeights)
 
    def getSMain(self) -> bool:
        """ 
            return: global _ScaleMainDirection  as boolean.
        """ 
        return self._ScaleMainDirection
  
    def setSMain(self, SMain: bool) -> None:
        """
        param SMain: as boolean.
        """
        self._ScaleMainDirection = SMain
        self._preferences.setValue("customsupportcylinder/scale_main_direction", SMain)
        
    def getSOrient(self) -> bool:
        """ 
            return: global _OrientSupport  as boolean.
        """ 
        return self._OrientSupport
  
    def setSOrient(self, SOrient: bool) -> None:
        """
        param SOrient: as boolean.
        """
        self._OrientSupport = SOrient
        self._preferences.setValue("customsupportcylinder/s_orient", SOrient)
    
    def getSMirror(self) -> bool:
        """ 
            return: global _MirrorSupport  as boolean.
        """ 
        return self._MirrorSupport
  
    def setSMirror(self, SMirror: bool) -> None:
        """
        param SMirror: as boolean.
        """
        self._MirrorSupport = SMirror
        self._preferences.setValue("customsupportcylinder/s_mirror", SMirror)