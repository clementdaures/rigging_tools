'''
MIT License

Copyright (c) 2024 Clement Daures

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import maya.cmds as cmds

# Global list to store selected attributes and target controllers
selection_list = []
target_controller_list = []

# Global variable to control whether confirmation dialogs are shown
show_dialogs = True

def add_to_selection_list():
    """
    Add the currently selected attributes from the channel box to the selection list.
    """
    selected_objects = cmds.ls(selection=True, long=True) or []
    channel_box = 'mainChannelBox'
    selected_attributes = []

    if selected_objects:
        for obj in selected_objects:
            attrs = cmds.channelBox(channel_box, query=True, selectedMainAttributes=True) or []
            if attrs:
                for attr in attrs:
                    full_attr = f"{obj}.{attr}"
                    selected_attributes.append(full_attr)

    if not selected_attributes:
        cmds.warning("No attributes selected to add to the list.")
        return

    for item in selected_attributes:
        if item not in selection_list:
            selection_list.append(item)

    update_selection_list_ui()

def remove_from_selection_list(item_to_remove):
    if item_to_remove in selection_list:
        selection_list.remove(item_to_remove)
    update_selection_list_ui()

def clear_selection_list():
    global selection_list
    selection_list = []
    update_selection_list_ui()

def update_selection_list_ui():
    if cmds.textScrollList("selectionList", exists=True):
        cmds.textScrollList("selectionList", edit=True, removeAll=True)
        cmds.textScrollList("selectionList", edit=True, append=selection_list)

def query_attribute():
    selected_items = cmds.textScrollList("selectionList", query=True, selectItem=True)

    if not selected_items:
        cmds.warning("No item selected from the list.")
        return

    for selected_item in selected_items:
        if '.' in selected_item:
            obj, attr = selected_item.split('.')
            if cmds.objExists(obj) and cmds.attributeQuery(attr, node=obj, exists=True):
                attr_value = cmds.getAttr(f"{obj}.{attr}")
                if show_dialogs:
                    cmds.confirmDialog(title="Attribute Value", message=f"Value of {selected_item}: {attr_value}")
            else:
                cmds.warning(f"Attribute '{attr}' does not exist on '{obj}'")
        else:
            cmds.warning(f"'{selected_item}' is not an attribute. Select an attribute entry (e.g., 'ctrl.ikfk').")

# Function to create a proxy attribute on multiple target controllers
def create_proxy_attribute():
    selected_items = cmds.textScrollList("selectionList", query=True, selectItem=True)
    target_controllers = cmds.textScrollList("targetList", query=True, selectItem=True)

    if not selected_items or not target_controllers:
        cmds.warning("No item selected or no target controllers specified.")
        return

    for target_controller in target_controllers:
        for selected_item in selected_items:
            if '.' in selected_item:
                obj, attr = selected_item.split('.')
                proxy_attr_name = attr
                cmds.addAttr(target_controller, longName=proxy_attr_name, proxy=f"{obj}.{attr}")
                if show_dialogs:
                    cmds.confirmDialog(title="Proxy Attribute", message=f"Created proxy '{proxy_attr_name}' on {target_controller}.")

# Function to copy the value of an attribute to multiple controllers
def copy_attribute_value():
    selected_items = cmds.textScrollList("selectionList", query=True, selectItem=True)
    target_controllers = cmds.textScrollList("targetList", query=True, selectItem=True)

    if not selected_items or not target_controllers:
        cmds.warning("No item selected or no target controllers specified.")
        return

    for target_controller in target_controllers:
        for selected_item in selected_items:
            if '.' in selected_item:
                obj, attr = selected_item.split('.')
                if cmds.objExists(obj) and cmds.attributeQuery(attr, node=obj, exists=True):
                    attr_value = cmds.getAttr(f"{obj}.{attr}")
                    if not cmds.attributeQuery(attr, node=target_controller, exists=True):
                        cmds.addAttr(target_controller, longName=attr, attributeType="double", keyable=True)
                    cmds.setAttr(f"{target_controller}.{attr}", attr_value)
                    if show_dialogs:
                        cmds.confirmDialog(title="Copy Attribute", message=f"Copied value of '{attr}' to {target_controller}.")

# Function to link an attribute to multiple controllers
def link_attribute():
    selected_items = cmds.textScrollList("selectionList", query=True, selectItem=True)
    target_controllers = cmds.textScrollList("targetList", query=True, selectItem=True)

    if not selected_items or not target_controllers:
        cmds.warning("No item selected or no target controllers specified.")
        return

    for target_controller in target_controllers:
        for selected_item in selected_items:
            if '.' in selected_item:
                obj, attr = selected_item.split('.')
                if not cmds.attributeQuery(attr, node=target_controller, exists=True):
                    cmds.addAttr(target_controller, longName=attr, attributeType="double", keyable=True)
                cmds.connectAttr(f"{obj}.{attr}", f"{target_controller}.{attr}")
                if show_dialogs:
                    cmds.confirmDialog(title="Link Attribute", message=f"Linked '{attr}' to {target_controller}.")

def load_target_controllers():
    selected_objects = cmds.ls(selection=True)
    if not selected_objects:
        cmds.warning("No objects selected to load as target controllers.")
        return

    for obj in selected_objects:
        if obj not in target_controller_list:
            target_controller_list.append(obj)

    update_target_list_ui()

def remove_from_target_list(item_to_remove):
    if item_to_remove in target_controller_list:
        target_controller_list.remove(item_to_remove)
    update_target_list_ui()

def clear_target_list():
    global target_controller_list
    target_controller_list = []
    update_target_list_ui()

def update_target_list_ui():
    if cmds.textScrollList("targetList", exists=True):
        cmds.textScrollList("targetList", edit=True, removeAll=True)
        cmds.textScrollList("targetList", edit=True, append=target_controller_list)

def toggle_dialog_state():
    global show_dialogs
    show_dialogs = cmds.checkBox("dialogToggle", query=True, value=True)

def manipulation_tool_ui():
    """
    Create a UI for managing the selection list and attribute manipulations.
    """
    if cmds.window("selectionListWindow", exists=True):
        cmds.deleteUI("selectionListWindow", window=True)
    
    window = cmds.window("selectionListWindow", title="Selection List", widthHeight=(400, 500))
    
    cmds.columnLayout(adjustableColumn=True)
    
    cmds.button(label="Add Selected Attributes to List", command=lambda x: add_to_selection_list())
    
    # Allow multi-selection in the textScrollList for attributes
    cmds.textScrollList("selectionList", allowMultiSelection=True, height=200)

    cmds.button(label="Query Selected Attribute(s)", command=lambda x: query_attribute())
    cmds.button(label="Remove Selected from List", command=lambda x: remove_selected_from_list())
    cmds.button(label="Clear List", command=lambda x: clear_selection_list())
    
    cmds.separator(height=10)
    
    # Target controller list UI
    cmds.text(label="Target Controllers:")
    cmds.textScrollList("targetList", allowMultiSelection=True, height=150)
    
    cmds.button(label="Load Target Controllers", command=lambda x: load_target_controllers())
    cmds.button(label="Remove Selected from Target List", command=lambda x: remove_from_target_list(cmds.textScrollList("targetList", query=True, selectItem=True)))
    cmds.button(label="Clear Target List", command=lambda x: clear_target_list())

    cmds.separator(height=20)

    # Checkbox to toggle confirmation dialogs
    cmds.checkBox("dialogToggle", label="Show Confirmation Dialogs", value=True, changeCommand=lambda x: toggle_dialog_state())
    
    cmds.separator(height=10)

    # Buttons for attribute manipulations
    cmds.button(label="Create Proxy of Selected Attribute(s)", command=lambda x: create_proxy_attribute())
    cmds.button(label="Copy Selected Attribute(s) to Target", command=lambda x: copy_attribute_value())
    cmds.button(label="Link Selected Attribute(s) to Target", command=lambda x: link_attribute())

    cmds.showWindow(window)

def remove_selected_from_list():
    selected_items = cmds.textScrollList("selectionList", query=True, selectItem=True)
    if selected_items:
        for item in selected_items:
            remove_from_selection_list(item)

# Create the UI to manage selection list and attribute manipulations
manipulation_tool_ui()
