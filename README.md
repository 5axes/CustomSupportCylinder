# Custom Supports plugin for Cura

Cura plugin which enables you to add custom supports!
It is based on the CustomSupports plugin.
The initial version was tested on Cura 4.5


Installation
----
First, make sure your Cura version is 3.3 or newer
You can only add manualy the plugin

**Automatic Install**
Go to the releases page, and download the correct file for your Cura version - the .curaplugin file for Cura 3.3.x and the .curapackage file for Cura 3.4 and newer.
Start Cura, and drag & drop the file on the main window. Restart Cura, and you are done!

**Manual Install**
Download & extract the repository as ZIP or clone it. Copy the files/plugins/CustomSupports directory to:
- on Windows: [Cura installation folder]/plugins/CustomSupports
- on Linux: ~/.local/share/cura/[YOUR CURA VERSION]/plugins/CustomSupports (e.g. ~/.local/share/cura/3.4/plugins/CustomSupports)
- on Mac: ~/Library/Application Support/cura/[YOUR CURA VERSION]/plugins/CustomSupports


How to use
----
- Load some model in Cura and select it
- Uncheck the "Generate Support" checkbox in the right panel (if you want to use ONLY custom supports)
- click on the "Custom Supports cylinder" button on the left toolbar
- click anywhere on the model to place support cylinder there
- clicking existing support cylinder deletes it
Note: it's easier to add/remove supports when you are in "Solid View" mode
	
