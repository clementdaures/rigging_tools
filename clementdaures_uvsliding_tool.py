
from maya import cmds
import re

# Function to create the UI
def show_ui():
    # Check if the window already exists
    if cmds.window("UVSlidingUI", exists=True):
        cmds.deleteUI("UVSlidingUI", window=True)
 
    # Copyright notice
    copyright_text = f'\nCopyright (c) 2024 Clement Daures. All rights reserved.' 
    
    # Create the main window
    window = cmds.window("UVSlidingUI", sizeable=False, title="UV Sliding Tool", widthHeight=(330, 275))
    layout = cmds.columnLayout(adjustableColumn=True)
    
    # UI to select or enter the controller
    cmds.text(label="Select or Enter Controller:")
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(100, 200))
    cmds.button(label="Select Controller", command=lambda x: select_controller("controller_field"))
    controller_field = cmds.textField("controller_field", placeholderText="Enter Controller Name", text="")  # Unique name for text field
    cmds.setParent("..")  # Return to main layout
    
    cmds.separator(height=10, style="in")
    
    # UI for the attribute name
    cmds.text(label="Enter Attribute Name to Drive UV Pin:")
    attr_name_field = cmds.textField("attr_name_field", placeholderText="Enter Attribute Name", text="offset")  # Preload 'offset'
    
    cmds.separator(height=10, style="in")
    
    # Checkbox for U or V coordinate selection
    cmds.text(label="Coordinate to Drive:")
    u_or_v = cmds.checkBoxGrp("coordinate_selection", numberOfCheckBoxes=2, labelArray2=["Use U Coordinate", "Use V Coordinate"], value1=True, value2=False)
    
    cmds.separator(height=10, style="in")
    
    # UI for UV pin input
    cmds.text(label="Enter UV Pin Name:")
    uvpin_field = cmds.textField("uvpin_field", placeholderText="Enter UV Pin Name", text="uvPin1")  # Preload 'uvPin1'
    
    cmds.separator(height=10, style="in")
    
    # UI for running the script
    cmds.text(label="Select Joints:")
    cmds.button(label="Run Script", command=lambda x: run_script_on_joints("controller_field", "attr_name_field", "uvpin_field", "coordinate_selection"))
    
    cmds.separator(height=10, style="in")
    
    # Quit button
    cmds.button(label="Close", command=lambda x: cmds.deleteUI(window, window=True))
    
    # Add copyright notice
    cmds.text(label=copyright_text, align="left")
    
    # Show the window
    cmds.showWindow(window)

# Global variable to store the selected controller
selected_controller = ""

# Function to handle controller selection
def select_controller(controller_field):
    global selected_controller
    
    # Let the user select the controller in the scene
    selection = cmds.ls(selection=True)
    if not selection:
        cmds.warning("No controller selected. Please select a controller and try again.")
        return
    
    selected_controller = selection[0]
    
    # Automatically update the text field with the selected controller
    cmds.textField(controller_field, edit=True, text=selected_controller)
    cmds.confirmDialog(title="Controller Selected", message=f"Controller '{selected_controller}' selected.")

# Function to run the provided script on selected joints
def run_script_on_joints(controller_field, attr_name_field, uvpin_field, u_or_v):
    global selected_controller
    
    # Get the controller name from the text field if entered
    controller_name = cmds.textField(controller_field, query=True, text=True).strip()
    if controller_name:
        selected_controller = controller_name
    
    # Validate the selected controller
    if not cmds.objExists(selected_controller):
        cmds.warning("Invalid controller specified. Please select or enter a valid controller.")
        return
    
    # Get the attribute name
    attr_name = cmds.textField(attr_name_field, query=True, text=True).strip()
    if not attr_name:
        cmds.warning("Please specify an attribute name to drive the UV pin.")
        return
    
    # Ensure the custom attribute exists
    if not cmds.attributeQuery(attr_name, node=selected_controller, exists=True):
        cmds.addAttr(selected_controller, longName=attr_name, attributeType='double', keyable=True)
        cmds.setAttr(f"{selected_controller}.{attr_name}", 0)  # Initialize it with 0
    
    # Get the UV pin name
    uv_pin = cmds.textField(uvpin_field, query=True, text=True).strip()
    if not uv_pin or not cmds.objExists(uv_pin):
        cmds.warning("Invalid UV pin specified. Please enter a valid UV pin name.")
        return
    
    # Determine whether to use U or V coordinate
    use_u = cmds.checkBoxGrp(u_or_v, query=True, value1=True)
    use_v = cmds.checkBoxGrp(u_or_v, query=True, value2=True)
    if use_u == use_v:
        cmds.warning("Please select either U or V coordinate, but not both.")
        return
    
    coordinate = "coordinateU" if use_u else "coordinateV"

    # Select joints
    jnt_selection = cmds.ls(selection=True)
    if not jnt_selection:
        cmds.warning("No joints selected. Please select joints and try again.")
        return

    # Process each selected joint
    for i, joint in enumerate(jnt_selection):
        # Retrieve the U or V value for the corresponding joint
        uv_value = cmds.getAttr(f'{uv_pin}.coordinate[{i}].{coordinate}')
        
        # Create addDoubleLinear and modulo nodes
        add_name = f'{joint}_Add'
        modulo_name = f'{joint}_Modulo'
        add_node = cmds.createNode('addDoubleLinear', n=add_name)
        modulo_node = cmds.createNode('modulo', n=modulo_name)
        
        # Set the initial input1 value for addDoubleLinear
        cmds.setAttr(f'{add_node}.input1', uv_value)
        cmds.setAttr(f'{modulo_node}.modulus', 1)
        
        # Connect the custom attribute to addDoubleLinear's input2
        cmds.connectAttr(f'{selected_controller}.{attr_name}', f'{add_node}.input2')
        cmds.connectAttr(f'{add_node}.output', f'{modulo_node}.input')
        
        # Connect modulo's output to the UV pin's coordinate attribute
        cmds.connectAttr(f'{modulo_node}.output', f'{uv_pin}.coordinate[{i}].{coordinate}')

    cmds.confirmDialog(title="Script Complete", message="Script executed successfully on selected joints.")

# Launch the UI
show_ui()
