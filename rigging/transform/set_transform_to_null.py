import maya.cmds as cmds

def zero_out_joint_transforms():
    # Get the current selection
    selected_joints = cmds.ls(selection=True, type='joint')

    if not selected_joints:
        cmds.warning("Please select at least one joint.")
        return

    for joint in selected_joints:
        # Zero out the translation, rotation, and scale
        cmds.setAttr(f"{joint}.translate", 0, 0, 0)
        cmds.setAttr(f"{joint}.rotate", 0, 0, 0)
        cmds.setAttr(f"{joint}.scale", 1, 1, 1)

        # Zero out the joint orient
        cmds.setAttr(f"{joint}.jointOrient", 0, 0, 0)

    print(f"Zeroed out transforms for {len(selected_joints)} joints.")

# Execute the function
zero_out_joint_transforms()
