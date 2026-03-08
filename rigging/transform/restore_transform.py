# -*- coding: utf-8 -*-
""" Function to restore transform of a node

This file provides function to restore transformations of a mesh in maya.

Author: Clement Daures
Created: 2023

# ---------- LICENSE ----------

MIT License

Copyright (c) 2023 Clement Daures

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import maya.cmds as cmds

def restore_transform_verif():
    """Check if user selected a face using verify_face_selection() and return a message"""
    #Condition face selected
    if verify_face_selection():
        restore_transform()
    else :
        print("No face selected, please select at least one face")

def verify_face_selection():
    """Verify if at least one face have been selected"""
    # Get selected objects
    selected_objects = cmds.ls(selection=True, flatten=True)
    
    # Check if any selected object is a mesh and has face components
    for obj in selected_objects:
        if cmds.objectType(obj) == "mesh" and cmds.filterExpand(obj, selectionMask=34):  # 34 represents face component type
            return True
    
    return False

def restore_transform():
    """Restore Transformations: Restores the transformations to their original state before freezing"""
    
    # Create lists
    del_uv = []
    projection = []
    obj_1 = []
    targets = cmds.ls(sl=True) 
    obj_2 = cmds.ls(sl=True, type="transform")
    locator = "z_locator"
    
    # Exclude objects of type 'transform' from component selection
    targets = list(set(targets) - set(obj_2))
    
    for target in targets:
        obj_1.append(target.split('.')[0])

    cmds.constructionHistory(toggle=True)

    if not cmds.objExists(locator):
        cmds.spaceLocator(n=locator, p=(0, 0, 0))
    
    # Process component-selected objects
    if obj_1:
        for i in range(len(obj_1)):
            # Snap locator to selected object
            cmds.makeIdentity(obj_1[i], apply=True, t=True, r=True, s=True, n=False)
            del_uv.append(cmds.polyMapDel(obj_1[i], ch=True))
            cmds.select(targets[i])
            projection.append(cmds.polyProjection(ch=True, type="Planar", ibd=True, kir=True, md="b"))
            cmds.select(targets[i], locator)
            cmds.pointOnPolyConstraint(targets[i], locator, maintainOffset=False)
            cmds.delete(cmds.listRelatives(locator, typ="constraint"))
            cmds.setAttr(f"{locator}.rotateX", cmds.getAttr(f"{locator}.rotateX") - 90)
            
            # Snap locator to selected object's pivot
            pivot = cmds.xform(obj_1[i], q=True, rp=True)
            cmds.move(pivot[0], pivot[1], pivot[2], locator, rpr=True)
            
            # Snap object to world origin
            translate = cmds.getAttr(f"{locator}.translate")[0]
            rotate = cmds.getAttr(f"{locator}.rotate")[0]
            cmds.parentConstraint(locator, obj_1[i], mo=True, w=1)
            cmds.move(0, 0, 0, locator, a=True)
            cmds.rotate(0, 0, 0, locator, a=True)
            
            # Restore object's transform
            cmds.select(obj_1[i])
            cmds.delete(cmds.listRelatives(obj_1[i], typ="constraint"))
            cmds.makeIdentity(obj_1[i], apply=True, t=True, r=True, s=True, n=False)
            cmds.move(translate[0], translate[1], translate[2], obj_1[i], a=True)
            cmds.rotate(rotate[0], rotate[1], rotate[2], obj_1[i], a=True)
        
        # Clean up data
        flat_projection = [item for sublist in projection for item in sublist]
        flat_del_uv = [item for sublist in del_uv for item in sublist]
        cmds.delete(flat_projection)
        cmds.delete(flat_del_uv)
        cmds.delete(obj_1, ch=True)

    # Process transform-selected objects
    if obj_2:
        for obj in obj_2:
            cmds.makeIdentity(obj, apply=True, t=True, r=True, s=True, n=False)
            cmds.select(obj, locator)
            cmds.delete(cmds.pointConstraint(locator, obj, offset=[0, 0, 0], weight=1))
            cmds.move(0, 0, 0, obj, rpr=True)
            cmds.makeIdentity(obj, apply=True, t=True, r=True, s=True, n=False)
            cmds.select(locator, obj)
            cmds.delete(cmds.pointConstraint(locator, obj, offset=[0, 0, 0], weight=1))

    cmds.delete(locator)

if __name__=="__main__":
    restore_transform()

