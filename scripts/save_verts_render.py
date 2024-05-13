import bpy
import csv
import os
from datetime import datetime
from mathutils import Vector

# Define a global resolution
RENDER_RESOLUTION_X = 1024
RENDER_RESOLUTION_Y = 1024

def configure_render_settings():
    bpy.context.scene.render.resolution_x = RENDER_RESOLUTION_X
    bpy.context.scene.render.resolution_y = RENDER_RESOLUTION_Y

def save_viewport_snapshot(file_path):
    configure_render_settings()
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Attempt to render the current viewport to an image and save
    try:
        bpy.context.scene.render.filepath = file_path
        bpy.ops.render.render(write_still=True)
        print(f"Viewport snapshot saved to {file_path}")
    except Exception as e:
        print(f"Failed to save viewport snapshot: {e}")
    
    return bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y

def world_space_to_screen_space(camera, world_point):
    cam_obj = bpy.data.objects[camera]
    scene = bpy.context.scene
    from bpy_extras.object_utils import world_to_camera_view
    co_2d = world_to_camera_view(scene, cam_obj, world_point)
    render_scale = scene.render.resolution_percentage / 100
    render_size = (
        int(RENDER_RESOLUTION_X * render_scale),
        int(RENDER_RESOLUTION_Y * render_scale),
    )
    return (co_2d.x * render_size[0], (1-co_2d.y) * render_size[1])

def is_vertex_visible(camera, world_point, obj):
    cam_obj = bpy.data.objects[camera]
    origin = cam_obj.location
    direction = (world_point - origin).normalized()

    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated_obj = obj.evaluated_get(depsgraph)

    # Perform ray casting
    hit, location, normal, index, hit_obj, matrix = bpy.context.scene.ray_cast(depsgraph, origin, direction)

    # Ensure the hit object is the evaluated version of the original object
    return hit and hit_obj == evaluated_obj

def write_vertices_to_csv(mesh_name, camera_name, file_path, image_path):
    configure_render_settings()
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(file_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Vertex Index', 'World X', 'World Y', 'World Z', 'Screen X', 'Screen Y', 'Visible', 'Width', 'Height', 'ScaleX', 'ScaleY'])

        mesh_obj = bpy.data.objects[mesh_name]
        mesh_data = mesh_obj.data

        for i, v in enumerate(mesh_data.vertices):
            world_co = mesh_obj.matrix_world @ v.co
            screen_pos = world_space_to_screen_space(camera_name, world_co)
            visible = 'Yes' if is_vertex_visible(camera_name, world_co, mesh_obj) else 'No'

            csvwriter.writerow([i, world_co.x, world_co.y, world_co.z, screen_pos[0], screen_pos[1], visible, RENDER_RESOLUTION_X, RENDER_RESOLUTION_Y, 1.0, 1.0])

            if i % 1000 == 0:
                print(i, world_co.x, world_co.y, world_co.z, screen_pos[0], screen_pos[1], visible)

    w, h = save_viewport_snapshot(image_path)
    print(f"Snapshot saved with dimensions {w}x{h}")

# Example usage
mesh_name = bpy.context.selected_objects[0].name
camera_name = 'Camera'
output_directory = r"C:\Users\joeli\Desktop\Data"

# Generate a unique name based on the current time
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
csv_path = os.path.join(output_directory, f"vertices_data_{timestamp}.csv")
image_path = os.path.join(output_directory, f"vertices_data_{timestamp}.png")

if not os.path.exists(output_directory):
    os.makedirs(output_directory)

write_vertices_to_csv(mesh_name, camera_name, csv_path, image_path)

print(f"CSV file path: {csv_path}")
print(f"Image file path: {image_path}")