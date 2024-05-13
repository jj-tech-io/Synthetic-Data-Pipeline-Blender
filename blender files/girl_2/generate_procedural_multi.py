import bpy
import csv
import os
import datetime
import bpy
import csv
import os
import bpy
import os
from math import radians

import bpy
import bmesh
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
# Setup function to apply camera transforms and render images
def setup_and_render(camera, transform, file_path):
    # Set the render engine to Cycles
    bpy.context.scene.render.engine = 'CYCLES'
    
    # Get current viewport dimensions (or set to a fixed size if the context is not available)
    viewport_width = 1024  # Example width, replace with bpy.context.area.width if available
    viewport_height = 1024  # Example height, replace with bpy.context.area.height if available

    # Apply camera transforms
    camera.location = transform['location']
    camera.rotation_euler = (radians(transform['rotation_euler'][0]), 
                             radians(transform['rotation_euler'][1]), 
                             radians(transform['rotation_euler'][2]))
    camera.scale = transform['scale']
    
    # Set render dimensions to match the viewport
    bpy.context.scene.render.resolution_x = viewport_width
    bpy.context.scene.render.resolution_y = viewport_height
    bpy.context.scene.render.resolution_percentage = 100  # Render at 100% scale

    # Set the filepath for the render output
    bpy.context.scene.render.filepath = file_path
    
    # Render the scene
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {file_path}")
def save_viewport_snapshot(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    w = bpy.context.scene.render.resolution_x
    h = bpy.context.scene.render.resolution_y
    try:
        bpy.context.scene.render.filepath = file_path
        bpy.ops.render.opengl(write_still=True)
        print(f"Viewport snapshot saved to {file_path}")
    except Exception as e:
        print(f"Failed to save viewport snapshot: {e}")
    return w, h
camera_transforms = [
    {'location': (-0.019242, -0.75185, 1.0297), 'rotation_euler': (128.4, 0.00011, -1.9469), 'scale': (1.0, 1.0, 1.0)},
    {'location': (-0.005842, -0.93112, 1.3933), 'rotation_euler': (104, 0.00013, -0.7469), 'scale': (1.0, 1.0, 1.0)},
    {'location': (-0.032472, -0.94656, 1.7786), 'rotation_euler': (80.8, 0.00012, -2.3469), 'scale': (1.0, 1.0, 1.0)},
    {'location': (-0.023739, -0.62667, 2.3511), 'rotation_euler': (40.8, 0.00008, -2.7469), 'scale': (1.0, 1.0, 1.0)},
    {'location': (-0.65528, -0.45476, 2.1503), 'rotation_euler': (56.8, -0.00005, -55.547), 'scale': (1.0, 1.0, 1.0)},
    {'location': (0.44261, -0.68701, 2.1334), 'rotation_euler': (58, -0.00019, 32.453), 'scale': (1.0, 1.0, 1.0)},
    {'location': (0.42679, -0.57038, 0.97878), 'rotation_euler': (132.4, -0.00009, 36.453), 'scale': (1.0, 1.0, 1.0)},
    {'location': (0.15224, -0.68441, 0.96895), 'rotation_euler': (133.2, -0.00017, 12.053), 'scale': (1.0, 1.0, 1.0)},
    {'location': (-0.17866, -0.79268, 1.1172), 'rotation_euler': (122, -0.00015, -13.147), 'scale': (1.0, 1.0, 1.0)},
    {'location': (-0.63588, -0.53288, 1.1517), 'rotation_euler': (119.6, -0.0001, -50.347), 'scale': (1.0, 1.0, 1.0)},
    {'location': (0.89553, -0.008057, 1.6829), 'rotation_euler': (84.8, -0.00025, 89.653), 'scale': (1.0, 1.0, 1.0)},
    {'location': (-0.8506, -0.3017, 1.3163), 'rotation_euler': (108.8, -0.0001, -70.747), 'scale': (1.0, 1.0, 1.0)},
    {'location': (-0.92812, -0.20723, 1.6855), 'rotation_euler': (86.4, 0.00012, -77.547), 'scale': (1.0, 1.0, 1.0)},
    {'location': (-0.82973, -0.46913, 1.6588), 'rotation_euler': (88, -0.00006, -60.747), 'scale': (1.0, 1.0, 1.0)},
    {'location': (-0.65808, -0.69013, 1.6788), 'rotation_euler': (86.8, -0.00033, -43.947), 'scale': (1.0, 1.0, 1.0)},
    {'location': (-0.39445, -0.87027, 1.6788), 'rotation_euler': (86.8, -0.00042, -24.747), 'scale': (1.0, 1.0, 1.0)},
    {'location': (-0.06175, -0.95678, 1.6989), 'rotation_euler': (85.6, -0.00014, -0.74681), 'scale': (1.0, 1.0, 1.0)},
    {'location': (0.86293, -0.25193, 1.6762), 'rotation_euler': (85.2, -0.00019, 74.853), 'scale': (1.0, 1.0, 1.0)}

]

# Create a directory for rendered images if it doesn't exist
output_directory = "C:\\Desktop\\Rendered_Images_CSV"
os.makedirs(output_directory, exist_ok=True)

# Assuming 'Camera' is the object you want to manipulate
camera = bpy.data.objects.get('Camera')
if camera:
    for i, transform in enumerate(camera_transforms):
        file_path = os.path.join(output_directory, f"Render_{i}.png")
        setup_and_render(camera, transform, file_path)
        print(f"Saved render at {file_path}")
else:
    print("Camera object not found")