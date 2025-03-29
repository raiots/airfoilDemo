cd sims
plot3dToFoam ../grids/naca0012_5c.p3d -2D 1 -singleBlock -noBlank
autoPatch 45 -overwrite
createPatch -overwrite
