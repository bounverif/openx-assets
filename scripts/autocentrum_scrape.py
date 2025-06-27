import requests
from bs4 import BeautifulSoup
import json

import os
import uuid
from datetime import date

# Polish-to-English translation map for selected fields
translation_dict = {
    "Długość": "Length",
    "Szerokość": "Width",
    "Szerokość z lusterkami bocznymi": "Width with side mirrors",
    "Wysokość": "Height",
    "Rozstaw osi": "Wheelbase",
    "Rozstaw kół - przód": "Front track width",
    "Rozstaw kół - tył": "Rear track width",
    "Zwis przedni": "Front overhang",
    "Zwis tylny": "Rear overhang",
}


def scrape_vehicle_dimensions(url):
    """Scrape selected car body dimensions from AutoCentrum."""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    dimensions = {}
    rows = soup.find_all("div", class_="dt-row")

    for row in rows:
        key = row.find("div", class_="dt-row__text__content")
        value = row.find("span", class_="dt-param-value")

        if key and value:
            key_text = key.get_text(strip=True)
            if key_text in translation_dict:
                value_text = value.get_text(strip=True).replace("mm", "").strip()
                dimensions[translation_dict[key_text]] = value_text

    return dimensions


def build_vehicle_asset_json(name, scraped_dimensions):
    length = float(scraped_dimensions["Length"]) / 1000  # Convert mm to meters
    width = float(scraped_dimensions["Width"]) / 1000
    height = float(scraped_dimensions["Height"]) / 1000
    front_track = float(scraped_dimensions["Front track width"]) / 1000
    rear_track = float(scraped_dimensions["Rear track width"]) / 1000
    # front_overhang = float(scraped_dimensions["Front overhang"]) / 1000
    rear_overhang = float(scraped_dimensions["Rear overhang"]) / 1000
    wheelbase = float(scraped_dimensions["Wheelbase"]) / 1000

    rear_axle_position_x = rear_overhang - length / 2
    front_axle_position_x = rear_axle_position_x + wheelbase

    half_length = length / 2
    half_width = width / 2

    asset = {
        "$schema": "https://raw.githubusercontent.com/asam-ev/OpenMATERIAL-3D/refs/tags/v1.0.0/schemas/asset_schema.json",
        "metadata": {
            "name": name,
            "openMaterial3dVersion": "1.0.0",
            "assetType": "object",
            "objectClass": "vehicle",
            "uuid": str(uuid.uuid5(uuid.NAMESPACE_DNS, name)),
            "assetVersion": date.today().isoformat(),
            "copyrights": ["(c) 2025 Dogan Ulus <dogan.ulus@bogazici.edu.tr>"],
            "license": "MPL-2.0",
            "authors": ["Dogan Ulus <dogan.ulus@bogazici.edu.tr>"],
            "mass": 1500,
            "vehicleClassData": {
                "vehicleCategory": "car",
                "axles": {
                    "frontAxle": {
                        "maxSteering": 0.175,
                        "wheelDiameter": 0.7,
                        "trackWidth": round(front_track, 3),
                        "positionX": round(front_axle_position_x, 3),
                        "positionZ": 0.35,
                    },
                    "rearAxle": {
                        "maxSteering": 0.0,
                        "wheelDiameter": 0.7,
                        "trackWidth": round(rear_track, 3),
                        "positionX": round(rear_axle_position_x, 3),
                        "positionZ": 0.35,
                    },
                },
                "performance": {
                    "maxSpeed": 50,
                    "maxAcceleration": 5.0,
                    "maxDeceleration": 10.0,
                },
            },
            "boundingBox": {
                "x": [-round(half_length, 4), round(half_length, 4)],
                "y": [-round(half_width, 4), round(half_width, 4)],
                "z": [0, round(height, 4)],
            },
            "animated": True,
            "triangleCount": 1,
            "meshCount": 1,
            "textureResolutions": [""],
            "normalMapFormat": "OpenGL",
            "pbrMaterialWorkflow": "metallic",
        },
    }

    return asset


# Example usage
bmw_targets = {
    "m1.bmw.x1.2009": "https://www.autocentrum.pl/dane-techniczne/bmw/x1/e84/crossover/",
    "m1.bmw.x1.2012": "https://www.autocentrum.pl/dane-techniczne/bmw/x1/e84/crossover-facelifting/",
    "m1.bmw.x1.2016": "https://www.autocentrum.pl/dane-techniczne/bmw/x1/f48/crossover/",
    "m1.bmw.x1.2019": "https://www.autocentrum.pl/dane-techniczne/bmw/x1/f48/crossover-facelifting/",
    "m1.bmw.x1.2022": "https://www.autocentrum.pl/dane-techniczne/bmw/x1/u11/crossover/",
    "m1.bmw.i4": "https://www.autocentrum.pl/dane-techniczne/bmw/i4/gran-coupe-facelifting/",
}


def make_targets(folder_name, targets):
    os.makedirs(folder_name, exist_ok=True)
    for key, url in targets.items():
        print(f"Scraping dimensions for {key} from {url}")
        data = scrape_vehicle_dimensions(url)
        xoma = build_vehicle_asset_json(name=key, scraped_dimensions=data)
        with open(
            f"{folder_name}/{key.replace('.', '_')}.xoma", "w", encoding="utf-8"
        ) as f:
            json.dump(xoma, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":

    bmw_targets = {
        "m1.bmw.1.2004.hatchback": "https://www.autocentrum.pl/dane-techniczne/bmw/seria-1/e81-e87/hatchback-5d-e87/",
        "m1.bmw.1.2007.hatchback": "https://www.autocentrum.pl/dane-techniczne/bmw/seria-1/e81-e87/hatchback-3d-e81/",
        "m1.bmw.1.2007.coupe": "https://www.autocentrum.pl/dane-techniczne/bmw/seria-1/e81-e87/coupe-e82/",
        "m1.bmw.1.2007.cabriolet": "https://www.autocentrum.pl/dane-techniczne/bmw/seria-1/e81-e87/cabrio-e88/",
        "m1.bmw.1.2011.coupe": "https://www.autocentrum.pl/dane-techniczne/bmw/seria-1/e81-e87/m-coupe/",
        "m1.bmw.1.2011.hatchback.3d": "https://www.autocentrum.pl/dane-techniczne/bmw/seria-1/f20-f21/hatchback-3d/",
        "m1.bmw.1.2011.hatchback.5d": "https://www.autocentrum.pl/dane-techniczne/bmw/seria-1/f20-f21/hatchback-5d/",
        "m1.bmw.1.2015.hatchback.3d": "https://www.autocentrum.pl/dane-techniczne/bmw/seria-1/f20-f21/hatchback-3d-facelifting-2015/",
        "m1.bmw.1.2015.hatchback.5d": "https://www.autocentrum.pl/dane-techniczne/bmw/seria-1/f20-f21/hatchback-5d-facelifting-2015/",
        "m1.bmw.1.2017.hatchback.3d": "https://www.autocentrum.pl/dane-techniczne/bmw/seria-1/f20-f21/hatchback-3d-facelifting-2017/",
        "m1.bmw.1.2017.hatchback.5d": "https://www.autocentrum.pl/dane-techniczne/bmw/seria-1/f20-f21/hatchback-5d-facelifting-2017/",
        "m1.bmw.1.2019.hatchback": "https://www.autocentrum.pl/dane-techniczne/bmw/seria-1/f40/hatchback/",
        "m1.bmw.1.2024.hatchback": "https://www.autocentrum.pl/dane-techniczne/bmw/seria-1/f70/hatchback/",
        "m1.bmw.2.2021.coupe": "https://www.autocentrum.pl/dane-techniczne/bmw/seria-2/g42-u06/coupe/",
        "m1.bmw.2.2021.grancoupe": "https://www.autocentrum.pl/dane-techniczne/bmw/seria-2/g42-u06/gran-coupe/",
        "m1.bmw.2.2025.grancoupe": "https://www.autocentrum.pl/dane-techniczne/bmw/seria-2/f74/gran-coupe/",
        "m1.bmw.x1.2009": "https://www.autocentrum.pl/dane-techniczne/bmw/x1/e84/crossover/",
        "m1.bmw.x1.2012": "https://www.autocentrum.pl/dane-techniczne/bmw/x1/e84/crossover-facelifting/",
        "m1.bmw.x1.2016": "https://www.autocentrum.pl/dane-techniczne/bmw/x1/f48/crossover/",
        "m1.bmw.x1.2019": "https://www.autocentrum.pl/dane-techniczne/bmw/x1/f48/crossover-facelifting/",
        "m1.bmw.x1.2022": "https://www.autocentrum.pl/dane-techniczne/bmw/x1/u11/crossover/",
        # "m1.bmw.x2.2017": "https://www.autocentrum.pl/dane-techniczne/bmw/x2/f39/crossover/",
        "m1.bmw.x2.2020": "https://www.autocentrum.pl/dane-techniczne/bmw/x2/f39/crossover-plug-in/",
        "m1.bmw.x2.2023": "https://www.autocentrum.pl/dane-techniczne/bmw/x2/u10/suv/",
        # "m1.bmw.x3.2003": "https://www.autocentrum.pl/dane-techniczne/bmw/x3/e83/",
        "m1.bmw.x3.2010": "https://www.autocentrum.pl/dane-techniczne/bmw/x3/f25/suv/",
        "m1.bmw.x3.2014": "https://www.autocentrum.pl/dane-techniczne/bmw/x3/f25/suv-facelifting/",
        "m1.bmw.x3.2017": "https://www.autocentrum.pl/dane-techniczne/bmw/x3/g01/suv/",
        "m1.bmw.x3.2021": "https://www.autocentrum.pl/dane-techniczne/bmw/x3/g01/suv-facelifting/",
        "m1.bmw.x3.2024": "https://www.autocentrum.pl/dane-techniczne/bmw/x3/g45/suv/",
        "m1.bmw.x4.2014": "https://www.autocentrum.pl/dane-techniczne/bmw/x4/g01/",
        "m1.bmw.x4.2018": "https://www.autocentrum.pl/dane-techniczne/bmw/x4/g02/suv/",
        "m1.bmw.x4.2022": "https://www.autocentrum.pl/dane-techniczne/bmw/x4/g02/suv-facelifting/",
        "m1.bmw.x5.2010": "https://www.autocentrum.pl/dane-techniczne/bmw/x5/e70/suv-facelifting/",
        # "m1.bmw.x5.2013": "https://www.autocentrum.pl/dane-techniczne/bmw/x5/f15/suv/",
        "m1.bmw.x5.2018": "https://www.autocentrum.pl/dane-techniczne/bmw/x5/g05/suv/",
        "m1.bmw.x5.2023": "https://www.autocentrum.pl/dane-techniczne/bmw/x5/g05/suv-facelifting/",
    }

    make_targets("bmw", bmw_targets)
