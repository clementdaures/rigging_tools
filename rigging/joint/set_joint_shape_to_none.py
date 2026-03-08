import maya.cmds as cmds

selection = cmds.ls(selection=True)

for j in selection:
    if cmds.attributeQuery('drawStyle', node=j, exists=True):
        cmds.setAttr(f'{j}.drawStyle', 2)
    else:
        print(f"Object {j} does not have a 'drawStyle' attribute.")
