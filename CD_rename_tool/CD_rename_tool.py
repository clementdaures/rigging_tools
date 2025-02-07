import maya.cmds as cmds

# Global list to keep track of renaming history
renaming_history = []

def clementdaures_rename_tool():
    """Main function to initialize and display the Rename Tool window."""
    if cmds.window('dc_renameWindow', exists=True):
        cmds.deleteUI('dc_renameWindow')

    # Create the main window
    window = cmds.window('dc_renameWindow', title="DC Rename Tool", widthHeight=(400, 600), sizeable=True)

    # Main layout
    main_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=10, columnAlign="center")

    # Rename and Number Section
    cmds.frameLayout(label="Rename and Number", collapsable=True, width=380, marginHeight=5)
    cmds.textFieldGrp('renameTextField', label="Rename:", columnAlign=(1, 'right'), columnWidth=[(1, 80), (2, 280)])
    cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 180), (2, 180)])
    cmds.intFieldGrp('startNumberField', label="Start Number:", value1=1, columnWidth=[(1, 90), (2, 90)])
    cmds.intFieldGrp('paddingField', label="Padding:", value1=2, columnWidth=[(1, 90), (2, 90)])
    cmds.setParent('..')
    cmds.button(label="Rename and Number", height=30, command=lambda x: rename_and_number_objects())

    cmds.separator(height=20, style="in")

    # Prefix/Suffix Section
    cmds.frameLayout(label="Prefix and Suffix", collapsable=True, width=380, marginHeight=5)
    cmds.textFieldGrp('prefixTextField', label="Prefix:", columnAlign=(1, 'right'), columnWidth=[(1, 80), (2, 280)])
    cmds.textFieldGrp('suffixTextField', label="Suffix:", columnAlign=(1, 'right'), columnWidth=[(1, 80), (2, 280)])
    cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 180), (2, 180)])
    cmds.button(label="Add Prefix", command=lambda x: rename_with_prefix_suffix(1))
    cmds.button(label="Add Suffix", command=lambda x: rename_with_prefix_suffix(2))
    cmds.setParent('..')

    cmds.separator(height=20, style="in")

    # Remove Characters Section
    cmds.frameLayout(label="Remove Characters", collapsable=True, width=380, marginHeight=5)
    cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 180), (2, 180)])
    cmds.button(label="Remove First Character", command=lambda x: remove_character(1))
    cmds.button(label="Remove Last Character", command=lambda x: remove_character(2))
    cmds.setParent('..')

    cmds.separator(height=20, style="in")

    # Quick Prefix Section
    cmds.frameLayout(label="Quick Prefix", collapsable=True, width=380, marginHeight=5)
    cmds.rowColumnLayout(numberOfColumns=5, columnWidth=[(1, 75), (2, 75), (3, 75), (4, 75), (5, 75)])
    quick_prefix_buttons = ['Grp', 'Sk', 'Jnt','Bn', 'Ctrl', 'EFF', 'IKRP', 'IKSC', 'IKSPL', 'IKSPR', 'Loc', 'Geo', 'Proxy', 'Wire', 'ffdLat', 'RBN', 'CRV', 'BS', 'DRV', 'AUTO']
    for prefix in quick_prefix_buttons:
        cmds.button(label=prefix, command=lambda x, p=prefix: add_quick_prefix(p))
    cmds.setParent('..')

    cmds.separator(height=20, style="in")

    # Quick Suffix Section
    cmds.frameLayout(label="Quick Suffix", collapsable=True, width=380, marginHeight=5)
    cmds.rowColumnLayout(numberOfColumns=5, columnWidth=[(1, 75), (2, 75), (3, 75), (4, 75), (5, 75)])
    quick_suffix_buttons = ['Lt', 'Rt', 'T', 'TOP', 'MID', 'LOW', 'CTR']
    for suffix in quick_suffix_buttons:
        cmds.button(label=suffix, command=lambda x, s=suffix: add_quick_suffix(s))
    cmds.setParent('..')

    cmds.separator(height=20, style="in")

    # Search and Replace Section
    cmds.frameLayout(label="Search and Replace", collapsable=True, width=380, marginHeight=5)
    cmds.textFieldGrp('searchTextField', label="Search:", columnAlign=(1, 'right'), columnWidth=[(1, 80), (2, 280)])
    cmds.textFieldGrp('replaceTextField', label="Replace:", columnAlign=(1, 'right'), columnWidth=[(1, 80), (2, 280)])
    cmds.radioButtonGrp('searchReplaceOption', numberOfRadioButtons=3, label="Scope:", labelArray3=["Hierarchy", "Selected", "All"], select=2)
    cmds.button(label="Apply Search and Replace", height=30, command=lambda x: search_and_replace())

    # Open Advanced Features Window Button
    cmds.separator(height=20, style="in")
    cmds.button(label="Advanced Features", height=40, command=lambda x: open_advanced_features_window())

    cmds.showWindow(window)

# Renaming Core Functions

def rename_and_number_objects():
    """Rename selected objects with numbering and padding."""
    selected_objects = cmds.ls(selection=True)
    new_name = cmds.textFieldGrp('renameTextField', query=True, text=True)
    start_number = cmds.intFieldGrp('startNumberField', query=True, value1=True)
    padding = cmds.intFieldGrp('paddingField', query=True, value1=True)
    
    if not new_name:
        cmds.warning("Please enter a new name.")
        return

    for i, obj in enumerate(selected_objects):
        numbered_name = f"{new_name}{str(start_number + i).zfill(padding)}"
        renamed_object = cmds.rename(obj, numbered_name)
        renaming_history.append((obj, renamed_object))

def rename_with_prefix_suffix(mode):
    """Add prefix or suffix to selected objects."""
    selected_objects = cmds.ls(selection=True)
    if mode == 1:  # Prefix mode
        prefix = cmds.textFieldGrp('prefixTextField', query=True, text=True)
        if not prefix:
            cmds.warning("Please enter a prefix.")
            return
        for obj in selected_objects:
            renamed_object = cmds.rename(obj, prefix + obj.split('|')[-1])
            renaming_history.append((obj, renamed_object))
    elif mode == 2:  # Suffix mode
        suffix = cmds.textFieldGrp('suffixTextField', query=True, text=True)
        if not suffix:
            cmds.warning("Please enter a suffix.")
            return
        for obj in selected_objects:
            renamed_object = cmds.rename(obj, obj.split('|')[-1] + suffix)
            renaming_history.append((obj, renamed_object))

def remove_character(position):
    """Remove the first or last character from selected objects."""
    selected_objects = cmds.ls(selection=True)
    for obj in selected_objects:
        short_name = obj.split('|')[-1]
        if position == 1 and len(short_name) > 1:  # Remove first character
            renamed_object = cmds.rename(obj, short_name[1:])
        elif position == 2 and len(short_name) > 1:  # Remove last character
            renamed_object = cmds.rename(obj, short_name[:-1])
        renaming_history.append((obj, renamed_object))

def add_quick_prefix(prefix):
    """Add a predefined quick prefix to selected objects."""
    selected_objects = cmds.ls(selection=True)
    for obj in selected_objects:
        renamed_object = cmds.rename(obj, prefix + '_' + obj.split('|')[-1])
        renaming_history.append((obj, renamed_object))

def add_quick_suffix(suffix):
    """Add a predefined quick suffix to selected objects."""
    selected_objects = cmds.ls(selection=True)
    for obj in selected_objects:
        renamed_object = cmds.rename(obj, obj.split('|')[-1] + '_' + suffix)
        renaming_history.append((obj, renamed_object))

def search_and_replace():
    """Search for a term in selected object names and replace it."""
    search_term = cmds.textFieldGrp('searchTextField', query=True, text=True)
    replace_term = cmds.textFieldGrp('replaceTextField', query=True, text=True)
    option = cmds.radioButtonGrp('searchReplaceOption', query=True, select=True)
    
    if not search_term:
        cmds.warning("Please enter a search term.")
        return

    if option == 1:
        objs = cmds.ls(selection=True, dag=True, long=True)
    elif option == 2:
        objs = cmds.ls(selection=True, long=True)
    elif option == 3:
        objs = cmds.ls(long=True)

    for obj in objs:
        short_name = obj.split('|')[-1]
        new_name = short_name.replace(search_term, replace_term)
        renamed_object = cmds.rename(obj, new_name)
        renaming_history.append((obj, renamed_object))

# Advanced Features Window

def open_advanced_features_window():
    """Opens a new window with advanced renaming features like history and naming conventions."""
    if cmds.window('dc_advancedWindow', exists=True):
        cmds.deleteUI('dc_advancedWindow')

    window = cmds.window('dc_advancedWindow', title="Advanced Features", widthHeight=(400, 400), sizeable=True)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10)

    # Renaming History Section
    cmds.frameLayout(label="Renaming History", collapsable=True, width=380)
    cmds.textScrollList('historyTextScroll', numberOfRows=8, allowMultiSelection=False, height=150)
    cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 180), (2, 180)])
    cmds.button(label="Refresh History", command=lambda x: refresh_history_list())
    cmds.button(label="Clear History", command=lambda x: clear_history())
    cmds.setParent('..')

    # Automated Naming Conventions
    cmds.frameLayout(label="Automated Naming Conventions", collapsable=True, width=380)
    cmds.optionMenuGrp('namingConventionMenu', label="Convention:", columnAlign=(1, 'right'))
    cmds.menuItem(label="Rig")
    cmds.menuItem(label="Animation")
    cmds.menuItem(label="Geometry")
    cmds.menuItem(label="Controller")
    cmds.button(label="Apply Convention", command=lambda x: apply_naming_convention())

    cmds.showWindow(window)

def refresh_history_list():
    """Refresh the renaming history in the advanced features window."""
    cmds.textScrollList('historyTextScroll', edit=True, removeAll=True)
    for old_name, new_name in renaming_history:
        cmds.textScrollList('historyTextScroll', edit=True, append=f"{old_name} --> {new_name}")

def clear_history():
    """Clears the renaming history."""
    global renaming_history
    renaming_history.clear()
    refresh_history_list()

def apply_naming_convention():
    """Apply a naming convention based on the selected option."""
    convention = cmds.optionMenuGrp('namingConventionMenu', query=True, value=True)
    selected_objects = cmds.ls(selection=True)
    for obj in selected_objects:
        if convention == "Rig":
            renamed_object = cmds.rename(obj, f"RIG_{obj}")
        elif convention == "Animation":
            renamed_object = cmds.rename(obj, f"ANIM_{obj}")
        elif convention == "Geometry":
            renamed_object = cmds.rename(obj, f"GEO_{obj}")
        elif convention == "Controller":
            renamed_object = cmds.rename(obj, f"CTRL_{obj}")
        renaming_history.append((obj, renamed_object))

# Launch the tool
clementdaures_rename_tool()
