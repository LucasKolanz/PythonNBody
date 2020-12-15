import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation
import os
import data as d
import make_data as md
import numpy as np
import h5py
import time
# import graph as g

def get_data(force,approx,num_planets,max_frames, dim=3, option=0):
	data_name = d.get_data_name(force,approx,num_planets)
	try:
		f = h5py.File(data_name, 'r')
	except:
		# print('Data for force={}, approx={}, num_bodies={} does not exist. Please run make_data.py with appropriate parameters'.format(force,approx,num_planets))
		return [-1,-1,-1,-1]
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
				return -1
		elif 'approx=' in i:
			try:
				requested_approx = i.strip('approx=') 
			except:
				print("error: in setting approx.")
				return -1
		elif 'force=' in i:
			try:
				requested_force = i.strip('force=') 
			except:
				print("error: in setting force.")
				return -1


	if np.isnan(requested_num_planets):
		requested_num_planets = 2
	if requested_force == -1:
		requested_force = 'Grav'
	if requested_approx == -1:
		requested_approx = 'central'

	if isinstance(requested_num_planets, int):
		if requested_num_planets < 0 or requested_num_planets > 8:
			print('Requested number of planets not supported. Please set a value from 1 to {}.'.format(d.max_solar_system_bodies))
			return -1
	elif isinstance(requested_num_planets, list):
		if requested_approx == 'central' or requested_approx == 'many-body':
			if len(requested_num_planets) > d.max_solar_system_bodies:
				print("Requested number of bodies not supported. Please enter a number from 1 to {} or a list of indices to include with maximum length of {}".format(d.max_solar_system_bodies,d.max_solar_system_bodies))
				return -1

	if requested_approx not in approx:
		print('Requested approx is not supported. Supported approx are:')
		print(approx)
		return -1

	if requested_force not in forces:
		print('Requested force is not supported. Supported forces are:')
		print(forces)
		return -1

	data,nombre,total_iter,radii = get_data(requested_force,requested_approx,requested_num_planets,max_frames=50000,dim=3)
	# data = get_data(total_iter,50000,bodies,3)
	if isinstance(data,int):
		return -1,-1,-1,-1

	return data,nombre,total_iter,radii

	# fig = plt.figure()
	# ax = p3.Axes3D(fig)
	# # data = get_data()
	# # Creating "iterations" line objects.
	# # NOTE: Can't pass empty arrays into 3d version of plot()
	# lines = []#np.zeros((len(data)),dtype=Line3D)
	# # print(np.array(data))
	# marker_sizes = np.full((requested_num_planets),10)
	# marker_sizes[0] = 40
	# # marker_sizes = radii_to_markersize(radii)
	# # marker_sizes[0] = 40
	# # marker_sizes[1:5] *= 10/marker_sizes[3]

	# colors = ['y','#ffa07a','#fff56a','b','r','#ff4500','#7a7733','#acf0f9','#109ae1']

	# lines.append(ax.plot(data[0][0, 0:1], data[0][1, 0:1], data[0][2, 0:1],lw = 3,marker='*',markersize=marker_sizes[0],color=colors[0],markevery=[-1])[0])
	# lines.extend([ax.plot(dat[0, 0:1], dat[1, 0:1], dat[2, 0:1],lw = 0.9, marker='.',markersize=marker_sizes[i+1],color=colors[i+1],markevery=[-1])[0] for i,dat in enumerate(data[1:])])
	# # Setting the axes properties
	# lim = 3
	# ax.set_xlim3d([-lim, lim])
	# ax.set_xlabel('X')

	# ax.set_ylim3d([-lim, lim])
	# ax.set_ylabel('Y')

	# ax.set_zlim3d([-lim, lim])
	# ax.set_zlabel('Z')

	# # ax.set_title('3D Test')
	# fig.legend(nombre)


	# # Creating the Animation object
	# line_ani = animation.FuncAnimation(fig, update_lines, total_iter, fargs=(data, lines),
	#                                     blit=False, interval=1)

	# plt.show()
	# return fig

def handle_run_click(event):
	# time.sleep(5)
	# lbl_status_value.delete("1.0",tk.END)
	status_text.set('Processing')
	approx = approx_option.get()
	if approx == "Central Force":
		approx = 'central'
	elif approx == 'Many-body':
		approx = 'many-body'
	force = force_option.get()
	if force == 'Gravity':
		force = 'Grav'
	elif force == 'Electromagnetic':
		force = 'em'
	bodies = int(num_bodies.get())

	if not os.path.isfile(d.get_data_name(force,approx,bodies)):
		md.make_data(force,approx,bodies)

	data,nombre,total_iter,radii = make_graph(['approx={}'.format(approx),'force={}'.format(force), \
		'num_planets={}'.format(bodies)])

	fig = plt.figure()
	ax = p3.Axes3D(fig)
	# data = get_data()
	# Creating "iterations" line objects.
	# NOTE: Can't pass empty arrays into 3d version of plot()
	lines = []#np.zeros((len(data)),dtype=Line3D)
	# print(np.array(data))
	marker_sizes = np.full((bodies),10)
	marker_sizes[0] = 40
	# marker_sizes = radii_to_markersize(radii)
	# marker_sizes[0] = 40
	# marker_sizes[1:5] *= 10/marker_sizes[3]

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

	fig.canvas.show()
	# graph_canvas = FigureCanvasTkAgg(fig, master=frm_graph)
	# graph_canvas.get_tk_widget().pack()

	status_text.set('Idle')

window = tk.Tk()

width  = int(window.winfo_screenwidth()/2)
height = window.winfo_screenheight()
window.geometry(f'{width}x{height}')

frm_graph = tk.Frame(master=window, height=height*0.85, bg="red", \
	relief=tk.FLAT, borderwidth=5)
frm_graph.pack(fill=tk.X)

frm_input = tk.Frame(master=window, height=height*0.15, width=width/2, \
	bg="yellow", relief=tk.RIDGE, borderwidth=5)
frm_input.pack(fill=tk.X)


forces = ["Gravity","Electromagnetic","Both"]
lbl_force_input = tk.Label(master=frm_input, text="Force: ")
lbl_force_input.grid(row=0,column=0)
force_option = tk.StringVar(master=frm_input)
force_option.set(forces[0])

ent_force_input = tk.OptionMenu(frm_input,force_option,*forces)
ent_force_input.grid(row=0,column=1)



approx = ["Central Force","Many-body"]
lbl_approx_input = tk.Label(master=frm_input, text="Approximation: ")
lbl_approx_input.grid(row=0,column=2)
approx_option = tk.StringVar(master=frm_input)
approx_option.set(approx[0])

ent_force_input = tk.OptionMenu(frm_input,approx_option,*approx)
ent_force_input.grid(row=0,column=3)



lbl_num_body_input = tk.Label(master=frm_input, text='Bodies: ')
lbl_num_body_input.grid(row=0,column=4)
num_bodies = tk.Entry(master=frm_input)
num_bodies.grid(row=0,column=5)


btn_run = tk.Button(master=frm_input, text='Run Sim')
btn_run.bind("<Button-1>", handle_run_click)
btn_run.grid(row=0,column=6)


status_text = tk.StringVar()
status_text.set('Idle')
lbl_status = tk.Label(master=frm_input,text='Status: ')
lbl_status.grid(row=0,column=7)
lbl_status_value = tk.Label(master=frm_input,textvariable=status_text)
lbl_status_value.grid(row=0,column=8)



window.mainloop()
