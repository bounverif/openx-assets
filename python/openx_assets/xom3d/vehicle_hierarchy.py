import bpy


def create_empty_node(name, parent_name=None):
    if name in bpy.data.objects:
        return bpy.data.objects[name]
    empty_node = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(empty_node)
    empty_node.empty_display_type = 'PLAIN_AXES'
    if parent_name and parent_name in bpy.data.objects:
        empty_node.parent = bpy.data.objects[parent_name]
        empty_node.matrix_parent_inverse = empty_node.parent.matrix_world.inverted()
        bpy.context.evaluated_depsgraph_get().update()
    return empty_node


def delete_empty_hierarchy(obj):
    """
    Recursively deletes the given empty object and all its child empties.
    """
    # First, recurse on all children
    for child in obj.children:
        if child.type == 'EMPTY':
            delete_empty_hierarchy(child)
    
    # Deselect everything and select the object to delete
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.object.delete()

def create_base_hierarchy():
    grp_root = create_empty_node("Grp_Root")
    grp_exterior = create_empty_node("Grp_Exterior", "Grp_Root")
    grp_exterior_dynamic = create_empty_node("Grp_Exterior_Dynamic", "Grp_Exterior")
    grp_exterior_static = create_empty_node("Grp_Exterior_Static", "Grp_Exterior")

def create_interior_hierarchy(eyepoint=1):
    create_empty_node("Grp_Root")
    create_empty_node("Grp_Interior", "Grp_Root")
    create_empty_node("Grp_Interior_Static", "Grp_Interior")
    create_empty_node("Grp_Interior_Dynamic", "Grp_Interior")
    create_empty_node("Grp_Steering_Wheel", "Grp_Interior_Dynamic")
    for idx in range(eyepoint):
        create_empty_node(f"Grp_Eyepoint_{idx}", "Grp_Interior_Dynamic")


def create_minimal_car_hierarchy():
    create_base_hierarchy()
    for axle_idx in [0, 1]:  
        for wheel_idx in [0, 1]:
            create_empty_wheel_hierarchy(axle_idx, wheel_idx)

def create_full_car_hierarchy():
    create_base_hierarchy()
    create_interior_hierarchy()
    for axle_idx in [0, 1]:  
        for wheel_idx in [0, 1]:
            create_empty_wheel_hierarchy(axle_idx, wheel_idx)


def create_empty_wheel_hierarchy(axle_idx, wheel_idx):

    wheel_name = f"Grp_Wheel_{axle_idx}_{wheel_idx}"
    wheel_node = create_empty_node(wheel_name, "Grp_Exterior_Dynamic")

    steering_name = f"Grp_Wheel_Steering_{axle_idx}_{wheel_idx}"
    steering_node = create_empty_node(steering_name, wheel_name)

    rotating_name = f"Grp_Wheel_Steering_Rotating_{axle_idx}_{wheel_idx}"
    create_empty_node(rotating_name, wheel_name)