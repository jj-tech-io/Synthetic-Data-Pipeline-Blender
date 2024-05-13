import bpy
import os
import csv
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

# Convert world space coordinates to screen space coordinates
def world_space_to_screen_space(camera_name, world_point):
    cam_obj = bpy.data.objects[camera_name]
    scene = bpy.context.scene
    co_2d = world_to_camera_view(scene, cam_obj, world_point)
    render_scale = scene.render.resolution_percentage / 100
    render_size = (
        int(scene.render.resolution_x * render_scale),
        int(scene.render.resolution_y * render_scale),
    )
    return (co_2d.x * render_size[0], (1 - co_2d.y) * render_size[1])

# Check if a vertex is visible from the camera
def vertex_visibility(scene, cam, mesh_obj, vertex):
    mat_world = mesh_obj.matrix_world
    co_world = mat_world @ vertex.co
    co_ndc = world_to_camera_view(scene, cam, co_world)

    if not (0.0 < co_ndc.x < 1.0 and 0.0 < co_ndc.y < 1.0 and cam.data.clip_start < co_ndc.z < cam.data.clip_end):
        return False

    direction = (co_world - cam.location).normalized()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    result, location, _, _, _, _ = scene.ray_cast(depsgraph, cam.location, direction)

    return not result or (location - co_world).length < 0.0001

# Write vertices data to a CSV file
def write_vertices_to_csv(mesh_obj, vertex_group_name, camera_name, file_path):
    scene = bpy.context.scene
    camera_obj = bpy.data.objects[camera_name]

    with open(file_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Vertex Index', 'World X', 'World Y', 'World Z', 'Screen X', 'Screen Y', 'Visible', 'Width', 'Height', 'ScaleX', 'ScaleY'])

        if isinstance(mesh_obj, bpy.types.Object) and mesh_obj.type == 'MESH':
            mesh_data = mesh_obj.data
        else:
            print("Error: Provided mesh object is not a valid mesh")
            return

        # Ensure the vertex group exists
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
                        print(i, world_co.x, world_co.y, world_co.z, screen_pos[0], screen_pos[1], visibility_text)

# Render the scene and save vertex data
def render_and_save(camera_name, vertex_group_name, output_dir):
    # Check if the camera exists
    camera_obj = bpy.data.objects.get(camera_name)
    if not camera_obj:
        print(f"Error: Camera '{camera_name}' not found")
        return

    bpy.context.scene.camera = camera_obj
    print(f"Switched to camera: {camera_name}")

    # Retrieve the mesh object and ensure it exists
    mesh_obj = bpy.context.view_layer.objects.active
    if mesh_obj is None or mesh_obj.type != 'MESH':
        print("Error: No mesh object selected")
        return

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Render the image
    img_output_path = os.path.join(output_dir, f'{camera_name}_{vertex_group_name}.png')
    bpy.context.scene.render.filepath = img_output_path
    bpy.ops.render.render(write_still=True)

    # Write vertices data to CSV
    csv_output_path = os.path.join(output_dir, f'{camera_name}_{vertex_group_name}.csv')
    write_vertices_to_csv(mesh_obj, vertex_group_name, camera_name, csv_output_path)

# Example usage
camera_name = "Camera"  # Replace with your actual camera name
vertex_group_name = "Head"  # Replace with your actual vertex group name
output_dir = r'C:\Desktop\SDPL\render_test'

render_and_save(camera_name, vertex_group_name, output_dir)
