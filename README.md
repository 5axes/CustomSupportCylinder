# Custom Supports Plugin for Cura

Cura plugin which enables you to add custom cylindrical and cubic supports. It was originaly based on the Support Eraser plugin code of Ultimaker B.V. but instead of creating a cube **"anti_overhang_mesh"**, this plugin offer you the possibility to define a custom sized **"support_mesh"** element.

Source code on Github : [https://github.com/Ultimaker/Cura/tree/master/plugins/SupportEraser](https://github.com/Ultimaker/Cura/tree/master/plugins/SupportEraser)

This plugin offer now much more possibilities :

- Possibility to define cylindrical / squarred support
- Possibility to define the support size
- Visualisation of the support on the total height
- Possibility to add angle to obtain conical support

The initial version was tested on Cura 4.5

![View plugin](./images/plugin.jpg)

## Installation

First, make sure your Cura version is 3.6 or newer. 

### Manual Install

Download & extract the repository as ZIP or clone it. Copy the files/plugins/CustomSupportCylinder directory to:
- on Windows: [Cura installation folder]/plugins/CustomSupportCylinder
- on Linux: ~/.local/share/cura/[YOUR CURA VERSION]/plugins/CustomSupportCylinder (e.g. ~/.local/share/cura/4.6/plugins/CustomSupportCylinder)
- on Mac: ~/Library/Application Support/cura/[YOUR CURA VERSION]/plugins/CustomSupportCylinder


### Automatic Install

This plugin is now avalaible in the Cura marketplace. So you can install it automaticaly from this place:
![Automatic Install](./images/MarketPlace.JPG)


## How to use

- Load a model in Cura and select it
- Click on the "Custom Supports Cylinder" button on the left toolbar
- Change de value for the support *Size* in numeric input field in the tool panel if necessary

- Change de value for the support *Angle* in numeric input field in the tool panel if necessary **(Version 1.0.03)**

![Numeric input field in the tool panel](./images/option_n.jpg)


- Click anywhere on the model to place support cylinder there
* The length of the support is automaticaly set from the pick point to the construction plate.

- **Clicking existing support cylinder deletes it**

- **Clicking existing support cylinder + Ctrl** switch automaticaly to the Translate Tool to modify the position of the support.


- Before to slice your model, uncheck the "Generate Support" checkbox in the right panel **(if you want to use ONLY custom supports)**

With the CheckBox 'Create cube', it's possible to switch the geometry between a cylinder or a cubic support

>Note: it's easier to add/remove supports when you are in "Solid View" mode

## Modifications

- Version 1.03 : Possibility to define conical support

![Conical Support](./images/conical_support.jpg)
	
