import maya.cmds as cmds

def set_scale_to_one():
    '''Sets the scale of all selected DAG nodes to (1, 1, 1).'''
    
    # Get the selected DAG nodes
    selected_dag_nodes = cmds.ls(selection=True, dag=True, shapes=False)

    # Check if any DAG nodes are selected
    if not selected_dag_nodes:
        print("No DAG nodes selected.")
        return

    # Set the scale of each selected DAG node to (1, 1, 1)
    for dag_node in selected_dag_nodes:
        if cmds.attributeQuery("scale", node=dag_node, exists=True):
            cmds.setAttr(dag_node + ".scale", 1, 1, 1)
            print(f"Set scale of {dag_node} to (1, 1, 1).")
        else:
            print(f"{dag_node} does not have a scale attribute.")

# Call the function to execute
set_scale_to_one()
