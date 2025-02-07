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

class AttributeReorderTool:
    def __init__(self):
        self.window = "AttributeReorderWindow"
        self.controller = None
        self.custom_attrs = []
        self.attr_list_ui = None
        
        # Build the UI
        self.create_ui()

    def create_ui(self):
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window)
        
        self.window = cmds.window(self.window, title="Attribute Reorder Tool", widthHeight=(300, 400))
        cmds.columnLayout(adjustableColumn=True)

        # Add a button to select the current controller
        cmds.button(label="Select Controller", command=self.select_controller)
        self.controller_label = cmds.text(label="Controller: None", align="left")
        
        # List custom attributes
        self.attr_list_ui = cmds.textScrollList(numberOfRows=8, allowMultiSelection=False, height=200)
        
        # Buttons to move attributes
        cmds.button(label="Refresh Attributes", command=self.refresh_attributes)
        cmds.button(label="Move Up", command=self.move_up)
        cmds.button(label="Move Down", command=self.move_down)
        cmds.button(label="Apply Reordering", command=self.apply_reorder)

        cmds.showWindow(self.window)

    def select_controller(self, *args):
        # Get the selected controller from the scene
        selection = cmds.ls(sl=True)
        if selection:
            self.controller = selection[0]
            cmds.text(self.controller_label, edit=True, label=f"Controller: {self.controller}")
            self.refresh_attributes()
        else:
            cmds.warning("No controller selected.")
            cmds.text(self.controller_label, edit=True, label="Controller: None")

    def refresh_attributes(self, *args):
        # Clear current attribute list
        cmds.textScrollList(self.attr_list_ui, edit=True, removeAll=True)
        
        if self.controller:
            # Filter out default attributes to get only custom attributes
            all_attrs = cmds.listAttr(self.controller, userDefined=True) or []
            self.custom_attrs = all_attrs

            if self.custom_attrs:
                for attr in self.custom_attrs:
                    cmds.textScrollList(self.attr_list_ui, edit=True, append=attr)
            else:
                cmds.warning(f"No custom attributes found on {self.controller}.")
        else:
            cmds.warning("No controller selected.")

    def move_up(self, *args):
        selected_attr = cmds.textScrollList(self.attr_list_ui, query=True, selectIndexedItem=True)
        if selected_attr:
            index = selected_attr[0] - 1
            if index > 0:
                # Swap attributes in the custom_attrs list
                self.custom_attrs[index - 1], self.custom_attrs[index] = self.custom_attrs[index], self.custom_attrs[index - 1]
                self.refresh_attributes_ui()

    def move_down(self, *args):
        selected_attr = cmds.textScrollList(self.attr_list_ui, query=True, selectIndexedItem=True)
        if selected_attr:
            index = selected_attr[0] - 1
            if index < len(self.custom_attrs) - 1:
                self.custom_attrs[index + 1], self.custom_attrs[index] = self.custom_attrs[index], self.custom_attrs[index + 1]
                self.refresh_attributes_ui()

    def refresh_attributes_ui(self):
        cmds.textScrollList(self.attr_list_ui, edit=True, removeAll=True)
        for attr in self.custom_attrs:
            cmds.textScrollList(self.attr_list_ui, edit=True, append=attr)

    def apply_reorder(self, *args):
        if self.controller:
            for attr in self.custom_attrs:
                attr_long_name = f"{self.controller}.{attr}"

                # Check if the attribute is a proxy (connected from another attribute)
                inputs = cmds.listConnections(attr_long_name, plugs=True, source=True, destination=False) or []

                # If it's a proxy attribute, capture the input connection
                proxy_source = inputs[0] if inputs else None

                # Gather attribute properties before deletion
                attr_value = cmds.getAttr(attr_long_name)
                attr_type = cmds.attributeQuery(attr, node=self.controller, attributeType=True)
                min_value = cmds.attributeQuery(attr, node=self.controller, minimum=True) if cmds.attributeQuery(attr, node=self.controller, minExists=True) else None
                max_value = cmds.attributeQuery(attr, node=self.controller, maximum=True) if cmds.attributeQuery(attr, node=self.controller, maxExists=True) else None
                enum_options = cmds.attributeQuery(attr, node=self.controller, listEnum=True)[0] if attr_type == 'enum' else None
                is_keyable = cmds.getAttr(attr_long_name, keyable=True)
                is_locked = cmds.getAttr(attr_long_name, lock=True)
                outputs = cmds.listConnections(attr_long_name, plugs=True, source=False, destination=True) or []

                # Delete the attribute
                cmds.deleteAttr(attr_long_name)

                # Recreate the attribute with the same settings
                if proxy_source:
                    # Recreate as a proxy attribute
                    cmds.addAttr(self.controller, longName=attr, attributeType='proxy', proxy=proxy_source)
                    cmds.warning(f"Recreated proxy attribute {attr} with connection to {proxy_source}")
                else:
                    if attr_type == 'double':
                        cmds.addAttr(self.controller, longName=attr, attributeType='double')
                        if min_value is not None:
                            cmds.addAttr(f"{self.controller}.{attr}", edit=True, minValue=min_value[0])
                        if max_value is not None:
                            cmds.addAttr(f"{self.controller}.{attr}", edit=True, maxValue=max_value[0])
                    elif attr_type == 'enum':
                        cmds.addAttr(self.controller, longName=attr, attributeType='enum', enumName=enum_options)

                    # Restore attribute value and other settings
                    cmds.setAttr(f"{self.controller}.{attr}", attr_value)
                    cmds.setAttr(f"{self.controller}.{attr}", lock=is_locked)
                    cmds.setAttr(f"{self.controller}.{attr}", keyable=is_keyable)

                # Restore output connections
                for output_conn in outputs:
                    cmds.connectAttr(f"{self.controller}.{attr}", output_conn)

            cmds.warning("Attributes reordered successfully.")
        else:
            cmds.warning("No controller selected.")

# Initialize the tool
AttributeReorderTool()
