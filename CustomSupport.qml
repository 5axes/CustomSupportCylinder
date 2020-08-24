//-----------------------------------------------------------------------------
// Copyright (c) 2020 5@xes
// 
// proterties values
//   "SSize"       : Support Size in mm
//   "AAngle"      : Support Angle in °
//   "SType"       : Support Type ( Cylinder/Cube/Custom ) 
//-----------------------------------------------------------------------------

import QtQuick 2.2
import QtQuick.Controls 1.2

import UM 1.1 as UM

Item
{
    id: base
    width: childrenRect.width
    height: childrenRect.height
    UM.I18nCatalog { id: catalog; name: "cura"}

    property var currentSType: UM.ActiveTool.properties.getValue("SType");

    function setSType(type)
    {
        // set checked state of mesh type buttons
		cylinderButton.checked = type === 'cylinder';
        cubeButton.checked = type === 'cube';  
		customButton.checked = type === 'custom';
        UM.ActiveTool.setProperty("SType", type);
    }
	
    Column
    {
        id: sTypeItems
        anchors.top: parent.top;
        anchors.left: parent.left;
        spacing: UM.Theme.getSize("default_margin").height;

        Row // Mesh type buttons
        {
            id: sTypeButtons
            spacing: UM.Theme.getSize("default_margin").width

            Button
            {
                id: cylinderButton;
                text: catalog.i18nc("@label", "Cylinder");
                iconSource: "type_cylinder.svg";
                property bool needBorder: true;
                checkable:true;
                onClicked: setSType('cylinder');
                style: UM.Theme.styles.tool_button;
                checked: UM.ActiveTool.properties.getValue("SType") === 'cylinder';
                z: 3; // Profondeur
            }
			
            Button
            {
                id: cubeButton;
                text: catalog.i18nc("@label", "Cube");
                iconSource: "type_cube.svg";
                property bool needBorder: true;
                checkable: true;
                onClicked: setSType('cube');
                style: UM.Theme.styles.tool_button;
                checked: UM.ActiveTool.properties.getValue("SType") === 'cube';
                z: 2; // Profondeur
            }

            Button
            {
                id: customButton;
                text: catalog.i18nc("@label", "Custom");
                iconSource: "type_custom.svg";
                property bool needBorder: true;
                checkable:true;
                onClicked: setSType('custom');
                style: UM.Theme.styles.tool_button;
                checked: UM.ActiveTool.properties.getValue("SType") === 'custom';
                z: 1; // Profondeur
            }
        }
    }

    Grid
    {
        id: textfields;
        anchors.leftMargin: UM.Theme.getSize("default_margin").width;
        anchors.top: sTypeItems.bottom;
		anchors.topMargin: UM.Theme.getSize("default_margin").height;

        columns: 2;
        flow: Grid.TopToBottom;
        spacing: Math.round(UM.Theme.getSize("default_margin").width / 2);

        Label
        {
            height: UM.Theme.getSize("setting_control").height;
            text: catalog.i18nc("@label","Size");
            font: UM.Theme.getFont("default");
            color: UM.Theme.getColor("text");
            verticalAlignment: Text.AlignVCenter;
            renderType: Text.NativeRendering
            width: Math.ceil(contentWidth) //Make sure that the grid cells have an integer width.
        }

        Label
        {
            height: UM.Theme.getSize("setting_control").height;
            text: catalog.i18nc("@label","Angle");
            font: UM.Theme.getFont("default");
            color: UM.Theme.getColor("text");
            verticalAlignment: Text.AlignVCenter;
            renderType: Text.NativeRendering
            width: Math.ceil(contentWidth) //Make sure that the grid cells have an integer width.
        }
		
        TextField
        {
            id: sizeTextField
            width: UM.Theme.getSize("setting_control").width;
            height: UM.Theme.getSize("setting_control").height;
            property string unit: "mm";
            style: UM.Theme.styles.text_field;
            text: UM.ActiveTool.properties.getValue("SSize")
            validator: DoubleValidator
            {
                decimals: 2
                bottom: 0.1
                locale: "en_US"
            }

            onEditingFinished:
            {
                var modified_text = text.replace(",", ".") // User convenience. We use dots for decimal values
                UM.ActiveTool.setProperty("SSize", modified_text);
            }
        }
		
		TextField
        {
            id: angleTextField
            width: UM.Theme.getSize("setting_control").width;
            height: UM.Theme.getSize("setting_control").height;
            property string unit: "°";
            style: UM.Theme.styles.text_field;
            text: UM.ActiveTool.properties.getValue("AAngle")
            validator: DoubleValidator
            {
                decimals: 0
                bottom: 0
                locale: "en_US"
            }

            onEditingFinished:
            {
                var modified_angle_text = text.replace(",", ".") // User convenience. We use dots for decimal values
                UM.ActiveTool.setProperty("AAngle", modified_angle_text);
            }
        }
    }

}
