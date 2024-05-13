import bpy
import mathutils
import os
import csv
import random
from math import radians
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
import datetime

# Constants
HEMISPHERE_MESH_NAME = "Hemisphere"
TARGET_OBJECT_NAME = "HG_Body"
CAMERA_NAME = "Render_Camera"
VERTEX_GROUP_NAME = "Head"
OUTPUT_DIR = r'C:\Desktop\SDPL\generated_data\Jane'
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
OUTPUT_DIR = os.path.join(OUTPUT_DIR, timestamp)
HDRI_DIR = r'C:\Desktop\SDPL\hdris'
NUM_RANDOM_VERTICES = 7
CACHE_FILE = os.path.join(OUTPUT_DIR, 'render_cache.txt')

# Functions
def set_random_hdri(hdri_directory):
    """Set a random HDRI from a specified directory as the world background."""
    if not os.path.exists(hdri_directory) or not os.path.isdir(hdri_directory):
        raise ValueError(f"Invalid directory: {hdri_directory}")

    # Filter for HDRI files (assuming HDRIs are in EXR, HDR, or other standard formats)
    valid_extensions = {'.hdr', '.exr', '.png'}
    hdri_files = [f for f in os.listdir(hdri_directory) if os.path.splitext(f)[1].lower() in valid_extensions]

    if not hdri_files:
        raise ValueError(f"No valid HDRI files found in directory: {hdri_directory}")

    # Select a random HDRI file
    selected_hdri = random.choice(hdri_files)
    hdri_path = os.path.join(hdri_directory, selected_hdri)

    # Enable 'Use Nodes' for the World
    world = bpy.context.scene.world
    if not world.use_nodes:
        world.use_nodes = True

    # Set up the HDRI as the world background
    nodes = world.node_tree.nodes
    links = world.node_tree.links

    # Clear existing nodes except the output node
    for node in nodes:
        if node.type != 'OUTPUT_WORLD':
            nodes.remove(node)

    # Add new Environment Texture node
    env_tex_node = nodes.new(type='ShaderNodeTexEnvironment')
    env_tex_node.image = bpy.data.images.load(hdri_path)
    env_tex_node.location = (-300, 0)

    # Find the World Output node and add Background node
    output_node = next(node for node in nodes if node.type == 'OUTPUT_WORLD')
    background_node = nodes.new(type='ShaderNodeBackground')
    background_node.location = (-150, 0)
    
    background_strength = random.uniform(0.12, 1)
    background_node.inputs[1].default_value = background_strength
    # Link nodes
    links.new(env_tex_node.outputs['Color'], background_node.inputs['Color'])
    links.new(background_node.outputs['Background'], output_node.inputs['Surface'])

    print(f"Applied HDRI: {hdri_path}, strength: {background_strength}")

def add_camera(location, rotation):
    """Add a camera at a specified location and rotation."""
    bpy.ops.object.camera_add(location=location, rotation=rotation)
    return bpy.context.object

def look_at(obj, target):
    obj = bpy.data.objects.get(HEMISPHERE_MESH_NAME)
    """Make an object look at a specific target point with a baseline X rotation of 90 degrees."""
    direction = target - obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    adjusted_rotation = rot_quat.to_euler()
    adjusted_rotation.x += radians(90)  # Add 90 degrees to the X rotation
    obj.rotation_euler = adjusted_rotation
    #add -1 to y location to make the camera look at the center of the object
    obj.location.y -= 1

def get_vertices_from_mesh(mesh_obj):
    """Extract vertices from a mesh object."""
    return [mesh_obj.matrix_world @ vert.co for vert in mesh_obj.data.vertices]

def world_space_to_screen_space(camera_name, world_point):
    """Convert world space coordinates to screen space coordinates."""
    cam_obj = bpy.data.objects.get(camera_name)
    scene = bpy.context.scene

    if not cam_obj or cam_obj.type != 'CAMERA':
        raise ValueError(f"Camera '{camera_name}' not found or is not a valid camera object.")

    try:
        co_2d = world_to_camera_view(scene, cam_obj, world_point)
    except Exception as e:
        print(f"Error calculating screen coordinates for {world_point}: {e}")
        return (0, 0)

    render_scale = scene.render.resolution_percentage / 100
    render_size = (
        int(scene.render.resolution_x * render_scale),
        int(scene.render.resolution_y * render_scale),
    )
    return (co_2d.x * render_size[0], (1 - co_2d.y) * render_size[1])

def vertex_visibility(scene, cam, mesh_obj, vertex):
    """Check if a vertex is visible from the camera."""
    mat_world = mesh_obj.matrix_world
    co_world = mat_world @ vertex.co
    co_ndc = world_to_camera_view(scene, cam, co_world)

    if not (0.0 < co_ndc.x < 1.0 and 0.0 < co_ndc.y < 1.0 and cam.data.clip_start < co_ndc.z < cam.data.clip_end):
        return False

    direction = (co_world - cam.location).normalized()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    result, location, _, _, _, _ = scene.ray_cast(depsgraph, cam.location, direction)

    return not result or (location - co_world).length < 0.01

def write_vertices_to_csv(mesh_obj, vertex_group_name, camera_name, file_path):
    """Write vertices data to a CSV file."""
    scene = bpy.context.scene
    camera_obj = bpy.data.objects.get(camera_name)

    with open(file_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Vertex Index', 'World X', 'World Y', 'World Z', 'Screen X', 'Screen Y', 'Visible', 'Width', 'Height', 'ScaleX', 'ScaleY'])

        if isinstance(mesh_obj, bpy.types.Object) and mesh_obj.type == 'MESH':
            mesh_data = mesh_obj.data
        else:
            print("Error: Provided mesh object is not a valid mesh")
            return

        if vertex_group_name not in mesh_obj.vertex_groups:
            print(f"Error: Vertex group '{vertex_group_name}' not found in mesh '{mesh_obj.name}'")
            return

        vertex_group = mesh_obj.vertex_groups[vertex_group_name]

        for i, vert in enumerate(mesh_data.vertices):
            for group in vert.groups:
                if group.group == vertex_group.index:
                    world_co = mesh_obj.matrix_world @ vert.co
                    screen_pos = world_space_to_screen_space(camera_name, world_co)
                    visible = vertex_visibility(scene, camera_obj, mesh_obj, vert)
                    visibility_text = 'Yes' if visible else 'No'

                    csvwriter.writerow([i, world_co.x, world_co.y, world_co.z, screen_pos[0], screen_pos[1], visibility_text, scene.render.resolution_x, scene.render.resolution_y, 1.0, 1.0])

                    if i % 1000 == 0:
                        print(f"Vertex {i}: ({world_co.x}, {world_co.y}, {world_co.z})")

def render_camera_from_vertices(camera, vertices, cursor_location, mesh_obj, vertex_group_name, target_obj, start_index=0):
    """Render views from the vertices on the mesh and save each with corresponding CSV."""
    for index in range(start_index, len(vertices)):
        set_random_hdri(HDRI_DIR)
        camera.location = vertices[index]
        look_at(camera, cursor_location)
        bpy.context.view_layer.update()
        output_image = os.path.join(OUTPUT_DIR, f'view_{index:03}.png')
        output_csv = os.path.join(OUTPUT_DIR, f'view_{index:03}.csv')
        bpy.context.scene.render.filepath = output_image
        bpy.ops.render.render(write_still=True)
        write_vertices_to_csv(target_obj, vertex_group_name, camera.name, output_csv)

        # Update cache file after each render
        with open(CACHE_FILE, 'w') as file:
            file.write(str(index + 1))

# Main execution flow
def main():
    # Ensure output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Initialize camera
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='CAMERA')
    bpy.ops.object.delete()

    camera = add_camera((0, -10, 10), (0, 0, 0))
    camera.name = CAMERA_NAME
    bpy.context.scene.camera = camera

    hemisphere_mesh = bpy.data.objects.get(HEMISPHERE_MESH_NAME)
    vertices = get_vertices_from_mesh(hemisphere_mesh)

    target_obj = bpy.data.objects.get(HEMISPHERE_MESH_NAME)
    cursor_location = bpy.context.scene.cursor.location

    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU'
    bpy.context.preferences.addons['cycles'].preferences.get_devices()
    for device in bpy.context.preferences.addons['cycles'].preferences.devices:
        device.use = True

    bpy.context.scene.render.resolution_x = 512
    bpy.context.scene.render.resolution_y = 512
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.cycles.samples = 128

    # Resume rendering from cache
    start_index = 0
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as file:
            try:
                start_index = int(file.read())
            except ValueError:
                start_index = 0

    random_vertices = random.sample(vertices, NUM_RANDOM_VERTICES)
    render_camera_from_vertices(camera, random_vertices, cursor_location, hemisphere_mesh, VERTEX_GROUP_NAME, target_obj, start_index)

# Run the main function
main()
