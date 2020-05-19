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
    UM.I18nCatalog { id: catalog; name: "uranium"}

    property string sizeText
	property bool lockType: false

    //Rounds a floating point number to 4 decimals. This prevents floating
    //point rounding errors.
    //
    //input:    The number to round.
    //decimals: The number of decimals (digits after the radix) to round to.
    //return:   The rounded number.
    function roundFloat(input, decimals)
    {
        //First convert to fixed-point notation to round the number to 4 decimals and not introduce new floating point errors.
        //Then convert to a string (is implicit). The fixed-point notation will be something like "3.200".
        //Then remove any trailing zeroes and the radix.
        var output = "";
        if (input !== undefined)
        {
            output = input.toFixed(decimals).replace(/\.?0*$/, ""); //Match on periods, if any ( \.? ), followed by any number of zeros ( 0* ), then the end of string ( $ ).
        }
        if (output == "-0")
        {
            output = "0";
        }
        return output;
    }

    function selectTextInTextfield(selected_item){
        selected_item.selectAll()
        selected_item.focus = true
    }

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
            id: xTextField
            width: UM.Theme.getSize("setting_control").width;
            height: UM.Theme.getSize("setting_control").height;
            property string unit: "mm";
            style: UM.Theme.styles.text_field;
            text: sizeText
            validator: DoubleValidator
            {
                decimals: 3
                locale: "en_US"
            }

            onEditingFinished:
            {
                var modified_text = text.replace(",", ".") // User convenience. We use dots for decimal values
                UM.ActiveTool.setProperty("SSize", modified_text);
            }
            // Keys.onBacktabPressed: selectTextInTextfield(zTextField)
            // Keys.onTabPressed: selectTextInTextfield(yTextField)
        }
    }

    CheckBox
    {
        property var checkbox_state: 0; // 

        // temporary property, which is used to recalculate checkbox state and keeps reference of the
        // binging object. If the binding object changes then checkBox state will be updated.
        property var temp_checkBox_value:{

            checkbox_state = getCheckBoxState()

            // returning the lockType the propery will keep reference, for updating
            return base.lockType
        }

        function getCheckBoxState(){
            if (base.lockType == true){
                lockTypeCheckbox.checked = true
                return 1;
            }
            else{
                lockTypeCheckbox.checked = false
                return 0;
            }
        }


        id: lockTypeCheckbox
        anchors.top: textfields.bottom
        anchors.topMargin: UM.Theme.getSize("default_margin").height;
        anchors.left: textfields.left
        anchors.leftMargin: UM.Theme.getSize("default_margin").width

        text: catalog.i18nc("@option:check","Create Cube");
        style: UM.Theme.styles.partially_checkbox;

        onClicked: {

            UM.ActiveTool.setProperty("LockCube", lockTypeCheckbox.checked);


            // After clicking the base.lockType is not refreshed, fot this reason manually update the state
            // Set zero because only 2 will show partially icon in checkbox
            checkbox_state = 0;
        }
    }
	
    // We have to use indirect bindings, as the values can be changed from the outside, which could cause breaks
    // (for instance, a value would be set, but it would be impossible to change it).
    // Doing it indirectly does not break these.
    Binding
    {
        target: base
        property: "sizeText"
        value: base.roundFloat(UM.ActiveTool.properties.getValue("SSize"), 4)
    }
	
    Binding
    {
        target: base
        property: "lockType"
        value: UM.ActiveTool.properties.getValue("LockCube")
    }

}