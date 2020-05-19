// Copyright (c) 2016 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

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
            text: "Diameter";
            font: UM.Theme.getFont("default");
            color: UM.Theme.getColor("text");
            verticalAlignment: Text.AlignVCenter;
            renderType: Text.NativeRendering
            width: Math.ceil(contentWidth) //Make sure that the grid cells have an integer width.
        }

        TextField
        {
            id: diameterTextField
            width: UM.Theme.getSize("setting_control").width;
            height: UM.Theme.getSize("setting_control").height;
            property string unit: "mm";
            style: UM.Theme.styles.text_field;
            text: UM.ActiveTool.properties.getValue("Diameter")
            validator: DoubleValidator
            {
                decimals: 2
                bottom: 0.1
                locale: "en_US"
            }

            onEditingFinished:
            {
                var modified_text = text.replace(",", ".") // User convenience. We use dots for decimal values
                UM.ActiveTool.setProperty("Diameter", modified_text);
            }
        }
    }
}