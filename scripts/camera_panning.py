import bpy
import os
import random
from math import radians, sin, cos, pi, acos, atan2
from datetime import datetime
from mathutils import Vector, Euler

# Define a global resolution
RENDER_RESOLUTION_X = 1024
RENDER_RESOLUTION_Y = 1024

class Camera:
    def __init__(self, name):
        """Initialize the Camera class with a given camera name."""
        self.name = name
        self.camera = bpy.data.objects[name]
        self.default_x_rotation = radians(90)
    
    def configure_render_settings(self, resolution_x=1024, resolution_y=1024):
        """Configure the render settings."""
        bpy.context.scene.render.resolution_x = resolution_x
        bpy.context.scene.render.resolution_y = resolution_y

    def set_location_and_rotation(self, location, rotation):
        """Set the camera's location and rotation."""
        self.camera.location = location
        self.camera.rotation_euler = rotation

    def spherical_to_cartesian(self, radius, theta, phi):
        """Convert spherical coordinates to Cartesian coordinates."""
        x = radius * sin(theta) * cos(phi)
        y = radius * sin(theta) * sin(phi)
        z = radius * cos(theta)
        return Vector((x, y, z))

    def cartesian_to_spherical(self, cartesian):
        """Convert Cartesian coordinates to spherical coordinates."""
        radius = cartesian.length
        theta = acos(cartesian.z / radius)
        phi = atan2(cartesian.y, cartesian.x)
        return radius, theta, phi

    def set_random_view_from_cursor(self, radius_range=(1.5, 3.0), theta_range=(0, pi), phi_range=(-pi, pi)):
        """Set a random view around the 3D cursor using spherical coordinates."""
        cursor_location = bpy.context.scene.cursor.location

        # Randomize the radius, theta, and phi angles
        radius = random.uniform(*radius_range)
        theta = random.uniform(*theta_range)  # Polar angle (vertical)
        phi = random.uniform(*phi_range)      # Azimuthal angle (horizontal)

        # Convert spherical coordinates to Cartesian
        offset = self.spherical_to_cartesian(radius, theta, phi)

        # Set camera location and rotation
        self.set_location_and_rotation(cursor_location + offset, Vector((self.default_x_rotation, 0, 0)))
        direction = cursor_location - self.camera.location
        rot_euler = direction.to_track_quat('Z', 'Y').to_euler()
        self.set_location_and_rotation(self.camera.location, rot_euler)

        print(f"Set random view from cursor: Radius: {radius}, Theta: {theta}, Phi: {phi}, Location: {self.camera.location}")

    def save_viewport_snapshot(self, file_path):
        """Save a snapshot of the current viewport to an image file."""
        self.configure_render_settings(RENDER_RESOLUTION_X, RENDER_RESOLUTION_Y)
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

def assign_random_hdri(directory):
    """Assign a random HDRI from a given directory to the world environment."""
    hdri_files = [f for f in os.listdir(directory) if f.lower().endswith('.hdr')]
    if not hdri_files:
        print(f"No HDRI files found in directory: {directory}")
        return
    
    random_hdri = os.path.join(directory, random.choice(hdri_files))
    bpy.context.scene.world.use_nodes = True
    nodes = bpy.context.scene.world.node_tree.nodes
    env_node = nodes.get('Environment Texture')
    
    if not env_node:
        env_node = nodes.new(type='ShaderNodeTexEnvironment')
        env_node.name = 'Environment Texture'
        bpy.context.scene.world.node_tree.links.new(env_node.outputs[0], nodes['Background'].inputs[0])
    
    env_node.image = bpy.data.images.load(random_hdri)
    print(f"Assigned HDRI: {random_hdri}")

# Example usage
camera_name = 'Camera'
camera = Camera(camera_name)
HDRI_DIRECTORY = r"C:\Desktop\SyntheticDataBlender\hdris"

assign_random_hdri(HDRI_DIRECTORY)
camera.set_random_view_from_cursor(radius_range=(1.5, 3.0), theta_range=(radians(85), radians(92.8)), phi_range=(radians(106), radians(148.45)))

# Generate a unique name based on the current time
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
output_directory = r"C:\Desktop\Data"
csv_path = os.path.join(output_directory, f"vertices_data_{timestamp}.csv")
image_path = os.path.join(output_directory, f"vertices_data_{timestamp}.png")

if not os.path.exists(output_directory):
    os.makedirs(output_directory)

camera.save_viewport_snapshot(image_path)

print(f"CSV file path: {csv_path}")
print(f"Image file path: {image_path}")
