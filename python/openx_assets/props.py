import bpy

from bpy.props import FloatProperty, PointerProperty


class MinMaxLengthProperty(bpy.types.PropertyGroup):
    min: FloatProperty(name="Min", unit="LENGTH")
    max: FloatProperty(name="Max", unit="LENGTH")


class BoundingBoxProperty(bpy.types.PropertyGroup):
    x: PointerProperty(type=MinMaxLengthProperty)
    y: PointerProperty(type=MinMaxLengthProperty)
    z: PointerProperty(type=MinMaxLengthProperty)


class WheelAxleProperty(bpy.types.PropertyGroup):
    wheelDiameter: FloatProperty(name="Wheel Diameter")
    trackWidth: FloatProperty(name="Track Width")
    positionX: FloatProperty(name="Position X")
    positionZ: FloatProperty(name="Position Z")


class VehicleAssetProperty(bpy.types.PropertyGroup):
    """Property group to hold bounding box Propertyrmation for OpenMATERIAL 3D assets."""

    boundingBox: PointerProperty(type=BoundingBoxProperty)
    frontAxle: PointerProperty(type=WheelAxleProperty)
    rearAxle: PointerProperty(type=WheelAxleProperty)


def register():
    """Register the module."""

    bpy.utils.register_class(MinMaxLengthProperty)
    bpy.utils.register_class(BoundingBoxProperty)
    bpy.utils.register_class(WheelAxleProperty)
    bpy.utils.register_class(VehicleAssetProperty)

    bpy.types.Scene.open_material_asset_Property = PointerProperty(
        type=VehicleAssetProperty
    )

    if not hasattr(bpy.types.Scene, "xom3d_vehicle_asset"):
        bpy.types.Scene.xom3d_vehicle_asset = bpy.props.PointerProperty(
            type=VehicleAssetProperty
        )


def unregister():
    """Unregister the module."""

    if hasattr(bpy.types.Scene, "xom3d_vehicle_asset"):
        del bpy.types.Scene.xom3d_vehicle_asset

    del bpy.types.Scene.open_material_asset_Property

    bpy.utils.unregister_class(VehicleAssetProperty)
    bpy.utils.unregister_class(WheelAxleProperty)
    bpy.utils.unregister_class(BoundingBoxProperty)
    bpy.utils.unregister_class(MinMaxLengthProperty)
