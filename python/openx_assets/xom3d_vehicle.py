import bpy


def add_empty_node(name, parent_name=None):
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


def trim_vehicle_structure(obj=None, exclude=None):
    """
    Recursively deletes empty objects in the hierarchy, unless:
    - The object itself matches any prefix in the exclude list, OR
    - Any of its descendants match a prefix (ensuring ancestors are retained).
    
    Returns True if the object or any of its descendants should be kept.
    """
    if exclude is None:
        exclude = ["Grp_Root", "Grp_Rear_Axle_Center", "Grp_Eyepoint_"]
    
    if obj is None:
        obj = bpy.data.objects.get("Grp_Root")
        if obj is None:
            print("Object 'Grp_Root' not found.")
            return False

    # Check if this object is excluded
    is_excluded = any(obj.name.startswith(pattern) for pattern in exclude)

    # Recurse on children
    keep_any_child = False
    for child in list(obj.children):
        if trim_vehicle_structure(child, exclude):
            keep_any_child = True

    # Determine whether to keep this object
    keep_this = is_excluded or keep_any_child

    if obj.type == 'EMPTY' and not keep_this:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.ops.object.delete()
        return False  # Deleted

    return True  # Retained


def add_empty_base_structure():
    add_empty_node("Grp_Root")
    add_empty_node("Grp_Exterior", "Grp_Root")
    add_empty_node("Grp_Exterior_Dynamic", "Grp_Exterior")
    add_empty_node("Grp_Exterior_Static", "Grp_Exterior")
    add_empty_node("Grp_Rear_Axle_Center", "Grp_Exterior_Dynamic")
    add_empty_node("Grp_Interior", "Grp_Root")
    add_empty_node("Grp_Vehicle_Part", "Grp_Root")
    add_empty_node("Grp_Interior_Dynamic", "Grp_Interior")
    add_empty_eyepoint_structure(1)

def add_empty_interior_structure(interior=dict()):
    add_empty_node("Grp_Root")
    add_empty_node("Grp_Interior", "Grp_Root")
    add_empty_node("Grp_Interior_Static", "Grp_Interior")
    add_empty_node("Grp_Interior_Dynamic", "Grp_Interior")
    add_empty_node("Grp_Steering_Wheel", "Grp_Interior_Dynamic")
    add_empty_eyepoint_structure(interior.get('eyepoints', 1))
    add_empty_seats_structure(interior.get('seats', {'rows': 2, 'seats_per_row': 2}))

def add_empty_eyepoint_structure(number=1):
    for eyepoint_idx in range(number):
        add_empty_node(f"Grp_Eyepoint_{eyepoint_idx}", "Grp_Interior_Dynamic")

def add_empty_vehicle_structure(wheels=dict(), lights=dict(), doors=dict(), interior=dict(), license_plate=2, convertible_top=False):
    add_empty_base_structure()
    add_empty_wheels_structure(wheels)
    add_empty_lights_structure(lights)
    add_empty_doors_structure(doors)
    add_empty_interior_structure(interior)
    add_empty_license_plate_structure(license_plate)
    add_convertible_top_structure(convertible_top)

def add_empty_wheels_structure(wheels=dict()):
    for axle_idx in range(wheels.get('axles', 2)):  
        for wheel_idx in range(wheels.get('wheels_per_axle', 2)):
            add_empty_single_wheel_structure(axle_idx, wheel_idx)

def add_empty_single_wheel_structure(axle_idx, wheel_idx):

    wheel_name = f"Grp_Wheel_{axle_idx}_{wheel_idx}"
    steering_name = f"Grp_Wheel_Steering_{axle_idx}_{wheel_idx}"
    steering_rotating_name = f"Grp_Wheel_Steering_Rotating_{axle_idx}_{wheel_idx}"

    add_empty_node(wheel_name, "Grp_Exterior_Dynamic")
    add_empty_node(steering_name, wheel_name)
    add_empty_node(steering_rotating_name, wheel_name)

def add_empty_doors_structure(doors=dict()):
    add_empty_door_left_structure(doors.get('left', 2))
    add_empty_door_right_structure(doors.get('right', 2))
    add_empty_door_rear_structure(doors.get('rear', 1))
    add_empty_door_front_structure(doors.get('front', 1))
    add_empty_door_top_structure(doors.get('top', 1))
    add_empty_door_bottom_structure(doors.get('bottom', 1))

def add_empty_license_plate_structure(number=2):
    for license_plate_idx in range(number):
        add_empty_node(f"Grp_License_Plate_{license_plate_idx}", "Grp_Exterior_Dynamic")

def add_empty_door_left_structure(number=1):
    for door_left_idx in range(number):
        add_empty_node(f"Grp_Door_Left_{door_left_idx}", "Grp_Exterior_Dynamic")

def add_empty_door_right_structure(number=1):
    for door_right_idx in range(number):
        add_empty_node(f"Grp_Door_Right_{door_right_idx}", "Grp_Exterior_Dynamic")

def add_empty_door_rear_structure(number=1):
    for door_rear_idx in range(number):
        add_empty_node(f"Grp_Door_Rear_{door_rear_idx}", "Grp_Exterior_Dynamic")

def add_empty_door_front_structure(number=1):
    for door_front_idx in range(number):
        add_empty_node(f"Grp_Door_Front_{door_front_idx}", "Grp_Exterior_Dynamic")

def add_empty_door_top_structure(number=1):
    for door_top_idx in range(number):
        add_empty_node(f"Grp_Door_Top_{door_top_idx}", "Grp_Exterior_Dynamic")

def add_empty_door_bottom_structure(number=1):
    for door_bottom_idx in range(number):
        add_empty_node(f"Grp_Door_Bottom_{door_bottom_idx}", "Grp_Exterior_Dynamic")

def add_empty_lights_structure(lights=dict()):
    add_empty_light_brake_structure(lights.get('brake', 2))
    add_empty_light_corner_structure(lights.get('corner', 1))
    add_empty_light_day_structure(lights.get('day', 1))
    add_empty_light_fog_structure(lights.get('fog', 1))
    add_empty_light_high_beam_structure(lights.get('high_beam', 2))
    add_empty_light_indicator_structure(lights.get('indicator', 3))
    add_empty_light_license_plate_structure(lights.get('license_plate', 0))
    add_empty_light_low_beam_structure(lights.get('low_beam', 2))
    add_empty_light_park_structure(lights.get('park', 1))
    add_empty_light_position_structure(lights.get('position', 1))
    add_empty_light_reverse_structure(lights.get('reverse', 1))
    add_empty_light_tail_structure(lights.get('tail', 2))
    add_empty_light_warning_structure(lights.get('warning', 0))

def add_empty_light_brake_structure(number=1):
    for light_idx in range(number):
        add_empty_node(f"Grp_Light_Brake_Center_{light_idx}", "Grp_Exterior_Dynamic")
        add_empty_node(f"Grp_Light_Brake_Left_{light_idx}", "Grp_Exterior_Dynamic")
        add_empty_node(f"Grp_Light_Brake_Right_{light_idx}", "Grp_Exterior_Dynamic")

def add_empty_light_corner_structure(number=0):
    for light_idx in range(number):
        add_empty_node(f"Grp_Light_Corner_Left_{light_idx}", "Grp_Exterior_Dynamic")
        add_empty_node(f"Grp_Light_Corner_Right_{light_idx}", "Grp_Exterior_Dynamic")

def add_empty_light_day_structure(number=1):
    for light_idx in range(number):
        add_empty_node(f"Grp_Light_Day_Left_{light_idx}", "Grp_Exterior_Dynamic")
        add_empty_node(f"Grp_Light_Day_Right_{light_idx}", "Grp_Exterior_Dynamic")
        
def add_empty_light_fog_structure(number=1):
    for light_idx in range(number):
        add_empty_node(f"Grp_Light_Fog_Left_{light_idx}", "Grp_Exterior_Dynamic")
        add_empty_node(f"Grp_Light_Fog_Right_{light_idx}", "Grp_Exterior_Dynamic")

def add_empty_light_high_beam_structure(number=1):
    for light_idx in range(number):
        add_empty_node(f"Grp_Light_High_Beam_Left_{light_idx}", "Grp_Exterior_Dynamic")
        add_empty_node(f"Grp_Light_High_Beam_Right_{light_idx}", "Grp_Exterior_Dynamic")

def add_empty_light_indicator_structure(number=2):
    for light_idx in range(number):
        add_empty_node(f"Grp_Light_Indicator_Left_{light_idx}", "Grp_Exterior_Dynamic")
        add_empty_node(f"Grp_Light_Indicator_Right_{light_idx}", "Grp_Exterior_Dynamic")

def add_empty_light_license_plate_structure(number=0):
    for light_idx in range(number):
        add_empty_node(f"Grp_Light_License_Plate_{light_idx}", "Grp_Exterior_Dynamic")

def add_empty_light_low_beam_structure(number=1):
    for light_idx in range(number):
        add_empty_node(f"Grp_Light_Low_Beam_Left_{light_idx}", "Grp_Exterior_Dynamic")
        add_empty_node(f"Grp_Light_Low_Beam_Right_{light_idx}", "Grp_Exterior_Dynamic")

def add_empty_light_park_structure(number=1):
    for light_idx in range(number):
        add_empty_node(f"Grp_Light_Park_Left_{light_idx}", "Grp_Exterior_Dynamic")
        add_empty_node(f"Grp_Light_Park_Right_{light_idx}", "Grp_Exterior_Dynamic")

def add_empty_light_position_structure(number=1):
    for light_idx in range(number):
        add_empty_node(f"Grp_Light_Position_Left_{light_idx}", "Grp_Exterior_Dynamic")
        add_empty_node(f"Grp_Light_Position_Right_{light_idx}", "Grp_Exterior_Dynamic")

def add_empty_light_reverse_structure(number=1):
    for light_idx in range(number):
        add_empty_node(f"Grp_Light_Reverse_Left_{light_idx}", "Grp_Exterior_Dynamic")
        add_empty_node(f"Grp_Light_Reverse_Right_{light_idx}", "Grp_Exterior_Dynamic")

def add_empty_light_tail_structure(number=1):
    for light_idx in range(number):
        add_empty_node(f"Grp_Light_Tail_Left_{light_idx}", "Grp_Exterior_Dynamic")
        add_empty_node(f"Grp_Light_Tail_Right_{light_idx}", "Grp_Exterior_Dynamic")

def add_empty_light_warning_structure(number=0):
    for light_idx in range(number):
        add_empty_node(f"Grp_Light_Warning_{light_idx}", "Grp_Exterior_Dynamic")

def add_empty_seats_structure(seats=dict()):
    for row_idx in range(seats.get('rows', 2)):  
        for seat_idx in range(seats.get('seats_per_row', 2)):
            add_empty_node(f"Grp_Seat_{row_idx}_{seat_idx}", "Grp_Interior_Dynamic")

def add_convertible_top_structure(enabled=False):
    if enabled:
        add_empty_node("Grp_Convertible_Top", "Grp_Exterior_Dynamic")
        