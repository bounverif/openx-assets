from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple


@dataclass
class XOM3D:
    template_1_0_0 = {
        "metadata": {
            "name": "",
            "description": "",
            "uuid": "",
            "authors": [],
            "license": "",
            "copyrights": [],
            "openMaterial3dVersion": "1.0.0",
            "assetVersion": "devel",
            "assetType": "object",
            "objectClass": "vehicle",
            "boundingBox": {"x": [0.0, 0.0], "y": [0.0, 0.0], "z": [0.0, 0.0]},
            "vehicleClassData": {
                "vehicleCategory": "car",
                "axles": {
                    "frontAxle": {
                        "maxSteering": 0.0,
                        "wheelDiameter": 0.0,
                        "trackWidth": 0.0,
                        "positionX": 0.0,
                        "positionZ": 0.0,
                    },
                    "rearAxle": {
                        "maxSteering": 0.0,
                        "wheelDiameter": 0.0,
                        "trackWidth": 0.0,
                        "positionX": 0.0,
                        "positionZ": 0.0,
                    },
                },
                "performance": {
                    "maxSpeed": 0.0,
                    "maxAcceleration": 0.0,
                    "maxDeceleration": 0.0,
                },
            },
            "meshCount": 1,
            "triangleCount": 1,
            "animated": False,
            "textureResolutions": [],
            "pbrMaterialWorkflow": "metallic",
            "normalMapFormat": "OpenGL",
        }
    }
