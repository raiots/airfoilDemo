import os
from pathlib import Path
from foamlib import FoamCase

case = FoamCase(Path("../../sims"))

case.run(cmd="simpleFoam")
# case.clean()