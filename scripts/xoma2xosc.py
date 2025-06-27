import os
import json
import argparse

from xml.dom import minidom


def add_vehicle(doc, xml_parent, asset_data, vehicle_name):
    """
    Adds a <Vehicle> element to the given XML parent using minidom, based on asset data.

    Args:
        doc: The minidom Document object.
        xml_parent: The parent minidom XML element to which the Vehicle will be added.
        asset_data: A dictionary containing the asset's JSON data.
        vehicle_name: The name to assign to the vehicle.
    """
    meta = asset_data["metadata"]
    vehicle_class = meta.get("vehicleClassData", {})
    performance = vehicle_class.get("performance", {})
    axles = vehicle_class.get("axles", {})
    bbox = meta["boundingBox"]

    # Create Vehicle element
    vehicle = doc.createElement("Vehicle")
    vehicle.setAttribute("name", vehicle_name)
    vehicle.setAttribute("vehicleCategory", vehicle_class.get("vehicleCategory", "car"))
    # Fallback mass
    vehicle.setAttribute(
        "mass", str(meta.get("humanClassData", {}).get("mass", meta.get("mass", 2000)))
    )
    xml_parent.appendChild(vehicle)

    # BoundingBox
    bb = doc.createElement("BoundingBox")
    vehicle.appendChild(bb)

    center = doc.createElement("Center")
    center.setAttribute("x", f"{(bbox['x'][0] + bbox['x'][1]) / 2:.3f}")
    center.setAttribute("y", f"{(bbox['y'][0] + bbox['y'][1]) / 2:.3f}")
    center.setAttribute("z", f"{(bbox['z'][0] + bbox['z'][1]) / 2:.3f}")
    bb.appendChild(center)

    dimensions = doc.createElement("Dimensions")
    dimensions.setAttribute("length", f"{bbox['x'][1] - bbox['x'][0]:.3f}")
    dimensions.setAttribute("width", f"{bbox['y'][1] - bbox['y'][0]:.3f}")
    dimensions.setAttribute("height", f"{bbox['z'][1] - bbox['z'][0]:.3f}")
    bb.appendChild(dimensions)

    # Performance
    max_speed_kmh = performance.get(
        "maxSpeed", 217.0
    )  # Default to 217 km/h if not found
    max_speed_mps = max_speed_kmh / 3.6  # Convert km/h to m/s

    perf_el = doc.createElement("Performance")
    perf_el.setAttribute("maxSpeed", f"{max_speed_mps:.3f}")
    perf_el.setAttribute(
        "maxDeceleration", str(performance.get("maxDeceleration", 10.0))
    )
    perf_el.setAttribute(
        "maxAcceleration", str(performance.get("maxAcceleration", 5.0))
    )
    vehicle.appendChild(perf_el)

    # Axles
    axles_el = doc.createElement("Axles")
    vehicle.appendChild(axles_el)
    for tag, axle in [
        ("FrontAxle", axles.get("frontAxle")),
        ("RearAxle", axles.get("rearAxle")),
    ]:
        if axle:
            axle_el = doc.createElement(tag)
            axle_el.setAttribute("maxSteering", str(axle.get("maxSteering", 0.0)))
            axle_el.setAttribute("wheelDiameter", str(axle.get("wheelDiameter", 1.0)))
            axle_el.setAttribute("trackWidth", str(axle.get("trackWidth", 1.6)))
            axle_el.setAttribute("positionX", str(axle.get("positionX", 0.0)))
            axle_el.setAttribute("positionZ", str(axle.get("positionZ", 0.5)))
            axles_el.appendChild(axle_el)

    # Properties
    props = doc.createElement("Properties")
    vehicle.appendChild(props)

    prop_el = doc.createElement("Property")
    prop_el.setAttribute("name", "scaleMode")
    prop_el.setAttribute("value", "ModelToBB")
    props.appendChild(prop_el)


def convert(srcdir, destdir):
    """
    Converts OpenMATERIAL JSON files from srcdir into a single OpenSCENARIO XML vehicle catalog.

    Args:
        srcdir: Source directory containing OpenMATERIAL 3D JSON files (.xoma).
        destdir: Destination directory for the output XML file.
    """
    os.makedirs(destdir, exist_ok=True)
    catalog_name = os.path.basename(os.path.normpath(srcdir))
    output_path = os.path.join(destdir, f"{catalog_name}.xosc")

    # Create the minidom Document object
    doc = minidom.Document()

    # Create root structure
    root = doc.createElement("OpenSCENARIO")
    doc.appendChild(root)

    file_header = doc.createElement("FileHeader")
    file_header.setAttribute("revMajor", "1")
    file_header.setAttribute("revMinor", "0")
    file_header.setAttribute("author", "Dogan Ulus")
    root.appendChild(file_header)

    catalog = doc.createElement("Catalog")
    catalog.setAttribute("name", catalog_name)
    root.appendChild(catalog)

    # Iterate through files in the source directory
    for filename in sorted(os.listdir(srcdir)):
        if filename.lower().endswith(".xoma"):
            json_path = os.path.join(srcdir, filename)
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    asset = json.load(f)
                meta = asset.get("metadata", {})
                # Skip if the objectClass is not 'vehicle'
                if meta.get("objectClass") != "vehicle":
                    continue
                base_name = os.path.splitext(filename)[0]
                vehicle_name = base_name
                # Pass the document object to add_vehicle
                add_vehicle(doc, catalog, asset, vehicle_name)
            except Exception as e:
                # Log an error and skip the file if parsing fails
                print(f"Skipping {filename}: {e}")

    # Write the pretty-printed XML to the output file
    # Use toprettyxml() for formatting the entire document
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(doc.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8"))
    print(f"Written OpenSCENARIO XML to: {output_path}")


if __name__ == "__main__":
    # Set up argument parsing for command-line execution
    parser = argparse.ArgumentParser(
        description="Convert OpenMATERIAL JSON directory into OpenSCENARIO XML vehicle catalog."
    )
    parser.add_argument(
        "srcdir", help="Directory containing OpenMATERIAL 3D JSON files"
    )
    parser.add_argument(
        "--destdir", default=".", help="Destination directory for output XML"
    )
    args = parser.parse_args()

    convert(args.srcdir, args.destdir)
