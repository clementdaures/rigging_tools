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

# Main function to launch the UI
def state_tool_ui():
    if cmds.window('setAttrWindow', exists=True):
        cmds.deleteUI('setAttrWindow', window=True)

    # Create the window
    window = cmds.window('setAttrWindow', title="Set Attributes", sizeable=False)

    # Main layout
    cmds.columnLayout(adjustableColumn=True)

    # Native Maya transform attributes section
    cmds.frameLayout(label="Maya Native Transform Attributes", collapsable=True, marginHeight=10)
    cmds.text(label="Select which native transform attributes to lock/unlock or make keyable/unkeyable", align="center")

    # Checkboxes for transforms
    cmds.rowColumnLayout(numberOfColumns=5, columnWidth=[(1, 70), (2, 70), (3, 70), (4, 70), (5, 70)])
    native_tx_cb = cmds.checkBox(label="Translate", value=True)
    native_rx_cb = cmds.checkBox(label="Rotate")
    native_sx_cb = cmds.checkBox(label="Scale")
    native_vis_cb = cmds.checkBox(label="Visibility")
    native_all_cb = cmds.checkBox(label="All", value=False)

    cmds.setParent('..')  # Return to parent layout

    # Buttons for lock/unlock operations
    cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 160), (2, 160)])
    cmds.button(label="Lock and Hide", command=lambda _: set_native_attributes(0, native_tx_cb, native_rx_cb, native_sx_cb, native_vis_cb, native_all_cb))
    cmds.button(label="Unlock", command=lambda _: set_native_attributes(1, native_tx_cb, native_rx_cb, native_sx_cb, native_vis_cb, native_all_cb))

    cmds.setParent('..')

    cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 160), (2, 160)])
    cmds.button(label="Make Keyable", command=lambda _: set_native_keyable(True, native_tx_cb, native_rx_cb, native_sx_cb, native_vis_cb, native_all_cb))
    cmds.button(label="Make Unkeyable", command=lambda _: set_native_keyable(False, native_tx_cb, native_rx_cb, native_sx_cb, native_vis_cb, native_all_cb))

    cmds.setParent('..')
    cmds.setParent('..')  # Return to the main column layout

    # Custom user attributes section
    cmds.frameLayout(label="User Attributes", collapsable=True, marginHeight=10)
    cmds.text(label="Select the user attributes in the channel box to lock/unlock or make keyable/unkeyable", align="center")

    # Buttons for user-defined attributes
    cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 160), (2, 160)])
    cmds.button(label="Lock User Attributes", command=lambda _: lock_user_attributes(lock=True))
    cmds.button(label="Unlock User Attributes", command=lambda _: lock_user_attributes(lock=False))

    cmds.setParent('..')

    cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 160), (2, 160)])
    cmds.button(label="User Attributes Keyable", command=lambda _: keyable_user_attributes(True))
    cmds.button(label="User Attributes Unkeyable", command=lambda _: keyable_user_attributes(False))

    # Show the window
    cmds.showWindow(window)


# Function to get the selected attributes from the channel box
def get_selected_channel_box_attrs():
    selected_objects = cmds.ls(selection=True, long=True)
    if not selected_objects:
        cmds.warning("No objects selected!")
        return []

    channel_box = 'mainChannelBox'
    selected_attributes = []

    for obj in selected_objects:
        attrs = cmds.channelBox(channel_box, query=True, selectedMainAttributes=True) or []
        for attr in attrs:
            selected_attributes.append(f"{obj}.{attr}")

    if not selected_attributes:
        cmds.warning("No attributes selected in the channel box!")

    return selected_attributes


# Function to lock or unlock user attributes selected in the channel box
def lock_user_attributes(lock=True):
    """
    Lock or unlock user-defined attributes selected in the channel box.

    Args:
        lock (bool): If True, lock the attributes, otherwise unlock.
    """
    selected_attrs = get_selected_channel_box_attrs()

    if not selected_attrs:
        return

    for attr in selected_attrs:
        if cmds.objExists(attr):
            cmds.setAttr(attr, lock=lock)


# Function to make user attributes keyable or unkeyable (and keep them visible in the channel box)
def keyable_user_attributes(is_keyable=True):
    """
    Set user-defined attributes selected in the channel box as keyable or unkeyable but visible in the channel box.

    Args:
        is_keyable (bool): If True, make keyable; if False, make unkeyable but visible in the channel box.
    """
    selected_attrs = get_selected_channel_box_attrs()

    if not selected_attrs:
        return

    for attr in selected_attrs:
        if cmds.objExists(attr):
            cmds.setAttr(attr, keyable=is_keyable)
            if not is_keyable:
                cmds.setAttr(attr, channelBox=True)


# Function to set native transform attributes (translation, rotation, scale, visibility)
def set_native_attributes(lock_state, tx_cb, rx_cb, sx_cb, vis_cb, all_cb):
    """
    Args:
        lock_state (int): 0 to lock, 1 to unlock
        tx_cb (str): CheckBox for translate attributes
        rx_cb (str): CheckBox for rotate attributes
        sx_cb (str): CheckBox for scale attributes
        vis_cb (str): CheckBox for visibility attribute
        all_cb (str): CheckBox for all attributes
    """
    selected_objects = cmds.ls(selection=True)

    if not selected_objects:
        cmds.warning("No objects selected!")
        return

    # Determine which attributes to lock/unlock based on checkboxes
    lock = True if lock_state == 0 else False
    keyable = False if lock_state == 0 else True

    attributes = []
    if cmds.checkBox(all_cb, query=True, value=True):
        attributes = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']
    else:
        if cmds.checkBox(tx_cb, query=True, value=True):
            attributes.extend(['tx', 'ty', 'tz'])
        if cmds.checkBox(rx_cb, query=True, value=True):
            attributes.extend(['rx', 'ry', 'rz'])
        if cmds.checkBox(sx_cb, query=True, value=True):
            attributes.extend(['sx', 'sy', 'sz'])
        if cmds.checkBox(vis_cb, query=True, value=True):
            attributes.append('v')

    for obj in selected_objects:
        for attr in attributes:
            if cmds.objExists(f"{obj}.{attr}"):
                cmds.setAttr(f"{obj}.{attr}", lock=lock, keyable=keyable)


# Function to set native attributes keyable/unkeyable (and keep them visible)
def set_native_keyable(is_keyable, tx_cb, rx_cb, sx_cb, vis_cb, all_cb):
    """
    Args:
        is_keyable (bool): If True, make keyable; if False, make unkeyable but visible in the channel box.
        tx_cb (str): CheckBox for translate attributes
        rx_cb (str): CheckBox for rotate attributes
        sx_cb (str): CheckBox for scale attributes
        vis_cb (str): CheckBox for visibility attribute
        all_cb (str): CheckBox for all attributes
    """
    selected_objects = cmds.ls(selection=True)

    if not selected_objects:
        cmds.warning("No objects selected!")
        return

    keyable = is_keyable

    attributes = []
    if cmds.checkBox(all_cb, query=True, value=True):
        attributes = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']
    else:
        if cmds.checkBox(tx_cb, query=True, value=True):
            attributes.extend(['tx', 'ty', 'tz'])
        if cmds.checkBox(rx_cb, query=True, value=True):
            attributes.extend(['rx', 'ry', 'rz'])
        if cmds.checkBox(sx_cb, query=True, value=True):
            attributes.extend(['sx', 'sy', 'sz'])
        if cmds.checkBox(vis_cb, query=True, value=True):
            attributes.append('v')

    for obj in selected_objects:
        for attr in attributes:
            if cmds.objExists(f"{obj}.{attr}"):
                cmds.setAttr(f"{obj}.{attr}", keyable=keyable)
                if not keyable:
                    cmds.setAttr(f"{obj}.{attr}", channelBox=True)


# Run the script
state_tool_ui()
