# Custom Supports plugin for Cura

Cura plugin which enables you to add custom cylindical supports. It is based on the CustomSupports plugin version of Krasimir Stenanov Custom Supports plugin : http://lokspace.eu/cura-custom-supports-plugin/
Source code on Github : https://github.com/lokster/cura-custom-supports/tree/master/CustomSupports

The initial version was tested on Cura 4.5

Installation
----
First, make sure your Cura version is 3.3 or newer. 

**Manual Install**
Download & extract the repository as ZIP or clone it. Copy the files/plugins/CustomSupports directory to:
- on Windows: [Cura installation folder]/plugins/CustomSupports
- on Linux: ~/.local/share/cura/[YOUR CURA VERSION]/plugins/CustomSupports (e.g. ~/.local/share/cura/3.4/plugins/CustomSupports)
- on Mac: ~/Library/Application Support/cura/[YOUR CURA VERSION]/plugins/CustomSupports


How to use
----
- Load some model in Cura and select it
- Uncheck the "Generate Support" checkbox in the right panel (if you want to use ONLY custom supports)
- click on the "Custom Supports Cylinder" button on the left toolbar
- click anywhere on the model to place support cylinder there
- clicking existing support cylinder deletes it

* The length of the support is automaticaly set from the pick point to the construction plate of the printer.
* The diameter is define by using the value of support_tower_diameter (Support as Tower diameter) as Cylinder diameter 

Note: it's easier to add/remove supports when you are in "Solid View" mode
	
