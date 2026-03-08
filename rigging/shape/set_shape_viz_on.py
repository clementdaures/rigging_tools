import maya.cmds as cmds

# Get the selected objects
selected_objects = cmds.ls(sl=True, fl=True)

for obj in selected_objects:
    # Find the shape node(s) associated with each selected transform node
    shape_nodes = cmds.listRelatives(obj, shapes=True, fullPath=True)
    
    # If shape nodes are found, set them to invisible without affecting children
    if shape_nodes:
        for shape in shape_nodes:
            # Enable the override on the shape node
            cmds.setAttr(f"{shape}.overrideEnabled", True)
            # Set the shape node to invisible
            cmds.setAttr(f"{shape}.overrideVisibility", True)