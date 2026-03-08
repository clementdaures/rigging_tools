from maya import cmds

node_list = cmds.ls(selection=True)
for node in node_list:
    cmds.lockNode( node, lock=False )
    cmds.delete(node)