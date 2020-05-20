// Copyright (c) 2016 Ultimaker B.V.
// 
// proterties values
//   "SSize"   : Support Size in mm
//   "LockCube" : boolean Cubre/Cylinder Creation  
//

import QtQuick 2.2
import QtQuick.Controls 1.2

import UM 1.1 as UM

Item
{
    id: base
    width: childrenRect.width
    height: childrenRect.height
    UM.I18nCatalog { id: catalog; name: "cura"}


    Grid
    {
        id: textfields;

        anchors.leftMargin: UM.Theme.getSize("default_margin").width;
        anchors.top: parent.top;

        columns: 2;
        flow: Grid.TopToBottom;
        spacing: Math.round(UM.Theme.getSize("default_margin").width / 2);

        Label
        {
            height: UM.Theme.getSize("setting_control").height;
            text: "Size";
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
    }

    CheckBox
    {
        id: lockTypeCheckbox
        anchors.top: textfields.bottom
        anchors.topMargin: UM.Theme.getSize("default_margin").height;
        anchors.left: textfields.left
        anchors.leftMargin: UM.Theme.getSize("default_margin").width

        text: catalog.i18nc("@option:check","Create Cube");
        style: UM.Theme.styles.partially_checkbox;

        checked: UM.ActiveTool.properties.getValue("LockCube")
        onClicked: UM.ActiveTool.setProperty("LockCube", checked)
    }

}
