import bpy
import pathlib

from xml.dom import minidom


def catalog_create(name, author="", version=""):
    """
    Creates an OpenSCENARIO catalog XML structure.

    Args:
        name: The name of the catalog.
        author: The author of the catalog (optional).

    Returns:
        A minidom Document object containing the XML representation of the catalog.
    """
    doc = minidom.Document()

    # Create root structure
    root = doc.createElement("OpenSCENARIO")
    doc.appendChild(root)

    file_header = doc.createElement("FileHeader")
    file_header.setAttribute("revMajor", "1")
    file_header.setAttribute("revMinor", "0")
    file_header.setAttribute("author", author)
    file_header.setAttribute("version", version)
    root.appendChild(file_header)

    catalog = doc.createElement("Catalog")
    catalog.setAttribute("name", name)
    root.appendChild(catalog)

    return doc, catalog


def catalog_add_vehicle(root, catalog, name=None, model3d=None, asset_data={}):
    """
    Adds a <Vehicle> element to the given XML parent using minidom, based on asset data.

    Args:
        root: The root minidom XML element to which the Vehicle will be added.
        catalog: The catalog element to which the Vehicle will be added.
        asset_data: A dictionary containing the asset's JSON data.
    """

    metadata = asset_data.get("metadata", {})
    vehicle_name = name if name is not None else metadata.get("name", "UnknownVehicle")
    bbox = metadata.get("boundingBox", {})
    vehicle_class = metadata.get("vehicleClassData", {})
    performance = vehicle_class.get("performance", {})
    axles = vehicle_class.get("axles", {})

    # Create Vehicle element
    vehicle = root.createElement("Vehicle")
    vehicle.setAttribute("name", vehicle_name)
    vehicle.setAttribute("vehicleCategory", vehicle_class.get("vehicleCategory", "car"))
    vehicle.setAttribute("mass", str(vehicle_class.get("mass", 2000)))
    if model3d is not None:
        vehicle.setAttribute("model3d", model3d)
    catalog.appendChild(vehicle)

    # BoundingBox
    bb = root.createElement("BoundingBox")
    vehicle.appendChild(bb)

    center = root.createElement("Center")
    center.setAttribute("x", f"{(bbox['x'][0] + bbox['x'][1]) / 2:.3f}")
    center.setAttribute("y", f"{(bbox['y'][0] + bbox['y'][1]) / 2:.3f}")
    center.setAttribute("z", f"{(bbox['z'][0] + bbox['z'][1]) / 2:.3f}")
    bb.appendChild(center)

    dimensions = root.createElement("Dimensions")
    dimensions.setAttribute("length", f"{bbox['x'][1] - bbox['x'][0]:.3f}")
    dimensions.setAttribute("width", f"{bbox['y'][1] - bbox['y'][0]:.3f}")
    dimensions.setAttribute("height", f"{bbox['z'][1] - bbox['z'][0]:.3f}")
    bb.appendChild(dimensions)

    # Performance
    perf_el = root.createElement("Performance")
    perf_el.setAttribute("maxSpeed", str(performance.get("maxSpeed", 55.0)))
    perf_el.setAttribute(
        "maxDeceleration", str(performance.get("maxDeceleration", 8.0))
    )
    perf_el.setAttribute(
        "maxAcceleration", str(performance.get("maxAcceleration", 4.0))
    )
    vehicle.appendChild(perf_el)

    # Axles
    axles_el = root.createElement("Axles")
    vehicle.appendChild(axles_el)
    for tag, axle in [
        ("FrontAxle", axles.get("frontAxle")),
        ("RearAxle", axles.get("rearAxle")),
    ]:
        if axle:
            axle_el = root.createElement(tag)
            axle_el.setAttribute("maxSteering", str(axle.get("maxSteering", 0.0)))
            axle_el.setAttribute("wheelDiameter", str(axle.get("wheelDiameter", 1.0)))
            axle_el.setAttribute("trackWidth", str(axle.get("trackWidth", 1.6)))
            axle_el.setAttribute("positionX", str(axle.get("positionX", 0.0)))
            axle_el.setAttribute("positionZ", str(axle.get("positionZ", 0.5)))
            axles_el.appendChild(axle_el)

    # Properties
    # props = root.createElement("Properties")
    # vehicle.appendChild(props)

    # prop_el = root.createElement("Property")
    # prop_el.setAttribute("name", "scaleMode")
    # prop_el.setAttribute("value", "ModelToBB")
    # props.appendChild(prop_el)
