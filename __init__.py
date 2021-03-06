# Copyright (c) 2020 5axes
# Based on the SupportBlocker plugin by Ultimaker B.V., and licensed under LGPLv3 or higher.

from . import CustomSupportsCylinder

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("cura")

def getMetaData():
    return {
        "tool": {
            "name": i18n_catalog.i18nc("@label", "Custom Supports Cylinder"),
            "description": i18n_catalog.i18nc("@info:tooltip", "Add 5 types of custom support"),
            "icon": "tool_icon.svg",
            "tool_panel": "CustomSupport.qml",
            "weight": 8
        }
    }

def register(app):
    return { "tool": CustomSupportsCylinder.CustomSupportsCylinder() }
