import numpy as np
import h5py
import data as d
import sys
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation

# def get_data(total_iter,bodies=3, dim=3):
#     tmp = []
#     for i in range(bodies):
#         tmp.append([])
#     c = 0
#     return_me = np.empty((bodies,dim, total_iter))#[[],[],[]]
#     with open("write_data.txt", 'r') as f:
#         for line in f:
#             if line[:9] == "iteration":
#                 c = 0
#             elif line[0] == "(":
#                 split_line = line[1:-2].split(', ')
#                 tmp[c].append([str(i) for i in split_line]) 
#                 c+=1

#     tmp = np.array(tmp)
#     for j in range(total_iter):
#         return_me[:, :, j] = tmp[:, j, :]


#     return return_me

def get_data(force,approx,num_planets,max_frames, dim=3, option=0):
    data_name = d.get_data_name(force,approx,num_planets)
    try:
        f = h5py.File(data_name, 'r')
    except:
        print('Data for force={}, approx={}, num_bodies={} does not exist. Please run make_data.py with appropriate parameters'.format(force,approx,num_planets))
        sys.exit(-1)
    total_iter = f.attrs['iterations']
    bodies = f.attrs['bodies']
    radii = f.attrs['radii']
    names = []
    if option == 0:
        names = f.attrs['names']

    if max_frames < total_iter:
        skip = int(np.ceil(total_iter/max_frames))
        frames = max_frames
    else:
        skip = 1
        frames = total_iter

    return_me = np.empty((bodies,dim, frames))#[[],[],[]]
    f = h5py.File(data_name, 'r')
    ind = 0
    for j in range(0,total_iter,skip):
        return_me[:, :, ind] = f['position_data'][j,:,:]
        ind += 1

    while ind < frames:
        return_me[:, :, ind] = f['position_data'][j,:,:]
        ind += 1

    return return_me, names, total_iter, radii

# def get_iterations():
#     return_me = 0
#     with open("write_data.txt", 'r') as f:
#         for line in f:
#             if line[:9] == "iteration":
#                 return_me += 1
#     return return_me

# def get_iterations(data_name):
#     f = h5py.File(data_name, 'r')
#     return f.attrs['iterations']

# def get_names(data_name):
#     f = h5py.File(data_name, 'r')
#     return f.attrs['iterations']

# def get_bodies():
#     return_me = 0
#     with open("write_data.txt", 'r') as f:
#         for line in f:
#             if line[1:5] == "body":
#                 return_me += 1
#             elif line[:12] == "iteration: 1":
#                 return return_me
#     return return_me

def get_bodies():
    f = h5py.File(d.data_name, 'r')
    return f.attrs['bodies']

def radii_to_markersize(radii):
    # print(radii*62775.3611135)
    return radii*62775.3611135

def update_lines(num, dataLines, lines):
    for line, data in zip(lines, dataLines):
        # NOTE: there is no .set_data() for 3 dim data...
        line.set_data(data[0:2, :num])
        line.set_3d_properties(data[2, :num])
    return lines

def make_graph(argv):
    approx = ['central','many-body']
    forces = ['Grav']
    # Attaching 3D axis to the figure
    requested_num_planets = np.nan
    requested_approx = -1
    requested_force = -1
    for i in argv:
        if 'num_planets=' in i:
            try:
                requested_num_planets = int(i.strip('num_planets='))
            except:
                print("error: in setting num_planets. Could not cast to int")
                sys.exit(-1)
        elif 'approx=' in i:
            try:
                requested_approx = i.strip('approx=') 
            except:
                print("error: in setting approx.")
                sys.exit(-1)
        elif 'force=' in i:
            try:
                requested_force = i.strip('force=') 
            except:
                print("error: in setting force.")
                sys.exit(-1)


    if np.isnan(requested_num_planets):
        requested_num_planets = 2
    if requested_force == -1:
        requested_force = 'Grav'
    if requested_approx == -1:
        requested_approx = 'central'

    if isinstance(requested_num_planets, int):
        if requested_num_planets < 0 or requested_num_planets > 8:
            print('Requested number of planets not supported. Please set a value from 1 to {}.'.format(d.max_solar_system_bodies))
            sys.exit(-1)
    elif isinstance(requested_num_planets, list):
        if requested_approx == 'central' or requested_approx == 'many-body':
            if len(requested_num_planets) > d.max_solar_system_bodies:
                print("Requested number of bodies not supported. Please enter a number from 1 to {} or a list of indices to include with maximum length of {}".format(d.max_solar_system_bodies,d.max_solar_system_bodies))
                sys.exit(-1)

    if requested_approx not in approx:
        print('Requested approx is not supported. Supported approx are:')
        print(approx)
        sys.exit(-1)

    if requested_force not in forces:
        print('Requested force is not supported. Supported forces are:')
        print(forces)
        sys.exit(-1)

    data,nombre,total_iter,radii = get_data(requested_force,requested_approx,requested_num_planets,max_frames=50000,dim=3)
    # data = get_data(total_iter,50000,bodies,3)
    
    fig = plt.figure()
    ax = p3.Axes3D(fig)
    # data = get_data()
    # Creating "iterations" line objects.
    # NOTE: Can't pass empty arrays into 3d version of plot()
    lines = []#np.zeros((len(data)),dtype=Line3D)
    # print(np.array(data))
    marker_sizes = radii_to_markersize(radii)
    marker_sizes[0] = 40
    marker_sizes[1:5] *= 10/marker_sizes[3]

    colors = ['y','#ffa07a','#fff56a','b','r','#ff4500','#7a7733','#acf0f9','#109ae1']

    lines.append(ax.plot(data[0][0, 0:1], data[0][1, 0:1], data[0][2, 0:1],lw = 3,marker='*',markersize=marker_sizes[0],color=colors[0],markevery=[-1])[0])
    lines.extend([ax.plot(dat[0, 0:1], dat[1, 0:1], dat[2, 0:1],lw = 0.9, marker='.',markersize=marker_sizes[i+1],color=colors[i+1],markevery=[-1])[0] for i,dat in enumerate(data[1:])])
    # Setting the axes properties
    lim = 3
    ax.set_xlim3d([-lim, lim])
    ax.set_xlabel('X')

    ax.set_ylim3d([-lim, lim])
    ax.set_ylabel('Y')

    ax.set_zlim3d([-lim, lim])
    ax.set_zlabel('Z')

    # ax.set_title('3D Test')
    fig.legend(nombre)


    # Creating the Animation object
    line_ani = animation.FuncAnimation(fig, update_lines, total_iter, fargs=(data, lines),
                                        blit=False, interval=1)

    # plt.show()
    return fig

