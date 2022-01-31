"""Solve for the first two hybridized modes of a LiNbO3-on-SiO2 waveguide.

This simulation re-produces the modes discussed in the Scientific Reports paper:

    A. Kaushalram et al., 'Mode hybridization analysis in thin flm lithium niobate strip multimode waveguides', 2020

On most *nix-based machines, run the script with:

    $ mpirun -n 8 python wg_modes_3D.py

If you wish to increase the number of cores that the example is executed on,
change 8 to the desired number of cores.
"""
import emopt
import sys
from emopt.misc import NOT_PARALLEL

import numpy as np
from math import pi

####################################################################################
# Set up the size of the problem
####################################################################################
W = 3.0
H = 3.0
dx = 0.02
dy = 0.02
N = int(np.ceil(W/dx)+1)
M = int(np.ceil(H/dy)+1)
W = (N-1)*dx
H = (M-1)*dy

wavelength = 1.55

####################################################################################
# Define the material diststriputions!
####################################################################################

n_o = 2.211111008653574
n_e = 2.1375596497855565
n_SiO2 = 1.444023632787416

eps_LiNbO3_x = n_e**2
eps_LiNbO3_y = n_o**2
eps_LiNbO3_z = n_o**2
eps_SiO2 = n_SiO2**2

w_wg = 1
h_wg = 0.3
tf = 0.6
angle = 65
h_clad = 1


comsol_result = 1.8907191769719351


# we need to set up the geometry of the cross section for which the mode will
# be computed. Here we use emopt.grid objects to define the permittivity and
# permeability of waveguiding structure for which the modes will be calculated

# With the current implementatin of the anisotropic permittivity, we must instatiate three
# versions of the permittivity: 1 for eps_xx, 1 for eps_yy, and one for eps_zz

# Define vertices of the polygon

w_wg_bot = w_wg + 2*h_wg/np.tan(angle*np.pi/180.)
vertices = np.array([
    [-W/2, tf/2 - h_wg],
    [-w_wg_bot/2., tf/2 - h_wg],
    [-w_wg/2., tf/2.],
    [w_wg/2., tf/2.],
    [w_wg_bot/2., tf/2. - h_wg],
    [W/2., tf/2. - h_wg],
    [W/2., - tf/2.],
    [-W/2., -tf/2.],
    [-W/2, tf/2 - h_wg]])


# eps_xx
lnoi = emopt.grid.Polygon(vertices[:,0],vertices[:,1])
bottom_cladding = emopt.grid.Rectangle(0, -tf/2. - h_clad/2. , W , h_clad)
eps_bg = emopt.grid.Rectangle(0, tf/2. + (H-h_clad-tf)/2., W, (H-h_clad-tf))

lnoi.layer = 1; lnoi.material_value = eps_LiNbO3_x
bottom_cladding.layer = 2; bottom_cladding.material_value = eps_SiO2
eps_bg.layer = 3; eps_bg.material_value = 1.0

eps_x = emopt.grid.StructuredMaterial2D(W,H,dx,dy)
eps_x.add_primitives([lnoi, bottom_cladding, eps_bg])
eps_x.add_primitives([lnoi])

# eps_yy
lnoi = emopt.grid.Polygon(vertices[:,0],vertices[:,1])
bottom_cladding = emopt.grid.Rectangle(0, -tf/2. - h_clad/2. , W , h_clad)
eps_bg = emopt.grid.Rectangle(0, tf/2. + (H-h_clad-tf)/2., W, (H-h_clad-tf))

lnoi.layer = 1; lnoi.material_value = eps_LiNbO3_y
bottom_cladding.layer = 2; bottom_cladding.material_value = eps_SiO2
eps_bg.layer = 3; eps_bg.material_value = 1.0

eps_y = emopt.grid.StructuredMaterial2D(W,H,dx,dy)
eps_y.add_primitives([strip, bottom_cladding, eps_bg])

# eps_zz
strip = emopt.grid.Polygon(vertices[:,0],vertices[:,1])
bottom_cladding = emopt.grid.Rectangle(0, -tf/2. - h_clad/2. , W , h_clad)
eps_bg = emopt.grid.Rectangle(0, tf/2. + (H-h_clad-tf)/2., W, (H-h_clad-tf))

strip.layer = 1; strip.material_value = eps_LiNbO3_z
bottom_cladding.layer = 2; bottom_cladding.material_value = eps_SiO2
eps_bg.layer = 3; eps_bg.material_value = 1.0

eps_z = emopt.grid.StructuredMaterial2D(W,H,dx,dy)
eps_z.add_primitives([strip, bottom_cladding, eps_bg])

# We provide these three permittivities to the mode solver as a list
eps = [eps_x, eps_y, eps_z]

mu = emopt.grid.ConstantMaterial2D(1.0)
domain = emopt.misc.DomainCoordinates(-W/2., W/2., -tf/2. - h_clad, tf/2. + (H - tf - h_clad), 0, 0, dx, dy, 1.0)

####################################################################################
# setup the mode solver
####################################################################################
neigs = 1
modes = emopt.modes.ModeFullVector(wavelength, eps, mu, domain, n0=np.sqrt(eps_LiNbO3_y), neigs=neigs)
modes.build() # build the eigenvalue problem internally
modes.solve() # solve for the effective indices and mode profiles

####################################################################################
# Plot the hybrid modes
####################################################################################
mindex = 1
Ex = modes.get_field_interp(mindex, 'Ex', squeeze=True)
Ey = modes.get_field_interp(mindex, 'Ey', squeeze=True)
Ez = modes.get_field_interp(mindex, 'Ez', squeeze=True)
if(NOT_PARALLEL):
    import matplotlib.pyplot as plt
    print('COMSOL Result for Effective index: {:.5}'.format(comsol_result))
    print('Effective index = {:.5}'.format(modes.neff[0].real))


    E = np.sqrt(np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2)
    vmin = np.min(np.abs(E))
    vmax = np.max(np.abs(E))

    f = plt.figure()
    ax = f.add_subplot(111)
    im = ax.imshow(np.abs(E), extent=[0,W,0,H], vmin=vmin,
                     vmax=vmax, cmap='inferno', origin='lower')

    ax.plot([W/2-w_wg/2, W/2+w_wg/2, W/2+w_wg/2, W/2-w_wg/2, W/2-w_wg/2],
            [H/2+h_wg/2, H/2+h_wg/2, H/2-h_wg/2, H/2-h_wg/2, H/2+h_wg/2],
            'w-', linewidth=1.0)
    ax.plot([0, W], [H/2-h_wg/2, H/2-h_wg/2], 'w-', linewidth=1)

    f.colorbar(im)
    plt.show()

mindex = 2
Ex = modes.get_field_interp(mindex, 'Ex', squeeze=True)
Ey = modes.get_field_interp(mindex, 'Ey', squeeze=True)
Ez = modes.get_field_interp(mindex, 'Ez', squeeze=True)
if(NOT_PARALLEL):
    import matplotlib.pyplot as plt

    print('Effective index = {:.5}'.format(modes.neff[0].real))


    E = np.sqrt(np.abs(Ex)**2 + np.abs(Ey)**2 + np.abs(Ez)**2)
    vmin = np.min(np.abs(E))
    vmax = np.max(np.abs(E))

    f = plt.figure()
    ax = f.add_subplot(111)
    im = ax.imshow(np.abs(E), extent=[0,W,0,H], vmin=vmin,
                     vmax=vmax, cmap='inferno', origin='lower')

    ax.plot([W/2-w_wg/2, W/2+w_wg/2, W/2+w_wg/2, W/2-w_wg/2, W/2-w_wg/2],
            [H/2+h_wg/2, H/2+h_wg/2, H/2-h_wg/2, H/2-h_wg/2, H/2+h_wg/2],
            'w-', linewidth=1.0)
    ax.plot([0, W], [H/2-h_wg/2, H/2-h_wg/2], 'w-', linewidth=1)

    f.colorbar(im)
    plt.show()
