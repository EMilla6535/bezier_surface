# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 23:05:56 2023

@author: Emiliano
"""

bl_info = {
    "name": "Bezier Surface",
    "author": "Milla, Emiliano",
    "version": (1, 0),
    "blender": (2, 75, 0),
    "location": "View3D > Add > Mesh > New Object",
    "description": "Creates a closed border,"
    "then it could be created a surface of that border",
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

# Operator

def main(self, obj, context):
    # Obtener los puntos de referencia y handlers
    p = bpy.data.curves[obj.name].splines[0].bezier_points
    n = self.steps
    # Crear los arreglos de parametros para la superficie
    x01 = [p[2].co[0], p[2].handle_left[0], p[1].handle_right[0], p[1].co[0]]
    y01 = [p[2].co[1], p[2].handle_left[1], p[1].handle_right[1], p[1].co[1]]
    z01 = [p[2].co[2], p[2].handle_left[2], p[1].handle_right[2], p[1].co[2]]

    x23 = [p[3].co[0], p[3].handle_right[0], p[0].handle_left[0], p[0].co[0]]
    y23 = [p[3].co[1], p[3].handle_right[1], p[0].handle_left[1], p[0].co[1]]
    z23 = [p[3].co[2], p[3].handle_right[2], p[0].handle_left[2], p[0].co[2]]

    x45 = [p[2].co[0], p[2].handle_right[0], p[3].handle_left[0], p[3].co[0]]
    y45 = [p[2].co[1], p[2].handle_right[1], p[3].handle_left[1], p[3].co[1]]
    z45 = [p[2].co[2], p[2].handle_right[2], p[3].handle_left[2], p[3].co[2]]

    x67 = [p[1].co[0], p[1].handle_left[0], p[0].handle_right[0], p[0].co[0]]
    y67 = [p[1].co[1], p[1].handle_left[1], p[0].handle_right[1], p[0].co[1]]
    z67 = [p[1].co[2], p[1].handle_left[2], p[0].handle_right[2], p[0].co[2]]

    x = [x01, x23, x45, x67]
    y = [y01, y23, y45, y67]
    z = [z01, z23, z45, z67]

    t_points = np.linspace(0.0, 1.0, n)
    # Llamar a la funcion
    s_name = bezier_func.bezierSurface(x, y, z, t_points, obj.location)
    obj.select = True
    bpy.ops.object.delete(use_global=False)
    context.scene.objects.active = bpy.data.objects[s_name]
    bpy.data.objects[s_name].select = True

def borderCheck(obj):
    if obj.type == 'CURVE':
        p = bpy.data.curves[obj.name].splines[0].bezier_points
        if len(p) == 4:
            return True
        
    return False

class BezierSurface(bpy.types.Operator):
    """Bezier Surface"""
    bl_idname = "object.bezier_surface"
    bl_label = "Bezier Surface"
    bl_options = {'REGISTER', 'UNDO'}

    steps = bpy.props.IntProperty(name="Steps", default=10, min=3, max=100)

    def execute(self, context):
        scene = context.scene
        obj = scene.objects.active
        if borderCheck(obj):
            main(self, obj, context)
        
        return {'FINISHED'}

def menu_func(self, context):
    if borderCheck(context.scene.objects.active):
        self.layout.operator(BezierSurface.bl_idname)

# Registration

def add_object_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_object.bl_idname,
        text="Surface Border",
        icon='OUTLINER_OB_LATTICE')

def register():
    bpy.utils.register_class(OBJECT_OT_add_object)
    bpy.types.INFO_MT_mesh_add.append(add_object_button)
    bpy.utils.register_class(BezierSurface)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_object)
    bpy.types.INFO_MT_mesh_add.remove(add_object_button)
    bpy.utils.unregister_class(BezierSurface)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()
        
    

