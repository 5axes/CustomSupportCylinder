# Copyright (c) 2022 5@xes
# Initialy Based on the SupportBlocker plugin by Ultimaker B.V., and licensed under LGPLv3 or higher.

VERSION_QT5 = False
try:
    from PyQt6.QtCore import QT_VERSION_STR
except ImportError:
    VERSION_QT5 = True
    
from . import CustomSupportsCylinder

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("customsupport")

def getMetaData():
    if not VERSION_QT5:
        QmlFile="qml_qt6/CustomSupport.qml"
    else:
        QmlFile="qml_qt5/CustomSupport.qml"

    return {
        "tool": {
            "name": i18n_catalog.i18nc("@label", "Custom Supports Cylinder"),
            "description": i18n_catalog.i18nc("@info:tooltip", "Add 6 types of custom support"),
            "icon": "tool_icon.svg",
            "tool_panel": QmlFile,
            "weight": 8
        }
    }

def register(app):
    return { "tool": CustomSupportsCylinder.CustomSupportsCylinder() }
