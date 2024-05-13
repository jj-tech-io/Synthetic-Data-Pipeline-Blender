import bpy

def set_dimensions(obj, target_dimensions):
    # Calculate current dimensions
    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    current_dimensions = (
        max(v.x for v in bbox) - min(v.x for v in bbox),
        max(v.y for v in bbox) - min(v.y for v in bbox),
        max(v.z for v in bbox) - min(v.z for v in bbox),
    )

    # Calculate scale ratios
    scale_ratios = [target / current for target, current in zip(target_dimensions, current_dimensions)]

    # Apply scaling
    obj.scale = tuple(s * r for s, r in zip(obj.scale, scale_ratios))

def main():
    target_dimensions = (1.19, 0.37, 1.8)  # (X, Y, Z) in meters
    selected_objs = bpy.context.selected_objects

    if not selected_objs:
        print("No object selected")
        return

    for obj in selected_objs:
        if obj.type == 'MESH':
            set_dimensions(obj, target_dimensions)
        else:
            print(f"{obj.name} is not a mesh object.")

if __name__ == "__main__":
    main()
