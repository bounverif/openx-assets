import os
import argparse
import xml.etree.ElementTree as ET
import json
import uuid

from datetime import date


def convert_to_float(value, ndigits=4):
    try:
        return round(float(value), ndigits)
    except (ValueError, TypeError):
        return value  # In case of invalid or missing values, return the original value


def evaluate_expression(value, ndigits=4):
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        # Remove the "${" and "}"
        expr = value[2:-1]
        try:
            # Evaluate the expression and return it rounded to 4 decimal places
            return round(eval(expr), ndigits)
        except Exception as e:
            print(f"Error evaluating expression {value}: {e}")
            return value  # If there's an error, return the original value
    else:
        # Otherwise, just convert it to float and round
        return convert_to_float(value, ndigits)


def create_vehicle_folders(xml_filepath):
    try:
        # Parse XML
        tree = ET.parse(xml_filepath)
        root = tree.getroot()

        # Determine base folder name from XML file
        base_folder = os.path.splitext(os.path.basename(xml_filepath))[0]
        os.makedirs(base_folder, exist_ok=True)

        catalog = root.find("Catalog")
        if catalog is None:
            print("No <Catalog> element found.")
            return

        for vehicle in catalog.findall("Vehicle"):
            name = vehicle.get("name")
            category = vehicle.get("vehicleCategory")

            print(f"Processing vehicle: {name}")

            if not name:
                print("Skipping vehicle without name.")
                continue

            original_name = name.strip()
            folder_name = original_name.replace(".", "_")
            folder_path = base_folder
            # folder_path = os.path.join(base_folder, folder_name)
            os.makedirs(folder_path, exist_ok=True)

            # Extract BoundingBox
            bbox = vehicle.find("BoundingBox")
            center = bbox.find("Center")
            dimensions = bbox.find("Dimensions")

            bb_x_offset = evaluate_expression(center.get("x"))
            half_length = evaluate_expression(float(dimensions.get("length")) / 2)
            half_width = evaluate_expression(float(dimensions.get("width")) / 2)
            height = evaluate_expression(dimensions.get("height"))

            bounding_box = {
                "x": [-half_length, half_length],
                "y": [-half_width, half_width],
                "z": [0, height],
            }

            # Extract Axles
            axles = vehicle.find("Axles")
            front = axles.find("FrontAxle")
            rear = axles.find("RearAxle")

            performance = vehicle.find("Performance")
            performance_data = {
                "maxSpeed": int(evaluate_expression(performance.get("maxSpeed"))),
                "maxAcceleration": evaluate_expression(
                    performance.get("maxAcceleration")
                ),
                "maxDeceleration": evaluate_expression(
                    performance.get("maxDeceleration")
                ),
            }

            mass_data = int(evaluate_expression(vehicle.get("mass")))

            axles_data = {
                "frontAxle": {
                    "maxSteering": evaluate_expression(front.get("maxSteering")),
                    "wheelDiameter": evaluate_expression(front.get("wheelDiameter")),
                    "trackWidth": evaluate_expression(front.get("trackWidth")),
                    "positionX": evaluate_expression(
                        float(front.get("positionX")) - bb_x_offset
                    ),
                    "positionZ": evaluate_expression(front.get("positionZ")),
                },
                "rearAxle": {
                    "maxSteering": evaluate_expression(rear.get("maxSteering")),
                    "wheelDiameter": evaluate_expression(rear.get("wheelDiameter")),
                    "trackWidth": evaluate_expression(rear.get("trackWidth")),
                    "positionX": evaluate_expression(
                        float(rear.get("positionX")) - bb_x_offset
                    ),
                    "positionZ": evaluate_expression(rear.get("positionZ")),
                },
            }

            metadata = {
                "$schema": "https://raw.githubusercontent.com/asam-ev/OpenMATERIAL-3D/refs/tags/v1.0.0/schemas/asset_schema.json",
                "metadata": {
                    "name": original_name,
                    "openMaterial3dVersion": "1.0.0",
                    "assetType": "object",
                    "objectClass": "vehicle",
                    "uuid": str(uuid.uuid5(uuid.NAMESPACE_URL, original_name)),
                    "assetVersion": date.today().strftime("%Y.%-m.%-d"),
                    "copyrights": [
                        "(c) 2025 Dogan Ulus <dogan.ulus@bogazici.edu.tr>",
                    ],
                    "license": "MPL-2.0",
                    "authors": ["Dogan Ulus <dogan.ulus@bogazici.edu.tr>"],
                    "mass": mass_data,
                    "vehicleClassData": {
                        "vehicleCategory": category,
                        "axles": axles_data,
                        "performance": performance_data,
                    },
                    "boundingBox": bounding_box,
                    "animated": True,
                    "triangleCount": 1,
                    "meshCount": 1,
                    "textureResolutions": [""],
                    "normalMapFormat": "OpenGL",
                    "pbrMaterialWorkflow": "metallic",
                },
            }

            json_filename = os.path.join(folder_path, f"{folder_name}.xoma")
            with open(json_filename, "w") as f:
                json.dump(metadata, f, indent=2)

            print(f"Created folder and JSON: {json_filename}")

    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate folders and metadata JSON for each Vehicle in OpenSCENARIO XML."
    )
    parser.add_argument("xml_file", help="Path to the OpenSCENARIO XML file")
    args = parser.parse_args()
    create_vehicle_folders(args.xml_file)


if __name__ == "__main__":
    main()
