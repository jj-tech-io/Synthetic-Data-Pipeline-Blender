import bpy
import csv
import os

def set_fixed_vray_render_resolution(width=None, height=None):
    bpy.context.scene.render.resolution_x = width
    bpy.context.scene.render.resolution_y = height
    print(f"V-Ray render resolution set to: {width}x{height}")

def save_viewport_snapshot(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    w = bpy.context.scene.render.resolution_x
    h = bpy.context.scene.render.resolution_y

    # Attempt to render the current viewport to an image and save
    try:
        bpy.context.scene.render.filepath = file_path
        bpy.ops.render.opengl(write_still=True)
        print(f"Viewport snapshot saved to {file_path}")
    except Exception as e:
        print(f"Failed to save viewport snapshot: {e}")
    
    return w, h

def save_vray_ipr_snapshot(file_path, w, h):
    if bpy.context.scene.render.engine != 'VRAY_RENDER_PREVIEW':
        print("V-Ray is not the current renderer.")
        return

    set_fixed_vray_render_resolution(w, h)
    bpy.context.scene.render.filepath = file_path
    bpy.ops.render.render(write_still=True)
    print("V-Ray screen shot saved.")

def world_space_to_screen_space(camera, world_point):
    cam_obj = bpy.data.objects[camera]
    scene = bpy.context.scene
    from bpy_extras import object_utils
    co_2d = object_utils.world_to_camera_view(scene, cam_obj, world_point)
    render_scale = scene.render.resolution_percentage / 100
    render_size = (
        int(scene.render.resolution_x * render_scale),
        int(scene.render.resolution_y * render_scale),
    )
    return (co_2d.x * render_size[0], (1-co_2d.y) * render_size[1])

def write_vertices_to_csv(mesh_name, camera_name, file_path):
    with open(file_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Vertex Index', 'World X', 'World Y', 'World Z', 'Screen X', 'Screen Y', 'Visible', 'Width', 'Height', 'ScaleX', 'ScaleY'])

        mesh_obj = bpy.data.objects[mesh_name]
        mesh_data = mesh_obj.data

        for i, v in enumerate(mesh_data.vertices):
            world_co = mesh_obj.matrix_world @ v.co
            screen_pos = world_space_to_screen_space(camera_name, world_co)
            visible = 'Yes'  # Placeholder for visibility

            csvwriter.writerow([i, world_co.x, world_co.y, world_co.z, screen_pos[0], screen_pos[1], visible, bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y, 1.0, 1.0])

            if i % 1000 == 0:
                print(i, world_co.x, world_co.y, world_co.z, screen_pos[0], screen_pos[1], visible)

mesh_name = bpy.context.selected_objects[0].name
camera_name = 'Camera'
output_path = 'C:\\Desktop\\Data\\vertices_data.csv'
image_path = 'C:\\Desktop\\Data\\vertices_data.png'

if os.path.exists(output_path):
    print("File already exists -- deleting")
    os.remove(output_path)

w, h = save_viewport_snapshot(image_path)
ipr_ss = 'C:\\Desktop\\Data\\vertices_ipr.png'
save_vray_ipr_snapshot(ipr_ss, w, h)
write_vertices_to_csv(mesh_name, camera_name, output_path)