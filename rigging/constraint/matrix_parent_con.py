import maya.cmds as cmds

class MatrixConstraint:
    def __init__(self):
        self.blend_matrix_node = None
        self.weight_translate_slider = "translateWeightSlider"
        self.weight_rotate_slider = "rotateWeightSlider"
        self.weight_scale_slider = "scaleWeightSlider"

        # Initialize pick matrix options
        self.pick_matrix_options = {
        'rotate': True,
        'scale': True,
        'translate': True
        }

        # Initialize weight values
        self.weight_translate = 0.5
        self.weight_rotate = 0.5
        self.weight_scale = 0.5
        

    def update_pick_matrix_options(self):
        """ Updates the pick matrix options based on UI checkboxes """
        if cmds.checkBox('rotateCheckBox', exists=True):
            self.pick_matrix_options['rotate'] = cmds.checkBox('rotateCheckBox', query=True, value=True)
        if cmds.checkBox('scaleCheckBox', exists=True):
            self.pick_matrix_options['scale'] = cmds.checkBox('scaleCheckBox', query=True, value=True)
        if cmds.checkBox('translateCheckBox', exists=True):
            self.pick_matrix_options['translate'] = cmds.checkBox('translateCheckBox', query=True, value=True)

        print("Updated Pick Matrix Options:", self.pick_matrix_options)  # Debugging print


    def update_blend_matrix_weights(self):
        """ Updates the blend matrix weights based on UI sliders. """
        
        if cmds.floatSliderGrp("translateWeightSlider", exists=True):
           self.weight_translate = cmds.floatSliderGrp("translateWeightSlider", query=True, value=True)
        if cmds.floatSliderGrp("rotateWeightSlider", exists=True):
            self.weight_rotate = cmds.floatSliderGrp("rotateWeightSlider", query=True, value=True)
        if cmds.floatSliderGrp("scaleWeightSlider", exists=True):
            self.weight_scale = cmds.floatSliderGrp("scaleWeightSlider", query=True, value=True)

        if not self.blend_matrix_node or not cmds.objExists(self.blend_matrix_node):
            print(" Error: Blend Matrix node does not exist. Skipping weight update.")
            return

        target_count = cmds.getAttr(f"{self.blend_matrix_node}.target", size=True) if cmds.attributeQuery('target', node=self.blend_matrix_node, exists=True) else 0

        if target_count == 0:
            print(f" Warning: Blend Matrix '{self.blend_matrix_node}' has no targets. Skipping weight updates.")
            return

        for i in range(target_count):
            cmds.setAttr(f"{self.blend_matrix_node}.target[{i}].translateWeight", self.weight_translate)
            cmds.setAttr(f"{self.blend_matrix_node}.target[{i}].rotateWeight", self.weight_rotate)
            cmds.setAttr(f"{self.blend_matrix_node}.target[{i}].scaleWeight", self.weight_scale)
        print(f"Set target[{i}] weights -> Translate: {self.weight_translate}, Rotate: {self.weight_rotate}, Scale: {self.weight_scale}")

    def create_with_hold_matrix(self, object_01, object_02, parent):

        self.update_pick_matrix_options()

        hold_matrix_name = f"holdMat_{object_02}_cc_by_{object_01}"
        mult_matrix_name = f"multMat_{object_02}_cc_by_{object_01}"
        pick_matrix_name = f"pickMat_{object_02}_cc_by_{object_01}"

        # Create and connect pickMatrix node
        pick_matrix = cmds.createNode("pickMatrix", name=pick_matrix_name)
        cmds.setAttr(f"{pick_matrix}.useRotate", self.pick_matrix_options['rotate'])
        cmds.setAttr(f"{pick_matrix}.useScale", self.pick_matrix_options['scale'])
        cmds.setAttr(f"{pick_matrix}.useTranslate", self.pick_matrix_options['translate'])

        # Create and connect multMatrix node
        mult_matrix = cmds.createNode("multMatrix", name=mult_matrix_name)
        cmds.connectAttr(f"{object_02}.worldMatrix[0]", f"{mult_matrix}.matrixIn[0]")
        cmds.connectAttr(f"{object_01}.worldInverseMatrix[0]", f"{mult_matrix}.matrixIn[1]")

        # Create holdMatrix node and connect
        hold_matrix = cmds.createNode("holdMatrix", name=hold_matrix_name)
        cmds.connectAttr(f"{mult_matrix}.matrixSum", f"{hold_matrix}.inMatrix")

        # Disconnect temporary connections
        cmds.disconnectAttr(f"{mult_matrix}.matrixSum", f"{hold_matrix}.inMatrix")
        cmds.disconnectAttr(f"{object_02}.worldMatrix[0]", f"{mult_matrix}.matrixIn[0]")
        cmds.disconnectAttr(f"{object_01}.worldInverseMatrix[0]", f"{mult_matrix}.matrixIn[1]")

        # Disconnect existing connections to offsetParentMatrix
        existing_connections = cmds.listConnections(f"{object_02}.offsetParentMatrix", s=True, d=False, p=True)
        if existing_connections:
            for connection in existing_connections:
                print(f"Disconnecting {connection} from {object_02}.offsetParentMatrix")
                cmds.disconnectAttr(connection, f"{object_02}.offsetParentMatrix")

        # Reconnect with final connections
        cmds.connectAttr(f"{hold_matrix}.outMatrix", f"{mult_matrix}.matrixIn[0]")
        cmds.connectAttr(f"{object_01}.worldMatrix[0]", f"{pick_matrix}.inputMatrix")
        cmds.connectAttr(f"{pick_matrix}.outputMatrix", f"{mult_matrix}.matrixIn[1]")  # Fixed to outputMatrix
        cmds.connectAttr(f"{parent}.worldInverseMatrix[0]", f"{mult_matrix}.matrixIn[2]")
        cmds.connectAttr(f"{mult_matrix}.matrixSum", f"{object_02}.offsetParentMatrix")

    def create_without_hold_matrix(self, object_01, object_02, parent):
        
        self.update_pick_matrix_options()
        
        mult_matrix_name = f"multMat_{object_02}_cc_by_{object_01}"
        pick_matrix_name = f"pickMat_{object_02}_cc_by_{object_01}"

        # Create and connect pickMatrix node
        pick_matrix = cmds.createNode("pickMatrix", name=pick_matrix_name)
        cmds.setAttr(f"{pick_matrix}.useRotate", self.pick_matrix_options['rotate'])
        cmds.setAttr(f"{pick_matrix}.useScale", self.pick_matrix_options['scale'])
        cmds.setAttr(f"{pick_matrix}.useTranslate", self.pick_matrix_options['translate'])

        # Create and connect multMatrix node
        mult_matrix = cmds.createNode("multMatrix", name=mult_matrix_name)
        cmds.connectAttr(f"{object_01}.worldMatrix[0]", f"{pick_matrix}.inputMatrix")
        cmds.connectAttr(f"{pick_matrix}.outputMatrix", f"{mult_matrix}.matrixIn[0]")  # Fixed to outputMatrix
        cmds.connectAttr(f"{parent}.worldInverseMatrix[0]", f"{mult_matrix}.matrixIn[1]")

        # Disconnect existing connections to offsetParentMatrix
        existing_connections = cmds.listConnections(f"{object_02}.offsetParentMatrix", s=True, d=False, p=True)
        if existing_connections:
            for connection in existing_connections:
                print(f"Disconnecting {connection} from {object_02}.offsetParentMatrix")
                cmds.disconnectAttr(connection, f"{object_02}.offsetParentMatrix")

        cmds.connectAttr(f"{mult_matrix}.matrixSum", f"{object_02}.offsetParentMatrix")

    def create_blend_matrix(self, mult_matrices, constrained_object):
        
        blend_matrix_name = f"blendMat_{constrained_object}"
        self.blend_matrix_node = cmds.createNode("blendMatrix", name=blend_matrix_name)

        # Connect the first multMatrix to inputMatrix
        cmds.connectAttr(f"{mult_matrices[0]}.matrixSum", f"{self.blend_matrix_node}.inputMatrix")

        # Connect all other multMatrix nodes to target[*].targetMatrix
        for index, mult_matrix in enumerate(mult_matrices[1:], start=1):
            cmds.connectAttr(f"{mult_matrix}.matrixSum", f"{self.blend_matrix_node}.target[{index - 1}].targetMatrix")

        # Disconnect existing connections to offsetParentMatrix
        existing_connections = cmds.listConnections(f"{constrained_object}.offsetParentMatrix", s=True, d=False, p=True)
        if existing_connections:
            for connection in existing_connections:
                print(f"Disconnecting {connection} from {constrained_object}.offsetParentMatrix")
                cmds.disconnectAttr(connection, f"{constrained_object}.offsetParentMatrix")

        # Connect blendMatrix to constrained object
        cmds.connectAttr(f"{self.blend_matrix_node}.outputMatrix", f"{constrained_object}.offsetParentMatrix")

        # Set initial weights from sliders
        self.update_blend_matrix_weights()

    def create_constraint(self):
        selected_objects = cmds.ls(selection=True)
        if len(selected_objects) < 2:
            raise ValueError("Please select at least two objects.")

        constraining_objects = selected_objects[:-1]
        constrained_object = selected_objects[-1]

        parent = cmds.listRelatives(constrained_object, parent=True)
        if not parent:
            # Create a group offset
            offset_constrained_object = cmds.createNode('transform', name='OFF_' + constrained_object)
            cmds.matchTransform(offset_constrained_object, constrained_object)
            cmds.parent(constrained_object, offset_constrained_object)
            cmds.select(clear=True)
            print("Offset parent for constrained object has been created")
            parent = offset_constrained_object  # Corrected: Set parent to the new offset object
        else:
            parent = parent[0]

        pick_matrix_options = {
            'rotate': cmds.checkBox('rotateCheckBox', query=True, value=True),
            'scale': cmds.checkBox('scaleCheckBox', query=True, value=True),
            'translate': cmds.checkBox('translateCheckBox', query=True, value=True),
        }

        mult_matrices = []

        use_hold_matrix = cmds.checkBox('offsetCheckBox', query=True, value=True)

        if use_hold_matrix:
            for constraining_object in constraining_objects:
                self.create_with_hold_matrix(constraining_object, constrained_object, parent)
                mult_matrices.append(f"multMat_{constrained_object}_cc_by_{constraining_object}")
        else:
            for constraining_object in constraining_objects:
                self.create_without_hold_matrix(constraining_object, constrained_object, parent)
                mult_matrices.append(f"multMat_{constrained_object}_cc_by_{constraining_object}")

        if len(constraining_objects) > 1:
            self.create_blend_matrix(mult_matrices, constrained_object)

    def matrix_cc(self):
        selected_objects = cmds.ls(selection=True)
        if len(selected_objects) < 2:
            cmds.warning("Select at least two objects.")
            return

        constraining_objects = selected_objects[:-1]
        constrained_object = selected_objects[-1]
        parent = cmds.listRelatives(constrained_object, parent=True)

        if not parent:
            offset_constrained_object = cmds.createNode('transform', name='OFF_' + constrained_object)
            cmds.matchTransform(offset_constrained_object, constrained_object)
            cmds.parent(constrained_object, offset_constrained_object)
            cmds.select(clear=True)
            parent = offset_constrained_object
        else:
            parent = parent[0]

        use_hold_matrix = cmds.checkBox('offsetCheckBox', query=True, value=True)

        mult_matrices = []
        for obj in constraining_objects:
            if use_hold_matrix:
                self.create_with_hold_matrix(obj, constrained_object, parent)
            else:
                self.create_without_hold_matrix(obj, constrained_object, parent)
            mult_matrices.append(f"multMat_{constrained_object}_cc_by_{obj}")

        if len(constraining_objects) > 1:
            self.create_blend_matrix(mult_matrices, constrained_object)


# Create UI
def matrix_cc_ui(matrix_constraint):
    if cmds.window("matrixCCWindow", exists=True):
        cmds.deleteUI("matrixCCWindow")
        
    def reset_preferences(*args):
        print("Preferences reset!")
    
    def show_help(*args):
        cmds.confirmDialog(title="Help", message="This is the help section.", button=["OK"])

    # Matrix Add Button Function
    def matrix_cc_add(*args):
        matrix_constraint.update_blend_matrix_weights()
        matrix_constraint.matrix_cc()
        matrix_constraint.update_blend_matrix_weights()
        cmds.deleteUI("matrixCCWindow", window=True)
    
    def matrix_cc_apply(*args):
        matrix_constraint.update_blend_matrix_weights()
        matrix_constraint.matrix_cc()
        matrix_constraint.update_blend_matrix_weights()

    # Text Variables
    offset_text = "Maintain offset:"
    frame_text = "Constraint axes:"
    translate_text = "Translate:"
    rotate_text = "Rotate:"
    scale_text = "Scale:"
    all_text = "All"
    x_text = "X"
    y_text = "Y"
    z_text = "Z"
    weight_text = "Weight:"
    copyright_text = f'Copyright (c) 2024 Clement Daures. All rights reserved.'

    # Create the window
    window = cmds.window("matrixCCWindow", sizeable=False, title="Matrix Constraint Options", widthHeight=(550, 375))

    # Create a form layout
    form = cmds.formLayout()

    # Create a main layout inside the form
    main_layout = cmds.columnLayout(adjustableColumn=True, parent=form)
    
    # Create a menu bar
    menu_bar = cmds.menuBarLayout(parent=main_layout)
    
    # Create the 'Edit' menu
    edit_menu = cmds.menu(label="Edit", parent=menu_bar)
    cmds.menuItem(label="Reset Preferences", command=reset_preferences)
    
    # Create the 'Help' menu
    help_menu = cmds.menu(label="Help", parent=menu_bar)
    cmds.menuItem(label="Help", command=show_help)

    cmds.setParent(main_layout)
    
    # Form layout of Maintain Offset
    cmds.separator(style="none", height=10)
    offset_form = cmds.formLayout(parent=main_layout)
    offset_label = cmds.text(label=offset_text, parent=offset_form)
    offset_checkbox = cmds.checkBox('offsetCheckBox', label='', value=True, parent=offset_form)
    cmds.formLayout(offset_form, edit=True,
                    attachForm=[(offset_label, 'left', 20), (offset_label, 'top', 5),
                                (offset_checkbox, 'top', 5)],
                    attachControl=[(offset_checkbox, 'left', 5, offset_label)])

    cmds.separator(style="none", height=25)
    cmds.separator(height=10, style='single', parent=main_layout)
    cmds.frameLayout(label=frame_text, collapsable=False, parent=main_layout)
    
    # Form layout of Translate
    translate_form = cmds.formLayout(parent=main_layout)
    translate_label = cmds.text(label=translate_text, parent=translate_form)
    translate_checkbox = cmds.checkBox('translateCheckBox', label=all_text, value=True, parent=translate_form)
    cmds.formLayout(translate_form, edit=True,
                    attachForm=[(translate_label, 'left', 50), (translate_label, 'top', 10),
                                (translate_checkbox, 'top', 10)],
                    attachControl=[(translate_checkbox, 'left', 5, translate_label)])
    
    # Row layout of Translate Axis
    translate_axis_form = cmds.formLayout(parent=main_layout)
    translate_x = cmds.checkBox('translateCheckbox_X', label=x_text, value=False, parent=translate_axis_form)
    translate_y = cmds.checkBox('translateCheckbox_Y', label=y_text, value=False, parent=translate_axis_form)
    translate_z = cmds.checkBox('translateCheckbox_Z', label=z_text, value=False, parent=translate_axis_form)
    cmds.formLayout(translate_axis_form, edit=True,
                    attachForm=[(translate_x, 'left', 184), (translate_y, 'left', 254), (translate_z, 'left', 324)])

    # Add sliders with input boxes
    
    weight_translate_form = cmds.formLayout(parent=main_layout)
    weight_translate_label = cmds.text(label=weight_text, parent=weight_translate_form)
    cmds.floatSliderGrp("translateWeightSlider",field=True, minValue=0.0000, maxValue=1.0000, fieldMinValue=-10.0, fieldMaxValue=20.0, value=0.5000, parent=weight_translate_form, changeCommand=lambda *args: matrix_constraint.update_blend_matrix_weights())
    cmds.formLayout(weight_translate_form, edit=True,
                    attachForm=[(weight_translate_label, 'left', 138), (weight_translate_label, 'top', 6),
                                ("translateWeightSlider", 'top', 1)],
                    attachControl=[("translateWeightSlider", 'left', 3, weight_translate_label)])

    # Form layout of Rotate
    rotate_form = cmds.formLayout(parent=main_layout)
    rotate_label = cmds.text(label=rotate_text, parent=rotate_form)
    rotate_checkbox = cmds.checkBox('rotateCheckBox', label=all_text, value=True, parent=rotate_form)
    cmds.formLayout(rotate_form, edit=True,
                    attachForm=[(rotate_label, 'left', 62), (rotate_label, 'top', 20),
                                (rotate_checkbox, 'top', 20)],
                    attachControl=[(rotate_checkbox, 'left', 5, rotate_label)])
    
    # Row layout of Rotate Axis
    rotate_axis_form = cmds.formLayout(parent=main_layout)
    rotate_x = cmds.checkBox('rotateCheckbox_X', label=x_text, value=False, parent=rotate_axis_form)
    rotate_y = cmds.checkBox('rotateCheckbox_Y', label=y_text, value=False, parent=rotate_axis_form)
    rotate_z = cmds.checkBox('rotateCheckbox_Z', label=z_text, value=False, parent=rotate_axis_form)
    cmds.formLayout(rotate_axis_form, edit=True,
                    attachForm=[(rotate_x, 'left', 184), (rotate_y, 'left', 254), (rotate_z, 'left', 324)])

    # Add sliders with input boxes
    weight_rotate_form = cmds.formLayout(parent=main_layout)
    weight_rotate_label = cmds.text(label=weight_text, parent=weight_rotate_form)
    cmds.floatSliderGrp("rotateWeightSlider", field=True, minValue=0.0000, maxValue=1.0000, fieldMinValue=-10.0, fieldMaxValue=20.0, value=0.5000, parent=weight_rotate_form, changeCommand=lambda *args: matrix_constraint.update_blend_matrix_weights())
    cmds.formLayout(weight_rotate_form, edit=True,
                    attachForm=[(weight_rotate_label, 'left', 138), (weight_rotate_label, 'top', 6),
                                ("rotateWeightSlider", 'top', 1)],
                    attachControl=[("rotateWeightSlider", 'left', 3, weight_rotate_label)])

    # Form layout of Scale
    scale_form = cmds.formLayout(parent=main_layout)
    scale_label = cmds.text(label=scale_text, parent=scale_form)
    scale_checkbox = cmds.checkBox('scaleCheckBox', label=all_text, value=True, parent=scale_form)
    cmds.formLayout(scale_form, edit=True,
                    attachForm=[(scale_label, 'left', 70), (scale_label, 'top', 20),
                                (scale_checkbox, 'top', 20)],
                    attachControl=[(scale_checkbox, 'left', 5, scale_label)])
    
    # Row layout of Scale Axis
    scale_axis_form = cmds.formLayout(parent=main_layout)
    scale_x = cmds.checkBox('scaleCheckbox_X', label=x_text, value=False, parent=scale_axis_form)
    scale_y = cmds.checkBox('scaleCheckbox_Y', label=y_text, value=False, parent=scale_axis_form)
    scale_z = cmds.checkBox('scaleCheckbox_Z', label=z_text, value=False, parent=scale_axis_form)
    cmds.formLayout(scale_axis_form, edit=True,
                    attachForm=[(scale_x, 'left', 184), (scale_y, 'left', 254), (scale_z, 'left', 324)])

    # Add sliders with input boxes
    weight_scale_form = cmds.formLayout(parent=main_layout)
    weight_scale_label = cmds.text(label=weight_text, parent=weight_scale_form)
    cmds.floatSliderGrp("scaleWeightSlider", field=True, minValue=0.0000, maxValue=1.0000, fieldMinValue=-10.0, fieldMaxValue=20.0, value=0.5000, parent=weight_scale_form, changeCommand=lambda *args: matrix_constraint.update_blend_matrix_weights())
    cmds.formLayout(weight_scale_form, edit=True,
                    attachForm=[(weight_scale_label, 'left', 138), (weight_scale_label, 'top', 6),
                                ("scaleWeightSlider", 'top', 1)],
                    attachControl=[("scaleWeightSlider", 'left', 3, weight_scale_label)])

    cmds.setParent(main_layout)  # Return to parent layout

    # Create a form layout for the buttons
    button_layout = cmds.formLayout(parent=form)
    
    add_button = cmds.button(label="Add", command=matrix_cc_add)
    apply_button = cmds.button(label="Apply", command=matrix_cc_apply)
    close_button = cmds.button(label="Close", command=lambda *args: cmds.deleteUI(window, window=True))
    
    cmds.formLayout(button_layout, edit=True, 
                    attachForm=[(add_button, 'left', 1), (add_button, 'bottom', 1),
                                (apply_button, 'bottom', 1),
                                (close_button, 'right', 1), (close_button, 'bottom', 1)],
                    attachPosition=[(add_button, 'right', 2, 33), 
                                    (apply_button, 'left', 2, 33), (apply_button, 'right', 2, 66),
                                    (close_button, 'left', 2, 66)])
    
    # Attach the main layout and button layout to the form
    cmds.formLayout(form, edit=True, 
                    attachForm=[(main_layout, 'top', 1), (main_layout, 'left', 1), (main_layout, 'right', 1),
                                (button_layout, 'left', 1), (button_layout, 'right', 1)],
                    attachControl=[(main_layout, 'bottom', 1, button_layout)])
    
    # Attach the copyright text directly to the form layout
    copyright_info = cmds.text(label=copyright_text, align="left", parent=form)
    cmds.formLayout(form, edit=True,
                    attachForm=[(copyright_info, 'left', 5), (copyright_info, 'bottom', 5)],
                    attachControl=[(button_layout, 'bottom', 5, copyright_info)])

    cmds.showWindow(window)

matrix_constraint = MatrixConstraint()
matrix_cc_ui(matrix_constraint)
