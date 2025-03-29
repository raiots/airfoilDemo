import os
from pathlib import Path
from foamlib import FoamCase

pitz_tutorial = FoamCase(Path(os.environ["FOAM_TUTORIALS"]) / "incompressible/simpleFoam/pitzDaily")

my_pitz = pitz_tutorial.clone("myPitz")