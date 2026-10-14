"""Set the ambient colour of every material in OSG text (.osgt) files to its diffuse colour.

The Blender FBX exporter writes AmbientFactor 0, so osgconv produces materials
with a black ambient term. esmini lights the sides of a vehicle that face away
from its key light with ambient light only, which makes such models render
almost black. glTF and USD have no ambient term, so only the OSGB output needs this.
"""

import pathlib
import re
import sys

# The OSG serializer always writes Ambient directly before Diffuse in osg::Material.
MATERIAL_COLORS = re.compile(
    r"(Ambient TRUE )(Front .*?) \n(\s*Diffuse TRUE )(Front .*?) \n"
)


def main():
    for path in map(pathlib.Path, sys.argv[1:]):
        text, count = MATERIAL_COLORS.subn(
            r"\g<1>\g<4> \n\g<3>\g<4> \n", path.read_text()
        )
        path.write_text(text)
        print(f"Set ambient to diffuse in {count} materials of '{path}'")


if __name__ == "__main__":
    main()
