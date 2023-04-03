# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 23:05:56 2023

@author: Emiliano
"""

bl_info = {
    "name": "Bezier Surface",
    "author": "Milla, Emiliano",
    "version": (1, 0),
    "blender": (3, 4, 1),
    "location": "View3D > Add > Mesh > New Object",
    "description": "Creates a closed border,"
    "then a surface could be created from that border",
    "category": "Add Mesh",
    }

if "bpy" in locals():
    import importlib
    importlib.reload(bezier_func)
    
else:
    from . import bezier_func

import bpy
from bpy.types import Operator
from bpy_extras.object_utils import AddObjectHelper
import numpy as np

# Add mesh

def add_object():
    bezier_func.createBorder()

class OBJECT_OT_add_object(Operator, AddObjectHelper):
    """Create the border of a surface"""
    bl_idname = "mesh.create_border"
    bl_label = "Create Border"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_object()
        return {'FINISHED'}

def recalculatePoints(p, mw, loc):
    for i in range(len(p)):
        v_local_co = p[i].co
        v_global_co = (mw @ v_local_co) - loc
        v_local_hl = p[i].handle_left
        v_global_hl = (mw @ v_local_hl) - loc
        v_local_hr = p[i].handle_right
        v_global_hr = (mw @ v_local_hr) - loc
        
        p[i].co = v_global_co
        p[i].handle_left = v_global_hl
        p[i].handle_right = v_global_hr
        
    return p

def main(self, obj, context):
    # Get reference points and handlers
    p = bpy.data.curves[obj.data.name].splines[0].bezier_points
    n = self.steps
    # Copy original values
    # Note for future versions: use a class
    co_cpy = []
    hl_cpy = []
    hr_cpy = []
    
    for i in range(len(p)):
        co_cpy.append([c for c in p[i].co])
        hl_cpy.append([c for c in p[i].handle_left])
        hr_cpy.append([c for c in p[i].handle_right])
    
    # Recalculate vertex coordinates using global matrix
    mw = obj.matrix_world
    p = recalculatePoints(p, mw, obj.location)
    
    # Create array of params for surface
    x01 = [p[3].co[0], p[3].handle_right[0], p[0].handle_left[0], p[0].co[0]]
    y01 = [p[3].co[1], p[3].handle_right[1], p[0].handle_left[1], p[0].co[1]]
    z01 = [p[3].co[2], p[3].handle_right[2], p[0].handle_left[2], p[0].co[2]]

    x23 = [p[2].co[0], p[2].handle_left[0], p[1].handle_right[0], p[1].co[0]]
    y23 = [p[2].co[1], p[2].handle_left[1], p[1].handle_right[1], p[1].co[1]]
    z23 = [p[2].co[2], p[2].handle_left[2], p[1].handle_right[2], p[1].co[2]]

    x45 = [p[3].co[0], p[3].handle_left[0], p[2].handle_right[0], p[2].co[0]]
    y45 = [p[3].co[1], p[3].handle_left[1], p[2].handle_right[1], p[2].co[1]]
    z45 = [p[3].co[2], p[3].handle_left[2], p[2].handle_right[2], p[2].co[2]]

    x67 = [p[0].co[0], p[0].handle_right[0], p[1].handle_left[0], p[1].co[0]]
    y67 = [p[0].co[1], p[0].handle_right[1], p[1].handle_left[1], p[1].co[1]]
    z67 = [p[0].co[2], p[0].handle_right[2], p[1].handle_left[2], p[1].co[2]]

    x = [x01, x23, x45, x67]
    y = [y01, y23, y45, y67]
    z = [z01, z23, z45, z67]

    t_points = np.linspace(0.0, 1.0, n)
    # Call the function that creates the surface
    s_name = bezier_func.bezierSurface(x, y, z, t_points, obj.location)
    
    # Delete the border.
    # Note for future version: make this steps optional if user wants to
    # preserve the border
    
    # Recover previous values
    for i in range(len(p)):
        p[i].co = co_cpy[i]
        p[i].handle_left = hl_cpy[i]
        p[i].handle_right = hr_cpy[i]
    
    #obj.select_set(True)
    #bpy.ops.object.delete(use_global=False)
    context.view_layer.objects.active = bpy.data.objects[s_name]
    bpy.data.objects[s_name].select_set(True)

def borderCheck(obj):
    """
    Only apply the operator when the object is a CURVE,
    with only 1 spline,
    and 4 bezier_points
    """
    if obj.type == 'CURVE':
        p = len(bpy.data.curves[obj.data.name].splines[0].bezier_points)
        s = len(bpy.data.curves[obj.data.name].splines)
        if s == 1 and p == 4:
            return True
        
    return False

class BezierSurface(bpy.types.Operator):
    """Bezier Surface"""
    bl_idname = "object.bezier_surface"
    bl_label = "Bezier Surface"
    bl_options = {'REGISTER', 'UNDO'}

    steps: bpy.props.IntProperty(name="Steps", default=10, min=3, max=100)

    def execute(self, context):
        obj = bpy.context.active_object
        if borderCheck(obj):
            main(self, obj, context)
        
        return {'FINISHED'}

class OBJECT_PT_bezier_surface(bpy.types.Panel):
    bl_idname = "OBJECT_PT_bezier_surface"
    bl_label = "Bezier Surface"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"

    def draw(self, context):
        props = self.layout.operator('object.bezier_surface')
        props.steps = 10


def menu_func(self, context):
    if borderCheck(context.active_object):
        self.layout.operator(BezierSurface.bl_idname)

# Registration

def add_object_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_object.bl_idname,
        text="Surface Border",
        icon='OUTLINER_OB_LATTICE')

def register():
    bpy.utils.register_class(OBJECT_OT_add_object)
    bpy.types.VIEW3D_MT_mesh_add.append(add_object_button)
    bpy.utils.register_class(BezierSurface)
    bpy.types.VIEW3D_MT_object.append(menu_func)
    bpy.utils.register_class(OBJECT_PT_bezier_surface)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_object)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_object_button)
    bpy.utils.unregister_class(BezierSurface)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    bpy.utils.unregister_class(OBJECT_PT_bezier_surface)


if __name__ == "__main__":
    register()
        
    

