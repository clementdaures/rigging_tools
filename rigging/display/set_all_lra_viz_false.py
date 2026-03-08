import maya.cmds as cmds

# Get all transform nodes in the scene
all_objects = cmds.ls(type='transform')

# Loop through each object and check if 'displayLocalAxis' exists
for obj in all_objects:
    # Check if the 'displayLocalAxis' attribute exists for the object
    if cmds.attributeQuery('displayLocalAxis', node=obj, exists=True):
        # Set the 'displayLocalAxis' attribute to False to hide the local rotation axis
        cmds.setAttr(f"{obj}.displayLocalAxis", False)

print("Local Rotation Axis has been turned off for all objects in the scene.")