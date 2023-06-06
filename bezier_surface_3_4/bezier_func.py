# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 21:01:57 2023

@author: Emiliano
"""
import bpy
import numpy as np

def bezierFunc(a0, a1, a2, a3, t):
    return (a0 * (1 - t)**3) + (3 * a1 * t * (1 - t)**2) + (3 * a2 * t**2 * (1 - t)) + (a3 * t**3)

def getCurve(x_params, y_params, t_points, handlers=False):
    coords = []
    
    for t in t_points:
        c_x = bezierFunc(x_params[0], x_params[1], x_params[2], x_params[3], t)
        c_y = bezierFunc(y_params[0], y_params[1], y_params[2], y_params[3], t)
        coords.append([c_x, c_y, 0.0])
        
    verts = []
    edges = []
    
    for i, c in enumerate(coords):
        if i == 0 and handlers:
            verts.append([x_params[1], y_params[1], 0.0])
        elif i == len(coords) - 1 and handlers:
            verts.append([x_params[2], y_params[2], 0.0])
        else:
            verts.append([c[0], c[1], 0.0])
    
    for i in range(len(verts) - 1):
        edges.append([i, i +1])
        
    return (verts, edges)

def renderBlenderData(verts, edges, faces, name, location):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    coll_name = bpy.context.view_layer.active_layer_collection.name
    if coll_name == 'Scene Collection':
        # Attach to Scene Collection
        bpy.context.scene.collection.objects.link(obj)
    else:
        # Get and attach to active collection
        col = bpy.data.collections.get(coll_name)
        col.objects.link(obj)
    
    bpy.context.view_layer.objects.active = obj
    mesh.from_pydata(verts, edges, faces)
    return obj.name

def renderCurve(x, y, t_points):
    verts, edges = getCurve(x, y, t_points, False)
    faces = []
    
    renderBlenderData(verts, edges, faces, "Bezier_Curve")
    
def renderCurves(xs, ys, t_points):
    for x, y in zip(xs, ys):
        renderCurve(x, y, t_points)

def getFaces(max_y, max_x, clockwise=False):
    r_faces = []
    for i in range(1, max_y):
        for j in range(1, max_x):
            l = (max_x * i) + j
            if clockwise:
                r_faces.append([l, l - max_x, l - max_x - 1, l - 1])
            else:
                r_faces.append([l, l - 1, l - max_x - 1, l - max_x])
    return r_faces

""" ----------------------------------------------------- """
def getCurve3D(x_params, y_params, z_params, t_points, handlers=False):
    coords = []
    for t in t_points:
        c_x = bezierFunc(x_params[0], x_params[1], x_params[2], x_params[3], t)
        c_y = bezierFunc(y_params[0], y_params[1], y_params[2], y_params[3], t)
        c_z = bezierFunc(z_params[0], z_params[1], z_params[2], z_params[3], t)
        coords.append([c_x, c_y, c_z])
    verts = []
    edges = []
    for i, c in enumerate(coords):
        if i == 0 and handlers:
            verts.append([x_params[1], y_params[1], z_params[1]])
            verts.append([c[0], c[1], c[2]])
        elif i == len(coords) - 1 and handlers:
            verts.append([c[0], c[1], c[2]])
            verts.append([x_params[2], y_params[2], z_params[2]])
        else:
            verts.append([c[0], c[1], c[2]])
    for i in range(len(verts) - 1):
        edges.append([i, i + 1])
    return (verts, edges)

def getParams(v1, v2, ns, n, coord_xyz):
    params = []
    params.append([v[coord_xyz] for v in v1])
    for i in range(2):
        params.append(np.linspace(ns[0][i + 1], ns[1][i + 1], n))
    params.append([v[coord_xyz] for v in v2])
    return params

def calcInnerVerts(xp, yp, zp, i, t_points):
    x_params = [xp[j][i + 1] for j in range(4)]
    y_params = [yp[j][i + 1] for j in range(4)]
    z_params = [zp[j][i + 1] for j in range(4)]
    o, oe = getCurve3D(x_params, y_params, z_params, t_points)
    o = o[1 : len(o) - 1]
    return [v for v in o]

def bezierSurface(xs, ys, zs, t_points, location):
    x1 = [xs[0], xs[1]]
    y1 = [ys[0], ys[1]]
    z1 = [zs[0], zs[1]]
    x2 = [xs[2], xs[3]]
    y2 = [ys[2], ys[3]]
    z2 = [zs[2], zs[3]]

    n = len(t_points)

    verts1, edges1 = getCurve3D(x1[0], y1[0], z1[0], t_points)
    verts2, edges2 = getCurve3D(x1[1], y1[1], z1[1], t_points)
    verts3, edges3 = getCurve3D(x2[0], y2[0], z2[0], t_points)
    verts4, edges4 = getCurve3D(x2[1], y2[1], z2[1], t_points)

    verts1.reverse()
    verts4.reverse()

    f_verts = []
    for v in range(len(verts1) - 1):
        f_verts.append(verts1[v])
    for v in range(len(verts3) - 1):
        f_verts.append(verts3[v])
    for v in range(len(verts2) - 1):
        f_verts.append(verts2[v])
    for v in range(len(verts4) - 1):
        f_verts.append(verts4[v])

    verts4.reverse()
    x1p = getParams(verts3, verts4, x1, n, 0)
    y1p = getParams(verts3, verts4, y1, n, 1)
    z1p = getParams(verts3, verts4, z1, n, 2)

    inner_p = []
    for i in range(n - 2):
        inner_p.append(calcInnerVerts(x1p, y1p, z1p, i, t_points))

    inner_verts = []
    for i in range(n - 2):
        for j in range(n - 2):
            inner_verts.append([inner_p[i][j][0], inner_p[i][j][1], inner_p[i][j][2]])

    r_verts = []

    for i in range(n):
        for j in range(n):
            if i == 0:
                r_verts.append(f_verts[n - 1 - j])
            elif i == n - 1:
                r_verts.append(f_verts[((n - 1) * 2) + j])
            else:
                if j == 0:
                    r_verts.append(f_verts[n - 1 + i])
                elif j == n - 1:
                    r_verts.append(f_verts[len(f_verts) - i])
                else:
                    r_verts.append(inner_verts[((n - 2) * (i - 1)) + (j - 1)])
    
    """ Calculate faces and render mesh """
    r_faces = getFaces(n, n, False)
    
    s_name = renderBlenderData(r_verts, [], r_faces, "Surface", location)
    return s_name

def createBorder():
    bpy.ops.curve.primitive_bezier_curve_add()
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.curve.switch_direction()
    bpy.ops.curve.handle_type_set(type='FREE_ALIGN')
    bpy.ops.transform.translate(value=(0, -1.0, 0))
    bpy.ops.curve.extrude_move(TRANSFORM_OT_translate={"value":(0, 2.0, 0)})
    bpy.ops.curve.select_all(action='SELECT')
    bpy.ops.curve.make_segment()
    
    obj = bpy.context.active_object

    # Move handlers to a default position
    
    p = bpy.data.curves[obj.data.name].splines[0].bezier_points
    
    p[1].handle_right = (p[1].co[0] - 0.5, p[1].co[1] + 0.5, p[1].co[2])
    p[1].handle_left = (p[1].co[0], p[1].co[1] - 0.7, p[1].co[2])

    p[0].handle_right = (p[0].co[0] + 0.5, p[0].co[1] + 0.5, p[0].co[2])
    p[0].handle_left = (p[0].co[0] - 0.7, p[0].co[1], p[0].co[2])

    p[3].handle_right = (p[3].co[0] + 0.5, p[3].co[1] + 0.5, p[3].co[2])
    p[3].handle_left = (p[3].co[0], p[3].co[1] + 0.7, p[3].co[2])

    p[2].handle_right = (p[2].co[0] + 0.5, p[2].co[1] - 0.5, p[2].co[2])
    p[2].handle_left = (p[2].co[0] + 0.7, p[2].co[1], p[2].co[2])

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
    return obj.name