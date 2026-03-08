import maya.cmds as cmds

def create_joint_on_locator():
    selected_locators = cmds.ls(selection=True, type='transform')  # Ensure only transforms are selected

    for locator in selected_locators:
        if 'pinOutput' in locator:
            joint_name = locator.replace('pinOutput', 'pinJoint')

            # Clear selection before creating a joint
            cmds.select(clear=True)
            joint = cmds.joint(name=joint_name)

            # Match the joint's transform to the locator
            cmds.matchTransform(joint, locator)

            # Parent the joint to the locator
            cmds.parent(joint, locator)

            # Rename the transform node created by parenting
            transform_node = cmds.listRelatives(joint, parent=True)[0]
            new_transform_name = locator.replace('pinOutput', 'pinTransform')
            cmds.rename(transform_node, new_transform_name)

            # Clear selection after processing each joint
            cmds.select(clear=True)

    print("Joints created and parented to locators.")

if __name__=="__main__":
    create_joint_on_locator()
