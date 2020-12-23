import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation
import os
import data as d
# import make_data as md
import numpy as np
import h5py
import time
# import graph as g

def get_existing_data():
	return_me = []
	for dat in os.listdir('./data_dump/'):
		f = h5py.File('./data_dump/{}'.format(dat))
		return_me.append('Approx={}, Force={}, Bodies={}, dt={}, Total Time={}'.format \
			(f.attrs['approximation'],f.attrs['force'],f.attrs['bodies'], \
				f.attrs['dt'],f.attrs['total_time']) \
		)
	return return_me

def get_data_num(bodies,force,approx,delta_t,total_t):
	for dat in os.listdir('./data_dump/'):
		f = h5py.File('./data_dump/{}'.format(dat))
		if f.attrs['approximation'] == approx and f.attrs['force'] == force:
			if f.attrs['bodies'] == int(bodies) and f.attrs['dt'] == float(delta_t) and f.attrs['total_time'] == float(total_t):
				return dat.strip('data_').strip('.hdf5')	
	return -1		
	

def get_data(data_num,max_frames, dim=3, option=0):
	data_name = 'data_' + str(data_num) + '.hdf5'
	print('data_dump/{}'.format(data_name))
	# print(data_name)
	try:
		f = h5py.File('data_dump/{}'.format(data_name), 'r')
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
	# f = h5py.File(data_name, 'r')
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
	approx = ['central']#,'many-body']
	forces = ['grav']#,'em']
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
		elif 'dt=' in i:
			try:
				requested_dt = i.strip('dt=')
			except:
				print("error: in setting dt")
		elif 'total_time=' in i:
			try:
				requested_tt = i.strip('total_time=')
			except:
				print("error: in setting total time")


	if np.isnan(requested_num_planets):
		requested_num_planets = 2
	if requested_force == -1:
		requested_force = 'grav'
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

	#def get_data_num(bodies,force,approx,delta_t,total_t):

	dat_num = get_data_num(requested_num_planets,requested_force,requested_approx,requested_dt,requested_tt)
	# data,nombre,total_iter,radii = get_data(requested_force,requested_approx,requested_num_planets,max_frames=50000,dim=3)
	data,nombre,total_iter,radii = get_data(data_num=dat_num,max_frames=50000,dim=3)
	# data = get_data(total_iter,50000,bodies,3)
	if isinstance(data,int):
		return -1,-1,-1,-1

	return data,nombre,total_iter,radii


def handle_get_data_click(event):
	reset_message()
	if get_data_text.get() == 'Make New Data':
		get_data_text.set('Get Saved Data')
		# if get_data_menu_bool:
		unpack_widgets(get_data_menu_items)
			# get_data_menu_bool = False
		# if not make_data_menu_bool:
		grid_widgets(make_data_menu_items)
		grid_widgets(input_variable_items)
		btn_add_body.pack()
			# make_data_menu_bool = True
	else:
		get_data_text.set('Make New Data')

		# if make_data_menu_bool:
		ungrid_widgets(make_data_menu_items)
		ungrid_widgets(input_variable_items)
		btn_add_body.pack_forget()
			# make_data_menu_bool = False
		# if not get_data_menu_bool:	
		pack_widgets(get_data_menu_items)
			# get_data_menu_bool = True
	window.update_idletasks()

def handle_exit_click(event):
	window.destroy()

def handle_run_click(event):
	reset_message()
	# lbl_status_value.delete("1.0",tk.END)
	# window.update()
	
	status_text.set('Status: Processing')
	window.update_idletasks()
	# time.sleep(1)

	if get_data_text.get() == 'Get Saved Data':
		if planet_data_or_not_text.get() != 'Input Body Variables':
			approx = approx_option.get()
			force = force_option.get()
			bodies = len(input_variable_x_variables)
			d.make_data(force=force_option,approx=approx_option,dt=float(dt.get()),total_time=float(tot_time.get()), \
				data=input_variable_x_variables, other_data=input_variable_o_variables)
		else:
			approx = approx_option.get()
			if approx == "Central Force":
				approx = 'central'
			elif approx == 'Many-body':
				approx = 'many-body'
			force = force_option.get()
			if force == 'Gravity':
				force = 'grav'
			elif force == 'Electromagnetic':
				force = 'em'
			bodies = int(num_bodies.get())
			d.make_data(force=force,approx=approx,bodies=bodies,dt=float(dt.get()),total_time=float(tot_time.get()))
	else:
		opts = data_option.get().split(',')
		approx = opts[0].split('=')[1]
		force = opts[1].split('=')[1]
		bodies = int(opts[2].split('=')[1])
		use_dt = float(opts[3].split('=')[1])
		use_tt = float(opts[4].split('=')[1])
		# print(bodies)

		# d.make_data(bodies=bodies,force=force,approx=approx,dt=use_dt,total_time=use_tt, \
		# 	data=input_variable_x_variables, other_data=input_variable_o_variables)


	data,nombre,total_iter,radii = make_graph(['approx={}'.format(approx),'force={}'.format(force), \
		'num_planets={}'.format(bodies),'dt={}'.format(use_dt),'total_time={}'.format(use_tt)])

	# fig = plt.figure()
	try:
		ax.clear()
		fig.legend([])
	except:
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

	try: 
		graph_canvas.get_tk_widget().pack_forget()
	except: 
		pass

	fig.canvas.draw()
	# graph_canvas = FigureCanvasTkAgg(fig, master=frm_graph)
	graph_canvas.get_tk_widget().pack(side = tk.LEFT)
	# time.sleep(5)
	status_text.set('Status: Idle')
	# window.update()


def handle_add_body_click(event):
	error_msg = ''
	try:
		init_x = float(xi.get())
	except:
		error_msg += 'Error: Please enter an initial x position for this body\n'
	try:	
		init_y = float(yi.get())
	except:
		error_msg += 'Error: Please enter an initial y position for this body\n'
	try:
		init_z = float(zi.get())
	except:
		error_msg += 'Error: Please enter an initial z position for this body\n'
	try:
		init_vx = float(vxi.get())
	except:
		error_msg += 'Error: Please enter an initial x velocity for this body\n'
	try:
		init_vy = float(vyi.get())
	except:
		error_msg += 'Error: Please enter an initial y velocity for this body\n'
	try:
		init_vz = float(vzi.get())
	except:
		error_msg += 'Error: Please enter an initial z velocity for this body\n'
	try:
		init_body_mass = float(body_mass.get()) 
	except:
		error_msg += 'Error: Please enter a mass for this body\n'
	try:
		init_body_name = string(body_name.get())
	except:
		pass
	try:
		init_body_radius = float(body_radius.get())
	except:
		pass

	if error_msg == '':
		xi.set('')
		yi.set('')
		zi.set('')
		vxi.set('')
		vyi.set('')
		vzi.set('')
		body_mass.set('')
		body_radius.set('')
		body_name.set('')

		input_variable_x_variables.append([[init_x,init_y,init_z],[init_vx,init_vy,init_vz]])
		input_variable_o_variables.append([init_body_mass,init_body_radius])
	else:
		error_msg = error_msg[:-1]
		lbl_message.set(error_msg)
		lbl_message_display_message.pack(fill="none", expand=True)

def handle_body_variable_click(event):
	reset_message()
	if planet_data_or_not_text.get() == 'Input Body Variables':
		grid_widgets(input_variable_items)
		planet_data_or_not_text.set('Use Solar System Variables')
		btn_add_body.pack(padx=10,pady=10)
	else:
		ungrid_widgets(input_variable_items)
		planet_data_or_not_text.set('Input Body Variables')
		btn_add_body.pack_forget()

def grid_widgets(widget_list,max_col_len=6):
	curr_row_len = 0
	curr_column_len = 0
	for ind,val in enumerate(widget_list):
		if curr_column_len >= max_col_len:
			curr_column_len = 0
			curr_row_len += 1

		if ind % 2 == 0:
			left_pad = 10
			right_pad = 0
			side = 'E'
		else:
			left_pad = 0
			right_pad = 10
			side = 'W'

		if ind == len(widget_list)-1:
			val.grid(row=curr_row_len,column=curr_column_len,sticky=side, \
				padx=(left_pad,right_pad),pady=3,columnspan=2)
		else:
			val.grid(row=curr_row_len,column=curr_column_len,sticky=side, \
				padx=(left_pad,right_pad),pady=3)

		curr_column_len += 1

def ungrid_widgets(widget_list):
	for ind,val in enumerate(widget_list):
		val.grid_forget()

def pack_widgets(widget_list):
	for ind,val in enumerate(widget_list): 
		val.pack(fill="none", expand=True)

def unpack_widgets(widget_list):
	for ind,val in enumerate(widget_list): 
		val.pack_forget()

def reset_message():
	lbl_message_display_message.pack_forget()




###Begin main window making###
make_data_menu_items = []
get_data_menu_items = []
input_variable_items = []

input_variable_x_variables = []
input_variable_o_variables = []
if not os.path.isdir('data_dump'):
	os.mkdir('data_dump')

window = tk.Tk()

width  = int(window.winfo_screenwidth()/2)
height = window.winfo_screenheight()
window.geometry(f'{width}x{height}')

frm_graph = tk.Frame(master=window, bg="red", \
	relief=tk.FLAT, borderwidth=5)
frm_graph.pack(fill=tk.X)

frm_input = tk.Frame(master=window, height=height*0.15, \
	bg="yellow", relief=tk.RIDGE, borderwidth=5)
frm_input.pack(fill=tk.X)

frm_variable_input = tk.Frame(master=window, height=height*0.2, bg='green', \
	relief=tk.RIDGE, borderwidth=5)
frm_variable_input.pack(fill=tk.X)

frm_add_body = tk.Frame(master=window, height=height*0.05, bg='green', \
	relief=tk.RIDGE, borderwidth=5)
frm_add_body.pack(fill=tk.X)

frm_display_message = tk.Frame(master=window, height=height*0.05, bg='orange', \
	relief=tk.RIDGE, borderwidth=5)
frm_display_message.pack(fill=tk.BOTH,expand=True)



master_ = frm_graph

fig = plt.Figure(figsize=(7,5))
graph_canvas = FigureCanvasTkAgg(fig, master=master_)
graph_canvas.get_tk_widget().pack(side = tk.LEFT)


get_data_text = tk.StringVar()
get_data_text.set('Get Saved Data')
btn_get_data = tk.Button(master=master_, textvariable=get_data_text)
btn_get_data.bind("<Button-1>", handle_get_data_click)
btn_get_data.pack(padx=10, pady=10)

btn_run = tk.Button(master=master_, text='Run Sim')
btn_run.bind("<Button-1>", handle_run_click)
btn_run.pack(padx=10,pady=10)
window.bind("<Return>", handle_run_click)

status_text = tk.StringVar()
status_text.set('Status: Idle')
# lbl_status = tk.Label(master=master_,text='Status: ')
lbl_status = tk.Label(master=master_,textvariable=status_text)
lbl_status.pack(padx=10, pady=10)
# lbl_status_value.pack(padx=10, pady=10)

btn_exit = tk.Button(master=master_, text='Exit Sim')
btn_exit.bind("<Button-1>", handle_exit_click)
btn_exit.pack(padx=10, pady=10,side='bottom')



master_ = frm_input

#make widgets to get new data
approx = ["Central Force","Many-body"]
lbl_approx_input = tk.Label(master=master_, text="Approximation: ")
make_data_menu_items.append(lbl_approx_input)
approx_option = tk.StringVar(master=master_)
approx_option.set(approx[0])

ent_approx_input = tk.OptionMenu(master_,approx_option,*approx)
make_data_menu_items.append(ent_approx_input)

forces = ["Gravity","Electromagnetic","Both"]
lbl_force_input = tk.Label(master=master_, text="Force: ")
make_data_menu_items.append(lbl_force_input)
force_option = tk.StringVar(master=master_)
force_option.set(forces[0])

ent_force_input = tk.OptionMenu(master_,force_option,*forces)
make_data_menu_items.append(ent_force_input)

lbl_num_body_input = tk.Label(master=master_, text='Bodies: ')
make_data_menu_items.append(lbl_num_body_input)
num_bodies = tk.Entry(master=master_)
make_data_menu_items.append(num_bodies)

lbl_dt_input = tk.Label(master=master_, text='dt (days): ')
make_data_menu_items.append(lbl_dt_input)
dt = tk.Entry(master=master_)
make_data_menu_items.append(dt)

lbl_tot_time_input = tk.Label(master=master_, text='Total Time (days): ')
make_data_menu_items.append(lbl_tot_time_input)
tot_time = tk.Entry(master=master_)
make_data_menu_items.append(tot_time)

planet_data_or_not_text = tk.StringVar()
planet_data_or_not_text.set('Input Body Variables')
btn_planet_data_or_not = tk.Button(master=master_, textvariable=planet_data_or_not_text)
btn_planet_data_or_not.bind("<Button-1>", handle_body_variable_click)
make_data_menu_items.append(btn_planet_data_or_not)

grid_widgets(make_data_menu_items)



master_ = frm_variable_input

#make widgets to input variables by body

lbl_xi = tk.Label(master=master_, text='Xi (au): ')
input_variable_items.append(lbl_xi)
xi = tk.Entry(master=master_)
input_variable_items.append(xi)

lbl_yi = tk.Label(master=master_, text='Yi (au): ')
input_variable_items.append(lbl_yi)
yi = tk.Entry(master=master_)
input_variable_items.append(yi)

lbl_zi = tk.Label(master=master_, text='Zi (au): ')
input_variable_items.append(lbl_zi)
zi = tk.Entry(master=master_)
input_variable_items.append(zi)

lbl_vxi = tk.Label(master=master_, text='Vxi (au/day): ')
input_variable_items.append(lbl_vxi)
vxi = tk.Entry(master=master_)
input_variable_items.append(vxi)

lbl_vyi = tk.Label(master=master_, text='Vyi: (au/day)')
input_variable_items.append(lbl_vyi)
vyi = tk.Entry(master=master_)
input_variable_items.append(vyi)

lbl_vzi = tk.Label(master=master_, text='Vzi: (au/day)')
input_variable_items.append(lbl_vzi)
vzi = tk.Entry(master=master_)
input_variable_items.append(vzi)

lbl_body_mass = tk.Label(master=master_, text='Body Mass: ')
input_variable_items.append(lbl_body_mass)
body_mass = tk.Entry(master=master_)
input_variable_items.append(body_mass)

lbl_body_name = tk.Label(master=master_, text='Body Label (op): ')
input_variable_items.append(lbl_body_name)
body_name = tk.Entry(master=master_)
input_variable_items.append(body_name)

lbl_body_radius = tk.Label(master=master_, text='Body radius (au) (op): ')
input_variable_items.append(lbl_body_radius)
body_radius = tk.Entry(master=master_)
input_variable_items.append(body_radius)

#make add data button (in different frame)
btn_add_body = tk.Button(master=frm_add_body, text='Add Body')
btn_add_body.bind("<Button-1>", handle_add_body_click)


master_ = frm_display_message
#make display message stuff
lbl_message_display = tk.Label(master=master_, text='Messages: ')
lbl_message_display.pack(fill=tk.Y,side=tk.LEFT)

lbl_message = tk.StringVar()
lbl_message.set('')
lbl_message_display_message = tk.Label(master=master_, textvariable=lbl_message)



master_ = frm_input
#make widgets to get existing data
lbl_get_data_prompt = tk.Label(master=master_, text='Please select a data set from the dropdown menu')
get_data_menu_items.append(lbl_get_data_prompt)

data = get_existing_data()
data_option = tk.StringVar(master=master_)
if len(data) == 0:
	data.append('No Previously Saved Data')

data_option.set(data[0])

ent_data_input = tk.OptionMenu(frm_variable_input,data_option,*data)
get_data_menu_items.append(ent_data_input)

window.mainloop()




