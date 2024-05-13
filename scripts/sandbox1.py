import bpy
from math import radians
def get_objects_of_type(obj_type):
    """Get all objects of a given type."""
    objects = []
    for obj in bpy.data.objects:
        if obj.type == obj_type:
            objects.append(obj)
    return objects

def delete_objects_by_type(obj_type, ignore="")
    count = 0
    """Delete all objects of a given type."""
    objects_to_delete = get_objects_of_type(obj_type)
    bpy.ops.object.select_all(action='DESELECT')  # Deselect all objects
    for obj in objects_to_delete:
        obj.select_set(True)  # Select objects of the specified type
        count += 1
    bpy.ops.object.delete()  # Delete the selected objects
    return count

def create_camera(name='Camera', location=(0, 0, 0), rotation=(0, 0, 0)):
    """Create and link a camera to the current collection."""
    cam_data = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, cam_data)
    cam.location = location
    cam.rotation_euler = (radians(rotation[0]), radians(rotation[1]), radians(rotation[2]))
    bpy.context.collection.objects.link(cam)  # Add camera to the current collection
    bpy.context.scene.camera = cam  # Set this camera as the active camera
    return cam

# Function to adjust camera rotation
def set_camera_rotation(camera, rotation=(0, 0, 0)):
    """Set the camera rotation in degrees (converted to radians)."""
    camera.rotation_euler = (radians(rotation[0]), radians(rotation[1]), radians(rotation[2]))
cube1 = bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, 
    align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
# Create a camera and set its initial rotation
camera = create_camera("cam1", (0, -1, 0), (0, 0, 0))

# Adjust the camera rotation later
set_camera_rotation(camera, (90, 0,0))

# Optional: Create and link a light to the current collection
light_data = bpy.data.lights.new('light', type='POINT')
light = bpy.data.objects.new('light', light_data)
light.location = (2, -2, 1)
bpy.context.collection.objects.link(light)
light.data.energy = 10.0
