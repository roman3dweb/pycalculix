import pycalculix as pyc

# Vertical hole in plate model, make model
proj_name = 'example2_hole_in_plate'
model = pyc.FeaModel(proj_name)
model.set_units('m')    # this sets dist units to meters, labels our consistent units

# Define variables we'll use to draw part geometry
diam = 2.000 # hole diam
width = 4.444 # plate width
ratio = diam/width
print('D=%f, H=%f, D/H=%f' % (diam, width, ratio))
length = 2*width  #plate length
rad = diam/2   #hole radius
vdist = (length - diam)/2  #derived dimension
adist = width/2             #derived dimension

# Draw part geometry, you must draw the part CLOCKWISE, x, y = radial, axial
part = pyc.Part(model)
part.goto(0.0,rad)
part.draw_arc(rad, 0.0, 0.0, 0.0)
part.draw_line_rad(vdist)
part.draw_line_ax(adist)
part.draw_line_rad(-length/4.0)
part.draw_line_rad(-length/4.0)
part.draw_line_ax(-(adist-rad))
model.plot_geometry(proj_name+'_A0') # view the geometry
part.chunk() # cut the part into area pieces so CGX can mesh it
model.plot_geometry(proj_name+'_A0chunked') # view the geometry

# set loads and constraints
model.set_load('press',part.top,-1000)
model.set_constr('fix',part.left,'y')
model.set_constr('fix',part.bottom,'x')

# set part material
mat = pyc.Material('steel')
mat.set_mech_props(7800, 210*(10**9), 0.3)
model.set_matl(mat, part)

# set the element type and mesh database
model.set_eshape('quad', 2)
model.set_etype('plstress', part, 0.1)
model.set_ediv('L0', 20) # set element divisions
model.mesh(1.0, 'gmsh') # mesh 1.0 fineness, smaller is finer
model.plot_elements(proj_name+'_elem')   # plot part elements
model.plot_pressures(proj_name+'_press')
model.plot_constraints(proj_name+'_constr')

# make and solve the model
prob = pyc.Problem(model, 'struct', part)
prob.solve()

# view and query results
sx = prob.rfile.get_nmax('Sx')
print('Sx_max: %f' % sx)
[fx, fy, fz] = prob.rfile.get_fsum(model.get_item('L5'))
print('Reaction forces (fx,fy,fz) = (%12.10f, %12.10f, %12.10f)' % (fx, fy, fz)) 

# Plot results
fields = 'Sx,Sy,S1,S2,S3,Seqv,ux,uy,utot,ex'    # store the fields to plot
fields = fields.split(',')
for field in fields:
    fname = proj_name+'_'+field
    prob.rfile.nplot(field, fname, display=False)
