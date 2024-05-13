import bpy
import mathutils
import os
import random

# Function to add a camera
def add_camera(location, rotation):
    bpy.ops.object.camera_add(location=location, rotation=rotation)
    return bpy.context.object

# Function to make an object look at a specific point
def look_at(obj, target):
    direction = target - obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    obj.rotation_euler = rot_quat.to_euler()

# Function to extract vertices from a mesh object
def get_vertices_from_mesh(mesh_obj):
    return [mesh_obj.matrix_world @ vert.co for vert in mesh_obj.data.vertices]

# Function to render views from the vertices on the mesh
def render_camera_from_vertices(camera, vertices, subject):
    for index, point in enumerate(vertices):
        camera.location = point
        look_at(camera, subject)
        bpy.context.view_layer.update()
        # Render each view and save
        output_path = os.path.join(output_dir, f'view_{index:03}.png')
        bpy.context.scene.render.filepath = output_path
        bpy.ops.render.render(write_still=True)
# Clear existing cameras
for obj in bpy.data.objects:
    if obj.type == 'CAMERA':
        obj.select_set(True)
    else:
        obj.select_set(False)
bpy.ops.object.delete()
# Add a new camera and set it as the active camera
camera = add_camera((0, -10, 10), (0, 0, 0))
bpy.context.scene.camera = camera

# Retrieve the hemisphere mesh
hemisphere_mesh_name = "Hemisphere"  # Update this to the name of your hemisphere mesh
hemisphere_mesh = bpy.data.objects.get(hemisphere_mesh_name)

if hemisphere_mesh is None:
    raise ValueError(f"Mesh object named '{hemisphere_mesh_name}' not found. Make sure you have a mesh with this name.")

# Extract vertices
vertices = get_vertices_from_mesh(hemisphere_mesh)

# Retrieve the target object named "HG_Eyes"
subject_name = "Hemisphere"
subject_obj = bpy.data.objects.get(subject_name)

if subject_obj is None:
    raise ValueError(f"Object named '{subject_name}' not found. Make sure you have an object with this name.")
else:
    subject = subject_obj.location

# Set rendering engine to Cycles and enable GPU
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'GPU'

# Ensure GPU is enabled
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'CUDA'  # or 'OPENCL'
prefs.get_devices()
for device in prefs.devices:
    device.use = True

# Set up output directory and ensure it exists
output_dir = r'C:\Desktop\SDPL\render_test'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Set output settings
bpy.context.scene.render.filepath = output_dir
bpy.context.scene.render.filepath = output_dir
bpy.context.scene.render.resolution_x = 512
bpy.context.scene.render.resolution_y = 512
bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.cycles.samples = 64  # Reduce sample count for faster rendering


# Select 3 random vertices
random_vertices = random.sample(vertices, 3)

# Render the camera views using the random vertices from the hemisphere mesh
render_camera_from_vertices(camera, random_vertices, subject)
